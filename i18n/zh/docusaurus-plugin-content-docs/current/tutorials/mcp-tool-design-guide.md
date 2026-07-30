---
title: "MCP Tool 设计实践：拆边界、写 Schema、处理错误，让 Agent 少猜一步"
description: "用任务边界、Schema、annotation、结构化返回与可操作错误设计 MCP Tool，让 Agent 少猜一步，并区分 handler test 与 Agent eval。"
keywords:
  - MCP Tool 设计
  - Agent Tool 设计
  - MCP inputSchema
  - MCP Tool annotation
  - MCP Agent eval
sidebar_position: 25
tags: [tutorial, mcp, agent-engineering, typescript]
---

# MCP Tool 设计实践：拆边界、写 Schema、处理错误，让 Agent 少猜一步

*作者：有光*

## 当后端接口碰上 Agent：MCP Tool 的设计视角

有一段时间，我每次打开工程里的 Tool 定义，都会看到这个：

```ts
project_api({ action, payload })
```

对写后端的人来说，它很干净。一个入口，多种操作，鉴权和请求逻辑只写一遍。整洁，符合直觉，几乎所有后端接口都可以这样包一层就交差。

问题在于，这份整洁是站在开发者视角看的。Agent 看到的是另一回事。

它要猜 `action` 有哪些合法值。它要猜 `payload` 在不同 action 下是什么形状。它要猜这次调用会不会改数据，失败以后该改参数还是换别的 Tool。所有真正要做的决定，都藏在那个万能入口后面。

2026-07-28 的 MCP 规范把这些问题直接摊在了 Tool definition 和 Tool result 里。但规范讲的是字段该怎么填；这篇文章想讲的是评审角度：接口能调用，只是底线；Agent 能不能根据这份定义做出下一步判断，才是 Tool 设计的标准。

---

### 第一层问题：它把决定推给了谁

`project_api(action, payload)` 这样的设计，本质上是把操作选择推给了调用者，却没有给调用者足够的信息来做选择。

人类开发者能翻文档、跑 REPL、问同事，可以接受这种模糊。Agent 只有 Tool definition 和上下文窗口。它没有别的信息来源。

所以，当我坐下来重新审查这个接口时，我要问的不是"这个 handler 能不能跑"，而是：

- Agent 看到这份定义，知不知道什么时候该调它？
- 它能不能从参数结构本身判断哪些是这次操作需要的字段？
- 它能不能在调用前估计副作用？
- 调用失败后，错误信息告诉它下一步怎么改？

这四个问题，`project_api` 一个都答不了。这不是参数描述写得不够详细的问题，是边界划错了。

Anthropic 在他们的 Tool 设计文章里说过一句话：**Tool 的边界应该围绕 Agent 要完成的工作，不要照搬后端的每一个 endpoint。** 我觉得反过来说更清楚：每个 endpoint 该不该对应一个 Tool，先想 Agent 下一步要做什么，再想这个操作放哪里。

---

### 第二层问题：边界怎么划

我在本地写了一个合成示例来跑这些想法。环境是 Node.js v24.18.0、pnpm 11.10.0、`@modelcontextprotocol/server` 2.0.0 和 `@modelcontextprotocol/client` 2.0.0、Zod 4.4.3，client 和 server 用 in-memory transport 连接。只有两个 Tool，刻意让它们的边界不一样：

- **`issues.search`**：只读，用关键词查 issue 标题。
- **`issues.close`**：修改状态，幂等，调同一个 ID 不会重复变更。

为什么是这两个，而不是一个通用的 `issues_api(action, payload)`？

因为这两个操作对 Agent 的含义完全不同。`issues.search` 是"我不知道 ID 是什么，先看看"；`issues.close` 是"我已经确认了 ID，现在要做一个改变已有状态的操作"。它们需要不同的上下文才能触发，失败后的处理方式也完全不同。把它们放进同一个入口，不是减少了 Tool，是让 Agent 在每次调用前多做一道没有答案的选择题。

把它们拆开，可以直接在 annotation 和 description 里把这些区别说清楚：

```ts
server.registerTool(
  'issues.search',
  {
    description:
      'Search the local issue index by words in the title. Use this before issues.close when the exact issue ID is unknown. This tool never changes issue state.',
    annotations: { readOnlyHint: true, openWorldHint: false },
    // ...
  },
  handler,
);
```

