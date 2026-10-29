# Methodology

## Research question

The experiment asks whether the physical target QPU materially influences the execution quality of a quantum workload.

## Experimental design

Dense all-to-all circuit families are compiled using multiple strategies and executed on real IBM Quantum hardware. For the broadcast experiments, the same workload family is separately targeted to Fez, Kingston, and Marrakesh so that physical target is an explicit experimental variable.

The evidence records the compiler outputs, structural characteristics, physical allocations, measured execution observables, and IBM execution metadata.

## Recorded measurements

The repository preserves:

- two-qubit gate count;
- circuit depth;
- state fidelity;
- total variation distance (TVD);
- cross-entropy benchmarking (XEB);
- Shannon entropy;
- heavy-output probability (HOP); and
- reference metrics where supplied.

## Important interpretation

Structural metrics describe the submitted circuit. Physical observables describe what occurred when that circuit ran on actual hardware. These are related but not interchangeable.

The study therefore treats the QPU as an explicit experimental factor rather than assuming that a structural ranking alone predicts physical execution quality.

## Reproducibility boundary

This repository is an evidence/results repository. It exposes what was executed and what was observed without publishing the private internal implementation of Prometheus.
