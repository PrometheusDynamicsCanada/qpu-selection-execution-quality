# 20Q Visual Guide

The screenshots in `github_images/` are included so a reader can see the experiment as it appears in the execution interface rather than interpreting the result only from CSV/JSON files.

## What each screenshot group represents

Each QPU has four views:

1. **Measured execution results** — fidelity, entropy, HOP, TVD and XEB for SABRE O3, TKET and Prometheus.
2. **Hardware allocation** — the physical-qubit realization for the 20Q workload on that target.
3. **Circuit structure** — depth, two-qubit gate count and related structural comparisons.
4. **Metric chart** — visual comparison of the measured/structural values.

## Fez

- `Screenshot (1440).png` — measured results
- `Screenshot (1441).png` — hardware allocation
- `Screenshot (1442).png` — circuit structure
- `Screenshot (1443).png` — metric chart

## Kingston

- `Screenshot (1444).png` — measured results
- `Screenshot (1445).png` — hardware allocation
- `Screenshot (1446).png` — circuit structure
- `Screenshot (1447).png` — metric chart

## Marrakesh

- `Screenshot (1448).png` — measured results
- `Screenshot (1449).png` — hardware allocation
- `Screenshot (1450).png` — circuit structure
- `Screenshot (1451).png` — metric chart

## Why the screenshots matter

The visual interface makes the physical nature of the experiment immediately apparent: each result is attached to a named QPU, an IBM job ID, a qubit scale, a shot count, and measured execution metrics.

The screenshots are explanatory material. The authoritative evidence remains the preserved IBM job payloads and their verification manifests.
