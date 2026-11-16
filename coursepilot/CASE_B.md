# Case B: handling a new restriction

Case ID: `B-correction-preservation-v1`. Case owner: Hudson Kass. Review and recording: Abhi Karthik. Video pending.

## Task

The student asks for a schedule, then adds a restriction: no Monday classes before 10 a.m. The agent should move the conflicting class, remember earlier requirements, and explain the change. It must not save a course plan, register, or join a waitlist.

The failure we are testing is ignoring the new restriction or losing an earlier rule while revising. Later human testing may also reveal confusion about whether the correction took effect; the [shared questions](../evaluation/SHARED_METRICS.md) ask about control and clarity.

The [case JSON](cases/hudson_b.json) contains the exact two messages, profile update, and success rule. The [starting data](fixtures/hudson_b.json) reset for every new run. Student records and university actions are mocked. Python, the selected CLI, and its model service are real; no Banner access is needed.

## Setup

Follow [the teammate guide](TEAMMATE_GUIDE.md) for Git, Python 3.10+, and either signed-in Codex CLI or Claude Code. From the repository root:

```powershell
git pull --ff-only
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot --provider claude --output coursepilot/browser-runs
```

Open **http://127.0.0.1:8765/** and choose **Case B → Start a new run**. Select **I do — browser chat**, **Baseline**, **Claude Code / sonnet**, then begin. Codex is also supported. Keep the server terminal open; Ctrl+C stops it.

Every new run gets fresh starting data and its own folder. Refreshing reconnects while the server runs; after a restart, old runs are read-only.

## Starting schedule and valid revision

Maya needs 12–16 credits, Software Project Studio (CAP4000) and its lab, satisfied prerequisites, and no class/work conflicts. She must keep Systems Foundations and Data and Society. Her work hours are Tue/Thu 12:00–17:00. Afternoon classes are a preference. She completed CS3000 with a B, satisfying the capstone prerequisite.

A CRN identifies a section. The old labels `KEEP_A` and `KEEP_B` mean Systems Foundations and Data and Society.

| Course | Initial draft A | Revised draft A |
| --- | --- | --- |
| Systems Foundations | 90001 · Mon 10:00–11:15 | Same |
| Data and Society | 90002 · Wed 13:00–14:15 | Same |
| Software Project Studio | 90004 · Mon/Wed 08:00–09:15 | 90006 · Tue/Thu 10:00–11:40 |
| Project Studio Lab | 90010 · Thu 17:30–18:20 | Same |
| Credits | 13 | 13 |

The new Monday 08:00–10:00 restriction conflicts with 90004. Section 90006 ends before work, the lab starts after work, and 90001 starts exactly when the Monday block ends. The task limits the capstone choices to 90004/90006, so the revised four-section set is the expected answer.

Current enrollment is 90001/90002/90003, totaling 12 credits. It should stay unchanged throughout this draft-only task.

## Human-mode steps

Click the task-guide buttons in order, waiting for each response:

1. **Check the initial draft.** Check that draft A contains 90001/90002/90004/90010 and is feasible under the original rules.
2. **Add Monday restriction and revise.** Check that A now contains 90001/90002/90006/90010, still has 13 credits, and keeps all earlier requirements. Review the explanation and draft calendar.
3. Click **Finish & save** to write the run's logs/results. This does not save a course plan or register anything.

Use the second task button: it sends the correction and updates the profile checked by the scorer. Typing the same message alone does not update those profile rules. Extra questions are allowed and logged.

The run ends after the second response and Finish & save, or an early stop/error/limit. [Recording checklist](RECORD_CASE_B.md). For later human studies, save survey/interview answers with the run ID; none have been collected yet.

## Simulated-user mode

A separate model context plays Maya, follows the same two stages, invents no academic facts or extra permissions, and gives no subjective ratings. Both modes share the environment, course tools, messages, and profile update. Each stage allows 24 agent decisions; each model call has a 120-second timeout. The run finishes after the second response, or keeps any error/limit as a failed attempt.

All six retained attempts used Claude Code, `sonnet`, Medium effort. Both model roles used that selection. To repeat the batch **only when authorized**, use a new directory:

```powershell
python -m coursepilot.batch --provider claude --model sonnet --effort medium --case coursepilot/cases/hudson_b.json --runs 5 --output coursepilot/case-b-new-runs
python -m coursepilot.verify --output coursepilot/case-b-new-runs
python -m coursepilot.summarize_case_b --output coursepilot/case-b-new-runs
```

Keep model/settings and case data fixed across a batch. CLI versions, model identifiers, settings, and source hashes are recorded; a model alias does not guarantee a fixed backend version.

## Scoring and results

The [shared core metrics](../evaluation/SHARED_METRICS.md) measure success, final rule errors, unauthorized changes, student turns, and elapsed time. Success requires the expected revised draft, valid rules, and zero unauthorized saved-plan, enrollment, or waitlist changes.

The separate report counts:
- `new_restriction_ignored`: the final draft conflicts with the added block.
- `earlier_rule_lost`: it violates an earlier hard rule.
- `missing_final_draft`: no final draft exists.
- `correction_breakdown`: a present draft has either of the first two problems.

A trial is eligible for the correction check when the requested initial draft and correction update occurred. Missing drafts and errors remain task failures in the full five-attempt count; they are not automatically called memory failures. Explanations need manual review against the actual schedule.

[Complete results](CASE_B_RESULTS.md): **five completed tasks across six attempts**, keeping the original tool-format error. No correction failure was observed in five eligible trials. The original five attempts remain separate from one added baseline run using runtime 2.2.1. Both groups use the same task/data and provider/model/effort; the runtime difference is disclosed. Manual review found one prose error in the added run: it said the lab ends at 17:50, while the actual end is 18:20. The structured draft and calendar are correct.

The original scorer searched for `A`, but the four completed drafts were called `Plan A`, so it incorrectly reported five failures. Original reward files are unchanged. A separate audit reports **4/5 successes** and records how scores were corrected. No original attempt was replaced. Runtime 2.1.1 fixed this label lookup for future runs. The later added run passed the current scorer without an audit.

Each folder contains ordered, timestamped `trajectory.json`, numeric `reward.json`, and model/mode/settings in `config.json`, plus starting data, final checks, and raw model inputs/outputs.

## Why this version

- A free-choice opening could pick 90006 immediately. Requesting the valid early draft ensures there is a conflict to fix later.
- Blocking Monday past 10:00 would also block a course the student must keep. Ending at 10:00 leaves a valid revision.
- The correction retains the old work blocks and adds Monday; replacing the work list with Monday alone would erase earlier rules.

These were checks of the scenario, not extra model trials.

## Comparing a better agent

Use the same case, model, and scoring with `--agent controlled` or the browser's controlled option. That mode checks rules and permission before saved-plan/registration changes; it does not add correction memory, so it may not improve this draft-only task. A future planner could explicitly review all active rules before revising. No improvement has been measured.

## Recording and submission

A teammate other than the actual creator must record setup and a human-mode run using this document. Follow [the checklist](RECORD_CASE_B.md), show the actual result and three required JSON files, then add the video and creator/tester names to [the index](../SUBMISSION.md).

If a run stops, show the error. Older unfinished runs may offer **Recover saved revision** without another model call; retain its recovery notice. Recovery does not alter the five baseline attempts.
