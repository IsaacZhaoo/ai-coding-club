---
title: "MCP 2026-07-28 无状态迁移：handler 替换、session 搬迁与新旧路径并存"
description: "迁移 TypeScript MCP SDK v2 到 2026-07-28 协议：配置 versionNegotiation、无状态 HTTP handler、显式状态与旧 client 兼容验证。"
keywords:
  - MCP 2026-07-28 迁移
  - MCP 无状态 server
  - TypeScript MCP SDK v2
  - MCP versionNegotiation
  - MCP 旧 client 兼容
sidebar_position: 24
tags: [tutorial, mcp, typescript, agent-engineering]
---

# MCP 2026-07-28 无状态迁移：handler 替换、session 搬迁与新旧路径并存

*作者：有光*

---

## 从一个让人短暂放松的假象说起

```bash
npm install @modelcontextprotocol/client @modelcontextprotocol/server
```

跑完，`package.json` 显示 v2 的拆分包，依赖树里没有冲突，CI 全绿。你把这张截图发到群里，然后去倒了杯水。

我第一次经历这件事的时候，也差点就这么结束了。

但几天后我去翻日志，发现 wire 上的握手顺序还是旧的：`initialize`、`notifications/initialized`、`Mcp-Session-Id`。全套。

包是 v2，但协议还是 2025。这是官方 TypeScript 迁移指南里写得很直接的一件事，只是放在中间段落，很容易在读"安装方法"和"兼容性说明"时跳过——**SDK 版本和协议版本是两件分开的事，安装 v2 不会自动启用 2026-07-28。**

这篇文章从这个错位出发，走完一条完整但有边界的迁移路径。

---

## 先搞清楚你现在在哪里

在做任何改动之前，有四件事需要对齐：

| 维度 | 旧状态（典型） | 新状态（目标） |
|------|--------------|--------------|
| **SDK 版本** | `@modelcontextprotocol/sdk` v1，或早期 v2 | SDK v2（最新稳定） |
| **协议版本** | MCP 2025（或更早） | MCP 2026-07-28 |
| **Transport** | HTTP+SSE，或 stdio | Streamable HTTP（主路径），stdio（次要分支） |
| **状态管理** | 协议层 session，`Mcp-Session-Id` | 显式 handle 作为工具参数，或 MRTR `requestState`（仅重试流程） |

这张表不是为了填空，是为了在动手之前知道自己在哪个格子里——以及要跨过几条线。

---

## SDK v1 → v2：codemod 能做什么，不能做什么

如果你还在 v1，官方提供了一个 codemod：

```bash
npx @modelcontextprotocol/codemod@latest v1-to-v2 .
```

在 package root 运行，它会处理包名变更和机械 API 差异。但有一张表你必须在运行前就明确：

| codemod 负责 | codemod 不负责 |
|-------------|--------------|
| 包名重命名 | 选择 2026-07-28 还是 2025 协议 |
| 机械 API 替换 | `createMcpHandler` vs 旧 HTTP handler 的架构决策 |
| Import 路径更新 | session 状态的搬迁方案 |
| 类型签名适配 | client `versionNegotiation` 的模式选择 |

跑完 codemod，先 `git diff` 看一遍 manifest 和 import 变化，确认没有残留旧包引用。之后你就到了一个清醒的起点：代码在 v2 的语法上，但还没有做任何协议层的决策。

---

## 从这里开始，协议迁移才真正开始

### 2026-07-28 移除了什么

MCP 2026-07-28 移除了以下东西：

- `initialize` 握手请求
- `notifications/initialized` 通知
- 协议层 session（`Mcp-Session-Id` header）

取而代之的是：每个请求在 `_meta` 里携带协议版本和 client capabilities。这意味着 server 不再需要维护握手状态，每个请求都是独立的——这就是"无状态"的字面含义。

同时新增了 `server/discover`，server 必须实现这个端点。client 可以在需要的时候调用它，但不是每次请求都必须调用。

新版 Streamable HTTP 还要求请求带上 `Mcp-Method` 和 `Mcp-Name` header。

### client 端：versionNegotiation 的三种选择

