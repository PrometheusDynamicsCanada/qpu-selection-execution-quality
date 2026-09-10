#!/usr/bin/env python3
import json, os, argparse

ALLOWED_ROOT_KEYS = [
    "job_id", "selected_qpu", "circuit_family", "shots_requested", 
    "timestamp", "logical_metrics", "circuit_metrics", 
    "physical_allocation", "qasm_codes", "raw_counts", 
    "physical_observables", "status"
]
ALLOWED_CIRCUIT_METRICS = [
    "sabre_depth", "tket_depth", "prometheus_depth",
    "sabre_2q_gates", "tket_2q_gates", "prometheus_2q_gates"
]

def sanitize():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, help="Path to the original ledger on the server")
    args = parser.parse_args()

    if not os.path.exists(args.raw):
        print(f"[!] Error: Could not find raw ledger at {args.raw}")
        return

    with open(args.raw, 'r') as f:
        raw_ledger = json.load(f)

    clean_records = []
    for record in raw_ledger:
        clean = {k: v for k, v in record.items() if k in ALLOWED_ROOT_KEYS}
        if "circuit_metrics" in clean:
            clean["circuit_metrics"] = {
                k: v for k, v in clean["circuit_metrics"].items() if k in ALLOWED_CIRCUIT_METRICS
            }
        clean_records.append(clean)

    with open("public_evidence_ledger.json", 'w') as f:
        json.dump(clean_records, f, indent=2)
        
    print(f"[+] Successfully sanitized {len(clean_records)} records.")
    print("[+] Saved clean data to: public_evidence_ledger.json")

if __name__ == "__main__":
    sanitize()