# Abhi's short Case B recording checklist

The runnable case is ready; this checklist does not itself constitute a video. Confirm the actual case creator before labeling the recording as an independent teammate reproduction. Do not invent that contribution or a tester/video URL.

1. Start your screen recorder. Show [CASE_B.md](CASE_B.md) and the repository/commit you are using. Say: **“I’m Abhi, reproducing CoursePilot Case B: keeping earlier requirements when a student adds a restriction.”**
2. Show the written setup commands being run. For a new clone, follow the teammate guide; from its repository root:

   ```powershell
   git rev-parse HEAD
   python --version
   claude --version
   python -m unittest discover -s coursepilot/tests -v
   python -m coursepilot --provider claude --case coursepilot/cases/hudson_b.json --port 8766 --output coursepilot/browser-runs/abhi-reproduces-b
   ```

   If the prepared server already owns 8766, stop that server before recording setup or use 8768 and open that port. Sign in before recording; do not show login credentials.
3. Open the app. Choose **human mode**, **baseline**, **Claude Code / sonnet**, then Begin session.
4. Click **Check the initial draft** and wait. Show draft A: sections 90001/90002/90004/90010, 13 credits, with the capstone Monday/Wednesday at 08:00.
5. Click **Add Monday restriction and revise** and wait. This button sends the correction and updates the authoritative profile. Show the new draft and calendar. A correct result uses 90006 instead of 90004 and keeps the other three sections, still totaling 13 credits. Say what actually happened; do not narrate the expected outcome as though it happened if it did not.
6. Click **Finish & save**. Show the actual run ID/result. Open its `trajectory.json`, `reward.json`, and `config.json` in the output folder shown by the app. Explain briefly: **“We check for ignoring the new restriction or losing an earlier requirement. These are draft changes; enrollment should remain unchanged.”**
7. Show [the actual five-trial results](case-b-runs/RESULTS.md), including any errors and untriggered trials. Report the real counts. This new video run is separate from those five trials and is not a participant study.
8. Stop/save the recording. Upload the video and put its accessible URL, the actual tester, and confirmed creator information in [SUBMISSION.md](../SUBMISSION.md). Do not mark the video complete before that artifact exists.

The case takes two student turns. Keep both agent responses in the video, or clearly disclose any edited waiting periods. The last teammate to finish submits the single team index.