```ts
// 默认：legacy 模式，兼容旧协议，但不会探测新版本
const client = new Client({ name: 'my-client', version: '1.0.0' });

// auto 模式：先探测 2026-07-28，失败时回退到旧协议
const client = new Client(
  { name: 'my-client', version: '1.0.0' },
  { versionNegotiation: { mode: 'auto' } },
);

// pin 到具体协议版本：明确拒绝旧协议
const client = new Client(
  { name: 'my-client', version: '1.0.0' },
  { versionNegotiation: { mode: { pin: '2026-07-28' } } },
);
```

过渡阶段的建议很明确：**用 `auto`，给自己留回退空间**。`auto` 会探测新协议，在配置版本与 transport 条件允许时回退，不会让你在 server 还没准备好的情况下断掉连接。等到新旧两条路径都验证通过，再考虑 pin 到具体协议版本、移除 fallback。

不要跳过中间这一步。"我的 server 已经是新版了"不是跳过 `auto` 阶段的理由，因为你的 client 可能还会连接到其他人的旧版 server。

---

## HTTP server 端：handler 换掉，session 路径单独处理

### 新入口：`createMcpHandler`

```ts
const handler = createMcpHandler(buildServer);
```

`createMcpHandler(factory)` 是 v2 HTTP 的新协议入口。它接受一个 server factory 函数，默认同时能够从同一个 factory 提供无状态的旧协议兼容。注意是 factory，不是 server 实例——这和旧的用法在概念上就不同了：每个请求进来，factory 被调用，产生一个新的 server 上下文，没有跨请求的协议层状态。

### 旧 session 路径：不要假设默认 handler 会保留它

如果你原来的 v1 HTTP server 依赖 `Mcp-Session-Id` 来保存跨调用状态，这是迁移里最需要单独设计的部分。默认的 `createMcpHandler` **不会**保留旧 session 模型。

实践做法是：在 modern strict handler 之前调用 `isLegacyRequest(request)` 检测请求类型；旧请求交给现有的 sessionful handler 继续服务；其余请求交给 modern handler。等旧 client 全部迁移完，再移除该判断分支。

不要假设一个 handler 会自动处理两种模型的状态需求。那不是它的职责。

---

## 状态放回正确位置

这是整个迁移里最容易搞错的地方，也是两种不同的状态需求被混淆最多的地方。

### 普通跨调用状态：显式 handle，作为工具参数传递

MCP 2026-07-28 移除了协议层 session，但并不是说你的工具不能有跨调用状态——它只是不能藏在协议里了。正确的做法是：**在 server 端生成一个显式 handle**（比如一个 UUID 或 token），把它作为普通工具参数返回给 client；client 下次调用时把这个 handle 带回来。

这个 handle 是你自己管理的，存在你自己的存储里，完全透明。这比旧的 session 模型更可预期，也更容易调试。

### MRTR `requestState`：范围窄，必须做完整性保护

`requestState` 是一个不同的东西。它是 MRTR（Multi Round-Trip Requests）流程里，穿过 client 重试的状态。

它的范围很窄：只用于 MRTR 的重试流程。一旦你想用 `requestState` 影响授权、资源分配或业务逻辑，就必须做完整性保护——因为这是不可信输入，client 理论上可以篡改它。

不要把"普通的跨调用状态"和 `requestState` 混用。前者放在你自己的存储里，通过显式 handle 管理；后者只在 MRTR 场景下出现，使用时要验证。

---

## stdio 分支：简短说明

如果你的 server 走 stdio，入口是：

```ts
serveStdio(() => buildServer());
```

同样是 factory 模式。`serveStdio` 是 TypeScript 在 stdio 上提供现代协议（或双版本）的入口。stdio 场景通常没有 session 层的复杂性，但同样需要做协议 era 的选择——不过官方 SDK 在 stdio 上的探测进程、超时和失败语义与 HTTP 不完全相同，具体行为请以官方文档为准。

stdio 分支在本文的验证范围之外，只作为路径提示。

---

## 我实际跑了什么，以及它证明了什么

2026-07-29，我用官方 TypeScript SDK 仓库 commit `cc4b41617ce3601b1290d67216ea0b194a3cd9ac`，在 Node.js `v24.18.0`、pnpm `10.26.1` 的环境下，运行了官方 `examples/stateless-legacy` 示例。

过程是这样的：

server 监听在 `http://127.0.0.1:32123/mcp`。官方 client 依次以 `legacy` 和 `auto` 两种模式连接，检查工具列表中存在 `greet`，调用它，并确认两种模式都返回 `Hello, world!`。client 退出码为 0。

