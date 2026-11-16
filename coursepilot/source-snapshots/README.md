# Archived source fingerprints

The UTF-8 file-reading fix in the offline verification helper was made while the baseline batch was being collected. It does not change agent inference, tool behavior, permission logic, or scoring. Earlier run configurations captured the original helper's file hash; its exact original bytes are preserved here as a hash-named text file.

The verifier accepts a source fingerprint only when either the current file or an archived blob exactly matches its SHA-256. Its report explicitly lists any archived sources used. This avoids rewriting historical configurations or treating Windows text-decoding errors as model failures.

Version 2.1 adds Claude Code alongside Codex and changes the provider routing and browser controls. Exact pre-change bytes for the affected v2.0 files are also archived here. Historical trials retain their original source fingerprints and prompts; a verification report using these blobs checks the historical implementation, not a claim that the trials ran on the newer code.

After the five Case B attempts, version 2.1.1 corrected an artifact lookup that treated `Plan A` as different from `A`. The pre-audit engine, version file, analysis helper, and integrity test bytes are preserved by hash. Historical rewards and model traces were not rewritten; the separate Case B audit records original and audited metrics plus the audit source fingerprints.

Version 2.2 adds the shared case hub, separate run URLs/history, and an optional loopback bridge for the user's existing conversation. Pre-change server, interface, style, and version bytes are archived here. Historical inference prompts, model responses, and scoring records are unchanged.
