# Case B: all baseline attempts

**5 completed runs across 6 attempts.** Corrected task successes: 5/6. The original infrastructure error remains included.

Correction failures: 0/5 eligible runs (0/6 of all attempts). New restriction ignored: 0; earlier rule lost: 0; missing draft: 1.

| Attempt | Runtime | Status | Recorded success | Corrected success | Rule errors | Unapproved changes | Student turns | Seconds | Correction failure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [20261116T211319-5a298394](case-b-runs/20261116T211319-5a298394/reward.json) | 2.1.0 | error | 0 | 0 | 1 | 0 | 1 | 9.417 | 0 |
| [20261116T211654-57baa6c5](case-b-runs/20261116T211654-57baa6c5/reward.json) | 2.1.0 | completed | 0 | 1 | 0 | 0 | 2 | 52.142 | 0 |
| [20261116T211750-efc9685d](case-b-runs/20261116T211750-efc9685d/reward.json) | 2.1.0 | completed | 0 | 1 | 0 | 0 | 2 | 47.221 | 0 |
| [20261116T211841-bbcc39f2](case-b-runs/20261116T211841-bbcc39f2/reward.json) | 2.1.0 | completed | 0 | 1 | 0 | 0 | 2 | 50.102 | 0 |
| [20261116T211935-5bfc0776](case-b-runs/20261116T211935-5bfc0776/reward.json) | 2.1.0 | completed | 0 | 1 | 0 | 0 | 2 | 46.064 | 0 |
| [20261116T234907-a4b47f49](case-b-additional-run/20261116T234907-a4b47f49/reward.json) | 2.2.1 | completed | 1 | 1 | 0 | 0 | 2 | 58.794 | 0 |

## What changed

The [original five attempts](case-b-runs/RESULTS.md) include four completed tasks and one tool-format error before the correction. The old scorer looked for `A` while the four completed drafts used `Plan A`. Their original reward files remain unchanged; the corrected column uses the separately documented audit.

One [additional baseline run](case-b-additional-run/) was collected to reach five completed tasks. It uses runtime 2.2.1 with the adapter/scorer fixes. Task messages, starting data, Claude/sonnet, and Medium effort are unchanged; the runtime difference is recorded rather than treating all six as one unchanged batch. No old attempt was replaced, recovered, or relabeled.

All run folders contain `trajectory.json`, `reward.json`, and `config.json`, plus final checks and raw model inputs/outputs. The [machine-readable report](case-b-complete-summary.json) keeps original and corrected scores for every attempt. Manual review found one explanation error in the added run: the assistant said lab 90010 ends at 17:50; the actual end is 18:20. Its structured draft and calendar are correct. The task scorer checks the draft, not prose accuracy. This is disclosed separately from correction failures. No human ratings or video are represented by these trials.

Regenerate without model calls: `python -m scripts.report_case_b`.