这个验证说明了：**官方最小 HTTP 双版本示例可以运行，`legacy` 与 `auto` 两条路径都完成了工具列表和 `Hello, world!` 断言，client 退出码为 0。**

它没有说明的：

- 真实 v1 项目经过 codemod 之后的行为
- 生产环境的 session 迁移
- 鉴权、MRTR、`requestState` 的正确性
- 缓存（`ttlMs` / `cacheScope`）行为
- stdio、网关、负载均衡下的表现
- 任何性能、延迟或失败率数据

官方示例是起点，不是终点。不要用它来证明你的生产迁移已经完成。

---

## 几个在正文里没展开的细节

**可缓存结果**：新协议支持 `ttlMs` 和 `cacheScope` 来标记规范列出的可缓存结果，例如 `server/discover`、各类 list 和 `resources/read`。如果你用到 `listTools()`、`listPrompts()`、`listResources()`、`listResourceTemplates()` 或 `readResource()`，这些方法对应的结果是值得查看的。但它不是迁移必要项，先让迁移本身跑通。

**Deprecated 但未删除**：Roots、Sampling、Logging、Dynamic Client Registration 和 HTTP+SSE 在 2026-07-28 规范里是 deprecated 状态，不是已经全部删除。如果你的 server 依赖这些，还有时间窗口，但不要当成"以后再说"的理由一直拖。

**`client identity` 是 SHOULD**：新协议要求每个请求在 `_meta` 里携带协议版本和 capabilities，client identity 也建议携带——但规范写的是 SHOULD，不是 MUST。不要把它写成强制要求。

---

## 迁移检查清单

在移除 fallback 之前，逐项过一遍：

**SDK 层**
- [ ] `package.json` 已显示 SDK v2
- [ ] codemod 已运行，`git diff` 已审查，无残留 v1 包引用
- [ ] 没有混用 v1 和 v2 的 API

**Client 端**
- [ ] `versionNegotiation` 已显式配置（过渡期使用 `auto`）
- [ ] `auto` 模式下已验证新协议连接成功
- [ ] `auto` 模式下已验证回退到旧协议时连接成功
- [ ] 确认所有 client 实例都已更新，不只是新写的那个

**HTTP Server 端**
- [ ] 新路径已使用 `createMcpHandler(factory)`
- [ ] 已实现 `server/discover` 端点
- [ ] 旧 session 路径已通过 `isLegacyRequest` 判断单独处理（如适用）
- [ ] 新 Streamable HTTP 请求已携带 `Mcp-Method` 和 `Mcp-Name` header

**状态管理**
- [ ] 原本依赖 `Mcp-Session-Id` 的跨调用状态已改为显式 handle
- [ ] 显式 handle 作为普通工具参数传递，不再藏在协议层
- [ ] `requestState` 仅用于 MRTR 重试流程，且已做完整性保护

**验证**
- [ ] 新协议客户端连接新 server，端到端通过
- [ ] 旧协议客户端连接兼容分支，端到端通过
- [ ] 以上两项在 CI 中都有覆盖，不只是本地跑过一次

**清理（确认后）**
- [ ] 所有 client 已迁移到新协议后，移除 legacy 路由
- [ ] 确认 deprecated 功能（Roots、Sampling、HTTP+SSE 等）的使用计划

---

## 参考资料

- [MCP 2026-07-28 发布说明](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [规范变更日志](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- [Server Discovery 规范](https://modelcontextprotocol.io/specification/2026-07-28/server/discover)
- [TypeScript SDK 迁移索引](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/index.md)
- [TypeScript 2026-07-28 支持指南](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/migration/support-2026-07-28.md)
- [官方双版本 HTTP 示例](https://github.com/modelcontextprotocol/typescript-sdk/tree/main/examples/stateless-legacy)

---

## 相关指南

- [MCP Server 指南](/zh/docs/tools/mcps/)
- [MCP Tool 设计指南](/zh/docs/tutorials/mcp-tool-design-guide/)
- [MCP Server 安全检查清单](/zh/docs/tutorials/mcp-server-security-checklist/)
- [Claude Code 的 Skills、Hooks 和 MCP](/zh/docs/tutorials/claude-code-skills-hooks-mcp/)
