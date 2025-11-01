# Security Configuration Guide: HTTPS, HSTS & Security Headers

This guide walks through enabling HTTPS, configuring HSTS (HTTP Strict Transport Security), setting up WWW redirects, and implementing security headers for the `aicoding.club` domain.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Enable HTTPS](#step-1-enable-https)
3. [Step 2: Configure HSTS](#step-2-configure-hsts-http-strict-transport-security)
4. [Step 3: Set Up WWW Redirect](#step-3-set-up-www-redirect)
5. [Step 4: Configure Security Headers](#step-4-configure-security-headers)
6. [Step 5: Verify Security Configuration](#step-5-verify-security-configuration)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before proceeding, ensure:

- [ ] Custom domain `aicoding.club` added to Cloudflare Pages (see DOMAIN_SETUP.md)
- [ ] DNS properly configured and resolving
- [ ] HTTPS working (green padlock in browser)
- [ ] Access to Cloudflare dashboard
- [ ] Verification tools installed (optional):
  - `curl` (for header inspection)
  - `openssl` (for certificate details)

## Step 1: Enable HTTPS

### Procedure

1. **Navigate to SSL/TLS Settings**:
   - Cloudflare Dashboard → Select domain `aicoding.club`
   - Click **SSL/TLS** in the left sidebar
   - Click **Edge Certificates** subsection

2. **Configure SSL/TLS Mode**:
   - Select SSL/TLS Mode: **Full (strict)** or **Full**
   - This ensures Cloudflare uses HTTPS to origin servers

3. **Enable Required Features**:

   a. **Always Use HTTPS** (Automatic HTTPS Rewrites):
      - Status: **ON** (redirect all HTTP to HTTPS)
      - This adds `https://` to requests when HTTPS is available

   b. **Automatic HTTPS Rewrites**:
      - Status: **ON** (fix mixed content)
      - Rewrites mixed content URLs automatically

   c. **Minimum TLS Version**:
      - Set to: **TLSv1.2** (or higher)
      - Prevents old/weak protocols
      - Note: TLS 1.3 not supported in all regions; 1.2 is safe minimum

   d. **Opportunistic Encryption**:
      - Status: **ON**
      - Automatically encrypts HTTP traffic when possible

4. **Save Settings**:
   - Changes apply immediately (no wait required)

### Verification

Test HTTPS enforcement:

```bash
# Test HTTP redirect to HTTPS
curl -I http://aicoding.club

# Expected: 301 Moved Permanently or 302 Found
# Location: https://aicoding.club/
```

## Step 2: Configure HSTS (HTTP Strict Transport Security)

HSTS prevents downgrade attacks by instructing browsers to always use HTTPS.

### Procedure

1. **Navigate to HSTS Settings**:
   - Cloudflare Dashboard → SSL/TLS → Edge Certificates
   - Scroll to **HTTP Strict Transport Security (HSTS)** section

2. **Enable HSTS**:
   - Click **"Enable HSTS"** button (if not already enabled)

3. **Configure HSTS Parameters**:

   - **Max-Age**: `15768000` (6 months in seconds)
     - Recommended for production: 6-12 months
     - Start with 6 months for stability testing
     - Can increase to 2 years after stable operation

   - **Include Subdomains**: **YES** (checkmark enabled)
     - Applies HSTS to all subdomains
     - Important for future API/admin subdomains
     - Ensures consistent security policy

   - **Preload**: **NO** (do NOT enable yet)
     - Do NOT enable HSTS preload during initial setup
     - HSTS preload is irreversible; wait 3+ months for stability
     - Can apply to HSTS preload list later when site is mature
     - See: https://hstspreload.org/

   - **No-Sniff Header**: **YES** (recommended)
     - Prevents MIME-sniffing attacks
     - Should be enabled

4. **Save Configuration**:
   - Click **Save** to apply HSTS settings
   - Changes take effect immediately

### HSTS Header Format

After enabling, Cloudflare adds this header to all responses:

```
Strict-Transport-Security: max-age=15768000; includeSubDomains
```

- `max-age=15768000`: 6 months in seconds (15,768,000 = 6 × 30.44 × 24 × 60 × 60)
- `includeSubDomains`: Applies to all subdomains
- `preload` NOT included (optional, not yet enabled)

### Timing Considerations

| Phase | Max-Age | includeSubDomains | Preload |
|-------|---------|-------------------|---------|
| **Initial (Week 1-2)** | 3600 (1 hour) | No | No |
| **Stable (Week 2-4)** | 604800 (1 week) | Yes | No |
| **Production (Month 1+)** | 15768000 (6 months) | Yes | No |
| **Mature (Month 3+)** | 31536000 (1 year) | Yes | Optional |

**Note**: We're starting directly at 6 months as recommended by security best practices.

## Step 3: Set Up WWW Redirect

Configure permanent (301) redirect from `www.aicoding.club` to `aicoding.club`.

### Part A: Add WWW Domain (Optional but Recommended)

This step ensures both domains are recognized by Cloudflare Pages.

1. **Navigate to Custom Domains**:
   - Cloudflare Pages → aicodingclub project
   - Click **Custom domains** tab

2. **Add WWW Domain**:
   - Click **"Add a domain"** or **"Set up a custom domain"**
   - Enter: `www.aicoding.club`
   - Click **Continue**

3. **Configure DNS for WWW**:
   - Add CNAME record in DNS settings:
     - Type: CNAME
     - Name: `www`
     - Value: `aicodingclub.pages.dev`
     - TTL: 300 seconds (optional, for testing)

4. **Verify WWW is Accessible**:
   ```bash
   curl -I https://www.aicoding.club
   # Should return 200 OK (before redirect is added)
   ```

### Part B: Create Redirect Rule

Create a permanent redirect from `www.aicoding.club` to `aicoding.club`.

1. **Navigate to Rules**:
   - Cloudflare Dashboard → Rules section (in left sidebar)
   - Click **Redirect Rules** (or **Page Rules** in older UI)

2. **Create New Redirect Rule**:
   - Click **"Create redirect rule"** or **"Create rule"**

3. **Configure Rule Details**:

   - **Rule Name**: `Redirect WWW to Root`
   - **Expression** (matching condition):
     ```
     (http.host eq "www.aicoding.club")
     ```
   - **Target URL**: `https://aicoding.club${http.request.uri}`
     - `${http.request.uri}` preserves the path and query string
     - Example: `https://www.aicoding.club/docs/guide?v=2` → `https://aicoding.club/docs/guide?v=2`

   - **Status Code**: `301` (Permanent Redirect)
     - HTTP 301: Permanent (browsers cache)
     - Preferred for canonical domain consolidation

   - **Priority**: Default (lowest priority)
   - **Preserve query string**: Included in target URL format

4. **Save Rule**:
   - Click **Save and Deploy** (or **Save** depending on UI)
   - Rule is active immediately

### Testing the Redirect

```bash
# Test WWW redirect (should show 301 status)
curl -I https://www.aicoding.club

# Expected output:
# HTTP/2 301
# location: https://aicoding.club/

# Follow redirect with curl
curl -L https://www.aicoding.club

# Should eventually show 200 OK from root domain
```

## Step 4: Configure Security Headers

Cloudflare can inject security headers to protect against common attacks.

### Option A: Using Cloudflare Security Settings (Recommended)

Cloudflare automatically adds some headers. Configure additional ones via Page Rules:

1. **Enable No-Sniff Header** (already done in HSTS section):
   - Cloudflare → SSL/TLS → No-Sniff Header: **ON**

2. **Configure Additional Headers via Rules** (if needed):
   - If Cloudflare doesn't auto-add headers, create custom rules

### Option B: Custom Headers via Transform Rules (Advanced)

If using Cloudflare's advanced rules:

1. **Navigate to Transform Rules**:
   - Cloudflare Dashboard → Rules → Transform Rules

2. **Create Modify Response Header Rule**:
   - **Rule Name**: `Add Security Headers`
   - **Condition**: `(http.host eq "aicoding.club")`
   - **Action**: Modify Response Header
   - **Header Name**: `X-Content-Type-Options`
   - **Value**: `nosniff`

3. **Add Additional Security Headers**:
   Create separate rules for:

   | Header | Value | Purpose |
   |--------|-------|---------|
   | `X-Frame-Options` | `DENY` | Prevent clickjacking |
   | `X-Content-Type-Options` | `nosniff` | Prevent MIME-sniffing |
   | `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer data |

### Security Headers Cloudflare Should Add

These headers should appear automatically from Cloudflare:

```
Strict-Transport-Security: max-age=15768000; includeSubDomains
X-Content-Type-Options: nosniff
```

### Optional Headers (Docusaurus-specific)

These can be added via `docusaurus.config.ts` if needed (for future enhancement):

```typescript
// In docusaurus.config.ts
httpHeaders: {
  "X-Content-Type-Options": ["nosniff"],
  "X-Frame-Options": ["DENY"],
  "Referrer-Policy": ["strict-origin-when-cross-origin"],
}
```

## Step 5: Verify Security Configuration

### Check HSTS Header

```bash
curl -I https://aicoding.club | grep -i "strict-transport"

# Expected output:
# strict-transport-security: max-age=15768000; includeSubDomains
```

### Check TLS Version

```bash
curl -v https://aicoding.club 2>&1 | grep "TLSv"

# Expected output:
# * TLSv1.3 or TLSv1.2 (or higher)
# NOT TLS 1.0 or 1.1
```

### Check Certificate

```bash
openssl s_client -connect aicoding.club:443 -showcerts

# Look for:
# - Issuer: Cloudflare (or DigiCert/other)
# - Subject: aicoding.club
# - Not Before/After: Valid dates
# - Verify return code: 0 (ok)
```

### Check Security Headers

```bash
curl -I https://aicoding.club | grep -i "x-content-type\|x-frame\|referrer"

# Expected headers:
# x-content-type-options: nosniff
# x-frame-options: DENY (or equivalent)
```

### Test HTTP to HTTPS Redirect

```bash
curl -I http://aicoding.club

# Expected: 301/302 with Location: https://aicoding.club
```

### Test WWW to Root Redirect

```bash
curl -I https://www.aicoding.club

# Expected: 301 with Location: https://aicoding.club/
```

## Testing & Validation

### Browser-Based Testing

1. **Visit domain in browser**:
   ```
   https://aicoding.club
   ```

2. **Check security indicators**:
   - [ ] Green padlock in address bar
   - [ ] No warnings or errors
   - [ ] Click lock icon → Certificate shows valid
   - [ ] CN/SAN includes `aicoding.club`

3. **Check console for errors**:
   - Open DevTools (F12)
   - Go to Console tab
   - No mixed content warnings
   - No certificate warnings

### Using Online Security Checkers

1. **SSL Labs**:
   - Go to: https://www.ssllabs.com/ssltest/
   - Enter: `aicoding.club`
   - Target: **A+** or **A** grade
   - Verify:
     - TLS 1.2+ support
     - Strong cipher suites
     - HSTS enabled
     - Certificate valid

2. **Security Headers**:
   - Go to: https://securityheaders.com/
   - Enter: `https://aicoding.club`
   - Target: **A+** or **A** grade
   - Verify:
     - HSTS present
     - X-Content-Type-Options present
     - No deprecated headers

### Automated Verification

Run the verification scripts:

```bash
# Check domain and DNS
./scripts/verify-domain.sh

# Check security headers and TLS
./scripts/verify-security.sh
```

See `/scripts` directory for details.

## Troubleshooting

### HSTS Not Appearing in Headers

**Symptom**: `curl -I https://aicoding.club` doesn't show HSTS header

**Causes**:
1. HSTS not yet enabled in Cloudflare
2. DNS not propagated
3. Browser caching old response

**Solutions**:
1. Verify HSTS is enabled:
   - Cloudflare → SSL/TLS → Check HSTS toggle is ON
2. Wait 5-10 minutes after enabling
3. Clear browser cache:
   - Chrome: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Shift+Delete
4. Test with fresh curl:
   ```bash
   curl -I --connect-to aicoding.club:443:aicoding.club https://aicoding.club
   ```

### WWW Redirect Not Working

**Symptom**: `curl -I https://www.aicoding.club` doesn't redirect

**Causes**:
1. Redirect rule not created
2. Redirect rule not enabled
3. www domain not added to Cloudflare Pages

**Solutions**:
1. Verify redirect rule exists and is enabled:
   - Dashboard → Rules → Redirect Rules
   - Check rule is "Active" (green toggle)
   - Check expression matches `www.aicoding.club`

2. Verify www domain is added:
   - Cloudflare Pages → Custom domains
   - Should list both `aicoding.club` and `www.aicoding.club`

3. Check DNS for www:
   ```bash
   dig www.aicoding.club CNAME
   # Should resolve to aicodingclub.pages.dev
   ```

### Certificate Shows "Invalid" or "Untrusted"

**Symptom**: Browser or curl shows certificate error

**Causes**:
1. Certificate not yet issued
2. Domain not properly configured
3. Cloudflare DNS issues

**Solutions**:
1. Wait 5-10 minutes for certificate issuance
2. Force certificate renewal:
   - Cloudflare → SSL/TLS → Edge Certificates
   - Find domain, click "Reissue"
3. Clear browser cache and try again
4. Verify domain is "Active" in Cloudflare Pages

### Mixed Content Warnings

**Symptom**: Browser shows "Mixed Content" or insecure warning

**Causes**:
1. Assets loaded via HTTP instead of HTTPS
2. External resources not HTTPS
3. Auto-rewrite not enabled

**Solutions**:
1. Verify "Automatic HTTPS Rewrites" is ON:
   - Cloudflare → SSL/TLS → Enable this option
2. Check browser console for failing resources:
   - DevTools → Console → Look for warnings
   - Each warning shows the offending resource
3. If external resource, check if available on HTTPS
4. Update resource URLs to use HTTPS scheme

### TLS Version Lower Than 1.2

**Symptom**: `curl -v` shows `TLSv1.0` or `TLSv1.1`

**Causes**:
1. Minimum TLS Version not configured
2. Old Cloudflare settings

**Solutions**:
1. Set Minimum TLS Version:
   - Cloudflare → SSL/TLS → Edge Certificates
   - Minimum TLS Version: `1.2`
2. Allow 5-10 minutes for propagation
3. Clear browser cache

## Security Checklist

Before considering security setup complete, verify:

- [ ] HTTPS enforced (no HTTP access)
- [ ] HSTS header present with correct max-age
- [ ] HSTS includes subdomains
- [ ] TLS 1.2 or higher enforced
- [ ] Certificate valid and issued by trusted CA
- [ ] WWW redirects to root domain (301)
- [ ] No mixed content warnings
- [ ] Security headers present (X-Content-Type-Options, etc.)
- [ ] No certificate warnings in browser
- [ ] SSL Labs grade A or A+
- [ ] Security Headers grade A or A+

## Next Steps

After security configuration is complete:

1. **Submit Sitemap**: Follow next section in this guide
2. **Set Up Google Search Console**: Configure and verify ownership
3. **Monitor Security**: Regularly check SSL Labs and Security Headers
4. **Run Verification Scripts**: Use scripts in `/scripts` directory
5. **Review HSTS Preload**: After 3 months of stable operation, consider applying

## References

- [Cloudflare SSL/TLS Configuration](https://developers.cloudflare.com/ssl/)
- [HSTS Preload List](https://hstspreload.org/)
- [HTTP Strict Transport Security (HSTS) Explained](https://www.cloudflare.com/learning/ssl/what-is-hsts/)
- [Security Headers Guide](https://securityheaders.com/)
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
