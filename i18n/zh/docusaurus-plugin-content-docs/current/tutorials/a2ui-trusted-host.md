---
title: "A2UI 实战：为 Agent 生成界面构建可信 Host"
description: "用消息校验、组件准入、整批预检和 action name 白名单，为 Agent 生成界面构建一个可复现的可信 A2UI Host。"
keywords:
  - A2UI 教程
  - 可信 A2UI Host
  - Agent 生成界面安全
  - A2UI 组件白名单
  - A2UI action 白名单
sidebar_position: 25.5
tags: [tutorial, a2ui, agent-engineering, security, javascript]
---

# A2UI 实战：为 Agent 生成界面构建可信 Host

你准备让 Agent 生成一张发布确认卡片：标题、状态、批准按钮都在已知组件目录里。随后一条保存的消息请求了 `ShellCommand`。固定版本的 processor 把这个未知类型保留成 surface 数据，但没有执行 shell。真正需要解决的问题是：应用应该在哪一层把未知请求挡在 live state 之外？

这个问题之所以值得认真对待，是因为很多 Demo 用了声明式 JSON 就结束了信任讨论——仿佛结构化消息本身就等于安全边界。A2UI 的协议确实给了你结构，但它无法替你决定哪些组件类型可以进入界面、哪些动作名称可以触发副作用、一批消息里有一条格式错误时整体应该怎么处理。这些决定必须由 Host 应用负责。

本文从一个可运行的 fixture 出发，逐步把这些边界建进去。

---

### 先把卡片跑起来

