---
title: "连接 MCP Server 之前，我会检查这 12 件事"
description: "一份连接 MCP Server 前的安全检查清单，覆盖来源、OAuth Scope、Token、Tool 副作用、数据访问、日志与撤销路径。"
keywords:
  - MCP Server 安全
  - MCP 安全检查清单
  - Model Context Protocol 安全
  - MCP OAuth
  - MCP Server 风险
sidebar_position: 12
tags: [tutorial, mcp, agent-engineering, security]
---

# 连接 MCP Server 之前，我会检查这 12 件事

---

README 里那段话通常只有两行：

```json
{
  "mcpServers": {
    "some-tool": {
      "command": "npx",
      "args": ["-y", "some-mcp-server@latest"]
    }
  }
}
```

粘贴进配置文件，重启 Client，工具就出现在 Agent 的上下文里了。这个过程顺畅得让人忘记一件事：刚才你做的，是把一段可执行代码、一组网络权限，以及潜在的 token 访问路径，交给了一个你不认识的发布者。

能连上不代表应该连。

我在接入每一个 MCP Server 之前，都会过下面这张清单。它不能让你证明某个 Server "绝对安全"——那种声明本身就是危险信号。它帮你把隐性的信任决策变成显性的核对动作。

---

## 快速 Stop / Go 判断

在进入 12 项细节之前，先做三个过滤：

| 信号 | 建议 |
|---|---|
| 发布者不可追溯（无仓库、无组织、无历史提交） | 🔴 Stop |
| 安装命令使用 `@latest` 且无 lockfile 机制 | 🟡 谨慎，固定版本后再评估 |
| 授权流程要求的 scope 明显超过工具所需功能 | 🔴 Stop |
| 文档里没有提 tool list，也没有说明副作用 | 🟡 手动检查源码后再评估 |
| 官方组织发布，有审计记录，scope 最小化 | 🟢 继续完整清单 |

三个红灯中任意一个触发，我通常直接跳过，而不是寻找变通方案。

---

## 12 项检查

### 1. 发布者来源

**看什么证据**

- 发布者是否有可追溯的 GitHub 组织或公司实体？
- npm / PyPI / 其他包注册表上的账号，注册时间、历史包、维护者数量是否可信？
- 项目是否有明确的负责人或安全联系方式（SECURITY.md 或 security policy）？

如果一个 Server 的唯一存在是一个三周前注册的 GitHub 账号推送的单一仓库，没有 issue 历史、没有 CI 记录，这不是"新项目"的正常样子，这是信任锚点缺失。

**什么情况应立即停止**

发布者无法被追溯到任何可验证的个人或组织；或者包名与知名工具高度相似但来自完全不同的账号——这是包名劫持（typosquatting）的经典模式。

---

### 2. 仓库与发布维护状态

**看什么证据**

- 源码仓库与发布到包注册表的内容是否一致？最简单的验证方式：把发布版本的 tarball 解压，对比仓库对应 tag 的源码，检查是否有额外的文件或混淆代码。
- 最近一次 commit 与最近一次 release 的时间差是否合理？一个六个月没有 commit 但昨天刚发了新版本的仓库值得警惕。
- 是否有 changelog，说明版本之间的变更？

**什么情况应立即停止**

发布包里包含未出现在仓库里的文件；或者仓库已被归档（archived）但包注册表仍在接受新版本推送。

---

### 3. 安装命令与版本固定

**看什么证据**

README 里的安装命令是否使用了浮动版本？

```bash
# 浮动版本 —— 每次执行可能拉取不同代码
npx -y some-mcp-server@latest

# 固定版本 —— 可追溯、可审计
npx -y some-mcp-server@1.2.3
```

`@latest` 在开发者体验上是便利设计，在安全模型里是一个持续开放的攻击面：任何一次恶意的发布更新，都会在下一次 Client 重启时自动被执行。

- 是否有 `package-lock.json` 或等价的锁文件机制保证可重现安装？
- 是否有 subresource integrity（SRI）或签名验证？

**什么情况应立即停止**

官方文档只提供 `@latest` 安装，且明确反对或没有提及版本固定——这说明发布者自己没有把版本一致性当成安全边界来对待。

---

### 4. 本地进程 vs 远程 Endpoint

