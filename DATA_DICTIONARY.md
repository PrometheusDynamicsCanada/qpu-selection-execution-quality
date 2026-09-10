# Data Dictionary

| Field | Meaning |
|---|---|
| `job_id` | IBM Quantum job identifier |
| `qpu` | IBM backend used for execution |
| `qubits` | Logical workload size |
| `shots` / `shots_per_circuit` | Number of measurements per compiler output |
| `sabre_2q_gates` | Two-qubit gate count for SABRE O3 output |
| `tket_2q_gates` | Two-qubit gate count for TKET output |
| `prometheus_2q_gates` | Two-qubit gate count for Prometheus output |
| `sabre_depth` | Circuit depth for SABRE output |
| `tket_depth` | Circuit depth for TKET output |
| `prometheus_depth` | Circuit depth for Prometheus output |
| `physical_observables` | Measured execution metrics from hardware |
| `fidelity` | Reported state-fidelity metric |
| `tvd` | Total variation distance |
| `xeb` | Cross-entropy benchmark metric |
| `entropy` | Shannon entropy shown for the physical execution |
| `hop` | Heavy-output probability |
| `physical_allocation` | Physical qubit assignment recorded for the execution |
| `qasm_codes` | Serialized submitted circuit representations where preserved |
| `raw_counts` | Preserved measurement counts where available |
| `sha256` | Cryptographic digest used for integrity verification |
