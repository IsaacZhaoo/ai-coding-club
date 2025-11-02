---
title: "MCP 服务器指南"
description: "使用 Model Context Protocol 扩展 AI 助手能力"
sidebar_position: 1
---

# MCP 服务器指南

**给 AI 助手接入外部工具和数据源**

## 什么是 MCP？

**Model Context Protocol (MCP)** 是一个开放协议，让 AI 助手能够连接外部工具、数据库和 API。

### 用人话解释

```
AI 助手本身  = 一个聪明的大脑
MCP 服务器   = 给大脑接上眼睛、耳朵、手
```

### 没有 MCP vs 有了 MCP

❌ **没有 MCP**：
```
用户：帮我查看 GitHub 上的最新 Issues
AI：我无法直接访问 GitHub，请手动复制内容给我
```

✅ **有了 MCP（GitHub 服务器）**：
```
用户：帮我查看最新 Issues
AI：[自动连接 GitHub API]
     Issue #42: Bug in login form (2 hours ago)
     Issue #43: Feature request for dark mode (4 hours ago)
     [AI 可以直接分析并提供建议]
```

---

## MCP 能做什么？

### 核心能力

```markdown
📂 访问文件系统：读写本地文件
🗄️ 连接数据库：查询 PostgreSQL、MongoDB、Redis
🌐 调用 API：GitHub、GitLab、Jira、Slack
☁️ 云服务集成：AWS、Azure、Google Cloud
🔧 执行命令：运行测试、构建项目、部署代码
📊 数据分析：读取 CSV、处理 JSON、生成报告
```

### 实际应用场景

| 场景 | 需要的 MCP 服务器 | 效果 |
|------|-----------------|------|
| 代码审查 | GitHub MCP | AI 直接读取 PR，提供审查意见 |
| 数据库查询 | PostgreSQL MCP | AI 生成并执行 SQL，返回结果 |
| 日志分析 | Filesystem MCP | AI 读取日志文件，诊断问题 |
| 部署检查 | AWS MCP | AI 检查 EC2 状态，优化配置 |
| 任务管理 | Jira MCP | AI 创建 Issue，更新状态 |

---

## 快速开始

### 步骤 1: 了解你的 AI 工具是否支持 MCP

**支持 MCP 的工具**：
- ✅ Claude Code（Anthropic 官方）
- ✅ Cursor（v0.42+）
- ✅ Cline（VS Code 扩展）
- ✅ Continue（开源 AI 助手）

### 步骤 2: 安装 MCP 服务器

**方法 A: 使用官方 MCP 服务器（推荐）**

```bash
# 安装 MCP CLI
npm install -g @modelcontextprotocol/cli

# 安装 GitHub MCP 服务器
npx @modelcontextprotocol/create-server github

# 配置
npx mcp-server-github configure
```

**方法 B: 手动配置（以 Cursor 为例）**

1. 创建配置文件 `~/.cursor/mcp_servers.json`

```json
{
  "servers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/your/project"]
    }
  }
}
```

2. 重启 Cursor
3. 在 AI 聊天中输入：`@github` 或 `@filesystem`

### 步骤 3: 测试 MCP 连接

**测试提示词**：
```
@github 列出 my-repo 仓库的最新 5 个 Issues
```

**成功输出**：
```
已连接到 GitHub MCP 服务器
仓库：username/my-repo

最近的 Issues：
1. #42 - 登录表单 Bug [open] (2 小时前)
2. #43 - 深色模式功能请求 [open] (4 小时前)
3. #41 - 性能优化建议 [closed] (1 天前)
...
```

---

## 常用 MCP 服务器

### 1. GitHub MCP

**功能**：
- 查看 Issues、PRs、Commits
- 创建/更新 Issues
- 读取代码文件
- 查询 CI/CD 状态

**安装**：
```bash
npm install -g @modelcontextprotocol/server-github
```

**配置**：
```json
{
  "github": {
    "command": "mcp-server-github",
    "env": {
      "GITHUB_TOKEN": "ghp_your_token"
    }
  }
}
```

