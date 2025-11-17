# Feature Flags & Experiments Rules

**Last Updated:** January 15, 2025  
**Version:** 1.0  
**Applies To:** All projects (Argo Capital, Alpine Analytics LLC)

---

## Overview

Comprehensive feature flag management, A/B testing, and gradual rollout strategies to enable safe deployments and experimentation.

**Strategic Context:** Feature flags align with deployment safety and experimentation goals defined in [24_VISION_MISSION_GOALS.md](24_VISION_MISSION_GOALS.md).

---

## Feature Flag Principles

### Core Principles

1. **Safe Deployments:** Enable gradual rollouts
2. **Quick Rollback:** Disable features instantly
3. **Experimentation:** Enable A/B testing
4. **Environment Control:** Different flags per environment
5. **Clean Code:** Remove flags after feature is stable

---

## Feature Flag Naming

### Naming Convention

**Rule:** Use descriptive, hierarchical flag names

**Format:** `{service}_{feature}_{component}`

**Examples:**
```
trading_enable_new_risk_engine
alpine_enable_new_dashboard
api_enable_rate_limiting_v2
frontend_enable_dark_mode
```

**Components:**
- **Service:** `trading`, `alpine`, `api`, `frontend`
- **Feature:** Descriptive feature name
- **Component:** Optional component identifier

---

## Feature Flag Lifecycle

### Lifecycle Stages

**1. Development**
- Flag created
- Feature implemented behind flag
- Flag disabled by default
- Tested in development

**2. Staging**
- Flag enabled in staging
- Full testing completed
- Performance validated
- Ready for production

**3. Production - Gradual Rollout**
- Flag enabled for internal users (10%)
- Monitor metrics and errors
- Gradually increase (25%, 50%, 100%)
- Full rollout when stable

**4. Stable**
- Feature fully rolled out
- Flag always enabled
- Remove flag in next release
- Clean up flag code

### Flag States

**Enabled:** Feature is active
**Disabled:** Feature is inactive
**Rolling Out:** Gradually enabling (percentage-based)

---

## Feature Flag Implementation

### Backend Implementation

**Rule:** Use feature flag service/library

**Example:**
```python
from feature_flags import FeatureFlag

# Check flag
if FeatureFlag.is_enabled("trading_enable_new_risk_engine"):
    result = new_risk_engine.calculate_risk(signal)
else:
    result = old_risk_engine.calculate_risk(signal)
```

**With User Targeting:**
```python
if FeatureFlag.is_enabled_for_user(
    "alpine_enable_new_dashboard",
    user_id=user.id
):
    return render_new_dashboard()
else:
    return render_old_dashboard()
```

### Frontend Implementation

**Rule:** Use feature flag API or config

**Example:**
```typescript
import { useFeatureFlag } from '@/hooks/useFeatureFlag'

function Dashboard() {
  const showNewDashboard = useFeatureFlag('alpine_enable_new_dashboard')
  
  if (showNewDashboard) {
    return <NewDashboard />
  }
  
  return <OldDashboard />
}
```

---

## Gradual Rollout

### Rollout Strategy

**Rule:** Roll out features gradually

**Rollout Stages:**
1. **Internal (10%):** Team members only
2. **Beta (25%):** Selected users
3. **Wider (50%):** Half of users
4. **Full (100%):** All users

**Rollout Criteria:**
- No increase in error rate
- Performance metrics stable
- User feedback positive
- No critical bugs reported

### Percentage-Based Rollout

**Rule:** Use percentage-based targeting

**Implementation:**
```python
def should_enable_feature(flag_name: str, user_id: str) -> bool:
    flag = get_feature_flag(flag_name)
    
    if not flag.enabled:
        return False
    
    if flag.rollout_percentage == 100:
        return True
    
    # Consistent hash for user
    user_hash = hash(f"{flag_name}:{user_id}") % 100
    return user_hash < flag.rollout_percentage
```

---

