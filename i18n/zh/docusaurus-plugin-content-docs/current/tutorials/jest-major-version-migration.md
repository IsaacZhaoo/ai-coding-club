---
title: "Jest从29升到30，怎样让AI改代码又保住测试的意思？"
sidebar_label: "Jest 29 升级到 30"
description: "参考 NestJS 升级案例，用 AI 迁移 Jest 29 到 30 的 matcher 别名和 CLI 参数，同时保留测试意图与业务预期。"
keywords: ["Jest 30", "Jest migration", "AI coding agent", "test migration"]
sidebar_position: 45
tags: ["tutorial", "agent-engineering"]
---

# Jest从29升到30，怎样让AI改代码又保住测试的意思？

如果你有一个稳定的 Jest 29 项目，已经跑满测试、CI 绿勾不断，现在突然要升级到 Jest 30，最让人不安的往往不是版本号本身，而是那些藏在断言里的“默契”——旧版别名、隐式枚举属性、宽松的匹配逻辑……一旦版本切换，AI 改写代码时若只按字面替换，很容易把“语义正确”改成了“语法正确”。

本文基于真实 NestJS 升级 PR#15268（sample/05-sql-typeorm）的改动细节，结合官方文档与工程实践，告诉你如何指导 AI 在升级中精准迁移测试：只改必须改的，不触碰业务预期；改完有依据，跑得快，还有 CI 兜底。

---

## 一、先搞清楚：Jest 30 到底改了哪些“坑”？

