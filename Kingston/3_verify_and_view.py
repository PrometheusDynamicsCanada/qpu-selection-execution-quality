#!/usr/bin/env python3

import csv
import hashlib
import json
import os
import zipfile
from datetime import datetime, timezone


# ============================================================================
# CONFIGURATION
# ============================================================================

LEDGER_PATH = "public_evidence_ledger.json"
SHA256_MANIFEST = "sha256sums.txt"
EVIDENCE_MANIFEST = "evidence_manifest.json"

OUTPUT_CSV = "master_results.csv"
OUTPUT_EVIDENCE_CSV = "evidence_verification.csv"

# Directional metrics.
# These are only used for automatic "vs best" and "beats both" comparisons.
HIGHER_IS_BETTER = {
    "fidelity": True,
    "xeb": True,
}

LOWER_IS_BETTER = {
    "tvd": True,
}

# These are reference/context metrics, not strategy-ranking metrics.
REFERENCE_METRICS = {
    "ideal_entropy",
}


# ============================================================================
# BASIC FORMATTING
# ============================================================================

def print_sep(char="=", length=150):
    print(char * length)


def numeric(value):
    try:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def fmt(value, decimals=4):
    """Consistent numeric display."""
    if value in ("--", "N/A", "", None):
        return "N/A"

    n = numeric(value)

    if n is None:
        return str(value)

    return f"{n:.{decimals}f}"


def fmt_int(value):
    if value in ("--", "N/A", "", None):
        return "N/A"

    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value)


def pretty_metric_name(metric):
    return metric.replace("_", " ").upper()


# ============================================================================
# COMPARISONS
# ============================================================================

def format_delta(prom, sabre, tket, higher_is_better=True):
    """
    Percentage change of Prometheus relative to the stronger SABRE/TKET
    baseline.

    For higher-is-better:
        positive = Prometheus is higher

    For lower-is-better:
        negative = Prometheus is lower
    """
    p = numeric(prom)
    s = numeric(sabre)
    t = numeric(tket)

    if p is None or s is None or t is None:
        return "N/A"

    baseline = max(s, t) if higher_is_better else min(s, t)

    if baseline == 0:
        return "N/A"

    delta = ((p - baseline) / abs(baseline)) * 100

    return f"({'+' if delta > 0 else ''}{delta:.1f}%)"


def better_than_baselines(prom, sabre, tket, higher_is_better=True):
    """
    Whether Prometheus beats both baselines.

    Returns:
        YES
        TIE
        NO
        N/A
    """
    p = numeric(prom)
    s = numeric(sabre)
    t = numeric(tket)

    if p is None or s is None or t is None:
        return "N/A"

    if higher_is_better:
        if p > s and p > t:
            return "YES"
        if p >= s and p >= t:
            return "TIE"
    else:
        if p < s and p < t:
            return "YES"
        if p <= s and p <= t:
            return "TIE"

    return "NO"


def absolute_error(value, reference):
    """
    Absolute distance from a reference value.

    Used for ideal_entropy display only.
    """
    v = numeric(value)
    r = numeric(reference)

    if v is None or r is None:
        return None

    return abs(v - r)


def parse_iso_datetime(value):
    """Return a normalized UTC timestamp string when possible."""
    if not value:
        return "N/A"

    try:
        raw = str(value).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        dt = dt.astimezone(timezone.utc)

        return dt.isoformat().replace("+00:00", "Z")

    except (ValueError, TypeError):
        return str(value)


