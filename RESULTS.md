# Results

## Primary finding

The experimental results support a clear conclusion for the workloads studied:

> **The target QPU materially affects observed quantum execution quality.**

The effect is visible both in absolute physical observables and in the relative performance of the compilation strategies.

## 20Q multi-QPU broadcast

The 20Q broadcast provides the easiest side-by-side example because the same workload family was sent to all three target QPUs.

| QPU | SABRE fidelity | TKET fidelity | Prometheus fidelity | Prometheus vs best | Prometheus wins? |
|---|---:|---:|---:|---:|---|
| Fez | 0.0227 | 0.0022 | **0.0357** | +57.4% | Yes |
| Kingston | 0.0249 | 0.0021 | **0.0981** | +293.8% | Yes |
| Marrakesh | 0.0293 | 0.0067 | **0.0577** | +97.3% | Yes |

The three Prometheus fidelity values differ by a factor of roughly 2.75 between the lowest and highest observed result. The important point is not that Prometheus wins these three cases; it is that **the same logical workload produces materially different physical outcomes depending on the target QPU**.

### 20Q secondary observables

| QPU | Prometheus TVD | Prometheus XEB |
|---|---:|---:|
| Fez | 0.8960 | 27.1090 |
| Kingston | 0.8089 | 58.1474 |
| Marrakesh | 0.8609 | 38.1583 |

## 21Q multi-QPU broadcast

| QPU | SABRE fidelity | TKET fidelity | Prometheus fidelity |
|---|---:|---:|---:|
| Fez | 0.0133 | 0.0012 | **0.0345** |
| Kingston | **0.1059** | 0.0020 | 0.0813 |
| Marrakesh | 0.0641 | 0.0136 | **0.0904** |

Here the relative winner changes with the QPU. Prometheus is ahead on Fez and Marrakesh, while SABRE is ahead on Kingston.

## 22Q multi-QPU broadcast

| QPU | SABRE fidelity | TKET fidelity | Prometheus fidelity |
|---|---:|---:|---:|
| Fez | 0.0002 | 0.0005 | **0.0275** |
| Kingston | 0.0636 | 0.0003 | **0.0944** |
| Marrakesh | **0.1036** | 0.0021 | 0.0815 |

Again, the relative outcome changes by physical target.

## Historical scaling study

The repository also preserves earlier 16Q–23Q sweeps across Fez, Kingston, and Marrakesh. These records provide a broader context for the broadcast experiments and contain cases where structural metrics and measured physical outcomes do not rank the strategies identically.

## Structural vs physical results

The data should not be interpreted as a simple gate-count contest. The repository records:

- two-qubit gate count;
- circuit depth;
- state fidelity;
- total variation distance;
- cross-entropy benchmarking; and
- additional observables including entropy and HOP.

The presence of cases where a structurally shorter circuit does not yield the best physical result is part of the motivation for studying the execution environment explicitly.

## Evidence status

The supplied broadcast set contains 9 IBM hardware jobs across the three target QPUs and 20Q–22Q. All nine evidence packages were successfully locked and verified in the supplied verification output.
