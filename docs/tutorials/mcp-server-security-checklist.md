---
title: "MCP Server Security Checklist: What to Verify Before You Connect"
description: "Use a practical MCP server security checklist to verify provenance, OAuth scopes, token handling, tool side effects, data access, logging, and revocation."
keywords:
  - MCP server security checklist
  - MCP security
  - Model Context Protocol security
  - MCP OAuth security
  - secure MCP server
sidebar_position: 12
tags: [tutorial, mcp, agent-engineering, security]
---

# MCP Server Security Checklist: What to Verify Before You Connect

*By Youguang — product developer, supply-chain skeptic*

---

The README is clean. The config block is three lines. Someone in a Discord thread says it "just works." You paste the snippet, restart your agent, and the new server appears in the tool list.

That moment — the half-second between reading the install command and running it — is the only moment when you are still fully in control of what your agent can reach, what credentials it can relay, and what a malicious tool description could instruct it to do. After that moment, you have delegated trust. The question is not whether the connection works. The question is: *what exactly did you just authorize?*

This checklist is a gate, not a guarantee. Passing every check does not certify a server as safe. It means you have done the inspection that makes a reasoned trust decision possible.

---

## Stop/Go Screen

Run through these five questions before spending time on the full 12-point review. A single **Stop** answer means you should not connect the server until that item is resolved.

| Question | Go | Stop |
|---|---|---|
| Can you identify a real publisher — an individual, company, or organization — with a verifiable public presence? | Yes | Publisher is anonymous or unverifiable |
| Is the install command pinned to a specific version, digest, or commit? | Yes | Latest/unpinned |
| Does the server request only the OAuth scopes or filesystem paths it demonstrably needs for its stated purpose? | Yes | Broad or unexplained scope |
| Are the tools and their descriptions publicly documented so you can read them before connecting? | Yes | Tool list is opaque or revealed only at runtime |
| Does the project have a documented way to revoke access or disable the server immediately? | Yes | No revocation or disable path described |

If you passed all five, proceed to the full review.

---

## The 12-Point Review

### 1. Publisher Provenance

**What to inspect:** The GitHub organization or user account, the npm/PyPI package owner, the domain of any hosted endpoint, and any "verified" badges on the registry page.

Find the real publisher. A name on a README is not provenance. Look for: a history of public commits, a verifiable company affiliation, a signing key on releases, or a track record in adjacent open-source projects. Check that the package registry owner matches the repository owner — supply-chain attacks frequently register a package under a lookalike account once the original project gains attention.

**What should make you stop:**
- No real individual or organization is identifiable.
- The package registry owner and the repository owner differ without explanation.
- The project appeared recently with a large star count but no commit history that supports it.

Popularity is not provenance. A server with thousands of stars and anonymous authorship is still anonymous.

---

### 2. Repository and Release Activity

**What to inspect:** Commit dates, open issues flagged as security-related, the release changelog, the gap between the last commit and the current published version, and whether automated CI runs on pull requests.

A well-maintained project has a visible paper trail. You are looking for evidence that someone is actually watching the code. Equally important: look for issues or PRs that describe suspicious behavior. Maintainers who close security issues with "won't fix" or "by design" are telling you something.

**What should make you stop:**
- The last commit is more than a year old but the README claims active support.
- Open issues describe unexpected network calls or credential access with no response.
- No signed releases, no changelog, no reproducible build path.

---

### 3. Exact Package and Install Command — Version Pinning

**What to inspect:** The install command the README gives you. Compare it to what your package manager will actually resolve.

`npm install @vendor/mcp-server` and `npm install @vendor/mcp-server@1.2.3` are completely different trust decisions. The first will silently install whatever the maintainer pushes tomorrow. Pin to a specific version, and where your toolchain supports it, pin to a content hash or digest. For Docker-distributed servers, require an image digest, not a tag.

If the official documentation only shows unpinned commands, that is a signal worth noting. Pin the package, image, or install artifact through the package manager or runtime where the toolchain supports it.

**What should make you stop:**
- The README insists on `@latest` or provides no version at all.
- The version you pin has known vulnerabilities disclosed after release.
- The package requires post-install scripts that run arbitrary code and the scripts are not reviewed.

---

### 4. Local Process Versus Remote Endpoint

**What to inspect:** How the server actually runs — stdio subprocess, local HTTP, or remote HTTPS — and what that means for your threat surface.

These are fundamentally different trust models:

- **stdio (local subprocess):** The server runs as a child process of your agent client. It has access to your local environment, including environment variables inherited from the parent process. This is where local-server compromise risk lives: a malicious package running locally can read files, make outbound network calls, and access credentials your shell has already loaded.
- **Local HTTP (e.g., localhost:3000):** Any other process on your machine can potentially reach this endpoint. It is not as isolated as stdio.
- **Remote HTTPS endpoint:** The server runs on infrastructure you do not control. Now you have data-in-transit concerns, the server operator can log everything, and the endpoint might be a proxy into systems you cannot inspect.

Claude Code documents local, project, and user scopes with different configuration visibility and sharing behavior; understand which one you are adding and why.

**What should make you stop:**
- A local server that requires broad filesystem or environment access without explanation.
- A remote server with no TLS or with a self-signed certificate.
- A remote server operated by an entity whose infrastructure you cannot verify.

---

### 5. Authorization Issuer and Redirect Behavior

**What to inspect:** If the server initiates an OAuth flow, verify: who is the authorization issuer, is the redirect URI validated, and where does the resulting token actually go.

The MCP specification calls out confused deputy attacks explicitly. A confused deputy occurs when a server with legitimate authority is manipulated into using it for the wrong client or request. Authorization requests, callbacks, client identity, and user consent must remain correctly bound throughout the OAuth flow.

Before you complete an OAuth login:
- Confirm the issuer is the service you expect (e.g., `accounts.google.com`, not a lookalike).
- Confirm the redirect URI is the server's own documented endpoint, not a third-party relay.
- Confirm the server is not performing token passthrough.

**Token passthrough** means the MCP server accepts a token that was not issued for it — for example, passing your GitHub access token directly to the server as if it were the intended audience. The official MCP guidance explicitly discourages this pattern because it means any compromise of the MCP server also compromises every service whose token it holds. A legitimate server should obtain its own tokens for its own audience and use them within its own boundary.

**What should make you stop:**
- The server's OAuth flow uses a redirect URI you do not recognize.
- The documentation asks you to pass your existing service tokens directly into the server configuration.
- The authorization issuer does not match the service the server claims to integrate.

---

### 6. Least Scopes

**What to inspect:** The OAuth scopes or permission sets the server requests, compared to its documented functionality.

Claude Code documents pinned OAuth scopes as a safeguard. The principle is simple: a server that reads your calendar should not request write access. A server that queries a read-only API should not request admin scopes. Read the scope request before you approve it.

Look for:
- Scopes that include `write`, `delete`, `admin`, or `*` (wildcard) when the server's stated function is read-only.
- Vague scopes like `full_access` or `all_data` with no documentation explaining why.
- A request for scopes to services that the server's stated function does not involve at all.

**What should make you stop:**
- Any scope that exceeds what the server's documented function requires.
- A scope list that changes between server versions without a corresponding changelog entry.
- No ability to approve specific scopes; the server requires all-or-nothing consent.

---

### 7. Secret Storage and Token Audience

**What to inspect:** How the server stores and handles secrets — API keys, tokens, credentials — and whether it enforces token audience checks.

Secrets in environment variables, in plaintext config files, or in a project-level `.mcp.json` that gets committed to source control are high-risk. For remote servers, investigate where credentials are stored on the server side and what the operator's data retention policy is.

Token audience matters: the server must validate that a token was issued for the intended resource rather than accepting arbitrary upstream tokens. Otherwise, tokens meant for another service can cross the boundary the authorization flow was supposed to enforce.

**What should make you stop:**
- The server's setup instructions ask you to add API keys to a file that will be committed to your repository.
- The server documentation does not mention how credentials are stored or protected.
- The server accepts tokens without verifying their intended audience.

---

### 8. Complete Tool List and Side Effects

**What to inspect:** Every tool the server registers, its description, and what real-world actions it can trigger.

This is one of the most overlooked checks. MCP tools are not passive interfaces — they are actions your agent can take on your behalf. A tool called `search_documents` sounds read-only. A tool called `post_to_api` sounds write-capable. But tool names alone are unreliable; you need to read the descriptions and, where available, the source code.

Specifically:
- Does the tool list match what the README claims the server does?
- Are there tools that were not mentioned in the marketing copy?
- Do the tool descriptions contain instructions to the model rather than descriptions of functionality? (This is a prompt-injection signal; see Check 11.)
- Do the tools trigger irreversible actions — sending emails, posting content, deleting records, making purchases?

Claude Code documents an approval flow for project-scoped server configuration. Use that review window to inspect the tool list and do not skip it.

