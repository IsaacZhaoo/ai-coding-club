# Translation Maintenance Guide

**Version:** 1.0
**Last Updated:** 2025-11-04
**Status:** Active

## Overview

This guide defines the ongoing responsibilities for maintaining AI Coding Club's Chinese translation. It covers monthly and quarterly tasks, monitoring processes, and procedures for handling new content.

## Table of Contents

1. [Responsibilities](#responsibilities)
2. [Monthly Tasks](#monthly-tasks)
3. [Quarterly Tasks](#quarterly-tasks)
4. [Annual Tasks](#annual-tasks)
5. [Monitoring and Alerts](#monitoring-and-alerts)
6. [New Content Process](#new-content-process)
7. [Glossary Management](#glossary-management)
8. [Performance Metrics](#performance-metrics)
9. [Escalation Procedures](#escalation-procedures)

---

## Responsibilities

### Core Responsibilities

The Translation Team is responsible for:

1. **Coverage Maintenance**: Keep translation coverage above 80% for P0 and P1 content
2. **Quality Assurance**: Ensure translations meet quality standards
3. **Consistency**: Maintain terminology consistency using the glossary
4. **New Content**: Translate new English content within 2 weeks of publication
5. **Bug Fixes**: Address reported translation errors promptly
6. **Glossary Updates**: Maintain and expand the translation glossary
7. **Community Support**: Respond to translation-related issues and feedback

### Key Contacts

- **Translation Lead**: Responsible for overall coordination and decision-making
- **Community Manager**: Monitors feedback and reports issues
- **QA Reviewer**: Native speaker who validates translations
- **Content Team**: Notifies translation team of new content

---

## Monthly Tasks

### Week 1: Coverage Assessment

**Task:** Run translation coverage report

```bash
# Check current translation status
npm run check:translations

# Save results for comparison
npm run check:translations > coverage-report-$(date +%Y-%m).txt
```

**Action Items:**
- Review P0 and P1 coverage percentages
- Identify any drop in coverage since last month
- Flag any files that became untranslatable
- Check for new files added to the codebase

**Success Criteria:**
- P0 coverage = 100%
- P1 coverage >= 80%
- No unexplained coverage drops

### Week 2: Quality Review

**Task:** Identify and fix translation issues

**Process:**
1. Check GitHub issues labeled `i18n` or `translation`
2. Review user-reported translation bugs
3. Identify common translation problems
4. Create fixes or improvements

**Actions:**
```bash
# For each issue:
# 1. Locate the file
# 2. Review the translation
# 3. Fix the issue
# 4. Commit with clear message
cd content
git add i18n/
git commit -m "Fix: Improve translation of [filename] - [specific fix]"
git push origin main
```

**Example Issues to Look For:**
- Inconsistent terminology (e.g., "API" translated differently)
- Untranslated English text in Chinese page
- Incorrect links (missing `/zh/` prefix)
- Tone mismatches (too formal/casual)
- Grammar or spelling errors

### Week 3: New Content Review

**Task:** Identify and translate newly added English content

**Process:**
1. Check git log for new files in `content/docs/` and `content/blog/`
2. Identify files without Chinese translations
3. Prioritize by importance (P0 > P1 > P2 > P3)
4. Begin translation process

**Commands:**
```bash
# See recently modified files
cd content
git log --oneline --name-only -30 | grep -E "(docs|blog)" | sort -u

# Check which need translation
npm run check:translations
```

**Deadline:** Start translations within 1 week; complete within 2 weeks

### Week 4: Glossary Review

**Task:** Review and update the translation glossary

**Process:**
1. Review any new terms proposed by translators
2. Verify consistency with established terminology
3. Add new terms that appear repeatedly
4. Document changes for future reference

**File Location:**
```
content/i18n/glossary.json
```

**Example Update:**
```json
{
  "category": "programming-concepts",
  "en": "middleware",
  "zh": "中间件",
  "notes": "Standard translation in web development context"
}
```

---

## Quarterly Tasks

### Q1, Q2, Q3, Q4: Comprehensive Quality Audit

**Frequency:** Every 3 months (at end of quarter)
**Effort:** 8-12 hours
**Lead:** Translation Lead + QA Reviewer

#### Part 1: Coverage Audit

```bash
# Generate comprehensive coverage report
npm run check:translations

# Compare with previous quarter
# Document any drops or improvements
```

**Checklist:**
- [ ] Overall translation percentage
- [ ] P0 coverage (should be 100%)
- [ ] P1 coverage (should be >= 80%)
- [ ] Files with most impact untranslated
- [ ] Trends (improving or declining?)

#### Part 2: Quality Audit

**Sample 10-15 recently translated files:**

1. **Consistency Check**
   - Search for multiple translations of same terms
   - Verify glossary adherence
   - Check for duplicate meanings

2. **Accuracy Check**
   - Verify translations preserve original meaning
   - Check links are correctly localized
   - Ensure code examples unchanged

3. **Tone Check**
   - Verify friendly, beginner-focused tone
   - Check for overly formal language
   - Ensure consistency with brand voice

4. **Technical Check**
   - Verify Markdown formatting intact
   - Check images render correctly
   - Test links work properly

**Example Audit Script:**
```bash
# Check a sample of files
FILES=(
  "content/i18n/zh/docusaurus-plugin-content-docs/current/intro.md"
  "content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md"
  "content/i18n/zh/docusaurus-plugin-content-blog/2025-10-31-ai-coding-philosophy.md"
)

for file in "${FILES[@]}"; do
  echo "Auditing: $file"
  # Check for common issues:
  grep -n "en:" "$file" && echo "  WARNING: English term found"
  grep -n "TODO\|FIXME\|XXX" "$file" && echo "  WARNING: Unfinished translation"
done
```

#### Part 3: User Feedback Review

**Sources:**
- GitHub issues with `i18n` label
- Community discussions
- Direct user feedback
- Analytics data

**Process:**
1. Collect all feedback from past quarter
2. Categorize by issue type
3. Identify patterns or common problems
4. Plan fixes for next quarter

**Categories:**
- **Critical**: Breaks functionality (broken links, untranslated UI)
- **High**: Confusing translations, wrong terminology
- **Medium**: Grammar, tone, minor wording
- **Low**: Style preferences, alternative translations

#### Part 4: Documentation Review

**Update these documents:**
1. TRANSLATION_GUIDE.md - Any new patterns discovered?
2. TRANSLATION_WORKFLOW.md - Any new tips or issues?
3. This file - Any new procedures?
4. MAINTENANCE_GUIDE.md - Update statistics

**Template:**
```markdown
**Q[N] [YEAR] Audit Results**

Coverage:
- Overall: X%
- P0: 100%
- P1: X%
- P2: X%

Issues Found: Y
Issues Fixed: Z
Remaining: W

Key Improvements:
-

Recommendations:
-
```

#### Part 5: Generate Audit Report

**Create file:** `content/docs/internal/i18n/audits/AUDIT-Q[N]-[YEAR].md`

```markdown
# Q[N] [YEAR] Translation Audit Report

**Date:** [Date]
**Conducted by:** [Name]

## Summary

[Executive summary of audit results]

## Coverage Analysis

- Overall: X%
- P0: 100% (7/7)
- P1: X% (Y/Z)
- P2: X% (Y/Z)

## Quality Findings

### Consistency Issues
- [List any inconsistencies found]

### Technical Issues
- [List any broken links, formatting issues]

### Tone Issues
- [List any tone mismatches]

## User Feedback Summary

[Summary of feedback from past quarter]

## Recommendations

1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## Action Items

- [ ] [Task 1] - Owner
- [ ] [Task 2] - Owner
```

---

## Annual Tasks

### Year 1, Year 2, etc: Annual Review and Planning

**Timing:** End of calendar year or project year
**Effort:** 12-16 hours
**Participants:** Full translation team + leadership

#### Part 1: Comprehensive Retrospective

Review entire year:
- Coverage growth
- Quality improvements
- Community feedback
- Team performance
- Tool effectiveness

#### Part 2: Metrics Analysis

**Collect these metrics:**
```
- Number of files translated
- Average time per file
- Coverage growth (%)
- Issues reported vs fixed
- User satisfaction
- Glossary growth (# of terms)
- Tool usage stats
```

#### Part 3: Strategic Planning

**Plan for next year:**
1. Translation coverage goals
2. New language support
3. Tooling improvements
4. Team growth
5. Community engagement

---

## Monitoring and Alerts

### Automated Monitoring

The CI/CD pipeline (`build-and-validate.yml`) automatically monitors:

1. **Build Failures**: Alerts if translation breaks the build
2. **Coverage Drops**: Alerts if coverage drops below 80% threshold
3. **Broken Links**: Alerts for invalid internal links
4. **High Bounce Rate**: Alerts if Chinese pages have unusual traffic patterns

### Manual Monitoring

**Weekly Check:**
```bash
# Run coverage check
npm run check:translations

# Review GitHub issues
# Check Discord/Slack for translation issues
```

**Monthly Check:**
- Gather metrics in spreadsheet
- Review community feedback
- Check analytics dashboard

### Alert Escalation

**If coverage drops below 80%:**
1. Notify translation team
2. Identify cause (new files? missing translations?)
3. Create action plan
4. Update progress

**If critical file untranslated:**
1. Flag as high priority
2. Assign to translator immediately
3. Target: Complete within 1 week

**If multiple user complaints:**
1. Document the issue
2. Assess impact severity
3. Create fix
4. Communicate resolution to users

---

## New Content Process

### When New English Content is Published

**Timeline: From publication to translated**

#### Day 0: Publication
- New file added to `content/docs/` or `content/blog/`
- Content team notifies translation team

#### Day 1-2: Triage
```bash
# Check the new file
npm run check:translations

# Determine priority:
# P0 = Core content (intro, roadmap, Stage 0-2)
# P1 = Tools, essential lessons, popular blog posts
# P2 = Secondary lessons, niche content
# P3 = Archives, deprecated content
```

#### Day 3-7: Setup and Begin Translation
```bash
# Setup translation file
npm run translation:setup content/docs/[new-file].md

# Assign to translator
# Begin translation work
```

#### Day 8-14: Complete and Review
- Complete translation
- Native speaker review
- Fix any issues

#### Day 15: Merge and Deploy
```bash
# Commit translations
cd content
git add i18n/
git commit -m "i18n: Translate [content description]"
git push origin main

# Update main repo
cd ..
git add content
git commit -m "Update content: Add translation for [description]"
git push
```

### Priority Guidelines

**P0 (Critical) - Translate within 1 week:**
- Homepage content
- Introduction pages
- Course foundations/basics
- Roadmap content
- Getting started guides

**P1 (High) - Translate within 2 weeks:**
- Tool guides (ChatGPT, Claude, Cursor, etc.)
- Important lessons
- Popular blog posts
- Stage 1-2 content

**P2 (Medium) - Translate within 1 month:**
- Secondary lessons
- Tool comparisons
- Advanced tutorials
- Specialized topics

**P3 (Low) - Translate as capacity allows:**
- Archives
- Deprecated content
- Nice-to-have resources
- Low-traffic pages

---

## Glossary Management

### Adding New Terms

**When to add a term:**
- Used in multiple files
- Creates inconsistency if not standardized
- Specific to AI Coding Club domain

**How to add:**

1. Research the term (find standard Chinese translation)
2. Add to `content/i18n/glossary.json`:

```json
{
  "category": "[category]",
  "en": "[English term]",
  "zh": "[Chinese translation]",
  "notes": "[Context or usage notes]"
}
```

3. Commit change:
```bash
cd content
git add i18n/glossary.json
git commit -m "i18n: Add '[English term]' to glossary"
git push origin main
```

### Categories

- **tool-names**: AI tools, IDEs, platforms
- **programming-concepts**: Programming terms, software concepts
- **ui-ux-terms**: Interface elements, user experience terms
- **educational-terms**: Learning-related terminology
- **ai-specific-terms**: AI/ML specific concepts
- **action-verbs**: Common action verbs
- **project-specific**: AI Coding Club specific terms

### Glossary Maintenance

**Monthly:**
- Review proposed new terms
- Verify consistency with established usage
- Add approved terms

**Quarterly:**
- Audit glossary for relevance
- Remove outdated terms (if any)
- Document new patterns

**Annually:**
- Comprehensive glossary review
- Statistics: # of terms, growth rate
- Plan for next year's expansion

---

## Performance Metrics

### Key Metrics to Track

#### 1. Coverage Metrics

```
Overall Translation %:
  = (Translated Files / Total Files) × 100

P0 Coverage %:
  = (Translated P0 / Total P0) × 100
  Target: 100%

P1 Coverage %:
  = (Translated P1 / Total P1) × 100
  Target: >= 80%

Content Type Breakdown:
  - Docs: X%
  - Blog: X%
  - Course: X%
  - Tools: X%
```

#### 2. Quality Metrics

```
Issues Reported (monthly): [#]
Issues Fixed (monthly): [#]
Average Resolution Time: [days]

User Satisfaction: [feedback score]
  - Excellent: Very natural, idiomatic Chinese
  - Good: Clear, accurate, readable
  - Fair: Understandable but stiff
  - Poor: Confusing, incorrect, or untranslated
```

#### 3. Productivity Metrics

```
Files Translated (monthly): [#]
Average Time per File: [hours]
Glossary Additions (monthly): [#]

Efficiency Improvement:
  = (Files/Time) month-to-month
  Track improvement over time
```

#### 4. User Engagement Metrics

```
Chinese User Traffic: [#]
Language Switcher Clicks: [#]
Bounce Rate (EN vs ZH): [%]
Course Completion (EN vs ZH): [%]
Search Usage (Chinese): [#]
```

### Reporting Template

**Monthly Status Report:**
```
## Translation Status - [Month, Year]

### Coverage
- Overall: X% (up/down from Y%)
- P0: 100% ✅
- P1: X% (up/down from Y%)
- Course: X% (up/down from Y%)

### Activity
- Files translated: X
- Issues fixed: Y
- New glossary terms: Z

### User Feedback
- Issues reported: X
- Average satisfaction: [rating]

### Next Steps
- [Priority 1]
- [Priority 2]
```

---

## Escalation Procedures

### Issue Escalation Path

```
User Reports Issue
     ↓
Community Manager receives issue
     ↓
Assess severity (Critical/High/Medium/Low)
     ↓
If Critical → Immediate escalation
If High → Escalate to Translation Lead
If Medium → Log for next review cycle
If Low → Archive for future consideration
```

### Critical Issues (Same Day Response)

**Definition:** Translation prevents functionality or is seriously wrong

**Examples:**
- Broken links that prevent navigation
- Untranslated UI elements
- Seriously incorrect translation affecting understanding

**Response:**
```bash
# 1. Acknowledge issue
# 2. Identify root cause
# 3. Create fix immediately
# 4. Test fix
cd content
git add i18n/
git commit -m "Critical Fix: [Issue description]"
git push origin main

# 5. Follow up with user
# 6. Document in monthly report
```

### High Priority Issues (Within 1 Week)

**Definition:** Notable translation problem that impacts understanding

**Examples:**
- Incorrect terminology (confuses readers)
- Unnatural phrasing that's hard to understand
- Missing translations in important files

**Response:**
```bash
# 1. Log the issue
# 2. Assign to translator
# 3. Target completion: Within 1 week
# 4. Review before committing
# 5. Communicate fix to user
```

### Medium Priority Issues (Within 1 Month)

**Definition:** Translation could be better but doesn't prevent understanding

**Examples:**
- Grammar improvements
- Better phrasing options
- Tone adjustments
- Minor inconsistencies

**Response:**
- Log for next review cycle
- Include in monthly fixes
- Improve before quarterly audit

### Low Priority Issues (Backlog)

**Definition:** Style preferences, alternative translations

**Response:**
- Archive in backlog
- Review quarterly
- Include if capacity allows

---

## Documentation and Communication

### Internal Documentation

Keep these files up to date:

- **TRANSLATION_GUIDE.md**: Comprehensive translation philosophy
- **TRANSLATION_WORKFLOW.md**: Step-by-step process guide
- **This file (MAINTENANCE_GUIDE.md)**: Maintenance procedures
- **content/i18n/glossary.json**: Term dictionary
- **GitHub Issues**: Track bugs and feature requests

### External Communication

Share regular updates with:

- **Community**: Monthly blog post or newsletter
- **Users**: GitHub discussions, comments on translated pages
- **Team**: Weekly sync meetings (if applicable)

### Community Announcements

**Announce:**
- New languages supported
- Translation coverage milestones (e.g., "80% of course translated!")
- Major glossary updates
- Quarterly audit findings
- Annual reviews

**Example Announcement:**
```
🎉 Translation Milestone!
We're excited to announce that 80% of our course content is now available in Chinese!
This means [X] lessons, [Y] guides, and [Z] blog posts translated.
A huge thank you to our translation team for their hard work.

Continue learning in Chinese: [zh.aicoding.club/docs/course/]
```

---

## Tools and Resources

### Translation Tools

- **translation-setup.js**: Automate translation file setup
- **ai-translate.js**: AI-assisted translation drafts
- **check-translations.js**: Coverage reporting

### Utilities

```bash
# Check coverage
npm run check:translations

# Setup translation file
npm run translation:setup <file>

# AI translation (with API key)
npm run ai:translate <file>

# Validate build
npm run build

# Clear cache
npm run clear
```

### References

- **Glossary**: `content/i18n/glossary.json`
- **Translation Guide**: `content/docs/internal/i18n/TRANSLATION_GUIDE.md`
- **Workflow**: `content/docs/internal/i18n/TRANSLATION_WORKFLOW.md`
- **Docusaurus i18n**: [docs.docusaurus.io/i18n](https://docusaurus.io/docs/i18n/introduction)

---

## Contacts and Escalation

### Team Roles

| Role | Responsibilities | Contact |
|------|------------------|---------|
| **Translation Lead** | Overall coordination, glossary, standards | [@lead] |
| **Content Manager** | Identifies new content, prioritization | [@manager] |
| **QA Reviewer** | Native speaker review, quality validation | [@qa] |
| **Community Manager** | User feedback, issue triage | [@community] |

### Where to Report Issues

- **Translation Bug**: GitHub issue with `i18n` label
- **General Question**: GitHub Discussions
- **Urgent Issue**: Direct message to Translation Lead
- **New Content**: Notify via [channel]

---

## Appendix: Maintenance Checklist

### Monthly Checklist

- [ ] Run `npm run check:translations`
- [ ] Review translation coverage
- [ ] Review GitHub issues with `i18n` label
- [ ] Identify and fix quality issues
- [ ] Review new content for translation
- [ ] Update glossary with new terms
- [ ] Communicate status to team

### Quarterly Checklist

- [ ] Comprehensive quality audit
- [ ] Sample review of 10-15 files
- [ ] User feedback analysis
- [ ] Generate audit report
- [ ] Update documentation
- [ ] Plan next quarter

### Annual Checklist

- [ ] Full year retrospective
- [ ] Coverage trend analysis
- [ ] Community feedback review
- [ ] Team performance review
- [ ] Strategic planning for next year
- [ ] Update annual metrics

---

**Maintained by:** AI Coding Club Translation Team
**Questions?** Create issue with `i18n` label
