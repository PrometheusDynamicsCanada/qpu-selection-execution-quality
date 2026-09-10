#!/usr/bin/env python3
"""
PROMETHEUS EVIDENCE FETCHER & CRYPTOGRAPHIC LOCK
================================================

Fetches IBM Quantum job evidence using the current IBM Quantum
Compute Service REST API.

For every job ID in public_evidence_ledger.json:

    1. Authenticates the IBM Cloud API key through IBM IAM.
    2. Fetches the raw IBM job metadata.
    3. Fetches the raw IBM final job result.
    4. Stores BOTH responses in a deterministic ZIP evidence package.
    5. Calculates SHA-256 of the final ZIP.
    6. Writes sha256sums.txt.

IMPORTANT:
- The IBM API key is NEVER written to disk.
- The temporary IAM bearer token is NEVER written to disk.
- Raw IBM API responses are preserved inside each ZIP.
- ZIP contents are written deterministically so the same retrieved
  evidence produces reproducible package structure.
"""

import os
import json
import hashlib
import requests
import argparse
import sys
import zipfile
from datetime import datetime, timezone


# ============================================================================
# CONFIGURATION
# ============================================================================

IAM_URL = "https://iam.cloud.ibm.com/identity/token"

DEFAULT_API_BASE = "https://quantum.cloud.ibm.com/api/v1"

# Current API version documented by IBM Quantum.
# Can be overridden with --api-version if IBM changes it later.
DEFAULT_API_VERSION = "2026-04-15"

CHUNK_SIZE = 8192
TIMEOUT = 30


# ============================================================================
# IBM IAM AUTHENTICATION
# ============================================================================

def get_ibm_bearer_token(api_key: str) -> str:
    """
    Exchange an IBM Cloud API key for a temporary IAM bearer token.
    """

    print("[*] Authenticating with IBM IAM...")

    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            IAM_URL,
            headers=headers,
            data=data,
            timeout=TIMEOUT,
        )

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Could not reach IBM IAM endpoint: {exc}"
        ) from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"IBM IAM authentication failed.\n"
            f"HTTP Status: {response.status_code}\n"
            f"Response: {response.text}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "IBM IAM returned a non-JSON response."
        ) from exc

    bearer_token = payload.get("access_token")

    if not bearer_token:
        raise RuntimeError(
            "IBM IAM authentication response contained no access_token.\n"
            f"Response keys: {list(payload.keys())}"
        )

    expires_in = payload.get("expires_in", "unknown")

    print("[+] IBM IAM authentication successful")
    print(f"[+] Temporary bearer token lifetime: {expires_in} seconds")

    return bearer_token


# ============================================================================
# API REQUESTS
# ============================================================================

def make_headers(
    bearer_token: str,
    service_crn: str,
    api_version: str
) -> dict:
    """
    Build required IBM Quantum API headers.
    """

    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}",
        "Service-CRN": service_crn,
        "IBM-API-Version": api_version,
    }


def fetch_raw_json(
    url: str,
    headers: dict,
    label: str
):
    """
    Fetch a raw JSON response from IBM.

    Returns:
        (json_object, raw_response_bytes)

    The raw bytes are preserved separately so the evidence package can
    contain exactly the HTTP response body received from IBM.
    """

    print(f"    [*] {label}")

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=TIMEOUT,
        )

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Network error while fetching {label}: {exc}"
        ) from exc

    # 204 means no result content exists.
    if response.status_code == 204:
        print(f"    [!] {label}: HTTP 204 - no content")

        return (
            {
                "_prometheus_fetch_status": 204,
                "_prometheus_note": "IBM returned HTTP 204 No Content",
            },
            b""
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"{label} failed.\n"
            f"HTTP Status: {response.status_code}\n"
            f"Response: {response.text}"
        )

    raw_bytes = response.content

    try:
        parsed = response.json()

    except ValueError as exc:
        raise RuntimeError(
            f"{label} returned HTTP 200 but the body was not valid JSON."
        ) from exc

    print(
        f"    [+] {label}: "
        f"{len(raw_bytes):,} raw bytes received"
    )

    return parsed, raw_bytes


# ============================================================================
# DETERMINISTIC EVIDENCE ZIP
# ============================================================================

def write_deterministic_file(
    zip_file: zipfile.ZipFile,
    filename: str,
    data: bytes
):
    """
    Write a file with a fixed ZIP timestamp and permissions.

    This prevents the ZIP metadata itself from introducing unnecessary
    timestamp variation into the evidence package.
    """

    info = zipfile.ZipInfo(filename)

    # ZIP timestamps cannot be earlier than 1980.
    # Fixed timestamp makes package structure deterministic.
    info.date_time = (1980, 1, 1, 0, 0, 0)

    # Regular file, read-only permissions.
    info.external_attr = 0o100444 << 16

    info.compress_type = zipfile.ZIP_DEFLATED

    zip_file.writestr(info, data)