**What should make you stop:**
- More tools are registered than the README describes.
- Tools have descriptions that contain phrases like "ignore previous instructions" or "always include X in your output."
- Tools trigger irreversible external actions with no confirmation step.

---

### 9. Filesystem and Network Reach

**What to inspect:** What filesystem paths the server can access, what outbound network connections it makes, and whether it can reach internal services or metadata endpoints.

SSRF (Server-Side Request Forgery) is explicitly listed in MCP security guidance. A server component — whether it is a local subprocess or a remote endpoint proxy — that fetches user-supplied URLs can be directed at internal services: your cloud provider's instance metadata endpoint (`169.254.169.254`), internal admin APIs, or other services inside your network perimeter. OWASP's SSRF guidance recommends allowlisting outbound destinations and validating that user-controlled input cannot redirect requests to internal addresses. Apply the same logic here.

For local servers: what directories does it read? Does it use the current working directory, home directory, or an explicitly scoped path? Claude Code documents cloned-repository protections and file access scoping — check whether the server you are adding respects equivalent boundaries.

**What should make you stop:**
- The server accepts arbitrary URLs from tool input without validation.
- The server requests filesystem access to paths outside its stated working scope.
- A remote server is positioned as a proxy into your internal infrastructure without explicit security documentation.

---

### 10. Prompt Injection and Untrusted Content Paths

**What to inspect:** Whether the server fetches, processes, or returns content from sources you do not control, and how that content reaches your agent's context.

This is the attack surface where supply-chain security meets model security. A server that retrieves web pages, documents, database records, or any external content and returns them verbatim to the model is also returning any instructions embedded in that content. A malicious actor who controls the content — a web page you asked the server to summarize, a document stored in a third-party system — can embed instructions that the model may follow.

Questions to ask:
- Does the server fetch content from third-party URLs that you provide as tool input?
- Does it index or process files from sources outside your control?
- Does it return that content directly, without sanitization or isolation, into the model's context?

There is no complete defense here that the server can provide on its own — this is an architectural risk. But understanding whether the data path exists helps you decide whether the server should operate in a context where it has write access or action-taking authority.

**What should make you stop:**
- The server fetches arbitrary external content and returns it to the model with no isolation, and it also has tools that take write or action-triggering operations.
- The server's tool descriptions themselves appear to contain model instructions rather than functional documentation.

---

### 11. Logging and Data Retention

**What to inspect:** What the server logs, where those logs go, how long they are retained, and who can access them.

A local server might write every tool call and every result to a local log file — which may include API responses, document snippets, or data you passed through the tool. A remote server logs everything it receives, potentially including credentials, document content, or query parameters containing sensitive data.

Ask:
- Is there a privacy policy or data handling document for remote servers?
- Where do local server logs go — a temp directory, a persistent path, a cloud service?
- Are logs encrypted at rest?
- Is there a retention limit, or do logs accumulate indefinitely?

Claude Code's stdio proxy considerations are relevant here: when you add a server that acts as a proxy, you may be routing data through an additional logging layer.

**What should make you stop:**
- A remote server has no data handling documentation.
- A local server writes logs to a path that syncs to cloud storage without your knowledge.
- Log files include raw credentials or tokens.

---

### 12. Disable, Revoke, Update, and Incident Path

**What to inspect:** How you turn the server off immediately, how you revoke its credentials, how you apply security updates, and where you report a problem.

Before you connect a server, you should know how to disconnect it. This is not paranoia; it is incident response preparation. If a server exhibits unexpected behavior — making network calls you did not authorize, accessing files outside its scope, failing in ways that suggest compromise — you need to be able to stop it faster than you can read documentation.

Verify:
- Is there a documented way to remove the server from your client configuration immediately?
- Can you revoke the server's OAuth tokens from the issuing service's dashboard?
- Is there a security contact or responsible disclosure path?
- How are security updates published — are you notified, or do you have to check manually?

Claude Code allows servers to be removed or disabled in the applicable local, project, or user scope. Know which scope you used so you know where to remove it.

**What should make you stop:**
- No revocation path exists for the credentials the server uses.
- The project has no security contact or disclosure policy.
- Updates are silent with no changelog; you cannot tell when a security fix was applied.

---

## Risk-to-Check Mapping

The official MCP security guidance defines several risk families. This table maps each risk to the checks above.

