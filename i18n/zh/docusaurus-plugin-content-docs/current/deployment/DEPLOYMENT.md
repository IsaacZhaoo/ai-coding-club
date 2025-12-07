# Cloudflare Pages 部署手册

本文档详细说明如何将 AI Coding Club 网站部署到 Cloudflare Pages，包括前置要求、配置步骤、验证流程以及常见问题排查。

## 目录

1. [概述](#概述)
2. [前置条件](#前置条件)
3. [初始接入流程](#初始接入流程)
4. [部署配置](#部署配置)
5. [构建流程](#构建流程)
6. [环境变量](#环境变量)
7. [部署验证](#部署验证)
8. [常见问题排查](#常见问题排查)
9. [构建性能](#构建性能)
10. [持续部署](#持续部署)

## 概述

项目部署在 **Cloudflare Pages**，这是一个 JAMstack 平台，具有以下特性：

- 只要向 `main` 分支执行 `git push` 即可自动部署
- 对每个 Pull Request 自动生成预览链接
- 依托 Cloudflare 全球 CDN，性能与安全性俱佳
- 免费版本提供每月 500 次构建

**当前状态：**
- 生产预览地址：`https://aicodingclub-xxx.pages.dev`（后续会绑定自定义域名）
- 构建耗时：约 3-5 分钟
- 部署频率：每次 push 到 `main`

## 前置条件

### 账户
- Cloudflare 账户（https://dash.cloudflare.com）
- 拥有 `IsaacZhaoo/aicodingclub` 仓库访问权限的 GitHub 账户

### 本地环境
- **Node.js**：20 LTS 及以上
- **npm**：9 及以上
- **Git**：用于版本控制

### 仓库要求
- 仓库为公开仓库；若为私有，需要在授权时勾选访问权限
- `main` 分支保持可正常构建
- `package-lock.json` 必须提交（确保可复现构建）

## 初始接入流程

### 步骤 1：授权 Cloudflare GitHub 应用
1. 登录 Cloudflare 控制台 → **Pages**
2. 点击 **Create a project** → **Connect to Git**
3. 选择 **GitHub**，点击 **Authorize GitHub**
4. 在 GitHub 授权页面授予 Cloudflare 访问仓库的权限

### 步骤 2：连接仓库
1. 在 Pages 中搜索 `aicodingclub`
2. 选择 `IsaacZhaoo/aicodingclub`
3. 点击 **Connect**

### 步骤 3：配置构建参数

| 配置项 | 值 | 说明 |
|--------|----|------|
| Project name | `aicodingclub` | 用于生成预览链接 |
| Production branch | `main` | 仅 `main` 触发生产部署 |
| Build command | `npm ci && npm run build && npx pagefind --site build` | 详见下方构建流程 |
| Build output directory | `build` | Docusaurus 默认输出目录 |
| Root directory | （留空） | 使用仓库根目录 |

### 步骤 4：新增环境变量

在 **Advanced → Environment variables** 中添加：

| 变量名 | 值 | 作用环境 |
|--------|----|----------|
| `NODE_VERSION` | `20` | Production & Preview |
| `NPM_FLAGS` | `--prefer-offline --no-audit` | Production & Preview |

> `NODE_VERSION` 保证使用 Node 20，`NPM_FLAGS` 可利用缓存并略过 npm audit，提升速度。

### 步骤 5：保存并部署

点击 **Save and Deploy**，Cloudflare 会立即触发第一次构建，约 3-5 分钟完成。预览地址格式为 `https://aicodingclub-[hash].pages.dev`。

## 部署配置

### 配置文件摘要

**wrangler.toml**
```toml
name = "aicodingclub"
[build]
command = "npm ci && npm run build && npx pagefind --site build"
output_dir = "build"
[env.production]
vars = { NODE_VERSION = "20", NPM_FLAGS = "--prefer-offline --no-audit" }
```

**package.json**
```json
{
  "scripts": {
    "build": "docusaurus build"
  },
  "engines": {
    "node": ">=20.0"
  }
}
```

> Cloudflare Pages 无需额外的 vercel.json / netlify.toml，只需在控制台配置即可。

## 构建流程

部署时执行的命令：

```bash
npm ci && npm run build && npx pagefind --site build
```

### 1. `npm ci`
- 根据 `package-lock.json` 精确安装依赖
- 比 `npm install` 更快且可重复
- 约耗时 1-2 分钟

### 2. `npm run build`
- 调用 Docusaurus 构建脚本
- 将 Markdown 转换为静态 HTML，并打包 CSS/JS
- 输出到 `build/` 目录
- 约耗时 1-2 分钟

### 3. `npx pagefind --site build`
- 生成静态搜索索引，存放在 `build/pagefind/`
- 约耗时 30 秒

**总耗时：** 首次约 3-5 分钟，后续因缓存命中通常 1-3 分钟。

## 环境变量

### 生产环境

| 变量 | 值 | 说明 |
|------|----|------|
| `NODE_VERSION` | `20` | 使用 Node 20 LTS |
| `NPM_FLAGS` | `--prefer-offline --no-audit` | 加快依赖安装 |

### 预览环境

- 继承生产环境的变量，可在 Cloudflare 中单独覆盖
- 若未来需要 Docusaurus 特定变量，可在此扩展

## 部署验证

### 1. 检查构建状态
1. 登录 Cloudflare → Pages → `aicodingclub`
2. 打开 **Deployments**
3. 查看最新构建状态：
   - ✅ Success：构建成功
   - 🔄 In Progress：正在构建
   - ❌ Failed：查看日志排查

### 2. 查看构建日志
- 确认 `npm ci` / `npm run build` / `pagefind` 均无报错

### 3. 测试预览 URL
- 打开 `https://aicodingclub-[hash].pages.dev`
- 检查：页面加载、样式、导航、图片、控制台报错

### 4. 浏览器控制台
- `F12` 打开开发者工具 → Console
- 关注红色错误信息

### 5. 功能回归
- 测试英文 / 中文版本切换
- 检查搜索（实现后）
- 检查响应式布局

## 常见问题排查

### 模块未找到（Module Not Found）
- 核心原因：依赖安装失败
- 处理：检查 `package-lock.json` 是否提交，重试或本地 `npm install` 后重新提交

### 构建超时（>10 分钟）
- 可能原因：依赖过大或网络慢
- 处理：
  1. 检查 Cloudflare 状态
  2. 本地执行 `npm ci` 评估耗时
  3. 必要时改用镜像源

### Pagefind 命令不存在
- 原因：未安装 `pagefind`
- 处理：
  ```bash
  npm install --save-dev pagefind
  npm install
  git add package-lock.json package.json
  git commit -m "Add pagefind to devDependencies"
  git push
  ```

### 预览地址 404
- 原因：输出目录配置错误
- 处理：确保 Cloudflare 设置为 `build`，本地 `npm run build` 后检查 `build/index.html`

### 样式丢失
- 检查 `docusaurus.config.ts` 的 `baseUrl`
- 确认 `build/assets/` 目录下存在 CSS/JS 文件

更多场景详见原文，对应章节提供命令示例与解决思路。

## 构建性能

- **平均构建时间**：3-4 分钟
- **首次构建**：4-5 分钟（首次安装依赖）
- **再次构建**：2-3 分钟（命中缓存）
- **目标 SLA**：小于 5 分钟

可在 Cloudflare → Pages → Analytics 中查看：
- 构建次数
- 平均构建时间
- 构建成功率
- 当月累计构建分钟数

## 持续部署

### 自动部署
1. push 到 `main`
2. GitHub 发送 webhook
3. Cloudflare 触发构建
4. 构建成功后立即上线

### Pull Request 预览
1. 每个 PR 自动生成独立预览 URL（如 `pr-123.aicodingclub-xxx.pages.dev`）
2. Cloudflare 机器人在 PR 评论中附上链接
3. PR 关闭后自动清理

### 手动触发
1. Cloudflare → Pages → `aicodingclub` → **Deployments**
2. 找到目标部署
3. 点击 **...** → **Retry build**

### 回滚
1. 在部署列表中挑选目标版本
2. 点击 **...** → **Rollback to this deployment**
3. 无需改动 Git 历史，CDN 立即生效

## 后续建议

1. 根据 [DOMAIN_SETUP.md](./DOMAIN_SETUP.md) 绑定 `aicoding.club`
2. 配置 HTTPS / HSTS / WWW 重定向（见 [SECURITY_CONFIG.md](./SECURITY_CONFIG.md)）
3. 使用 `/scripts` 中的验证脚本进行巡检
4. 将预览 URL 写入 README 或内网文档，便于团队使用

## 参考资料

- [Cloudflare Pages 官方文档](https://developers.cloudflare.com/pages/)
- [Docusaurus 部署指南](https://docusaurus.io/docs/deployment)
- [Cloudflare Pages 构建配置](https://developers.cloudflare.com/pages/configuration/build-configuration/)
- [故障排查指南](https://developers.cloudflare.com/pages/troubleshooting/)

---

**撰写/更新日期：** 2025-10-25  
**维护者：** AI Coding Club 团队  
**适用环境：** Cloudflare Pages + Docusaurus 3.x
