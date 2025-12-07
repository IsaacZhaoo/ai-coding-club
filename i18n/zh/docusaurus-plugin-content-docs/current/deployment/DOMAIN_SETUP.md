# 自定义域名绑定指南：aicoding.club

本文档指导如何将自定义域名 `aicoding.club` 绑定到 Cloudflare Pages，并完成 DNS、验证与排查工作。

## 目录

1. [前置条件](#前置条件)
2. [第 1 步：在 Cloudflare Pages 中添加域名](#第-1-步在-cloudflare-pages-中添加域名)
3. [第 2 步：配置 DNS 记录](#第-2-步配置-dns-记录)
4. [第 3 步：验证 DNS 解析](#第-3-步验证-dns-解析)
5. [第 4 步：测试访问](#第-4-步测试访问)
6. [故障排查](#故障排查)
7. [验证清单与下一步](#验证清单与下一步)

## 前置条件

- [ ] 已完成 Cloudflare Pages 部署，项目名为 `aicodingclub`
- [ ] 已注册并可管理域名 `aicoding.club`
- [ ] 拥有 Cloudflare 控制台或域名注册商的 DNS 管理权限
- [ ] 建议安装 DNS 诊断工具（`dig`、`nslookup`）及 `curl`

## 第 1 步：在 Cloudflare Pages 中添加域名

1. 登录 Cloudflare（https://dash.cloudflare.com/）
2. 选择账户 → 点击 **Pages** → 进入 `aicodingclub` 项目
3. 打开 **Custom domains** 标签页
4. 点击 **Add a domain** / **Set up a custom domain**
5. 输入 `aicoding.club`（不带 `www`）→ **Continue**
6. 确认提示信息：
   - 若域名托管在 Cloudflare，将自动生成 CNAME
   - 若域名在外部注册商，需要手动添加记录
7. 添加成功后，域名状态显示为 **Pending**，并开始申请 SSL 证书

## 第 2 步：配置 DNS 记录

### 情况一：域名托管在 Cloudflare

1. Cloudflare 控制台 → 选择 `aicoding.club` → 点击 **DNS**
2. 查找是否已有指向 `aicodingclub.pages.dev` 的 CNAME 记录
3. 如无则新增：
   - 类型：CNAME
   - 名称：`aicoding.club`（或留空/`@`）
   - 内容：`aicodingclub.pages.dev`
   - TTL：Auto 或 5 分钟
   - 代理：默认（橙色云朵）

### 情况二：域名托管在其他注册商

**方案 A：CNAME（推荐）**

1. 登录注册商的 DNS 管理页面
2. 新增记录：
   - 类型：CNAME
   - 名称：`aicoding.club` 或 `@`
   - 值：`aicodingclub.pages.dev`
   - TTL：300 秒
3. 保存后等待生效（通常 5-30 分钟）

**方案 B：A/AAAA 记录（仅在根域不支持 CNAME 时使用）**

1. 参考 Cloudflare 文档获取 Pages IP 段（使用前需再次确认）
2. 添加记录：
   - 类型：A
   - 名称：`aicoding.club` 或 `@`
   - 值：Cloudflare 提供的 IPv4 地址
   - TTL：300 秒
3. 再添加 AAAA 记录：
   - 类型：AAAA
   - 名称：`aicoding.club`
   - 值：Cloudflare 提供的 IPv6 地址

## 第 3 步：验证 DNS 解析

### 在线工具

1. 打开 https://www.whatsmydns.net/
2. 输入 `aicoding.club`
3. 选择记录类型（CNAME 或 A）
4. 检查全球节点是否解析到 `aicodingclub.pages.dev`

### 命令行（`dig`）

```bash
dig aicoding.club CNAME
dig aicoding.club
dig aicoding.club @8.8.8.8
```

### 命令行（`nslookup`）

```bash
nslookup aicoding.club
nslookup aicoding.club 8.8.8.8
```

**状态判断：**

| 时间 | 预期状态 |
|------|----------|
| 0-5 分钟 | 部分节点更新 |
| 5-15 分钟 | 大部分节点更新 |
| 15-60 分钟 | 全球完成传播 |
| ≤24 小时 | 少数极端情况 |

## 第 4 步：测试访问

### HTTPS 访问测试

```bash
curl -I https://aicoding.club

# 预期：HTTP/2 200，含 cf-cache-status、content-type 等头部
```

### 浏览器访问

1. 打开 `https://aicoding.club`
2. 检查：
   - [ ] 地址栏显示绿色锁标
   - [ ] 页面内容与样式加载正常
   - [ ] 无「Not Secure」或证书警告

### Curl 详细输出

```bash
curl -v https://aicoding.club

# 关注：
# * TLSv1.2 / TLSv1.3
# * certificate verify ok
# HTTP/2 200
```

### 常见异常

| 异常 | 处理建议 |
|------|----------|
| `curl: (6) Could not resolve host` | DNS 尚未生效，等待传播 |
| `curl: (35) ...certificate problem` | SSL 证书尚未签发，等待 5-10 分钟 |
| 浏览器显示 `ERR_CERT_COMMON_NAME_INVALID` | 清除缓存或等待证书更新 |

## 故障排查

### SERVFAIL / 无法解析
- 核实注册商处的 DNS 记录是否保存
- 检查是否录入了正确的目标值：`aicodingclub.pages.dev`
- 等待传播或联系注册商支持

### DNS 正常但 HTTPS 失败
- 证书未签发：等待 5-10 分钟
- Cloudflare Pages 中域名状态是否为 Active
- 使用 `curl -v` 查看证书详情，必要时在 Cloudflare 中重新签发

### 缓存的旧记录
- 清空本机 DNS 缓存：
  ```bash
  # Linux
  sudo systemctl restart systemd-resolved

  # macOS
  sudo dscacheutil -flushcache

  # Windows
  ipconfig /flushdns
  ```
- 指定公共 DNS 再次查询：`dig aicoding.club @8.8.8.8`

### 提示「Not Secure」
- 证书签发需要时间，10 分钟后再试
- 强制刷新浏览器缓存（Ctrl/Cmd + Shift + R）
- 确认 Cloudflare → SSL/TLS 中的 **Automatic HTTPS Rewrites** 已开启

### 根域可访问但 `www` 不可用
- 在 DNS 中新增：`www` → `aicodingclub.pages.dev` 的 CNAME
- 或使用 Cloudflare 重定向规则将 `www` 指向根域（参考 SECURITY_CONFIG.md）

## 验证清单与下一步

### 完成清单
- [ ] `dig aicoding.club` 返回 CNAME → `aicodingclub.pages.dev`
- [ ] `curl -I https://aicoding.club` 得到 200 响应
- [ ] 浏览器无证书/混合内容警告
- [ ] Cloudflare Pages 中域名状态为 **Active**
- [ ] 页面内容与资源加载正常

### 下一步
1. 配置 HTTPS / HSTS / WWW 重定向 → 参见 [SECURITY_CONFIG.md](./SECURITY_CONFIG.md)
2. 设置安全头与站点验证 → 继续阅读 SECURITY_CONFIG.md
3. 使用 `/scripts` 下的验证脚本定期巡检

## 参考资料

- [Cloudflare Pages Custom Domains](https://developers.cloudflare.com/pages/platform/custom-domains/)
- [WhatsMyDNS](https://www.whatsmydns.net/)
- [dig 命令文档](https://linux.die.net/man/1/dig)
- [CNAME 记录说明](https://www.cloudflare.com/learning/dns/dns-records/dns-cname-record/)
