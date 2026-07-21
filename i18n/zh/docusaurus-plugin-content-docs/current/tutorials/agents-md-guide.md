---
title: "AGENTS.md 完整指南：让 Coding Agent 真正读懂仓库规则"
description: "学习如何编写根目录与嵌套 AGENTS.md，理解 Codex 文件发现、优先级、Override、常见错误和维护方法。"
keywords:
  - AGENTS.md 指南
  - Codex AGENTS.md
  - Coding Agent 仓库规则
  - Codex 项目指令
  - 嵌套 AGENTS.md
sidebar_position: 15
tags: [tutorial, codex, agent-engineering, workflow]
---

# AGENTS.md 完整指南：让 Coding Agent 真正读懂仓库规则

---

## 一次让我印象深刻的错误

那次 PR 的来源是一个我觉得设置得相当完善的项目——monorepo，前端、后端、基础设施三个子目录，各自有独立的构建脚本。我让 Codex 在 `backend/` 里修复一个数据库迁移的 Bug。它改对了逻辑，还顺手在根目录运行了 `npm run build`。

不是 `pnpm`，不是 `make build-backend`，是 `npm run build`。那个命令触发的是前端全量打包，耗时四分钟，产出物落到了后端目录完全无法识别的路径下。

Agent 的选择在"局部"是合理的：它看到了 `package.json`，判断这是 JavaScript 项目，选了最常见的构建命令。但在仓库层面是错的，因为正确的构建命令、工作目录约束、子目录边界——从来没有放在它能发现的位置。

这就是 `AGENTS.md` 要解决的问题。

---

## AGENTS.md 是什么，不是什么

