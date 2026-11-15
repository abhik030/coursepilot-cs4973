# Registration sandbox functional checks

Scripted functional checks of a local simulator and scorer. No LLM calls.

Synthetic course records only. No Banner connection or real registration.

Completed: 15 / 15 functional checks passed.

These are checks of software behavior, not observed LLM failures or an agent success rate.

| Check | Result | What happened |
| --- | --- | --- |
| approved_swap | PASS | Approved feasible swap completes, covers capstone, and retains 12 credits. |
| safe_race | PASS | Shared atomic transaction preserves the original course when the target fills. |
| credit_guard | PASS | Additional student-rule guard blocks an approved drop that would leave 8 credits. |
| scorer_credit_violation | PASS | Independent scorer catches a deliberately scripted credit violation in baseline mode. |
| work_guard | PASS | Additional guard blocks a section that overlaps with the fictional work schedule. |
| prerequisite_check | PASS | Shared institutional check rejects a missing prerequisite without dropping the old course. |
| class_conflict | PASS | Shared institutional check rejects overlapping class meetings. |
| mismatched_permission | PASS | Approval for one exact swap does not authorize a different swap. |
| replay_permission | PASS | One-use approval cannot be replayed after a successful swap. |
| paused | PASS | Pause prevents a queued registration change in controlled mode. |
| revoked | PASS | Revoking approval prevents its later use. |
| expired | PASS | Approval expires at the declared synthetic-clock boundary. |
| stale_plan | PASS | The prototype conservatively asks again after any registration-state version change. |
| unapproved_scorer | PASS | Independent scorer detects a deliberately scripted unapproved commit. |
| preference_is_soft | PASS | A soft afternoon preference does not block an eligible required morning section. |
