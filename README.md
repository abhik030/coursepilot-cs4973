# CoursePilot

CoursePilot studies student control over course planning and registration. The browser application now supports a multi-stage task: **compare A/B, save A, explore B without changing it, and register the original A only after the student's instruction**. All academic records and registration actions are fictional.

Team: Abhi Karthik, Aditya Vij, Hudson Kass. Cases A and B remain the responsibility of their proposed owners; they are not implemented here yet.

**[Team submission index](SUBMISSION.md)** — Case C evidence is ready; Cases A/B and teammate videos are still pending.

- [Team handoff and responsibilities](TEAM_PLAN.md)
- [Shared editable team document](https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit)
- [Current browser Case C setup, protocols, scoring, and limitations](coursepilot/README.md)
- [Current five-run baseline results](coursepilot/RESULTS.md)
- [Historical v1 terminal case](evaluation/CASE_C.md) and [v1 results](evaluation/RESULTS.md)
- [Shared proposed metrics and participant questions](evaluation/SHARED_METRICS.md)
- [Observed Banner workflows and inspection limits](evaluation/BANNER_OBSERVATIONS.md)
- [Browser case design and implementation boundaries](evaluation/V2_DESIGN.md)

## Start the browser application

```powershell
git clone https://github.com/abhik030/coursepilot-cs4973.git
cd coursepilot-cs4973
codex login status
python -m coursepilot --output coursepilot/browser-runs
```

Open **http://127.0.0.1:8765** in your browser. Choose human or LLM simulated-student mode, and baseline or approval-enforced condition. In human mode, click the task-guide steps or type your own messages. The catalog, calendar, drafts, saved plans, pending registration, enrollment, and waitlists show distinct states. You can send a correction, pause, or revoke unused approval while inference is running. Use **Finish & save** at the end; stopping in-flight inference may take a moment, but stale actions are discarded.

This is a local web application: the browser talks to your Python server, which uses your signed-in CLI. A GitHub link shares the code and evidence; it does not host the model backend. Each teammate runs the same command on their own computer. No new Python dependencies are needed. The server binds only to loopback.

- [V2 setup and reproducibility protocol](coursepilot/README.md)
- [Case configuration](coursepilot/cases/approval_v2.json)
- [Teammate case authoring guide](coursepilot/TEAMMATE_GUIDE.md)

For the shared app checks and a new baseline batch:

```powershell
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot.batch --runs 5 --output coursepilot/new-runs
python -m coursepilot.verify --output coursepilot/new-runs
```

Use a new directory for your own experiments. The recorded assignment batch is under `coursepilot/runs/`; v1 evidence remains under `evaluation/runs/`.

## Original v1 terminal runner

Requirements: Python 3.10+, Git, and an installed Codex CLI with a signed-in account that can access the selected model. No third-party Python packages, Docker, API key file, university account, or Banner connection are needed by this implementation. Model inference is a real external dependency.

```powershell
git clone https://github.com/abhik030/coursepilot-cs4973.git
cd coursepilot-cs4973
python --version
codex --version
codex login status
python -m unittest discover -s evaluation/tests -v
```

If the CLI is not signed in, run `codex login` using your own account. The recorded configuration used `codex-cli 0.169.0-alpha.11.1`, model `gpt-6.1-sol`, Medium effort. A different model/version must be recorded as a different configuration. Setup has been checked on Windows with Python 3.13; the code uses the Python standard library.

### Run one LLM simulated-user trial

```powershell
python -m evaluation run --mode simulated --agent baseline
```

The same selected model runs two independent roles: the course agent and the simulated student. Each inference is an ephemeral CLI call with the relevant conversation explicitly supplied. Native tool activity is rejected; course actions are executed only by the Python runner. This is a custom conversational baseline, not a reproduction of Codex's complete browser product.

### Run human mode

```powershell
python -m evaluation run --mode human --agent baseline
```

Read the instructions and press Enter to send the fixed initial request. Respond if the agent asks a question. Type `/quit` to end early. Both modes use the same case, tools, agent prompt, decision schema, and message interface. Human mode replaces the simulated-student input adapter.

### Run five fresh baseline trials and summarize

```powershell
python -m evaluation run --mode simulated --agent baseline --runs 5 --output evaluation/new-runs
python -m evaluation summarize --output evaluation/new-runs
```

The recorded assignment batch is in `evaluation/runs/`. Use a different output directory for your own trials so the assignment batch stays clearly identifiable. Every new run starts from a fresh fixture and gets a unique folder. No separate reset command is required.

### Improved-agent comparison

```powershell
python -m evaluation run --mode simulated --agent controlled --output evaluation/controlled-runs
```

This selects the existing simulator's additional student-rule and exact-approval guards. It provides a concrete comparison path, not the complete proposed CoursePilot review interface. The underlying model, task, course tools, and institutional safe transaction remain shared. No controlled-condition LLM results are claimed in the recorded baseline report.

## What each run saves

```text
run-id/
  trajectory.json        # timestamped messages, tool calls/results, state events
  trajectory.jsonl       # incremental journal
  reward.json            # objective metrics, named numbers only
  config.json            # mode, agent, model alias/version information, settings, hashes
  fixture.json           # exact reset state
  assessment.json        # independent expected values and scoring details
  provider/              # exact prompts, schemas, raw CLI JSONL, stderr, responses
```

Later human sessions should also save survey responses and interview notes in that run's folder. No human responses have been collected here.

## Repository layout

`sandbox/` holds the original simulator and 15 scripted functional checks. `evaluation/` holds the new runner, case, transport, protocols, integrity tests, and real LLM outputs. `evaluation/pilot-runs/` preserves setup trials, including an infrastructure error. `evaluation/interface-checks/` holds a piped-input human-adapter software check. Neither directory is counted in the five-run baseline batch.

All academic records, registration changes, requirements, and seat counts are fictional. The simulator makes no university requests and cannot register a real student.
