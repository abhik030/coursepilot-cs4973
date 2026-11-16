# Teammate setup and case guide

## Install and run

You need Git, Python 3.10+, and **either Codex CLI or Claude Code**, signed in with your own account. A desktop chat app alone does not install its CLI. No Banner login, Docker, database, or extra Python packages are needed.

Use the official [Codex setup](https://learn.chatgpt.com/docs/cli) or [Claude Code setup](https://code.claude.com/docs/en/setup). Check your chosen CLI:

```powershell
# Codex
codex --version
codex login status
# Or Claude
claude --version
claude auth status
```

Sign in with `codex login` or `claude auth login` if needed. Claude support was checked with version 2.1.292.

```powershell
git clone https://github.com/abhik030/coursepilot-cs4973.git
cd coursepilot-cs4973
python -m unittest discover -s coursepilot/tests -v
python -m coursepilot --output coursepilot/browser-runs
```

For an existing clone, run `git pull --ff-only` first. Use `python3` or `py` if that is your Python command.

Open **http://127.0.0.1:8765/** on your computer. Choose a case, start a run, then select human/simulated mode, baseline/controlled, provider, and model. Codex defaults to `gpt-6.1-sol`; Claude to `sonnet`. Both model roles use that selection.

Keep the server terminal open; Ctrl+C stops it. If port 8765 is occupied, reuse the existing app or add `--port 8766` and open that address. All cases use one server.

Tests make no model calls; an assistant reply does. If setup fails, send Abhi the command/error and Python/CLI versions. See [website navigation](WORKSPACE.md) for runs and saved results.

## Who does what

- **Aditya:** Implement Case A, where a preference tempts the agent to drop a required course.
- **Hudson:** Review the implemented [Case B](CASE_B.md), its [five attempts](case-b-runs/RESULTS.md), and actual contribution/ownership. Do not overwrite it with a template or rerun the batch.
- **Videos:** Aditya records C, Hudson records A, Abhi records B, subject to confirming actual creators. The recorder must be someone other than the creator.

## Build Case A

Create a branch, then copy the starting files:

```powershell
git switch -c case-a-aditya
Copy-Item coursepilot/cases/planning_template.json coursepilot/cases/aditya_a.json
Copy-Item coursepilot/fixtures/approval_v2.json coursepilot/fixtures/aditya_a.json
```

1. In the case JSON, set a unique ID, title, actual creator, and `fixture` path (`../fixtures/aditya_a.json`). Replace template status.
2. Edit the starting data: courses, requirements, work blocks, grades, and seats. Include a tempting invalid option and independently check at least one valid schedule.
3. Set the stage titles/messages. Human task buttons and the simulated student use the same stages. `chat` asks/discusses; `save` and `register` grant permission for the named `target`.
4. For corrections, `profile_update` changes the stored rules when that task button is sent. Include the change in the visible message and retain earlier rules.
5. Set the success rule. A draft-only task uses `"success": {"final_draft": "A"}`. Add `expected_sections` only if the task requires one exact set; otherwise accept all valid drafts.

Course-section keys are five-digit CRNs. `requires_sections` lists linked labs. Prerequisite groups are AND across groups, OR within each group, with minimum grades. Enrollment seats and waitlist places are different.

## Check and collect results

First try your case in human mode:

```powershell
python -m coursepilot --case coursepilot/cases/aditya_a.json --output coursepilot/a-development
```

After the case is final and model use is authorized, collect five baseline simulated-user trials:

```powershell
python -m coursepilot.batch --case coursepilot/cases/aditya_a.json --provider codex --model gpt-6.1-sol --effort medium --runs 5 --output coursepilot/a-recorded-runs
python -m coursepilot.verify --output coursepilot/a-recorded-runs
```

For Claude, use `--provider claude --model sonnet`. Keep provider/model/settings and case data fixed. Use new output folders; retain failures and keep development runs separate.

Write a short case document covering setup, task/initial prompt, starting data/reset, both user-mode protocols and stopping rules, valid outcomes, shared metrics/questions, actual five-run results and failure counts, rejected alternatives, mocked/external systems, and how the proposed agent would use the same case. [B](CASE_B.md) and [C](README.md) are examples.

## Share your work

Send a branch or pull request containing your case, starting data, document, five complete run folders, and result table. Do not overwrite existing evidence. Each run needs `trajectory.json`, `reward.json`, and `config.json`.

Public read access does not grant push access. If needed, fork the repo on GitHub and add your fork:

```powershell
git remote add mine https://github.com/YOUR_USERNAME/coursepilot-cs4973.git
```

Commit only your intended files, then `git push -u mine YOUR_BRANCH_NAME` and open a pull request to `abhik030/coursepilot-cs4973`. If blocked, send Abhi the branch/fork link.

Use the [shared metrics/questions](../evaluation/SHARED_METRICS.md) and [recording guides](REPRODUCTION.md). Add completed case/video links and actual creator/tester names to [the submission index](../SUBMISSION.md). The last teammate to finish submits. Human-study responses are not due now.
