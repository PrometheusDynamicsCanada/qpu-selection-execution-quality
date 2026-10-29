# Security and Publication Boundary

This repository is intended to publish experimental evidence while avoiding disclosure of private credentials or the internal implementation of Prometheus.

## Never publish

- IBM API keys or bearer tokens
- credentials stored in shell history or environment dumps
- private service credentials

## What the evidence repository exposes

The repository intentionally exposes experimental outputs such as circuit metrics, physical allocations, measured observables, IBM job identifiers, timestamps, and preserved execution artifacts needed for independent review.

It does not contain the private Prometheus optimizer implementation, internal weighting scheme, weights, or internal decision logic.

## Raw IBM metadata

Before public distribution, reviewers should confirm that no account-specific or otherwise unnecessary IBM metadata remains in raw evidence packages. The public evidence should contain what is needed for reproducibility and provenance without disclosing unrelated private information.

## Public Derivative Sanitization Policy

To protect proprietary routing trajectories and account identifiers while preserving independent verification of all physical measurements:

1. **`public_evidence_ledger.json` (Sanitized Public Derivative):**
   - Retains `qasm_codes.logical` (the unrouted logical workload circuit), structural compilation metrics (`circuit_metrics`: depth and 2Q gate counts), raw hardware measurement bitstring counts (`raw_counts`), and computed distribution observables (`physical_observables`).
   - Withholds routed physical OpenQASM trajectories (`qasm_codes.prometheus`, `qasm_codes.sabre`, `qasm_codes.tket`) and physical qubit placement maps (`physical_allocation`).
2. **`job-*.zip` Evidence Packages (Sanitized Public Derivative):**
   - `job_results_raw.json`: **Unmodified** raw HTTP response body from the IBM Quantum `/results` endpoint containing the exact `SamplerV2` measurement bitstrings and `ExecutionSpans` timestamps.
   - `job_details_raw.json`: **Sanitized public derivative** of the `/jobs/{id}` metadata with serialized physical circuit payloads (`params.pubs`) and account `user_id` removed, while retaining `id`, `backend`, `created`, `status`, `program`, and `params.options.default_shots`.
   - `evidence_metadata.json`, `evidence_manifest.json`, and `sha256sums.txt`: Record the SHA-256 digests of the sanitized public derivative packages (with original raw packages retained in private storage).