**使用示例**：
```
@github 分析最近 10 次 commit 的改动模式
@github 为 Issue #42 提供修复建议
@github 审查 PR #15 的代码变更
```

### 2. PostgreSQL MCP

**功能**：
- 执行 SQL 查询
- 分析数据库性能
- 生成查询优化建议
- 创建数据库 Schema

**安装**：
```bash
npm install -g @modelcontextprotocol/server-postgres
```

**配置**：
```json
{
  "postgres": {
    "command": "mcp-server-postgres",
    "env": {
      "DATABASE_URL": "postgresql://user:pass@localhost:5432/dbname"
    }
  }
}
```

**使用示例**：
```
@postgres 查询过去 7 天注册的用户数量
@postgres 分析 users 表的索引使用情况
@postgres 生成用户活跃度报告的 SQL
```

### 3. Filesystem MCP

**功能**：
- 读写本地文件
- 搜索文件内容
- 批量处理文件
- 分析项目结构

**配置**：
```json
{
  "filesystem": {
    "command": "mcp-server-filesystem",
    "args": ["/path/to/project"]
  }
}
```

**使用示例**：
```
@filesystem 分析 src/ 目录下所有 .ts 文件的代码复杂度
@filesystem 找出所有包含 TODO 注释的文件
@filesystem 统计项目的代码行数（按语言分类）
```

### 4. AWS MCP

**功能**：
- 查看 EC2 实例状态
- 管理 S3 存储桶
- 查询 CloudWatch 日志
- 检查 Lambda 函数

**配置**：
```json
{
  "aws": {
    "command": "mcp-server-aws",
    "env": {
      "AWS_ACCESS_KEY_ID": "your_key",
      "AWS_SECRET_ACCESS_KEY": "your_secret",
      "AWS_REGION": "us-east-1"
    }
  }
}
```

**使用示例**：
```
@aws 列出所有运行中的 EC2 实例
@aws 查看过去 1 小时的 Lambda 错误日志
@aws 分析 S3 存储成本优化建议
```

### 5. Jira MCP

**功能**：
- 创建/更新 Issues
- 查询 Sprint 进度
- 生成工时报告
- 分析团队效率

**配置**：
```json
{
  "jira": {
    "command": "mcp-server-jira",
    "env": {
      "JIRA_URL": "https://your-domain.atlassian.net",
      "JIRA_EMAIL": "your@email.com",
      "JIRA_TOKEN": "your_api_token"
    }
  }
}
```

**使用示例**：
```
@jira 创建一个 Bug：登录页面加载慢
@jira 查看当前 Sprint 的所有未完成任务
@jira 生成本周团队工时报告
```

---

## 高级用法

### 技巧 1: 组合多个 MCP 服务器

**场景**：完整的开发工作流

```
步骤 1: @jira 查看今天要完成的任务
步骤 2: @github 创建功能分支
步骤 3: @filesystem 分析需要修改的文件
步骤 4: [AI 生成代码]
步骤 5: @github 创建 Pull Request
步骤 6: @jira 更新任务状态为"代码审查中"
```

### 技巧 2: 创建自动化工作流

**示例：自动化代码审查流程**

```markdown
# 提示词模板

请执行完整的代码审查流程：

1. @github 获取 PR #[number] 的文件变更
2. @filesystem 读取相关文件的完整内容
3. 分析代码质量（性能、安全、最佳实践）
4. @github 在 PR 中添加审查评论
5. 生成审查摘要报告
```

### 技巧 3: 数据分析管道

**场景**：分析生产数据库性能

```
1. @postgres 查询慢查询日志（过去 24 小时）
2. 分析查询模式，找出性能瓶颈
3. 生成优化建议（索引、查询重写）
4. @filesystem 将报告保存到 reports/db-optimization.md
5. @jira 创建优化任务，附上报告链接
```

---

## 自定义 MCP 服务器

### 为什么要自定义？

**场景**：
- 公司内部 API（CRM、ERP 系统）
- 自建数据库或工具
- 特殊工作流程

### 创建简单的 MCP 服务器

