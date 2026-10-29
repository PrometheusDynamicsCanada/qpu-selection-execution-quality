#!/usr/bin/env python3
"""
PROMETHEUS PUBLIC LEDGER SANITIZER
==================================
Produces the sanitized public derivative `public_evidence_ledger.json` from an
internal benchmark ledger by:
  - Retaining only approved root fields (`physical_allocation` is excluded).
  - Retaining only structural gate/depth metrics (`circuit_metrics`).
  - Retaining only the unrouted logical circuit definition (`qasm_codes.logical`),
    excluding compiled physical OpenQASM trajectories (`prometheus`, `sabre`, `tket`).
"""
import json, os, argparse

ALLOWED_ROOT_KEYS = [
    "job_id", "selected_qpu", "circuit_family", "shots_requested",
    "timestamp", "logical_metrics", "circuit_metrics",
    "qasm_codes", "raw_counts", "physical_observables", "status"
]
ALLOWED_CIRCUIT_METRICS = [
    "sabre_depth", "tket_depth", "prometheus_depth",
    "sabre_2q_gates", "tket_2q_gates", "prometheus_2q_gates"
]
ALLOWED_QASM_KEYS = [
    "logical"
]

def sanitize():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="Path to the original ledger on the server")
    args = parser.parse_args()

    if not os.path.exists(args.raw):
        print(f"[!] Error: Could not find raw ledger at {args.raw}")
        return

    with open(args.raw, "r", encoding="utf-8") as f:
        raw_ledger = json.load(f)

    clean_records = []
    for record in raw_ledger:
        clean = {k: v for k, v in record.items() if k in ALLOWED_ROOT_KEYS}
        if "circuit_metrics" in clean and isinstance(clean["circuit_metrics"], dict):
            clean["circuit_metrics"] = {
                k: v for k, v in clean["circuit_metrics"].items() if k in ALLOWED_CIRCUIT_METRICS
            }
        if "qasm_codes" in clean and isinstance(clean["qasm_codes"], dict):
            clean["qasm_codes"] = {
                k: v for k, v in clean["qasm_codes"].items() if k in ALLOWED_QASM_KEYS
            }
        clean_records.append(clean)

    with open("public_evidence_ledger.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(clean_records, f, indent=2)
        f.write("\n")

    print(f"[+] Successfully sanitized {len(clean_records)} records.")
    print("[+] Saved clean data to: public_evidence_ledger.json")

if __name__ == "__main__":
    sanitize()
