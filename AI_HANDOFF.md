# Coding-assistant handoff

Reuse this checkout. Read the relevant case document and [teammate guide](coursepilot/TEAMMATE_GUIDE.md).

| Case | Status | Next work |
| --- | --- | --- |
| A: Aditya proposed | Template only | Implement, document, check, collect five trials |
| B: Hudson proposed; creator unconfirmed | [Implemented](coursepilot/CASE_B.md); [five attempts](coursepilot/case-b-runs/RESULTS.md) | Review contribution/ownership; Abhi's video |
| C: Abhi | [Implemented](coursepilot/README.md); [five successful trials](coursepilot/RESULTS.md) | Aditya's video |

All three videos are pending. The last teammate to finish submits the [Google Doc's Submission tab](https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit?tab=t.uig7mgyr21pt); [SUBMISSION.md](SUBMISSION.md) is a backup. Anyone with the Doc link can view; Aditya and Hudson can edit. Check video access after upload. Older planning notes are kept in a separate tab.

## Runtime

```powershell
python -m coursepilot --provider claude --output coursepilot/browser-runs
```

Open http://127.0.0.1:8765/. One server hosts all cases/runs. Both Codex and Claude are supported. Old runs become read-only after a restart; the old two-server bridge is no longer needed.

Browser B run `20261116T221256-8c5ff075` is saved. Start a new run for recording. Chat formatting/course names affect display only. The B completion card comes from checked app state, separate from model text.

Runtime 2.2.1 accepts a valid final Claude response after an explicitly rejected unavailable course-tool call. Python alone executes course actions. **Recover saved revision** can recover older unfinished human B runs from saved responses without another model call, retaining the error. It cannot rewrite finalized baseline trials.

## Preserve evidence

- B already has five Claude attempts: four correct completions and one tool-format error before the correction. Do not collect another five or replace the error.
- B's original scorer searched for `A`, but four drafts were called `Plan A`. Original scores remain; a separate report shows corrected scores.
- C's five Codex trials, earlier pilots, and terminal-only results stay separate.
- No new model calls without user authorization. The checks below make none.
- Preserve raw logs/configs. Before changing source files recorded in old runs, archive their original bytes; see [source snapshots](coursepilot/source-snapshots/README.md).
- Record actual contributions, videos, and survey responses only. Do not add tool-assistance credits.
- Stage intended changes only; untracked pitch files are separate work.

## Checks

```powershell
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot.verify --output coursepilot/case-b-runs
python -m coursepilot.verify --output coursepilot/runs
python -m coursepilot.summarize_case_b --output coursepilot/case-b-runs
```
