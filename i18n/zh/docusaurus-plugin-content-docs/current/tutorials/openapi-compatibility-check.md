---
title: "OpenAPI 改了，旧客户端会不会坏？用 oasdiff 给 AI 一份具体修复清单"
sidebar_label: "OpenAPI 兼容检查"
description: "用 oasdiff 检查 OpenAPI 破坏性变更，定位受影响的旧客户端请求，再把差异交给 AI 完成针对性修复。"
keywords: ["OpenAPI", "oasdiff", "API compatibility", "AI coding agent"]
sidebar_position: 44
tags: ["tutorial", "agent-engineering"]
---

# OpenAPI 改了，旧客户端会不会坏？用 oasdiff 给 AI 一份具体修复清单

当你在 Git 里提交了一版新的 `openapi.yaml`，服务端的契约已经“进化”了，可你的调用方——无论是遗留的 TypeScript 客户端、老旧的 Python 库，还是第三方系统——还守着旧的定义在跑。

这时候最关键的问题不是“接口变没变”，而是：
- **旧客户端发出的有效请求，在新契约下是否仍然被接受？**
- **如果不再被接受，具体是哪些字段、哪些行为出了问题？**
- **如何把这些差异转成 AI 能执行的修复任务清单？**

本文带你从零理清这些问题，并手把手用 `oasdiff` 构建一条从“发现变化”到“生成修复任务再到 CI 收口”的可落地流程。

---

## 一、问题拆解：当 OpenAPI 从 base 变成 revision

先看一个最经典的场景（官方示例，直接复现）：

- 旧契约只要求 POST `/products` 携带 `name`
- 新契约新增了一个字段 `description`，并且把它标记为 required

```yaml
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /products:
    post:
      operationId: addProduct
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
              required:
                - name
      responses:
        '200':
          description: OK
```

```yaml
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /products:
    post:
      operationId: addProduct
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
              required:
                - name
                - description
      responses:
        '200':
          description: OK
```

旧客户端请求：

```json
{ "name": "Notebook" }
```

直观来看：
- 在新契约中，它缺少 `description`，因此违反了 schema。
- 但服务端的 HTTP 行为并不等于“拒绝”或“报错”；服务可能：
  - 真的校验并返回 400/422
  - 或者更隐蔽地默认一个值
  - 甚至为了兼容悄悄接受但后续逻辑有问题

**结论：**
> “服务端仍接收这个请求” ≠ “旧请求在新契约下是有效的”。
> 我们要用契约（OpenAPI）作为判断基准，而不是服务端的实际容忍度。

---

## 二、工具准备：oasdiff 的正确姿势