根据官方升级指南（[https://jestjs.io/docs/upgrading-to-jest30](https://jestjs.io/docs/upgrading-to-jest30)），Jest 30 的核心变更集中在三点：

- **移除旧 matcher 别名**：例如 `toBeCalledWith` → `toHaveBeenCalledWith`，保持功能一致但名称统一。
- **CLI 参数微调**：`--testPathPattern`（单数）→ `--testPathPatterns`（复数），支持多个模式拼接，仍按文件路径过滤而非测试函数名。
- **底层行为收紧**：对象 matcher（如 `toHaveBeenCalledWith`）默认排除不可枚举属性；TypeScript 类型推断更严格；环境依赖更新（如 jsdom 相关变化）。

> 💡 关键认知：这些改动需细分为“机械性”调整与运行时行为变更。别名替换通常属于前者；对象 matcher 排除不可枚举属性、CalledWith 类型严格化和 JSDOM 差异则可能影响断言逻辑或执行表现，应单独评估其业务语义影响。

---

## 二、用真实案例看清迁移细节（NestJS sample）

在 NestJS PR#15268 中，`sample/05-sql-typeorm` 从 Jest 29.7.0 升级到 30.2.0，类型包同步更新。代码改动极其克制，仅两处 matcher 名称：

```diff
-expect(repoSpy).toBeCalledWith({ id: 1 });
+expect(repoSpy).toHaveBeenCalledWith({ id: 1 });

-expect(removeSpy).toBeCalledWith('2');
+expect(removeSpy).toHaveBeenCalledWith('2');
```

这里 `repoSpy` 是 `repository.findOneBy` 的 spy，`removeSpy` 是 `repository.delete` 的 spy。  
**运行效果完全一致**——因为 Jest 30 明确保证 canonical 名称功能等价。

这给我们一个清晰的工作流：

1. **确认迁移类型**：机械别名替换 vs 语义行为变化
2. **定位改动范围**：用 CLI 工具先看清“跑什么”
3. **指导 AI 输出最小 diff**：只改必要行，保留注释与结构
4. **验证闭环**：测试范围、断言、类型、CI 四重核验

---

## 三、第一步：让 AI 知道“我们跑哪些测试”

在升级前，先固化测试范围。Jest 30 的筛选逻辑仍基于文件路径，因此可用 `--listTests` 生成执行清单：

```bash
npm test -- --listTests
```

对比升级前后的输出，确保：
- 路径模式未断裂（如 `src/**/*.spec.ts`）
- 新引入的测试文件未被遗漏
- 脚本参数传递正确（如 `--testPathPatterns "users.service.spec.ts"`）

> ⚠️ 注意：`--listTests` 不执行断言，仅扫描匹配的文件。它与 CI 入口的“实际运行”是不同验证层，不可互相替代。

---

## 四、第二步：用 AI 做“有约束的改写”，而不是“全自动替换”

当你把代码交给 AI Agent，不要只说：“帮我升级到 Jest 30。”  
要提供结构化上下文，让 AI 知道迁移的规则边界。例如：

> “基于 Jest 29→30 升级指南（尤其是 matcher 别名和 CLI 参数变更），将以下测试文件机械更新为 Jest 30 兼容版本。要求：
> - 仅替换已废弃的 matcher 名称（如 toBeCalledWith → toHaveBeenCalledWith）；
> - CLI 调用中，若环境为 Jest 30，请显式将旧版 --testPathPattern 参数更新为 --testPathPatterns；不依赖未经验证的自动映射。
> - 保留所有业务断言参数、顺序和调用次数预期；
> - 输出最小 diff，并标注每项改动依据。”

下面实际展示的是 `package.json` 里 Jest 和 @types/jest 的依赖版本字段（ts-jest 本身并未额外增加 transform 配置行）：

```diff
- "jest": "29.7.0",
+ "jest": "30.2.0",

- "@types/jest": "29.5.14",
+ "@types/jest": "30.0.0",
```

以及测试代码的精准替换（如上 NestJS 案例所示）。  
**关键点：AI 不应“脑补”新增断言或修改参数值，除非有明确的类型错误证据。**

---

## 五、第三步：升级后四重核验清单

改完不是终点。按顺序完成以下检查，确保“跑得快 + 断得准”：

1. **Manifest & Lock 对齐**  
   执行 `npm install`（或对应包管理器），确认版本解析符合预期。  
   检查 `package-lock.json` 或 `yarn.lock` 中 Jest 相关条目是否为稳定大版本，无临时补丁。

2. **测试范围验证**  
   再次运行 `npm test -- --listTests`，与升级前对比。  
   若路径模式未变，文件应全量出现——这是最基础的“连续性”指标；但升级可能改变默认测试收集规则，因此需对照--listTests差异并核对原因。

3. **类型与静态检查**  
   运行项目自带的 TypeScript 编译与检查命令（如 `tsc` 或项目中定义的 ts-check/compile 命令）。仅 ESLint + TypeScript parser 不能完全等价地提供完整的编译器类型检查覆盖。
   Jest 30 配合 `@types/jest` 大版本更新后，若出现“类型不匹配”或“未定义属性”，通常源于旧版宽松推断残留。

4. **CI 入口回归测试**  
   执行原本用于 CI 的命令（如 GitHub Actions、GitLab CI 中的 `npm test`），确保：
   - 所有测试通过
   - 无新增超时或内存警告
   - 输出未因 matcher 变更而混入多余信息

> 🧪 小技巧：若怀疑某个断言行为变化，可临时加 `console.log(repoSpy.mock.calls)` 观察实际调用参数是否与预期一致——这是调试“隐性语义变化”最快手段。

---

## 六、给 AI 的“防错口诀”与项目适配建议

- **先改明确的机械项**：matcher 别名、CLI 参数拼写、版本字段。
- **再处理有证据的语义变化**：如类型报错、运行时未定义属性（debug 查看 mock 调用）。
- **保留业务断言的核心**：参数值、次数、顺序、预期失败场景——这些才是“需求”所在。
- **最小 diff 优先**：避免 AI 重写整个测试文件结构，尤其是嵌套 `describe/it` 块。

针对你的项目，适配建议如下：

| 项目特征         | 调整建议                                                                 |
|------------------|--------------------------------------------------------------------------|
| 使用 jsdom       | 确认 `jest-environment-jsdom` 兼容 Jest 30 + JSDOM 26（可能需额外升级）      |
| 多环境根目录     | 在 `package.json` 中显式指定 `testMatch` 或 `roots`，避免路径模式漂移        |
| 遗留 Node 14/16 | 同步升级至 Jest 30 官方支持的运行时；Jest 30 已移除对 Node 14/16/19/21 的兼容性保证                         |
| CI 脚本传参复杂   | 改用 `--testPathPatterns "path1" --testPathPatterns "path2"` 显式拼接         |

---

## 七、结语：升级是校验“测试质量”的最佳时机

从 29 到 30，Jest 没有颠覆性重构，却是一次极佳的“压力测试”——它迫使你审视：那些长期依赖旧别名、宽松类型推断或隐式枚举属性的测试，是否真的健壮？

让 AI 协助升级，不是为了偷懒，而是为了把人类的经验转化为结构化指令：**知道改什么、为什么改、不改什么**。当 CI 再次绿勾，而断言依旧精准捕捉业务边界时，你就完成了从“版本升级”到“质量升级”的跃迁。

## 事实来源

- [Official Jest30 upgrade guide](https://jestjs.io/docs/upgrading-to-jest30)
- [Jest29.7 CLI](https://jestjs.io/docs/29.7/cli) / [Jest30.0 CLI](https://jestjs.io/docs/30.0/cli)
- [NestJS migration PR #15268](https://github.com/nestjs/nest/pull/15268/files)
- [Pinned sample configuration](https://raw.githubusercontent.com/nestjs/nest/22e2b8cc4e832895d436a09da9d7407f30d42e92/sample/05-sql-typeorm/package.json)
- [ts-jest29.4.5 peer compatibility](https://raw.githubusercontent.com/kulshekhar/ts-jest/v29.4.5/package.json)
