# CoursePilot

A local course-planning app for our CS4973 test cases. Students chat with an agent, compare schedules, and control when plans are saved or courses are registered. All student records and registration actions are fictional.

Team: Abhi Karthik, Aditya Vij, Hudson Kass.

## Start here

- [Team tasks](TEAM_PLAN.md)
- [Setup and teammate guide](coursepilot/TEAMMATE_GUIDE.md)
- [Case B: handling a new restriction](coursepilot/CASE_B.md)
- [Case C: saving versus registering](coursepilot/README.md)
- [Submission Google Doc](https://docs.google.com/document/d/1I3dnPWBtAP_rZCBOhyWOOJOh13H8v9YgnUiKL6i-Z-A/edit?tab=t.uig7mgyr21pt) · [Markdown backup](SUBMISSION.md)
- [Shared metrics and questions](evaluation/SHARED_METRICS.md)

## Run the app

Install Git, Python 3.10+, and either Codex CLI or Claude Code. Sign in to your chosen CLI with your own account. No extra Python packages, Docker, database, or Banner account are needed.

```powershell
git clone https://github.com/abhik030/coursepilot-cs4973.git
cd coursepilot-cs4973
python -m coursepilot --output coursepilot/browser-runs
```

Open **http://127.0.0.1:8765/**. Choose a case, start a new run, and select the mode, condition, provider, and model. Keep the terminal open. Stop the server with Ctrl+C.

Already cloned? Run `git pull --ff-only` first. See the [teammate guide](coursepilot/TEAMMATE_GUIDE.md) for sign-in checks and troubleshooting.

The app runs on each teammate's computer. GitHub shares code and saved results; it does not host the app. After a server restart, old runs open as read-only results.

## Current status

- **A:** Aditya's [completed case](coursepilot/CASE_A.md). Five baseline trials: four successes and one requirement failure.
- **B:** Hudson's assigned case, implemented. [Five completed runs across six retained attempts](coursepilot/CASE_B_RESULTS.md), including the original tool-format error and scoring audit.
- **C:** Abhi's case. [Five Codex trials](coursepilot/RESULTS.md), all successful.
- **Videos:** All three recordings are pending. The last teammate to finish submits.

Software checks make no model calls:

```powershell
python -m unittest discover -s coursepilot/tests -v
```

Coding assistants: read [AI_HANDOFF.md](AI_HANDOFF.md). Earlier terminal-only work is kept separately in [evaluation/](evaluation/CASE_C.md).
