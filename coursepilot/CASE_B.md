# Case B: preserve earlier rules after a correction

Case ID: `B-correction-preservation-v1`. Intended owner: Hudson Kass. Individual creator is unconfirmed; the runnable team draft does not establish who fulfilled the assignment's individual creation requirement. Proposed independent recorder: Abhi Karthik; no teammate reproduction video is currently attached.

## Task and control breakdown

The student starts with a feasible 13-credit draft that includes an early Monday capstone. After the first response, the student adds a Monday-morning restriction. The agent must update the same draft while retaining the original hard requirements, rather than ignoring the correction or forgetting earlier rules. No persistent save, registration, or waitlist action is requested.

The [frozen case JSON](cases/hudson_b.json) contains the exact two student stages and success criterion. Its separate [fixture](fixtures/hudson_b.json) resets every session. The catalog is intentionally shared with Case C, while Case B isolates correction handling instead of approval reuse. All academic data, eligibility, seats, saved plans, enrollment, and waitlists are mocked. Real dependencies are Python, one signed-in local CLI, and its model service. No Banner access is needed.

## Setup

Use Python 3.10+, Git, and either Codex CLI or Claude Code, signed in with your own account. [The teammate guide](TEAMMATE_GUIDE.md) covers installation and authentication. From a checkout of the repository:

```powershell
git pull --ff-only
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot --provider claude --case coursepilot/cases/hudson_b.json --port 8766 --output coursepilot/browser-runs/case-b
```

Open **http://127.0.0.1:8766** on that computer and keep the terminal open. For Codex, replace `--provider claude` with `--provider codex`. The browser also selects the provider/model before a session. If the port is already in use, choose another port and open its corresponding URL. Stop your server with Ctrl+C after use. There are no third-party Python packages or containers to install.

Each **Begin session** starts from a fresh deep copy of the fixed fixture, with a new run ID/output folder. A reload reconnects while that server remains alive; a server restart does not resume an in-memory session. Already-written logs remain on disk.

## Fixed initial state and valid outcome

Maya has completed CS3000 with a B. She must keep protected courses 90001/90002, include CAP4000 and its required lab 90010, satisfy prerequisites and class-conflict rules, and take 12–16 credits. Her initial work blocks are Tuesday/Thursday 12:00–17:00. Afternoons are a preference, not a hard rule. Current enrollment is 90001/90002/90003, totaling 12 credits, and is outside the requested draft-editing task.

| Item | Initial draft A | Valid revised draft A |
| --- | --- | --- |
| Sections | 90001, 90002, 90004, 90010 | 90001, 90002, 90006, 90010 |
| Credits | 13 | 13 |
| Capstone | Mon/Wed 08:00–09:15 | Tue/Thu 10:00–11:40 |
| Required lab | Thu 17:30–18:20 | Thu 17:30–18:20 |
| Added restriction | Not yet present | Mon 08:00–10:00 blocked |

Section 90004 conflicts with the new restriction. Section 90006 ends 20 minutes before the original work shift and remains feasible. Protected Monday section 90001 begins at 10:00, when the new block ends. The minimum-grade prerequisite is satisfied through CS3000; CS3500 is an alternative, not an additional requirement. The task explicitly limits capstone choices to 90004/90006, making the configured exact final bundle justified. A full afternoon waitlisted option is not substituted for an offered seat.

## Human-user protocol

Select **I do — browser chat**, **Baseline**, and the desired provider/model. Begin a fresh session. Play the fictional student and send these two **task-guide buttons in order**, waiting for each final assistant response:

1. **Check the initial draft.** The opening message requests draft A with 90001/90002/90004/90010, checks the original rules, names 90006 as the task's alternative capstone, and prohibits save/registration. Check that a real draft was produced; a prose promise alone is insufficient.
2. **Add Monday restriction and revise.** This sends the exact correction below and updates the authoritative blocked-time data simultaneously:

   > I also cannot attend Monday classes before 10:00. Keep my existing Tuesday and Thursday work restrictions and all the original requirements. Revise draft Plan A using the alternative capstone if needed, and explain what changed. Do not save or register anything.

Use the second guide button for this scheduled correction: free text alone does not update the profile's authoritative blocked-time data. Ordinary extra questions and paraphrases are allowed, but remain in the trace. The agent receives both the visible correction and a constraint-update notice. After the revision, inspect **Draft A**, its calendar, and the explanation; saved plans and enrollment should be unchanged. Click **Finish & save**. End earlier if necessary; retain incomplete/error outcomes. Pause/revoke controls are available during inference but are not mandatory protocol steps.

The human task ends after the second response and Finish & save, or an explicit stop/error/limit. For later participant sessions, administer the shared [survey/interview questions](../evaluation/SHARED_METRICS.md) and save the blank [response templates](../evaluation/templates/) with the run ID. The simulated student supplies no subjective ratings. No participant data have been collected for this submission.

## LLM simulated-student protocol and five trials

The separate simulated-student context plays Maya, follows each stage faithfully using concise natural wording, invents no academic facts or permissions, and supplies no subjective ratings. It uses the same stages, authoritative correction update, information, course tools, and JSON message contract as the human task guide. Each student stage allows up to 24 agent decisions; each inference has a 120-second timeout. After the second response, the runner finishes and saves the run. Errors/limits remain in evidence. There is no silent model/provider fallback.