**看什么证据**

MCP 常见传输包括本地 stdio（Server 作为本机进程运行）和远程 Streamable HTTP 等 Transport。两者的风险模型不同。

- **本地 stdio**：Server 作为本机进程运行。它的可达范围取决于启动方式、操作系统权限、环境变量传递和客户端隔离策略；MCP 协议本身并不提供主机沙箱。
- **远程 Streamable HTTP 等 Transport**：数据离开本地机器，经过网络传输。需要额外关注 TLS 配置、endpoint 归属和 session 管理。

MCP 官方安全规范特别指出了远程 Server 面临的 SSRF（Server-Side Request Forgery）风险：如果 Server 代理了网络请求，且没有对目标 URL 做白名单验证，攻击者可以构造请求让 Server 访问内部网络资源。参见 [OWASP SSRF 防御指南](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。

**什么情况应立即停止**

远程 endpoint 使用 HTTP 明文传输；或者文档没有说明 endpoint 归属于哪个组织/基础设施，只给了一个 IP 地址或无法追溯的域名。

---

### 5. 授权 Issuer 与 Redirect URI 验证

**看什么证据**

如果 Server 需要 OAuth 授权，检查以下几点：

- Authorization issuer 是否是你认识的可信 Identity Provider（如 GitHub、Google Workspace、企业 IdP）？还是一个你无法追溯的第三方？
- Redirect URI 是否被严格验证？MCP 官方 Authorization 规范要求 Server 必须精确匹配 redirect URI，不能使用模糊匹配或通配符。
- 授权流程是否发生在浏览器里的可见 URL 中，还是被一个中间页面代理，让你无法看到实际的 authorization endpoint？

MCP 官方安全规范把"authorization URL 验证"列为核心安全控制之一。Confused Deputy 攻击的一种变体，就是诱导合法的授权 Server 为攻击者代发 token——如果 redirect URI 没有被严格校验，这个链条就可能被利用。

**什么情况应立即停止**

你无法在浏览器地址栏看到完整的 authorization URL；或者授权页面要求你在第三方界面输入原始 credential（用户名+密码），而不是通过 Identity Provider 的标准 OAuth 流程。

---

### 6. 最小 Scope

**看什么证据**

授权请求的 OAuth scope，应当与 Server 声称提供的功能严格对应。

- 一个日历读取工具，是否请求了 `write` 或 `admin` scope？
- 一个代码搜索工具，是否请求了访问你邮件或云存储的 scope？
- Scope 是否在文档里有明确说明？还是只在授权弹窗里才第一次出现？

Claude Code 文档提到，项目级 MCP 配置支持在审批时指定 OAuth scope，这是客户端层面的 scope 约束机制。但这是客户端行为，不是所有 MCP 实现的通用特性——如果你使用的 Client 没有这个机制，scope 的边界完全由 Server 声明，你无法在客户端限制它。

MCP 官方安全规范明确要求实现最小权限原则：只请求完成任务所需的最小 scope，并向用户提供清晰的 scope 说明。

**什么情况应立即停止**

授权请求的 scope 超过工具描述功能所需；或者文档里找不到 scope 说明，只有一个"一键授权"按钮。

---

### 7. Secret 存储与 Token Audience

**看什么证据**

MCP Server 在运行时可能持有各种凭证：API Key、OAuth Access Token、Service Account 密钥。检查：

- Server 如何获取这些 Secret？是通过环境变量、配置文件，还是要求你在 tool 调用时直接传入？
- Token audience 是否被正确约束？MCP 官方安全规范特别警告了 token passthrough 问题：如果 Server 把它收到的 token 原样转发给第三方服务，而不是使用专属于该服务的 token，这会导致 token 的权限边界崩塌。
- API Key 是否以明文形式出现在配置文件里，并且这个配置文件会被纳入版本控制？

```json
// ❌ 危险：Secret 硬编码在配置里
{
  "env": {
    "API_KEY": "sk-realkey-hardcoded-here"
  }
}

// ✅ 更好：通过环境变量引用
{
  "env": {
    "API_KEY": "${MY_SERVICE_API_KEY}"
  }
}
```

**什么情况应立即停止**

Server 文档要求你把 API Key 直接写进 MCP 配置 JSON，而这个文件是项目级共享配置（意味着会进入代码仓库）；或者 Server 明确说明会把你的 token 转发给下游服务。

---

### 8. Tool 列表与副作用声明

**看什么证据**

MCP Server 提供的 Tool，是 Agent 在执行任务时可以直接调用的函数。你需要知道：

- Server 暴露了哪些 tool？tool 名称、参数、预期行为是否有完整文档？
- 每个 tool 是否区分了只读操作和写操作（副作用）？
- 有没有高权限操作（删除、修改、发布、转账）被包装成看起来无害的 tool 名称？

一个 file-search tool 如果实际上也有 `delete_file` capability，而这个能力没有在文档里明确说明，你的 Agent 可能在你不知情的情况下执行破坏性操作。

MCP 官方安全规范指出，MCP Client 应当在调用有副作用的 tool 之前向用户请求确认。但这同样是客户端行为，不是协议强制执行的——确认机制依赖于 Client 实现。

**什么情况应立即停止**

Server 没有公开 tool 列表；或者 tool 描述刻意模糊，无法判断它会修改还是只读目标资源。

---

### 9. 文件系统与网络访问范围

**看什么证据**

本地 MCP Server 的文件访问范围取决于启动用户、操作系统权限和客户端隔离策略。检查：

- Server 文档是否说明它只访问特定目录？是否有路径白名单？
- 如果 Server 需要读写文件，它是否只操作工作目录，还是会遍历任意路径？
- Server 是否会发起出站网络请求？请求目标是固定的域名列表，还是由 tool 参数动态指定？

Claude Code 文档提到，克隆仓库时应注意仓库内容可能携带项目级 MCP 配置；这类配置需要审批，不能依靠仓库中受版本控制的内容自行批准。这说明文件系统访问范围不只是 Server 的问题，也是 Client 加载策略的问题。

**什么情况应立即停止**

Server 源码里有遍历 `$HOME` 或 `/` 的逻辑，且没有明确说明这是必要功能；或者出站请求的目标 URL 完全由外部输入（tool 参数）控制，没有白名单验证。

---

### 10. Prompt Injection 与不可信内容路径

**看什么证据**

如果 MCP Server 会从外部来源获取内容——网页、文件、数据库记录、邮件正文——并把这些内容作为 tool 返回值交回给 Agent，就存在 Prompt Injection 风险。

攻击路径如下：攻击者在网页或文档里嵌入伪造的指令，Agent 读取这段内容时，把恶意指令当成合法任务执行。MCP 官方安全规范把这列为核心威胁之一。

检查：

- Server 是否会返回来自不可信来源的原始文本内容？
- 这些内容是否在返回给 Agent 之前做了任何过滤或转义？
- 文档里是否有关于 Prompt Injection 防御的说明？

目前没有任何客户端或服务端机制可以完全消除 Prompt Injection 风险，这是语言模型作为执行引擎的固有挑战。诚实的 Server 文档应当承认这一限制，而不是声称已经"解决"了这个问题。

**什么情况应立即停止**

Server 会把用户可写入的内容（如公开评论、任意 URL 返回的网页正文）直接注入 Agent 上下文，且没有任何内容隔离说明。

---

### 11. 日志与留存策略

**看什么证据**

- Server 是否记录 tool 调用日志？日志里是否包含完整的请求参数（可能含有敏感数据）？
- 日志存在哪里？本地文件、你控制的基础设施，还是发布者的云服务？
- 日志的留存周期是多少？是否有自动删除机制？
- 如果是远程 Server，发布者的隐私政策是否覆盖了 tool 调用数据？

很多 MCP Server 为了调试方便会记录详细日志，包括完整的工具调用参数。如果你通过 MCP Server 发送了包含个人数据、商业机密或认证信息的请求，这些数据可能以日志形式留存在你无法控制的地方。

**什么情况应立即停止**

远程 Server 没有隐私政策；或者文档明确说明 tool 调用会被记录并用于模型训练或产品改进，而你无法选择退出。

---

### 12. 停用、撤销、更新与事故响应

**看什么证据**

连接一个 MCP Server，不只是一个时间点的决策——它是一个持续的信任关系。检查：

- 如何撤销授权？OAuth token 是否可以在 Identity Provider 侧单独撤销，而不需要删除整个账号连接？
- 如何停用 Server？从配置文件里删除 Server 条目后，是否还有残留的 token 或 session 需要手动清理？
- Server 是否有安全更新通知机制（如 GitHub Security Advisory）？
- 如果你怀疑 Server 被攻陷，你能在 15 分钟内完成撤销和审计吗？

MCP 官方安全规范把 session hijacking 和本地 Server 被攻陷列为威胁模型的一部分。防御的终点不是"连上去"，而是"能快速切断"。

Claude Code 文档区分 local、project 和 user 三类配置 scope；应从实际使用的 scope 中移除或停用 Server。OAuth token 仍可能需要在对应的 Identity Provider 侧单独撤销——这两个动作都要做。

**什么情况应立即停止**

你无法找到撤销该 Server OAuth 授权的方法；或者停用 Server 需要联系发布者客服，而不是你自己能操作的界面。

---

## 风险 — 检查项映射

| MCP 官方威胁模型 | 对应清单项 |
|---|---|
| Confused Deputy | 5（授权 issuer）、6（最小 scope） |
| Token Passthrough | 7（Secret 存储与 token audience） |
| SSRF | 4（本地 vs 远程）、9（网络访问范围） |
| Session Hijacking | 4（传输方式）、12（撤销机制） |
| 本地 Server 被攻陷 | 1（发布者来源）、3（版本固定）、9（文件系统范围） |
| Prompt Injection | 10（不可信内容路径） |
| Authorization URL 操纵 | 5（redirect URI 验证） |
| 数据留存 | 11（日志与留存） |
| 供应链污染 | 2（仓库与发布维护）、3（安装命令）、8（tool 副作用） |

---

## 连接之后：持续监控与撤销

清单是连接前的门槛，不是一次性的护身符。连接后我会保持几个习惯：

**定期审查活跃 Server 列表。** 项目结束后没有用到的 Server，删掉配置条目，然后去 Identity Provider 里撤销对应的 OAuth token。留着"备用"的连接只是在扩大攻击面。

**关注 Server 的版本更新。** 如果你使用固定版本，需要主动订阅仓库的 release 通知（GitHub Watch → Releases only），以便在有安全补丁时及时跟进。

**异常 tool 调用留意。** 如果 Agent 日志里出现你没有主动触发的 tool 调用——尤其是涉及文件写入、网络请求或授权操作的——应当立即检查是否存在 Prompt Injection 或 Session Hijacking。

**演练撤销流程。** 不要等到出问题再去找撤销按钮。在初次连接后，确认一下撤销路径：配置文件在哪里、Identity Provider 的 Token 管理页面在哪里、删除后是否有残留状态需要清理。

---

## 一个关于"便利"的注脚

MCP 生态的增长速度很快，便利性是这种速度的驱动力之一。"一行复制即可使用"的体验设计是合理的——但它把信任决策隐藏在了便利性的背后。

我在任何热门徽章、高星数或"官方推荐"标签面前都会保持同样的核对习惯。热门不等于安全审计过，Star 数量不等于发布链安全，官方字样需要追溯到具体的组织和验证机制。

这张清单的目的不是让你拒绝所有第三方 MCP Server——那样会放弃这个工具生态里真实的生产力价值。它的目的是让你在连接之前，知道自己在把哪些信任交出去，以及在出问题的时候，你有没有能力快速切断和审计。

这是基本的供应链卫生，不是偏执。

---

## 参考资料

- [MCP 官方安全最佳实践](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices) — 覆盖 confused deputy、token passthrough、SSRF、session hijacking 和 authorization URL 验证
- [MCP 官方 Authorization 规范](https://modelcontextprotocol.io/specification/latest/basic/authorization) — Authorization 流程、scope 与安全要求
- [Claude Code：MCP 配置文档](https://code.claude.com/docs/en/mcp) — local/project/user scope、项目级审批、OAuth scope 与 stdio proxy
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — SSRF 防御的通用指导原则

## 相关指南

- [Claude Code 的 Skills、Hooks 和 MCP](/zh/docs/tutorials/claude-code-skills-hooks-mcp/)
- [Coding Agent 沙箱安全指南](/zh/docs/tutorials/coding-agent-sandbox-security/)
