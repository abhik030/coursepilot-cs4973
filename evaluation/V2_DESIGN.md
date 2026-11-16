# Browser app design notes

The app is implemented. Use [Case C](../coursepilot/README.md) for its current protocol, [Case B](../coursepilot/CASE_B.md) for corrections, and [the submission index](../SUBMISSION.md) for remaining work.

## Main decisions

- Use browser chat with a calendar, catalog, plan cards, and registration view.
- Keep drafts, saved plans, pending registration, enrollment, and waitlists separate.
- Saving A gives permission to save that plan/version only. Discussing B or saying “looks good, but let me check” grants no new permission.
- A clear registration instruction authorizes that action. Ambiguous wording needs clarification.
- Keep the current schedule intact if a requested registration fails.
- Let students correct, pause, or revoke unused permission while the agent works.

These decisions came from the team discussion. [Banner observations](BANNER_OBSERVATIONS.md) informed the workflow; the app uses fictional records and does not connect to Banner.

## What is implemented

Both human and simulated-user modes share the task, course tools, information, and scoring. A local Python server calls the user's signed-in Codex CLI or Claude Code. Python executes the course actions.

Baseline and controlled mode share institutional checks: seats, prerequisites, linked sections, eligibility, and safe registration. Controlled mode adds student-rule checks and permission enforcement for the exact action/plan. The comparison tests enforcement, not a different UI alone.

The logs distinguish attempted, blocked, and completed changes. Scoring checks the requested result as well as permission; refusing all action cannot pass.

## Limits

This is a subset of course-registration rules, not a complete academic audit. A waitlist place is not an enrollment offer; accepting offers is not implemented. No live university writes or human-study findings are claimed.

The earlier terminal-only case, design checks, and pilot remain separate from the five browser baseline trials. [Case C's alternatives section](../coursepilot/README.md#alternatives-considered) explains the rejected scenarios.
