# QPU Selection and Quantum Execution Quality

**Empirical study across three 156-qubit IBM Heron processors (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`) testing whether target-QPU selection materially alters physical execution quality when the logical workload is held constant.**

> **Research Question:** Does the choice of physical QPU materially affect the quality of a quantum computation, even when the logical workload is held constant?

---

## Executive Summary & Principal Multi-QPU Broadcast Comparison (`20Q`-`22Q`)

Across the `20Q`-`22Q` multi-QPU broadcast experiments (`9` packed 3-compiler IBM Quantum jobs, `16,384` shots/compiler = `49,152` shots/job, `442,368` broadcast shots preserved in [`Fez_Marrakesh_Kingston/`](Fez_Marrakesh_Kingston/)), dispatching the exact same dense all-to-all logical circuit to `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh` changes measured distribution fidelity by up to **2.75x (`20Q`)** and changes the relative compiler winner at `21Q` and `22Q`:

| Workload Width | Target Processor | SABRE O3 Fidelity $F_B$ (↑) | TKET Fidelity $F_B$ (↑) | Prometheus Fidelity $F_B$ (↑) | Best Strategy on Target QPU | Cross-QPU Arbitrated Winner |
| :---: | :--- | ---: | ---: | ---: | :--- | :--- |
| **20Q Dense ($K_{20}$)** | `ibm_fez` | 0.0227 | 0.0022 | **0.0357** | Prometheus (`+57.4%` vs SABRE) | |
| **20Q Dense ($K_{20}$)** | `ibm_kingston` | 0.0249 | 0.0021 | **0.0981** | **Prometheus (`+293.8%` vs SABRE)** | **`ibm_kingston` (`0.0981`, `2.75x` vs Fez)** |
| **20Q Dense ($K_{20}$)** | `ibm_marrakesh` | 0.0293 | 0.0067 | **0.0577** | Prometheus (`+97.3%` vs SABRE) | |
| **21Q Dense ($K_{21}$)** | `ibm_fez` | 0.0133 | 0.0012 | **0.0345** | Prometheus (`+159.4%` vs SABRE) | |
| **21Q Dense ($K_{21}$)** | `ibm_kingston` | **0.1059** | 0.0020 | 0.0813 | **SABRE O3 (`+30.3%` vs Prom)** | **`ibm_kingston` (`0.1059` SABRE / `0.0904` Prom on Marrakesh)** |
| **21Q Dense ($K_{21}$)** | `ibm_marrakesh` | 0.0641 | 0.0136 | **0.0904** | Prometheus (`+41.0%` vs SABRE) | |
| **22Q Dense ($K_{22}$)** | `ibm_fez` | 0.0002 | 0.0005 | **0.0275** | Prometheus (`55.0x` vs TKET) | |
| **22Q Dense ($K_{22}$)** | `ibm_kingston` | 0.0636 | 0.0003 | **0.0944** | Prometheus (`+48.4%` vs SABRE) | **`ibm_marrakesh` (`0.1036` SABRE / `0.0944` Prom on Kingston)** |
| **22Q Dense ($K_{22}$)** | `ibm_marrakesh` | **0.1036** | 0.0021 | 0.0815 | **SABRE O3 (`+27.1%` vs Prom)** | |

![20Q IBM Kingston metric chart](github_images/Screenshot%20%281447%29.png)
*Figure 1: 20-Qubit Dense All-to-All ($K_{20}$) 3-Way Comparative Execution on `ibm_kingston` (`16,384` shots/compiler, `49,152` total job shots; Classical Distribution Fidelity $F_B$: `SABRE O3 = 0.0249`, `TKET = 0.0021`, `Prometheus = 0.0981`; source archive: [`Fez_Marrakesh_Kingston/`](Fez_Marrakesh_Kingston/)).*

### Metric Definitions & Direction Conventions
- **Classical Computational-Basis Distribution Fidelity ($F_B$, ↑ higher is better):** Throughout this repository (`fidelity` in JSON ledgers and `"State Fidelity"` in Studio UI screenshots), values report the **Bhattacharyya distribution overlap**:
  $$F_B(P_{\text{ideal}}, P_{\text{meas}}) = \sum_{x \in \{0,1\}^n} \sqrt{P_{\text{ideal}}(x)\, P_{\text{meas}}(x)} = \sqrt{F_H}$$
  between the ideal noiseless Z-basis bitstring distribution $P_{\text{ideal}}(x)$ and the measured hardware distribution $P_{\text{meas}}(x)$ after inverse physical-to-logical qubit mapping (where $F_H = F_B^2$ is Squared Hellinger Fidelity). Both metrics evaluate Z-basis measurement distributions from shot counts and are distinct from $4^n$ quantum state tomography.
- **Total Variation Distance ($\text{TVD}$, ↓ lower is better):** $\frac{1}{2}\sum_x |P_{\text{ideal}}(x) - P_{\text{meas}}(x)|$.
- **Linear Cross-Entropy Benchmarking ($\text{XEB}$, ↑ higher is better):** $2^n \sum_x P_{\text{ideal}}(x) P_{\text{meas}}(x) - 1$.
- **Heavy-Output Probability ($\text{HOP}$, ↑ higher is better):** Total measured probability mass on bitstrings exceeding the median of $P_{\text{ideal}}(x)$.

---

## Cryptographic Evidence Integrity

Every hardware execution in this repository is packaged with its raw IBM Quantum job metadata, measurement payloads, and SHA-256 cryptographic digests:

```text
IBM Quantum hardware job
        |
        v
Authenticated IBM API retrieval
        |
        v
Raw job details + raw job results preserved
        |
        v
Deterministic evidence package (.zip)
        |
        v
SHA-256 of raw artifacts + complete package (REPOSITORY_SHA256SUMS.txt)
        |
        v
Independent local verification (3_verify_and_view.py)
```

See [`docs/HASHING_AND_INTEGRITY.md`](docs/HASHING_AND_INTEGRITY.md), [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md), and [`REPOSITORY_SHA256SUMS.txt`](REPOSITORY_SHA256SUMS.txt).

---

## Visual Walkthrough: 20-Qubit Dense All-to-All ($K_{20}$) Broadcast Across 3 Heron QPUs

All three executions below compile the same 20-qubit dense all-to-all logical workload (`39` logical depth, `230` logical gates, `16,384` shots/compiler, `49,152` shots/job; source package: [`Fez_Marrakesh_Kingston/`](Fez_Marrakesh_Kingston/)).

### 1. Target Processor: `ibm_fez` (Job `dah7efb9k43c73aedfp0`, 20Q Dense All-to-All, `16,384` shots/compiler)

| Target QPU | Metric | SABRE O3 | TKET | Prometheus | Prometheus vs. Best Baseline |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `ibm_fez` | Distribution Fidelity $F_B$ (↑) | 0.0227 | 0.0022 | **0.0357** | **+57.37%** |
| `ibm_fez` | Total Variation Distance $\text{TVD}$ (↓) | 0.9193 | 0.9779 | **0.8960** | **-2.54%** |
| `ibm_fez` | Heavy-Output Probability $\text{HOP}$ (↑) | 0.5389 | 0.5264 | **0.5430** | **+0.77%** |
| `ibm_fez` | Cross-Entropy $\text{XEB}$ (↑) | 20.0724 | 2.6434 | **27.1090** | **+35.06%** |
| `ibm_fez` | Shannon Entropy $H$ (bits) | 13.9381 | 13.9716 | **13.9213** | **-0.12%** |
| `ibm_fez` | Compiled Circuit Depth (↓) | 390 | 596 | **315** | **-19.23%** |
| `ibm_fez` | Two-Qubit `CZ` Gates (↓) | 474 | 799 | **405** | **-14.56%** |

![20Q IBM Fez measured results](github_images/Screenshot%20%281440%29.png)
*Figure 2a: `ibm_fez` 20Q Dense All-to-All (`Job ID: dah7efb9k43c73aedfp0`, `16,384` shots/compiler) - Measured Execution Results (`F_B`: `0.0227` SABRE / `0.0022` TKET / **`0.0357`** Prometheus; `TVD`: `0.9193` / `0.9779` / **`0.8960`**; `XEB`: `20.0724` / `2.6434` / **`27.1090`**; source: `Fez_Marrakesh_Kingston/`).*

![20Q IBM Fez hardware allocation](github_images/Screenshot%20%281441%29.png)
*Figure 2b: `ibm_fez` 20Q Dense All-to-All - Physical 156-Qubit Hardware Allocation View.*

![20Q IBM Fez structural comparison](github_images/Screenshot%20%281442%29.png)
*Figure 2c: `ibm_fez` 20Q Dense All-to-All - Compiled Circuit Structural Comparison (`Depth`: `390` SABRE / `596` TKET / **`315`** Prometheus; `2Q Gates`: `474` / `799` / **`405`**).*

![20Q IBM Fez metric chart](github_images/Screenshot%20%281443%29.png)
*Figure 2d: `ibm_fez` 20Q Dense All-to-All - Comparative Observable Chart (`16,384` shots/compiler).*

---

### 2. Target Processor: `ibm_kingston` (Job `dah7efgmhr3c73e665g0`, 20Q Dense All-to-All, `16,384` shots/compiler)

| Target QPU | Metric | SABRE O3 | TKET | Prometheus | Prometheus vs. Best Baseline |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `ibm_kingston` | Distribution Fidelity $F_B$ (↑) | 0.0249 | 0.0021 | **0.0981** | **+293.81%** |
| `ibm_kingston` | Total Variation Distance $\text{TVD}$ (↓) | 0.9147 | 0.9789 | **0.8089** | **-11.57%** |
| `ibm_kingston` | Heavy-Output Probability $\text{HOP}$ (↑) | 0.5236 | 0.4880 | **0.6176** | **+17.95%** |
| `ibm_kingston` | Cross-Entropy $\text{XEB}$ (↑) | 19.7459 | 2.1115 | **58.1474** | **+194.48%** |
| `ibm_kingston` | Shannon Entropy $H$ (bits) | 13.9276 | 13.9434 | **13.8115** | **-0.83%** |
| `ibm_kingston` | Compiled Circuit Depth (↓) | 512 | 596 | **315** | **-38.48%** |
| `ibm_kingston` | Two-Qubit `CZ` Gates (↓) | 600 | 799 | **409** | **-31.83%** |

![20Q IBM Kingston measured results](github_images/Screenshot%20%281444%29.png)
*Figure 3a: `ibm_kingston` 20Q Dense All-to-All (`Job ID: dah7efgmhr3c73e665g0`, `16,384` shots/compiler) - Measured Execution Results (`F_B`: `0.0249` SABRE / `0.0021` TKET / **`0.0981`** Prometheus; `TVD`: `0.9147` / `0.9789` / **`0.8089`**; `XEB`: `19.7459` / `2.1115` / **`58.1474`**; source: `Fez_Marrakesh_Kingston/`).*

![20Q IBM Kingston hardware allocation](github_images/Screenshot%20%281445%29.png)
*Figure 3b: `ibm_kingston` 20Q Dense All-to-All - Physical 156-Qubit Hardware Allocation View.*

![20Q IBM Kingston structural comparison](github_images/Screenshot%20%281446%29.png)
*Figure 3c: `ibm_kingston` 20Q Dense All-to-All - Compiled Circuit Structural Comparison (`Depth`: `512` SABRE / `596` TKET / **`315`** Prometheus; `2Q Gates`: `600` / `799` / **`409`**).*

![20Q IBM Kingston metric chart](github_images/Screenshot%20%281447%29.png)
*Figure 3d: `ibm_kingston` 20Q Dense All-to-All - Comparative Observable Chart (`16,384` shots/compiler).*

---

### 3. Target Processor: `ibm_marrakesh` (Job `dah7ekgmhr3c73e665kg`, 20Q Dense All-to-All, `16,384` shots/compiler)

| Target QPU | Metric | SABRE O3 | TKET | Prometheus | Prometheus vs. Best Baseline |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `ibm_marrakesh` | Distribution Fidelity $F_B$ (↑) | 0.0293 | 0.0067 | **0.0577** | **+97.34%** |
| `ibm_marrakesh` | Total Variation Distance $\text{TVD}$ (↓) | 0.9032 | 0.9578 | **0.8609** | **-4.69%** |
| `ibm_marrakesh` | Heavy-Output Probability $\text{HOP}$ (↑) | 0.5388 | 0.5381 | **0.5758** | **+6.86%** |
| `ibm_marrakesh` | Cross-Entropy $\text{XEB}$ (↑) | 19.4430 | 7.6657 | **38.1583** | **+96.26%** |
| `ibm_marrakesh` | Shannon Entropy $H$ (bits) | 13.9112 | 13.9549 | **13.8697** | **-0.30%** |
| `ibm_marrakesh` | Compiled Circuit Depth (↓) | 337 | 596 | **300** | **-10.98%** |
| `ibm_marrakesh` | Two-Qubit `CZ` Gates (↓) | 439 | 799 | **396** | **-9.79%** |

![20Q IBM Marrakesh measured results](github_images/Screenshot%20%281448%29.png)
*Figure 4a: `ibm_marrakesh` 20Q Dense All-to-All (`Job ID: dah7ekgmhr3c73e665kg`, `16,384` shots/compiler) - Measured Execution Results (`F_B`: `0.0293` SABRE / `0.0067` TKET / **`0.0577`** Prometheus; `TVD`: `0.9032` / `0.9578` / **`0.8609`**; `XEB`: `19.4430` / `7.6657` / **`38.1583`**; source: `Fez_Marrakesh_Kingston/`).*

![20Q IBM Marrakesh hardware allocation](github_images/Screenshot%20%281449%29.png)
*Figure 4b: `ibm_marrakesh` 20Q Dense All-to-All - Physical 156-Qubit Hardware Allocation View.*

![20Q IBM Marrakesh structural comparison](github_images/Screenshot%20%281450%29.png)
*Figure 4c: `ibm_marrakesh` 20Q Dense All-to-All - Compiled Circuit Structural Comparison (`Depth`: `337` SABRE / `596` TKET / **`300`** Prometheus; `2Q Gates`: `439` / `799` / **`396`**).*

![20Q IBM Marrakesh metric chart](github_images/Screenshot%20%281451%29.png)
*Figure 4d: `ibm_marrakesh` 20Q Dense All-to-All - Comparative Observable Chart (`16,384` shots/compiler).*

---

## Dataset Inventory & Reproducibility

- **Processors Tested:** `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh` (156Q IBM Heron r2)
- **Workloads:** Dense All-to-All ($K_n$) historical `16Q`-`23Q` sweeps (`Fez/`, `Kingston/`, `Marrakesh/`) and `20Q`-`22Q` multi-QPU broadcast runs (`Fez_Marrakesh_Kingston/`)
- **Sampling Depth:** `16,384` shots per compiler (`49,152` shots per 3-way job in the broadcast set)
- **Verification Guides:**
  1. [`RESULTS.md`](RESULTS.md) - Consolidated multi-QPU broadcast tables and analysis
  2. [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) - Complete IBM Quantum Job ID and ZIP package inventory
  3. [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) & [`docs/HASHING_AND_INTEGRITY.md`](docs/HASHING_AND_INTEGRITY.md) - Step-by-step SHA-256 verification workflow
  4. [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) - Field definitions and metric conventions

---

## Prometheus Dynamics Public Repository Portfolio

| Repository | Scope & Empirical Dataset | Primary Verification Artifacts |
| :--- | :--- | :--- |
| **[`Hybrid-Quantum-HPC-Benchmarks`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks)** | **Multi-Cloud QPU & Hybrid GPU Corpus:** `12` live Amazon Braket `ProgramSet` tasks (`Rigetti Cepheus-1-108Q`, `IQM Garnet` 20Q, `IQM Emerald` 54Q), `107` IBM Heron 3-way jobs (`4Q`-`23Q`), `144`-execution pre-committed validation suite (`48.0s` QPU time), and `150` NVIDIA H100 (`VeloxQH100_1`) QUBO runs (`4` to `1,029` variables). | [`aws_braket_qpu_12_jobs_ledger.json`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks/blob/main/aws_braket_qpu_12_jobs_ledger.json), [`ibm_heron_156q_verified_benchmarks.json`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks/blob/main/ibm_heron_156q_verified_benchmarks.json), [`validation_suite_144_executions/`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks/tree/main/validation_suite_144_executions), `verify_corpus_and_schedules.py` |
| **[`IBM-Heron-156Q-Benchmarks`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-156Q-Benchmarks)** | **156Q Heron r2 Scaling & Pre-Committed Suite:** `10` packed `SamplerV2` batch jobs (`441` physical circuits, `755,712` shots) across `ibm_fez`, `ibm_marrakesh`, and `ibm_kingston` covering `3Q`-`13Q` odd/even parity scaling, a `15-algorithm` matrix at `9Q`, and the `144-execution` pre-committed validation suite. | [`data/heron_156q_99tournaments_297circuits.csv`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-156Q-Benchmarks/blob/main/data/heron_156q_99tournaments_297circuits.csv), [`validation_suite_144_executions/`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-156Q-Benchmarks/tree/main/validation_suite_144_executions), `scripts/verify_ledger.py` |
| **[`qpu-selection-execution-quality`](https://github.com/PrometheusDynamicsCanada/qpu-selection-execution-quality)** | **Cryptographic Provenance & Cross-QPU Arbitration:** Archived IBM Quantum job ZIP bundles and `SHA-256` manifests (`16Q`-`23Q` dense all-to-all across `ibm_fez`, `ibm_kingston`, and `ibm_marrakesh`). | [`EVIDENCE_INDEX.md`](https://github.com/PrometheusDynamicsCanada/qpu-selection-execution-quality/blob/main/EVIDENCE_INDEX.md), [`REPOSITORY_SHA256SUMS.txt`](https://github.com/PrometheusDynamicsCanada/qpu-selection-execution-quality/blob/main/REPOSITORY_SHA256SUMS.txt), `Fez_Marrakesh_Kingston/3_verify_and_view.py` |
| **[`prometheus-quantum-telemetry`](https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry)** | **Mechanistic Operating Envelope (`01`-`05`):** Distributional concentration (`100k` shots/circuit), `40` randomized matched pairs, `3Q`-`10Q` scaling boundaries, `13Q` ground-state avoidance, and a `540`-PUB (`1.11M`-shot) 3-QPU sweep. | [`IBM_JOB_EVIDENCE_INDEX.csv`](https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry/blob/main/IBM_JOB_EVIDENCE_INDEX.csv), [`MASTER_RESULTS.csv`](https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry/blob/main/MASTER_RESULTS.csv), `verify_sha256_evidence.py` |
| **[`prometheus-execution-intelligence`](https://github.com/PrometheusDynamicsCanada/prometheus-execution-intelligence)** | **System Architecture & Execution-Selection Overview:** Multi-compiler candidate evaluation (`SABRE O3`, `TKET`, `Prometheus`), multi-QPU dispatch workflow, and Studio interface walkthrough. | [`ARCHITECTURE.md`](https://github.com/PrometheusDynamicsCanada/prometheus-execution-intelligence/blob/main/ARCHITECTURE.md), [`SCREENSHOT_GALLERY.md`](https://github.com/PrometheusDynamicsCanada/prometheus-execution-intelligence/blob/main/SCREENSHOT_GALLERY.md) |
| **[`Hyperion-fusion-telemetry`](https://github.com/PrometheusDynamicsCanada/Hyperion-fusion-telemetry)** | **Multi-Tokamak Disruption Forecasting Telemetry:** `4,121` supervised holdout discharges (`ASIPP EAST`, `GA DIII-D`, `MIT Alcator C-Mod`) with binary confusion matrices & 95% Wilson CIs, plus a `12,693`-shot `UKAEA MAST` archive audit (`2,017` disruptions). | [`data/holdout/cross_reactor_summary.csv`](https://github.com/PrometheusDynamicsCanada/Hyperion-fusion-telemetry/blob/main/data/holdout/cross_reactor_summary.csv), [`scripts/verify_classification_metrics.py`](https://github.com/PrometheusDynamicsCanada/Hyperion-fusion-telemetry/blob/main/scripts/verify_classification_metrics.py) |
