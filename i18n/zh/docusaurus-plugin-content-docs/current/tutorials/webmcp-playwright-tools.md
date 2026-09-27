---
title: "用 WebMCP 把网页动作暴露给 Agent，并通过 Playwright MCP 直接调用"
description: "用 WebMCP 注册网页动作，通过 Playwright MCP 发现并直接调用工具；配置固定版本浏览器，并对照工具返回值与页面 DOM 验证结果。"
keywords:
  - "WebMCP 教程"
  - "Playwright MCP"
  - "WebMCP 工具注册"
  - "AI Agent 网页工具"
  - "WebMCP 披萨演示"
sidebar_position: 38
tags: [tutorial, mcp, agent-engineering, browser-testing]
---

# 用 WebMCP 把网页动作暴露给 Agent，并通过 Playwright MCP 直接调用

> 如果你想让某个网页里的按钮、表单或交互逻辑能被 AI Agent“看见”并直接操控，本文带你从零搭建：配置固定版本的浏览器与桥接服务，注册一个页面函数为工具，然后让 Agent 通过 Playwright MCP 调用它，最后验证页面真实发生了什么。
> 全程基于 Google 官方披萨演示，但你会学到把这套流程迁移到自己网页的通用方法。

## 一、目标与读者假设

读完并动手做完，你应该能：

- 搭建可复现的实验环境（Node.js、Playwright MCP 0.0.82 + 配套 Chromium）。
- 在已有的页面中，注册一个名为 `toggle_layer` 的 WebMCP 工具。
- 让 Agent 通过 MCP 协议发现并调用该工具（例如：添加/移除奶酪层）。
- 对照工具返回文本与页面 DOM 状态，确认动作真正生效。
- 把这套“注册 — 发现 — 调用 — 验证”的流程，迁移到自己的项目里。

读者假设：你熟悉 JavaScript 函数、JSON 结构，并知道如何在 MCP 客户端中配置额外的 MCP Server（比如 VS Code 或 Cursor）。不需要深入 WebMCP 协议细节，但需要能读懂示例代码和 JSON 配置。

## 二、背景：WebMCP 与 Playwright MCP 的分工

- **WebMCP**（browser API proposal）：让网页“描述”自己能做什么（工具名、输入结构、动作说明），并在脚本执行时调用对应的函数。普通页面默认不暴露这些，需要作者主动注册。
Playwright MCP 不仅会把页面动态注册的 WebMCP 动作“暴露”成 MCP Tool 推送到 Agent，同时也直接提供 `browser_navigate`、`browser_snapshot`、`browser_evaluate` 等浏览器与 DOM 操作能力。


> 注意：官方披萨演示自带 fallback polyfill，仅凭能否运行无法判断浏览器是否原生支持 WebMCP。下面的方案使用固定版本组合，确保行为一致。

## 三、环境准备：固定版本的浏览器与桥接服务

### 1. 安装 Node.js（18+）

- 任意发行版均可（LTS 推荐），用于运行 `npx` 和配置 MCP 客户端。
- 验证：`node -v` ≥ 18.0.0

### 2. 安装 Playwright MCP 与配套 Chromium

我们锁定一个已知能工作的版本组合，避免默认浏览器路径或自动升级带来的不一致。

```bash
npx -y playwright@1.64.0-alpha-1789764292000 install chromium
```

要点：

- `browserName: "chromium"` 确保使用 Playwright 捆绑的 Chromium（而非系统 Chrome）。
- 该 Chromium 对应 revision 1246，Chrome for Testing 154.0.8037.0。
- WebMCP 启动参数参考微软官方测试配置，通过 launchOptions 注入 `--enable-features=WebMCP`。

### 3. 创建浏览器配置文件（webmcp.config.json）

```json
{
  "browser": {
    "browserName": "chromium",
    "isolated": true,
    "launchOptions": {
      "headless": false,
      "args": ["--enable-features=WebMCP"]
    }
  }
}
```

