# Archived source fingerprints

The UTF-8 file-reading fix in the offline verification helper was made while the baseline batch was being collected. It does not change agent inference, tool behavior, permission logic, or scoring. Earlier run configurations captured the original helper's file hash; its exact original bytes are preserved here as a hash-named text file.

The verifier accepts a source fingerprint only when either the current file or an archived blob exactly matches its SHA-256. Its report explicitly lists any archived sources used. This avoids rewriting historical configurations or treating Windows text-decoding errors as model failures.
