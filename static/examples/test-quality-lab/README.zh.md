# Test Quality Lab — 中文独立练习说明

本目录是“别只看全绿”教程的配套小练习。无需安装额外 npm 包：只需 Node.js 24+ 以及其内置的测试器即可运行与观察测试执行结果。

## 准备

在解压后进入`test-quality-lab`文件夹（该目录直接包含`age.mjs`），在此文件夹内打开终端以执行后续命令。

确认 Node 可用：
   ```bash
   node --version
   ```

## 结构概览

- `age.mjs`：被测函数，按规则判断用户是否已满 18 岁。
- `baseline-zh.test.mjs`：中文教程原始用例（17/19/30）。
- `baseline-en.test.mjs`：英文教程原始用例（10/19/25）。
- `boundary.test.mjs`：专门覆盖年龄边界的用例（17/18/19）。

三份`.test.mjs`测试文件调用 Node 内置的测试断言模块进行严格验证，被测逻辑集中在独立的`age.mjs`文件中。配套压缩包运行的是与教程正文相同的年龄示例，但无需额外依赖；`age.mjs`仅作为纯函数模块被调用，保持环境干净、可复现。
- 运行命令：`node --test --test-reporter=tap <test-file>`
- 多文件一次性运行：
  ```bash
  node --test --test-reporter=tap baseline-en.test.mjs baseline-zh.test.mjs boundary.test.mjs
  ```

## 正确状态（起点）

确认三组测试全通过后再进行修改：

```bash
node --test --test-reporter=tap baseline-en.test.mjs baseline-zh.test.mjs boundary.test.mjs
```

预期输出：共 9 个测试，全部通过。

## 实验一：引入一个“几乎正确”的实现错误

### 步骤 1：修改 `age.mjs`

用文本编辑器打开 `age.mjs`，将返回语句中的 `>=` 改为 `>`：

```javascript
// 原来
return user.age >= 18;
```

```javascript
// 改为
return user.age > 18;
```

保存文件。

### 步骤 2：重跑原始中文用例（旧用例）

```bash
node --test --test-reporter=tap baseline-zh.test.mjs
```

观察结果：3 个测试全部通过。  
结论：旧用例对“等于 18”这一边界没有覆盖，因此即使实现从 `>=` 变为 `>`，它们仍认为“没问题”。

### 步骤 3：重跑边界用例（关键对比）

```bash
node --test --test-reporter=tap boundary.test.mjs
```

观察结果：
- 2 个测试通过
- 1 个测试失败（`ERR_ASSERTION`），失败点：`age 18 returns true`
- 实际值 `false`，期望值 `true`

- **导入、语法或其他运行错误 ≠ 预期的断言失败。**  
  如果遇到 `ERR_ASSERTION` 之外的问题（例如未定义导入、SyntaxError、module not found 等），先解决这些基础错误，再观察边界用例是否抛出“期望的”断言失败。

结论：边界用例专门针对“刚好成年”的情况设计，能立刻发现“大于而非大于等于”的错误。

### 步骤 4：再跑英文原始用例（对照）

```bash
node --test --test-reporter=tap baseline-en.test.mjs
```

结果同样为 3 个测试通过。  
结论：同一类旧式用例对相似的边界错误同样“看不见”。

## 恢复正确实现

用编辑器把 `age.mjs` 改回：

```javascript
export function isUserOldEnough(user) {
  return user.age >= 18;
}
```

保存后，一次验证三组测试：

```bash
node --test --test-reporter=tap baseline-en.test.mjs baseline-zh.test.mjs boundary.test.mjs
```

预期结果：9 个测试全部通过。

## 学习要点（一句话版）

- 当你在项目中做小幅改动时，旧用例容易“假装没问题”，边界与针对性的用例才真正帮你发现行为是否仍然符合需求。
- 用 Node 自带测试器 + 严格断言即可，无需额外工具；重点是把测试的“范围”覆盖到你的关键边界上。

更多英文说明请参见 [README.md](./README.md)。