```ts
server.registerTool(
  'issues.close',
  {
    description:
      'Close one issue by exact ID after the user has selected it. This changes stored issue state. Repeating the same call returns already_closed without another change.',
    annotations: {
      readOnlyHint: false,
      destructiveHint: true,
      idempotentHint: true,
      openWorldHint: false,
    },
    // ...
  },
  handler,
);
```

`description` 里"Use this before issues.close when the exact issue ID is unknown"这句不是废话。它在告诉 Agent 一个常见的两步序列：先搜，确认 ID，再关。这比等 Agent 自己试错要快。

---

### 名称与描述：减少猜测的第一道防线

Tool name 在规范里建议是 1–128 字符，ASCII 字母、数字、下划线、连字符和点，在单个 server 内唯一，大小写敏感。这些是格式约束，更实质的问题是名字本身传达了什么。

`issues.search` 和 `issues.close` 用点做 namespace，这样在多个 server 聚合、可能出现名称碰撞的环境里，至少还能看出来它们属于同一组操作。名字本身——search 和 close——直接说明了动作性质。

description 里要解决的是三件事：

1. **何时用这个 Tool**：触发条件，不能只写"查询 issue"这种循环定义。
2. **何时别用**：`issues.close` 的 description 里说"by exact ID after the user has selected it"，隐含的意思是，如果你还不知道 ID，不该来这里。
3. **会不会改状态**：`issues.search` 的 description 明确写了"This tool never changes issue state"，`issues.close` 写了"This changes stored issue state"。这不是废话，是 Agent 在决定是否需要确认时要看的信息。

description 和 inputSchema 里每个参数的 describe 字符串，都会进入 client 看到的 Tool definition。它们是模型在选择 Tool 和填参数时的直接上下文。把时间花在这里，比花在 handler 注释上回报高得多。

---

### Schema：把模糊输入关进合法形状里

MCP 的 `inputSchema` 使用 JSON Schema，根必须是 `object`。但我倾向于用 Zod 写，再让 SDK 转换，因为 Zod 的约束表达更直接，`describe()` 也能直接附在字段上：

```ts
inputSchema: z.object({
  query: z.string().trim().min(2).max(80)
    .describe('Two or more characters to match in the issue title'),
  status: z.enum(['open', 'closed', 'any']).default('open')
    .describe('Which issue states to include'),
}),
```

```ts
inputSchema: z.object({
  issueId: z.string().regex(/^ISSUE-\d{3}$/)
    .describe('The issue ID, e.g. ISSUE-042'),
  reason: z.string().trim().min(5).max(200)
    .describe('Why this issue is being closed'),
}),
```

几个判断点：

- `query` 用 `min(2)` 而不是只 `min(1)`，是因为单字符查询通常过于宽泛、结果没意义，与其让 Agent 得到一大堆噪音，不如在 Schema 层拒掉。数据规模更大时，仍需给 `limit` 参数加上限，或引入 pagination 来控制结果集大小。
- `status` 用 `enum` 而不是 `string`，消除了 Agent 自己猜合法值的可能。
- `issueId` 用 `regex` 锁定格式。这样 Agent 如果填了一个不符合格式的 ID，会在参数校验阶段就拿到明确的 error，而不是在 handler 里静默失败或触发意外行为。
- `reason` 是 required 字段，不是 optional。关闭 issue 是有业务含义的操作，强迫有理由，也让调用轨迹更可追溯。

`enum`、`pattern`、范围约束和参数 description，是把"Agent 猜"变成"Schema 拒绝"的具体手段。每减少一种猜测，就减少一种潜在错误路径。

---

### Annotation：如实填写，但不要误解它的效力

MCP 规范目前有四个正式的行为 hint：`readOnlyHint`、`destructiveHint`、`idempotentHint`、`openWorldHint`。规范有一组默认值：read-only 为 false、destructive 为 true、idempotent 为 false、open-world 为 true。

这四个默认值是**保守的**。新写的 Tool 如果什么都不填，默认被认为是可能修改状态、不可重复、面向开放世界的操作。所以 `issues.search` 需要显式声明 `readOnlyHint: true`，否则 client 有理由对它多加戒心。

`issues.close` 同时有 `destructiveHint: true` 和 `idempotentHint: true`。这两个不矛盾：它确实改变已有状态（destructive），但重复调用不会再改一次（idempotent）。handler 里实现了这一点，重复对同一个 ID 调用会返回 `already_closed` 而不是报错，也不会触发两次关闭逻辑。

