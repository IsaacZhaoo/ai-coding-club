---
title: "如何验证 Coding Agent 生成的 Go 代码：测试、vet、fuzz 与 govulncheck"
description: "用可复现的 Go 工作流验证 Coding Agent 生成的代码，覆盖构建、测试、vet、fuzz、govulncheck 与人工审查。"
keywords:
  - 验证 Coding Agent 生成的 Go 代码
  - Go Coding Agent 验证
  - AI 生成 Go 代码
  - Go 工具链测试
  - govulncheck
  - Go fuzz 测试
sidebar_position: 9.5
tags: [tutorial, coding-assistant, agent-engineering, go, testing]
---

# 如何验证 Coding Agent 生成的 Go 代码：测试、vet、fuzz 与 govulncheck

前一篇 [AI Code Review 工作流](/zh/docs/tutorials/ai-code-review-workflow/) 回答了合并前应该建立哪些证据，这一篇把那套框架落到一个具体的 Go module：从应用契约出发，构建可执行的检查链，最后说清楚哪些判断工具链无法替你做。

<a href="/examples/go-agent-verification-lab.zip">下载经过验证的 `go-agent-verification-lab` 夹具</a>，也可以继续按本文步骤从零复现。

---

一份让人放心的 Go 补丁往往长这样：能编译，调用了正确的标准库函数，错误信息也用 `fmt.Errorf` 加了上下文。如果你只看完成总结或跑一次 `go build`，这份补丁似乎已经可以接受。但"可以编译"和"满足应用契约"是两件事，这正是本文要验证的。

为了让每一层工具链在受控条件下回答它能回答的窄问题，下面用一个合成模块 `go-agent-verification-lab` 把整个验证过程走一遍。模块不包含生产代码、真实用户数据或外部依赖，只有一个公开函数 `retrywindow.Parse`，契约是：

1. 去掉首尾空白；
2. 按 Go duration 语法解析；
3. 只接受闭区间 `[1s, 5m]`；
4. 非法语法或越界输入必须返回错误。

初始实现是为了教程验证过程而重建的刻意不完整状态，不是某个真实 Agent 输出的逐字记录。

---

## 前置条件

需要一台能运行 Go 的机器（Linux、macOS 或 WSL 均可），Go 版本与 `go.mod` 中声明的 `1.21` 相容。`govulncheck` 的最低 Go 版本要求可能高于 1.21，教程使用 `GOTOOLCHAIN=auto` 让工具链自行选择兼容版本，不需要手动升级本地安装。首次运行需要网络访问来下载未缓存的工具或工具链，并查询漏洞数据库。

---

## 创建项目

```bash
mkdir -p go-agent-verification-lab/retrywindow
cd go-agent-verification-lab
go mod init example.com/go-agent-verification-lab
go mod edit -go=1.21
```

项目结构：

```text
go-agent-verification-lab/
├── go.mod
└── retrywindow/
    ├── retry_window.go
    └── retry_window_test.go
```

`go.mod` 内容：

```go
module example.com/go-agent-verification-lab

go 1.21
```

---

## 放入初始实现

把以下内容写入 `retrywindow/retry_window.go`。这是为了复现验证过程而重建的刻意不完整实现：`Min` / `Max` 常量已经声明，但 `Parse` 既没有 trim 输入，也没有执行范围校验。

```go
package retrywindow

import (
	"fmt"
	"time"
)

const (
	Min = time.Second
	Max = 5 * time.Minute
)

// Parse converts an operator-provided retry window into a duration.
func Parse(input string) (time.Duration, error) {
	duration, err := time.ParseDuration(input)
	if err != nil {
		return 0, fmt.Errorf("parse retry window: %w", err)
	}

	return duration, nil
}
```

它可以编译，调用了 `time.ParseDuration`，错误也用 `%w` 包裹了语法错误。但契约的第一条（trim）和第三条（范围限制）都没有落实，而声明在代码里的 `Min`、`Max` 对任何调用路径都没有实际作用。

