---
title: "OpenAPI 客户端生成后：认证、超时与错误的适配接入"
sidebar_label: "OpenAPI 客户端接入"
description: "从 OpenAPI 工具生成 TypeScript 客户端，再让 AI 接入项目认证、超时和错误处理，用具体验收条件检查结果。"
keywords: ["OpenAPI", "TypeScript", "AI coding agent", "authentication", "timeout"]
sidebar_position: 47
tags: ["tutorial", "agent-engineering"]
---

# OpenAPI 客户端生成后：认证、超时与错误的适配接入

使用 OpenAPI 客户端生成工具能够迅速完成基础请求调用，把接口定义转化为可运行的代码。

这篇教程的目标很直接：把上述这些项目层面的约定——从每次请求如何安全地读取 token、到超时信号如何精准触发、再到错误如何带状态区分并校验响应字段——整理成编程 Agent 可读的指令集。

## 一、总体思路

本文档的任务目标很明确：

- **生成结果作为起点**：以本站生成的 TypeScript 客户端为基础，它拥有基础的 fetch 层与必要的返回格式，但尚未对接项目的身份认证和超时策略。
- **项目约定为准则**：明确 token 获取方式（同步返回 string|null）、超时控制（AbortSignal.timeout）、活跃时间要求、以及对本例 GET /tasks 的响应约定（204 表示空数组，200 必须为 JSON，每个元素包含 integer id 与 string title）。
- **修改生成请求核心**：将生成文件中的“通用请求”改造为项目所需的行为：注入 getToken 等配置、接入 AbortSignal 超时、统一 HttpError 状态处理、并依据项目约定对 Task 字段做严格判断（生成器本身不导出 Task 类型，也不做运行时校验）。
- **验收闭环**：提供覆盖成功、认证失败、5xx 错误、204 空响应、无效 JSON、字段错误、Token 轮换及请求计数等场景的 Mock 与测试思路，确保从请求层到业务层的完整性。

整体流程为：工具生成 → 接入项目配置（baseURL、getToken、headers） → 修改核心请求逻辑（超时、状态分类、字段约定） → 初始化真实客户端 → 在应用中复用并验证成功/失败场景。

## 二、用站内工具生成初始客户端