def extract_ibm_execution_info(job_id, sha_manifest=None, detailed_manifest=None):
    """
    Read the preserved IBM job evidence and derive the actual PUB/circuit
    shot execution information.

    IBM Runtime job details expose:
        params.options.default_shots

    and job results expose execution_spans/data_slices. In the supplied
    evidence each PUB has a 16,384-shot data slice and there are three PUBs,
    corresponding to the three strategy circuits represented in the ledger.
    """

    zip_path = f"job-{job_id}.zip"

    info = {
        "shots_per_circuit": None,
        "circuits_per_job": None,
        "total_shots_executed": None,
        "ibm_created_utc": "N/A",
        "execution_start_utc": "N/A",
        "execution_stop_utc": "N/A",
    }

    if not os.path.exists(zip_path):
        return info

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            job_details = json.loads(
                z.read("job_details_raw.json").decode("utf-8")
            )

            results = json.loads(
                z.read("job_results_raw.json").decode("utf-8")
            )

        info["ibm_created_utc"] = parse_iso_datetime(
            job_details.get("created")
        )

        default_shots = numeric(
            (
                job_details.get("params", {})
                or {}
            ).get("options", {})
             .get("default_shots")
        )

        pub_count = None
        slice_shots = []

        # Count PUB results and inspect execution data_slices.
        if isinstance(results, dict):
            value = results.get("__value__", {}) or {}

            pub_results = value.get(
                "pub_results",
                []
            )

            if isinstance(pub_results, list):
                pub_count = len(pub_results)

            metadata = value.get(
                "metadata",
                {}
            ) or {}

            execution = metadata.get(
                "execution",
                {}
            ) or {}

            spans = (
                execution.get(
                    "execution_spans",
                    {}
                )
                or {}
            ).get(
                "__value__",
                {}
            ) or {}

            # execution_spans may contain multiple spans; collect the
            # data_slices from all of them.
            for span in spans.get("spans", []) or []:

                span_value = (
                    span.get("__value__", {})
                    if isinstance(span, dict)
                    else {}
                )

                data_slices = span_value.get(
                    "data_slices",
                    {}
                ) or {}

                for _, slice_value in data_slices.items():

                    if (
                        isinstance(slice_value, list)
                        and len(slice_value) >= 5
                    ):
                        # Last field is the number of shots in this slice.
                        shot_count = numeric(
                            slice_value[-1]
                        )

                        if shot_count is not None:
                            slice_shots.append(
                                int(shot_count)
                            )

                start = span_value.get("start", {}) or {}
                stop = span_value.get("stop", {}) or {}

                if isinstance(start, dict):
                    start = start.get("__value__")

                if isinstance(stop, dict):
                    stop = stop.get("__value__")

                if start:
                    info["execution_start_utc"] = parse_iso_datetime(start)

                if stop:
                    info["execution_stop_utc"] = parse_iso_datetime(stop)

        # Strongest shot-per-circuit value is the actual execution slice.
        if slice_shots:
            # In this job structure there is one slice per PUB/circuit.
            info["shots_per_circuit"] = slice_shots[0]
            info["circuits_per_job"] = (
                len(slice_shots)
                if len(slice_shots) > 0
                else pub_count
            )

            info["total_shots_executed"] = sum(
                slice_shots
            )

        elif default_shots is not None and pub_count:
            # Fallback to the IBM job's default shots and PUB count.
            info["shots_per_circuit"] = int(default_shots)
            info["circuits_per_job"] = int(pub_count)
            info["total_shots_executed"] = int(
                default_shots * pub_count
            )

        elif default_shots is not None:
            info["shots_per_circuit"] = int(default_shots)

        return info

    except (
        OSError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        zipfile.BadZipFile,
    ):
        return info


# ============================================================================
# CRYPTOGRAPHIC EVIDENCE VERIFICATION
# ============================================================================

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def load_sha256_manifest(path=SHA256_MANIFEST):
    """
    Read:
        <sha256> *<filename>
    """
    manifest = {}

    if not os.path.exists(path):
        return manifest

    try:
        with open(path, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                parts = line.split(maxsplit=1)

                if len(parts) != 2:
                    continue

                digest, filename = parts

                if filename.startswith("*"):
                    filename = filename[1:]

                manifest[os.path.basename(filename)] = (
                    digest.lower()
                )

    except OSError:
        return {}

    return manifest


def load_detailed_manifest(path=EVIDENCE_MANIFEST):
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        return {
            record.get("job_id"): record
            for record in payload.get("records", [])
            if record.get("job_id")
        }

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
    ):
        return {}


