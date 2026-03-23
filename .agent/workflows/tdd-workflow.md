---
description: Test-Driven Development workflow - write tests first, implement minimal code, refactor
---

# TDD Workflow

Enforce test-driven development methodology with RED → GREEN → REFACTOR cycle.

## When to Use

- Implementing new features
- Adding new functions/components
- Fixing bugs (write test that reproduces bug first)
- Refactoring existing code
- Building critical business logic

## TDD Cycle

```
RED → GREEN → REFACTOR → REPEAT

RED:      Write a failing test
GREEN:    Write minimal code to pass
REFACTOR: Improve code, keep tests passing
REPEAT:   Next feature/scenario
```

## Steps

### 1. Define Interface (SCAFFOLD)
Define types/interfaces first before any implementation.

```typescript
export interface MyData {
  // Define your data structure
}

export function myFunction(data: MyData): ReturnType {
  throw new Error('Not implemented')
}
```

### 2. Write Failing Test (RED)
Write tests that will FAIL because code doesn't exist yet.

```typescript
import { myFunction } from './myModule'

describe('myFunction', () => {
  it('should handle happy path', () => {
    const result = myFunction(testData)
    expect(result).toBe(expectedValue)
  })

  it('should handle edge cases', () => {
    // Test edge cases
  })

  it('should handle errors', () => {
    // Test error conditions
  })
})
```

### 3. Run Tests - Verify FAIL
```bash
npm test
# Verify tests fail for the RIGHT reason
```

✅ Tests should fail with "Not implemented" or similar

### 4. Implement Minimal Code (GREEN)
Write just enough code to make tests pass.

```typescript
export function myFunction(data: MyData): ReturnType {
  // Minimal implementation to pass tests
  return result
}
```

### 5. Run Tests - Verify PASS
```bash
npm test
# All tests should pass
```

✅ All tests passing!

### 6. Refactor (IMPROVE)
Improve code quality while keeping tests green.

- Extract constants
- Improve readability
- Add helper functions
- Optimize performance

### 7. Verify Tests Still Pass
```bash
npm test
# Tests should still pass after refactoring
```

### 8. Check Coverage
```bash
npm test -- --coverage
# Ensure 80%+ coverage (100% for critical code)
```

## Coverage Requirements

- **80% minimum** for all code
- **100% required** for:
  - Financial calculations
  - Authentication logic
  - Security-critical code
  - Core business logic

## Best Practices

**DO:**
- ✅ Write the test FIRST, before any implementation
- ✅ Run tests and verify they FAIL before implementing
- ✅ Write minimal code to make tests pass
- ✅ Refactor only after tests are green
- ✅ Add edge cases and error scenarios
- ✅ Aim for 80%+ coverage

**DON'T:**
- ❌ Write implementation before tests
- ❌ Skip running tests after each change
- ❌ Write too much code at once
- ❌ Ignore failing tests
- ❌ Test implementation details (test behavior)
- ❌ Mock everything (prefer integration tests)

## Test Types

**Unit Tests** (Function-level):
- Happy path scenarios
- Edge cases (empty, null, max values)
- Error conditions
- Boundary values

**Integration Tests** (Component-level):
- API endpoints
- Database operations
- External service calls
- React components with hooks

**E2E Tests** (use `/e2e` workflow):
- Critical user flows
- Multi-step processes
- Full stack integration

## Important Notes

**MANDATORY**: Tests must be written BEFORE implementation.

Never skip the RED phase. Never write code before tests.

## Related

- Agent: `tdd-guide` in `.agent/agents/tdd-guide.md`
- Skill: `test-driven-development` in `.agent/skills/test-driven-development/`
