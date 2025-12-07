# Cloudflare Pages 设置指南

本指南提供从零开始将 AI Coding Club 仓库接入 Cloudflare Pages 并实现自动部署的完整步骤。

## 前置条件

- Cloudflare 账户（免费版即可）
- 拥有 `IsaacZhaoo/aicodingclub` 仓库访问权限的 GitHub 账户
- 浏览器（Chrome、Firefox、Safari 或 Edge）

**预计耗时：** 约 10 分钟

## 操作步骤

### 第 1 步：打开 Cloudflare 控制台

1. 访问 https://dash.cloudflare.com/
2. 使用 Cloudflare 账户登录
   - 如果还没有账户，点击 **Sign up** 注册（免费）
3. 进入主控制台首页

### 第 2 步：进入 Pages 模块

1. 在左侧导航栏点击 **Pages**
2. 点击 **Create a project**
3. 选择 **Connect to Git**

### 第 3 步：授权 GitHub

1. 选择 **GitHub** 作为 Git 提供商
2. 点击 **Authorize GitHub**
3. 跳转至 GitHub OAuth 授权页面
4. 点击 **Authorize cloudflare**
5. 如提示请输入 GitHub 密码
6. 核对权限需求（Cloudflare 需要访问你的仓库）
   - **公开仓库**：默认授权
   - **私有仓库**：需要手动勾选 `IsaacZhaoo/aicodingclub`
7. 再次点击 **Authorize cloudflare**
8. 返回 Cloudflare Pages 页面

### 第 4 步：选择仓库

1. 搜索 **aicodingclub** 仓库
2. 选择 `IsaacZhaoo/aicodingclub`
3. 点击 **Connect**

### 第 5 步：配置构建参数

Cloudflare 将显示构建配置表单，请按下表填写：

| 字段 | 值 |
|------|----|
| **Project name** | `aicodingclub` |
| **Production branch** | `main` |
| **Build command** | `npm ci && npm run build && npx pagefind --site build` |
| **Build output directory** | `build` |
| **Root directory** | （留空） |

**重要提示：** 请复制上方构建命令的完整内容，不要做任何改动。

### 第 6 步：设置环境变量

1. 向下滚动到 **Advanced build settings**
2. 点击 **Environment variables**
3. 新增两个环境变量：

**变量 1：NODE_VERSION**
- 名称：`NODE_VERSION`
- 值：`20`
- 作用环境：`Production` 与 `Preview`

**变量 2：NPM_FLAGS**
- 名称：`NPM_FLAGS`
- 值：`--prefer-offline --no-audit`
- 作用环境：`Production` 与 `Preview`

**变量说明：**
- `NODE_VERSION=20`：保证使用 Node.js 20 LTS（项目要求）
- `NPM_FLAGS`：利用缓存并跳过 npm audit，加快构建速度

### 第 7 步：保存并触发部署

1. 点击 **Save and Deploy**
2. Cloudflare 立即触发首次构建
3. 页面将实时显示构建日志
4. 等待构建完成（通常 3-5 分钟）

**构建状态说明：**
- 🟦 **蓝色**：构建进行中
- 🟩 **绿色**：构建成功
- 🟥 **红色**：构建失败

### 第 8 步：获取预览地址

1. 构建成功后会看到提示：
   ```
   Your site is live at: https://aicodingclub-[随机哈希].pages.dev
   ```
2. **请保存该链接！** 它即是当前的预览 / 生产访问地址
3. 点击链接即可在新窗口打开站点

### 第 9 步：验证部署效果

访问预览地址并检查：

- [ ] 首页可正常打开，无报错
- [ ] 样式加载正常（页面不是仅有黑白文字）
- [ ] 图片资源显示正常
- [ ] 导航链接可点击并跳转
- [ ] 浏览器控制台（F12 > Console）无报错

## 后续行为说明

### 自动部署

每次向 `main` 分支 push：
1. GitHub 会向 Cloudflare 发送 webhook
2. Cloudflare 自动触发构建
3. 依次执行：`npm ci && npm run build && npx pagefind --site build`
4. 构建成功即自动上线，无需人工干预

