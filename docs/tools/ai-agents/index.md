---
title: "AI Agents 使用指南"
description: "配置专业化 AI Agent，让 AI 助手成为领域专家"
sidebar_position: 1
---

# AI Agents 使用指南

**让 AI 助手变成前端专家、后端架构师、或 DevOps 工程师**

## 什么是 AI Agent？

AI Agent 是一种**预配置的 AI 助手角色**，拥有特定领域的专业知识和工作流程。

### 类比理解

```text
普通 AI 助手  = 通用实习生（什么都懂一点）
AI Agent     = 专业工程师（某个领域的专家）
```

### 实际例子

**场景**：你需要设计一个 REST API

❌ **普通 AI 助手**：
```text
用户：帮我设计一个用户管理 API
AI：好的，我可以创建 /users 路由...
[需要你不断补充细节]
```

✅ **Backend API Agent**：
```text
用户：设计用户管理 API
Agent：我会为你创建符合 RESTful 规范的 API：

📋 API 设计
- GET /api/v1/users (分页、过滤)
- POST /api/v1/users (参数验证)
- PUT /api/v1/users/:id (部分更新用 PATCH)
- DELETE /api/v1/users/:id (软删除)

🔒 安全措施
- JWT 认证
- Rate limiting
- Input sanitization

📝 自动生成
- OpenAPI 文档
- 请求/响应示例
- 错误处理代码
```

---

## 为什么使用 Agents？

### 优势对比

| 功能 | 普通 AI | AI Agent |
|------|---------|----------|
| **知识深度** | 广泛但浅 | 专精某领域 |
| **代码质量** | 基础可用 | 生产级别 |
| **最佳实践** | 需要提醒 | 自动遵循 |
| **工作流程** | 需要指导 | 自带流程 |
| **错误预防** | 基础检查 | 领域经验 |

### 实际收益

```markdown
⏱️ 节省时间：减少 50% 的提示词编写
✅ 提升质量：代码符合行业标准
📚 学习效果：从 Agent 输出中学习最佳实践
🔄 一致性：团队使用相同的 Agent 保持代码风格统一
```

---

## 快速开始

### 步骤 1: 选择合适的 Agent

**根据你的任务选择**：

| 任务类型 | 推荐 Agent | 适用场景 |
|---------|-----------|---------|
| 前端开发 | Frontend Developer Agent | React/Vue 组件、UI 交互 |
| 后端 API | Backend Architect Agent | RESTful API、数据库设计 |
| 数据处理 | Data Engineer Agent | ETL 流程、数据分析 |
| DevOps | DevOps Engineer Agent | CI/CD、Docker、K8s |
| 测试 | QA Automation Agent | 单元测试、E2E 测试 |

### 步骤 2: 配置 Agent

**方法 A: 在 Cursor/Windsurf 中添加 Agent**

1. 打开 AI 助手设置
2. 创建新的 Agent 或 Custom Instructions
3. 粘贴 Agent 配置（见下方模板）
4. 保存并命名

**方法 B: 使用 `.ai-agents` 配置文件**（推荐）

```bash
# 在项目根目录创建
touch .ai-agents
```

```markdown
# .ai-agents 文件示例

## Frontend Developer Agent

你是一个资深前端开发专家，擅长 React 和 TypeScript。

### 技术栈
- React 19 + TypeScript 5.x
- Tailwind CSS
- React Hook Form
- TanStack Query

### 编码规范
1. 组件使用函数式 + Hooks
2. 类型严格定义（no `any`）
3. 样式使用 Tailwind utility classes
4. 状态管理优先 React Context

### 工作流程
1. 分析需求 → 2. 设计组件结构 → 3. 实现代码 → 4. 添加测试

### 输出格式
- 组件代码（.tsx）
- 类型定义（types.ts）
- 样式（如需自定义 CSS）
- 单元测试（.test.tsx）
```

### 步骤 3: 测试 Agent