为了获得可复现的分析结果，本文所有示例均固定使用 **oasdiff v1.33.0**（发布页：[https://github.com/oasdiff/oasdiff/releases/tag/v1.33.0](https://github.com/oasdiff/oasdiff/releases/tag/v1.33.0)）。建议通过该 Release 页面下载与你的操作系统和架构匹配的压缩包并解压到系统 PATH，然后用 `oasdiff --version` 确认实际版本。仅依赖未固定版本的安装方式（例如某些包管理器的自动安装）无法保证恰好命中 v1.33.0，因此文档中的命令和规则说明均基于该特定版本行为。

oasdiff 的输入文件顺序会影响判断结果：第一个参数视为“旧/基线”（base），第二个参数视为“新/变更”（revision）。  
- `breaking` 按语义规则判定变更是否可能破坏调用方。  
- 默认 diff 报告包含纯描述字段、example 文档等变化，但不会引入 ERR/WARN/INFO 等级；INFO 及以上级别的变化会在 changelog 中汇总。  
- `--fail-on ERR`：只有当触发 ERR 类失败条件时退出码为 1；0 表示未触发该失败策略。  
- `--fail-on WARN`：将 WARN 及更高严重性的规则也视为失败条件。

此外，oasdiff 的调用失败也可能表现为非零退出码但不代表“契约破坏”，常见说明包括：参数错误（如 101）、Spec 加载失败（如 102）、glob 路径无匹配（如 103）。详细含义可参考其官方说明：[https://github.com/oasdiff/oasdiff/blob/v1.33.0/docs/ERRORS.md](https://github.com/oasdiff/oasdiff/blob/v1.33.0/docs/ERRORS.md)。  
在实际工作中，契约检查与对真实服务的兼容性测试应分开执行，分别验证“定义是否被破坏”和“运行时行为是否正确”。

## 三、实战：用 oasdiff 看新旧契约的差异

我们用一个贴近现实的场景演示：  
- 旧契约只要求 POST `/products` 携带 `name`
- **新契约（revision）**：在同样接口上增加了 `description` 字段，并将其标记为必填（required）。请求体采用内联 schema，没有使用 components。

这意味着旧版请求体：
```json
{"name":"Notebook"}
```
仍然符合 base，但在新 revision 中会因为缺少必填的 `description` 而被视为不合规。oasdiff 正是用来在发布前提前捕捉这类定义层面的变更。

运行检查命令：
```bash
oasdiff breaking --fail-on ERR openapi-base.yaml openapi-revision.yaml
```

报告的核心语义可以概括为（实际终端输出以你运行的报告为准）：
- 涉及操作：`POST /products`  
- 变化点：在请求体 schema 中新增字段 `description`，并设置其规则为“必填”  
- 影响判断：旧版请求体缺少该字段，因此在新契约下不再合规；这属于“新增必填约束”，而不是“把原有可选字段改成必填”。  
- 这是 ERR 级别的变化，建议纳入 CI 失败策略。

关于 oasdiff 的语义分级：
- **ERR**：可被明确判定为破坏性变更。  
- **WARN**：仅凭契约定义无法程序性确定是否一定会造成破坏，需要结合实现代码或运行时约束进一步评估。  
各条规则会区分请求/响应方向，并受你配置的级别策略影响；不要把“readOnly 变动”或“枚举边界微调”自动等同于 WARN，应以报告给出的分类为准。

## 四、把“差异”变成 AI 可执行的修复清单

现在你手里有：
- 两份 spec：base / revision
- 一份 oasdiff 报告（包含具体字段/路径）
- 还知道旧客户端的请求样例

接下来，给一个 Project Agent / Coding Agent 输入时，要让它“看得懂”并且“输出可验证的修复方案”。推荐的结构如下（可直接作为 prompt 模板）：

```text
Role: API compatibility remediation engineer.

Context:
- Old OpenAPI: openapi-base.yaml
- New OpenAPI: openapi-revision.yaml
- oasdiff report: attached (breaking diff)
- Known legacy client request: { "name": "Notebook" } for POST /products

Goal:
1) Explain, in plain language, which requests/fields are affected.
2) Propose minimal changes to make the system compatible while respecting business intent.
3) Define acceptance criteria for both:
   - Legacy clients still work (backward compatibility)
   - New clients and new fields work correctly

Inputs:
- Base spec, Revision spec, oasdiff output, legacy request samples, relevant handler/client code paths.

Output format:
- Affected endpoints & properties (with source from specs)
- Root cause (breaking rule + why it breaks)
- Minimal fix options (e.g., keep description optional / explicit deprecation plan)
- Verification plan:
  - Contract-level: oasdiff commands to run in CI
  - Real-world: test cases / integration steps to confirm backward behavior

Constraints:
- If new field is truly required, define migration timeline and versioning policy.
```

AI 的任务通常包括：
- 判断是“新 required”、“新 enum”、“新 readOnly”等哪一类破坏。
- 结合业务需求给出方案：
  - 最小兼容：保留 description 为 optional，并确认服务端如何对待缺失值。
  - 强制要求：明确新字段必填，同时给出客户端升级计划（版本号、灰度、迁移脚本）。

---

## 五、CI 集成：让契约检查成为“质量门禁”

在典型的 Git 工作流中，我们假设项目中的 OpenAPI 文件名为 `openapi.yaml`，基线来自远程分支 `origin/main`，待检查的新定义是当前工作树中的 `openapi.yaml`。在 CI 或本地验证时，可先确保基线已同步到位，再执行检查：
```bash
git fetch origin main
oasdiff breaking --fail-on ERR origin/main:openapi.yaml openapi.yaml
```
这里的 `origin/main:openapi.yaml` 表示从已经获取的远程对象中读取该文件内容，当前工作树的 `openapi.yaml` 作为新契约。团队务必确认所比较的基线确实对应要纳入检查的发布/PR 基线，避免因为分支切换或标签未更新导致误判。

在 CI 流水线中：
- 将上述命令作为一步执行，并让命令的退出码直接决定该步骤是否失败；  
- 若希望进一步阻止合并，可将此检查配置为必需的状态检查（required status check）或分支保护条件；  
- 注意：退出码 0 仅表示“本次检查未触发失败”，并不等同于业务测试通过或功能正确，因此应将其定位为“契约质量门禁”，而非“功能验证”。

以 DependencyTrack 公开的 CI workflow 为例（来源：[https://github.com/DependencyTrack/dependency-track/blob/a26075bf4bd1b7665d464f2a08ecfd8a0f063c65/.github/workflows/ci-lint.yaml](https://github.com/DependencyTrack/dependency-track/blob/a26075bf4bd1b7665d464f2a08ecfd8a0f063c65/.github/workflows/ci-lint.yaml)）：
- 它会将 PR 的 base SHA 检出到 `base` 目录，然后使用 Action 比较：
  - 基线：`base/api/src/main/openapi/openapi.yaml`  
  - 当前：`api/src/main/openapi/openapi.yaml`  
- 配置中包含 `fail-on: ERR` 策略，用于在检测到破坏性变更时阻断流水线；  
- 该文件证明了“如何配置检查”，但不能据此直接推定某个仓库已经启用了合并保护——分支保护规则和 PR 策略仍需在仓库设置中独立配置。  
同时需注意，Action 中的版本声明与本文 CLI 的 v1.33.0 是相互独立固定的，引用时保持一致性有助于问题排查与复现。

## 六、验收策略：从契约到真实请求的闭环

验收分两层，缺一不可。

第一层：契约对比
- 基线定义始终是 `openapi-base.yaml`，当前提议或修复版本为 `openapi-revision.yaml`。
- 使用命令：
  - 严格失败模式：`oasdiff breaking --fail-on ERR openapi-base.yaml openapi-revision.yaml`
  - 若团队选择纳入 WARN 级别的兼容风险：`oasdiff breaking --fail-on WARN openapi-base.yaml openapi-revision.yaml`
- diff 的核心用途是审阅“定义差异”，而不是把带 ERR/WARN/INFO 的输出当作 changelog。

第二层：真实请求侧验证
- 在对应项目的测试环境中，验证三类场景：
  1) 旧风格请求：仅传 `name`，确认在修复策略下仍按业务逻辑有效。
  2) 新风格请求：携带 `description`，确认正确写入并返回。
  3) 混合场景：确保新字段不影响已有流程、幂等性与错误码一致性。