---

## Red 1：首尾空白

这个示例的应用契约要求容忍首尾空白。先写一个测试把这个预期行为钉住。

把以下内容写入 `retrywindow/retry_window_test.go`：

```go
package retrywindow

import (
	"testing"
	"time"
)

func TestParseAcceptsTrimmedDuration(t *testing.T) {
	duration, err := Parse(" 30s ")
	if err != nil {
		t.Fatalf("Parse() returned error: %v", err)
	}

	if duration != 30*time.Second {
		t.Fatalf("Parse() = %v, want %v", duration, 30*time.Second)
	}
}
```

运行：

```bash
go test -count=1 -run TestParseAcceptsTrimmedDuration ./retrywindow
```

输出的稳定部分：

```text
--- FAIL: TestParseAcceptsTrimmedDuration (0.00s)
    Parse() returned error: parse retry window: time: invalid duration " 30s "
FAIL
```

`time.ParseDuration` 不会自动去掉首尾空白，所以 `" 30s "` 被当成非法语法拒绝了。修复很小：在 import 里加入 `strings`，并将解析那行改为：

```go
duration, err := time.ParseDuration(strings.TrimSpace(input))
```

改好后重跑同一命令，输出变为 `PASS`。

---

## Red 2：应用范围

`[1s, 5m]` 不是 `time.ParseDuration` 的内建规则，而是这个应用层的契约。标准库乐于解析 `999ms` 或 `5m1s` 并返回一个合法的 `time.Duration`，但这两个值对运维场景而言都不应该被接受。在 `retry_window_test.go` 里追加：

```go
func TestParseEnforcesRetryWindowRange(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{name: "below minimum", input: "999ms"},
		{name: "above maximum", input: "5m1s"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if _, err := Parse(test.input); err == nil {
				t.Fatalf("Parse(%q) returned no error", test.input)
			}
		})
	}
}
```

运行：

```bash
go test -count=1 -run TestParseEnforcesRetryWindowRange ./retrywindow
```

输出的稳定部分：

```text
--- FAIL: TestParseEnforcesRetryWindowRange (0.00s)
    --- FAIL: TestParseEnforcesRetryWindowRange/below_minimum (0.00s)
        Parse("999ms") returned no error
    --- FAIL: TestParseEnforcesRetryWindowRange/above_maximum (0.00s)
        Parse("5m1s") returned no error
FAIL
```

`Parse` 正确地解析了这两个字符串，但直接返回了值，没有拒绝它们。最小修复是在成功解析后加入范围判断：

```go
if duration < Min || duration > Max {
	return 0, fmt.Errorf("retry window must be between %s and %s", Min, Max)
}
```

改好后重跑，变为 `PASS`。两次 red→green 都对应着契约里的一条具体规则，而不是重构或性能优化。这是测试作为应用文档的基本用法。

---

## 完整最终实现

把 `retrywindow/retry_window.go` 替换为以下内容：

```go
package retrywindow

import (
	"fmt"
	"strings"
	"time"
)

const (
	Min = time.Second
	Max = 5 * time.Minute
)

// Parse converts an operator-provided retry window into a duration.
func Parse(input string) (time.Duration, error) {
	duration, err := time.ParseDuration(strings.TrimSpace(input))
	if err != nil {
		return 0, fmt.Errorf("parse retry window: %w", err)
	}
	if duration < Min || duration > Max {
		return 0, fmt.Errorf("retry window must be between %s and %s", Min, Max)
	}

	return duration, nil
}
```

---

## 完整最终测试文件

把 `retrywindow/retry_window_test.go` 替换为以下完整内容，包含边界测试、非法语法测试和 fuzz target：