- `isolated: true`：让每个会话在独立上下文运行，避免状态污染。
- `headless: false`：演示用真实窗口，方便肉眼观察 DOM 变化（生产可改为 headless）。

### 4. 将 Playwright MCP 加入 MCP 客户端配置

以 VS Code / Cursor 为例（不同客户端语法类似）。当前 VS Code 官方支持在项目根目录的 `.mcp.json` 文件中配置 mcpServers；而 `.vscode/mcp.json` 使用的是 servers 字段，路径与键名务必对应。把下面的 JSON 放入你项目根目录的 `.mcp.json`：


```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp@0.0.82",
        "--config",
        "/path/to/absolute/webmcp.config.json"
      ]
    }
  }
}
```

关键：

建议在启动命令行时采用绝对路径指定 Playwright MCP 的配置文件，以规避客户端启动工作目录不一致带来的问题。例如：

- `--config /absolute/path/webmcp.config.json`

- 重启 MCP 客户端或重新连接该 server。

#### 为什么固定版本很重要？

- Playwright MCP 0.0.82 内部仍以 JSON 字符串传递 `executeTool` 参数；从 Chrome 155 起，官方推荐改用对象形式。
- 为了避免协议细节与浏览器版本混用导致的异常，我们全程使用：
  - Playwright MCP `0.0.82`
  - 配套 Chromium `154.0`（revision 1246）

#### 手动开启方式（仅本地开发调试）

如果不想通过 Playwright 配置，Chrome 也提供原生开关（实验性）：

```
chrome://flags/#enable-webmcp-testing
```

- Enabled → Relaunch
- 上面的 JSON 方案本质是在启动参数中直接注入该功能标志。

## 四、页面注册：把现有动作变成 MCP 工具

### 1. 演示页面说明

官方披萨演示（带按钮调试）：https://googlechromelabs.github.io/webmcp-tools/demos/pizza-maker/?showButtons

- 页面上有“Cheese”按钮，对应一个 JavaScript 函数 `toggleLayer(layer, action)`。
- WebMCP 的核心思想：**不重复造轮子**，只告诉 Agent“有这个动作、怎么调用”，然后复用现有业务函数。

### 2. 在页面中注册工具

官方在线演示已经注册了 `toggle_layer` 工具，读者可以直接访问体验。下方代码的作用是帮助理解现有注册机制，并把这套模式迁移到你拥有 `toggleLayer` 函数的自有页面中。将下面这段放入页面的 `<script>` 标签（模块脚本或 async 函数内），只需执行一次：


```js
await document.modelContext.registerTool({
  name: 'toggle_layer',
  description: 'Control pizza layers (sauce, cheese). Use "add", "remove", or "toggle".',
  inputSchema: {
    type: 'object',
    properties: {
      layer: { type: 'string', enum: ['sauce-layer', 'cheese-layer'] },
      action: { type: 'string', enum: ['add', 'remove', 'toggle'] },
    },
    required: ['layer'],
  },
  execute: async ({ layer, action }) => {
    await toggleLayer(layer, action); // 复用页面已有函数
    return `Performed ${action || 'toggle'} on layer: ${layer}`;
  },
});
```

关键点解释：

- `name` / `description`：让 Agent 理解这工具是干嘛的。
- `inputSchema`：明确参数结构、枚举约束与必填项，帮助 Agent 构造合法调用。
- `execute`：
  - execute接收工具调用传入的参数：示例直接调用 `toggleLayer`，生产环境则需将业务逻辑封装在函数中，于调用时应用参数校验与权限判断。

  - 调用你现有的业务逻辑（这里是 `toggleLayer`）；
  - 返回一句话文本，作为“执行结果”给 Agent 和桥接层使用。

> 实际项目中务必在 `execute` 里做权限与输入校验；这里示例为最小可行版本。

## 五、发现工具：让 Agent 看到 webmcp_toggle_layer

### 1. 导航到演示页面

让 Agent（或在客户端中）执行：

```json
{"name": "browser_navigate", "arguments": {"url": "https://googlechromelabs.github.io/webmcp-tools/demos/pizza-maker/?showButtons"}}
```