def create_evidence_zip(
    job_id: str,
    job_raw: bytes,
    results_raw: bytes,
    metadata: dict,
    output_dir: str
) -> str:
    """
    Create the evidence ZIP.

    Returns the full path to the ZIP.
    """

    zip_path = os.path.join(
        output_dir,
        f"job-{job_id}.zip"
    )

    metadata_bytes = (
        json.dumps(
            metadata,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")

    with zipfile.ZipFile(
        zip_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:

        # Raw response bodies exactly as received from IBM.
        write_deterministic_file(
            zf,
            "job_details_raw.json",
            job_raw,
        )

        write_deterministic_file(
            zf,
            "job_results_raw.json",
            results_raw,
        )

        # Local manifest describing the retrieval.
        write_deterministic_file(
            zf,
            "evidence_metadata.json",
            metadata_bytes,
        )

    return zip_path


# ============================================================================
# HASHING
# ============================================================================

def sha256_file(path: str) -> str:
    """
    Calculate SHA-256 without loading the entire file into memory.
    """

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================================
# FETCH ONE JOB
# ============================================================================

def fetch_job(
    job_id: str,
    bearer_token: str,
    service_crn: str,
    api_base: str,
    api_version: str,
    output_dir: str
):
    """
    Fetch IBM job metadata and final results, package them, and hash them.
    """

    headers = make_headers(
        bearer_token=bearer_token,
        service_crn=service_crn,
        api_version=api_version,
    )

    job_url = f"{api_base}/jobs/{job_id}"
    results_url = f"{api_base}/jobs/{job_id}/results"

    try:
        # --------------------------------------------------------------------
        # Fetch raw IBM job details
        # --------------------------------------------------------------------

        job_json, job_raw = fetch_raw_json(
            job_url,
            headers,
            "Fetching IBM job details"
        )

        # --------------------------------------------------------------------
        # Fetch raw IBM final results
        # --------------------------------------------------------------------

        results_json, results_raw = fetch_raw_json(
            results_url,
            headers,
            "Fetching IBM job results"
        )

        # --------------------------------------------------------------------
        # Calculate hashes of the individual raw IBM response bodies
        # --------------------------------------------------------------------

        job_response_sha256 = hashlib.sha256(
            job_raw
        ).hexdigest()

        results_response_sha256 = hashlib.sha256(
            results_raw
        ).hexdigest()

        # --------------------------------------------------------------------
        # Build local retrieval metadata
        # --------------------------------------------------------------------

        metadata = {
            "format": "prometheus_ibm_quantum_evidence_v1",
            "job_id": job_id,
            "retrieved_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),

            "source": {
                "api_base": api_base,
                "job_details_endpoint": job_url,
                "job_results_endpoint": results_url,
                "ibm_api_version": api_version,
            },

            "raw_response_sha256": {
                "job_details_raw.json": job_response_sha256,
                "job_results_raw.json": results_response_sha256,
            },

            "response_status": {
                "job_details": 200,
                "job_results": (
                    204 if not results_raw else 200
                ),
            },

            "package_contents": [
                "job_details_raw.json",
                "job_results_raw.json",
                "evidence_metadata.json",
            ],
        }

        # --------------------------------------------------------------------
        # Create evidence package
        # --------------------------------------------------------------------

        zip_path = create_evidence_zip(
            job_id=job_id,
            job_raw=job_raw,
            results_raw=results_raw,
            metadata=metadata,
            output_dir=output_dir,
        )

        # --------------------------------------------------------------------
        # Hash final evidence package
        # --------------------------------------------------------------------

        package_sha256 = sha256_file(zip_path)

        return {
            "job_id": job_id,
            "zip_path": zip_path,
            "sha256": package_sha256,
            "job_response_sha256": job_response_sha256,
            "results_response_sha256": results_response_sha256,
            "job_json": job_json,
            "results_json": results_json,
        }

    except Exception as exc:
        print(f"    [!] Job {job_id} failed: {exc}")
        return None


# ============================================================================
# MAIN
# ============================================================================

def fetch():
    parser = argparse.ArgumentParser(
        description=(
            "Fetch IBM Quantum job evidence and create SHA-256 "
            "locked evidence packages."
        )
    )

    parser.add_argument(
        "--token",
        required=True,
        help="IBM Cloud API key",
    )

    parser.add_argument(
        "--service-crn",
        required=True,
        help=(
            "IBM Quantum Compute Service instance CRN"
        ),
    )

    parser.add_argument(
        "--api-base",
        default=DEFAULT_API_BASE,
        help=(
            "IBM Quantum API base URL. "
            f"Default: {DEFAULT_API_BASE}"
        ),
    )

    parser.add_argument(
        "--api-version",
        default=DEFAULT_API_VERSION,
        help=(
            "IBM API version header. "
            f"Default: {DEFAULT_API_VERSION}"
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=".",
        help=(
            "Directory for evidence ZIPs and manifests. "
            "Default: current directory"
        ),
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------------
    # Validate ledger
    # ------------------------------------------------------------------------

    ledger_path = "public_evidence_ledger.json"

    if not os.path.exists(ledger_path):
        print(
            "[!] Error: Run 1_sanitize_ledger.py first "
            "to generate public_evidence_ledger.json."
        )
        return

    try:
        with open(
            ledger_path,
            "r",
            encoding="utf-8"
        ) as f:
            ledger = json.load(f)

    except Exception as exc:
        print(
            f"[!] Could not read {ledger_path}: {exc}"
        )
        sys.exit(1)

    job_ids = []

    for record in ledger:
        job_id = record.get("job_id")

        if job_id:
            job_id = str(job_id).strip()

            if job_id:
                job_ids.append(job_id)

    # Remove duplicates while preserving ledger order.
    job_ids = list(dict.fromkeys(job_ids))

    if not job_ids:
        print(
            "[!] No valid job IDs found in "
            "public_evidence_ledger.json."
        )
        return

    # ------------------------------------------------------------------------
    # Prepare output directory
    # ------------------------------------------------------------------------

    os.makedirs(
        args.output_dir,
        exist_ok=True,
    )

    print("=" * 72)
    print("PROMETHEUS IBM QUANTUM EVIDENCE FETCHER")
    print("=" * 72)

    print(
        f"[*] Hardware records in ledger: "
        f"{len(job_ids)}"
    )

    print(
        f"[*] IBM API base: {args.api_base}"
    )

    print(
        f"[*] IBM API version: {args.api_version}"
    )

    print()

    # ------------------------------------------------------------------------
    # Authenticate
    # ------------------------------------------------------------------------

    try:
        bearer_token = get_ibm_bearer_token(
            args.token
        )

    except Exception as exc:
        print(f"\n[!] Authentication failed: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------------
    # Fetch all jobs
    # ------------------------------------------------------------------------

    manifest = []

    detailed_manifest = []

    successful = 0
    failed = 0

    print()
    print(
        f"[*] Initiating evidence fetch for "
        f"{len(job_ids)} IBM hardware records..."
    )
    print()

    for index, job_id in enumerate(
        job_ids,
        start=1
    ):

        print(
            f"[{index}/{len(job_ids)}] "
            f"Processing Job: {job_id}"
        )

        result = fetch_job(
            job_id=job_id,
            bearer_token=bearer_token,
            service_crn=args.service_crn,
            api_base=args.api_base.rstrip("/"),
            api_version=args.api_version,
            output_dir=args.output_dir,
        )

        if result:
            successful += 1

            filename = os.path.basename(
                result["zip_path"]
            )

            manifest.append(
                f"{result['sha256']} *{filename}"
            )

            detailed_manifest.append({
                "job_id": job_id,
                "package": filename,
                "package_sha256": result["sha256"],
                "job_details_raw_sha256":
                    result["job_response_sha256"],
                "job_results_raw_sha256":
                    result["results_response_sha256"],
            })

            print(
                f"    [+] LOCKED: {job_id}"
            )

            print(
                f"    [+] Package SHA-256: "
                f"{result['sha256']}"
            )

        else:
            failed += 1

        print()

    # ------------------------------------------------------------------------
    # Write manifests
    # ------------------------------------------------------------------------

    if manifest:

        sha256_manifest_path = os.path.join(
            args.output_dir,
            "sha256sums.txt"
        )

        with open(
            sha256_manifest_path,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            f.write("\n".join(manifest))
            f.write("\n")

        detailed_manifest_path = os.path.join(
            args.output_dir,
            "evidence_manifest.json"
        )

        evidence_manifest = {
            "format": "prometheus_evidence_manifest_v1",
            "generated_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "source_ledger": ledger_path,
            "total_jobs": len(job_ids),
            "successful_jobs": successful,
            "failed_jobs": failed,
            "records": detailed_manifest,
        }

        with open(
            detailed_manifest_path,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as f:
            json.dump(
                evidence_manifest,
                f,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            f.write("\n")

        print("=" * 72)
        print("[+] FETCH COMPLETE")
        print("=" * 72)
        print(
            f"[+] Successfully locked: {successful}"
        )
        print(
            f"[!] Failed: {failed}"
        )
        print(
            f"[+] SHA-256 manifest: "
            f"{sha256_manifest_path}"
        )
        print(
            f"[+] Detailed manifest: "
            f"{detailed_manifest_path}"
        )

    else:
        print()
        print(
            "[!] No evidence packages were created."
        )
        sys.exit(1)


if __name__ == "__main__":
    fetch()