**必须说清楚的边界**：annotation 全部只是 hint。来自不可信 server 时，client 必须把它们视为不可信。`readOnlyHint: true` 不等于沙箱，不等于权限控制，也不等于"真的不会写数据"的保证。它是 server 自我声明的行为描述，可以被错误填写，也可以被恶意利用。确认框、权限校验、沙箱环境，是 application 的责任，不是 annotation 的责任。

---

### 返回值：高信号，留下续步需要的 ID

规范里的 `outputSchema` 是可选的。一旦提供，server 返回的 `structuredContent` 必须符合它，client 应执行验证。

```ts
outputSchema: z.object({
  count: z.number().int().nonnegative(),
  issues: z.array(z.object({
    id: z.string(),
    title: z.string(),
    status: z.enum(['open', 'closed']),
  })),
}),
```

```ts
outputSchema: z.object({
  issueId: z.string(),
  outcome: z.enum(['closed', 'already_closed']),
  status: z.literal('closed'),
}),
```

`issues.search` 的 outputSchema 只返回 `id`、`title`、`status`，没有完整记录、没有元数据、没有调试字段。这三个字段正好满足 Agent 做下一步决定的需要：知道 ID，知道标题，知道当前状态，才能判断要不要调 `issues.close`。

`issues.close` 的 outcome 字段区分了 `closed` 和 `already_closed`，而不是把两种情况都返回成 `"success"`。这个区分让 Agent 知道：重复调用不是新的变更，不需要重新通知用户或触发下游流程。

为了兼容旧 client，规范 SHOULD（不是 MUST）同时返回序列化后的 text content：

```ts
async ({ query, status }) => ({
  content: [{ type: 'text', text: '给人和旧 client 看的精简结果' }],
  structuredContent: { count, issues: matches },
}),
```

text content 是给没有 outputSchema 支持的旧 client 的降级路径，也是人工调试时最快的查看方式。structuredContent 是给新 client 和支持结构化输出的 Agent 的主要返回。

Anthropic 的文章提到，大结果要有 filter、limit、pagination 或 concise/detailed 模式。`issues.search` 加了 `query` 的 min 长度限制，可以拒绝过宽泛的单字符查询。如果数据规模更大，给 `limit` 参数加个上限是合理的下一步，但不要在没有必要的时候提前引入复杂度。

---

### 错误：告诉 Agent 下一步怎么改

MCP 里有两层错误，用途不一样：

- **Protocol error**：找不到 Tool、请求结构错误、server 故障。这层走 JSON-RPC 的 error response，对 Agent 来说是"调用失败，不是我的参数问题"。
- **Tool execution error**：API 失败、输入校验失败、业务失败。这层用 `isError: true`，把错误放进正常的 Tool result，client 应该把它提供给模型，给它修改参数并重试的机会。

`issues.close` 里不存在的 ID，走的是 Tool execution error：

```ts
// issueId 不在数据集里：
return {
  isError: true,
  content: [{
    type: 'text',
    text: `Unknown issue ${issueId}. Call issues.search to find a valid issue ID, then retry.`,
  }],
};
```

注意这里的错误文本："Call issues.search to find a valid issue ID, then retry."这句话直接告诉 Agent 下一步要做什么。不是"ID not found"，不是"invalid input"，是可操作的下一步。

规范说 client 应该把 Tool execution error 提供给模型，让它有修改参数并重试的机会。但这不等于保证模型一定能恢复。错误信息写得好，只是提高了模型自我修正的概率，不是保证。

我在合成示例里跑了几种场景，`pnpm verify` 的实际输出：

```json
{
  "toolOrder": ["issues.search", "issues.close"],
  "invalidSchemaInputIsError": true,
  "searchMatches": ["ISSUE-001", "ISSUE-002"],
  "missingIssueIsError": true,
  "firstClose": "closed",
  "repeatedClose": "already_closed"
}
```

`toolOrder` 是确定的，这符合规范的 SHOULD：当 Tool 集合不变时，server 应以确定顺序返回，便于 client 缓存和 prompt cache 复用。`invalidSchemaInputIsError: true` 和 `missingIssueIsError: true` 验证了同一类 Tool execution error 在 Schema 校验阶段和 handler/业务阶段都返回 `isError: true`。`repeatedClose: "already_closed"` 验证了幂等行为。

**必须说清楚的限制**：这证明的是 Tool definition、Schema 和 handler 的行为。它不证明真实 Agent 在面对这组 Tool 时会做出正确的选择序列。handler test 和 Agent eval 是两个不同的问题。

