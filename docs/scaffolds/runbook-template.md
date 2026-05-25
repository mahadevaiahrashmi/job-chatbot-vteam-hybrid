---
agent-notes:
  ctx: "runbook template for operational procedures"
  deps: []
  state: canonical
  last: "ines@2026-02-15"
---
# Runbook: [Title]

<!-- Ines creates runbooks alongside the infrastructure they support. -->
<!-- Every alert must link to a runbook. If there's no runbook, don't create the alert. -->

**Service:** [service name]
**Alert:** [alert name that links here]
**Severity:** [P0/P1/P2/P3]
**Last tested:** [date]

## Symptoms

What does the operator see when this fires?

- [symptom 1]
- [symptom 2]

## Impact

What is the user-facing impact?

- [impact description]
- **Affected users:** [all / subset / internal only]

## Diagnosis Steps

1. [ ] Check [what] — `[command or dashboard link]`
2. [ ] Verify [what] — `[command]`
3. [ ] Look for [pattern] in logs — `[command]`

## Resolution Steps

### Quick fix (if applicable)

1. [ ] [immediate action]
2. [ ] Verify recovery — `[command]`

### Root cause fix

1. [ ] [investigation step]
2. [ ] [fix step]
3. [ ] Verify — `[command]`
4. [ ] Monitor for [duration]

## Rollback

If the fix makes things worse:

1. [ ] [rollback step]
2. [ ] Verify rollback — `[command]`

## Escalation

If you can't resolve within [timeframe]:

- **Escalate to:** [team/person]
- **Include:** [what information to share]

## Post-Incident

- [ ] Create post-mortem issue
- [ ] Update this runbook if diagnosis/resolution steps changed
- [ ] Review if alert threshold needs adjustment
