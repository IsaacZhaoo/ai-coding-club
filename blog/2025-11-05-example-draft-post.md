---
slug: example-draft-post
title: Example Draft Post - Coming Soon
authors: [isaac]
tags: [announcement, draft-example]
draft: true
---

This is an example draft blog post. It demonstrates how to use the `draft: true` frontmatter to hide posts from production while keeping them visible in development.

<!--truncate-->

## How Draft Posts Work

When you set `draft: true` in the frontmatter:

- **Development mode** (`npm start`): Post is visible
- **Production build** (`npm run build`): Post is hidden
- **GitHub repository**: Source file is visible to everyone

## Publishing Workflow

To publish this post:

1. Remove `draft: true` from frontmatter
2. Commit and push to content repository
3. Deploy to production

## Benefits of This Approach

- Write content at your own pace
- Review and refine before publishing
- Maintain transparent development process
- Community can see upcoming content (acceptable for educational content)