```go
package retrywindow

import (
	"testing"
	"time"
)

func TestParseAcceptsTrimmedDuration(t *testing.T) {
	duration, err := Parse(" 30s ")
	if err != nil {
		t.Fatalf("Parse() returned error: %v", err)
	}

	if duration != 30*time.Second {
		t.Fatalf("Parse() = %v, want %v", duration, 30*time.Second)
	}
}

func TestParseAcceptsInclusiveBounds(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  time.Duration
	}{
		{name: "minimum", input: "1s", want: time.Second},
		{name: "maximum", input: "5m", want: 5 * time.Minute},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			duration, err := Parse(test.input)
			if err != nil {
				t.Fatalf("Parse(%q) returned error: %v", test.input, err)
			}
			if duration != test.want {
				t.Fatalf("Parse(%q) = %v, want %v", test.input, duration, test.want)
			}
		})
	}
}

func TestParseEnforcesRetryWindowRange(t *testing.T) {
	tests := []struct {
		name  string
		input string
	}{
		{name: "below minimum", input: "999ms"},
		{name: "above maximum", input: "5m1s"},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if _, err := Parse(test.input); err == nil {
				t.Fatalf("Parse(%q) returned no error", test.input)
			}
		})
	}
}

func TestParseRejectsInvalidDuration(t *testing.T) {
	if _, err := Parse("not-a-duration"); err == nil {
		t.Fatal("Parse() returned no error for invalid duration syntax")
	}
}

func FuzzParseNeverAcceptsOutOfRangeDuration(f *testing.F) {
	for _, seed := range []string{"1s", "30s", "5m", "999ms", "5m1s", "", " 30s "} {
		f.Add(seed)
	}

	f.Fuzz(func(t *testing.T, input string) {
		duration, err := Parse(input)
		if err == nil && (duration < Min || duration > Max) {
			t.Fatalf("Parse(%q) accepted out-of-range duration %v", input, duration)
		}
	})
}
```

`FuzzParseNeverAcceptsOutOfRangeDuration` 验证的不变量是：只要 `Parse` 不返回错误，返回值就必须在 `[Min, Max]` 区间内。任何破坏这个断言的输入都会让 fuzz 引擎停下来并保存 corpus 条目。

---

## 最终命令链

需要生成一份不复用本地测试或 fuzz 缓存的独立证据记录时，可以先执行 `go clean -testcache -fuzzcache`。日常执行不需要把清理缓存当成固定仪式，除非你有明确的重现需求。

```bash
go clean -testcache -fuzzcache
gofmt -w retrywindow/retry_window.go retrywindow/retry_window_test.go
go build ./...
go test -count=1 ./...
go vet ./...
go test -count=1 -fuzz=FuzzParseNeverAcceptsOutOfRangeDuration -fuzztime=3s ./retrywindow
GOTOOLCHAIN=auto go run golang.org/x/vuln/cmd/govulncheck@latest -version
GOTOOLCHAIN=auto go run golang.org/x/vuln/cmd/govulncheck@latest -show verbose ./...
```

每层工具在回答一个比较窄的问题，绿灯的含义也只覆盖那个窄问题：

**`gofmt`** 统一源代码的展示格式，减少 diff 噪音。它不检查行为，格式正确的代码可以在逻辑上完全错误。

**`go build`** 证明所选 package 与依赖在当前环境下语法、类型和构建合法。构建通过不意味着运行时行为正确，也不运行任何测试。

**`go test`** 验证你写进测试的行为，以及这次运行的环境。它只能覆盖已有的测试 case；没有写进去的行为不会被发现。

**`go vet`** 用启发式规则扫描可疑结构，比如格式化字符串和参数不匹配，或锁值被错误地按值传递。它的干净结果不是正确性证明，只是一部分常见错误模式没有出现。

**fuzz** 从 seed corpus 生成大量输入并寻找新的覆盖路径，目标是找到破坏不变量的输入。三秒的 `fuzztime` 不是穷举；不变量本身也可能写错，fuzz 只验证你写进去的那个断言。成功的三秒运行会从 7 个 seed 开始，并以 `PASS` 结束，输出形如：

