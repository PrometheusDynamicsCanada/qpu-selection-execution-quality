# Reproducibility

## Evidence verification

The repository includes the capture and verification scripts used to preserve and validate the IBM evidence packages.

The verification process can be run against the already-published evidence packages without an IBM API key because the hashes are computed locally from the package contents.

## Directory workflow

Within each experiment directory, the workflow is:

```text
1_sanitize_ledger.py
        ↓
public_evidence_ledger.json
        ↓
2_fetch_zips.py
        ↓
raw IBM evidence ZIPs + manifests + SHA-256
        ↓
3_verify_and_view.py
        ↓
master_results.csv + evidence_verification.csv
```

## Re-running capture

A fresh IBM capture requires appropriate IBM Quantum credentials and access to the corresponding jobs. Credentials are not stored in the repository.

## Independent checks

A reviewer can:

1. inspect the IBM job identifiers;
2. inspect the preserved raw IBM responses;
3. recompute SHA-256 hashes locally;
4. compare those hashes with `sha256sums.txt` and the evidence manifest; and
5. inspect the consolidated CSV results.

The screenshots are convenience views; the preserved evidence packages remain the authoritative artifacts.
