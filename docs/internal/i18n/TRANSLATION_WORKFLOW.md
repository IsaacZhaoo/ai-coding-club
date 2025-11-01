# 🌐 翻译工作流 - 简化版

> 本地开发，使用Claude Code手动翻译，构建时自动检查

## 工作流程

### 1. 写文章
```bash
# 在blog/目录创建新文章
code blog/2025-10-30-my-new-post.md
```

### 2. 构建检查
```bash
npm run build
```

**自动检查结果**：
```
🌐 Checking blog post translations...

❌ Missing ZH translations (1 files):

   📄 2025-10-30-my-new-post.md
      → Should be at: i18n/zh/docusaurus-plugin-content-blog/2025-10-30-my-new-post.md

💡 How to translate:
   1. Open the original file in blog/
   2. Ask Claude Code (or your AI assistant) to translate it
   3. Save the translation to the path shown above
```

### 3. 使用Claude Code翻译

**示例提示词**：
```
请将 blog/2025-10-30-my-new-post.md 翻译成中文，并保存到
i18n/zh/docusaurus-plugin-content-blog/2025-10-30-my-new-post.md

翻译要求：
- 保持所有Markdown格式不变
- 代码块不要翻译
- 使用标准技术术语
- 内部链接自动加上 /zh/ 前缀（例如 /docs/intro → /zh/docs/intro）
- 保持友好的教育性语气
```

### 4. 验证翻译
```bash
# 再次检查
npm run check:translations

# 应该看到：
✅ All blog posts have ZH translations

📊 Translation Coverage:
   ZH: ████████████████████ 100% (2/2)
```

### 5. 构建和预览
```bash
# 构建（现在不会有警告）
npm run build

# 预览中文版
npm run serve -- --locale zh
```

## 可用命令

```bash
# 构建前检查翻译（自动运行）
npm run build

# 只检查翻译，不构建
npm run check:translations

# 跳过翻译检查直接构建（不推荐）
npm run build:skip-check
```

## 翻译指南

### 文件位置

| 原文 | 翻译 |
|------|------|
| `blog/2025-10-30-post.md` | `i18n/zh/docusaurus-plugin-content-blog/2025-10-30-post.md` |
| `blog/authors.yml` | `i18n/zh/docusaurus-plugin-content-blog/authors.yml` |

### 翻译原则

✅ **翻译**：
- 标题和描述
- 正文内容
- 链接文本
- 图片alt文本
- frontmatter中的 title, description, tags

❌ **不翻译**：
- 代码块
- 命令行
- 变量名
- URL路径
- 作者名（通常）

### 内部链接处理

**原文**：
```markdown
查看[入门指南](/docs/intro)了解更多
```

**翻译**：
```markdown
查看[入门指南](/zh/docs/intro)了解更多
```

**规则**：内部链接加上 `/zh/` 前缀

## 添加更多语言

编辑 `scripts/check-translations.js`:

```javascript
const CONFIG = {
  locales: ['zh', 'es', 'fr'], // 添加西班牙语和法语
};
```

同时更新 `docusaurus.config.ts` 的 i18n 配置。

## 示例：完整翻译流程

```bash
# 1. 写新文章
code blog/2025-10-30-getting-started.md

# 2. 尝试构建
npm run build
# 输出：❌ Missing ZH translations...

# 3. 在Claude Code中执行
# "请翻译 blog/2025-10-30-getting-started.md 到中文..."

# 4. 验证
npm run check:translations
# 输出：✅ All blog posts have ZH translations

# 5. 构建成功
npm run build

# 6. 预览两种语言
npm run serve
# 英文：http://localhost:3000/
# 中文：http://localhost:3000/zh/
```

## 常见问题

### Q: 我必须翻译吗？
A: 不必须。构建时只会提示，不会失败。但为了更好的覆盖率，建议翻译。

### Q: 如何跳过翻译检查？
A: 使用 `npm run build:skip-check`

### Q: 翻译文件在哪？
A: `i18n/zh/docusaurus-plugin-content-blog/` 目录

### Q: 链接怎么处理？
A: 内部链接加 `/zh/` 前缀，外部链接保持不变

### Q: 代码块要翻译吗？
A: 不要！保持代码块原样

## 优势

✅ **简单** - 不需要API密钥和复杂配置
✅ **灵活** - 你控制翻译质量和风格
✅ **本地** - 所有操作在本地完成
✅ **提醒** - 构建时自动检查提醒
✅ **免费** - 使用你现有的AI助手

---

就是这么简单！写完文章 → 构建提醒 → 用Claude Code翻译 → 完成！
