# Working in CoursePilot

- Start with [AI_HANDOFF.md](AI_HANDOFF.md). Follow the actual case documents and configuration, not assumptions from old chat summaries.
- Reuse this checkout. Preserve recorded evidence; use new output directories for new experiments and never silently replace failures.
- Codex CLI and Claude Code are inference providers selected with `--provider`; either coding assistant can work on this repository.
- Use one website/server with Cases and All runs. Case URLs are `/cases/a`, `/cases/b`, `/cases/c`; each attempt has `/runs/RUN_ID`. Do not reintroduce separate case-specific servers/ports as the primary workflow. During migration, keep the attached legacy process alive until its current run is saved.
- Model calls consume account quota. Case B is complete: the original five attempts plus one additional completed baseline run authorized by the user's request to finish remaining B work. All six are retained. Do not start more trials without new authorization.
- Keep source/case/fixture stable during a final batch. Archive original source bytes before changing files fingerprinted by existing evidence; do not rewrite historical config or raw output.
- Creator, tester, participant, and video labels must reflect actual contributions/actions. Do not fill pending fields from a proposed owner alone or invent participant responses.
- Do not add unsolicited tool-assistance credits or commit coauthors.
- Stage only intended project changes. Existing untracked pitch deliverables are separate work.
