# One website, separate cases and runs

Start one server from the repository root:

```powershell
python -m coursepilot --provider claude --output coursepilot/browser-runs
```

Open **http://127.0.0.1:8765/**. Use Codex instead with `--provider codex`; either provider can be selected before a new run.

- **Cases** is the home page. Case A is Aditya's pending requirements scenario, Case B is the runnable correction scenario, and Case C is the runnable approval scenario.
- Each **case page** lists that case's runs and has a **Start a new run** button when its configuration is ready. Case A instead shows the remaining work until its real configuration exists.
- Each **run page** has its own conversation, draft/state, task progress, and result. Task buttons send instructions to the assistant; the text in the chat is its response.
- **All runs** shows both browser conversations and saved trials, with a case filter. **Continue run** resumes an available live conversation. **View run** opens a saved snapshot with mutation controls disabled.

For the current Case B recording, open Case B and choose **Continue run** for the conversation already started. It is waiting at **Step 2 of 2**. Do not send the first instruction again. Send **Add Monday restriction and revise**, wait, review the draft, then **Finish & save**.

If starting a completely new recording from setup, use **Case B → Start a new run**, choose human mode/baseline/provider/model, and click Begin session. Send the two guide steps in order. New runs retain earlier attempts. There is no need to run another five-trial batch.

New run URLs look like `/runs/RUN_ID`, and case URLs are `/cases/a`, `/cases/b`, and `/cases/c`. The port is the address of the one local server; cases no longer require separate ports.

Snapshots from a previous server process remain readable but are not automatically restored as live model sessions. During the current migration, the existing Case B server is retained behind an explicit loopback bridge so that the already-started conversation can finish through the new site. Keep that older process running until its run is saved. New sessions are created by the single main server. The bridge does not issue model calls by itself.
