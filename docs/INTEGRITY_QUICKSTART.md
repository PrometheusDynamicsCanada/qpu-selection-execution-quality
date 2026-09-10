# Integrity Quickstart

The fastest way to inspect the evidence integrity layer is:

```text
1. Download a job ZIP
2. Read its published SHA-256
3. Recompute SHA-256 locally
4. Compare the values
5. Run the verifier
6. Confirm the raw-response hashes and manifest checks pass
```

For the current broadcast set, the verifier reports:

```text
IBM evidence packages verified: 9/9
```

A successful verification means the bytes currently being inspected match the hashes recorded when those evidence packages were locked.