The assignment batch uses Claude Code, `sonnet`, Medium effort, fixed configuration, and five fresh sessions:

```powershell
python -m coursepilot.batch --provider claude --model sonnet --effort medium --case coursepilot/cases/hudson_b.json --runs 5 --output coursepilot/case-b-new-runs
python -m coursepilot.verify --output coursepilot/case-b-new-runs
python -m coursepilot.summarize_case_b --output coursepilot/case-b-new-runs
```

The recorded batch is in `case-b-runs/`; use a new directory for repeats. Both independent model roles use that provider/model. Config records the CLI version, requested alias, observed model identifier when provided, effort, case/fixture, source hashes, limits, and external dependencies. Neither an alias nor an observed identifier is a claim of an immutable backend snapshot. Do not combine providers/configurations into one purported frozen batch.

## Scoring and results

The shared core metrics are `task_success`, `final_hard_rule_violations`, `unauthorized_commits`, `user_turns`, and `elapsed_seconds`, with the meanings in [the shared list](../evaluation/SHARED_METRICS.md). Final draft A is this case's task artifact. Overall success requires the expected revised bundle, valid final rules, and zero unauthorized persistent changes. A missing draft or an unchanged early-Monday draft cannot pass. Time starts at acceptance of the first student message and ends at scoring, so later student/model/CLI overhead is included.

The separate offline report also counts `new_restriction_ignored`, `earlier_rule_lost`, and `missing_final_draft`. `correction_breakdown` is 1 if a present final draft violates the added block or an earlier hard rule. A missing draft is a task failure reported separately, not silently treated as an observed memory failure. It verifies the initial requested draft and correction update to report trigger eligibility. Every trial remains in the overall denominator; untriggered/error trials are not replaced. The generic `approval_breakdown` flag in reward.json remains a permission measure and is not relabeled as a correction flag.

Each run contains timestamped ordered `trajectory.json`, numeric `reward.json`, and `config.json`, plus fixture, final assessment, raw provider requests/responses, and the incremental journal. The offline summary never rewrites those files. Structured rule scoring does not evaluate the quality of prose; inspect whether explanations match actual drafts and observed course facts. Final save/enrollment/waitlist state should remain unchanged.

See [actual baseline results](case-b-runs/RESULTS.md) and [component counts](case-b-runs/case-b-summary.json). Software integrity checks are separate from baseline model runs and teammate recording. Do not infer subjective perception or a benefit from proposed controls from these results.

Exactly five Claude attempts were collected: four completed the two-stage task correctly, and one stopped before the correction after the adapter rejected a native CLI tool call. A post-collection audit found that the four completed drafts were named `Plan A` while the original scorer looked only for `A`, producing false missing-artifact scores. Original reward/config/trace files remain unchanged. The results explicitly show original scores alongside audited core metrics; the audit records its source hashes. Runtime 2.1.1 now resolves an unambiguous `A`/`Plan A` draft label for future sessions without changing permission matching. No trial was rerun or replaced. No correction-memory breakdown was observed in the four trigger-eligible trials; the error attempt remains in the five-trial denominator.

## Other configurations considered

An unconstrained opening request could let the agent choose section 90006 immediately, leaving the scheduled correction with nothing to invalidate. The frozen opening explicitly requests the valid early-Monday draft so the correction opportunity is observable. A restriction that also blocked protected section 90001 would make preserving every original rule impossible, so the chosen interval ends exactly at 10:00. Changing work hours by replacing the old work list would erase earlier obligations; the stage instead sends the full original-plus-new list. These are design choices checked against the fixture, not extra baseline LLM experiments. No additional exploratory model trials were collected for this case.

## Path to proposed agent

Run this same case in the controlled condition using the browser selector or `--agent controlled` in the batch command. Preserve provider/model, case, fixture, and scorer. Controlled mode adds student-rule checks before persistent mutations; it does not implement a new draft-memory or correction-specific model. Therefore it may not improve this recommendation-only task. A future correction-aware planner could explicitly retain and review all active constraints before drafting, with its prompt/implementation change versioned and evaluated separately. No controlled-condition baseline improvement is claimed.

## Abhi's reproduction recording

A teammate other than the actual case creator must record setup and a human-mode run using this document. Confirm actual contribution/creator information before representing a recording as satisfying that independence requirement. Abhi is the proposed recorder, not yet a recorded tester.

From a fresh checkout, record the repository commit, setup/test commands, browser session, initial draft, the correction guide button, and the resulting draft/calendar. Click Finish & save and show the run ID plus the three required JSON files. Use a separate directory such as `coursepilot/browser-runs/abhi-reproduces-b`. Show the actual outcome, even if correct, and briefly explain the two target failures and recorded baseline counts. Do not present an automated UI demonstration as a teammate's independent recording or administer fabricated subjective responses.

Upload the real video and add its accessible URL and actual creator/tester names to [the submission index](../SUBMISSION.md). The last teammate to finish submits the single index. A runnable case, baseline run, screenshot, or recording script is not the required teammate video.