`AGENTS.md` 是一个普通的 Markdown 文件，没有强制字段，没有特殊语法。根据 [agents.md](https://agents.md) 整理的数据，目前已有超过 60,000 个开源项目在使用它（此数字系该站点统计，请以访问时实际数据为准）。

它的定位不是 README 的替代，也不是任务 Prompt。对 Codex 来说，它是仓库级指令，在每次运行时按发现规则装载进指令链。

区分几个容易混淆的概念：

| 概念 | 生命周期 | 目的 | 典型内容 |
|---|---|---|---|
| **AGENTS.md** | 持久，随代码库版本化 | 仓库级约束与约定 | 构建命令、目录规则、生成文件策略 |
| **Memory（记忆）** | 持久，跨会话保存到 Agent 存储 | 用户偏好与长期学习 | 格式偏好、个人习惯 |
| **Skill（技能）** | 持久，可复用的能力包 | 特定任务的操作能力 | 如何使用某 CLI 工具 |
| **README / Docs** | 持久，面向人类读者 | 项目说明与使用文档 | 安装步骤、架构说明 |
| **任务 Prompt** | 一次性，当次运行 | 描述当前要完成的具体任务 | "修复 issue #42" |

AGENTS.md 的核心价值是**稳定性和可版本化**：团队通常让它随着代码库演进并接受 review。项目更换构建工具后，更新对应规则可以让后续 Codex 运行读取新的指令。

---

## Codex 的文件发现机制（Codex-specific）

以下优先级规则明确针对 OpenAI Codex，其他 Coding Agent 的实现可能不同，不能一概而论。

Codex 在每次运行或会话开始时，从 **repository root** 出发，逐级向下走到当前工作目录，沿途收集指令文件，最终组合成完整的指令链。

**每个目录只会选择一个文件，选择顺序如下：**

1. `AGENTS.override.md`（在 Codex 全局层级中，此文件优先级高于 `AGENTS.md`）
2. `AGENTS.md`
3. 配置中指定的 fallback 文件（如有）

**覆盖规则：越近的指令覆盖越宽泛的指令。**

这意味着子目录指令会覆盖根目录中的冲突规则；根目录里没有被覆盖的规则仍然生效。同一目录如果存在 `AGENTS.override.md`，该目录的普通 `AGENTS.md` 会被跳过。

组合后的指令链默认上限为 **32 KiB**（此为当前文档记录的默认值，可能随版本变化，请以 [OpenAI Codex 官方文档](https://developers.openai.com/codex/guides/agents-md) 为准）。

用目录树直观呈现：

```
my-repo/
├── AGENTS.md              ← ① 首先读取（根层级指令）
├── frontend/
│   ├── AGENTS.md          ← ③ 如果工作目录在 frontend/ 下则读取
│   └── src/
├── backend/
│   ├── AGENTS.override.md ← ② override 存在时，同级 AGENTS.md 被跳过
│   └── src/
└── infra/
    └── （无 AGENTS.md）   ← 此目录直接跳过，继承根层级规则
```

**关键推论：文件位置本身就是指令设计的一部分。**

如果你希望某条规则在整个仓库范围内生效，它应该在根目录的 `AGENTS.md` 里。如果你希望某条规则只在 `backend/` 内覆盖全局默认，它应该在 `backend/AGENTS.md` 里。如果你希望某条规则在紧急情况下临时强制执行，可以使用 `AGENTS.override.md`。

此外，`/init` 命令可以让 Codex 基于现有仓库结构生成 `AGENTS.md` 的初始版本，作为起点使用，之后仍需人工审核和补充。

---

## 根 AGENTS.md 应该写什么

根文件是整个指令链的基础，应该包含那些**全局稳定、普遍适用**的内容。以下六类内容是根文件的核心职责：

### 1. 构建与验证命令

这是最容易被猜错的部分。明确写出 Agent 在修改代码后应该运行哪些命令：

```markdown
## 构建与验证

- 安装依赖：`pnpm install`
- 运行测试：`pnpm test`
- 类型检查：`pnpm typecheck`
- Lint：`pnpm lint`
- 不要运行 `npm` 或 `yarn`，本项目使用 pnpm
```

注意：命令要具体，要可以直接复制粘贴执行。

### 2. 目录结构与职责边界

让 Agent 知道哪个目录负责什么，以及跨目录的规则：

```markdown
## 目录职责

- `frontend/` — Next.js 应用，构建产物输出到 `frontend/.next/`
- `backend/` — FastAPI 服务，不要在此目录运行前端构建命令
- `infra/` — Terraform 配置，不要在 CI 之外执行 apply
- `packages/shared/` — 跨前后端共享类型定义
```

### 3. 不变量与约束

那些无论做什么修改都必须保持的规则：

```markdown
## 不变量

- 所有公开 API 端点必须有对应的 OpenAPI 注释
- `backend/migrations/` 中的文件不能被修改，只能新增
- 不能直接修改 `packages/shared/generated/` 中的文件，它们由代码生成工具产出
```

### 4. 生成文件规则

Agent 需要知道哪些文件是生成的，哪些是手写的，以及如何触发重新生成：

```markdown
## 生成文件

以下文件由工具自动生成，不要手动编辑：
- `packages/shared/generated/` — 运行 `pnpm codegen` 更新
- `backend/app/openapi.json` — 运行 `pnpm generate-schema` 更新

如果你的修改影响了 API schema，必须重新运行对应的生成命令。
```

### 5. 验证步骤

除了单元测试，还有哪些验收标准：

```markdown
## 验收标准

修改 backend/ 时：
1. 运行 `pnpm test:backend`
2. 如果修改了 API，运行 `pnpm generate-schema` 并将更新后的 openapi.json 一起提交

修改 packages/shared/ 时：
1. 运行 `pnpm codegen`
2. 运行 `pnpm typecheck` 确认前后端类型一致
```

### 6. 范围限制

告诉 Agent 它不应该触碰的区域：

```markdown
## 范围限制

- 不要修改 `.github/workflows/` 中的文件，除非任务明确要求
- 不要修改根目录的 `package.json` 中的 `engines` 字段
- `CHANGELOG.md` 由发布脚本维护，不要手动编辑
```

---

## 何时增加嵌套 AGENTS.md

嵌套文件的使用原则是：**只有当子目录真的不同，才值得增加一个嵌套文件。**

**适合嵌套的情况：**

- 子目录使用了不同的编程语言或工具链（例如根目录是 Node.js，但 `ml/` 是 Python）
- 子目录有独立的测试框架或构建系统
- 子目录的代码规范与根目录有明显差异
- 子目录有特殊的安全约束，需要比根目录更严格的规则

```
# backend/AGENTS.md 示例（覆盖根目录的构建命令）

## 构建与验证（覆盖根目录规则）

本目录使用 Python 工具链，不适用根目录的 pnpm 命令。

- 安装依赖：`uv sync`
- 运行测试：`uv run pytest`
- 类型检查：`uv run mypy .`
```

**容易制造矛盾的情况：**

- 嵌套文件重复了根目录的规则但措辞略有不同，导致 Agent 不确定哪个优先
- 嵌套文件覆盖了应该全局一致的规则（例如 Git commit message 格式）
- 多个嵌套文件互相引用对方目录的规则，产生循环依赖

一个检验方法：如果你必须在两个 AGENTS.md 文件里同步更新同一条规则，那这条规则大概率应该只存在于更高层级的文件里。

---

## 常见错误类型

我在维护多个被 Agent 使用的仓库时，见过以下几类反复出现的错误：

### 错误一：模糊规则

❌ `尽量保持代码简洁`<br />
✅ `函数体不超过 50 行；超过时拆分为独立函数并编写对应测试`

Agent 需要可判断、可验证的规则。"尽量"、"适当"、"合理"这类词对它没有意义。

### 错误二：过期命令

❌ `运行 yarn install`（但项目已迁移到 pnpm）<br />
✅ 定期审计 AGENTS.md，每次更换工具链时同步更新

过期命令比没有命令更糟糕——它会让 Agent 产生错误的置信度。

### 错误三：巨量背景

❌ 把架构 ADR、历史决策、未来规划全部塞进 AGENTS.md

AGENTS.md 是给 Agent 读的，不是给人类读的归档文档。背景越多，关键规则越容易被淹没，也越容易撞上 32 KiB 的组合上限。

### 错误四：重复与矛盾

❌ 根目录写"使用 2 空格缩进"，`frontend/AGENTS.md` 写"使用 4 空格缩进"，但 `frontend/` 里也有根目录约束的文件

这类矛盾会导致 Agent 行为不一致，且问题极难排查，因为它不会报错，只会"选择"。

### 错误五：包含 Secret

❌ `OPENAI_API_KEY=sk-xxxxxx`

AGENTS.md 通常会随版本库维护，并被装载进 Agent 上下文。任何密钥、凭证或内部 Secret 都不应该出现在这里。

### 错误六：不可验证的指令

❌ `确保所有改动都经过充分测试`<br />
✅ `运行 pnpm test，确认所有测试通过，覆盖率不低于 80%`

指令应该是 Agent 能够执行并自行验证结果的操作，而不是需要主观判断的要求。

---

## 最小可用模板

以下是一个适合中小型项目的根 `AGENTS.md` 起始模板：

```markdown
# AGENTS.md

本文件为 AI Coding Agent 提供仓库级指令。

## 工具链

- Node.js 20+，包管理器：pnpm 9
- 不要使用 npm 或 yarn

## 常用命令

| 任务 | 命令 |
|---|---|
| 安装依赖 | `pnpm install` |
| 运行所有测试 | `pnpm test` |
| 类型检查 | `pnpm typecheck` |
| Lint | `pnpm lint` |
| 构建 | `pnpm build` |

在提交任何代码修改前，必须确认 `pnpm test` 和 `pnpm typecheck` 均通过。

## 目录结构

```
src/          应用主体代码
src/generated/ 自动生成，不要手动编辑（运行 pnpm codegen 更新）
tests/        单元测试和集成测试
docs/         面向人类的文档，不是指令
```

## 不变量

- `src/generated/` 中的文件只能通过 `pnpm codegen` 更新
- 公开函数必须有 JSDoc 注释
- 不要修改 `CHANGELOG.md`，由发布脚本维护

## 范围限制

- 不要修改 `.github/workflows/`，除非任务明确涉及 CI/CD
- 不要修改根目录 `package.json` 中的 `engines` 字段

## 提交规范

遵循 Conventional Commits：`type(scope): description`<br />
示例：`fix(auth): 修正 token 过期时间计算错误`
```

---

## 排错步骤

当你发现 Agent 没有遵循 AGENTS.md 中的规则时，按以下顺序排查：

**步骤 1：确认文件位置**<br />
Agent 的工作目录在哪里？从那个目录向上到 repository root，沿途是否都有正确的文件？

**步骤 2：检查文件名大小写**<br />
文件名必须是 `AGENTS.md`（全大写），而不是 `agents.md` 或 `Agents.md`。Codex 对文件名大小写敏感。

**步骤 3：检查是否超出大小限制**<br />
如果组合后的指令链超过 32 KiB，部分内容可能被截断。用以下命令粗略估算：

```bash
# 估算从根目录到当前目录的 AGENTS.md 总大小
find . -name "AGENTS.md" | xargs wc -c
```

**步骤 4：检查矛盾规则**<br />
搜索所有 AGENTS.md 文件，找出同一主题的重复描述：

```bash
# 找出所有包含"构建"相关内容的 AGENTS.md
grep -r "build\|构建\|install\|安装" --include="AGENTS.md" .
```

**步骤 5：简化规则表述**<br />
如果规则中包含条件句、例外情况或模糊词，尝试重写为无歧义的命令式表述。

**步骤 6：验证任务 Prompt 没有覆盖**<br />
任务 Prompt 的优先级高于 AGENTS.md。如果你在 Prompt 中给出了与 AGENTS.md 矛盾的指令，Prompt 会胜出。

---

## 维护清单

AGENTS.md 的质量会随时间衰减，定期维护是必要的。建议在以下时机检查：

**每次工具链变更时：**
- [ ] 构建命令是否仍然有效？
- [ ] 包管理器是否变了？
- [ ] 测试命令或参数是否有变化？

**每次目录结构调整时：**
- [ ] 目录职责描述是否仍然准确？
- [ ] 生成文件的路径是否有变化？
- [ ] 是否需要增加或删除嵌套的 AGENTS.md？

**每个季度（或每次重大重构后）：**
- [ ] 整体大小是否合理？（建议根文件控制在 2 KiB 以内）
- [ ] 是否有已失效的不变量？
- [ ] 是否有过期的范围限制（例如"不要修改 v1 API"但 v1 已经删除）？
- [ ] 嵌套文件之间是否有新出现的矛盾？

**一个实用习惯：** 把 AGENTS.md 的 review 加入 Pull Request 的 checklist。每当有人修改了构建脚本、包管理器配置或目录结构，同时更新 AGENTS.md。把它当作代码的一部分对待，而不是一次性写好的文档。

---

## 跨 Agent 兼容性的注意事项

虽然越来越多的 Coding Agent 开始支持 AGENTS.md，但需要明确的是：**本文中关于文件发现顺序、优先级机制和大小限制的描述，明确针对 OpenAI Codex。**

其他 Agent（如 GitHub Copilot Workspace、Cursor、各类基于 API 的 Agent 框架）对 AGENTS.md 的处理方式可能不同，也可能使用不同的配置文件名。在多 Agent 环境中使用时，建议：

- 将核心规则写成对所有工具都成立的表述（例如"构建命令是 `pnpm build`"，而不是依赖某个 Agent 的特定行为）
- 在根 AGENTS.md 里注明该文件主要面向哪些 Agent，避免歧义
- 不要假设优先级机制在不同 Agent 之间是一致的

---

## 结语

回到最开始的那次错误：`npm run build` 在根目录运行了四分钟，产出了没人需要的文件。

这件事之后我在根 `AGENTS.md` 里加了一张五行的命令表，和一条"不要在 `backend/` 目录运行前端相关命令"的约束。此后处理同类任务，Agent 不再猜测构建命令。

AGENTS.md 没有魔法。它就是一个 Markdown 文件，放在 Agent 能发现的路径上，写着稳定、可验证、无歧义的规则。难的不是语法，是纪律：在规则失效时去更新它，在矛盾出现时去解决它，在文件变大时去精简它。

把稳定的仓库级命令、约束和约定放进精简的根 AGENTS.md；只有子目录真的不同才增加嵌套文件。对 Codex 来说，从 root 到当前目录的发现顺序和近处覆盖远处的规则，意味着文件位置本身就是指令设计的一部分。

---

*参考资料：*
- *[OpenAI Codex AGENTS.md 指南](https://developers.openai.com/codex/guides/agents-md)*
- *[agents.md — 开源项目使用统计](https://agents.md)*

## 相关指南

- [Coding Agent 的记忆应该保存什么？](/zh/docs/tutorials/coding-agent-memory/)
- [用 GitHub Spec Kit 做规格驱动开发](/zh/docs/tutorials/spec-driven-development-guide/)
