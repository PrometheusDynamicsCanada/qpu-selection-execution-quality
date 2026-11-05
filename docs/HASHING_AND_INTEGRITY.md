# Hashing and Evidence Integrity

## Why the hashing layer exists

Scientific benchmark numbers are easy to copy into a table. The harder question is whether the underlying observations can be independently inspected and whether the preserved evidence can be shown to be unchanged after capture.

This repository therefore treats the raw hardware responses as evidence artifacts and applies cryptographic integrity checks before publication.

## Evidence chain

```text
IBM Quantum job
      |
      +--> raw job details JSON
      |
      +--> raw job results JSON
                |
                v
       deterministic evidence ZIP
                |
                v
          SHA-256 digest
                |
                v
      published hash manifests
                |
                v
        independent verifier
```

## What is hashed

For each IBM job package, the workflow records SHA-256 digests for:

- the raw IBM job-details response;
- the raw IBM results response; and
- the complete deterministic ZIP package containing the evidence.

The repository also retains a manifest of package digests so a reviewer can recompute the final package hash independently.

## Why a deterministic package matters

The evidence package is constructed deterministically so that the same preserved contents produce the same archive representation. This avoids making the final package hash depend on incidental archive metadata such as changing timestamps.

## What verification checks

The verification workflow checks that:

1. the package exists and is readable;
2. required evidence members exist;
3. the IBM job identifier is internally consistent;
4. raw response hashes match the values recorded in the package metadata;
5. the outer package SHA-256 matches the published checksum manifest; and
6. the detailed evidence manifest agrees with the package hash.

A changed byte in one of the preserved artifacts changes the corresponding SHA-256 digest and causes verification to fail.

## What this establishes

The hashing system provides a strong **tamper-evident integrity mechanism for the preserved evidence after hashing**. It does not claim that no one could have fabricated an experiment before the initial capture. That broader provenance question is addressed separately through the IBM job identifier, authenticated retrieval, raw IBM response preservation, execution timestamps, and experimental records.

The purpose of the system is to minimize the amount of trust a reviewer must place in a manually assembled results table.

## Independent verification

The verification scripts are published with the experiment. A reviewer can obtain the evidence packages, recompute SHA-256 values locally, and compare them to the published manifests without trusting a hidden checksum service.

No API credential is required to recompute the hashes of already-published evidence packages.
