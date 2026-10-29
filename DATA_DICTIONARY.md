# Data Dictionary & Metric Conventions

| Field | Type / Range | Definition |
| :--- | :--- | :--- |
| `job_id` | `string` (IBM Job ID) | Unique IBM Quantum hardware job identifier |
| `selected_qpu` / `qpu` | `string` | Target 156-qubit IBM Heron r2 processor (`ibm_fez`, `ibm_kingston`, `ibm_marrakesh`) |
| `qubits` | `integer` (`16` to `23`) | Logical workload width ($n$) |
| `shots_requested` / `shots` | `integer` (`16,384`) | Number of physical measurement shots per compiled circuit (`49,152` per 3-way job) |
| `sabre_depth`, `tket_depth`, `prometheus_depth` | `integer` ($\ge 1$) | Compiled physical circuit depth on the target processor |
| `sabre_2q_gates`, `tket_2q_gates`, `prometheus_2q_gates` | `integer` ($\ge 0$) | Compiled native two-qubit gate count (`CZ` / `ECR`) |
| `sabre_1q_gates`, `tket_1q_gates`, `prometheus_1q_gates` | `integer` ($\ge 0$) | Compiled single-qubit gate count |
| `sabre_total_gates`, `tket_total_gates`, `prometheus_total_gates` | `integer` ($\ge 1$) | Total compiled gate count (`1Q + 2Q`) |
| `sabre_swap_overhead`, `tket_swap_overhead`, `prometheus_swap_overhead` | `integer` ($\ge 0$) | Routing overhead relative to the unrouted logical circuit |
| `logical_depth`, `logical_2q_gates`, `logical_1q_gates`, `logical_total_gates` | `integer` ($\ge 1$) | Uncompiled logical input circuit structure |
| `physical_observables` | `object` | Measured hardware execution metrics computed from returned bitstring shot counts |
| `fidelity` (`sabre_fidelity`, `tket_fidelity`, `prometheus_fidelity`) | $[0, 1]$ (↑ higher is better) | **Classical Computational-Basis Distribution Fidelity (Bhattacharyya Overlap):** $F_B(P_{\text{ideal}}, P_{\text{meas}}) = \sum_{x \in \{0,1\}^n} \sqrt{P_{\text{ideal}}(x)\, P_{\text{meas}}(x)} = \sqrt{F_H}$, where $F_H = F_B^2$ is Squared Hellinger Fidelity. Note: In historical Studio UI screenshots (`github_images/`), this Z-basis distribution overlap is labeled `"State Fidelity"`; it measures computational-basis probability distribution overlap and not $4^n$ quantum state tomography. |
| `tvd` (`sabre_tvd`, `tket_tvd`, `prometheus_tvd`) | $[0, 1]$ (↓ lower is better) | **Total Variation Distance:** $\frac{1}{2}\sum_{x \in \{0,1\}^n} |P_{\text{ideal}}(x) - P_{\text{meas}}(x)|$ |
| `hop` (`sabre_hop`, `tket_hop`, `prometheus_hop`) | $[0, 1]$ (↑ higher is better) | **Heavy-Output Probability:** Total measured probability mass on bitstrings with ideal probability above the median of $P_{\text{ideal}}$ |
| `xeb` (`sabre_xeb`, `tket_xeb`, `prometheus_xeb`) | $\mathbb{R}$ (↑ higher is better) | **Linear Cross-Entropy Benchmarking:** $2^n \sum_{x \in \{0,1\}^n} P_{\text{ideal}}(x)\, P_{\text{meas}}(x) - 1$ |
| `entropy`, `ideal_entropy` | $[0, n]$ bits | **Shannon Entropy:** $-\sum_{x \in \{0,1\}^n} P(x)\log_2 P(x)$ of the measured (`entropy`) and ideal (`ideal_entropy`) distributions |
| `qasm_codes` | `object` (`logical`) | Unrouted logical OpenQASM 2.0 benchmark circuit definition |
| `raw_counts` | `object` | Preserved hardware bitstring measurement counts per compiler |
| `sha256` | `string` (64-char hex) | SHA-256 cryptographic digest used for package integrity verification |
