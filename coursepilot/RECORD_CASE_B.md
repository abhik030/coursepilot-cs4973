# Record Case B

Use [CASE_B.md](CASE_B.md) as the written case document. Confirm the actual creator before calling this an independent teammate recording. Sign in to the CLI before recording.

1. Start your screen recorder. Show the case document and repository. Say: **“I'm Abhi, running Case B: keeping earlier requirements when a student adds a restriction.”**
2. Show setup from the repository root:

   ```powershell
   git rev-parse HEAD
   python --version
   claude --version
   python -m unittest discover -s coursepilot/tests -v
   python -m coursepilot --provider claude --output coursepilot/browser-runs
   ```

   For a new checkout, follow [the setup guide](TEAMMATE_GUIDE.md). If the server is already running, show it rather than starting a second one.
3. In Brave, open **http://127.0.0.1:8765/** → **Case B → Start a new run**. Choose **I do — browser chat**, **Baseline**, **Claude Code / sonnet**, then begin.
4. Click **Check the initial draft**. Wait for the response. Show draft A and its calendar: 90001/90002/90004/90010, 13 credits, capstone Mon/Wed at 08:00.
5. Click **Add Monday restriction and revise**. Wait. This button updates the stored restriction as well as sending the message. Show the revised draft/calendar: expected 90006 instead of 90004, with the other three sections kept. Read the confirmation and explain what actually changed.
6. Click **Finish & save**. Show the run ID/result. Open that run's `trajectory.json`, `reward.json`, and `config.json` in the folder shown by the app. Check that enrollment stayed unchanged.
7. Briefly show [the five-attempt results](case-b-runs/RESULTS.md): four correct completions, one tool-format error, and the separately corrected scoring bug. Your video run is separate from those trials.
8. Save/upload the recording and add its accessible URL and actual creator/tester names to [SUBMISSION.md](../SUBMISSION.md).

Keep both responses in the video, or disclose trimmed waiting periods. Show errors if they happen. No survey answers are needed. The last teammate to finish submits.
