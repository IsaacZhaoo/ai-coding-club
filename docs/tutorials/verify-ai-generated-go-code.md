---
title: "How to Verify AI-Generated Go Code: Build, Test, Vet, Fuzz, and govulncheck"
description: "Verify AI-generated Go code with a reproducible Go workflow covering build, tests, vet, fuzzing, govulncheck, and human review."
keywords:
  - verify AI-generated Go code
  - Go Coding Agent verification
  - Agent-generated Go code
  - Go toolchain testing
  - govulncheck
  - Go fuzz testing
sidebar_position: 9.5
tags: [tutorial, coding-assistant, agent-engineering, go, testing]
---

# How to Verify AI-Generated Go Code: Build, Test, Vet, Fuzz, and govulncheck

The [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/) guide establishes what a pre-merge review must prove before an Agent-generated patch is accepted: that the change satisfies its application contract, that the evidence is executable rather than narrative, and that residual risk is named rather than assumed away. This tutorial applies that three-layer structure—contract, executable evidence, residual risk—to a Go module you can reproduce from scratch.

The fixture I built for this exercise is called `go-agent-verification-lab`. A Coding Agent can return a plausible Go patch: it compiles, it delegates duration parsing to the standard library, and it wraps malformed-input errors with context. A completion summary or a single successful build can make that patch look ready to accept. The controlled experiment here exposes what that first impression leaves unproven, and it builds a repeatable evidence chain that a human reviewer can actually read and sign.

<a href="/examples/go-agent-verification-lab.zip">Download the verified `go-agent-verification-lab` fixture</a>, or follow the steps below to reproduce it from scratch.

---

## Why compilation alone is not enough

The module under test exposes one exported function, `retrywindow.Parse`, which converts an operator-provided text value to a `time.Duration`. Its application contract has four clauses:

1. trim surrounding whitespace from the input;
2. parse Go duration syntax using `time.ParseDuration`;
3. accept only values in the inclusive range `[1s, 5m]`;
4. return an error for invalid syntax or out-of-range input, preserving parse-error context.

A patch that compiles can satisfy clause 2 and clause 4 (for syntax errors) while silently violating clauses 1 and 3. The incomplete starting implementation below does exactly that. Marking these omissions as bugs and tracing them to green tests is the point of the exercise—not to characterize any Agent's behavior in general.

---

## Prerequisites

You need a Linux, macOS, or WSL environment. The module uses Go 1.21 as its language version, but the current `govulncheck` tool may require a newer Go toolchain. Setting `GOTOOLCHAIN=auto` lets the Go toolchain management layer select a compatible version automatically when you invoke `govulncheck`. The first uncached run needs network access to download the scanner and its tool module and to query the vulnerability database.

---

## Setting up the module

Run these four commands from a directory where you want to create the project:

```bash
mkdir -p go-agent-verification-lab/retrywindow
cd go-agent-verification-lab
go mod init example.com/go-agent-verification-lab
go mod edit -go=1.21
```

After setup, the project tree is:

```text
go-agent-verification-lab/
├── go.mod
└── retrywindow/
    ├── retry_window.go
    └── retry_window_test.go
```

`go.mod` contains:

```go
module example.com/go-agent-verification-lab

go 1.21
```

---

## The reconstructed starting implementation

The file below is a deliberately incomplete tutorial reconstruction. It is not a verbatim output preserved from a named Agent or a production incident. Its purpose is to represent the class of patch that passes a build and partial review but has not been verified against the full application contract.

Create `retrywindow/retry_window.go`:

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

This implementation compiles cleanly. It uses `time.ParseDuration` and wraps syntax errors with `%w` so the original error remains accessible to callers using `errors.Is` or `errors.As`. The declared constants `Min` and `Max` signal the intended bounds. But the function neither trims whitespace nor checks whether the parsed duration falls within those bounds. The constants are currently decorative.

---

## Red 1 — surrounding whitespace

Create `retrywindow/retry_window_test.go` with this first slice. The file must include the package declaration and imports so you can copy and run it directly:

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

Run the focused test:

```bash
go test -count=1 -run TestParseAcceptsTrimmedDuration ./retrywindow
```

The stable portion of the failure output looks like this:

```text
--- FAIL: TestParseAcceptsTrimmedDuration (0.00s)
    Parse() returned error: parse retry window: time: invalid duration " 30s "
FAIL
```

The file and line reference in the actual output will reflect your local file path; the error message and test name are stable. `time.ParseDuration` does not strip surrounding whitespace. The patch delegates parsing to the standard library correctly, but it also inherits this edge-case behavior.

The minimal fix is to add `"strings"` to the imports and replace the parse call:

