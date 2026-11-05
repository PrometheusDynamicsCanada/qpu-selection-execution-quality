# QPU Selection and Quantum Execution Quality

Empirical study across three 156-qubit IBM Heron processors (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`) testing whether target-QPU selection materially alters physical execution quality when the logical workload is held constant.

**Dataset Scope:** 33 archived IBM Quantum job ZIP bundles (99 physical circuits, 1,622,016 shots across 16Q-23Q in `Fez/`, `Kingston/`, `Marrakesh/`, and 20Q-22Q broadcast runs in `Fez_Marrakesh_Kingston/`; all 33 archived jobs also occur in the 107-job historical IBM Heron corpus) plus the shared 4-job (144-circuit, 147,456-shot) pre-committed validation suite, preserved with raw measurement payloads and SHA-256 cryptographic digests.

---

## 1. Executive Summary & Principal Multi-QPU Broadcast Comparison (20Q-22Q)

### Key Findings

- **2.75x Cross-QPU Fidelity Spread on Identical Logical Circuits:** Across the 20Q-22Q multi-QPU broadcast experiments (9 packed 3-compiler IBM Quantum jobs, 16,384 shots/compiler = 49,152 shots/job, 442,368 broadcast shots preserved in [`Fez_Marrakesh_Kingston/`](Fez_Marrakesh_Kingston/)), dispatching the exact same 20-qubit dense all-to-all logical circuit (K_20) across `ibm_fez`, `ibm_marrakesh`, and `ibm_kingston` changes measured distribution overlap F_B from **0.0357** (`ibm_fez`) and **0.0577** (`ibm_marrakesh`) to **0.0981** (`ibm_kingston`, **2.75x** higher than `ibm_fez`).
- **Compiler Ranking Shifts Across Physical Processors:** At 20Q, **Prometheus** wins on all three QPUs (+57.4% on `ibm_fez`, +97.3% on `ibm_marrakesh`, and **+293.8%** on `ibm_kingston`). At 21Q and 22Q, the winning compiler depends on the target QPU, demonstrating why joint `(Compiler, QPU)` arbitration is required in production.
- **Offline Cryptographic Verification:** Every hardware execution in this repository is packaged with raw IBM Quantum job metadata, bitstring payloads, and SHA-256 digests verified by `Fez_Marrakesh_Kingston/3_verify_and_view.py`.

> [!NOTE]
> **Metric & Direction Conventions:**
> - **Classical Computational-Basis Distribution Overlap (F_B, ↑ higher is better):** Throughout this repository (`fidelity` in JSON ledgers and `"State Fidelity"` in Studio UI screenshots), values report F_B(P_ideal, P_meas) = Σ_x √(P_ideal(x) · P_meas(x)) = √F_H (where F_H = F_B² is Squared Hellinger Fidelity). Both evaluate computational-basis measurement distributions from shot counts and are distinct from 4ⁿ state tomography.
> - **Total Variation Distance (TVD, ↓ lower is better):** 0.5 · Σ_x |P_ideal(x) - P_meas(x)|.
> - **Linear Cross-Entropy Benchmarking (XEB, ↑ higher is better):** 2ⁿ · Σ_x P_ideal(x) · P_meas(x) - 1.
> - **Heavy-Output Probability (HOP, ↑ higher is better):** Measured probability mass on bitstrings exceeding the median of P_ideal(x).

### Table 1: 20Q-22Q Multi-QPU Broadcast Summary (9 Jobs, 27 Circuits, 442,368 Shots)

| Workload Width | Target Processor | SABRE O3 Fidelity F_B (↑) | TKET Fidelity F_B (↑) | Prometheus Fidelity F_B (↑) | Best Strategy on Target QPU | Cross-QPU Arbitrated Winner for Width |
| :---: | :--- | ---: | ---: | ---: | :--- | :--- |
| **20Q Dense (K_20)** | `ibm_fez` | 0.0227 | 0.0022 | **0.0357** | Prometheus (+57.4% vs. SABRE) | `ibm_kingston` (**0.0981** Prometheus, 2.75x vs. Fez) |
| **20Q Dense (K_20)** | `ibm_kingston` | 0.0249 | 0.0021 | **0.0981** | **Prometheus (+293.8% vs. SABRE)** | **`ibm_kingston` (0.0981 Prometheus, 2.75x vs. Fez)** |
| **20Q Dense (K_20)** | `ibm_marrakesh` | 0.0293 | 0.0067 | **0.0577** | Prometheus (+97.3% vs. SABRE) | `ibm_kingston` (**0.0981** Prometheus, 1.70x vs. Marrakesh) |
| **21Q Dense (K_21)** | `ibm_fez` | 0.0133 | 0.0012 | **0.0345** | Prometheus (+159.4% vs. SABRE) | `ibm_kingston` (**0.1059** SABRE) / `ibm_marrakesh` (**0.0904** Prom) |
| **21Q Dense (K_21)** | `ibm_kingston` | **0.1059** | 0.0020 | 0.0813 | **SABRE O3 (+30.3% vs. Prom)** | **`ibm_kingston` (0.1059 SABRE / 0.0904 Prom on Marrakesh)** |
| **21Q Dense (K_21)** | `ibm_marrakesh` | 0.0641 | 0.0136 | **0.0904** | Prometheus (+41.0% vs. SABRE) | `ibm_kingston` (**0.1059** SABRE) / `ibm_marrakesh` (**0.0904** Prom) |
| **22Q Dense (K_22)** | `ibm_fez` | 0.0002 | 0.0005 | **0.0275** | Prometheus (55.0x vs. TKET) | `ibm_marrakesh` (**0.1036** SABRE) / `ibm_kingston` (**0.0944** Prom) |
| **22Q Dense (K_22)** | `ibm_kingston` | 0.0636 | 0.0003 | **0.0944** | Prometheus (+48.4% vs. SABRE) | `ibm_marrakesh` (**0.1036** SABRE) / `ibm_kingston` (**0.0944** Prom) |
| **22Q Dense (K_22)** | `ibm_marrakesh` | **0.1036** | 0.0021 | 0.0815 | **SABRE O3 (+27.1% vs. Prom)** | **`ibm_marrakesh` (0.1036 SABRE / 0.0944 Prom on Kingston)** |

![20Q IBM Kingston metric chart](github_images/Screenshot%20%281447%29.png)

*Figure 1: 20-Qubit Dense All-to-All (K_20) 3-Way Comparative Execution on `ibm_kingston` (16,384 shots/compiler, 49,152 total job shots; Classical Distribution Fidelity F_B: SABRE O3 = 0.0249, TKET = 0.0021, Prometheus = 0.0981; source archive: [`Fez_Marrakesh_Kingston/`](Fez_Marrakesh_Kingston/)).*

---

## 2. Visual Walkthrough: 20-Qubit Dense All-to-All (K_20) Broadcast Across 3 Heron QPUs

All three executions below compile the same 20-qubit dense all-to-all logical workload (39 logical depth, 230 logical gates, 16,384 shots/compiler, 49,152 shots/job; source package: [`Fez_Marrakesh_Kingston/`](Fez_Marrakesh_Kingston/)).

### 2A. Target Processor: `ibm_fez` (Job `dah7efb9k43c73aedfp0`, 20Q Dense All-to-All, 16,384 Shots/Compiler)

| Target QPU | Metric & Direction | SABRE O3 | TKET | Prometheus | Prometheus vs. Best Baseline |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `ibm_fez` | Distribution Fidelity F_B (↑) | 0.0227 | 0.0022 | **0.0357** | **+57.37%** |
| `ibm_fez` | Total Variation Distance TVD (↓) | 0.9193 | 0.9779 | **0.8960** | **-2.54%** |
| `ibm_fez` | Heavy-Output Probability HOP (↑) | 0.5389 | 0.5264 | **0.5430** | **+0.77%** |
| `ibm_fez` | Cross-Entropy XEB (↑) | 20.0724 | 2.6434 | **27.1090** | **+35.06%** |
| `ibm_fez` | Shannon Entropy H (bits) | 13.9381 | 13.9716 | **13.9213** | **-0.12%** |
| `ibm_fez` | Compiled Circuit Depth (↓) | 390 | 596 | **315** | **-19.23%** |
| `ibm_fez` | Two-Qubit CZ Gates (↓) | 474 | 799 | **405** | **-14.56%** |

<details>
<summary><strong>View <code>ibm_fez</code> Studio Screenshots (Figures 2a-2d)</strong></summary>

![20Q IBM Fez measured results](github_images/Screenshot%20%281440%29.png)

*Figure 2a: `ibm_fez` 20Q Dense All-to-All (Job ID: `dah7efb9k43c73aedfp0`, 16,384 shots/compiler) - Measured Execution Results (F_B: 0.0227 SABRE / 0.0022 TKET / 0.0357 Prometheus; TVD: 0.9193 / 0.9779 / 0.8960; XEB: 20.0724 / 2.6434 / 27.1090).*

![20Q IBM Fez hardware allocation](github_images/Screenshot%20%281441%29.png)

*Figure 2b: `ibm_fez` 20Q Dense All-to-All - Physical 156-Qubit Hardware Allocation View.*

![20Q IBM Fez structural comparison](github_images/Screenshot%20%281442%29.png)

*Figure 2c: `ibm_fez` 20Q Dense All-to-All - Compiled Circuit Structural Comparison (Depth: 390 SABRE / 596 TKET / 315 Prometheus; 2Q Gates: 474 / 799 / 405).*

![20Q IBM Fez metric chart](github_images/Screenshot%20%281443%29.png)

*Figure 2d: `ibm_fez` 20Q Dense All-to-All - Comparative Observable Chart (16,384 shots/compiler).*

</details>

### 2B. Target Processor: `ibm_kingston` (Job `dah7efgmhr3c73e665g0`, 20Q Dense All-to-All, 16,384 Shots/Compiler)

| Target QPU | Metric & Direction | SABRE O3 | TKET | Prometheus | Prometheus vs. Best Baseline |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `ibm_kingston` | Distribution Fidelity F_B (↑) | 0.0249 | 0.0021 | **0.0981** | **+293.81%** |
| `ibm_kingston` | Total Variation Distance TVD (↓) | 0.9147 | 0.9789 | **0.8089** | **-11.57%** |
| `ibm_kingston` | Heavy-Output Probability HOP (↑) | 0.5236 | 0.4880 | **0.6176** | **+17.95%** |
| `ibm_kingston` | Cross-Entropy XEB (↑) | 19.7459 | 2.1115 | **58.1474** | **+194.48%** |
| `ibm_kingston` | Shannon Entropy H (bits) | 13.9276 | 13.9434 | **13.8115** | **-0.83%** |
| `ibm_kingston` | Compiled Circuit Depth (↓) | 512 | 596 | **315** | **-38.48%** |
| `ibm_kingston` | Two-Qubit CZ Gates (↓) | 600 | 799 | **409** | **-31.83%** |

<details>
<summary><strong>View <code>ibm_kingston</code> Studio Screenshots (Figures 3a-3d)</strong></summary>

![20Q IBM Kingston measured results](github_images/Screenshot%20%281444%29.png)

*Figure 3a: `ibm_kingston` 20Q Dense All-to-All (Job ID: `dah7efgmhr3c73e665g0`, 16,384 shots/compiler) - Measured Execution Results (F_B: 0.0249 SABRE / 0.0021 TKET / 0.0981 Prometheus; TVD: 0.9147 / 0.9789 / 0.8089; XEB: 19.7459 / 2.1115 / 58.1474).*

![20Q IBM Kingston hardware allocation](github_images/Screenshot%20%281445%29.png)

*Figure 3b: `ibm_kingston` 20Q Dense All-to-All - Physical 156-Qubit Hardware Allocation View.*

![20Q IBM Kingston structural comparison](github_images/Screenshot%20%281446%29.png)

*Figure 3c: `ibm_kingston` 20Q Dense All-to-All - Compiled Circuit Structural Comparison (Depth: 512 SABRE / 596 TKET / 315 Prometheus; 2Q Gates: 600 / 799 / 409).*

![20Q IBM Kingston metric chart](github_images/Screenshot%20%281447%29.png)

*Figure 3d: `ibm_kingston` 20Q Dense All-to-All - Comparative Observable Chart (16,384 shots/compiler).*

</details>

### 2C. Target Processor: `ibm_marrakesh` (Job `dah7ekgmhr3c73e665kg`, 20Q Dense All-to-All, 16,384 Shots/Compiler)

| Target QPU | Metric & Direction | SABRE O3 | TKET | Prometheus | Prometheus vs. Best Baseline |
| :--- | :--- | ---: | ---: | ---: | ---: |
| `ibm_marrakesh` | Distribution Fidelity F_B (↑) | 0.0293 | 0.0067 | **0.0577** | **+97.34%** |
| `ibm_marrakesh` | Total Variation Distance TVD (↓) | 0.9032 | 0.9578 | **0.8609** | **-4.69%** |
| `ibm_marrakesh` | Heavy-Output Probability HOP (↑) | 0.5388 | 0.5381 | **0.5758** | **+6.86%** |
| `ibm_marrakesh` | Cross-Entropy XEB (↑) | 19.4430 | 7.6657 | **38.1583** | **+96.26%** |
| `ibm_marrakesh` | Shannon Entropy H (bits) | 13.9112 | 13.9549 | **13.8697** | **-0.30%** |
| `ibm_marrakesh` | Compiled Circuit Depth (↓) | 337 | 596 | **300** | **-10.98%** |
| `ibm_marrakesh` | Two-Qubit CZ Gates (↓) | 439 | 799 | **396** | **-9.79%** |

<details>
<summary><strong>View <code>ibm_marrakesh</code> Studio Screenshots (Figures 4a-4d)</strong></summary>

![20Q IBM Marrakesh measured results](github_images/Screenshot%20%281448%29.png)

*Figure 4a: `ibm_marrakesh` 20Q Dense All-to-All (Job ID: `dah7ekgmhr3c73e665kg`, 16,384 shots/compiler) - Measured Execution Results (F_B: 0.0293 SABRE / 0.0067 TKET / 0.0577 Prometheus; TVD: 0.9032 / 0.9578 / 0.8609; XEB: 19.4430 / 7.6657 / 38.1583).*

![20Q IBM Marrakesh hardware allocation](github_images/Screenshot%20%281449%29.png)

*Figure 4b: `ibm_marrakesh` 20Q Dense All-to-All - Physical 156-Qubit Hardware Allocation View.*

![20Q IBM Marrakesh structural comparison](github_images/Screenshot%20%281450%29.png)

*Figure 4c: `ibm_marrakesh` 20Q Dense All-to-All - Compiled Circuit Structural Comparison (Depth: 337 SABRE / 596 TKET / 300 Prometheus; 2Q Gates: 439 / 799 / 396).*

![20Q IBM Marrakesh metric chart](github_images/Screenshot%20%281451%29.png)

*Figure 4d: `ibm_marrakesh` 20Q Dense All-to-All - Comparative Observable Chart (16,384 shots/compiler).*

</details>

---

## 3. Cryptographic Evidence Integrity & Reproducibility

Every hardware execution in this repository is packaged with its raw IBM Quantum job metadata, measurement payloads, and SHA-256 cryptographic digests:

```bash
python Fez_Marrakesh_Kingston/3_verify_and_view.py
```

- [`RESULTS.md`](RESULTS.md) - Consolidated multi-QPU broadcast tables and analysis.
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) & [`REPOSITORY_SHA256SUMS.txt`](REPOSITORY_SHA256SUMS.txt) - Complete IBM Quantum Job ID, ZIP package, and SHA-256 inventory.
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) & [`docs/HASHING_AND_INTEGRITY.md`](docs/HASHING_AND_INTEGRITY.md) - Step-by-step SHA-256 verification workflow.
- [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) - Field definitions and metric conventions.

---

## 4. Prometheus Dynamics Public Repository Portfolio (9 repositories | 248 benchmark jobs | 5,110 physical circuits/PUBs | 13,264,640 physical shots)

**Portfolio Totals:** 9 Verified Repositories | 248 Completed Benchmark Jobs/Tasks (167 IBM Heron Jobs, 22 AWS Braket Tasks, 59 IQM Resonance Jobs) | 5,110 Physical Circuits/PUBs | 13,264,640 Physical Measurement Shots

Counts refer to completed public benchmark executions, excluding simulations, classical GPU runs, unrecovered queue dispatches, and two setup smoke tests. Shared datasets are counted once (`IBM-Heron-156Q-Benchmarks` includes the 4-job 144-circuit pre-committed suite, and `Hybrid-Quantum-HPC-Benchmarks` includes all 33 archived job ZIPs from `qpu-selection-execution-quality`).

| Repository | Scope & Empirical Dataset | Primary Verification Artifacts |
| :--- | :--- | :--- |
| **[`IQM-Resonance-Spatial-Multiplexing`](https://github.com/PrometheusDynamicsCanada/IQM-Resonance-Spatial-Multiplexing)** | **IQM Emerald (54Q) Dense-Circuit Optimization & Spatial Multiplexing:** 59 scored hardware jobs (1,479 physical circuits/PUBs, 1,935 workload evaluations, 1,135,616 physical shots): 19-job Dense-Circuit Optimization, Odd/Even Parity, & Matched-Placement Campaign (739 circuits, 756,736 shots, **+3.73%** vs. SABRE K8, **+7.57%** vs. Pure TKET K8, **16/16** matched-placement wins) + 40-job Spatial Multiplexing & Prospective Scheduler Campaign (740 PUBs, 1,196 evaluations, **3.30x** 4-Way throughput). | [`data/dense_campaign_stages2_3_4_results.json`](https://github.com/PrometheusDynamicsCanada/IQM-Resonance-Spatial-Multiplexing/blob/main/data/dense_campaign_stages2_3_4_results.json), [`data/stage2_emerald_replication_results.json`](https://github.com/PrometheusDynamicsCanada/IQM-Resonance-Spatial-Multiplexing/blob/main/data/stage2_emerald_replication_results.json), [`scripts/verify_iqm_resonance_ledger.py`](https://github.com/PrometheusDynamicsCanada/IQM-Resonance-Spatial-Multiplexing/blob/main/scripts/verify_iqm_resonance_ledger.py) |
| **[`Quantum-Execution-Manager-Spatial-Multiplexing`](https://github.com/PrometheusDynamicsCanada/Quantum-Execution-Manager-Spatial-Multiplexing)** | **IBM Heron 8-Way Spatial Multiplexing & Multi-Compiler Meta-Selection:** 19 completed hardware jobs (586 physical PUBs, 1,140 workload evaluations, 655,360 physical shots) across `ibm_fez`, `ibm_marrakesh`, and `ibm_kingston` (**2.85x** qualifying workloads per billed second, **-57.1%** billed time, and SABRE/TKET/Prometheus interoperability). | [`data/campaign3_compiler_interoperability_results.json`](https://github.com/PrometheusDynamicsCanada/Quantum-Execution-Manager-Spatial-Multiplexing/blob/main/data/campaign3_compiler_interoperability_results.json), [`scripts/verify_spatial_multiplexing_campaigns.py`](https://github.com/PrometheusDynamicsCanada/Quantum-Execution-Manager-Spatial-Multiplexing/blob/main/scripts/verify_spatial_multiplexing_campaigns.py) |
| **[`IBM-Heron-Extended-Validation-1023-Circuits`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-Extended-Validation-1023-Circuits)** | **4-Pillar Extended IBM Heron r2 Validation (1,023 Circuits):** 17 batch jobs (1,023 physical circuits, 1,047,552 physical shots) across `ibm_marrakesh`, `ibm_fez`, and `ibm_kingston` (**+3.27%** mean F_B vs. SABRE O3 in Pillar 1A, **+6.67%** F_H with QPU dispatch, and 8Q-101Q Clifford mirror scaling). | [`ALL_1023_CIRCUITS_RESULTS.csv`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-Extended-Validation-1023-Circuits/blob/main/ALL_1023_CIRCUITS_RESULTS.csv), [`scripts/verify_campaign.py`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-Extended-Validation-1023-Circuits/blob/main/scripts/verify_campaign.py) |
| **[`AWS-Braket-Multi-Window-Validation`](https://github.com/PrometheusDynamicsCanada/AWS-Braket-Multi-Window-Validation)** | **Rigetti Cepheus-1-108Q 3-Window Replication & Cross-Provider Comparison:** 10 AWS Braket `ProgramSet` tasks (450 physical circuits, 460,800 physical shots) across 3 calibration windows (**+3.91%** vs. SABRE O3, p_Holm = 0.0112; **+9.03%** vs. TKET, p_Holm = 0.000641). | [`data/ALL_450_BRAKET_CIRCUITS_RESULTS.csv`](https://github.com/PrometheusDynamicsCanada/AWS-Braket-Multi-Window-Validation/blob/main/data/ALL_450_BRAKET_CIRCUITS_RESULTS.csv), [`scripts/verify_braket_campaign.py`](https://github.com/PrometheusDynamicsCanada/AWS-Braket-Multi-Window-Validation/blob/main/scripts/verify_braket_campaign.py) |
| **[`IBM-Heron-156Q-Benchmarks`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-156Q-Benchmarks)** | **156Q Heron r2 Scaling & Pre-Committed Suite:** 10 packed `SamplerV2` batch jobs (441 physical circuits, 755,712 shots) across `ibm_fez`, `ibm_marrakesh`, and `ibm_kingston` covering 3Q-13Q odd/even parity scaling, a 15-algorithm matrix at 9Q (297 circuits), and the 144-execution pre-committed validation suite (4 jobs). | [`data/heron_156q_99tournaments_297circuits.csv`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-156Q-Benchmarks/blob/main/data/heron_156q_99tournaments_297circuits.csv), [`validation_suite_144_executions/`](https://github.com/PrometheusDynamicsCanada/IBM-Heron-156Q-Benchmarks/tree/main/validation_suite_144_executions), `scripts/verify_ledger.py` |
| **[`Hybrid-Quantum-HPC-Benchmarks`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks)** | **Multi-Cloud QPU & Hybrid GPU Corpus:** 119 unique 3-way QPU jobs/tasks (357 physical circuits, 5,084,160 shots: 107 IBM Heron jobs / 321 circuits / 4,964,352 shots + 12 AWS Braket `ProgramSet` tasks / 36 circuits / 119,808 shots), plus the shared 144-execution pre-committed suite and 150 NVIDIA H100 (`VeloxQH100_1`) QUBO runs (4 to 1,029 variables). | [`aws_braket_qpu_12_jobs_ledger.json`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks/blob/main/aws_braket_qpu_12_jobs_ledger.json), [`ibm_heron_156q_verified_benchmarks.json`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks/blob/main/ibm_heron_156q_verified_benchmarks.json), [`validation_suite_144_executions/`](https://github.com/PrometheusDynamicsCanada/Hybrid-Quantum-HPC-Benchmarks/tree/main/validation_suite_144_executions), `verify_corpus_and_schedules.py` |
| **[`qpu-selection-execution-quality`](https://github.com/PrometheusDynamicsCanada/qpu-selection-execution-quality)** | **Cryptographic Provenance & Cross-QPU Arbitration:** 33 archived IBM Quantum job ZIP bundles (99 physical circuits, 1,622,016 shots across 16Q-23Q in `Fez/`, `Kingston/`, `Marrakesh/`, and 20Q-22Q broadcast runs in `Fez_Marrakesh_Kingston/`, already counted in the 107-job historical IBM corpus) plus the shared 4-job 144-circuit pre-committed suite. | [`EVIDENCE_INDEX.md`](https://github.com/PrometheusDynamicsCanada/qpu-selection-execution-quality/blob/main/EVIDENCE_INDEX.md), [`REPOSITORY_SHA256SUMS.txt`](https://github.com/PrometheusDynamicsCanada/qpu-selection-execution-quality/blob/main/REPOSITORY_SHA256SUMS.txt), `Fez_Marrakesh_Kingston/3_verify_and_view.py` |
| **[`prometheus-quantum-telemetry`](https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry)** | **Mechanistic Operating Envelope (01-05):** 14 IBM Heron jobs (774 physical PUBs, 4,125,440 physical shots across all 14 archived `job-*-result.json` measurement arrays; 417 normalized circuit rows in `MASTER_RESULTS.csv` for Experiments 01-03) covering distributional concentration (100k shots/circuit), 40 randomized matched pairs, 3Q-10Q scaling boundaries, 13Q ground-state avoidance, and a 540-PUB (1,105,920-shot) 3-QPU mechanistic sweep. | [`IBM_JOB_EVIDENCE_INDEX.csv`](https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry/blob/main/IBM_JOB_EVIDENCE_INDEX.csv), [`MASTER_RESULTS.csv`](https://github.com/PrometheusDynamicsCanada/prometheus-quantum-telemetry/blob/main/MASTER_RESULTS.csv), `verify_sha256_evidence.py` |
| **[`prometheus-execution-intelligence`](https://github.com/PrometheusDynamicsCanada/prometheus-execution-intelligence)** | **System Architecture & Consolidated Multi-Cloud Index:** Multi-compiler candidate evaluation (SABRE O3, TKET, Prometheus), multi-QPU dispatch workflow, and 18-screenshot Studio visual gallery indexing the 248 completed benchmark jobs/tasks across 6 QPUs. | [`ARCHITECTURE.md`](https://github.com/PrometheusDynamicsCanada/prometheus-execution-intelligence/blob/main/ARCHITECTURE.md), [`SCREENSHOT_GALLERY.md`](https://github.com/PrometheusDynamicsCanada/prometheus-execution-intelligence/blob/main/SCREENSHOT_GALLERY.md) |