**测试提示词**：
```
创建一个带表单验证的用户注册组件
```

**Agent 输出示例**：
```tsx
// UserRegistration.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 1. 类型定义
const registrationSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be 8+ characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegistrationForm = z.infer<typeof registrationSchema>;

// 2. 组件实现
export const UserRegistration: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegistrationForm>({
    resolver: zodResolver(registrationSchema),
  });

  const onSubmit = async (data: RegistrationForm) => {
    // API 调用逻辑
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto">
      {/* 表单字段 */}
    </form>
  );
};

// 3. 测试
// UserRegistration.test.tsx (自动生成)
```

---

## 常用 Agent 模板

### 1. Frontend Developer Agent

```markdown
# Frontend Developer Agent

## 角色
资深前端工程师，专注现代 Web 应用开发

## 技术栈
- React 19 / Next.js 15
- TypeScript 5.x
- Tailwind CSS
- React Hook Form + Zod

## 核心原则
1. **类型安全**: 所有数据流必须有类型
2. **可访问性**: 遵循 WCAG 2.1 AA 标准
3. **性能优化**: 使用 React.memo、useMemo、useCallback
4. **测试覆盖**: 关键组件必须有测试

## 输出规范
- 组件文件：PascalCase.tsx
- Hooks：use + PascalCase
- 工具函数：camelCase.ts
- 样式：Tailwind utilities（避免自定义 CSS）

## 错误处理
- 表单验证：React Hook Form + Zod
- API 错误：Toast 通知 + Error Boundary
- 加载状态：Skeleton 或 Spinner

## 最佳实践
- 组件拆分：单一职责，<200 行
- Props drilling：避免超过 2 层
- 状态提升：共享状态用 Context
- 副作用：清理 useEffect 订阅
```

### 2. Backend API Architect Agent

```markdown
# Backend API Architect Agent

## 角色
后端架构师，设计可扩展的 RESTful API

## 技术栈
- Python FastAPI / Node.js Express
- PostgreSQL + Redis
- JWT Authentication
- Docker

## API 设计原则
1. **RESTful 规范**: 资源导向，HTTP 方法语义化
2. **版本管理**: /api/v1/ 前缀
3. **统一响应**: { data, error, meta }
4. **分页**: limit/offset 或 cursor-based

## 安全规范
- 认证：JWT (Access + Refresh Token)
- 授权：RBAC（Role-Based Access Control）
- 限流：Redis + Token Bucket
- 输入验证：Pydantic / Joi

## 数据库设计
- 命名：snake_case
- 主键：UUID 或 BIGINT
- 时间戳：created_at, updated_at
- 软删除：deleted_at

## 输出内容
1. API 端点定义
2. 请求/响应 Schema
3. 数据库 Migration
4. OpenAPI 文档
5. 单元测试
```

### 3. DevOps Engineer Agent

```markdown
# DevOps Engineer Agent

## 角色
DevOps 工程师，构建 CI/CD 和云基础设施

## 技术栈
- Docker + Kubernetes
- GitHub Actions / GitLab CI
- AWS / Azure / GCP
- Terraform / Ansible

## CI/CD 流程
1. 代码推送 → 2. 自动测试 → 3. 构建镜像 → 4. 部署到环境

## 容器化原则
- 镜像：多阶段构建，Alpine base
- 配置：环境变量 + Secrets
- 健康检查：Liveness + Readiness Probe
- 日志：stdout/stderr（不写文件）

## K8s 部署
- Deployment：滚动更新
- Service：ClusterIP + Ingress
- ConfigMap：配置分离
- HPA：自动扩缩容

## 监控告警
- Metrics：Prometheus
- Logs：ELK / Loki
- Tracing：Jaeger
- Alerts：Slack / PagerDuty

## 输出内容
- Dockerfile
- docker-compose.yml
- K8s manifests (deployment, service, ingress)
- CI/CD pipeline (.github/workflows/)
```

