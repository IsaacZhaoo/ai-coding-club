# Domain Setup Guide: aicoding.club

This guide walks through binding the custom domain `aicoding.club` to the Cloudflare Pages deployment and configuring DNS records for proper resolution.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Add Custom Domain to Cloudflare Pages](#step-1-add-custom-domain-to-cloudflare-pages)
3. [Step 2: Configure DNS Records](#step-2-configure-dns-records)
4. [Step 3: Verify DNS Propagation](#step-3-verify-dns-propagation)
5. [Step 4: Test Domain Resolution](#step-4-test-domain-resolution)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before proceeding, ensure you have:

- [ ] Cloudflare Pages deployment created for `aicodingclub` project
- [ ] Domain `aicoding.club` registered and accessible
- [ ] Access to Cloudflare dashboard or domain registrar's DNS management
- [ ] DNS diagnostic tools installed (optional but recommended):
  - `dig` or `nslookup` (for DNS verification)
  - `curl` (for HTTPS verification)

## Step 1: Add Custom Domain to Cloudflare Pages

### Procedure

1. **Navigate to Cloudflare Pages Dashboard**:
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Select your account
   - Click **Pages** in the left sidebar
   - Select the `aicodingclub` project

2. **Access Custom Domains**:
   - Click on the **Custom domains** tab
   - This shows all currently configured custom domains

3. **Add Root Domain**:
   - Click the **"Set up a custom domain"** or **"Add a domain"** button
   - Enter the domain name: `aicoding.club` (without `www`)
   - Click **Continue**

4. **Review DNS Configuration**:
   - Cloudflare will display the DNS records needed:
     - **If domain is in Cloudflare**: CNAME record will be auto-configured
     - **If domain is external**: Cloudflare shows CNAME or A record options
   - Take note of the nameservers or DNS records shown

### Expected Outcome

- Domain appears in the "Custom domains" list
- Domain status shows as "Pending" (waiting for DNS propagation)
- Cloudflare has provisioned SSL certificate for the domain

## Step 2: Configure DNS Records

### If Domain is Hosted in Cloudflare

If `aicoding.club` is already in your Cloudflare account:

1. **Go to DNS Settings**:
   - Cloudflare Dashboard → Select domain `aicoding.club`
   - Click **DNS** in the left sidebar

2. **Verify CNAME Record**:
   - Look for a CNAME record pointing to: `aicodingclub.pages.dev`
   - If not present, create it:
     - **Type**: CNAME
     - **Name**: `aicoding.club` (or leave blank for root)
     - **Content**: `aicodingclub.pages.dev`
     - **TTL**: Auto or 300 seconds (for faster propagation during setup)
     - **Proxied**: Leave as-is (usually orange cloud)

3. **Save Changes**:
   - Click **Save** if you created the record

### If Domain is External (Namecheap, GoDaddy, etc.)

If the domain is hosted elsewhere, add the DNS record at your registrar:

#### Option A: CNAME Record (Recommended)

1. **Log in to Domain Registrar**:
   - Go to your registrar's DNS management (Namecheap, GoDaddy, Route 53, etc.)
   - Find DNS settings for `aicoding.club`

2. **Add CNAME Record**:
   - **Type**: CNAME
   - **Name**: `aicoding.club` or `@` (represents the root domain)
   - **Value**: `aicodingclub.pages.dev`
   - **TTL**: 300 seconds (for faster propagation)

3. **Save and Wait**:
   - DNS changes typically propagate in 5-30 minutes
   - Some registrars may take up to 1 hour

#### Option B: A Records (If CNAME Not Allowed)

If your registrar doesn't allow CNAME at the root domain:

1. **Get Cloudflare IP Addresses**:
   - Contact Cloudflare support or check Cloudflare Pages docs for IP ranges
   - Current Cloudflare Pages IPs (verify before using):
     - `104.200.131.0/24` (IPv4)
     - `2606:4700:3000::/48` (IPv6)

2. **Add A/AAAA Records**:
   - **Type**: A
   - **Name**: `aicoding.club` or `@`
   - **Value**: Use one of Cloudflare's IPs
   - **TTL**: 300 seconds

3. **Also Add AAAA Record**:
   - **Type**: AAAA
   - **Name**: `aicoding.club`
   - **Value**: IPv6 address from Cloudflare
   - **TTL**: 300 seconds

## Step 3: Verify DNS Propagation

DNS changes don't happen instantly. Monitor propagation using these methods:

### Method 1: Using DNS Propagation Checker (Online)

1. Go to [DNS Propagation Checker](https://www.whatsmydns.net/)
2. Enter: `aicoding.club`
3. Select record type: **CNAME** (or **A** if using A records)
4. View propagation status globally
5. Wait until all nameservers show green/resolved

### Method 2: Using `dig` Command (Linux/Mac)

```bash
# Check CNAME record
dig aicoding.club CNAME

# Expected output:
# aicoding.club. XXX IN CNAME aicodingclub.pages.dev.

# Check all records
dig aicoding.club

# Check specific nameserver
dig aicoding.club @8.8.8.8
```

### Method 3: Using `nslookup` Command

```bash
# Basic lookup
nslookup aicoding.club

# Check specific nameserver
nslookup aicoding.club 8.8.8.8
```

### What to Look For

- DNS resolves to `aicodingclub.pages.dev` (CNAME) or Cloudflare IP (A record)
- No "SERVFAIL" or timeout errors
- Propagation across multiple nameservers complete
- TTL countdown visible (showing record is active)

### Typical Timeline

| Timeframe | Status |
|-----------|--------|
| 0-5 minutes | Initial propagation started |
| 5-15 minutes | Most nameservers updated |
| 15-60 minutes | Global propagation complete |
| Up to 24 hours | Rare edge cases (DNS TTL exhaustion) |

## Step 4: Test Domain Resolution

Once DNS propagation is complete, test the domain:

### Test HTTPS Access

```bash
# Test domain with HTTPS
curl -I https://aicoding.club

# Expected response:
# HTTP/2 200
# cf-cache-status: HIT
# content-type: text/html
# etc.
```

### Test in Browser

1. Open browser to: `https://aicoding.club`
2. Check for:
   - [ ] Green padlock in address bar (HTTPS secure)
   - [ ] Page loads successfully
   - [ ] No "Not Secure" warning
   - [ ] CSS and JavaScript load correctly (no mixed content warnings)

### Test with Curl (Verbose)

```bash
# Verbose output showing certificate
curl -v https://aicoding.club

# Look for:
# * Connected to aicoding.club
# * TLSv1.3 (or TLSv1.2)
# * certificate verify ok
# HTTP/2 200
```

### Common Issues During Testing

| Issue | Solution |
|-------|----------|
| `curl: (6) Could not resolve host` | DNS not yet propagated, wait 5-15 min |
| `curl: (35) ...certificate problem` | SSL cert not issued yet, wait 5-10 min |
| `HSTS preload` warning | Expected, HSTS not yet configured |
| `Net::ERR_CERT_COMMON_NAME_INVALID` | Certificate issued, browser cache may need clear |

## Troubleshooting

### Domain Doesn't Resolve (SERVFAIL Error)

**Symptom**: `dig aicoding.club` returns SERVFAIL or no results

**Causes**:
1. DNS record not added to registrar
2. Registrar using different nameserver format
3. Typo in DNS record value

**Solutions**:
1. Verify DNS record exists at registrar:
   ```bash
   # Check registrar nameservers
   dig aicoding.club NS

   # Query registrar's nameserver directly
   dig @ns1.registrar.com aicoding.club
   ```

2. Check for typos in CNAME target:
   - Should be: `aicodingclub.pages.dev`
   - Not: `aicoding.pages.dev` or similar

3. Wait longer for propagation (up to 24 hours)

### DNS Resolves But HTTPS Connection Fails

**Symptom**: `dig aicoding.club` works but `curl https://aicoding.club` fails

**Causes**:
1. SSL certificate not yet issued
2. Certificate validation issue
3. Cloudflare proxy not enabled

**Solutions**:
1. Wait 5-10 minutes for certificate issuance
2. Check certificate with curl:
   ```bash
   curl -v https://aicoding.club 2>&1 | grep -i cert
   ```
3. In Cloudflare Pages, verify domain status is "Active" (not "Pending")

### Old DNS Still Cached

**Symptom**: Some devices/services show old IP, others show new

**Causes**:
1. DNS TTL not expired on devices
2. ISP DNS cache

**Solutions**:
1. Flush local DNS cache:
   ```bash
   # Linux
   sudo systemctl restart systemd-resolved

   # Mac
   sudo dscacheutil -flushcache

   # Windows
   ipconfig /flushdns
   ```

2. Query different nameservers:
   ```bash
   dig aicoding.club @8.8.8.8    # Google DNS
   dig aicoding.club @1.1.1.1    # Cloudflare DNS
   ```

### "Not Secure" Warning in Browser

**Symptom**: Browser shows "Not Secure" or certificate error

**Causes**:
1. Certificate not yet issued (typical: 5-10 min wait)
2. Mixed content (HTTP loaded from HTTPS page)
3. Browser cache with old certificate

**Solutions**:
1. Wait 5-10 minutes for certificate issuance
2. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Check browser console for mixed content:
   ```javascript
   // In browser console, look for mixed content warnings
   // Example: "Mixed Content: The page at 'https://aicoding.club/'..."
   ```
4. Verify "Automatic HTTPS Rewrites" is enabled in Cloudflare SSL/TLS settings

### Domain Works but www Subdomain Doesn't

**Symptom**: `aicoding.club` works but `www.aicoding.club` doesn't

**Causes**:
1. DNS record not added for www subdomain
2. Redirect rule not created yet

**Solutions**:
1. Add DNS record for www:
   - Type: CNAME
   - Name: `www`
   - Value: `aicodingclub.pages.dev`

2. Or use Cloudflare redirect rule (see SECURITY_CONFIG.md)

## Verification Checklist

After completing all steps, verify:

- [ ] DNS resolves: `dig aicoding.club` shows CNAME to `aicodingclub.pages.dev`
- [ ] HTTPS works: `curl -I https://aicoding.club` returns 200
- [ ] Certificate valid: `curl -v https://aicoding.club` shows valid cert
- [ ] Domain active: Browser shows green padlock
- [ ] No mixed content: Browser console shows no HTTPS/HTTP warnings
- [ ] Cloudflare shows "Active": Domain status in Cloudflare Pages dashboard
- [ ] Deployment working: Page content loads and displays correctly

Once all items checked, the domain is properly configured and ready for security setup (see SECURITY_CONFIG.md).

## Next Steps

After domain setup is complete:

1. **Configure HTTPS and HSTS**: See [SECURITY_CONFIG.md](./SECURITY_CONFIG.md)
2. **Set up WWW redirect**: See [SECURITY_CONFIG.md](./SECURITY_CONFIG.md)
3. **Submit sitemap**: See [SECURITY_CONFIG.md](./SECURITY_CONFIG.md)
4. **Run verification scripts**: See scripts in `/scripts` directory

## References

- [Cloudflare Pages Custom Domains](https://developers.cloudflare.com/pages/platform/custom-domains/)
- [DNS Lookup Tools](https://www.whatsmydns.net/)
- [Dig Man Page](https://linux.die.net/man/1/dig)
- [CNAME Records Explained](https://www.cloudflare.com/learning/dns/dns-records/dns-cname-record/)
