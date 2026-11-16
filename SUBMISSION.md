# CoursePilot submission

CS4973 · Abhi Karthik, Aditya Vij, Hudson Kass

**Submit the [Google Doc's Submission tab](https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit?tab=t.uig7mgyr21pt).** It links the materials below and is viewable by anyone with the link. Aditya and Hudson retain edit access. This Markdown page is a backup.

**In progress:** All three videos remain. The last teammate to finish submits the Google Doc linked above.

## Cases

| Case | Case owner | Document and code | Baseline results | Tester/video |
| --- | --- | --- | --- | --- |
| A: losing a required course while optimizing preferences | Aditya Vij | [Document](coursepilot/CASE_A.md), [case](coursepilot/cases/aditya_a.json), [starting data](coursepilot/fixtures/aditya_a.json) | [Five trials](coursepilot/CASE_A.md#results): 4/5 successful; one run dropped the required course and lab under preference pressure (disclosed but left as the final draft) | Hudson Kass; video pending |
| B: ignoring a new restriction or forgetting an earlier rule | Hudson Kass | [Document](coursepilot/CASE_B.md), [case](coursepilot/cases/hudson_b.json), [starting data](coursepilot/fixtures/hudson_b.json) | [Five completed runs / six attempts](coursepilot/CASE_B_RESULTS.md): original error retained; scoring correction and runtime differences disclosed | Abhi Karthik; video pending |
| C: treating discussion or save permission as registration permission | Abhi Karthik | [Document](coursepilot/README.md), [case](coursepilot/cases/approval_v2.json), [starting data](coursepilot/fixtures/approval_v2.json) | [Five trials](coursepilot/RESULTS.md): 5/5 successful, no approval failures | Aditya Vij; video pending |

[Public repository](https://github.com/abhik030/coursepilot-cs4973) · [Setup](coursepilot/TEAMMATE_GUIDE.md) · [Recording guides](coursepilot/REPRODUCTION.md)

The app runs locally using the tester's signed-in Codex CLI or Claude Code. Student data and university actions are mocked; model calls are real. C's recorded trials used Codex; A's and B's used Claude.

## Shared materials

- [Objective metrics, survey, and interview questions](evaluation/SHARED_METRICS.md)
- [Blank survey](evaluation/templates/survey.json) and [interview notes](evaluation/templates/interview-notes.md)

Each run saves timestamped messages/tools in `trajectory.json`, numeric metrics in `reward.json`, and mode/model/settings in `config.json`. No human-study responses have been collected or are due now.

## Before submitting

1. Finish A's case, document, five trials, and results. Keep B/C's existing evidence and report failures honestly.
2. Use the agreed rotation: Hudson records A, Aditya records C, Abhi records B. Add the actual recording details and keep case ownership distinct from recorded contribution history.
3. Add three setup/run videos and check grader access to every link.
4. Check that all cases use shared metrics/questions and document considered/rejected alternatives and the proposed-agent comparison.
5. Update the Google Doc and remove its in-progress notice when complete. Submit that Doc link once by the deadline. Check video sharing after the recordings are uploaded.
