# QPU Selection and Quantum Execution Quality

## Experimental evidence: the target QPU materially affects execution quality

This repository presents an empirical study of quantum circuit execution on real IBM Quantum hardware, with a specific research question:

> **Does the choice of physical QPU materially affect the quality of a quantum computation, even when the logical workload is held constant?**

The study uses dense all-to-all workloads and compares execution behavior across IBM Heron systems including **ibm_fez, ibm_kingston, and ibm_marrakesh**.

The repository preserves the experimental evidence, benchmark outputs, screenshots, IBM job identifiers, raw result packages, and the cryptographic verification system used to make post-capture modification detectable.

---

## Evidence integrity comes first

The evidence is not presented as a spreadsheet that must simply be trusted. The capture and verification path is preserved:

```text
IBM Quantum hardware job
        ↓
Authenticated IBM API retrieval
        ↓
Raw job details + raw job results preserved
        ↓
Deterministic evidence package
        ↓
SHA-256 of raw artifacts + complete package
        ↓
Published hash manifest
        ↓
Independent verification
```

Each evidence package can be checked independently. The verifier recomputes the relevant SHA-256 values and detects changes to the preserved artifacts after capture.

This is **tamper-evident evidence preservation**: a modified byte produces a different cryptographic fingerprint. The repository also retains IBM job IDs and execution timestamps so that the underlying hardware execution can be tied back to the IBM record.

See [docs/HASHING_AND_INTEGRITY.md](docs/HASHING_AND_INTEGRITY.md).

---

## The 20-qubit broadcast experiment

The clearest visual example is the 20Q broadcast experiment. The same dense all-to-all workload was executed against three different physical QPUs, with the compiler outputs and measured physical results recorded separately for each target.

### State fidelity observed on the three QPUs

| Target QPU | SABRE O3 | TKET | Prometheus |
|---|---:|---:|---:|
| IBM Fez | 0.0227 | 0.0022 | **0.0357** |
| IBM Kingston | 0.0249 | 0.0021 | **0.0981** |
| IBM Marrakesh | 0.0293 | 0.0067 | **0.0577** |

The Prometheus result therefore changes substantially with the physical target: **0.0357 on Fez, 0.0981 on Kingston, and 0.0577 on Marrakesh** for the same 20Q workload family.

That is the central observation of this repository. The execution environment is not interchangeable. The physical QPU changes the observed outcome.

The experiment also records TVD and XEB, providing additional physical observables rather than relying on a single metric.

### Visual walkthrough

The screenshots below are taken directly from the Prometheus execution interface and are included to make the experiment easier to understand without requiring a reader to start from raw JSON.

#### IBM Fez — 20Q

**Measured execution results**

![20Q IBM Fez measured results](github_images/Screenshot%20%281440%29.png)

**Hardware allocation**

![20Q IBM Fez hardware allocation](github_images/Screenshot%20%281441%29.png)

**Circuit structure**

![20Q IBM Fez structural comparison](github_images/Screenshot%20%281442%29.png)

**Visual metric comparison**

![20Q IBM Fez metric chart](github_images/Screenshot%20%281443%29.png)

#### IBM Kingston — 20Q

![20Q IBM Kingston measured results](github_images/Screenshot%20%281444%29.png)

![20Q IBM Kingston hardware allocation](github_images/Screenshot%20%281445%29.png)

![20Q IBM Kingston structural comparison](github_images/Screenshot%20%281446%29.png)

![20Q IBM Kingston metric chart](github_images/Screenshot%20%281447%29.png)

#### IBM Marrakesh — 20Q

![20Q IBM Marrakesh measured results](github_images/Screenshot%20%281448%29.png)

![20Q IBM Marrakesh hardware allocation](github_images/Screenshot%20%281449%29.png)

![20Q IBM Marrakesh structural comparison](github_images/Screenshot%20%281450%29.png)

![20Q IBM Marrakesh metric chart](github_images/Screenshot%20%281451%29.png)

---

## What the experiment demonstrates

The repository is designed to test a physical execution question, not to claim universal compiler superiority.

The important observation is that the measured result depends on **where the computation runs**. Across the broadcast experiment, the same workload family produces materially different fidelity, TVD, and XEB values on different QPUs. Relative compiler performance also changes by QPU.

For example, at 21Q:

- Fez: Prometheus fidelity 0.0345 vs SABRE 0.0133
- Kingston: Prometheus fidelity 0.0813 vs SABRE 0.1059
- Marrakesh: Prometheus fidelity 0.0904 vs SABRE 0.0641

At 22Q:

- Fez: Prometheus 0.0275 vs SABRE 0.0002
- Kingston: Prometheus 0.0944 vs SABRE 0.0636
- Marrakesh: Prometheus 0.0815 vs SABRE 0.1036

These differences are why compiler evaluation should be interpreted in the context of the physical machine executing the circuit.

Importantly, this repository preserves the cases where Prometheus does not produce the best result. The purpose is to expose the measured behavior of the hardware/compiler interaction, not to construct an always-win narrative.

---

## Dataset

The current package includes the supplied experimental runs across:

- **IBM Fez**
- **IBM Kingston**
- **IBM Marrakesh**
- Dense all-to-all benchmark families
- Historical 16Q–23Q sweeps
- 20Q–22Q multi-QPU broadcast runs
- 16,384 shots per compiler per job in the broadcast set
- 49,152 shots per three-compiler job in that set
- Preserved IBM job IDs and timestamps
- Raw IBM evidence packages
- SHA-256 manifests and verification records

See [RESULTS.md](RESULTS.md) for consolidated findings and [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md) for the job/evidence inventory.

---

## Reproducibility

The repository includes the capture, sanitization, packaging, hashing, and verification scripts used for the evidence workflow.

Start with:

1. [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
2. [docs/HASHING_AND_INTEGRITY.md](docs/HASHING_AND_INTEGRITY.md)
3. [DATA_DICTIONARY.md](DATA_DICTIONARY.md)

No IBM API credentials are included in this repository.

---

## Scope and interpretation

This repository supports the statement that **target-QPU selection materially affects observed execution quality for the experimental workloads studied here**.

It does not by itself establish that one compiler is universally superior across all circuits, QPUs, workloads, or hardware generations.

The raw evidence and verification chain are included so that technically capable reviewers can inspect the experiment rather than relying solely on summarized claims.
