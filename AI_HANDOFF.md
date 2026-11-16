# Coding-assistant handoff

Reuse this checkout. Read the relevant case document and [teammate guide](coursepilot/TEAMMATE_GUIDE.md).

| Case | Status | Next work |
| --- | --- | --- |
| A: Aditya | Template only | Implement, document, check, collect five trials |
| B: Hudson's assigned case | [Implemented](coursepilot/CASE_B.md); [five completed runs / six attempts](coursepilot/CASE_B_RESULTS.md) | Abhi reviews/records B |
| C: Abhi | [Implemented](coursepilot/README.md); [five successful trials](coursepilot/RESULTS.md) | Aditya reviews/records C |

All three videos are pending. The last teammate to finish submits the [Google Doc's Submission tab](https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit?tab=t.uig7mgyr21pt); [SUBMISSION.md](SUBMISSION.md) is a backup. Anyone with the Doc link can view; Aditya and Hudson can edit. Check video access after upload. Older planning notes are kept in a separate tab.

## Runtime

```powershell
python -m coursepilot --provider claude --output coursepilot/browser-runs
```

Open http://127.0.0.1:8765/. One server hosts all cases/runs. Both Codex and Claude are supported. Old runs become read-only after a restart; the old two-server bridge is no longer needed.

Browser B run `20261116T221256-8c5ff075` is saved. Start a new run for recording. Chat formatting/course names affect display only. The B completion card comes from checked app state, separate from model text.

Runtime 2.2.1 accepts a valid final Claude response after an explicitly rejected unavailable course-tool call. Python alone executes course actions. **Recover saved revision** can recover older unfinished human B runs from saved responses without another model call, retaining the error. It cannot rewrite finalized baseline trials.

## Preserve evidence

- B has six retained Claude attempts: five completed tasks and one tool-format error before the correction. The original five stay in `case-b-runs/`; one added run is in `case-b-additional-run/`. See `CASE_B_RESULTS.md`. No more model trials are needed or authorized by this completion.
- B's original scorer searched for `A`, but four drafts were called `Plan A`. Original scores remain; the combined report shows corrected scores. The extra run uses fixed runtime 2.2.1; do not call all six one unchanged-runtime batch. Its prose misstated a lab end time; the report discloses that separately from draft correctness.
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
python -m coursepilot.verify --output coursepilot/case-b-additional-run
python -m scripts.report_case_b
```
