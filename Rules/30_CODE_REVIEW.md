# Code Review & Pull Request Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All code changes (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive code review process, PR templates, and review guidelines to ensure code quality, knowledge sharing, and consistent standards.

**Strategic Context:** Code review aligns with code quality goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

**See Also:** [02_CODE_QUALITY.md](02_CODE_QUALITY.md) for code quality checklist, [.cursor/BUGBOT.md](.cursor/BUGBOT.md) for automated review guidelines.

---

## Pull Request Process

### PR Requirements

**Rule:** All code changes must go through PR review

**Requirements:**
- ✅ All tests pass
- ✅ Linting passes
- ✅ Code coverage maintained (95%+ for critical paths)
- ✅ Documentation updated
- ✅ No merge conflicts
- ✅ PR description completed

### PR Template

**Rule:** Use PR template for all pull requests

**Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Refactoring
- [ ] Documentation
- [ ] Performance improvement
- [ ] Security fix

## Related Issues
Closes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests pass locally
```

---

## Review Assignment

### Required Reviewers

**Rule:** Assign appropriate reviewers

**By Change Type:**
- **Security changes:** Security team member required
- **Trading logic:** Senior developer + trading expert
- **Database changes:** Database expert required
- **Infrastructure:** DevOps/Infrastructure team
- **Frontend:** Frontend team member
- **Backend:** Backend team member

### Review Assignment Rules

**Automatic Assignment:**
- Code owners (CODEOWNERS file)
- Team members in changed directory
- Previous contributors to changed files

**Manual Assignment:**
- Subject matter experts
- Senior developers for complex changes
- Security team for security-related changes

---

## Review Guidelines

### What to Review

**1. Functionality**
- Does the code do what it's supposed to?
- Are edge cases handled?
- Are error cases handled?
- Is the implementation correct?

**2. Code Quality**
- Follows coding standards
- Follows SOLID principles
- No code duplication
- Proper error handling
- Appropriate logging

**3. Testing**
- Adequate test coverage
- Tests are meaningful
- Edge cases tested
- Integration tests where needed

**4. Security**
- No security vulnerabilities
- Input validation
- Authentication/authorization
- No secrets in code
- SQL injection prevention

**5. Performance**
- No performance regressions
- Appropriate use of caching
- Efficient algorithms
- Database query optimization

**6. Documentation**
- Code is self-documenting
- Complex logic explained
- API documentation updated
- README updated if needed

### Review Checklist

**Architecture & Design:**
- [ ] Follows SOLID principles
- [ ] Appropriate design patterns
- [ ] Clear separation of concerns
- [ ] Scalable design

**Code Structure:**
- [ ] Functions under 50 lines
- [ ] Max 3-4 parameters per function
- [ ] Max 3-4 levels of nesting
- [ ] No code duplication
- [ ] No dead code

**Error Handling:**
- [ ] All operations wrapped in try/catch
- [ ] Specific exception types used
- [ ] Meaningful error messages
- [ ] Proper logging with context
- [ ] No silent failures

**Security:**
- [ ] Input validation at boundaries
- [ ] Request size limits implemented
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] No hardcoded secrets
- [ ] No default/weak secrets (fail fast if detected)
- [ ] Proper authentication/authorization
- [ ] No duplicate authentication logic
- [ ] Token blacklist checked on authenticated requests
- [ ] Admin endpoints require authentication AND authorization
- [ ] CSRF protection with origin validation
- [ ] Rate limiting (fail-closed in production)
- [ ] PII redaction in logs

**Performance:**
- [ ] No N+1 query problems
- [ ] Appropriate caching used
- [ ] Async operations for I/O
- [ ] Optimized algorithms
- [ ] Connection pooling used

**Testing:**
- [ ] Unit tests for business logic
- [ ] Integration tests for critical paths
- [ ] Edge cases covered
- [ ] Test isolation maintained
- [ ] 95%+ coverage for critical paths

**Documentation:**
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] Examples provided
- [ ] README updated if needed

---

## Review Comments

### Comment Types

**1. Must Fix (Blocking)**
- Security vulnerabilities
- Bugs that will cause failures
- Violations of critical rules
- Missing error handling

**2. Should Fix (Non-Blocking)**
- Code quality improvements
- Performance optimizations
- Better error messages
- Documentation improvements

**3. Nice to Have (Optional)**
- Style improvements
- Minor refactoring
- Additional comments
- Optional optimizations

### Comment Guidelines

**Rule:** Provide constructive, actionable feedback

**Good Comments:**
- Specific and clear
- Explain why, not just what
- Suggest solutions
- Reference relevant rules
- Be respectful and professional

**Example:**
```
This function is doing too much. Consider extracting the 
validation logic into a separate function following the 
Single Responsibility Principle (Rule 02). This would 
make the code more testable and maintainable.
```

**Bad Comments:**
- Vague ("This is wrong")
- Personal attacks
- No explanation
- No suggestions

---

## Review Turnaround

### Response Time Expectations

**Rule:** Respond to PRs within business hours

**Targets:**
- **Initial Review:** Within 24 hours
- **Re-review:** Within 4 hours after changes
- **Approval:** Within 48 hours for standard PRs
- **Urgent PRs:** Within 4 hours

### PR Status

**Labels:**
- `needs-review` - Waiting for review
- `in-review` - Currently being reviewed
- `changes-requested` - Changes needed
- `approved` - Ready to merge
- `blocked` - Blocked by dependencies

---

## Approval Requirements

### Approval Rules

**Rule:** Require appropriate approvals

**Standard PRs:**
- 1 approval from code owner
- All CI checks pass
- No blocking comments

**Critical PRs:**
- 2 approvals (including senior developer)
- Security review (if security-related)
- All CI checks pass
- No blocking comments

**Critical Areas:**
- Trading logic
- Security changes
- Database migrations
- Infrastructure changes
- Authentication/authorization

---

## Automated Reviews

### Bugbot Integration

**Rule:** Use Bugbot for automated code review

**See:** [.cursor/BUGBOT.md](.cursor/BUGBOT.md) for Bugbot configuration

**Bugbot Checks:**
- Security vulnerabilities
- Code quality issues
- Naming convention violations
- Test coverage gaps
- Performance issues
- SOLID principles violations
- Error handling gaps
- Documentation issues

**Bugbot Status:**
- Must pass before manual review
- Fix all Bugbot issues before requesting review
- Bugbot comments are blocking

### CI/CD Checks

**Rule:** All CI checks must pass

**Required Checks:**
- Linting (Ruff, ESLint)
- Type checking (mypy, TypeScript)
- Unit tests
- Integration tests
- Code coverage
- Security scanning
- Build verification

---

## Merge Strategies

### Merge Methods

**Rule:** Use appropriate merge method

**Squash and Merge (Recommended):**
- Clean commit history
- One commit per PR
- Easier to revert
- Use for feature branches

**Rebase and Merge:**
- Linear history
- Preserves individual commits
- Use for small, focused PRs

**Merge Commit:**
- Preserves branch history
- Use for long-lived branches
- Not recommended for feature branches

### Merge Requirements

**Before Merging:**
- [ ] All reviews approved
- [ ] All CI checks pass
- [ ] No merge conflicts
- [ ] PR description complete
- [ ] Related issues linked
- [ ] Documentation updated

---

## Post-Merge

### After Merge

**Rule:** Verify merge success

**Verification:**
- Check CI/CD pipeline
- Verify deployment (if auto-deploy)
- Monitor error rates
- Check application logs

### Rollback Plan

**Rule:** Have rollback plan ready

**If Issues After Merge:**
1. Revert PR immediately
2. Investigate issue
3. Fix and re-submit
4. Document lessons learned

---

## Review Best Practices

### For Authors

**Before Submitting:**
- Self-review your code
- Run all tests locally
- Fix linting issues
- Update documentation
- Write clear PR description

**During Review:**
- Respond to comments promptly
- Ask questions if unclear
- Be open to feedback
- Make requested changes
- Explain if you disagree

### For Reviewers

**Review Guidelines:**
- Review within 24 hours
- Be constructive and respectful
- Explain your reasoning
- Suggest improvements
- Approve when satisfied
- Don't nitpick unnecessarily

**Review Focus:**
- Correctness and functionality
- Code quality and maintainability
- Security and performance
- Testing and documentation
- Not style preferences (use linters)

---

## Related Rules

- **Code Quality:** [02_CODE_QUALITY.md](02_CODE_QUALITY.md) - Code quality checklist
- **Testing:** [03_TESTING.md](03_TESTING.md) - Testing requirements
- **Security:** [07_SECURITY.md](07_SECURITY.md) - Security review
- **Bugbot:** [.cursor/BUGBOT.md](.cursor/BUGBOT.md) - Automated review

---

**Note:** Code review is critical for code quality, knowledge sharing, and catching issues early. Always be respectful, constructive, and thorough in reviews. Remember: we're reviewing code, not people.

