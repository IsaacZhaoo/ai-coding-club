---
title: "在浏览器里核实 Agent 交付的 UI 补丁"
description: "用可复现的 UI 演示项目检查布局、按钮请求、控制台和会话状态，明确测试通过之后仍需取得哪些浏览器证据。"
keywords:
  - Coding Agent 浏览器测试
  - UI 补丁验证
  - Agent 前端验证
  - 浏览器会话隔离
  - 前端布局与网络检查
sidebar_position: 26
tags: [tutorial, coding-assistant, agent-engineering, browser-testing]
---

# 在浏览器里核实 Agent 交付的 UI 补丁

Agent 交付了一批 UI 改动，单元测试通过，构建没有报错。本例的测试在 Node 环境里运行，不渲染布局，也不点击按钮；本例的构建只把静态源码复制到 `dist`，不做类型检查或 bundle 分析。你还不知道手机宽度下页面会不会溢出，Retry 按钮有没有真的请求正确接口。

接收补丁之前，需要在明确的路由、视口和会话起点下，留下实际渲染、请求、控制台和可见状态的证据。本文用一个小演示项目走完这个流程——故障是故意植入的，用来展示你要追踪的具体信号，不涉及真实线上事故或生产代码。

---

## 演示项目准备

开始前需安装 Node.js、pnpm、agent-browser 和 Chromium。

下载演示项目：

<a href="/examples/ui-verification-lab.zip">下载 UI Verification Lab 示例</a>

解压后进入含 `package.json` 的目录。项目里只有虚构订单 `demo-001`、虚构角色 `editor` / `viewer` 和 localhost 路由，无生产代码，也无第三方运行依赖。

依次运行：

```bash
pnpm test
pnpm build
pnpm start
```

`pnpm test` 预期两项 Node/HTTP 测试通过：示例页面能经 HTTP 访问、正确 Retry 路由返回预期 JSON、错误路由返回 404。这些测试不渲染布局，也不点击页面按钮。`pnpm build` 把静态源码复制到 `dist`，完成后输出构建完成提示。`pnpm start` 启动本地服务并保持运行，另开一个终端进行后续浏览器操作。

测试直接调用接口能通过，同时按钮指向另一个路径——这正是需要在浏览器里核对 UI 实际发出的 method、path、status 的原因。

---

## 故障模式：打开页面，量宽度

项目内置两种模式。先从 `mode=broken` 开始，以 `editor` 角色打开一个全新会话：

```bash
agent-browser --session ui-lab-broken-01 open 'http://127.0.0.1:4173/?mode=broken&role=editor'
agent-browser --session ui-lab-broken-01 set viewport 390 844
agent-browser --session ui-lab-broken-01 snapshot -i
agent-browser --session ui-lab-broken-01 eval '({ innerWidth: window.innerWidth, scrollWidth: document.documentElement.scrollWidth })'
```

每组 session 名都必须是本次未使用的新名字；上面的 `ui-lab-broken-01` 只是示例，复跑时更换后缀。新名字用来隔离状态，不保证固定名字每次自动重置。

快照应能识别 `Retry status check` 按钮，表明交互控件已在页面中渲染。宽度命令只返回两个字段：

```json
{ "innerWidth": 390, "scrollWidth": 632 }
```

`innerWidth` 是布局视口内部宽度（可能包括垂直滚动条），`scrollWidth` 包括因溢出而不可见的内容宽度——这里比较的是根文档与视口；如果要检查某个具体元素是否自身溢出，可以对比它的 `scrollWidth` 和 `clientWidth`。

632 超出视口 390 约 242 像素，说明有内容溢出。上面的 632 是既有示例运行的记录值，受字体和渲染环境影响，你自己的测量结果可能不同；主要确认是否超过视口，以及修复后溢出是否消除。

---

## 故障模式：点击 Retry，追踪请求与状态

点击前先清理 network 与 console 记录，方便区分动作前后的信号。`errors` 是独立的 page error 列表，以下命令未清理它，因此本例依靠全新会话并对照动作前后来观察：

```bash
agent-browser --session ui-lab-broken-01 network requests --clear
agent-browser --session ui-lab-broken-01 console --clear
agent-browser --session ui-lab-broken-01 errors --json
agent-browser --session ui-lab-broken-01 click '#retry-button'
agent-browser --session ui-lab-broken-01 wait 300
agent-browser --session ui-lab-broken-01 network requests --filter '/api/orders/' --json
agent-browser --session ui-lab-broken-01 console --json
agent-browser --session ui-lab-broken-01 errors --json
agent-browser --session ui-lab-broken-01 eval '({ status: document.querySelector("#order-status").textContent, result: document.querySelector("#retry-result").textContent })'
```

300 ms 是本地示例的观察等待，不是请求完成的保证。如果页面还在处理中，继续等待可见结果后再读取，不要把超时直接视为产品故障。

故障模式的按钮故意调用 `POST /api/orders/demo-001/retry-status`，该路径返回 404；有效路由是 `POST /api/orders/demo-001/retry`。

点击后的记录：

- **网络**：一个 POST 到 `/api/orders/demo-001/retry-status`，状态 404
- **可见状态**：`#order-status` 仍为 `Needs attention`，`#retry-result` 显示 `Synthetic retry failed.`
- **console**：含一条受控 `console.error`（代码捕获异常后记录，因此 page errors 为空，两者不矛盾）
- **page errors**：空

---

## 修复模式：同样步骤，比较差异

修复来自同一项目预置的 `mode=fixed`，CSS 修复覆盖如下：

