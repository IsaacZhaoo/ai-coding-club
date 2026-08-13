# Go Agent Verification Lab

This anonymous synthetic fixture demonstrates a bounded verification loop for one Agent-style Go patch. It contains no production code, external service, credential, user data, or third-party runtime dependency.

The public function parses an operator-provided retry window. The contract is:

- trim surrounding whitespace;
- parse Go duration syntax;
- accept values from 1 second through 5 minutes, inclusive;
- reject invalid or out-of-range input.

Run the deterministic checks:

```bash
gofmt -w retrywindow/retry_window.go retrywindow/retry_window_test.go
go build ./...
go test ./...
go vet ./...
```

Run the bounded fuzz target:

```bash
go test -fuzz=FuzzParseNeverAcceptsOutOfRangeDuration -fuzztime=3s ./retrywindow
```

Run the official vulnerability checker with a current supported toolchain:

```bash
GOTOOLCHAIN=auto go run golang.org/x/vuln/cmd/govulncheck@latest -version
GOTOOLCHAIN=auto go run golang.org/x/vuln/cmd/govulncheck@latest -show verbose ./...
```

A green run is scoped evidence. It does not prove that the application range is the right policy, that the API belongs at this boundary, or that the surrounding system is correct or secure.
