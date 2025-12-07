# 安全配置指南：HTTPS、HSTS 与安全头

本文档介绍如何为 `aicoding.club` 启用 HTTPS、配置 HSTS、设置 WWW 重定向以及添加常用安全响应头。

## 目录

1. [前置条件](#前置条件)
2. [第 1 步：启用 HTTPS](#第-1-步启用-https)
3. [第 2 步：配置 HSTS](#第-2-步配置-hstshttp-strict-transport-security)
4. [第 3 步：设置 WWW 重定向](#第-3-步设置-www-重定向)
5. [第 4 步：配置安全响应头](#第-4-步配置安全响应头)
6. [第 5 步：验证安全配置](#第-5-步验证安全配置)
7. [测试与验证工具](#测试与验证工具)
8. [常见问题排查](#常见问题排查)

## 前置条件

- [ ] 自定义域名已绑定（参见 DOMAIN_SETUP.md）
- [ ] DNS 生效且浏览器可正常访问
- [ ] 拥有 Cloudflare 控制台访问权限
- [ ] 建议安装 `curl`、`openssl` 等验证工具

## 第 1 步：启用 HTTPS

1. 登录 Cloudflare → 选择 `aicoding.club`
2. 在左侧菜单点击 **SSL/TLS** → **Edge Certificates**
3. 设置：
   - **SSL/TLS Mode**：`Full (strict)`（如后端为纯静态可使用 Full）
   - **Always Use HTTPS**：开启（强制 HTTP 跳转 HTTPS）
   - **Automatic HTTPS Rewrites**：开启（自动修复混合内容）
   - **Minimum TLS Version**：`TLS 1.2`
   - **Opportunistic Encryption**：开启
4. 点击保存，配置立即生效

**验证：**

```bash
curl -I http://aicoding.club

# 预期返回 301/302，Location 指向 https://aicoding.club/
```

## 第 2 步：配置 HSTS（HTTP Strict Transport Security）

1. Cloudflare 控制台 → **SSL/TLS** → **Edge Certificates**
2. 找到 **HTTP Strict Transport Security (HSTS)** 区域，点击启用
3. 推荐参数：
   - `Max Age`：`15768000`（6 个月）
   - `Include subdomains`：勾选
   - `Preload`：暂不启用（待稳定运行 3 个月后再考虑）
   - `No-Sniff Header`：开启
4. 保存配置

**启用后的响应头示例：**

```
Strict-Transport-Security: max-age=15768000; includeSubDomains
```

> 初期若需谨慎，可先设较短的 max-age（如 1 小时 → 1 周 → 6 个月），确认无问题后再延长。

## 第 3 步：设置 WWW 重定向

### 1. 添加 `www` 自定义域名（可选）
1. Cloudflare Pages → `aicodingclub` → **Custom domains**
2. 添加 `www.aicoding.club`
3. 在 DNS 中新增 CNAME：`www` → `aicodingclub.pages.dev`

### 2. 创建重定向规则
1. Cloudflare 控制台 → **Rules** → **Redirect Rules**（或旧版 **Page Rules**）
2. 新建规则：
   - 名称：`Redirect WWW to Root`
   - 表达式：`(http.host eq "www.aicoding.club")`
   - 目标：`https://aicoding.club${http.request.uri}`
   - 状态码：`301`（永久重定向）
3. 保存并启用

**验证：**

```bash
curl -I https://www.aicoding.club

# 预期：HTTP/2 301，Location → https://aicoding.club/
```

## 第 4 步：配置安全响应头

### Cloudflare 自带设置
- 上一步 HSTS 已启用 `No-Sniff Header`
- 若需更多自定义，可使用 Response Header 规则

### 自定义响应头（Transform Rules）
1. Cloudflare → **Rules** → **Transform Rules**
2. 创建 `Modify Response Header` 规则：
   - 条件：`(http.host eq "aicoding.club")`
   - Header：`X-Content-Type-Options` → `nosniff`
3. 如需其他安全头，可额外添加：

| Header | Value | 用途 |
|--------|-------|------|
| `X-Frame-Options` | `DENY` | 防止 iframe 嵌套攻击 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | 控制引用者信息 |

### 在 Docusaurus 中配置（可选）

```ts
// docusaurus.config.ts 示例
httpHeaders: {
  "X-Content-Type-Options": ["nosniff"],
  "X-Frame-Options": ["DENY"],
  "Referrer-Policy": ["strict-origin-when-cross-origin"],
}
```

## 第 5 步：验证安全配置

### HSTS / TLS / 安全头

```bash
# 检查 HSTS
curl -I https://aicoding.club | grep -i strict-transport

# 检查 TLS 版本
curl -v https://aicoding.club 2>&1 | grep TLSv

# 查看安全头
curl -I https://aicoding.club | grep -i "x-content-type\|x-frame\|referrer"

# 检查 HTTP 到 HTTPS 跳转
curl -I http://aicoding.club

# 检查 WWW 重定向
curl -I https://www.aicoding.club
```

### 证书详情

```bash
openssl s_client -connect aicoding.club:443 -showcerts

# 确认：颁发者、有效期、域名匹配、Verify return code: 0
```

## 测试与验证工具

1. **浏览器**：访问 https://aicoding.club，检查 Padlock、Console
2. **SSL Labs**：https://www.ssllabs.com/ssltest/ （目标等级 A 或 A+）
3. **Security Headers**：https://securityheaders.com/ （目标等级 A 或 A+）
4. **脚本验证**：运行项目脚本（例如 `./scripts/verify-security.sh`）

## 常见问题排查

### 未看到 HSTS 头
- 确认 HSTS 已启用并等待 5-10 分钟生效
- 清除本地缓存后重试

### WWW 不跳转
- 确认重定向规则已启用且匹配 `www.aicoding.club`
- 检查 `www` CNAME 是否解析到 `aicodingclub.pages.dev`

### 证书报错
- 证书签发需 5-10 分钟
- 在 Cloudflare Edge Certificates 页面重新签发
- 清空浏览器缓存后重试

### 混合内容警告
- 检查页面资源是否仍使用 HTTP 链接
- 确认 **Automatic HTTPS Rewrites** 已开启
- 在控制台找到具体资源并改用 HTTPS

### TLS 版本过低
- Cloudflare → SSL/TLS → Edge Certificates → Minimum TLS Version 设置为 `1.2`
- 等待 5-10 分钟后重新验证

## 安全检查清单

- [ ] HTTP 请求自动跳转到 HTTPS
- [ ] HSTS 响应头存在且参数正确
- [ ] TLS 版本为 1.2 或以上
- [ ] 证书有效且浏览器无警告
- [ ] `www` 到根域的 301 重定向生效
- [ ] `X-Content-Type-Options` 等安全头存在
- [ ] SSL Labs / Security Headers 等测试通过

## 后续事项

1. 按照 [DOMAIN_SETUP.md](./DOMAIN_SETUP.md) 检查域名状态
2. 运行 `./scripts` 目录中的验证脚本
3. 若站点稳定运行 3 个月以上，可考虑申请 HSTS Preload（https://hstspreload.org/）
4. 配置 sitemap 提交、Search Console 验证等 SEO 相关步骤

## 参考资料

- [Cloudflare SSL/TLS 文档](https://developers.cloudflare.com/ssl/)
- [HSTS 预加载名单](https://hstspreload.org/)
- [Security Headers 指南](https://securityheaders.com/)
- [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/)
- [SSL Labs 最佳实践](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