```go
duration, err := time.ParseDuration(strings.TrimSpace(input))
```

Rerun the test. It passes. The implementation now satisfies clause 1 of the application contract.

---

## Red 2 — application bounds

The next omission is conceptually different. `time.ParseDuration` has no notion of what a valid retry window is for your system. The range `[1s, 5m]` is an application policy decision, not a rule the standard library can enforce. The declared constants only communicate intent; they enforce nothing on their own.

Add the following test function to the test file after the first test:

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

Run the new test in isolation:

```bash
go test -count=1 -run TestParseEnforcesRetryWindowRange ./retrywindow
```

Expected failure:

```text
--- FAIL: TestParseEnforcesRetryWindowRange (0.00s)
    --- FAIL: TestParseEnforcesRetryWindowRange/below_minimum (0.00s)
        Parse("999ms") returned no error
    --- FAIL: TestParseEnforcesRetryWindowRange/above_maximum (0.00s)
        Parse("5m1s") returned no error
FAIL
```

Both sub-tests fail because `Parse` returns the parsed duration and a nil error for any syntactically valid Go duration string, regardless of where it falls relative to `Min` and `Max`. The minimal fix adds a bounds check after a successful parse:

```go
if duration < Min || duration > Max {
	return 0, fmt.Errorf("retry window must be between %s and %s", Min, Max)
}
```

After this addition, rerun the test. Both sub-tests pass. The implementation now satisfies clause 3.

The two red-to-green slices together show the pattern: write a test that encodes one clause of the application contract, watch it fail against the starting implementation, add the minimal code that makes it pass, then proceed to the next clause. This forces each requirement to be stated in a form the toolchain can evaluate.

---

## Complete final implementation

Replace the contents of `retrywindow/retry_window.go` with the complete version:

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

## Complete final test file

Replace the contents of `retrywindow/retry_window_test.go` with the full test file, including the inclusive-bounds test, the invalid-syntax test, and the fuzz target:

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

`TestParseAcceptsInclusiveBounds` verifies the exact boundary values `1s` and `5m` are accepted. `TestParseRejectsInvalidDuration` confirms the syntax error path. `FuzzParseNeverAcceptsOutOfRangeDuration` encodes the central safety invariant: if `Parse` returns no error, the duration must be within bounds. The fuzzer will try to disprove that invariant with generated inputs.

---

## The full evidence command chain

If you need an independent evidence record that does not reuse local test or fuzz caches—for example, when you are creating a verification artifact before a merge—start by clearing both caches:

```bash
go clean -testcache -fuzzcache
```

This is not a ritual required before every normal local run. It is appropriate when you want to show that the green result is from a fresh execution, not a cached one.

Then run each layer in sequence:

```bash
gofmt -w retrywindow/retry_window.go retrywindow/retry_window_test.go
go build ./...
go test -count=1 ./...
go vet ./...
go test -count=1 -fuzz=FuzzParseNeverAcceptsOutOfRangeDuration -fuzztime=3s ./retrywindow
GOTOOLCHAIN=auto go run golang.org/x/vuln/cmd/govulncheck@latest -version
GOTOOLCHAIN=auto go run golang.org/x/vuln/cmd/govulncheck@latest -show verbose ./...
```

### What each layer actually proves

**`gofmt`** rewrites source files to canonical Go formatting. It eliminates diff noise from style variation and produces a deterministic presentation. It performs no behavioral analysis.

**`go build ./...`** confirms that all packages in the module parse correctly, resolve imports, and satisfy the type system under your current environment and build constraints. It produces no test results.

**`go test -count=1 ./...`** runs every test function the test files declare. The `-count=1` flag bypasses the test result cache, so the output reflects a real execution. Evidence is limited to the behaviors encoded in the test suite in this run and this environment. Inputs not covered by any test case are not validated.

**`go vet ./...`** applies a collection of heuristic checks for suspicious constructs: mismatched format verbs and arguments, lock values copied by value, unreachable code, and similar issues. A clean vet result is not a correctness proof; it means none of those specific heuristic conditions were triggered.

**`go test -fuzz=... -fuzztime=3s`** starts from the seven seeds in `FuzzParseNeverAcceptsOutOfRangeDuration` and generates new inputs guided by coverage discovery. A successful three-second run ends with `PASS` and produces output like this:

```text
fuzz: elapsed: 0s, gathering baseline coverage: 0/7 completed
fuzz: elapsed: 0s, gathering baseline coverage: 7/7 completed, now fuzzing with 8 workers
fuzz: elapsed: 3s, execs: ..., new interesting: ...
PASS
```

