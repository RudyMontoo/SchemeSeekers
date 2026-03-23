---
description: Comprehensive security and quality review of code changes
---

# Code Review Workflow

Perform comprehensive security and quality review of uncommitted changes.

## When to Use

- Before committing code
- Before creating pull requests
- After implementing features
- When security is critical
- Before production deployment

## Steps

### 1. Get Changed Files
```bash
git diff --name-only HEAD
```

### 2. Review Each File for Issues

#### Security Issues (CRITICAL) 🔴

Check for:
- [ ] Hardcoded credentials, API keys, tokens
- [ ] SQL injection vulnerabilities
- [ ] XSS vulnerabilities  
- [ ] Missing input validation
- [ ] Insecure dependencies
- [ ] Path traversal risks
- [ ] Command injection
- [ ] Insufficient authorization
- [ ] Race conditions in financial operations
- [ ] Logging sensitive data

#### Code Quality (HIGH) 🟡

Check for:
- [ ] Functions > 50 lines
- [ ] Files > 800 lines
- [ ] Nesting depth > 4 levels
- [ ] Missing error handling
- [ ] console.log statements
- [ ] TODO/FIXME comments
- [ ] Missing JSDoc for public APIs
- [ ] Duplicate code
- [ ] Complex conditionals

#### Best Practices (MEDIUM) 🟢

Check for:
- [ ] Mutation patterns (use immutable instead)
- [ ] Emoji usage in code/comments
- [ ] Missing tests for new code
- [ ] Accessibility issues (a11y)
- [ ] Performance concerns
- [ ] Inconsistent naming
- [ ] Missing type annotations

### 3. Generate Report

For each issue found, document:

**Severity:** CRITICAL | HIGH | MEDIUM | LOW

**Location:** `file.ts:line`

**Issue:** Description of the problem

**Suggested Fix:**
```typescript
// ✅ Correct implementation
```

### 4. Decision

- **BLOCK** if CRITICAL or HIGH security issues found
- **REQUEST CHANGES** if HIGH quality issues found
- **APPROVE WITH SUGGESTIONS** if only MEDIUM/LOW issues
- **APPROVE** if no issues found

## Security Checklist

Before approving any code:

- [ ] No hardcoded secrets
- [ ] All inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized HTML)
- [ ] CSRF protection enabled
- [ ] Authentication/authorization verified
- [ ] Rate limiting on endpoints
- [ ] Error messages don't leak sensitive data
- [ ] Dependencies up to date
- [ ] No vulnerable packages

## Quality Checklist

- [ ] Code follows project style guide
- [ ] Functions are small and focused
- [ ] Files are reasonably sized
- [ ] Error handling is comprehensive
- [ ] Tests cover new code (80%+ coverage)
- [ ] Documentation is updated
- [ ] No debug code (console.log, debugger)
- [ ] Performance is acceptable

## Report Template

```markdown
# Code Review Report

**Reviewer:** [Your Name]
**Date:** [Date]
**Files Reviewed:** [Count]

## Summary

- **Critical Issues:** X
- **High Issues:** Y
- **Medium Issues:** Z
- **Low Issues:** W
- **Risk Level:** 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW

## Critical Issues (Fix Immediately)

### 1. [Issue Title]
**File:** `path/to/file.ts:123`
**Severity:** CRITICAL
**Category:** SQL Injection

**Issue:**
[Description]

**Fix:**
```typescript
// ✅ Correct implementation
```

## Decision

**BLOCK** / **REQUEST CHANGES** / **APPROVE WITH SUGGESTIONS** / **APPROVE**

---

Never approve code with security vulnerabilities!
```

## Important Notes

**CRITICAL:** Never approve code with:
- Hardcoded secrets
- SQL injection vulnerabilities
- Missing authentication/authorization
- Unvalidated user input
- Known security vulnerabilities

**Block the commit/PR** until these are fixed.

## Related

- Agent: `code-reviewer` in `.agent/agents/code-reviewer.md`
- Agent: `security-reviewer` in `.agent/agents/security-reviewer.md`
- Skill: `security-review` in `.agent/skills/security-review/`
- Rules: `.agent/rules/security.md`