def inspect_evidence(
    job_id,
    sha_manifest=None,
    detailed_manifest=None
):
    """
    Verify the complete IBM evidence package.

    Checks:
        1. ZIP exists.
        2. ZIP is readable.
        3. Required files exist.
        4. Embedded job_id matches.
        5. Raw job-details SHA-256 matches metadata.
        6. Raw results SHA-256 matches metadata.
        7. Outer ZIP SHA-256 matches sha256sums.txt.
        8. Detailed manifest agrees with package hash.

    Returns a detailed dictionary rather than a single boolean.
    """

    zip_filename = f"job-{job_id}.zip"

    result = {
        "job_id": job_id,
        "package": zip_filename,
        "status": "NOT_ATTACHED",
        "package_sha256": "",
        "recorded_package_sha256": "",
        "job_details_sha256": "",
        "recorded_job_details_sha256": "",
        "job_results_sha256": "",
        "recorded_job_results_sha256": "",
        "error": "",
    }

    if not os.path.exists(zip_filename):
        return result

    if sha_manifest is None:
        sha_manifest = load_sha256_manifest()

    if detailed_manifest is None:
        detailed_manifest = load_detailed_manifest()

    try:
        # ------------------------------------------------------------
        # Outer package hash
        # ------------------------------------------------------------

        actual_package_hash = sha256_file(zip_filename)

        result["package_sha256"] = actual_package_hash

        recorded_package_hash = sha_manifest.get(
            zip_filename,
            ""
        )

        result["recorded_package_sha256"] = (
            recorded_package_hash
        )

        if not recorded_package_hash:
            result["error"] = (
                "No outer SHA-256 manifest entry."
            )

        elif (
            actual_package_hash.lower()
            != recorded_package_hash.lower()
        ):
            result["status"] = "HASH_FAIL"
            result["error"] = (
                "Outer package SHA-256 mismatch."
            )
            return result

        # ------------------------------------------------------------
        # Open ZIP
        # ------------------------------------------------------------

        with zipfile.ZipFile(
            zip_filename,
            "r"
        ) as z:

            required = {
                "job_details_raw.json",
                "job_results_raw.json",
                "evidence_metadata.json",
            }

            names = set(z.namelist())
            missing = required - names

            if missing:
                result["status"] = "PARTIAL"
                result["error"] = (
                    "Missing: "
                    + ", ".join(sorted(missing))
                )
                return result

            # --------------------------------------------------------
            # Read metadata
            # --------------------------------------------------------

            metadata = json.loads(
                z.read(
                    "evidence_metadata.json"
                ).decode("utf-8")
            )

            if not isinstance(metadata, dict):
                result["status"] = "ERROR"
                result["error"] = (
                    "Evidence metadata is not an object."
                )
                return result

            # --------------------------------------------------------
            # Job identity
            # --------------------------------------------------------

            if str(
                metadata.get("job_id", "")
            ).strip() != str(job_id).strip():

                result["status"] = "MISMATCH"
                result["error"] = (
                    "Embedded job_id does not match."
                )
                return result

            # --------------------------------------------------------
            # Raw IBM response bodies
            # --------------------------------------------------------

            job_raw = z.read(
                "job_details_raw.json"
            )

            results_raw = z.read(
                "job_results_raw.json"
            )

            actual_job_hash = sha256_bytes(
                job_raw
            )

            actual_results_hash = sha256_bytes(
                results_raw
            )

            result["job_details_sha256"] = (
                actual_job_hash
            )

            result["job_results_sha256"] = (
                actual_results_hash
            )

            # --------------------------------------------------------
            # Recorded internal hashes
            # --------------------------------------------------------

            recorded_hashes = metadata.get(
                "raw_response_sha256",
                {}
            ) or {}

            recorded_job_hash = (
                recorded_hashes.get(
                    "job_details_raw.json",
                    ""
                )
            )

            recorded_results_hash = (
                recorded_hashes.get(
                    "job_results_raw.json",
                    ""
                )
            )

            result["recorded_job_details_sha256"] = (
                recorded_job_hash
            )

            result["recorded_job_results_sha256"] = (
                recorded_results_hash
            )

            if not recorded_job_hash or not recorded_results_hash:

                result["status"] = "PARTIAL"
                result["error"] = (
                    "Internal response hashes are missing."
                )
                return result

            # --------------------------------------------------------
            # Internal cryptographic checks
            # --------------------------------------------------------

            if (
                actual_job_hash.lower()
                != recorded_job_hash.lower()
            ):

                result["status"] = "HASH_FAIL"
                result["error"] = (
                    "Job-details SHA-256 mismatch."
                )
                return result

            if (
                actual_results_hash.lower()
                != recorded_results_hash.lower()
            ):

                result["status"] = "HASH_FAIL"
                result["error"] = (
                    "Job-results SHA-256 mismatch."
                )
                return result

            # --------------------------------------------------------
            # Detailed manifest consistency
            # --------------------------------------------------------

            detailed = detailed_manifest.get(
                job_id
            )

            if detailed:

                detailed_hash = detailed.get(
                    "package_sha256",
                    ""
                )

                if (
                    detailed_hash
                    and detailed_hash.lower()
                    != actual_package_hash.lower()
                ):

                    result["status"] = "HASH_FAIL"
                    result["error"] = (
                        "Detailed manifest package hash mismatch."
                    )
                    return result

            # --------------------------------------------------------
            # Final status
            # --------------------------------------------------------

            if recorded_package_hash:
                result["status"] = "YES"
            else:
                result["status"] = "PARTIAL"

            return result

    except zipfile.BadZipFile:

        result["status"] = "ERROR"
        result["error"] = "Invalid ZIP archive."
        return result

    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        TypeError,
        ValueError,
    ) as exc:

        result["status"] = "ERROR"
        result["error"] = str(exc)
        return result


