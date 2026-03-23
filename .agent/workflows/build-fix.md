---
description: Incrementally fix TypeScript and build errors one at a time
---

# Build and Fix Workflow

Systematically fix TypeScript and build errors incrementally.

## When to Use

- Build is failing
- TypeScript errors present
- After major refactoring
- After dependency updates
- When errors are overwhelming

## Strategy

**Fix one error at a time for safety!**

Avoid cascading failures by:
- Fixing errors incrementally
- Verifying each fix before moving to next
- Stopping if fix introduces new errors

## Steps

### 1. Run Build
```bash
npm run build
# or
pnpm build
# or
yarn build
```

### 2. Parse Error Output

Group errors by:
- File location
- Error type
- Severity

Sort by:
- CRITICAL (blocking) first
- HIGH (important) second
- MEDIUM/LOW last

### 3. Fix Each Error Incrementally

For each error:

#### a) Show Error Context
```bash
# View 5 lines before/after error location
```

#### b) Explain the Issue
Understand what's causing the error:
- Type mismatch?
- Missing import?
- Syntax error?
- Configuration issue?

#### c) Propose Fix
Suggest the appropriate fix:
```typescript
// ❌ Current (broken)
const value: string = 123

// ✅ Fixed
const value: string = "123"
```

#### d) Apply Fix
Make the change to the file

#### e) Re-run Build
```bash
npm run build
```

#### f) Verify Error Resolved
- ✅ Error is gone
- ✅ No new errors introduced
- ✅ Build progresses further

### 4. Stop Conditions

Stop fixing if:
- ❌ Fix introduces new errors
- ❌ Same error persists after 3 attempts
- ❌ User requests pause
- ❌ Errors seem to be cascading
- ❌ Root cause is unclear

**Ask for help** if stuck!

### 5. Show Summary

After fixing session:

```
╔══════════════════════════════════════╗
║         Build Fix Summary            ║
╠══════════════════════════════════════╣
║ Errors Fixed:      X                 ║
║ Errors Remaining:  Y                 ║
║ New Errors:        Z                 ║
║ Status:            [PASS/FAIL]       ║
╚══════════════════════════════════════╝
```

## Common Error Types

### TypeScript Errors

**Type Mismatch:**
```typescript
// ❌ Error: Type 'number' is not assignable to type 'string'
const name: string = 123

// ✅ Fix
const name: string = "123"
```

**Missing Property:**
```typescript
// ❌ Error: Property 'id' is missing
const user: User = { name: "John" }

// ✅ Fix
const user: User = { id: 1, name: "John" }
```

**Null/Undefined:**
```typescript
// ❌ Error: Object is possibly 'undefined'
const value = data.value

// ✅ Fix
const value = data?.value ?? defaultValue
```

### Build Errors

**Missing Dependency:**
```bash
# ❌ Error: Cannot find module 'lodash'
npm install lodash
npm install --save-dev @types/lodash
```

**Configuration Issue:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true // Add if type errors in node_modules
  }
}
```

## Best Practices

**DO:**
- ✅ Fix one error at a time
- ✅ Verify each fix before moving on
- ✅ Understand the root cause
- ✅ Run build after each fix
- ✅ Commit working fixes incrementally

**DON'T:**
- ❌ Try to fix all errors at once
- ❌ Skip verification steps
- ❌ Use `@ts-ignore` without understanding
- ❌ Disable strict mode to hide errors
- ❌ Continue if errors are cascading

## Safety Checks

Before applying a fix:
- [ ] Understand why the error occurred
- [ ] Know what the fix will change
- [ ] Have a plan if fix fails
- [ ] Can revert if needed

After applying a fix:
- [ ] Build runs further than before
- [ ] No new errors introduced
- [ ] Error is actually resolved
- [ ] Code still makes sense

## Important Notes

**CRITICAL:** 
- One error at a time
- Verify after each fix
- Stop if cascading failures
- Ask for help if stuck

**Never:**
- Blindly apply fixes
- Use `any` type everywhere
- Disable TypeScript checks
- Skip understanding the error

## Related

- Agent: `build-error-resolver` in `.agent/agents/build-error-resolver.md`
- Skill: `systematic-debugging` in `.agent/skills/systematic-debugging/`