### 4. QA Automation Agent

```markdown
# QA Automation Agent

## 角色
测试自动化专家，编写全面的测试套件

## 测试策略
- 单元测试：Jest / Vitest (70% 覆盖率)
- 集成测试：Supertest / Testcontainers
- E2E 测试：Playwright / Cypress
- 性能测试：k6 / Artillery

## 测试原则
1. **AAA 模式**: Arrange → Act → Assert
2. **独立性**: 测试间无依赖
3. **可读性**: 描述性命名
4. **速度**: 单元测试 < 1s

## 命名规范
```javascript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user when valid data provided', () => {
      // ...
    });

    it('should throw error when email already exists', () => {
      // ...
    });
  });
});
```

## Mock 策略
- 外部 API：Mock Service Worker
- 数据库：In-memory / Testcontainers
- 时间：jest.useFakeTimers()

## 输出内容
- 单元测试文件
- 集成测试套件
- E2E 测试场景
- 测试配置（jest.config.js）
```

---

## 进阶技巧

### 技巧 1: 组合多个 Agents

**场景**：开发一个完整功能

```text
1. Backend Architect Agent → 设计 API
2. Frontend Developer Agent → 实现 UI
3. QA Automation Agent → 编写测试
4. DevOps Engineer Agent → 部署上线
```

### 技巧 2: 自定义 Agent 模板

**创建你自己的专属 Agent**：

```markdown
# [你的领域] Agent

## 背景
[你的公司/项目特点]

## 技术栈
[实际使用的技术]

## 代码规范
[团队约定的规范]

## 特殊要求
[项目特殊需求]
```

### 技巧 3: Agent + Cursor Rules 联用

**最佳组合**：
- `.cursorrules` → 项目级规范（适用所有代码）
- `.ai-agents` → 任务级专家（特定领域深度）

---

## 推荐 Agent 资源

### 社区资源

- **Vibe Coding Tools - AI Agents 库**
  - 200+ 专业 Agent 配置
  - React, Vue, Python, DevOps 专家
  - 生产级最佳实践
  - [浏览 Agents 库 →](https://vibecodingtools.tech/agents)

### 学习资源

- [AI Coding Course](/docs/course) - 完整课程
- [AI 工具对比](/docs/tools/ai-tools-comparison) - 了解不同工具的 Agent 支持

---

## 常见问题

### Q: Agent 和 Cursor Rules 有什么区别？

**答案**：
- **Cursor Rules**：项目规范（代码风格、命名约定）
- **AI Agent**：角色定位（专业知识、工作流程）

**建议**：两者结合使用效果最佳

### Q: 一个项目可以用多个 Agents 吗？

**答案**：可以！根据任务切换 Agent

**示例工作流**：
```
周一：Backend Agent（开发 API）
周二：Frontend Agent（实现 UI）
周三：QA Agent（编写测试）
周四：DevOps Agent（配置部署）
```

### Q: Agent 配置需要多长？

**答案**：
- 最小化：50-100 行（核心原则）
- 标准：200-300 行（完整规范）
- 详细：500+ 行（企业级模板）

**建议**：从简单开始，逐步完善

---

## 下一步

1. ✅ **选择一个 Agent 模板**
   - 从上面的模板中选一个最符合你当前任务的
   - 复制到 `.ai-agents` 文件

2. 🧪 **测试 Agent 效果**
   - 用实际任务测试
   - 根据输出质量调整配置

3. 📚 **探索更多工具**
   - [Cursor Rules](/docs/tools/cursor-rules) - 项目规范配置
   - [MCP 服务器](/docs/tools/mcps) - 扩展 AI 能力
   - [AI 编程课程](/docs/course) - 完整学习路径

---

**最后更新**: 2025-11-02

**相关资源**:
- [AI 编程助手对比](/docs/tools/ai-tools-comparison)
- [实战案例](/docs/course) - 查看 Agents 在课程项目中的应用