### Pull Request 预览

每个 Pull Request 都会：
1. 自动构建并生成预览链接
2. Cloudflare 机器人在 PR 中留言，附带预览地址
3. 团队成员可直接访问该链接进行测试
4. 无需额外配置

### 手动重建

如需在无新提交的情况下重新构建：

1. 访问 https://dash.cloudflare.com
2. 点击 **Pages** → **aicodingclub**
3. 打开 **Deployments** 标签页
4. 找到需要重建的部署记录
5. 点击 **...** → **Retry build**

## 常见问题

### 授权失败：“Insufficient permissions”

**原因：** Cloudflare GitHub 应用尚未获得仓库访问权限

**解决方法：**
1. 打开 GitHub Settings → Developer settings → OAuth Apps
2. 找到 “Cloudflare Pages”
3. 点击进入并授予 `IsaacZhaoo/aicodingclub` 访问权限

或：
1. 进入仓库 Settings → Integrations & services
2. 检查是否已授权 Cloudflare

### 构建失败：“npm ci: Module not found”

**原因：** 依赖未正确安装

**解决方法：**
1. 确认 `package-lock.json` 已提交到仓库
2. Cloudflare 后台点击 **Retry build** 重试
3. 仍失败时，本地执行并重新提交：
   ```bash
   npm install
   git add package-lock.json
   git commit -m "Update package-lock.json"
   git push
   ```

### 构建失败：“pagefind: command not found”

**原因：** `pagefind` 未被添加到 `devDependencies`

**解决方法：**
```bash
npm install --save-dev pagefind
npm install
git add package-lock.json package.json
git commit -m "Add pagefind to devDependencies"
git push
```

### 预览链接显示 404

**原因：** 构建输出目录配置错误

**解决方法：**
1. 在 Cloudflare 中确认 **Build output directory** 为 `build`
2. 本地验证：
   ```bash
   npm run build
   ls build/index.html  # 若存在则表示构建成功
   ```

### 耗时多久？

- **初始配置：** 约 10 分钟
- **首次构建：** 3-5 分钟
- **之后每次构建：** 2-3 分钟
- **上线之后：** 每次 push 自动部署

## 下一步？

1. ✅ 仓库已与 Cloudflare Pages 连接
2. ✅ 构建流程配置完成
3. ⏳ 检查第 8 步获取的预览链接
4. 📝 将链接分享给团队（格式：`https://aicodingclub-[hash].pages.dev`）
5. 🔗 下一任务：绑定自定义域名 `aicoding.club`（参考 DOMAIN_SETUP.md）

## 进阶：命令行方式（可选）

如偏好 CLI，可使用 Wrangler：

```bash
# 安装 Wrangler
npm install --save-dev wrangler

# 登录 Cloudflare
npx wrangler login

# 部署到 Pages
npx wrangler pages deploy build
```

**但建议优先使用 GitHub 集成**，以便获得自动部署能力。

## 支持与文档

- **Cloudflare Pages 文档：** https://developers.cloudflare.com/pages/
- **Cloudflare GitHub 集成：** https://developers.cloudflare.com/pages/configuration/git-integration/
- **构建配置：** https://developers.cloudflare.com/pages/configuration/build-configuration/
- **故障排查：** https://developers.cloudflare.com/pages/troubleshooting/

## 总结

完成以上步骤后：
- ✅ GitHub 仓库已连接 Cloudflare Pages
- ✅ 构建命令：`npm ci && npm run build && npx pagefind --site build`
- ✅ 环境变量已设置（Node 20、npm flags）
- ✅ 首次部署成功
- ✅ 已获取预览地址
- ✅ 每次推送 `main` 分支都会自动部署

**至此，全部配置完成！** 今后只需提交代码即可自动上线。

---

**文档版本：** 1.0  
**最后更新：** 2025-10-25  
**仓库：** IsaacZhaoo/aicodingclub  
**部署平台：** Cloudflare Pages
