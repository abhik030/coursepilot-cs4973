# CoursePilot team work

Assignment deadline: Monday, November 16, 2026, at the listed 11:59 p.m. deadline. One team submission. Each teammate creates one case, runs five baseline LLM simulated-user trials, and has a different teammate reproduce the case on video. Human study data are not required now.

Repository: https://github.com/abhik030/coursepilot-cs4973

Editable handoff: https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit

Submission agreement: the last teammate to finish submits the single team index. [Case B handoff instructions](coursepilot/HUDSON_CASE_B.md) are available for Hudson and Abhi.

## Proposed owners

| Person | Own case | Reproduction video |
| --- | --- | --- |
| Abhi | C: comparison versus approval; shared runner/logging | Record Hudson's B |
| Aditya | A: required courses versus preferences | Record Abhi's C |
| Hudson | B: correction during planning | Record Aditya's A |

These assignments still need teammate confirmation. Case C v2 and the reusable browser/server are implemented, with five completed real baseline trials. Case B is a runnable team draft with five retained Claude attempts: four semantically correct completions and one native-tool rejection. Its report separates original literal-label scores from audited metrics. Actual creator contribution remains unconfirmed. Case A is still a template. No teammate video is claimed as complete.

## What Aditya and Hudson can do now

1. Clone the repository and run the integrity tests and a human-mode Case C session using the README.
2. Write your own case's task, fixed starting state, exact initial prompt where possible, simulated-user persona/response policy, human instructions, and stopping condition. Independently verify at least one valid solution.
3. Use the same core metric names and participant questions in `evaluation/SHARED_METRICS.md`. Confirm their definitions together before collecting your assignment batch.
4. Follow [the case authoring guide](coursepilot/TEAMMATE_GUIDE.md). Copy the planning or correction template, curate your own fixture and stage protocol, and configure the success criteria. Both templates run through the shared browser and batch runner; they are not completed teammate cases. Add scorer logic only if your task needs an unsupported outcome.
5. Run five real baseline trials after freezing your case, retain raw evidence, and write setup/results/rejected-case notes. Optional extra metrics may differ by case.
6. Exchange documentation with your assigned recorder. Fix undocumented setup steps, record the reproduction video, and add its accessible URL to the team submission index.

## Abhi's remaining human work

Case C's written handoff is complete, including setup, both modes, target breakdown, rejected alternatives, actual baseline results, shared participant probes, and the proposed-agent comparison path. The [submission index](SUBMISSION.md) and [reproduction guide](coursepilot/REPRODUCTION.md) are prepared. On November 16, Abhi reported that Aditya and Hudson had not started their cases; neither their work nor the required videos is claimed as complete.

- Ask Aditya to reproduce and record browser Case C using `coursepilot/README.md`, without undocumented coaching. The five baseline trials and results are in `coursepilot/runs/` and `coursepilot/RESULTS.md`.
- Reproduce and record Hudson's Case B once it is ready.
- Confirm the shared metric definitions and case ownership; the last teammate to finish submits.
- Add all three finished cases and videos to the final index and check grader access before submission.

The current baseline results do not demonstrate an approval failure. Preserve that result honestly; no minimum breakdown rate is required. A longer interaction or different event sequence would be a separately versioned case requiring its own trials.
