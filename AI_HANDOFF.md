# Start here: CoursePilot team handoff

The shared app supports Codex CLI and Claude Code for inference. Teammates can use either coding assistant to work on the repository. Read [the teammate guide](coursepilot/TEAMMATE_GUIDE.md) for dependencies, CLI sign-in, model/provider selection, and fork/pull-request workflow. Nothing registers real university courses.

Website layout: [one server, separate case/run pages](coursepilot/WORKSPACE.md). Home shows A/B/C; A remains a pending-work page. Each run has a separate URL and conversation. After the laptop restart, start the normal server on port 8765; the old migration bridge is no longer needed. Case B browser run `20261116T221256-8c5ff075` was finished and saved before the restart. Earlier runs open as read-only snapshots; use a new run for a new recording. No model calls are needed to inspect the hub, run history, or saved snapshots.

Runtime 2.2.1 fixes rejection of a valid StructuredOutput response after the CLI explicitly rejected an unavailable course-tool name. Native tools remain disabled. An unfinished human Case B run can recover its saved draft through `/api/recover` without another inference; `before-recovery/`, the original error events, and a continuation record preserve what happened. Finalized baseline evidence cannot be recovered or rewritten. Do not rerun the five baseline attempts to hide transport errors.

Chat display now supports formatted prose, grouped assistant updates, and plan cards. Course names replace internal KEEP_A/KEEP_B labels on screen. Case B shows a separate, state-verified completion card; this does not alter the model transcript or recorded evidence. No additional model trials were collected for this UI refinement.

## Current artifacts

| Item | Where to continue | Status |
| --- | --- | --- |
| Shared app | `coursepilot/engine.py`, `server.py`, `providers.py`, `static/` | Working; both providers passed full integration checks |
| Case C (Abhi) | [Case document](coursepilot/README.md), [results](coursepilot/RESULTS.md) | Five original Codex trials complete; independent teammate video pending |
| Case B (proposed owner Hudson) | [Final runnable document](coursepilot/CASE_B.md), `coursepilot/cases/hudson_b.json`, `coursepilot/fixtures/hudson_b.json` | Five attempts retained: four correct completions and one native-tool rejection; original label-sensitive scores and audited metrics are separately reported; creator contribution and recording unconfirmed |
| Case A (Aditya proposed) | `coursepilot/cases/planning_template.json` and [authoring guide](coursepilot/TEAMMATE_GUIDE.md) | Still a template; do not mark finished |
| Final index | [SUBMISSION.md](SUBMISSION.md) | In progress; last teammate to finish submits |

## Hudson's AI: do this

1. Read `coursepilot/CASE_B.md` and the case JSON. The case is already implemented; do not re-scaffold or overwrite it with the correction template.
2. Check whether `coursepilot/case-b-runs/RESULTS.md` and `case-b-summary.json` exist and whether all five actual trial folders are present. Completed evidence should be reviewed, not regenerated. Ask before consuming more inference quota.
   All five attempts have now been collected. Do not run another five. Read the post-collection `Plan A`/`A` scoring-label audit; never present audited values as the unmodified contents of the original reward.json files. Runtime 2.1.1 fixes the label lookup for new sessions.
3. Help Hudson review the scenario/results and record his actual contribution. The creator field remains unconfirmed; do not automatically rename it to Hudson or claim independent creation based only on assigned ownership. Any later design change requires a new version/output directory, not relabeling these trials.
4. Hand the final case document and commit to Abhi for the reproduction. Hudson's separate video assignment is reproducing Aditya's Case A once available.

## Abhi or the recording helper: do this

1. Use the setup and two-step human protocol in `coursepilot/CASE_B.md`, with a fresh checkout and a separate browser-run directory.
2. The scheduled correction must use the second task-guide button, which updates the authoritative rule data along with the visible message. Wait for the first response before sending it.
3. Record the real setup/run and inspect the saved trajectory/reward/config. No required teammate recording exists until an actual recording is made and its accessible URL is added to the index. Do not label automation as Abhi's human reproduction.
   [RECORD_CASE_B.md](coursepilot/RECORD_CASE_B.md) gives a short sequence and spoken introduction.
4. Confirm the actual creator and independent tester rather than assuming the proposed rotation establishes independence.

## Aditya's AI: do this

Use the planning template to implement Case A, with a required-course versus preference conflict, an independently verified valid schedule, a complete both-mode protocol, and the shared metric/questions. Read the existing case documents as examples; do not submit an unchanged template. Collect five baseline trials only when the case is frozen and inference use is authorized. Aditya's proposed video assignment is reproducing Case C using `coursepilot/REPRODUCTION.md`.

## Commands that do not invoke a model

```powershell
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot.verify --output coursepilot/case-b-runs
python -m coursepilot.summarize_case_b --output coursepilot/case-b-runs
```

The first command checks software with scripted adapters. The next two inspect actual saved evidence; they need run folders to exist. They do not collect subjective responses or create a video. Core model/runtime settings are recorded per run; the two providers are not interchangeable experimental conditions merely because they share the same course tools.