要点：

- `showButtons` 让控制按钮保持可见，方便人工对照。
- 页面加载完成后，WebMCP 工具会自动注册到浏览器上下文。

### 2. 查看工具列表（MCP 侧）

在 MCP 客户端或调试面板中查看当前可用的工具列表：

- 应能看到一个名为 `webmcp_toggle_layer` 的工具（Playwright MCP 会在名称前加 `webmcp_` 前缀）。
- 工具列表与当前选中的标签页绑定；切换到其他页面，列表会动态更新。
- 服务端会发送 `tools/list_changed` 通知客户端刷新列表。

> 找不到工具？优先检查：
> - 是否选中了正确的标签页；
> - Playwright MCP 的 config 路径是否正确；
> - 浏览器控制台是否有 WebMCP 相关的错误；
> - 你的注册代码是否已执行。

### 3. 刷新工具列表（如需）

如果客户端工具列表未及时更新，可显式刷新：

```json
{"name": "browser_snapshot", "arguments": {}}
```

不同 MCP 客户端名称略有差异，但原理一致：触发一次页面/上下文快照以同步新注册的工具。

## 六、调用工具：通过 Playwright MCP 直接操控页面

### 1. 添加奶酪层

让 Agent 调用：

```json
{
  "name": "webmcp_toggle_layer",
  "arguments": {
    "layer": "cheese-layer",
    "action": "add"
  }
}
```

预期行为：

- 页面状态：#cheese-layer 的内联 display 被设为 block，奶酪层随即可见。
- 返回结果：页面 handler 精确输出 `Performed add on layer: cheese-layer`。
- 客户端结果：Playwright MCP 将该文本包装为工具返回结果，供 Agent 解析与展示。

### 2. 移除奶酪层

再次调用：

```json
{
  "name": "webmcp_toggle_layer",
  "arguments": {
    "layer": "cheese-layer",
    "action": "remove"
  }
}
```

预期行为：

- 页面返回：`Performed remove on layer: cheese-layer`
- DOM 中 `#cheese-layer.style.display` 回到 `none`，奶酪消失。

> `toggle` 会按逻辑切换当前状态；显式 `add/remove` 更利于 Agent 表达“目标状态”，便于形成确定性的工作流。

### 3. 验证页面真实状态（双重确认）

仅凭返回文本不够严谨，让 Agent 再执行一个检查：

```json
{
  "name": "browser_evaluate",
  "arguments": {
    "function": "() => document.getElementById('cheese-layer').style.display"
  }
}
```

- 在“add”后：预期返回 `"block"`
- 在“remove”后：预期返回 `"none"`

这样就把 **工具返回文本** + **DOM 实际状态** 关联起来，形成可验证的证据链。

## 七、从演示到自己页面：迁移步骤清单

### 迁移步骤清单

#### 1. 选择合适动作
本教程选择一个输入明确、结果可从页面核对的动作；WebMCP 同样支持提供只读数据的查询工具。

#### 2. 注册并校验工具
当页面所需函数与状态已就绪时，参照前文代码在页面上一次注册工具；业务层再检查传入参数与权限。示例中的 `await` 应置于模块顶层或异步函数内；`registerTool` 本身不依赖 DOMContentLoaded，仅当应用函数真正操作 DOM 时再按实际加载时机准备即可。

#### 3. 配置权限策略
页面原生 API 需要 origin-isolated 的 `document` 和 `tools` Permissions Policy，默认值为 `self`；若涉及跨源 iframe，请参阅本文下一节条件。

#### 4. 导航与列表刷新
让 Agent 访问目标页面并刷新快照及客户端工具列表；页面注册名为 `your_action_name`，Playwright MCP 对客户端显示为 `webmcp_your_action_name`。

#### 5. 调用与核对结果
给出明确参数发起调用，随后重新读取 DOM、URL 或业务返回数据以核对执行结果。

## 八、常见问题与边界说明

### 1. 为什么我用最新 Chrome 却看不到 webmcp_ 工具？