Execution counts, rates, and new-corpus counts vary by machine and run; the public tutorial does not record concrete values. Three seconds is not exhaustive. The encoded invariant—"if `Parse` returns no error, the result must be in bounds"—may itself be incomplete. A longer fuzz run increases confidence without guaranteeing it, and the invariant itself is a human judgment about what matters.

**`govulncheck -version`** followed by **`govulncheck -show verbose ./...`** scans the module's call graph against the Go vulnerability database. The `-version` flag reports the actually resolved scanner version and the database's update timestamp. The verbose mode adds progress messages and more finding detail; use `-show traces` when you need full call stacks for findings.

The result of a vulnerability scan is valid only under the database state and call reachability at execution time. A clean result means no known reachable vulnerability was found at that moment. It does not mean no vulnerabilities exist; it means none that the database knows about were reachable from the call paths `govulncheck` could trace. If your scan reports a finding, that current result overrides any expectation set by earlier runs. For reproducible CI, pin an explicit scanner version—`golang.org/x/vuln/cmd/govulncheck@vX.Y.Z`—and update it on a maintenance schedule rather than always resolving `@latest`.

When you record vulnerability-check evidence, include the tool version (from `-version`), the database update time, the scan time, the module scope, and the actual findings. Do not record only "no vulnerabilities found" without the context that makes that statement meaningful.

---

## Evidence-contract table

| Layer | Narrow question answered | Known limitation |
|---|---|---|
| `gofmt` | Is source formatting canonical? | No behavioral analysis |
| `go build` | Does the module compile in this environment? | Runs no tests |
| `go test` | Do encoded test cases pass? | Unencoded inputs not validated |
| `go vet` | Do heuristic suspicious-construct checks pass? | Not a correctness proof |
| Fuzzing | Does a bounded generated run find an invariant violation? | Duration-limited; invariant may be incomplete |
| `govulncheck` | Are known reachable vulnerabilities absent from this database state? | Database- and reachability-scoped; does not cover unknown vulnerabilities or design flaws |
| Human review | Does the patch satisfy the full application contract, API shape, and integration context? | Cannot substitute for runtime evidence |

---

## Pre-acceptance checklist

Before accepting this or any equivalent patch:

- [ ] `gofmt` has run and the formatted diff contains only the intended changes
- [ ] `go build ./...` exits 0
- [ ] `go test -count=1 ./...` exits 0, all tests pass
- [ ] `go vet ./...` exits 0
- [ ] A timed fuzz run exits `PASS` with no invariant violation
- [ ] `govulncheck` evidence record contains tool version, database update time, scan time, module scope, and actual findings
- [ ] A human reviewer has confirmed the bounds, whitespace policy, and error shape against product requirements
- [ ] Residual risks are named (see below)

---

## What the toolchain cannot decide

Every layer above answers a narrow technical question. None of them can answer the following:

**Whether `[1s, 5m]` is the correct range.** The bounds come from a product decision, not from any property of Go durations. The toolchain enforces what the code declares; it cannot evaluate whether the declaration is right. If the real system needs a five-second minimum or a ten-minute maximum, the tests will pass and the code will be wrong.

**Whether to tolerate surrounding whitespace at all.** Trimming whitespace is a usability decision. A stricter API could reject `" 30s "` with an explicit error. The choice made here—tolerate it silently—may or may not match what the configuration layer upstream expects.

**Whether callers need custom error types, localization, telemetry, or compatibility guarantees.** `fmt.Errorf` with `%w` is appropriate for many situations. If callers need to pattern-match on specific error types, or if error messages must be stable across versions, a different error design is required.

**Whether this function belongs at this API boundary.** Parsing retry windows might belong in configuration loading, in a separate validator, or in the caller that owns the policy. Placing it in a `retrywindow` package is a structural decision the toolchain cannot evaluate.

**Whether integration with the real configuration layer remains correct.** The fixture has no external dependencies, real user data, or integration surface. All evidence above is unit-level. Integration behavior with the actual configuration source must be verified separately.

**Whether a longer fuzz run or a different invariant would find a problem.** A three-second fuzz budget is a starting point. Longer runs, continuous fuzzing infrastructure, or additional properties encoded as separate fuzz targets may surface issues the current setup does not find.

Naming these gaps is itself part of the evidence record. An acceptance decision that accounts for known residual risk is a better decision than one that ignores what the evidence does not cover.

---

## References

- [Go command documentation](https://pkg.go.dev/cmd/go)
- [gofmt](https://go.dev/blog/gofmt)
- [go vet](https://pkg.go.dev/cmd/vet)
- [Go fuzzing tutorial](https://go.dev/doc/tutorial/fuzz)
- [Go vulnerability management](https://go.dev/doc/security/vuln/)