## A/B Testing

### A/B Test Setup

**Rule:** Use feature flags for A/B testing

**Process:**
1. Create feature flag
2. Implement variant A (control)
3. Implement variant B (treatment)
4. Split traffic 50/50
5. Measure metrics
6. Choose winner
7. Roll out winner

**Example:**
```python
if FeatureFlag.is_enabled_for_user("new_signal_ui", user_id):
    # Variant B: New UI
    return render_new_signal_ui()
else:
    # Variant A: Old UI (control)
    return render_old_signal_ui()
```

### Metrics to Track

**Rule:** Track relevant metrics for A/B tests

**Metrics:**
- Conversion rates
- User engagement
- Error rates
- Performance metrics
- User satisfaction

---

## Feature Flag Management

### Flag Configuration

**Rule:** Store flags in configuration service

**Storage:**
- **Development:** Local config file
- **Staging:** Configuration service
- **Production:** Configuration service (e.g., LaunchDarkly, ConfigCat)

**Configuration Format:**
```json
{
  "trading_enable_new_risk_engine": {
    "enabled": true,
    "rollout_percentage": 50,
    "environments": ["staging", "production"],
    "target_users": [],
    "expires_at": "2025-02-15T00:00:00Z"
  }
}
```

### Flag Cleanup

**Rule:** Remove flags after feature is stable

**Cleanup Process:**
1. Feature fully rolled out (100%)
2. Flag enabled for 2+ weeks
3. No issues reported
4. Remove flag code
5. Remove flag configuration
6. Update documentation

**Code Cleanup:**
```python
# Before cleanup
if FeatureFlag.is_enabled("feature_name"):
    new_code()
else:
    old_code()

# After cleanup
new_code()  # Flag removed, always use new code
```

---

## Environment-Specific Flags

### Environment Rules

**Rule:** Use different flags per environment

**Development:**
- All flags can be enabled
- Test new features
- Experiment freely

**Staging:**
- Production-like flags
- Test full rollout
- Validate performance

**Production:**
- Gradual rollouts only
- Monitor carefully
- Quick rollback capability

---

## Flag Monitoring

### Monitoring Requirements

**Rule:** Monitor feature flag usage

**Metrics to Track:**
- Flag enable/disable rate
- Feature usage (when flag enabled)
- Error rates (by flag state)
- Performance impact
- User feedback

**Alerting:**
- Error rate increase when flag enabled
- Performance degradation
- Unusual usage patterns

---

## Emergency Rollback

### Rollback Process

**Rule:** Be able to disable flags instantly

**Process:**
1. Disable flag immediately
2. Verify feature disabled
3. Monitor error rates
4. Investigate issue
5. Fix and re-enable (if appropriate)

**Implementation:**
```python
# Emergency disable
FeatureFlag.disable("problematic_feature")

# Verify disabled
assert not FeatureFlag.is_enabled("problematic_feature")
```

---

## Feature Flag Best Practices

### Do's

✅ **DO:**
- Use flags for new features
- Test flags in staging first
- Roll out gradually
- Monitor metrics
- Clean up flags after stable
- Document flag purpose
- Set expiration dates

### Don'ts

❌ **DON'T:**
- Leave flags enabled forever
- Use flags for configuration (use config files)
- Create too many flags (maintenance burden)
- Enable flags without testing
- Ignore flag-related errors
- Skip monitoring

---

## Related Rules

- **Deployment:** [04_DEPLOYMENT.md](04_DEPLOYMENT.md) - Safe deployment process
- **Testing:** [03_TESTING.md](03_TESTING.md) - Testing with flags
- **Monitoring:** [14_MONITORING_OBSERVABILITY.md](14_MONITORING_OBSERVABILITY.md) - Flag monitoring

---

**Note:** Feature flags enable safe deployments and experimentation. Use them wisely, monitor carefully, and clean up after features are stable. Too many flags create maintenance burden - remove flags promptly after features are stable.

