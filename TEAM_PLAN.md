# CoursePilot team work

Assignment deadline: Monday, November 16, 2026, at the listed 11:59 p.m. deadline. One team submission. Each teammate creates one case, runs five baseline LLM simulated-user trials, and has a different teammate reproduce the case on video. Human study data are not required now.

Repository: https://github.com/abhik030/coursepilot-cs4973

Editable handoff: https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit

## Proposed owners

| Person | Own case | Reproduction video |
| --- | --- | --- |
| Abhi | C: comparison versus approval; shared runner/logging | Record Hudson's B |
| Aditya | A: required courses versus preferences | Record Abhi's C |
| Hudson | B: correction during planning | Record Aditya's A |

These assignments still need teammate confirmation. The repository's completed implementation currently covers Case C only.

## What Aditya and Hudson can do now

1. Clone the repository and run the integrity tests and a human-mode Case C session using the README.
2. Write your own case's task, fixed starting state, exact initial prompt where possible, simulated-user persona/response policy, human instructions, and stopping condition. Independently verify at least one valid solution.
3. Use the same core metric names and participant questions in `evaluation/SHARED_METRICS.md`. Confirm their definitions together before collecting your assignment batch.
4. Add your case's configuration and scorer to the shared runner, or reuse its provider/logging components in your own runnable case. Case C's final comparison schema and scorer are specific to its task; copying its JSON alone does not implement A or B.
5. Run five real baseline trials after freezing your case, retain raw evidence, and write setup/results/rejected-case notes. Optional extra metrics may differ by case.
6. Exchange documentation with your assigned recorder. Fix undocumented setup steps, record the reproduction video, and add its accessible URL to the team submission index.

## Abhi's remaining human work

- Ask Aditya to reproduce and record Case C using `evaluation/CASE_C.md` and the README, without undocumented coaching.
- Reproduce and record Hudson's Case B once it is ready.
- Confirm the shared metric definitions, case ownership, and final submitter with the team.
- Add all three finished cases and videos to the final index and check grader access before submission.

The current baseline results do not demonstrate an approval failure. Preserve that result honestly; no minimum breakdown rate is required. A longer interaction or different event sequence would be a separately versioned case requiring its own trials.
