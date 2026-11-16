# Add your own case to the shared application

Aditya and Hudson each need to curate and own their own case, not submit the untouched templates. The shared browser/server, model transport, logging, and course tools are ready to reuse.

## Get started

```powershell
git clone https://github.com/abhik030/coursepilot-cs4973.git
cd coursepilot-cs4973
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot --output coursepilot/browser-runs
```

If you already cloned it, run `git pull` first. Confirm your own `codex login status`. Work on a named branch and avoid editing the recorded evidence folders.

## Define your case

Copy `cases/planning_template.json` or `cases/correction_template.json` to a new file. Set your creator name, unique case ID, title, and fixture path. These are starting structures, not finished student-created test cases.

Each stage has a human-readable title, student message, `intent`, and `target`. The browser task guide and simulated student use those same stages. `chat` conveys information or questions. `save` and `register` issue real user-channel permission for the named plan. Do not give the baseline deliberately irresponsible instructions.

For a correction stage, `profile_update` records the scenario's authoritative change to `work`, credit limits, or soft preferences when the student sends that task step. Include the change in the visible message. Keep prior hard rules unless the student explicitly replaces them. Both modes update the same truth; neither condition gets different academic information. Document that participants use the task-guide step to issue a scenario correction.

Copy and edit the fixture if your case needs different courses, blocked times, grades, requirements, or seats. Independently verify a valid solution. Section keys are synthetic five-digit CRNs; the term is stored separately. Prerequisite groups are AND across groups, OR within a group, with minimum letter grades. Linked section CRNs use `requires_sections`. `seats_available`, `waitlist_capacity`, and `waitlist_actual` describe different resources.

## Choose success criteria

For a planning/correction task:

```json
"success": {"final_draft": "A"}
```

This scores the final draft against the active rules, without demanding enrollment changes. You may add `expected_sections` if your case intentionally requires one exact valid set; otherwise accept all rule-satisfying final drafts. Required courses, credit rules, protected sections, work conflicts, and corequisites come from the fixture. If your task needs another success rule or breakdown flag, extend the scorer and add a meaningful integrity check before collecting trials.

For the approval case, the configuration instead identifies the reference final enrollment, saved plan, and required comparison after saving. The general stage controller does not automatically assume every case is a registration task.

## Run your case in both modes

```powershell
python -m coursepilot --case coursepilot/cases/YOUR_CASE.json --output coursepilot/your-interface-checks
python -m coursepilot.batch --case coursepilot/cases/YOUR_CASE.json --runs 5 --output coursepilot/your-recorded-runs
python -m coursepilot.verify --output coursepilot/your-recorded-runs
```

Use the same configuration for human and simulated modes. Freeze it before the final five-run batch, retain successes/failures, and preserve any development trials separately. The templates have been checked with deterministic adapter tests; their presence is not evidence that your own case has been run or is final.

Add your short case document explaining setup, breakdown, protocols, valid outcomes, actual metrics, rejected candidates, mocked/external systems, and the proposed-agent comparison path. Reuse the shared subjective questions. Exchange cases for the reproduction videos, then add accessible repository/document/video links and creator/tester names to the team index.
