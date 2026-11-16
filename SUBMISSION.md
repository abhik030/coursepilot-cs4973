# CoursePilot — curated test cases

CS4973 · Abhi Karthik, Aditya Vij, Hudson Kass

Submission agreement: **the last teammate to finish submits** this single team index.

**Team submission in progress.** Case C's implementation, document, and five baseline runs are available. Case B is a runnable team draft with trials being collected; its individual creator contribution remains unconfirmed. Case A and all three teammate reproduction videos are pending. This page is the single submission entry point once those items are added; templates are not completed cases.

## Case index

| Case and target breakdown | Creator | Setup and protocol | Five baseline runs and results | Independent tester and video |
| --- | --- | --- | --- | --- |
| A: a required course is lost while optimizing a preference | Aditya Vij, proposed owner | Pending; [authoring guide](coursepilot/TEAMMATE_GUIDE.md) is available | Pending | Hudson Kass proposed; actual tester and video pending |
| B: a correction is ignored or an earlier hard rule is lost | Individual creator unconfirmed; Hudson Kass proposed owner | [Runnable case document](coursepilot/CASE_B.md), [case JSON](coursepilot/cases/hudson_b.json) | Five Claude attempts being collected | Abhi Karthik proposed; actual tester and video pending |
| C v2: saving one plan is treated as permission for a different plan or registration action | Abhi Karthik | [Case document](coursepilot/README.md), [frozen stages](coursepilot/cases/approval_v2.json), [fixture](coursepilot/fixtures/approval_v2.json) | [Results](coursepilot/RESULTS.md), [five output folders](coursepilot/runs/), [verification](coursepilot/runs/verification.json) | Aditya Vij proposed; actual tester and video pending |

The shared [public repository](https://github.com/abhik030/coursepilot-cs4973) contains the environment and evidence. [Setup commands](README.md#start-the-browser-application) launch a local Python backend using the tester's own signed-in Codex CLI or Claude Code CLI. The browser selects the provider/model; both roles share that selection. The original five baseline trials used Codex. The repository does not host a remote model backend. Each fresh session resets the fictional academic state.

## Shared measurement and human-testing materials

- [Core objective and subjective metrics, survey, and interview questions](evaluation/SHARED_METRICS.md).
- Blank [survey response template](evaluation/templates/survey.json) and [interview notes](evaluation/templates/interview-notes.md). No subjective responses are required for this submission or have been collected.
- [Reproduction instructions](coursepilot/REPRODUCTION.md), including the independent Case C recording and the handoff Abhi needs from Hudson.

Every run includes ordered timestamped `trajectory.json`, numeric `reward.json`, and model/mode/settings `config.json`. Academic records and registration are mocked; model inference through the CLI is real. Case-specific documents state their reset, stopping rules, success criteria, and any additional external dependencies.

## Case C findings

The baseline completed all five multi-stage trials successfully, with five student turns per trial, zero unauthorized commits, and zero final hard-rule errors. No approval breakdown was observed. The same task can be run with `controlled` permission enforcement, but no controlled-condition LLM comparison is claimed. Software checks and the development pilot are separate from the five baseline trials and required reproduction video. Historical [v1 evidence](evaluation/RESULTS.md) is retained separately.

## Items required before submission

1. Confirm each actual creator and independent tester. Proposed case assignments above are not confirmations. Record who actually finishes last and submits, following the team agreement.
2. Add A/B's finished documents, fixed fixtures, both-mode protocols, curated/rejected-case notes, and five baseline output folders per case. Report actual breakdown counts, including zero.
3. Add all three accessible reproduction videos, with actual recorder names. A case's recorder must be a teammate other than its creator and must use the written instructions.
4. Confirm that all three cases use the shared core metrics and participant questions. Preserve each case's actual model/settings and any extra metrics.
5. Check the repository and every video link without an owner login. Keep the required material accessible to the grader; the editable coordination document is optional supplementary material.
6. Remove the in-progress notice only when the missing items above are present, then submit this page's URL or an equivalent single index. Submit once for the team by the assignment deadline.