| Risk Family | Primary Checks | Secondary Checks |
|---|---|---|
| Confused Deputy | 5 (Authorization issuer) | 6 (Least scopes), 7 (Token audience) |
| Token Passthrough | 7 (Token audience/storage) | 5 (Authorization behavior) |
| SSRF | 9 (Network reach) | 10 (Untrusted content paths) |
| Session Hijacking | 5 (Redirect validation) | 7 (Secret storage) |
| Local Server Compromise | 4 (Process type) | 1 (Provenance), 3 (Version pinning) |
| Authorization URL Validation | 5 (Issuer/redirect) | 12 (Revocation path) |
| Scope Minimization | 6 (Least scopes) | 7 (Token audience) |
| Prompt Injection | 10 (Untrusted content) | 8 (Tool descriptions) |
| Supply-Chain Substitution | 1 (Provenance), 2 (Activity), 3 (Pinning) | 12 (Update path) |
| Excessive Filesystem Access | 9 (Filesystem reach) | 4 (Process type) |

---

## Post-Connection Monitoring and Revocation

Passing the checklist before connection is the start of the trust relationship, not the end.

### After You Connect

**Watch what the server actually does.** Enable whatever logging your MCP client provides. Claude Code and other clients may surface tool calls in context; review them periodically, especially for any server that has write-capable tools or broad network access. Look for:
- Tool calls you did not trigger explicitly.
- Network requests to destinations outside the server's stated scope.
- Files read or written outside expected paths.

**Review changelogs before updating.** A version bump can add new tools, request new scopes, or change how credentials are handled. Do not auto-update servers that hold sensitive credentials or have broad system access. Treat version updates as a re-review of Checks 3, 6, 8, and 9.

**Audit scope grants periodically.** If the server uses OAuth, visit the connected-applications page of the issuing service (GitHub, Google, etc.) and verify the current scope grant matches what you approved. Some servers request elevated scopes at renewal time without alerting you.

### Revocation Procedure

If you observe unexpected behavior, apply this sequence:

1. **Disconnect the server** from your client configuration immediately. In Claude Code, this means removing it from the applicable scope (user or project). Do not wait to investigate; disconnect first.
2. **Revoke OAuth tokens** from the authorization issuer's dashboard. Do not assume disconnecting the client also revokes the token — these are independent operations.
3. **Rotate any secrets** that were stored in environment variables or config files that the server had access to. If you cannot determine exactly what the server could read, rotate broadly.
4. **Review agent session history** for tool calls made during the period the server was connected.
5. **Report the behavior** to the server's security contact if one exists, and to the relevant package registry if the issue suggests supply-chain compromise.

### Server Inventory Hygiene

The most common post-connection failure is accumulation: servers you added for a single project, never removed, still holding OAuth tokens you forgot about. Keep a short inventory of every server you have connected, the scope at which it is active, and the last time you reviewed it. Quarterly is a reasonable cadence for anything with write access.

---

## A Note on Client-Specific Safeguards

This checklist references Claude Code behaviors — project approval flows, pinned scopes, cloned-repository protections, stdio proxy considerations — because those are the documented safeguards in that client. Other MCP clients may implement similar protections, fewer, or different ones. The security properties described here are not universal MCP guarantees; they reflect the specification's requirements and one client's implementation.

Before connecting a server in any client, verify what safeguards that specific client provides. The responsibility the checklist places on you — reading tool lists, verifying OAuth issuers, understanding filesystem scope — is the portion that no client can automate away. It requires a human decision.

---

## Summary

Every MCP server is an executable integration. It can run code, make requests, receive credentials, and expose tool calls for your agent to use. The one-line install command is the convenience end of a trust decision whose other end includes authorization scope, data retention, network reach, and incident response.

The 12 checks above are the minimum responsible review. Do the stop/go screen first. Investigate the full checklist before connecting anything with write access, OAuth credentials, or broad filesystem scope. Know your revocation path before you need it. And treat the first unexpected behavior you observe as a reason to disconnect immediately and investigate, not as a reason to check the issue tracker.

The server that is easiest to add is not always the one you want in your agent's toolchain.

---

*References: [MCP Security Best Practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices) — Model Context Protocol specification; [MCP Authorization](https://modelcontextprotocol.io/specification/latest/basic/authorization) — Model Context Protocol specification; [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp) — Anthropic; [OWASP Server-Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) — OWASP Foundation.*

## Related Guides

- [Claude Code Skills, Hooks, and MCP](/docs/tutorials/claude-code-skills-hooks-mcp/)
- [Coding Agent Sandbox Security](/docs/tutorials/coding-agent-sandbox-security/)
