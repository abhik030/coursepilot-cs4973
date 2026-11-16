# Add your own case to the shared application

Aditya and Hudson each need to curate and own their own case, not submit the untouched templates. The shared browser/server, model transport, logging, and course tools are ready to reuse.

## Get started

First install Git, Python 3.10 or newer, and the Codex CLI using [the official setup instructions](https://learn.chatgpt.com/docs/cli). Sign in with your own account. The desktop app by itself is not the command-line dependency used by this project. The selected model defaults to `gpt-6.1-sol`; confirm your account can run it before collecting the final batch. No Banner login, Docker, database, or third-party Python packages are needed.

Run these commands in a terminal, from a folder where you keep projects:

```powershell
git clone https://github.com/abhik030/coursepilot-cs4973.git
cd coursepilot-cs4973
python --version
codex --version
codex login status
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot --output coursepilot/browser-runs
```

If you already cloned it, run `git pull --ff-only` first. On systems where Python is named `python3` or `py`, use that command in place of `python` consistently. Keep the server terminal open and visit **http://127.0.0.1:8765 on your own computer**. Select human mode and baseline, begin a fresh session, and follow Case C's task-guide buttons to understand the workflow. Stop the server with Ctrl+C when finished. If the port is occupied, add `--port 8766` and visit that port instead.

Successful setup means 16 integrity tests pass and the assistant answers the first comparison request in the browser. Tests do not need model access; an actual agent answer does. If setup fails, send Abhi the command and error text, your OS, and Python/CLI versions. Do not send sign-in credentials. Avoid editing the recorded evidence folders.

## Your assignment

| Person | Create | Starting template | Final case filename |
| --- | --- | --- | --- |
| Aditya | Case A: preserve required courses while optimizing preferences | `planning_template.json` | `coursepilot/cases/aditya_a.json` |
| Hudson | Case B: incorporate a correction without forgetting earlier hard rules | `correction_template.json` | `coursepilot/cases/hudson_b.json` |

For A, include a tempting preference-satisfying option that misses a hard requirement and at least one valid solution. For B, define a restriction introduced after the first draft, preserve the original rules, and independently verify a feasible revised schedule. These are the proposed assignments; confirm ownership with Abhi. You reuse the shared app and curate your own task, fixture, protocol, and outcomes.

Create a named branch before editing, for example `git switch -c case-a-aditya` or `git switch -c case-b-hudson`. Copy the chosen template and, if changing academic data, copy the fixture to your own filename. From the repository root, Aditya can start with:

```powershell
Copy-Item coursepilot/cases/planning_template.json coursepilot/cases/aditya_a.json
Copy-Item coursepilot/fixtures/approval_v2.json coursepilot/fixtures/aditya_a.json
```

Hudson substitutes the correction template and `hudson_b.json` for both destination filenames. In your case JSON, set `fixture` to `../fixtures/aditya_a.json` or `../fixtures/hudson_b.json`, replace the template ID/name/status, then curate and check the actual scenario. A renamed template alone is not a finished case.

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

## Return your work

Send Abhi a link containing your case JSON, fixture, case document, five complete baseline output folders, and a short result table with actual breakdown counts. Do not overwrite Abhi's `coursepilot/runs/` or change your fixture midway through the final batch. Share a case draft and at least one valid solution early so setup problems can be resolved before the five-run collection.

Public read access does not grant push access. If you are not a repository collaborator, click **Fork** on GitHub, then push your named branch to your own fork and open a pull request back to `abhik030/coursepilot-cs4973`. If you cloned the shared repository above, keep `origin` and add your fork as a separate remote, replacing `YOUR_USERNAME`:

```powershell
git remote add mine https://github.com/YOUR_USERNAME/coursepilot-cs4973.git
```

Stage only your intended case/document/evidence files, commit them, and push with `git push -u mine YOUR_BRANCH_NAME`, replacing the branch placeholder. Then use GitHub's pull-request button. If pushing is blocked, send the fork/branch link so Abhi can retrieve your work; do not wait silently.

After the cases are ready, the proposed video rotation is Aditya records Case C, Hudson records Case A, and Abhi records Case B. Confirm that rotation. Follow [the recording guide](REPRODUCTION.md) and add the actual creator/tester names and accessible video URLs to [the team index](../SUBMISSION.md). Each case requires five baseline runs, its written handoff, and a reproduction video by a different teammate. No human-study responses are due now.