```text
fuzz: elapsed: 0s, gathering baseline coverage: 0/7 completed
fuzz: elapsed: 0s, gathering baseline coverage: 7/7 completed, now fuzzing with 8 workers
fuzz: elapsed: 3s, execs: ..., new interesting: ...
PASS
```

执行次数和新增 corpus 数量取决于机器和单次运行，不是稳定值。`PASS` 的准确含义是：在限定时间内，引擎没有找到破坏所写不变量的输入。

**`govulncheck`** 结合调用图，在执行时的漏洞数据库中检查已知的可达漏洞。运行 `-version` 是为了记录实际解析出的 scanner 版本和漏洞数据库更新时间，这两个值会随时间变化。`-show verbose` 增加进度信息和发现详情；需要完整调用栈时使用 `-show traces`。

`govulncheck` 的输出取决于你执行时的漏洞数据库状态和调用可达性。无发现只代表当次数据库状态和调用可达范围内没有已知可达漏洞，不代表永远没有。如果当前扫描报告漏洞，必须以当前结果为准，逐条确认是否可达，而不能期待教程总是出现同一个结论。需要可重复的 CI 时，可以把 `@latest` 改为明确版本，并按维护节奏更新。

---

## 证据契约表

| 验证层 | 回答的问题 | 记录字段 | 绿灯边界 |
|---|---|---|---|
| `gofmt` | 格式是否统一 | 格式化后的 diff | 只覆盖展示格式 |
| `go build` | 能否在当前环境构建 | Go 版本、OS | 不运行测试 |
| `go test` | 已写 case 是否通过 | 测试数量、覆盖 package | 未写 case 不在范围内 |
| `go vet` | 是否有常见可疑结构 | vet 通过 / 发现 | 启发式，非完备 |
| fuzz | 限定时间内是否找到不变量违例 | seed 数量、fuzz 时长、执行次数 | 不是穷举，不变量可能写错 |
| `govulncheck` | 已知可达漏洞（当次数据库） | 工具版本、数据库更新时间、扫描时间、module 范围、可达发现 | 不发现未知漏洞或设计缺陷 |
| 人工审查 | 应用契约、API 边界、架构、证据缺口 | 审查者、时间、判断结论 | 无法用工具替代 |

---

## 接受前检查清单

完成全链验证后，把以下条目过一遍再决定是否合并：

- [ ] 已运行 `gofmt`，并检查格式化后的 diff 只包含预期改动
- [ ] `go build ./...` 通过
- [ ] `go test -count=1 ./...` 全绿
- [ ] `go vet ./...` 无报告
- [ ] `go test -fuzz=... -fuzztime=3s` 以 `PASS` 结束
- [ ] `govulncheck` 已记录工具版本、数据库更新时间、扫描时间、module 范围和当次可达发现
- [ ] 如发现漏洞，已评估可达性并确认处置方案
- [ ] 已确认 `[1s, 5m]` 是正确的产品范围（工具链无法判断这一条）
- [ ] 已确认是否应该容忍首尾空白（业务决策，不是标准库规则）
- [ ] 已评估调用者是否需要自定义错误类型、本地化或兼容策略
- [ ] 已考虑 `Parse` 放入真实配置层后的集成风险
- [ ] 已判断现有 fuzz 时长是否足够，或是否需要更长时间或更多不变量

工具链告诉你补丁已经证明了什么；这份清单的最后几条提醒你还缺什么。哪些证据足够、哪些判断属于你的职责，是审查者自己的结论，不是工具链的输出。

---

## 参考资料

- [Go command](https://pkg.go.dev/cmd/go)
- [gofmt](https://go.dev/blog/gofmt)
- [go vet](https://pkg.go.dev/cmd/vet)
- [Go fuzzing tutorial](https://go.dev/doc/tutorial/fuzz)
- [Go vulnerability management](https://go.dev/doc/security/vuln/)
