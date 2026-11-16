# CoursePilot submission

CS4973 · Abhi Karthik, Aditya Vij, Hudson Kass

**In progress:** Case A, creator/tester confirmations, and all three videos remain. The last teammate to finish submits this single index.

## Cases

| Case | Creator | Document and code | Baseline results | Tester/video |
| --- | --- | --- | --- | --- |
| A: losing a required course while optimizing preferences | Aditya proposed | Pending; [guide](coursepilot/TEAMMATE_GUIDE.md) | Pending | Hudson proposed; video pending |
| B: ignoring a new restriction or forgetting an earlier rule | Unconfirmed; Hudson proposed | [Document](coursepilot/CASE_B.md), [case](coursepilot/cases/hudson_b.json), [starting data](coursepilot/fixtures/hudson_b.json) | [Five attempts](coursepilot/case-b-runs/RESULTS.md): four correct completions, one tool-format error; original and corrected scores shown separately | Abhi proposed; video pending |
| C: treating discussion or save permission as registration permission | Abhi Karthik | [Document](coursepilot/README.md), [case](coursepilot/cases/approval_v2.json), [starting data](coursepilot/fixtures/approval_v2.json) | [Five trials](coursepilot/RESULTS.md): 5/5 successful, no approval failures | Aditya proposed; video pending |

[Public repository](https://github.com/abhik030/coursepilot-cs4973) · [Setup](coursepilot/TEAMMATE_GUIDE.md) · [Recording guides](coursepilot/REPRODUCTION.md)

The app runs locally using the tester's signed-in Codex CLI or Claude Code. Student data and university actions are mocked; model calls are real. C's recorded trials used Codex; B's used Claude.

## Shared materials

- [Objective metrics, survey, and interview questions](evaluation/SHARED_METRICS.md)
- [Blank survey](evaluation/templates/survey.json) and [interview notes](evaluation/templates/interview-notes.md)

Each run saves timestamped messages/tools in `trajectory.json`, numeric metrics in `reward.json`, and mode/model/settings in `config.json`. No human-study responses have been collected or are due now.

## Before submitting

1. Finish A's case, document, five trials, and results. Keep B/C's existing evidence and report failures honestly.
2. Confirm who created/tested each case. Each video must be recorded by someone other than the creator.
3. Add three setup/run videos and check grader access to every link.
4. Check that all cases use shared metrics/questions and document considered/rejected alternatives and the proposed-agent comparison.
5. Remove the in-progress notice when complete, then submit this index once by the deadline.