**示例：内部 API MCP 服务器**

```typescript
// custom-api-server.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'custom-api-server',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
  },
});

// 定义工具：获取用户信息
server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'get_user') {
    const userId = request.params.arguments?.userId;
    // 调用你的内部 API
    const response = await fetch(`https://api.internal.com/users/${userId}`);
    const data = await response.json();

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(data, null, 2),
      }],
    };
  }
});

// 启动服务器
const transport = new StdioServerTransport();
await server.connect(transport);
```

**配置使用**：
```json
{
  "custom-api": {
    "command": "node",
    "args": ["custom-api-server.js"]
  }
}
```

---

## 安全最佳实践

### 1. API Token 管理

❌ **不安全**：
```json
{
  "github": {
    "env": {
      "GITHUB_TOKEN": "ghp_abc123def456"  // 硬编码
    }
  }
}
```

✅ **安全**：
```json
{
  "github": {
    "env": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"  // 环境变量
    }
  }
}
```

```bash
# .env 文件
GITHUB_TOKEN=ghp_your_token_here
```

### 2. 权限最小化

**只授予必要权限**：
- GitHub Token：只读权限（除非需要写入）
- 数据库：只读用户（分析场景）
- AWS：限制特定服务和操作

### 3. 审计日志

**记录 MCP 操作**：
```json
{
  "logging": {
    "level": "info",
    "file": "~/.mcp/logs/operations.log"
  }
}
```

---

## 推荐 MCP 资源

### 官方资源

- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP GitHub 仓库](https://github.com/modelcontextprotocol)
- [MCP 服务器示例](https://github.com/modelcontextprotocol/servers)

### 社区资源

- **Vibe Coding Tools - MCP 集合**
  - 100+ MCP 服务器配置
  - GitHub, GitLab, Jira 连接
  - AWS, Azure, GCP 集成
  - [浏览 MCP 库 →](https://vibecodingtools.tech/mcps)

### 学习资源

- [AI 编程助手对比](/docs/tools/ai-tools-comparison) - 了解 MCP 支持情况
- [实战项目](/docs/course) - MCP 在实际项目中的应用

---

## 常见问题

### Q: MCP 会影响 AI 响应速度吗？

**答案**：
- 轻微影响（通常 +0.5-2 秒）
- 取决于外部 API 响应速度
- 文件系统 MCP 几乎无影响

### Q: MCP 数据会被发送到 AI 服务器吗？

**答案**：
- MCP 先在本地执行
- 只有**结果**发送给 AI（不是原始凭证）
- 敏感数据可以在本地过滤

**示例流程**：
```
1. AI 请求：@github 获取 Issue
2. 本地 MCP 服务器：调用 GitHub API
3. 返回结果：Issue 数据（不包含 Token）
4. AI 分析：基于返回的数据生成建议
```

### Q: 一个 AI 助手可以用多少个 MCP 服务器？

**答案**：
- 技术上无限制
- 实践中：5-10 个最常用的
- 太多会增加配置复杂度

**建议**：
```
核心 MCP（必装）：
- Filesystem（本地文件）
- GitHub（代码仓库）

按需 MCP：
- PostgreSQL（如果用 SQL）
- AWS（如果用云服务）
- Jira（如果用任务管理）
```

---

## 下一步

1. ✅ **安装第一个 MCP 服务器**
   - 推荐从 Filesystem 或 GitHub 开始
   - 测试基本功能

2. 🔧 **配置常用工作流**
   - 整合多个 MCP 服务器
   - 创建自动化流程

3. 📚 **探索更多工具**
   - [Cursor Rules](/docs/tools/cursor-rules) - 项目规范
   - [AI Agents](/docs/tools/ai-agents) - 专业化助手
   - [AI 编程课程](/docs/course) - 完整学习路径

---

**最后更新**: 2025-11-02

**相关资源**:
- [AI 编程助手对比](/docs/tools/ai-tools-comparison)
- [实战案例](/docs/course) - MCP 在项目中的应用
- [MCP 官方文档](https://modelcontextprotocol.io)