- HTTP 200 只是及格线之一；必须结合真实业务条件（如库存校验、审批流、权限控制）进行综合判定。

验收清单示例：
- [ ] 当前修复的 `openapi-revision.yaml` 在所选兼容策略下不触发失败（ERR/WARN 按约定处理）。
- [ ] 旧请求 `{ "name": "Notebook" }` 在服务端仍按业务规则被正确接收并执行。
- [ ] 新请求携带 `description` 后，行为正确、可追溯、不影响回滚路径。
- [ ] 本次提交（PR）涉及的改动在测试环境中被完整覆盖，而非仅依赖 `main` 的间接表现。

注意：示例 OpenAPI 文档只约定 200 为成功响应，不代表运行时结果；务必配合自动化测试与合同测试（contract test）落地验证。

## 七、常见误区与判断要点（短平快）

- **误区1：“服务还能收，就不算坏”**
  - 事实：服务端可能默认值、静默降级或后续校验失败。要以契约为准。
- **误区2：“只要旧请求能通就行”**
  - 事实：你同时要考虑新客户端和新字段的兼容性，尤其是向后兼容的边界条件。
- **误区3：“oasdiff 输出越复杂越好”**
  - 事实：聚焦 `breaking` + `--fail-on ERR`，在 CI 里用简单的命令和明确的失败策略。
- **误区4：“新 required 带 default 就不用管旧客户端”**
  - 事实：即使有 default，只要该字段进入 schema 且标记为 required，旧请求仍视为不满足契约；是否需要默认取决于业务决定。

---

## 八、下一步：从契约到代码生成与适配

当你已经：
- 跑通了 oasdiff 检查流程
- 明确了破坏性变化并给出修复方案
- 在 CI 中设立了契约门禁

就可以把 OpenAPI 更深入地接入开发流，例如使用本站的工具生成初始客户端，减少手工对接带来的偏差：

- https://tools.aicoding.club/openapi-client/

这类工具的任务是“代码生成”；而本文所讲的这套流程，是为生成后的客户端、服务以及整个项目生态提供“兼容性保障”和“变更治理”。

---

## 九、小结（30 秒内记住）

- OpenAPI 的变化有三种：兼容变化、破坏性变化和纯文档变化，不能一有变更就判定“不兼容”。
- 用 `openapi-base.yaml` / `openapi-revision.yaml` 加上 oasdiff 报告，精准定位受影响的 operation 与字段。
- 把具体旧请求、业务条件与真实服务代码交给编程 Agent，让它输出可执行的修复清单。
- 修复后同时做两件事：契约层面的对比验证，以及真实请求行为的端到端验证。
- 回到你的项目：选对策略、跑对命令、测对场景，而不是盯着报告里的一行 WARN 纠结。