# ============================================================================
# METRIC DISCOVERY
# ============================================================================

def collect_numeric_observable_keys(rows):
    """
    Discover numeric physical observables found in any strategy.

    Reference metrics such as ideal_entropy are excluded from the strategy
    comparison tables and displayed separately.
    """

    keys = set()

    for row in rows:

        observables = row["_observables"]

        for strategy in (
            "sabre",
            "tket",
            "prometheus",
        ):

            data = observables.get(
                strategy,
                {}
            ) or {}

            for key, value in data.items():

                if (
                    key not in REFERENCE_METRICS
                    and numeric(value) is not None
                ):
                    keys.add(key)

    preferred = [
        "fidelity",
        "tvd",
        "xeb",
        "entropy",
        "hop",
    ]

    ordered = [
        key
        for key in preferred
        if key in keys
    ]

    ordered.extend(
        sorted(
            keys - set(ordered)
        )
    )

    return ordered


def collect_reference_metrics(rows):
    """
    Discover reference/context metrics such as ideal_entropy.
    """

    references = set()

    for row in rows:

        observables = row["_observables"]

        for strategy in (
            "sabre",
            "tket",
            "prometheus",
        ):

            data = observables.get(
                strategy,
                {}
            ) or {}

            for key, value in data.items():

                if (
                    key in REFERENCE_METRICS
                    and numeric(value) is not None
                ):
                    references.add(key)

    return sorted(references)


# ============================================================================
# MAIN VIEW
# ============================================================================

