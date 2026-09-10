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