```css
body[data-mode='fixed'] .error-id {
  width: auto;
  max-width: 100%;
  overflow-wrap: anywhere;
  white-space: normal;
}
```

同时按钮请求路径切换为 `/api/orders/demo-001/retry`。

使用一个新的 editor 会话——名字不能与之前用过的重复：

```bash
agent-browser --session ui-lab-fixed-editor-01 open 'http://127.0.0.1:4173/?mode=fixed&role=editor'
agent-browser --session ui-lab-fixed-editor-01 set viewport 390 844
```

对这个会话重复 snapshot、宽度测量、清理 network/console、点击和读回的全套步骤，所有命令里的 session 都改为 `ui-lab-fixed-editor-01`。

点击完成后，再读一次宽度：

```bash
agent-browser --session ui-lab-fixed-editor-01 eval '({ innerWidth: window.innerWidth, scrollWidth: document.documentElement.scrollWidth })'
```

点击后的既有示例记录：

- **宽度**：innerWidth 390、scrollWidth 390（溢出消除；此宽度证据来自点击后，不是点击前）
- **网络**：一个 POST 到 `/api/orders/demo-001/retry`，状态 200
- **可见状态**：`#order-status` 显示 `Ready`，`#retry-result` 显示 `Synthetic retry succeeded.`
- **console**：清理后没有新消息
- **page errors**：空

下表并排列出两次观测，仅限本演示场景：

| 观测项 | 故障模式（broken） | 修复模式（fixed） |
|---|---|---|
| 视口设置 | 390 × 844 | 390 × 844 |
| scrollWidth | 632（点击前） | 390（点击后） |
| 请求 method/path | POST /api/orders/demo-001/retry-status | POST /api/orders/demo-001/retry |
| HTTP status | 404 | 200 |
| 可见状态 | Needs attention | Ready |
| 可见结果 | Synthetic retry failed. | Synthetic retry succeeded. |
| console（清理后） | 1 条 error | 无新消息 |
| page errors | 空 | 空 |

表中的比较是本演示项目的具体记录，不适用于任意应用的认证。CSS 与请求路径是这里的产品代码修复，独立会话是验证条件，不是靠换会话修复了业务权限。

---

## 角色隔离检查

从 fixed editor 会话继续，移除 role 参数，观察存储值是否保留：

```bash
agent-browser --session ui-lab-fixed-editor-01 open 'http://127.0.0.1:4173/?mode=fixed'
agent-browser --session ui-lab-fixed-editor-01 eval '({ role: document.querySelector("#active-role").textContent, stored: localStorage.getItem("ui-lab-role") })'
```

同一个 editor 会话移除 role 参数后仍显示 Editor，localStorage 存储 `editor`。

用独立会话打开 viewer：

```bash
agent-browser --session ui-lab-fixed-viewer-01 open 'http://127.0.0.1:4173/?mode=fixed&role=viewer'
agent-browser --session ui-lab-fixed-viewer-01 eval '({ role: document.querySelector("#active-role").textContent, stored: localStorage.getItem("ui-lab-role") })'
```

独立 viewer 会话显示 Viewer，localStorage 存储 `viewer`。再读原 editor 会话：

```bash
agent-browser --session ui-lab-fixed-editor-01 eval '({ role: document.querySelector("#active-role").textContent, stored: localStorage.getItem("ui-lab-role") })'
```

确认它仍显示 Editor、存储 `editor`，再判断两个会话的状态互不干扰。

`role` 参数是演示用的存储值，不是登录机制，不实施访问控制。[Playwright BrowserContext 文档](https://playwright.dev/docs/browser-contexts) 说明各上下文拥有独立的 cookies、localStorage 和 sessionStorage；本例只观察虚构 role 的 localStorage 和页面结果，不声称测试过 cookies、认证、授权或真实用户切换。

---

## 留给自己的验收记录

浏览器操作留下的记录应包含以下要素，可以是一张小表或简短说明：

- **路由**：完整 URL，包括 mode 和 role 参数
- **视口**：宽度 × 高度
- **会话前提**：会话名，是否全新，是否已清理 network/console
- **动作**：snapshot、click、eval 等
- **预期状态**与**实际状态**
- **相关请求**：method / path / status
- **新 console 信息**
- **page errors**
- **宽度**：innerWidth 与 scrollWidth，注明测量时机
- **是否通过**与**未覆盖范围**

---

## 覆盖范围说明

本文的宽度和 Retry 观测在同一 Chromium、390 × 844 视口下完成，不涵盖 Safari、Firefox、其他宽度、缩放、键盘操作、屏幕阅读器、性能或安全测试。HTTP 200、空 console、空 page errors 和宽度一致，都只是限定场景下的证据，不是应用完全正确的证明。

演示接口固定返回假数据，UI 验收不能替代业务逻辑测试。应用到自己的项目时，使用获准的测试环境和账号，按改动补相应的浏览器和视口；遇到身份不明或会触发真实订单等副作用的动作，先停止操作。

把本文中的演示路由和动作换成你获准测试的功能，按同样的步骤留下证据，合并前就有了一份知道覆盖范围的浏览器记录。

---

**参考链接**

- [Playwright BrowserContext](https://playwright.dev/docs/browser-contexts)
- [Element.scrollWidth — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollWidth)
- [Window.innerWidth — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Window/innerWidth)
- [Chrome DevTools Network](https://developer.chrome.com/docs/devtools/network)
- [Chrome DevTools Console](https://developer.chrome.com/docs/devtools/console)
- [agent-browser — GitHub](https://github.com/vercel-labs/agent-browser)