可运行源码放在 [GitHub 的 A2UI trusted-host fixture](https://github.com/IsaacZhaoo/ai-coding-club/tree/8bfe91f3b6ee0938bd286f077476340b75fb1ab2/examples/a2ui-trusted-host)。克隆仓库并切换到本文验证过的 revision，再安装依赖：

```bash
git clone https://github.com/IsaacZhaoo/ai-coding-club.git
cd ai-coding-club
git checkout 8bfe91f3b6ee0938bd286f077476340b75fb1ab2
cd examples/a2ui-trusted-host
npm ci
npm test
```

fixture 里保存了一组 v0.9.1 消息，用于描述一张发布确认卡片。实现固定使用 `@a2ui/web_core@0.10.6` 处理这些消息；包版本和协议版本是两件事。

初始化 processor 只需三行：

```js
import { A2uiMessageSchema, Catalog, MessageProcessor } from '@a2ui/web_core/v0_9';
import { BASIC_COMPONENTS } from '@a2ui/web_core/v0_9/basic_catalog';

const BASIC_CATALOG_ID = 'https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json';
const catalog = new Catalog(BASIC_CATALOG_ID, BASIC_COMPONENTS);
const processor = new MessageProcessor([catalog], onAction, { version: 'v0.9.1' });
```

`MessageProcessor` 接受 catalog 列表、action 回调和协议版本。`BASIC_COMPONENTS` 里有 `Column`、`Text`、`Button`——本文 fixture 里的发布确认卡片只用到这三种，加上另一个 `Text` 显示状态，没有 `Title` 或 `Heading`。

A2UI 用四种操作表达 surface 变化：`createSurface`、`updateComponents`、`updateDataModel` 和 `deleteSurface`。fixture 里第一批消息建立 surface 并填入组件，第二批消息把 `/status` 从 `pending` 更新为 `approved`：

```json
{
  "version": "v0.9.1",
  "updateDataModel": {
    "surfaceId": "release-approval",
    "path": "/status",
    "value": "approved"
  }
}
```

`processor.processMessages` 把这批消息依次应用到内存 surface 上，fixture 随后读取 surface 验证状态已更新。这个路径完全在内存里，没有网络调用，也不需要 API Key 或运行中的模型。

到这里 processor 工作正常。但 fixture 里还有一条额外的保存消息，请求了 `ShellCommand` 组件。processor 把它保留为 surface 数据——没有执行 shell——这正是协议设计的安全底线。如果应用不希望未知组件进入 live state，仍需要在更早的位置明确拒绝。

---

### 加入消息入口与组件准入

在任何消息进入 live state 之前，先过两道检查。

第一道：校验消息结构。`A2uiMessageSchema` 是 v0.9.1 的顶层 schema，每条消息都必须通过：

```js
for (const [index, message] of messages.entries()) {
  if (!A2uiMessageSchema.safeParse(message).success) {
    throw new Error(`Invalid A2UI message at index ${index}`);
  }
  for (const component of message.updateComponents?.components ?? []) {
    if (component.component && !catalog.components.has(component.component)) {
      throw new Error(`Untrusted component type: ${component.component}`);
    }
  }
}
```

第二道：检查组件是否在 catalog 里。`catalog.components.has` 查询的是你初始化时传入的组件集合——`BASIC_COMPONENTS` 里没有 `ShellCommand`，因此这条消息会在进入 processor 之前就被拒绝。

这里有三个样本需要区分清楚，不能混用：

- `executeScript` 是非法的顶层消息结构，过不了 `A2uiMessageSchema` 校验。
- `ShellCommand` 是合法结构的 `updateComponents` 消息，但组件类型不在 catalog 里，在第二道检查被拒。
- `delete_everything` 是合法的 action 请求，组件类型也已知，但 action name 本身需要单独处理。

schema 检查与 catalog 检查在 staging 开始前完成。通过这两道检查的消息才会进入后续流程。

---

### 在副作用前检查 action name

用户点击批准按钮时，`onAction` 回调会收到一个 action 对象。在调用 `surface.dispatchAction` 之前，先验证动作名称：

```js
const actionName = action?.event?.name;
if (!actionAllowlist.has(actionName)) {
  throw new Error(`Untrusted action: ${actionName ?? '<missing>'}`);
}
const surface = processor.model.getSurface(surfaceId);
if (!surface) throw new Error(`Surface not found: ${surfaceId}`);
await surface.dispatchAction(action, sourceComponentId);
```

`actionAllowlist` 是一个 `Set`，里面只有你明确允许的动作名称。`delete_everything` 不在其中，所以即使它的消息结构完全合法、组件类型也已知，副作用也不会发生。

说清楚这个白名单的边界很重要：它不是身份认证，不是权限判断，不是 payload 校验，也不是服务端授权。它唯一做的事是确认这个名称在你的应用策略里被明确允许。更完整的安全体系需要在这个门之外叠加其他层，但那不是本文的范围。

---

### 用 staging replay 说明整批边界

单条消息的检查解决不了一个问题：如果一批消息里前几条合法，最后一条格式错误，已经应用的状态变更要不要回滚？

本文 fixture 用 staging replay 给出一个同步路径的答案。在把消息提交给主 processor 之前，先在 staging 里走一遍：

```js
const stagingProcessor = new MessageProcessor([catalog], undefined, { version: 'v0.9.1' });
stagingProcessor.processMessages(structuredClone(acceptedMessages));
const candidateMessages = structuredClone(messages);
stagingProcessor.processMessages(candidateMessages);

const committedMessages = structuredClone(messages);
processor.processMessages(committedMessages);
acceptedMessages.push(...structuredClone(committedMessages));
```

`stagingProcessor` 没有 action 回调，不会触发副作用。它先 replay 已经接受的历史消息，再尝试应用这批候选消息。如果 staging 阶段 processor 抛错，主 processor 就不会收到这批消息。

局部 mutation 测试演示了这个场景：staging 先成功应用了一条合法的数据更新，然后遇到一个已知组件类型但格式错误的 `Text`（比如必填字段缺失）。staging processor 在第二条抛错，两条消息都不会进入 committed state。

需要说明的是：staging 捕获的是通过 schema 与 catalog 检查之后剩余的 processor 级校验错误。schema 错误和未知组件在 staging 开始前就已经被过滤掉了，不会走到这一步。

另一个限制同样重要：这个整批边界属于本文 fixture 的同步实现，不是 A2UI 本身提供的回滚保证。如果你的消息处理是异步的，或者 processor 状态由多个来源共享，你需要设计自己的边界策略。

---

### 把这个 Host 接到你的应用

走通 fixture 之后，有几个位置需要换成你自己的应用策略。

**替换 catalog**

`BASIC_COMPONENTS` 是 basic catalog 的内容，适合演示。你的应用很可能需要自定义组件。把 `BASIC_CATALOG_ID` 和 `BASIC_COMPONENTS` 换成你的应用 catalog，`catalog.components.has` 的检查逻辑不变。任何不在新 catalog 里的组件类型，都会在进入 live state 之前被拒绝。

**替换 actionAllowlist**

fixture 的测试白名单只允许 `approve_release`。你需要根据应用实际支持的操作来填充这个 `Set`。如果你的应用会调用后端 API，建议同时在服务端验证动作名称，不要只依赖客户端的 allowlist。

**补齐拒绝测试**

在接入真实 Agent 之前，先把三类拒绝场景各写一个测试：

1. 发送一条 `executeScript` 形状的消息，确认 `A2uiMessageSchema.safeParse` 返回失败，消息被拒。
2. 发送包含 `ShellCommand` 的 `updateComponents` 消息，确认 catalog 检查抛错。
3. 触发一个 `delete_everything` action，确认 allowlist 检查阻止了 `dispatchAction` 调用。

加上局部 mutation 的整批测试：确认两条消息都没有进入 committed state。这四个测试能覆盖本文描述的四道边界，让你在连接真实 Agent 之前知道边界是否工作。

**然后再连接 Agent**

有了这些测试之后，你接入真实 Agent 时的可观测性会好很多：你能区分"Agent 发送了格式错误的消息"、"Agent 请求了不在目录里的组件"和"Agent 触发了非法动作"这三种情况，而不是只看到界面没有响应。

---

### 关于兼容性的简短说明

A2UI 项目还在演进。`@a2ui/web_core@0.10.6` 处理 v0.9.1 消息，本文描述的 API 名称和消息形状基于这个组合。如果你使用不同的包版本或协议版本，请先核对对应的文档，部分 API 签名可能有变化。

---

读完这篇文章，你应该能说清楚四件事：哪些行为来自 A2UI 的 schema 和 processor，哪些必须由 Host 应用自己决定，整批边界的限制从哪里来，action name 白名单在整个安全体系里处于哪一层。把这四个答案对照你的应用设计检查一遍，再去连接真实 Agent。