- 官方披萨演示自带 polyfill；原生 WebMCP 支持仍在演进中。
- 若你通过 Playwright MCP 配置启动浏览器，请务必传入 `--enable-features=WebMCP`（已在本文示例中给出）。

### 2. 表单页面能用 WebMCP 吗？

能，但有两种模式：

- **命令式（本文演示）**：直接注册 `execute: async ({...}) => {...}`，Agent 调用即执行。
- **声明式表单**：
  - 在 HTML 中使用：`<form toolname="createSupportRequest" tooldescription="Submits a support request">...inputs...</form>`
  - 调用时会自动填充并聚焦表单；默认由用户提交，添加 `toolautosubmit` 后才自动提交。
  - 这与命令式直接执行函数不同，更适合“自然提交”场景。

### 3. 跨源 iframe / 第三方嵌入怎么办？

- WebMCP 对跨域有明确的权限模型：
  - 子帧注册需设置 `allow="tools"`。
  - 涉及 `exposedTo` 和调用方 `fromOrigins` 等元数据，用于精细化控制。
- 主框架演示无需这些配置；当你把页面嵌入到第三方或反向嵌入时，需要参考 WebMCP 的跨域规范调整注册策略。

### 4. 工具名称、描述和返回值算“页面私有数据”吗？

- Agent 看到的工具名、Schema、描述、执行文本都来自页面，但这仅表示“数据来源”，不等同于可信或私有数据。
- 应用层面仍需：
  - 对敏感字段做脱敏与权限控制；
  - 对用户关键操作（支付、账户变更）保留二次确认或日志记录；
  - 理解：DOM 状态变化只能证明“页面动作发生”，不能单独证明后端交易/数据写入完成。

### 5. Playwright MCP 版本差异会影响什么？

- `0.0.81` 使用 `browser_webmcp_list` / `browser_webmcp_call` 等专用工具；
- `0.0.82` 改为直接暴露页面工具（`webmcp_*`），减少桥接层抽象。
- 如需关闭 WebMCP 收集：
  - `--no-webmcp`
  - 根配置中 `webmcp: false`
  - 或环境变量 `PLAYWRIGHT_MCP_WEBMCP=false`

## 九、参考与进一步阅读

- Chrome WebMCP 概述与搭建：https://developer.chrome.com/docs/ai/webmcp
- Imperative API 与注册示例：https://developer.chrome.com/docs/ai/webmcp/imperative-api
- Declarative forms：https://developer.chrome.com/docs/ai/webmcp/declarative-api
- Playwright MCP 0.0.82 发布说明：https://github.com/microsoft/playwright-mcp/releases/tag/v0.0.82
- Playwright MCP 配置与要求：https://github.com/microsoft/playwright-mcp/blob/v0.0.82/README.md
- 配套浏览器版本信息：https://github.com/microsoft/playwright/blob/78ff4260d79b924724bdcc4ccd89e463b8f43b0d/packages/playwright-core/browsers.json
- WebMCP 直接调用测试（微软）：https://github.com/microsoft/playwright/blob/78ff4260d79b924724bdcc4ccd89e463b8f43b0d/tests/mcp/webmcp-dynamic.spec.ts
- 披萨演示源码：https://github.com/GoogleChromeLabs/webmcp-tools/blob/be5700df15ced221cfff862aaf5e6cf0c5f92b62/demos/pizza-maker/script.js

---

现在你已经掌握了从“让 Agent 看见”到“让 Agent 直接调用并验证”的完整闭环。下一步，就挑你项目中一个最频繁被 Agent 询问或需要自动化的动作，按本文流程注册成 `your_action_name` 工具，然后让 Agent 真正替你点一次按钮。

## 延伸阅读

- [在浏览器里核实 Agent 交付的 UI 补丁](/zh/docs/tutorials/coding-agent-browser-testing/)
- [MCP Tool 设计实践：拆边界、写 Schema、处理错误，让 Agent 少猜一步](/zh/docs/tutorials/mcp-tool-design-guide/)