:::tip[运行已验证示例]
<a href="/examples/mcp-tool-design-guide.zip" download>下载已验证的 TypeScript 示例</a>，使用 pnpm 安装固定依赖后运行 `pnpm verify`，即可复现上面的 in-memory 检查。
:::

---

### 重构前后的对比

| 维度 | `project_api(action, payload)` | `issues.search` / `issues.close` |
|------|---|----|
| Agent 何时调用 | 需要猜 action 是否适用 | description 直接给出触发条件 |
| 副作用判断 | 不可知 | annotation 明确声明 |
| 参数形状 | 随 action 变化，模型无法预知 | 每个 Tool 有固定的 inputSchema |
| 幂等性 | 未知 | `issues.close` 声明 idempotent，handler 保证 |
| 错误恢复 | 无结构化路径 | isError + 可操作文本 |
| 结果信号 | 完整记录还是字段？模型不知道 | outputSchema 约束返回形状 |
| 下一步可见性 | Agent 需要推断 | 错误文本直接指向下一步 Tool |

---

### handler test 之后：Agent eval

把 Tool 跑通，只是开始。

Anthropic 的文章说，最后要看任务有没有完成、调用轨迹哪里卡住，不只看 handler test 是否通过。这是两个不同的问题：handler test 验证的是"给定合法输入，handler 返回预期输出"；Agent eval 验证的是"给定真实任务描述，Agent 选了正确的 Tool，用了合法的参数，最终完成了任务"。

一个可操作的评估路径（这是建议路径，不是我已经跑过的）：

- 从真实工作流里整理任务，要有可验证的结果——比如"把标题包含'登录失败'的所有未关闭 issue 关掉，并说明原因"。
- 加入需要多次 Tool call 的任务，加入起始信息不完整的任务，比如只给 issue 关键词不给 ID。
- 每个任务用 fresh Agent loop，只给当前要评估的 Tool 集合，不给历史上下文。
- 同时看最终结果、Tool 选择顺序、参数内容、重试次数、错误类型、调用总次数和返回内容里有多少对 Agent 没用的字段。
- 修改了 description 或 Schema 之后，用没有参与调试的 held-out task 复核，避免只是把已知题目调通了。

handler 测试和 Agent eval 之间有一道沟。跨过这道沟，才能知道 Tool 定义在真实 Agent loop 里是否足够好用。

---

### Tool Review Checklist

设计完一个 Tool 之后，我会对照这几条过一遍：

- [ ] **名称**：一眼能看出操作性质，用了 namespace，没有和同组其他 Tool 产生语义重叠。
- [ ] **description**：写清何时用、何时别用、会不会改状态；包含常用序列的顺序提示。
- [ ] **inputSchema**：每个参数都有 describe；能用 enum 就不用 string；有 pattern 或 range 约束的地方写了约束；required 字段是真的必须，optional 字段有合理默认值。
- [ ] **annotation**：如实填写，没有夸大 readOnly 或 idempotent；理解它们只是 hint，不是权限控制。
- [ ] **outputSchema**：声明了，且 handler 返回的 structuredContent 确实符合；只返回 Agent 做下一步判断需要的字段；同时有降级用的 text content。
- [ ] **错误**：Tool execution error 用 `isError: true`；错误文本直接说明下一步能做什么；不把 server fault 包装成 Tool result。
- [ ] **幂等性**：声明了 idempotentHint 的 Tool，handler 确实保证了幂等行为。
- [ ] **评估**：跑了 handler test 之后，还有真实任务的 Agent eval 路径，不只看接口通不通。

---

### 参考资料

- [MCP Tools 规范（2026-07-28）](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- [MCP Schema（2026-07-28）](https://modelcontextprotocol.io/specification/2026-07-28/schema)
- [Anthropic：为 Agent 编写 Tool](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [MCP Tool Annotations（2026-03-16）](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/)
- [TypeScript SDK Tool 示例](https://github.com/modelcontextprotocol/typescript-sdk/blob/cc4b41617ce3601b1290d67216ea0b194a3cd9ac/examples/guides/servers/tools.examples.ts)

---

## 相关指南

- [MCP Server 指南](/zh/docs/tools/mcps/)
- [MCP 2026-07-28 无状态迁移指南](/zh/docs/tutorials/mcp-2026-07-28-stateless-migration/)
- [MCP Server 安全检查清单](/zh/docs/tutorials/mcp-server-security-checklist/)
- [Coding Agent Evals 指南](/zh/docs/tutorials/coding-agent-evals-guide/)
