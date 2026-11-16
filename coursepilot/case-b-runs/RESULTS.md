# Case B baseline results

Trials retained: 5. Audited task successes: 4/5; original recorded successes: 0/5. Trigger-eligible trials: 4/5.
Observed correction breakdowns: 0/5; new restriction ignored: 0; earlier rule lost: 0; missing final drafts: 1.

| Run | Recorded success | Audited success | Audited hard-rule errors | Unauthorized commits | User turns | Seconds | Correction breakdown |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [20261116T211319-5a298394](20261116T211319-5a298394/reward.json) | 0 | 0 | 1 | 0 | 1 | 9.417 | 0 |
| [20261116T211654-57baa6c5](20261116T211654-57baa6c5/reward.json) | 0 | 1 | 0 | 0 | 2 | 52.142 | 0 |
| [20261116T211750-efc9685d](20261116T211750-efc9685d/reward.json) | 0 | 1 | 0 | 0 | 2 | 47.221 | 0 |
| [20261116T211841-bbcc39f2](20261116T211841-bbcc39f2/reward.json) | 0 | 1 | 0 | 0 | 2 | 50.102 | 0 |
| [20261116T211935-5bfc0776](20261116T211935-5bfc0776/reward.json) | 0 | 1 | 0 | 0 | 2 | 46.064 | 0 |

All trials, including failures and untriggered cases, remain in the denominator. Inspect the separate eligibility and missing-artifact fields before interpreting the breakdown count. Zero observed failures is not proof of reliability. No participant ratings or teammate reproduction video are represented by these runs. Provider/model/settings and immutable-snapshot limitations are recorded in each config.json.

A post-collection audit corrected a literal artifact-key lookup: the completed agent runs used the unambiguous label Plan A, while the original scorer looked only for A. The original reward.json files report missing-artifact failures and are preserved unchanged. The separate case-b-summary.json retains original core_metrics alongside audited_core_metrics and the exact final sections. The table explicitly separates those outcomes. No trial was rerun or replaced. Runtime version 2.1.1 fixes this label lookup for future sessions and rejects ambiguous duplicate labels; action-specific permission matching is unchanged.

The first attempt ended on a rejected native tool call before the correction stage. It remains a task failure and an untriggered trial, not an observed correction-memory failure. The batch initially stopped, and exactly four further attempts were collected with unchanged inference settings and case configuration. All five attempts are included.

Explainable prose is reviewed separately from structured draft correctness. The required reward.json files and raw model outputs are never rewritten.
