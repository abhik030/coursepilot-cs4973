# Local course-registration sandbox

This is a small working Python simulator built for the CoursePilot pitch. It contains 16 fictional course sections, one fictional student, a one-course degree-requirement subset, enrollment, seat counts, prerequisites, class meetings, work hours, and minimum/maximum credits.

It makes no network requests, uses no university account, and has no Banner connection. It does not call an LLM. The functional checks feed it explicit synthetic actions. They establish software behavior, not the way a model actually behaves.

## Run

Use Python 3.10 or later. No third-party packages are required. The report timestamp uses UTC.

```powershell
python check_functionality.py
python registration_sandbox.py
```

Run those commands from this folder. The first writes `functional-checks.json` and `functional-report.md`. The second prints a scripted approved-swap example and its trace scores. Neither output is an LLM transcript.

## What is shared and what is added

Both modes use the same catalog, prerequisite/class-conflict checks, maximum-credit check, and atomic add/drop transaction. A failed transaction preserves the original enrollment. This models a protection described in Northeastern's registration guidance; it is not an integration with Banner.

Events run sequentially in one Python process. This prototype does not implement concurrent database transactions or a multi-user registration server.

`controlled=False` represents the underlying tools available to a responsible conversational baseline. Student-specific minimum credits, work hours, pause, and exact approval are recorded and checked by an independent scorer. The simulated tool layer does not enforce those extra student controls in this mode. A real baseline agent would receive instructions to follow them; we have not connected or tested that agent yet. Scripted invalid actions test that the scorer can detect a violation. They do not show that an LLM would choose those actions.

`controlled=True` adds harness enforcement for the confirmed student rules and exact-action approval. This is the intentional treatment difference. Approval binds the term, complete action set, registration-state version, constraint version, expiry, and a one-use ID. A student can revoke approval or pause. The prototype conservatively invalidates approval after any state-version change, including an unrelated seat update; a later design could make that rule more precise and measure whether it causes unnecessary interruptions.

The current fixture stores preferences separately from hard student rules. It permits a required morning course despite an afternoon preference. It does not test language interpretation or memory retention.

## What the scorer can check

- Enrollment and credits after each attempted action.
- Whether a committed action had applicable user approval.
- Student-rule violations in committed changes.
- Blocked attempts, counted separately from committed actions.
- Whether failed actions preserved the original enrollment.
- Whether the required capstone course appears in the final schedule.

The scorer reports these independently. It does not infer full task success, explanation accuracy, or user understanding from an endpoint alone.

## Next steps

1. Connect a real selected LLM and record the exact model, prompt, tools, configuration, and raw trace.
2. Run the same development cases in baseline and controlled conditions. Preserve successes and failures.
3. Build the planned review interface and use held-out cases for the final comparison.
4. Run the planned sessions with actual students, using fictional records.
5. Explore what a Banner connection would require only after access and a suitable university testing environment are established. Do not use live add/drop as a substitute for sandbox evaluation.

Reference: [Northeastern Waitlist Instructions, page 4](https://registrar.northeastern.edu/wp-content/uploads/sites/9/Waitlist-Document-1.pdf).