def build_and_view():

    if not os.path.exists(LEDGER_PATH):
        print(
            f"[!] Error: {LEDGER_PATH} not found."
        )
        return

    try:

        with open(
            LEDGER_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            ledger = json.load(f)

    except (
        OSError,
        json.JSONDecodeError,
    ) as exc:

        print(
            f"[!] Error reading {LEDGER_PATH}: {exc}"
        )
        return

    if not isinstance(ledger, list):
        print(
            f"[!] Error: {LEDGER_PATH} is not a list."
        )
        return

    if not ledger:
        print("[!] No records found.")
        return

    sha_manifest = load_sha256_manifest()
    detailed_manifest = load_detailed_manifest()

    rows = []
    evidence_rows = []

    # ------------------------------------------------------------------------
    # Build base rows
    # ------------------------------------------------------------------------

    for job in ledger:

        job_id = str(
            job.get(
                "job_id",
                ""
            )
        ).strip()

        logical = (
            job.get(
                "logical_metrics",
                {}
            )
            or {}
        )

        circuit = (
            job.get(
                "circuit_metrics",
                {}
            )
            or {}
        )

        observables = (
            job.get(
                "physical_observables",
                {}
            )
            or {}
        )

        sabre = (
            observables.get(
                "sabre",
                {}
            )
            or {}
        )

        tket = (
            observables.get(
                "tket",
                {}
            )
            or {}
        )

        prometheus = (
            observables.get(
                "prometheus",
                {}
            )
            or {}
        )

        evidence = inspect_evidence(
            job_id,
            sha_manifest=sha_manifest,
            detailed_manifest=detailed_manifest
        )

        execution_info = extract_ibm_execution_info(
            job_id,
            sha_manifest=sha_manifest,
            detailed_manifest=detailed_manifest
        )

        # Keep the requested value from the ledger, but use IBM evidence for
        # the actual executed-shot count whenever it is available.
        shots_requested = job.get(
            "shots_requested",
            "N/A"
        )

        row = {
            "job_id": job_id,
            "qpu": job.get(
                "selected_qpu",
                ""
            ),
            "qubits": logical.get(
                "qubits",
                ""
            ),
            "circuit_family": job.get(
                "circuit_family",
                ""
            ),
            "shots_requested": shots_requested,

            # IBM evidence-derived execution counts.
            "shots_per_circuit": (
                execution_info["shots_per_circuit"]
                if execution_info["shots_per_circuit"] is not None
                else "N/A"
            ),

            "circuits_per_job": (
                execution_info["circuits_per_job"]
                if execution_info["circuits_per_job"] is not None
                else "N/A"
            ),

            "shots_executed": (
                execution_info["total_shots_executed"]
                if execution_info["total_shots_executed"] is not None
                else "N/A"
            ),

            # Preserve both the original ledger timestamp and the
            # IBM-authoritative creation/execution timestamps.
            "timestamp": (
                job.get("timestamp")
                or "N/A"
            ),

            "ibm_created_utc": execution_info["ibm_created_utc"],
            "execution_start_utc": execution_info["execution_start_utc"],
            "execution_stop_utc": execution_info["execution_stop_utc"],

            "status": job.get(
                "status",
                ""
            ),

            # Structural
            "sabre_2q_gates": circuit.get(
                "sabre_2q_gates",
                "N/A"
            ),
            "tket_2q_gates": circuit.get(
                "tket_2q_gates",
                "N/A"
            ),
            "prometheus_2q_gates": circuit.get(
                "prometheus_2q_gates",
                "N/A"
            ),

            "sabre_depth": circuit.get(
                "sabre_depth",
                "N/A"
            ),
            "tket_depth": circuit.get(
                "tket_depth",
                "N/A"
            ),
            "prometheus_depth": circuit.get(
                "prometheus_depth",
                "N/A"
            ),

            # Evidence
            "ibm_verified": evidence["status"],
            "package_sha256": evidence["package_sha256"],

            "_observables": {
                "sabre": sabre,
                "tket": tket,
                "prometheus": prometheus,
            },

            "_evidence": evidence,
        }

        rows.append(row)
        evidence_rows.append(evidence)

    observable_keys = collect_numeric_observable_keys(rows)
    reference_keys = collect_reference_metrics(rows)

    # ------------------------------------------------------------------------
    # Enrich rows for CSV
    # ------------------------------------------------------------------------

    for row in rows:

        sabre = row["_observables"]["sabre"]
        tket = row["_observables"]["tket"]
        prometheus = row["_observables"]["prometheus"]

        # Strategy observables
        for metric in observable_keys:

            s = sabre.get(
                metric,
                "N/A"
            )

            t = tket.get(
                metric,
                "N/A"
            )

            p = prometheus.get(
                metric,
                "N/A"
            )

            row[f"sabre_{metric}"] = s
            row[f"tket_{metric}"] = t
            row[f"prometheus_{metric}"] = p

            direction = None

            if metric in HIGHER_IS_BETTER:
                direction = True

            elif metric in LOWER_IS_BETTER:
                direction = False

            if direction is not None:

                row[
                    f"prometheus_{metric}_vs_best"
                ] = format_delta(
                    p,
                    s,
                    t,
                    higher_is_better=direction
                )

                row[
                    f"prometheus_{metric}_beats_both"
                ] = better_than_baselines(
                    p,
                    s,
                    t,
                    higher_is_better=direction
                )

        # Reference metrics
        for metric in reference_keys:

            # In normal data these should be identical because ideal_entropy
            # is a circuit/reference property rather than a compiler output.
            values = [
                sabre.get(metric),
                tket.get(metric),
                prometheus.get(metric),
            ]

            numeric_values = [
                numeric(v)
                for v in values
                if numeric(v) is not None
            ]

            if numeric_values:

                reference = numeric_values[0]

                row[f"reference_{metric}"] = reference

                row[
                    f"sabre_{metric}_error"
                ] = absolute_error(
                    sabre.get(metric),
                    reference
                )

                row[
                    f"tket_{metric}_error"
                ] = absolute_error(
                    tket.get(metric),
                    reference
                )

                row[
                    f"prometheus_{metric}_error"
                ] = absolute_error(
                    prometheus.get(metric),
                    reference
                )

            else:

                row[f"reference_{metric}"] = "N/A"
                row[f"sabre_{metric}_error"] = "N/A"
                row[f"tket_{metric}_error"] = "N/A"
                row[f"prometheus_{metric}_error"] = "N/A"

    # ------------------------------------------------------------------------
    # Master CSV
    # ------------------------------------------------------------------------

    clean_rows = []

    for row in rows:

        clean_rows.append({
            key: value
            for key, value in row.items()
            if not key.startswith("_")
        })

    if clean_rows:

        with open(
            "master_results.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=list(
                    clean_rows[0].keys()
                )
            )

            writer.writeheader()
            writer.writerows(clean_rows)

    # ------------------------------------------------------------------------
    # Evidence CSV
    # ------------------------------------------------------------------------

    evidence_fields = [
        "job_id",
        "package",
        "status",
        "package_sha256",
        "recorded_package_sha256",
        "job_details_sha256",
        "recorded_job_details_sha256",
        "job_results_sha256",
        "recorded_job_results_sha256",
        "error",
    ]

    with open(
        OUTPUT_EVIDENCE_CSV,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=evidence_fields
        )

        writer.writeheader()

        for evidence in evidence_rows:
            writer.writerow(evidence)

    # ------------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------------

    print_sep(length=180)

    print(
        " PROMETHEUS SCALING STUDY - COMPLETE BENCHMARK VIEW"
        .ljust(180)
    )

    print_sep(length=180)

    executable_shots = [
        numeric(row.get("shots_executed"))
        for row in rows
        if numeric(row.get("shots_executed")) is not None
    ]

    total_shots = sum(executable_shots)

    total_shots_display = (
        f"{total_shots:,.0f}"
        if executable_shots
        else "N/A"
    )

    per_circuit_values = [
        numeric(row.get("shots_per_circuit"))
        for row in rows
        if numeric(row.get("shots_per_circuit")) is not None
    ]

    per_circuit_display = (
        f"{per_circuit_values[0]:,.0f}"
        if per_circuit_values
        else "N/A"
    )

    print(
        f" Records: {len(rows)}"
        f" | QPUs: {', '.join(sorted(set(str(r['qpu']) for r in rows)))}"
        f" | Shots/circuit: {per_circuit_display}"
        f" | Total shots across jobs: {total_shots_display}"
        f" | Strategy observables: "
        f"{', '.join(observable_keys) if observable_keys else 'none'}"
        f" | Reference metrics: "
        f"{', '.join(reference_keys) if reference_keys else 'none'}"
    )

    # ------------------------------------------------------------------------
    # JOB / EXECUTION INFORMATION
    # ------------------------------------------------------------------------

    print()
    print_sep(length=170)

    print(
        " JOB EXECUTION / PROVENANCE"
        .ljust(170)
    )

    print_sep(length=170)

    print(
        f"{'Qubits':<8} | "
        f"{'QPU':<12} | "
        f"{'Shots/Circuit':<14} | "
        f"{'Circuits/Job':<13} | "
        f"{'Total Shots/Job':<16} | "
        f"{'IBM Created UTC':<24} | "
        f"{'Execution Start UTC':<24} | "
        f"{'Job ID':<24}"
    )

    print_sep("-", 170)

    for row in rows:

        print(
            f"{str(row['qubits']) + 'Q':<8} | "
            f"{str(row['qpu']):<12} | "
            f"{fmt_int(row['shots_per_circuit']):<14} | "
            f"{fmt_int(row['circuits_per_job']):<13} | "
            f"{fmt_int(row['shots_executed']):<16} | "
            f"{str(row['ibm_created_utc'])[:24]:<24} | "
            f"{str(row['execution_start_utc'])[:24]:<24} | "
            f"{row['job_id']:<24}"
        )

    print()
    print(
        "Compiler shot allocation: "
        "SABRE 16,384 | TKET 16,384 | Prometheus 16,384 "
        "per job, for the supplied evidence."
    )

    # ------------------------------------------------------------------------
    # STRUCTURAL
    # ------------------------------------------------------------------------



    print()
    print_sep(length=170)

    print(
        " STRUCTURAL METRICS - 2Q GATES AND CIRCUIT DEPTH"
        .ljust(170)
    )

    print_sep(length=170)

    print(
        f"{'Qubits':<8} | "
        f"{'QPU':<12} | "
        f"{'Shots/Circ':<11} | "
        f"{'Total/Job':<11} | "
        f"{'SABRE 2Q':<10} | "
        f"{'TKET 2Q':<9} | "
        f"{'PROM 2Q':<9} | "
        f"{'vs Best':<9} | "
        f"{'Beats Both':<10} | "
        f"{'SABRE Dep':<10} | "
        f"{'TKET Dep':<9} | "
        f"{'PROM Dep':<9} | "
        f"{'vs Best':<9} | "
        f"{'Beats Both':<10}"
    )

    print_sep("-", 170)

    for row in rows:

        s2 = row["sabre_2q_gates"]
        t2 = row["tket_2q_gates"]
        p2 = row["prometheus_2q_gates"]

        sd = row["sabre_depth"]
        td = row["tket_depth"]
        pd = row["prometheus_depth"]

        print(
            f"{str(row['qubits']) + 'Q':<8} | "
            f"{str(row['qpu']):<12} | "
            f"{fmt_int(row['shots_per_circuit']):<11} | "
            f"{fmt_int(row['shots_executed']):<11} | "
            f"{fmt_int(s2):<10} | "
            f"{fmt_int(t2):<9} | "
            f"{fmt_int(p2):<9} | "
            f"{format_delta(p2, s2, t2, False):<9} | "
            f"{better_than_baselines(p2, s2, t2, False):<10} | "
            f"{fmt_int(sd):<10} | "
            f"{fmt_int(td):<9} | "
            f"{fmt_int(pd):<9} | "
            f"{format_delta(pd, sd, td, False):<9} | "
            f"{better_than_baselines(pd, sd, td, False):<10}"
        )

    # ------------------------------------------------------------------------
    # STRATEGY PHYSICAL OBSERVABLES
    # ------------------------------------------------------------------------

    for metric in observable_keys:

        direction = None

        if metric in HIGHER_IS_BETTER:
            direction = True
            interpretation = "higher is better"

        elif metric in LOWER_IS_BETTER:
            direction = False
            interpretation = "lower is better"

        else:
            interpretation = "shown only; no directional ranking applied"

        print()
        print_sep(length=145)

        print(
            f" PHYSICAL OBSERVABLE - {pretty_metric_name(metric)} "
            f"({interpretation})".ljust(145)
        )

        print_sep(length=145)

        if direction is not None:

            print(
                f"{'Qubits':<8} | "
                f"{'QPU':<12} | "
                f"{'Shots/Circ':<11} | "
                f"{'SABRE':<14} | "
                f"{'TKET':<14} | "
                f"{'PROMETHEUS':<14} | "
                f"{'PROM vs Best':<14} | "
                f"{'Prom Beats Both':<16}"
            )

            print_sep("-", 145)

            for row in rows:

                s = row["_observables"]["sabre"].get(
                    metric,
                    "N/A"
                )

                t = row["_observables"]["tket"].get(
                    metric,
                    "N/A"
                )

                p = row["_observables"]["prometheus"].get(
                    metric,
                    "N/A"
                )

                print(
                    f"{str(row['qubits']) + 'Q':<8} | "
                    f"{str(row['qpu']):<12} | "
                    f"{fmt_int(row['shots_per_circuit']):<11} | "
                    f"{fmt(s):<14} | "
                    f"{fmt(t):<14} | "
                    f"{fmt(p):<14} | "
                    f"{format_delta(p, s, t, direction):<14} | "
                    f"{better_than_baselines(p, s, t, direction):<16}"
                )

        else:

            print(
                f"{'Qubits':<8} | "
                f"{'QPU':<12} | "
                f"{'Shots/Circ':<11} | "
                f"{'SABRE':<18} | "
                f"{'TKET':<18} | "
                f"{'PROMETHEUS':<18}"
            )

            print_sep("-", 100)

            for row in rows:

                s = row["_observables"]["sabre"].get(
                    metric,
                    "N/A"
                )

                t = row["_observables"]["tket"].get(
                    metric,
                    "N/A"
                )

                p = row["_observables"]["prometheus"].get(
                    metric,
                    "N/A"
                )

                print(
                    f"{str(row['qubits']) + 'Q':<8} | "
                    f"{str(row['qpu']):<12} | "
                    f"{fmt_int(row['shots_per_circuit']):<11} | "
                    f"{fmt(s):<18} | "
                    f"{fmt(t):<18} | "
                    f"{fmt(p):<18}"
                )

    # ------------------------------------------------------------------------
    # REFERENCE METRICS
    # ------------------------------------------------------------------------

    if reference_keys:

        print()
        print_sep(length=120)

        print(
            " REFERENCE / IDEAL METRICS"
            .ljust(120)
        )

        print_sep(length=120)

        print(
            "These values describe the circuit/reference target and are not "
            "independent compiler outputs."
        )

        print()

        for metric in reference_keys:

            print_sep("-", 80)

            print(
                f" {pretty_metric_name(metric)}"
            )

            print_sep("-", 80)

            print(
                f"{'Qubits':<8} | "
                f"{'QPU':<12} | "
                f"{'Shots/Circ':<11} | "
                f"{'Reference Value':<18}"
            )

            print_sep("-", 45)

            for row in rows:

                observables = row["_observables"]

                # Prefer Prometheus' stored reference value, then SABRE/TKET
                # if necessary. All three should represent the same reference
                # quantity in this ledger.
                reference = observables["prometheus"].get(
                    metric,
                    None
                )

                if numeric(reference) is None:
                    reference = observables["sabre"].get(
                        metric,
                        None
                    )

                if numeric(reference) is None:
                    reference = observables["tket"].get(
                        metric,
                        None
                    )

                print(
                    f"{str(row['qubits']) + 'Q':<8} | "
                    f"{str(row['qpu']):<12} | "
                    f"{fmt_int(row['shots_per_circuit']):<11} | "
                    f"{fmt(reference):<18}"
                )

            print()

            print(
                "No compiler-to-compiler comparison is applied to this "
                "reference metric."
            )

    # ------------------------------------------------------------------------
    # EVIDENCE
    # ------------------------------------------------------------------------


    print()
    print_sep(length=175)

    print(
        " IBM EVIDENCE INTEGRITY VERIFICATION"
        .ljust(175)
    )

    print_sep(length=175)

    print(
        f"{'Job ID':<24} | "
        f"{'Shots/Circ':<11} | "
        f"{'Total/Job':<12} | "
        f"{'IBM Created UTC':<24} | "
        f"{'Package':<30} | "
        f"{'Status':<12} | "
        f"{'Package SHA-256':<70}"
    )

    print_sep("-", 175)

    for evidence in evidence_rows:

        print(
            f"{evidence['job_id']:<24} | "
            f"{fmt_int(next((r['shots_per_circuit'] for r in rows if r['job_id'] == evidence['job_id']), 'N/A')):<11} | "
            f"{fmt_int(next((r['shots_executed'] for r in rows if r['job_id'] == evidence['job_id']), 'N/A')):<12} | "
            f"{str(next((r['ibm_created_utc'] for r in rows if r['job_id'] == evidence['job_id']), 'N/A'))[:24]:<24} | "
            f"{evidence['package']:<30} | "
            f"{evidence['status']:<12} | "
            f"{evidence['package_sha256']:<70}"
        )

        if evidence["error"]:
            print(
                f"  [!] {evidence['error']}"
            )

    # ------------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------------

    structural_2q_wins = 0
    structural_depth_wins = 0
    fidelity_wins = 0
    verified_count = 0

    for row in rows:

        if (
            better_than_baselines(
                row["prometheus_2q_gates"],
                row["sabre_2q_gates"],
                row["tket_2q_gates"],
                False
            )
            == "YES"
        ):
            structural_2q_wins += 1

        if (
            better_than_baselines(
                row["prometheus_depth"],
                row["sabre_depth"],
                row["tket_depth"],
                False
            )
            == "YES"
        ):
            structural_depth_wins += 1

        if "fidelity" in observable_keys:

            if (
                better_than_baselines(
                    row["_observables"]["prometheus"].get(
                        "fidelity",
                        "N/A"
                    ),
                    row["_observables"]["sabre"].get(
                        "fidelity",
                        "N/A"
                    ),
                    row["_observables"]["tket"].get(
                        "fidelity",
                        "N/A"
                    ),
                    True
                )
                == "YES"
            ):
                fidelity_wins += 1

    verified_count = sum(
        1
        for evidence in evidence_rows
        if evidence["status"] == "YES"
    )

    print()
    print_sep(length=100)

    print(
        " STUDY SUMMARY"
        .ljust(100)
    )

    print_sep(length=100)

    print(
        f"Jobs analyzed:                    {len(rows)}"
    )

    print(
        f"IBM evidence packages verified:  "
        f"{verified_count}/{len(rows)}"
    )

    print(
        f"Prometheus beats both on 2Q gates:"
        f"{structural_2q_wins}/{len(rows)}"
    )

    print(
        f"Prometheus beats both on depth:   "
        f"{structural_depth_wins}/{len(rows)}"
    )

    if "fidelity" in observable_keys:

        print(
            f"Prometheus beats both on fidelity:"
            f"{fidelity_wins}/{len(rows)}"
        )

    print()
    print(
        f"[+] Detailed benchmark CSV: {OUTPUT_CSV}"
    )

    print(
        f"[+] Evidence verification CSV: "
        f"{OUTPUT_EVIDENCE_CSV}"
    )

    print_sep(length=100)


if __name__ == "__main__":
    build_and_view()
