---
title: "Integrate an AI-Generated OpenAPI TypeScript Client into Your Project"
sidebar_label: "OpenAPI Client Integration"
description: "Connect a generated OpenAPI TypeScript client to project authentication, timeouts, and error handling, then give an AI agent concrete acceptance checks."
keywords: ["OpenAPI", "TypeScript", "AI coding agent", "authentication", "timeout"]
sidebar_position: 47
tags: ["tutorial", "agent-engineering"]
---

# Integrate an AI-Generated OpenAPI TypeScript Client into Your Project

A generated OpenAPI TypeScript client handles HTTP mechanics gracefully: it runs `fetch` calls, inspects status codes, and returns JSON or text wrapped in a `Promise<any>`.

We’ll demonstrate how to add status-bearing errors and consistent response validation. You’ll see exactly how to ask an agent for these constraints and then verify whether the adjusted implementation respects them in practice.

## Generating the Starting Client

1. Go to [https://tools.aicoding.club/openapi-client/](https://tools.aicoding.club/openapi-client/).
2. Load the example OpenAPI 3.0.3 spec for a Task API (operationId: `listTasks`).
   - Server placeholder: `https://api.example.com`.
   - Endpoint: `GET /tasks`
3. Choose TypeScript and generate the client code or download the file.

### What the Generated Client Actually Provides

The tool gives you a basic wrapper around Fetch with these characteristics:

- **Constructor**: Takes one config object.
- **Internal behavior**:
  - Calls `fetch()` with the configured base URL and headers.
  - Checks `response.ok`.
  - Parses JSON only if the `Content-Type` is `application/json`; otherwise it returns the raw text.
- **Method signatures**:
  - Return type: `Promise<any>` (no typed schema).
  - No per-request token reading.
  - No built-in timeout.
  - No structured `HttpError` abstraction.

Because the generator does not know your project’s auth or validation rules, we must plug those in ourselves.

### Project Expectations for This Lesson

Your TypeScript application will expect:

- **Token resolution**: A synchronous function `getToken(): string | null` that returns the current Bearer token for each request.
  - The client should set the `Authorization` header to `Bearer <token>` if a token is present.
  - Stale `Authorization` headers must be removed when no token is available.
- **Timeout**: A configurable timeout (default: `5000ms`).
- **Observable errors**: Status codes and network/timeout failures should be surfaced consistently.
- **Response contract for `listTasks`**:
  - `204`: Implies an empty array in this application’s semantics.
  - `200`: Must contain valid JSON where every item has:
    - `id: number` (integer)
    - `title: string`

These field requirements are your application’s boundary contract, not automatic validation from the generator. Invalid JSON or invalid fields must cause a rejection.

## Adapting the Request Core (Single-Endpoint Focus)

For this lesson we keep the generated client and its `listTasks` method intact, but we replace the internal request core with a project-adapted implementation.

```ts
export interface Task {
  id: number;
  title: string;
}

export interface APIClientConfig {
  baseURL?: string;
  headers?: Record<string, string>;
  getToken: () => string | null;
  timeoutMs?: number;
}

export class HttpError extends Error {
  constructor(public readonly status: number) {
    super(`HTTP ${status}`);
    this.name = 'HttpError';
  }
}

// Replace the generated request core for this one-endpoint example;
// retain the class and public operation names.
export class TaskApiExampleClient {
  private readonly baseURL: string;

  constructor(private readonly config: APIClientConfig) {
    this.baseURL = config.baseURL ?? 'https://api.example.com';
  }

  private async request(method: string, path: string): Promise<unknown> {
    const headers = new Headers(this.config.headers);
    const token = this.config.getToken();
    if (token) headers.set('Authorization', `Bearer ${token}`);
    else headers.delete('Authorization');

    const response = await fetch(new URL(path, this.baseURL), {
      method,
      headers,
      signal: AbortSignal.timeout(this.config.timeoutMs ?? 5000),
    });

    if (!response.ok) throw new HttpError(response.status);
    // This lesson's list endpoint explicitly treats 204 as an empty list.
    if (response.status === 204) return [];
    if (!response.headers.get('content-type')?.includes('application/json')) {
      throw new Error('Expected a JSON response');
    }
    return await response.json();
  }

  async listTasks(): Promise<Task[]> {
    const data = await this.request('GET', '/tasks');
    if (!Array.isArray(data) || !data.every(item =>
      item !== null && typeof item === 'object'
      && typeof item.id === 'number' && Number.isInteger(item.id)
      && typeof item.title === 'string'
    )) {
      throw new Error('Expected an array of tasks with integer id and string title');
    }
    return data as Task[];
  }
}
```

### How This Core Serves Your Project

- **Headers**: Merges your project headers with dynamic auth headers.
- **Token Resolution**: Uses your existing `getToken()`; later token changes affect future requests only.
- **Timeout**: Implemented via `AbortSignal.timeout()`, observable through `DOMException`.
- **Error Handling**: Throws a custom `HttpError` for HTTP failures while preserving raw network/timeout errors.
- **Validation**: Ensures every returned task has the required `id` and `title` fields before exposing them.

This is your project-adapted version, not untouched tool output. The generated wrapper (`TaskApiExampleClient`) and method name (`listTasks`) remain unchanged.

### Initialization Example Using Project Modules

Initialize the client once and reuse it:

```ts
import { TaskApiExampleClient } from './taskApi';
import { getToken } from './auth';
import { config } from './config';

const taskApiClient = new TaskApiExampleClient({
  baseURL: config.apiBaseURL,
  getToken,
  headers: { Accept: 'application/json' }
});

// Later in your app:
const tasks = await taskApiClient.listTasks();
```

Because `getToken` is synchronous and called per-request, any token refresh updates subsequent calls automatically. The application reuses the same instance for all `listTasks` invocations.

## Observable Errors and Timeout Behavior

### HTTP Response Codes

- **401 (Unauthorized)**: Indicates missing or invalid authentication credentials; your sign-in policy should treat this as unauthenticated.
- **403 (Forbidden)**: Permission denial.
- **429 / 5xx (Rate Limit / Server Error)**: No automatic retry by default; implement an explicit backoff strategy if needed.

The existing `response.ok` check already filters out non-successful HTTP statuses. The adapted core turns those into structured `HttpError`s so your error-handling code can branch predictably.

### Timeout and Abort Signals

- **Timeout**: `AbortSignal.timeout(ms)` creates a signal that aborts after the given duration.
  - Passing this signal to `fetch()` affects both the request and body reading.
  - The budget uses **active time**, which pauses for suspended workers or bfcache, not strict wall-clock time.
- **Cancellation**: A user-triggered abort uses a normal controller; no special name is guaranteed across environments.

For robust checks (including in tests):

```ts
if (e instanceof DOMException && e.name === 'TimeoutError') {
  // handle timeout specifically
}
```

### Validation vs Casting

A TypeScript cast alone does not validate runtime data. Always:

- Check JSON validity (`try/catch` on parsing).
- Validate item fields against your application’s contract.
- Treat malformed `200` responses as errors.

### References

- Fetch API: [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch)
- AbortSignal.timeout(): [MDN](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static)
- HTTP 204 (No Content): [MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/204)

## Agent Task and Request-Level Acceptance Checks

Give your code-generation agent this short, reusable task description:

> “Adapt the generated TypeScript client for `GET /tasks` (OpenAPI 3.0.3, operationId: listTasks). Preserve the public method name `listTasks`; validate its result as `Promise<Task[]>`. Replace the internal request core with one that:
> - Uses project-provided `getToken(): string|null` for Bearer auth.
> - Applies a configurable timeout via `AbortSignal.timeout`.
> - Treats HTTP 204 as an empty array; validates `200` JSON items against `{ id: integer, title: string }`.
> - Throws `HttpError` for failed responses while preserving network/timeout errors.”

### Acceptance Checklist (per GET /tasks)

| Scenario                              | Expected Behavior                                                                                      |
|---------------------------------------|--------------------------------------------------------------------------------------------------------|
| `200` + valid JSON items              | Returns an array where every item has integer `id`, string `title`.                                   |
| Token change before next call         | New token is used; already-sent request is unaffected.                                                 |
| Absent token                         | No `Authorization` header sent; server responds with 401 if required.                                  |
| `401` / `403` / `5xx`                 | Thrown as `HttpError` with correct status; application can branch accordingly.                          |
| Slow response exceeding timeout       | Throws `DOMException` with name `TimeoutError`; requestCount stays at 1 in tests.                       |
| `204` (no content)                    | Returns empty array `[]` per project semantics.                                                        |
| Malformed JSON on `200` + `Content-Type: application/json`               | Caught during parsing; treated as an error (reject).                                                   |
| Valid JSON, wrong item fields         | The entire result is rejected if any item violates the `{id, title}` contract.                 |

### Mocking Strategy

- **Endpoint-level mocks**: Target the same URL (`GET /tasks`) with different handlers per scenario.
- **Preserve client behavior**: Mock the network response, not the `listTasks()` method itself. This validates your core adaptation, not a stubbed return value.
- **Timeout tests**:
  - Inject a short timeout (e.g., `1000ms`).
  - Use a mock handler that delays by slightly more than that (`1200ms`).
  - Assert that `DOMException` with name `TimeoutError` is thrown and only one request was sent.

> Note: A published example using Ky demonstrates this pattern:  
> https://github.com/sindresorhus/ky/blob/0d59458a0a58e1c3d7c6db0ab17ed5c7cd671e47/test/main.ts#L977  
> It delays a response 2000ms, sets a 1000ms timeout, and asserts `TimeoutError` with `requestCount === 1`. Use it as a reference for structure; your tutorial uses the native Fetch API.

## Next Steps

Now you have:

- A single-endpoint TypeScript client wired to your project’s auth (`getToken`).
- A predictable timeout that surfaces as observable errors.
- Clear validation rules that treat `204` and `200` responses consistently.

Recommended next actions:

1. Integrate the client into your app’s API layer using your existing config and auth exports.
2. Add test coverage for success, failure, timeout, and malformed responses.
3. When regenerating the client in the future, reapply these core adaptations to keep behavior stable.

For deeper guidance:

- AI-generated test review: [https://aicoding.club/docs/tutorials/ai-generated-test-review/](https://aicoding.club/docs/tutorials/ai-generated-test-review/)
- Prompt templates for code reviews: [https://aicoding.club/docs/tools/prompt-engineering/templates/code-review/](https://aicoding.club/docs/tools/prompt-engineering/templates/code-review/)
