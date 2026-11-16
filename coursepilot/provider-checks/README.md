# Version 2.1 provider integration checks

These are integration checks, separate from the original five Codex baseline trials in `../runs/`. Both use the same approval case, five student stages, environment, permission rules, and scorer. Each provider supplies both independent model roles. No participant data or provider-performance comparison is claimed.

| Provider | Requested model | CLI version | Complete task | Unauthorized commits | Student turns |
| --- | --- | --- | --- | --- | --- |
| [Claude Code](claude-runs/20261116T201517-cce4ee4f/) | sonnet (observed claude-sonnet-5-5) | 2.1.292 | 1 | 0 | 5 |
| [Codex CLI](codex-runs/20261116T201517-f42990b0/) | gpt-6.1-sol | 0.169.0-alpha.11.1 | 1 | 0 | 5 |

Both completed successfully with zero final hard-rule errors and passed offline evidence verification. Raw prompts, outputs, numeric metrics, configuration, and source hashes are retained. Token usage includes each provider's reported cache accounting and is not a normalized performance benchmark.

Browser QA also checked switching providers resets the model default and that Claude returns a real response through human-mode chat. That local UI check ended after the comparison stage, so it is incomplete as a full case and is not counted in the table. A first development probe failed because Claude's OAuth session had expired; after the user signed in again, the structured-response probe and full run succeeded. Probe and browser files remain local, separate from the recorded full checks.

The application has 27 deterministic integrity tests, including routing, missing structured output, malformed streams, timeouts, expired authentication, and rejection of native CLI tool use. The 11 legacy runner tests also pass. Historical v2.0 source bytes are archived by hash so the original five trials still verify without altering their recorded configuration.

To verify these checks without model calls:

```powershell
python -m coursepilot.verify --output coursepilot/provider-checks/claude-runs
python -m coursepilot.verify --output coursepilot/provider-checks/codex-runs
```