1. 打开 [OpenAPI Client Generator](https://tools.aicoding.club/openapi-client/)
2. 选择示例：  
   - Title: `Task API example`  
   - Operation: `GET /tasks`（operationId: `listTasks`）  
   - Server: `https://api.example.com`（占位）
3. 导出 TypeScript。

关键点：

- 已接受 `baseURL` 和 `headers`；
- 已用 `response.ok` 判断 HTTP 成功；
- 已有非 2xx 抛错的基础行为；
- 但缺：超时、request-level token、结构化错误类型、204 特判等。

接下来，在这之上做“项目适配”。

## 三、定义项目约定

为避免后续改造时出现“各自为政”的状态管理，本小节定义所有必须一致的项目行为：

- **Token 获取规则**：
  - getToken 为同步函数，返回 string|null。
  - 仅在 token 存在时向请求添加 `Authorization: Bearer <token>`；
- **超时控制**：
  - 使用 AbortSignal.timeout(ms)，确保目标浏览器环境支持该 API。
  - 若超时，统一抛出 TimeoutError（DOMException），拒绝理由明确为超时。
- **HTTP 状态分类**：
  - 非 2xx 状态码携带 status 属性，用于区分网络错误、认证失败与业务异常。
  - 网络/超时错误单独标记原因，便于上层统一处理（例如：HttpError instanceof + status 判断）。
- **本例响应约定**：
  - 204 No Content：客户端应返回空数组 []，不抛错。
  - 200 OK：必须为 JSON，且每个元素为对象，包含 integer id 与 string title。
  - 格式或字段错误（如不是 JSON、缺少字段、id 非整数等）均视为失败，由项目层拒绝该结果并记录原因。
- **生成器职责边界**：
  - 这些严格字段是“应用约定”，应由业务层保证；生成器不导出 Task 类型，也不在内部做运行时强校验（避免过度耦合）。

所有约定将在核心代码层被统一贯彻，确保后续改造的可维护性。

## 四、适配层实现（核心代码）

下面是在保留生成器 `TaskApiExampleClient` 与 `listTasks` 名称前提下的单接口适配实现。

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

## 五、接入项目现有流程

本小节演示如何将 TaskApiExampleClient 无缝接入项目已有的登录状态与配置体系。

- **保持单层实现**：TaskApiExampleClient 本身仍为单层设计，不引入额外的代理或封装层。
- **构造函数参数统一化**：只接收一个 config 对象，包含：
  - baseURL（来自项目配置）
  - getToken（同步获取 token 的函数）
  - headers（项目公共头，如 Accept、X-App-Key）
  - timeoutMs（可选，用于 AbortSignal.timeout）

示例接入方式：

```ts
// main.ts: auth/config are the project's existing modules.
import { TaskApiExampleClient, HttpError } from './taskApi';
import { getToken } from './auth';
import { config } from './config';

const client = new TaskApiExampleClient({
  baseURL: config.apiBaseURL,
  getToken,
  headers: { Accept: 'application/json' },
  timeoutMs: 5000,
});

export async function loadTasks() {
  try {
    return await client.listTasks();
  } catch (error) {
    if (error instanceof HttpError) {
      if (error.status === 401) {
        console.error('Sign-in required');
      } else if (error.status === 403) {
        console.error('Permission denied');
      } else {
        console.error('HTTP error:', error.status);
      }
    } else if (error instanceof DOMException && error.name === 'TimeoutError') {
      console.error('Request timed out');
    } else {
      console.error('Request or response failed:', error);
    }
    throw error;
  }
}
```

说明要点：

- **真实传入**：在初始化时，config.apiBaseURL、getToken、项目公共头与 timeoutMs 均按项目实际情况传入。
- **错误识别**：使用 HttpError instanceof + status 区分认证/业务异常；DOMException.name === 'TimeoutError' 专门处理超时；其他网络或格式错误则保留为不同原因。

至此，生成器输出、适配层改造与项目接入流程形成完整闭环。下一节将提供验收与 Mock 方案，确保从请求层到业务层的可测试性。

## 六、验收场景与检查清单

用这些场景验证你的实现是否达标：

### 1. 正常成功

- 请求：200 + JSON 数组 `[ { id: 1, title: "A" } ]`
- 预期：
  - token 被正确拼接到 `Authorization: Bearer xxx`；
  - 返回 `Task[]`，长度=1；
  - 没有沉默吞掉错误。

### 2. Token 动态变化

- 场景：调用前 token 存在 → 调用后 token 被清除/更新。
- 预期：
  - 每次请求都从 `getToken()` 重新读取；
  - 不会缓存“旧 token”到客户端内部；
  - 若中途丢失，下次请求自动不带头（或按项目策略处理）。

### 3. 无 Token

- 场景：`getToken()` 返回 `null`。
- 预期：
  - 不添加 `Authorization` 头；
  - 如果 API 设计为必须认证，则上游会收到 401（由业务处理）。

### 4. 401 可观测且不伪装成功

- 场景：API 返回 401 Unauthorized。
- 预期：
  - Promise reject，错误含 `status: 401`；
  - UI/逻辑能区分“HTTP 401”和“空任务列表”。

### 5. 403 / 5xx 保持 HTTP 错误

- 场景：权限不足或后端异常。
- 预期：
  - reject，status 为 403 或 5xx；
  - 不因误判变成空结果。

### 6. 超时触发

- 场景：网络延迟 > 5000ms（可用 MSW / mock server）。
- 预期：
  - Promise reject，错误标识为 `TimeoutError`；
  - 不会无限等待。

### 7. 204 No Content

- 场景：API 返回 `status: 204`。
- 预期：
  - 按约定返回 `[]`（或其他业务约定的空结果）；
  - 不抛 JSON parse 错误。

### 8. JSON 解析失败或形状不符

- 场景：200 OK + 非数组 JSON，或完全不可解析。
- 预期：
  - Promise reject；
  - 错误信息能区分“HTTP OK 但数据不对”。

### 9. 方法名稳定

- 外部调用始终为 `api.listTasks()`；
- 内部实现可重构，但不破坏此签名。

## 七、验收与 Mock

所有 Mock 场景都覆写同一个 GET /tasks 端点，超时延迟可配置，确保测试的便携性。

| 场景                       | 响应行为/条件                                         | 预期客户端行为                                  |
| -------------------------- | ---------------------------------------------------- | ---------------------------------------------- |
| 成功（200 JSON）           | 返回 JSON: `[{"id":1,"title":"A"},{"id":2,"title":"B"}]` | 返回 Task[]                |
| 认证失败（401）            | 返回 `{"error":"unauthorized"}`                         | HttpError(status=401)，记录认证错误         |
| 权限不足（403）            | 返回 `{"error":"forbidden"}`                            | HttpError(status=403)，拒绝并记录原因           |
| 服务器错误（500）          | 返回 `{"error":"internal server error"}`                | HttpError(status=500)，上层做告警或重试策略     |
| 204 No Content             | 空体，status=204                                     | 返回空数组 []                                  |
| 无效 JSON                  | Content-Type: application/json，返回 "not json"                                      | JSON 解析错误                 |
| 字段错误（非对象/非数组）  | 返回 [1, "text", null]                               | 字段校验错误 |
| Token 轮换后下一次调用     | 保持 200 JSON 正常响应                                | 验证 token 更新后请求仍成功                     |
| 超时（delay > timeoutMs）  | 实际响应可延迟 3000ms，而客户端配置 timeoutMs=1000ms | DOMException.name === 'TimeoutError'           |
| 请求计数验证               | 仅触发一次 GET /tasks                                | 确保无重复请求或竞态状态                       |

说明与参考：

- **超时测试**：可参照 Ky 公开测试中“将响应延迟 2000ms，配置 1000ms 超时，断言 TimeoutError 且请求数为 1"的思路：https://github.com/sindresorhus/ky/blob/0d59458a0a58e1c3d7c6db0ab17ed5c7cd671e47/test/main.ts#L977。在 Mock 环境中，只需控制 delay > timeoutMs，即可复现相同行为。
- **TimeoutError 来源**：MDN 文档中 AbortSignal.timeout 的规范实现，DOMException.name 为 'TimeoutError'：https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static 。
- **覆盖原则**：每个场景都复用同一个 GET /tasks 端点，避免引入额外 Mock 路由；超时延迟可统一用较短短的可配置预算（例如 300ms）来加速测试循环。

只要上述表格中的场景全部通过，即可认定生成器输出与适配层改造在请求层已达到项目验收标准。

## 八、小结

本文档完成的任务路径如下：

1. **工具生成**：用本站 TypeScript 客户端生成工具得到基础骨架（listTasks、fetch、`Promise<any>`）。
2. **接入改造**：
   - 引入项目认证入口（getToken → Bearer 头）
   - 定义响应与字段约定（204/200、Task 结构）
   - 设置超时（AbortSignal.timeout）与活跃时间预算
3. **核心修改**：将生成文件中的通用请求替换为项目所需的认证、超时与状态分类逻辑，同时保留类名与方法名以便复用。
4. **真实初始化**：在项目中以 config.apiBaseURL、auth.getToken、公共头及 timeoutMs 真实初始化 TaskApiExampleClient，并在应用层调用 listTasks。
5. **验收闭环**：通过成功/失败/超时/字段错误等场景的 Mock 测试，确保从请求层到业务层的可验证性。

推荐进一步阅读本站关于 AI 生成代码审查的流程：
- https://aicoding.club/zh/docs/tutorials/ai-generated-test-review/
- https://aicoding.club/zh/docs/tools/prompt-engineering/templates/code-review/
