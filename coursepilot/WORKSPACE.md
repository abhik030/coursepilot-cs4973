# Using the website

```powershell
python -m coursepilot --provider claude --output coursepilot/browser-runs
```

Open **http://127.0.0.1:8765/**. Use `--provider codex` for Codex defaults; choose either installed provider before a new run.

- **Cases:** A is pending; B and C are ready.
- **Case page:** Start a run or open a previous one.
- **Run page:** One conversation, schedule, task guide, and result.
- **All runs:** Browse trials and browser runs by case.

Task buttons send student messages. Wait for each response before the next step. In B, the second button also adds the restriction to the student profile.

**Continue run** resumes a live session. **View run** opens a read-only result. Refreshing can reconnect while the server runs; after restarting, old runs are read-only. Start a new run for a recording.

Drafting, saving a plan, and registering are separate actions. **Finish & save** writes logs/results; it does not save a course plan or register courses.

Runs belong to that local server and checkout. Committed baseline results appear in everyone's clone; new browser runs stay on that computer. All cases share one port.
