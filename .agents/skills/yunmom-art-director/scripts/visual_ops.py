#!/usr/bin/env python3
"""Transactional visual-program operations for the YunMom Art Director skill.

The only mutable source of truth is
``visual/manifests/visual_program.json``.  Every other registry and Markdown
log is a disposable projection generated from that file.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import datetime as dt
import hashlib
import json
import ntpath
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
import time
import uuid
from typing import Any, Callable
from urllib.parse import urlparse


PROGRAM_SCHEMA = 1
PROGRAM_ID = "yunmom-visual-program"
ASSET_CLASSES = {"S", "A", "B", "C"}
ASSET_TYPES = {
    "character", "baby", "screen", "component", "icon", "prop", "ambient",
    "motion", "widget", "safety", "gentle_closure", "illustration", "texture",
}
LIFECYCLE_STAGES = {
    "candidate", "finalist", "provisional", "aesthetic_golden", "deprecated", "rejected",
}
REGISTERABLE_STAGES = {"candidate", "finalist", "provisional"}
FRESHNESS_STATES = {"current", "stale", "stale_contract_conflict"}
STALE_REASON_CODES = {"manual", "dependency_changed", "golden_replaced", "contract_conflict"}
DECISION_KINDS = {"baseline", "feedback", "approval", "rejection", "change"}
DECISION_STATUSES = {"recorded", "provisional", "approved", "rejected", "superseded"}
REVIEW_FAMILIES = {"brand", "visual", "production", "medical", "accessibility_safety"}
VERDICTS = {"PASS", "FAIL", "NEEDS_REVISION", "NEEDS_MEDICAL_REFERENCE", "BLOCKED"}
REVIEWER_KINDS = {"custom_agent", "subagent", "human", "external_specialist"}
EVIDENCE_STAGES = {"concept", "aesthetic_golden", "integrated", "matrix_accepted", "release_signed"}
EVIDENCE_CATEGORIES = {"integration", "accessibility", "production", "matrix", "release"}
EVIDENCE_PLATFORMS = {"android", "ios", "cross_platform", "flutter", "not_applicable"}
EVIDENCE_VERIFIER_ROLES = {
    "DESIGN", "ANDROID", "IOS", "QA", "MD", "LEGAL", "SEC", "ETHICS", "PO", "TECH",
    "ACCESSIBILITY", "PRODUCTION",
}
RELEASE_SIGNING_ROLES = {"PO", "TECH", "QA", "MD", "LEGAL", "SEC", "ETHICS"}
EVIDENCE_ROLE_BY_CATEGORY: dict[str, set[str]] = {
    "integration": {"TECH", "QA", "ANDROID", "IOS"},
    "accessibility": {"QA", "ACCESSIBILITY", "ANDROID", "IOS", "MD"},
    "production": {"TECH", "QA", "DESIGN", "ANDROID", "IOS", "PRODUCTION"},
    "matrix": {"TECH", "QA", "ANDROID", "IOS"},
    "release": RELEASE_SIGNING_ROLES,
}
MEDICAL_VERDICTS = {"VERIFIED", "REJECTED"}
RELEASE_STATUSES = {"not_approved", "evidence_collecting", "approved"}
PROFESSIONAL_ROLES = {"obstetrician", "midwife", "pediatrician", "clinical_reviewer", "medical_director"}
GOLDEN_SLOTS = {"yunmom_master", "style_lock_sheet", "home_canonical", "app_icon"}
SLOT_RULES: dict[str, tuple[set[str], set[str]]] = {
    "yunmom_master": ({"S"}, {"character"}),
    "style_lock_sheet": ({"S"}, {"illustration"}),
    "home_canonical": ({"S"}, {"screen"}),
    "app_icon": ({"S"}, {"icon"}),
}
PRODUCTION_REVIEW_TYPES = {"screen", "component", "motion", "widget", "safety", "gentle_closure"}
ACCESSIBILITY_REVIEW_TYPES = {"screen", "component", "motion", "widget", "safety", "gentle_closure"}
DUAL_PLATFORM_MATRIX_TYPES = {"screen", "component", "motion", "widget", "safety", "gentle_closure"}
AUTO_MEDICAL_ASSET_TYPES = {"baby", "safety", "gentle_closure"}

RIGHTS_STATUSES = {
    "unverified", "owned", "licensed", "approved_provider_terms", "public_domain", "not_applicable",
}
VERIFIED_RIGHTS_STATUSES = RIGHTS_STATUSES - {"unverified"}
REPOSITORY_SAFE_ORIGINS = {"synthetic", "irreversibly_deidentified", "not_applicable"}

BASE_HARD_GATES: dict[str, set[str]] = {
    "brand": {"BRAND_DISTINCTIVENESS", "BRAND_CONSISTENCY"},
    "visual": {"VISUAL_HIERARCHY", "VISUAL_COHERENCE", "NON_TEMPLATE_QUALITY"},
    "production": {"IMPLEMENTATION_FEASIBILITY", "TOKEN_COMPLIANCE", "PERFORMANCE_RISK"},
    "medical": {"MEDICAL_SCOPE_ACCURACY", "SAFETY_SEVERITY_PRESERVED", "NO_DIAGNOSIS_TREATMENT"},
    "accessibility_safety": {
        "WCAG_2_2_AA", "SCREEN_READER", "TEXT_SCALE_200", "REDUCE_MOTION", "NON_COLOR_SAFETY",
    },
}
TYPE_HARD_GATES: dict[str, dict[str, set[str]]] = {
    "screen": {"accessibility_safety": {"P0_FLOW_COMPLETABLE"}},
    "component": {"accessibility_safety": {"P0_FLOW_COMPLETABLE"}},
    "motion": {"accessibility_safety": {"REDUCE_MOTION_EQUIVALENCE"}},
    "widget": {"accessibility_safety": {
        "WIDGET_PRIVACY_MINIMIZATION", "WIDGET_READ_ONLY", "WIDGET_MAX_24H_EXPIRY",
    }},
    "safety": {
        "medical": {"R0_R3_SEVERITY_ACTION", "DISMISS_NOT_RESOLVE"},
        "accessibility_safety": {"R0_R3_TEXT_ICON_ACTION", "DISMISS_NOT_RESOLVE"},
    },
    "gentle_closure": {
        "medical": {"GENTLE_CLOSURE_CLINICAL_BOUNDARY"},
        "accessibility_safety": {"TRAUMA_INFORMED_COMPLETION", "GENTLE_CLOSURE_PRIVACY"},
    },
}

ASSET_ID_RE = re.compile(r"^VA-\d{8}-[0-9a-f]{8}$")
DECISION_ID_RE = re.compile(r"^D-\d{4,}$")
REVIEW_ID_RE = re.compile(r"^VR-\d{4,}$")
SOURCE_ID_RE = re.compile(r"^MS-\d{4,}$")
VERIFICATION_ID_RE = re.compile(r"^MV-\d{4,}$")
EVIDENCE_ID_RE = re.compile(r"^EV-\d{4,}$")
OPERATION_ID_RE = re.compile(r"^OP-[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
TOKEN_PRIORITY = [
    "system_accessibility_high_contrast",
    "medical_safety_crisis",
    "error_permission_destructive_confirmation",
    "temporary_interaction",
    "silent_day_mood_ambient",
    "task",
    "time_weather_decoration",
]
TOKEN_PLATFORMS = {"flutter", "rive", "ios_widget", "android_widget"}
ASSET_AREA_PREFIXES = ("visual/candidates/", "visual/derived/", "visual/production/")
PRIVACY_CLASSIFICATIONS = {
    "unclassified", "public_product", "identity_commercial", "device_low_sensitive",
    "health_intimate", "credential_security",
}
CONTENT_ORIGINS = {"unknown", "synthetic", "irreversibly_deidentified", "real_sensitive", "not_applicable"}
EGRESS_STATUSES = {"not_requested", "confirmed_per_send", "prohibited"}
CLEANUP_SCOPES = {
    "source_asset", "golden_copy", "derived_assets", "review_artifacts", "evidence_artifacts",
    "prompts", "temporary_files", "external_provider_request",
}
DEFAULT_CLEANUP_SCOPE = sorted(CLEANUP_SCOPES)


class VisualStateError(RuntimeError):
    """A user-actionable visual-program contract violation."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def today_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_ntfs_ads_syntax(value: str | os.PathLike[str], *, label: str) -> None:
    """Reject NTFS alternate-stream syntax while allowing the drive designator."""
    raw = os.fspath(value)
    if "\x00" in raw:
        raise VisualStateError(f"{label} contains a NUL byte")
    _drive, tail = ntpath.splitdrive(raw)
    if ":" in tail:
        raise VisualStateError(f"{label} contains forbidden NTFS alternate-stream syntax: {raw}")


def is_reparse_or_symlink(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(getattr(info, "st_file_attributes", 0) & reparse_flag)


def named_streams(path: Path) -> list[str]:
    """Return non-default NTFS streams; non-Windows filesystems have none."""
    if os.name != "nt" or not path.exists():
        return []

    class FindStreamData(ctypes.Structure):
        _fields_ = [("stream_size", ctypes.c_longlong), ("stream_name", ctypes.c_wchar * 296)]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    first = kernel32.FindFirstStreamW
    first.argtypes = [ctypes.c_wchar_p, ctypes.c_int, ctypes.POINTER(FindStreamData), ctypes.c_uint]
    first.restype = ctypes.c_void_p
    next_stream = kernel32.FindNextStreamW
    next_stream.argtypes = [ctypes.c_void_p, ctypes.POINTER(FindStreamData)]
    next_stream.restype = ctypes.c_int
    close = kernel32.FindClose
    close.argtypes = [ctypes.c_void_p]
    close.restype = ctypes.c_int

    data = FindStreamData()
    handle = first(str(path), 0, ctypes.byref(data), 0)
    invalid = ctypes.c_void_p(-1).value
    if handle == invalid:
        code = ctypes.get_last_error()
        if code in {2, 38, 50, 87}:
            return []
        raise VisualStateError(f"cannot enumerate NTFS streams for {path}: WinError {code}")
    streams: list[str] = []
    try:
        while True:
            name = str(data.stream_name)
            if name and name != "::$DATA":
                streams.append(name)
            if not next_stream(handle, ctypes.byref(data)):
                code = ctypes.get_last_error()
                if code == 38:
                    break
                raise VisualStateError(f"cannot enumerate NTFS streams for {path}: WinError {code}")
    finally:
        close(handle)
    return streams


def reject_reparse_chain(base: Path, target: Path, *, label: str) -> None:
    """Reject every existing symlink/reparse component from base through target."""
    try:
        relative = target.relative_to(base)
    except ValueError as exc:
        raise VisualStateError(f"{label} escapes its trusted root: {target}") from exc
    current = base
    if is_reparse_or_symlink(current):
        raise VisualStateError(f"{label} trusted root is a symlink/reparse point: {current}")
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if is_reparse_or_symlink(current):
                raise VisualStateError(f"{label} crosses a symlink/reparse point: {current}")


def reject_any_reparse_component(path: Path, *, label: str) -> None:
    chain = [path, *path.parents]
    for component in reversed(chain):
        if component.exists() and is_reparse_or_symlink(component):
            raise VisualStateError(f"{label} crosses a symlink/reparse point: {component}")


def verify_regular_single_link(path: Path, *, label: str) -> None:
    """Fail closed for devices, directories, reparse points, and hard-linked files."""
    if is_reparse_or_symlink(path):
        raise VisualStateError(f"{label} may not be a symlink/reparse point: {path}")
    try:
        info = path.stat()
    except OSError as exc:
        raise VisualStateError(f"cannot inspect {label}: {path}: {exc}") from exc
    if not stat.S_ISREG(info.st_mode):
        raise VisualStateError(f"{label} must be a regular file: {path}")
    if getattr(info, "st_nlink", 1) != 1:
        raise VisualStateError(f"hard-linked {label} is forbidden: {path}")
    streams = named_streams(path)
    if streams:
        raise VisualStateError(f"NTFS alternate streams are forbidden for {label}: {path}: {streams}")


def secure_external_file(value: str | os.PathLike[str], *, label: str) -> Path:
    """Validate an explicitly trusted file outside project containment, e.g. a font."""
    reject_ntfs_ads_syntax(value, label=label)
    lexical = Path(os.path.abspath(os.fspath(Path(value).expanduser())))
    reject_any_reparse_component(lexical, label=label)
    path = lexical.resolve(strict=True)
    verify_regular_single_link(path, label=label)
    return path


def secure_project_root(value: str | os.PathLike[str]) -> Path:
    reject_ntfs_ads_syntax(value, label="project root")
    lexical = Path(os.path.abspath(os.fspath(Path(value).expanduser())))
    reject_any_reparse_component(lexical, label="project root")
    root = lexical.resolve(strict=True)
    if not root.is_dir():
        raise VisualStateError(f"project root is not a directory: {root}")
    return root


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def program_path(root: Path) -> Path:
    return root / "visual" / "manifests" / "visual_program.json"


def projection_paths(root: Path) -> dict[str, Path]:
    return {
        "state": root / "visual" / "state" / "DESIGN_STATE.json",
        "assets": root / "visual" / "manifests" / "asset_registry.json",
        "decisions": root / "visual" / "decisions" / "decision_registry.json",
        "reviews": root / "visual" / "reviews" / "review_registry.json",
        "decision_log": root / "visual" / "decisions" / "DECISION_LOG.md",
    }


def has_strong_project_markers(candidate: Path) -> bool:
    contract = candidate / "docs" / "YunMom_Engineering_Contracts_V1.0.0"
    skill = candidate / ".agents" / "skills" / "yunmom-art-director" / "SKILL.md"
    canonical = program_path(candidate)
    legacy = candidate / "visual" / "state" / "DESIGN_STATE.json"
    return contract.is_dir() and (skill.is_file() or canonical.is_file() or legacy.is_file())


def find_project_root(explicit: str | None) -> Path:
    if explicit:
        return secure_project_root(explicit)
    start = secure_project_root(Path.cwd())
    for candidate in (start, *start.parents):
        if has_strong_project_markers(candidate):
            return secure_project_root(candidate)
    raise VisualStateError(
        "cannot locate YunMom project root from strong markers; pass --project-root explicitly"
    )


def visual_path(
    root: Path,
    value: str,
    *,
    must_exist: bool = False,
    allowed_prefixes: tuple[str, ...] | None = None,
) -> tuple[Path, str]:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise VisualStateError("visual path must be a non-empty string")
    reject_ntfs_ads_syntax(value, label="visual path")
    root = secure_project_root(root)
    raw = Path(value).expanduser()
    lexical = Path(os.path.abspath(os.fspath(raw if raw.is_absolute() else root / raw)))
    try:
        lexical.relative_to(root)
    except ValueError as exc:
        raise VisualStateError(f"path escapes project root: {value}") from exc
    reject_reparse_chain(root, lexical, label="visual path")
    path = lexical.resolve(strict=False)
    try:
        rel_path = path.relative_to(root)
    except ValueError as exc:
        raise VisualStateError(f"path escapes project root: {value}") from exc
    rel = rel_path.as_posix()
    if not rel_path.parts or rel_path.parts[0].casefold() != "visual":
        raise VisualStateError(f"artifact must live under visual/: {value}")
    if allowed_prefixes and not any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in allowed_prefixes):
        raise VisualStateError(f"path is outside allowed visual area {allowed_prefixes}: {rel}")
    if must_exist and not path.is_file():
        raise VisualStateError(f"file does not exist: {path}")
    if path.is_file():
        verify_regular_single_link(path, label="managed visual file")
    elif path.exists() and not path.is_dir():
        raise VisualStateError(f"managed visual path is not a regular file or directory: {path}")
    return path, rel


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VisualStateError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise VisualStateError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise VisualStateError(f"JSON root must be an object: {path}")
    return value


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


@contextlib.contextmanager
def project_lock(root: Path, timeout: float = 10.0):
    lock_path = root / "visual" / "manifests" / ".visual_ops.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    deadline = time.monotonic() + timeout
    locked = False
    try:
        while not locked:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except (OSError, BlockingIOError):
                if time.monotonic() >= deadline:
                    raise VisualStateError("timed out waiting for visual-program lock")
                time.sleep(0.05)
        yield
    finally:
        if locked:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def ensure_directories(root: Path) -> None:
    for rel in (
        "visual/candidates", "visual/derived", "visual/golden/sha256", "visual/production",
        "visual/prompts", "visual/rejected", "visual/references", "visual/reviews/screens",
        "visual/reviews/evidence", "visual/reviews/medical", "visual/system/attestations",
        "visual/state", "visual/system", "visual/manifests",
        "visual/decisions",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)


def initial_program() -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": PROGRAM_SCHEMA,
        "program_id": PROGRAM_ID,
        "revision": 0,
        "created_at": now,
        "updated_at": now,
        "visual_version": "3.0.0",
        "contract_version": "YunMom_Engineering_Contracts_V1.0.0",
        "current_gate": "G1_YUNMOM_MASTER",
        "release_status": "not_approved",
        "golden_slots": {
            "yunmom_master": None,
            "style_lock_sheet": None,
            "home_canonical": None,
            "app_icon": None,
            "baby_anchors": {},
        },
        "assets": [],
        "decisions": [{
            "id": "D-0001",
            "occurred_at": now,
            "kind": "baseline",
            "status": "approved",
            "decided_by": "product-contract",
            "asset_ids": [],
            "text": "Frozen YunMom product and engineering contracts are authoritative; no visual master is approved yet.",
            "preserve": [],
            "change": [],
        }],
        "reviews": [],
        "medical_sources": [],
        "medical_verifications": [],
        "evidence_records": [],
        "operations": [],
        "migration_history": [],
    }


def load_program(root: Path) -> dict[str, Any]:
    return load_json(program_path(root))


def next_numeric_id(items: list[dict[str, Any]], prefix: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    numbers = [
        int(match.group(1))
        for item in items
        if (match := pattern.fullmatch(str(item.get("id", ""))))
    ]
    return f"{prefix}-{(max(numbers) + 1 if numbers else 1):04d}"


def strict_keys(value: dict[str, Any], required: set[str], allowed: set[str], label: str, errors: list[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        errors.append(f"{label} missing keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{label} has unknown keys: {', '.join(extra)}")


def require_unique(items: list[dict[str, Any]], label: str, errors: list[str]) -> None:
    seen: set[str] = set()
    for index, item in enumerate(items):
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id:
            errors.append(f"{label}[{index}] missing string id")
        elif item_id in seen:
            errors.append(f"duplicate {label} id: {item_id}")
        else:
            seen.add(item_id)


def parse_iso(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO-8601 string")
        return
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} is not valid ISO-8601")


def asset_by_id(program: dict[str, Any], asset_id: str) -> dict[str, Any]:
    asset = next((item for item in program["assets"] if item.get("id") == asset_id), None)
    if not asset:
        raise VisualStateError(f"asset not found: {asset_id}")
    return asset


def dependency_cycles(assets: list[dict[str, Any]]) -> list[str]:
    graph = {
        str(asset.get("id")): [*asset.get("parents", []), *asset.get("depends_on", [])]
        for asset in assets
    }
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            start = trail.index(node) if node in trail else 0
            errors.append("asset dependency cycle: " + " -> ".join(trail[start:] + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            if child in graph:
                visit(child, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, [])
    return sorted(set(errors))


def matching_reviews(program: dict[str, Any], asset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for review in program["reviews"]:
        if review.get("asset_id") != asset["id"]:
            continue
        if review.get("asset_version") != asset["version"] or review.get("asset_sha256") != asset["sha256"]:
            continue
        family = review["family"]
        current = latest.get(family)
        if current is None or review["sequence"] > current["sequence"]:
            latest[family] = review
    return latest


def matching_medical_verification(program: dict[str, Any], asset: dict[str, Any]) -> dict[str, Any] | None:
    candidates = [
        item for item in program["medical_verifications"]
        if item.get("asset_id") == asset["id"]
        and item.get("asset_version") == asset["version"]
        and item.get("asset_sha256") == asset["sha256"]
    ]
    return max(candidates, key=lambda item: item["sequence"], default=None)


def matching_evidence(program: dict[str, Any], asset: dict[str, Any], category: str) -> dict[str, Any] | None:
    candidates = [
        item for item in program["evidence_records"]
        if item.get("asset_id") == asset["id"]
        and item.get("asset_version") == asset["version"]
        and item.get("asset_sha256") == asset["sha256"]
        and item.get("category") == category
    ]
    return max(candidates, key=lambda item: item["sequence"], default=None)


def medical_status(program: dict[str, Any], asset: dict[str, Any]) -> str:
    if not asset.get("medical_applicable"):
        return "not_applicable"
    record = matching_medical_verification(program, asset)
    return "verified" if record and record["verdict"] == "VERIFIED" and record["independent"] else "unverified"


def required_aesthetic_reviews(asset: dict[str, Any]) -> set[str]:
    return {"brand", "visual"} if asset["class"] in {"S", "A"} else {"visual"}


def required_review_gates(asset: dict[str, Any], family: str) -> set[str]:
    """Return every non-compensable gate a PASS review must explicitly attest."""
    return set(BASE_HARD_GATES.get(family, set())) | set(
        TYPE_HARD_GATES.get(str(asset.get("type")), {}).get(family, set())
    )


def required_promotion_reviews(asset: dict[str, Any]) -> set[str]:
    families = required_aesthetic_reviews(asset)
    if asset.get("type") in PRODUCTION_REVIEW_TYPES:
        families.add("production")
    if asset.get("type") in ACCESSIBILITY_REVIEW_TYPES:
        families.add("accessibility_safety")
    if asset.get("medical_applicable") or asset.get("type") in {"safety", "gentle_closure"}:
        families.add("medical")
    return families


def pass_review_errors(review: dict[str, Any], asset: dict[str, Any]) -> list[str]:
    if review.get("verdict") != "PASS":
        return []
    gates = review.get("hard_gates")
    if not isinstance(gates, dict) or not gates:
        return ["PASS review has no hard-gate attestations"]
    missing = sorted(required_review_gates(asset, str(review.get("family"))) - {
        key for key, passed in gates.items() if passed is True
    })
    errors = [f"PASS review is missing required hard gates: {', '.join(missing)}"] if missing else []
    failed = sorted(key for key, passed in gates.items() if passed is not True)
    if failed:
        errors.append("PASS review contains failed hard gates: " + ", ".join(failed))
    return errors


def rights_errors(rights: Any, *, label: str) -> list[str]:
    errors: list[str] = []
    required = {
        "status", "commercial_use_allowed", "derivative_use_allowed", "attribution_required",
        "attribution_text", "evidence_refs",
    }
    if not isinstance(rights, dict):
        return [f"{label} must be an object"]
    strict_keys(rights, required, required, label, errors)
    status = rights.get("status")
    if status not in RIGHTS_STATUSES:
        errors.append(f"{label}.status is invalid")
    for field in ("commercial_use_allowed", "derivative_use_allowed", "attribution_required"):
        if not isinstance(rights.get(field), bool):
            errors.append(f"{label}.{field} must be boolean")
    attribution = rights.get("attribution_text")
    if attribution is not None and (not isinstance(attribution, str) or not attribution.strip()):
        errors.append(f"{label}.attribution_text must be null or a non-empty string")
    if rights.get("attribution_required") is True and not attribution:
        errors.append(f"{label} requires attribution_text")
    refs = rights.get("evidence_refs")
    if not isinstance(refs, list) or not all(
        isinstance(item, str) and item.strip() and len(item) <= 500 for item in refs
    ) or len(refs or []) != len(set(refs or [])):
        errors.append(f"{label}.evidence_refs must be a unique string array")
        refs = []
    if status == "unverified" and (
        rights.get("commercial_use_allowed") is True or rights.get("derivative_use_allowed") is True
    ):
        errors.append(f"{label} cannot grant use while status is unverified")
    if status in VERIFIED_RIGHTS_STATUSES and not refs:
        errors.append(f"{label} requires evidence_refs for a verified status")
    if status == "not_applicable" and not any(str(item).startswith("RIGHTS-NA:") for item in refs):
        errors.append(f"{label} not_applicable requires an explicit RIGHTS-NA: attestation")
    return errors


def rights_are_promotable(rights: Any) -> bool:
    if rights_errors(rights, label="rights"):
        return False
    assert isinstance(rights, dict)
    return (
        rights.get("status") in VERIFIED_RIGHTS_STATUSES
        and rights.get("commercial_use_allowed") is True
        and rights.get("derivative_use_allowed") is True
    )


def safe_text(value: Any, *, label: str, minimum: int = 1, maximum: int = 300) -> str:
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum or any(
        character in value for character in ("\x00", "\r", "\n")
    ):
        raise VisualStateError(f"{label} must be a single-line string of {minimum}-{maximum} characters")
    return value.strip()


def validate_privacy_record(privacy: Any, *, label: str) -> list[str]:
    errors: list[str] = []
    required = {"classification", "content_origin", "persistent_evidence_allowed", "external_egress"}
    if not isinstance(privacy, dict):
        return [f"{label} must be an object"]
    strict_keys(privacy, required, required, label, errors)
    if privacy.get("classification") not in PRIVACY_CLASSIFICATIONS - {"unclassified"}:
        errors.append(f"{label}.classification must be explicit and classified")
    if privacy.get("content_origin") not in REPOSITORY_SAFE_ORIGINS:
        errors.append(f"{label}.content_origin is not repository-safe")
    if privacy.get("persistent_evidence_allowed") is not True:
        errors.append(f"{label}.persistent_evidence_allowed must be true")
    egress = privacy.get("external_egress")
    if not isinstance(egress, dict):
        errors.append(f"{label}.external_egress must be an object")
    else:
        strict_keys(egress, {"status", "receipt_ref"}, {"status", "receipt_ref"}, f"{label}.external_egress", errors)
        if egress.get("status") not in EGRESS_STATUSES:
            errors.append(f"{label}.external_egress.status is invalid")
        receipt = egress.get("receipt_ref")
        if egress.get("status") == "confirmed_per_send" and (
            not isinstance(receipt, str) or not receipt.strip()
        ):
            errors.append(f"{label}.external_egress confirmed_per_send requires receipt_ref")
        if receipt is not None and (not isinstance(receipt, str) or not receipt.strip() or len(receipt) > 300):
            errors.append(f"{label}.external_egress.receipt_ref is invalid")
    return errors


def provenance_sidecar_path(source: Path) -> Path:
    return source.with_suffix(".provenance.json")


def validate_local_provenance(
    root: Path, source: Path, rel: str, *, purpose: str, require_rights: bool = True,
) -> str:
    """Validate the immutable, privacy-safe provenance sidecar for local prompts/references."""
    sidecar = provenance_sidecar_path(source)
    document = load_json(sidecar)
    if document.get("path") != rel:
        raise VisualStateError(f"{purpose} provenance path does not match source: {sidecar}")
    expected = document.get("sha256")
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected) or sha256_file(source) != expected:
        raise VisualStateError(f"{purpose} provenance SHA-256 mismatch: {sidecar}")
    privacy_errors = validate_privacy_record(document.get("privacy"), label=f"{purpose} provenance privacy")
    if privacy_errors:
        raise VisualStateError("; ".join(privacy_errors))
    if not require_rights:
        return sidecar.relative_to(root).as_posix()
    raw_rights = document.get("rights")
    if not isinstance(raw_rights, dict):
        raise VisualStateError(f"{purpose} provenance rights must be an object: {sidecar}")
    derivative = raw_rights.get("derivative_use_allowed", raw_rights.get("derivative_asset_use_allowed"))
    rights = {
        "status": raw_rights.get("status"),
        "commercial_use_allowed": raw_rights.get("commercial_use_allowed"),
        "derivative_use_allowed": derivative,
        "attribution_required": raw_rights.get("attribution_required"),
        "attribution_text": raw_rights.get("attribution_text"),
        "evidence_refs": raw_rights.get("evidence_refs"),
    }
    if rights["attribution_text"] is None and raw_rights.get("attribution_required") is False:
        rights["attribution_text"] = None
    provenance_role = document.get("reference_role")
    if rights.get("status") == "unverified" and purpose == "reference":
        prohibited = document.get("prohibited_roles")
        if (
            provenance_role != "inspiration_only"
            or rights.get("commercial_use_allowed") is not False
            or rights.get("derivative_use_allowed") is not False
            or not isinstance(prohibited, list)
            or "automatic_rights_clearance" not in prohibited
        ):
            raise VisualStateError("unverified reference rights are allowed only for quarantined inspiration-only input")
    else:
        problems = rights_errors(rights, label=f"{purpose} provenance rights")
        if problems or not rights_are_promotable(rights):
            raise VisualStateError("; ".join(problems or [f"{purpose} provenance rights do not allow commercial derivatives"]))
    if purpose == "medical source" and rights.get("status") == "public_domain" and not any(
        str(item).startswith("PUBLIC-CLINICAL-SOURCE:") for item in rights.get("evidence_refs", [])
    ):
        raise VisualStateError(
            "public-domain medical source provenance requires PUBLIC-CLINICAL-SOURCE: authorization evidence"
        )
    return sidecar.relative_to(root).as_posix()


def current_evidence_records(
    program: dict[str, Any], asset: dict[str, Any], category: str, source_tag: str, build_hash: str,
) -> list[dict[str, Any]]:
    """Return the current record per role/platform for one immutable build binding."""
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for item in program["evidence_records"]:
        if (
            item.get("asset_id") != asset["id"]
            or item.get("asset_version") != asset["version"]
            or item.get("asset_sha256") != asset["sha256"]
            or item.get("category") != category
            or item.get("source_tag") != source_tag
            or item.get("build_hash") != build_hash
        ):
            continue
        key = (str(item.get("verifier_role")), str(item.get("platform")))
        if key not in latest or item.get("sequence", 0) > latest[key].get("sequence", 0):
            latest[key] = item
    return list(latest.values())


def evidence_gate_errors(
    program: dict[str, Any], asset: dict[str, Any], *, target: str, source_tag: str, build_hash: str,
) -> list[str]:
    errors: list[str] = []

    def credential_hash(item: dict[str, Any]) -> str | None:
        path = item.get("credential_or_attestation")
        hashes = item.get("artifact_sha256")
        return hashes.get(path) if isinstance(path, str) and isinstance(hashes, dict) else None

    def passing(category: str) -> list[dict[str, Any]]:
        return [
            item for item in current_evidence_records(program, asset, category, source_tag, build_hash)
            if item.get("verdict") == "PASS" and item.get("independent") is True
        ]

    integration = passing("integration")
    if not integration:
        errors.append("same-build independent integration PASS evidence is required")
    if target in {"matrix_accepted", "release_signed"}:
        grouped = {category: passing(category) for category in ("production", "accessibility", "matrix")}
        for category, records in grouped.items():
            if not records:
                errors.append(f"same-build independent {category} PASS evidence is required")
        all_matrix_records = [item for records in grouped.values() for item in records]
        if len({item.get("verifier", "").casefold() for item in all_matrix_records}) < 3:
            errors.append("matrix acceptance requires at least three distinct independent verifiers")
        if len({credential_hash(item) for item in all_matrix_records if credential_hash(item)}) < 3:
            errors.append("matrix acceptance requires at least three content-distinct credential/attestation artifacts")
        if asset.get("type") in DUAL_PLATFORM_MATRIX_TYPES:
            matrix_platforms = {item.get("platform") for item in grouped["matrix"]}
            missing_platforms = sorted({"android", "ios"} - matrix_platforms)
            if missing_platforms:
                errors.append("matrix PASS evidence is missing platform coverage: " + ", ".join(missing_platforms))
    if target == "release_signed":
        release_records = current_evidence_records(program, asset, "release", source_tag, build_hash)
        latest_by_role: dict[str, dict[str, Any]] = {}
        for item in release_records:
            role = str(item.get("verifier_role"))
            current = latest_by_role.get(role)
            if current is None or item.get("sequence", 0) > current.get("sequence", 0):
                latest_by_role[role] = item
        missing_roles = sorted(
            role for role in RELEASE_SIGNING_ROLES
            if role not in latest_by_role
            or latest_by_role[role].get("verdict") != "PASS"
            or latest_by_role[role].get("independent") is not True
        )
        if missing_roles:
            errors.append("release requires independent same-build PASS sign-off from: " + ", ".join(missing_roles))
        selected = [latest_by_role[role] for role in RELEASE_SIGNING_ROLES if role in latest_by_role]
        if len({item.get("verifier", "").casefold() for item in selected}) != len(selected):
            errors.append("release sign-off roles must be represented by distinct verifier identities")
        credential_hashes = [credential_hash(item) for item in selected]
        if None in credential_hashes or len(set(credential_hashes)) != len(selected):
            errors.append("release sign-off roles require content-distinct signed credential/attestation artifacts")
    return errors


def validate_program(root: Path, program: dict[str, Any], *, check_files: bool = True) -> list[str]:
    errors: list[str] = []
    top_required = {
        "schema_version", "program_id", "revision", "created_at", "updated_at", "visual_version",
        "contract_version", "current_gate", "release_status", "golden_slots", "assets", "decisions",
        "reviews", "medical_sources", "medical_verifications", "evidence_records", "operations",
        "migration_history",
    }
    strict_keys(program, top_required, top_required, "visual_program", errors)
    if program.get("schema_version") != PROGRAM_SCHEMA:
        errors.append(f"visual_program schema_version must be {PROGRAM_SCHEMA}")
    if program.get("program_id") != PROGRAM_ID:
        errors.append(f"visual_program program_id must be {PROGRAM_ID}")
    if not isinstance(program.get("revision"), int) or program.get("revision", -1) < 0:
        errors.append("visual_program revision must be a non-negative integer")
    if not isinstance(program.get("visual_version"), str) or not SEMVER_RE.fullmatch(program["visual_version"]):
        errors.append("visual_program visual_version must be Semantic Versioning")
    if not isinstance(program.get("contract_version"), str) or not program["contract_version"].strip():
        errors.append("visual_program contract_version must be non-empty")
    if not isinstance(program.get("current_gate"), str) or not re.fullmatch(r"[A-Z0-9_\-]{2,80}", program["current_gate"]):
        errors.append("visual_program current_gate must be a safe uppercase identifier")
    if program.get("release_status") not in RELEASE_STATUSES:
        errors.append("visual_program release_status is invalid")
    parse_iso(program.get("created_at"), "visual_program.created_at", errors)
    parse_iso(program.get("updated_at"), "visual_program.updated_at", errors)
    for collection in (
        "assets", "decisions", "reviews", "medical_sources", "medical_verifications",
        "evidence_records", "operations", "migration_history",
    ):
        if not isinstance(program.get(collection), list):
            errors.append(f"visual_program.{collection} must be an array")
    if errors:
        return sorted(set([*errors, *validate_design_tokens(root, program)]))

    assets = program["assets"]
    decisions = program["decisions"]
    reviews = program["reviews"]
    sources = program["medical_sources"]
    verifications = program["medical_verifications"]
    evidence = program["evidence_records"]
    operations = program["operations"]
    for items, label in (
        (assets, "asset"), (decisions, "decision"), (reviews, "review"),
        (sources, "medical source"), (verifications, "medical verification"),
        (evidence, "evidence"), (operations, "operation"),
    ):
        require_unique(items, label, errors)

    asset_ids = {item.get("id") for item in assets}
    decision_ids = {item.get("id") for item in decisions}
    source_ids = {item.get("id") for item in sources}
    review_ids = {item.get("id") for item in reviews}

    asset_required = {
        "id", "name", "class", "type", "lifecycle_stage", "freshness", "evidence_stage", "version", "path",
        "sha256", "golden", "parents", "references", "depends_on", "created_by", "tool", "model",
        "prompt_path", "medical_applicable", "privacy", "rights", "evidence_binding", "stale_reasons",
        "created_at", "updated_at", "notes",
    }
    for asset in assets:
        label = f"asset {asset.get('id', '<missing>')}"
        strict_keys(asset, asset_required, asset_required, label, errors)
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not ASSET_ID_RE.fullmatch(asset_id):
            errors.append(f"invalid asset id: {asset_id}")
        if not isinstance(asset.get("name"), str) or not asset["name"].strip() or len(asset["name"]) > 200:
            errors.append(f"invalid name for {label}")
        if asset.get("class") not in ASSET_CLASSES:
            errors.append(f"invalid class for {label}")
        if asset.get("type") not in ASSET_TYPES:
            errors.append(f"invalid type for {label}")
        if asset.get("lifecycle_stage") not in LIFECYCLE_STAGES:
            errors.append(f"invalid lifecycle_stage for {label}")
        if asset.get("freshness") not in FRESHNESS_STATES:
            errors.append(f"invalid freshness for {label}")
        if asset.get("evidence_stage") not in EVIDENCE_STAGES:
            errors.append(f"invalid evidence_stage for {label}")
        stale_reasons = asset.get("stale_reasons")
        if not isinstance(stale_reasons, list):
            errors.append(f"stale_reasons must be an array for {label}")
            stale_reasons = []
        else:
            seen_stale_reasons: set[str] = set()
            for index, reason in enumerate(stale_reasons):
                reason_label = f"{label}.stale_reasons[{index}]"
                required_reason = {"code", "source_asset_id", "detail", "recorded_at"}
                if not isinstance(reason, dict):
                    errors.append(f"{reason_label} must be an object")
                    continue
                strict_keys(reason, required_reason, required_reason, reason_label, errors)
                if reason.get("code") not in STALE_REASON_CODES:
                    errors.append(f"invalid stale reason code for {reason_label}")
                if reason.get("source_asset_id") is not None and reason.get("source_asset_id") not in asset_ids:
                    errors.append(f"missing source asset for {reason_label}")
                if not isinstance(reason.get("detail"), str) or not reason["detail"].strip():
                    errors.append(f"detail must be non-empty for {reason_label}")
                parse_iso(reason.get("recorded_at"), f"{reason_label}.recorded_at", errors)
                signature = canonical_json(reason)
                if signature in seen_stale_reasons:
                    errors.append(f"duplicate structured stale reason for {label}")
                seen_stale_reasons.add(signature)
        if asset.get("freshness") == "current" and stale_reasons:
            errors.append(f"current asset must not carry stale_reasons: {label}")
        if asset.get("freshness") in {"stale", "stale_contract_conflict"} and not stale_reasons:
            errors.append(f"stale asset must carry structured stale_reasons: {label}")
        if asset.get("freshness") == "stale_contract_conflict" and not any(
            reason.get("code") == "contract_conflict" for reason in stale_reasons if isinstance(reason, dict)
        ):
            errors.append(f"stale_contract_conflict requires a contract_conflict reason: {label}")
        if not isinstance(asset.get("version"), int) or asset["version"] < 1:
            errors.append(f"invalid version for {label}")
        if not isinstance(asset.get("sha256"), str) or not SHA256_RE.fullmatch(asset["sha256"]):
            errors.append(f"invalid sha256 for {label}")
        if not isinstance(asset.get("created_by"), str) or not asset["created_by"].strip():
            errors.append(f"created_by must be non-empty for {label}")
        if not isinstance(asset.get("medical_applicable"), bool):
            errors.append(f"medical_applicable must be boolean for {label}")
        if asset.get("type") in AUTO_MEDICAL_ASSET_TYPES and asset.get("medical_applicable") is not True:
            errors.append(f"{asset.get('type')} assets must be medical_applicable: {label}")
        privacy = asset.get("privacy")
        privacy_required = {
            "classification", "content_origin", "persistent_evidence_allowed", "external_egress",
            "cleanup_scope",
        }
        if not isinstance(privacy, dict):
            errors.append(f"privacy must be an object for {label}")
        else:
            strict_keys(privacy, privacy_required, privacy_required, f"{label}.privacy", errors)
            if privacy.get("classification") not in PRIVACY_CLASSIFICATIONS:
                errors.append(f"invalid privacy classification for {label}")
            if privacy.get("content_origin") not in CONTENT_ORIGINS:
                errors.append(f"invalid privacy content_origin for {label}")
            if not isinstance(privacy.get("persistent_evidence_allowed"), bool):
                errors.append(f"persistent_evidence_allowed must be boolean for {label}")
            cleanup = privacy.get("cleanup_scope")
            if not isinstance(cleanup, list) or not cleanup or not all(
                isinstance(item, str) and item in CLEANUP_SCOPES for item in cleanup
            ) or len(cleanup) != len(set(cleanup)):
                errors.append(f"cleanup_scope must be a non-empty unique frozen-enum array for {label}")
            egress = privacy.get("external_egress")
            if not isinstance(egress, dict):
                errors.append(f"external_egress must be an object for {label}")
            else:
                strict_keys(
                    egress, {"status", "receipt_ref"}, {"status", "receipt_ref"},
                    f"{label}.privacy.external_egress", errors,
                )
                if egress.get("status") not in EGRESS_STATUSES:
                    errors.append(f"invalid external egress status for {label}")
                receipt = egress.get("receipt_ref")
                if receipt is not None and (
                    not isinstance(receipt, str) or not receipt.strip() or len(receipt) > 300
                ):
                    errors.append(f"external egress receipt_ref is invalid for {label}")
                if egress.get("status") == "confirmed_per_send" and not receipt:
                    errors.append(f"confirmed_per_send requires a non-empty receipt_ref for {label}")
            if privacy.get("content_origin") == "real_sensitive" and privacy.get("persistent_evidence_allowed"):
                errors.append(f"real_sensitive content can never allow persistent repository evidence: {label}")
            if privacy.get("content_origin") in {"real_sensitive", "unknown"}:
                errors.append(f"real_sensitive/unknown content cannot be a repository visual asset: {label}")
            if privacy.get("classification") == "unclassified":
                errors.append(f"unclassified content cannot be a repository visual asset: {label}")
        errors.extend(rights_errors(asset.get("rights"), label=f"{label}.rights"))
        binding = asset.get("evidence_binding")
        if binding is not None:
            if not isinstance(binding, dict):
                errors.append(f"evidence_binding must be null or an object for {label}")
            else:
                binding_required = {"source_tag", "build_hash", "bound_at"}
                strict_keys(binding, binding_required, binding_required, f"{label}.evidence_binding", errors)
                try:
                    safe_text(binding.get("source_tag"), label=f"{label}.evidence_binding.source_tag", minimum=2, maximum=200)
                    safe_text(binding.get("build_hash"), label=f"{label}.evidence_binding.build_hash", minimum=7, maximum=200)
                except VisualStateError as exc:
                    errors.append(str(exc))
                parse_iso(binding.get("bound_at"), f"{label}.evidence_binding.bound_at", errors)
        if asset.get("evidence_stage") in {"concept", "aesthetic_golden"} and binding is not None:
            errors.append(f"pre-integration asset must not carry evidence_binding: {label}")
        if asset.get("evidence_stage") in {"integrated", "matrix_accepted", "release_signed"} and binding is None:
            errors.append(f"advanced evidence asset requires evidence_binding: {label}")
        for relation in ("parents", "depends_on", "references", "notes"):
            if not isinstance(asset.get(relation), list) or not all(isinstance(v, str) for v in asset.get(relation, [])):
                errors.append(f"{relation} must be a string array for {label}")
        for relation in ("parents", "depends_on"):
            for related in asset.get(relation, []):
                if related not in asset_ids:
                    errors.append(f"{label} references missing {relation} asset {related}")
                if related == asset_id:
                    errors.append(f"{label} cannot depend on itself")
        for reference in asset.get("references", []):
            try:
                validate_reference(root, reference)
            except VisualStateError as exc:
                errors.append(f"{label}: {exc}")
        parse_iso(asset.get("created_at"), f"{label}.created_at", errors)
        parse_iso(asset.get("updated_at"), f"{label}.updated_at", errors)
        try:
            path, rel = visual_path(
                root, str(asset.get("path", "")), must_exist=False,
                allowed_prefixes=ASSET_AREA_PREFIXES,
            )
            if rel != asset.get("path"):
                errors.append(f"non-canonical path for {label}: {asset.get('path')}")
            if check_files and asset.get("lifecycle_stage") not in {"deprecated", "rejected"}:
                if not path.is_file():
                    errors.append(f"asset file missing for {label}: {rel}")
                elif not SHA256_RE.fullmatch(str(asset.get("sha256", ""))) or sha256_file(path) != asset.get("sha256"):
                    errors.append(f"asset hash mismatch for {label}")
        except VisualStateError as exc:
            errors.append(f"{label}: {exc}")
        prompt = asset.get("prompt_path")
        if prompt is not None:
            try:
                prompt_file, prompt_rel = visual_path(
                    root, str(prompt), must_exist=check_files, allowed_prefixes=("visual/prompts/",)
                )
                if prompt_rel != prompt:
                    errors.append(f"non-canonical prompt_path for {label}")
                if check_files:
                    validate_local_provenance(root, prompt_file, prompt_rel, purpose="prompt")
            except VisualStateError as exc:
                errors.append(f"{label}: {exc}")
        golden = asset.get("golden")
        if golden is not None:
            privacy = asset.get("privacy") if isinstance(asset.get("privacy"), dict) else {}
            if not privacy.get("persistent_evidence_allowed") or privacy.get("content_origin") in {"real_sensitive", "unknown"}:
                errors.append(f"Golden content is forbidden by privacy policy for {label}")
            if not rights_are_promotable(asset.get("rights")):
                errors.append(f"Golden content lacks verified commercial/derivative rights for {label}")
            if not isinstance(golden, dict) or set(golden) != {
                "path", "sha256", "decision_id", "approved_at", "asset_version"
            }:
                errors.append(f"invalid golden record for {label}")
            else:
                try:
                    golden_path, golden_rel = visual_path(
                        root, str(golden.get("path", "")), must_exist=check_files,
                        allowed_prefixes=("visual/golden/sha256/",),
                    )
                    expected_prefix = f"visual/golden/sha256/{str(asset.get('sha256', ''))[:2]}/{asset.get('sha256')}"
                    if not golden_rel.startswith(expected_prefix):
                        errors.append(f"Golden path is not content-addressed for {label}")
                    if check_files and golden_path.is_file() and sha256_file(golden_path) != golden.get("sha256"):
                        errors.append(f"Golden hash mismatch for {label}")
                except VisualStateError as exc:
                    errors.append(f"{label}: {exc}")
                if golden.get("sha256") != asset.get("sha256") or golden.get("asset_version") != asset.get("version"):
                    errors.append(f"Golden binding mismatch for {label}")
                if golden.get("decision_id") not in decision_ids:
                    errors.append(f"Golden decision missing for {label}")
            if asset.get("lifecycle_stage") not in {"aesthetic_golden", "deprecated"}:
                errors.append(f"asset with Golden content has invalid lifecycle for {label}")

    errors.extend(dependency_cycles(assets))

    decision_required = {
        "id", "occurred_at", "kind", "status", "decided_by", "asset_ids", "text", "preserve", "change"
    }
    for item in decisions:
        label = f"decision {item.get('id', '<missing>')}"
        strict_keys(item, decision_required, decision_required, label, errors)
        if not isinstance(item.get("id"), str) or not DECISION_ID_RE.fullmatch(item["id"]):
            errors.append(f"invalid decision id: {item.get('id')}")
        if item.get("kind") not in DECISION_KINDS or item.get("status") not in DECISION_STATUSES:
            errors.append(f"invalid kind/status for {label}")
        if not isinstance(item.get("decided_by"), str) or not item["decided_by"].strip():
            errors.append(f"missing decided_by for {label}")
        if not isinstance(item.get("asset_ids"), list):
            errors.append(f"asset_ids must be an array for {label}")
        else:
            for asset_id in item["asset_ids"]:
                if asset_id not in asset_ids:
                    errors.append(f"{label} references missing asset {asset_id}")
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            errors.append(f"empty text for {label}")
        for key in ("preserve", "change"):
            if not isinstance(item.get(key), list) or not all(isinstance(v, str) for v in item.get(key, [])):
                errors.append(f"{label}.{key} must be a string array")
        parse_iso(item.get("occurred_at"), f"{label}.occurred_at", errors)

    review_required = {
        "id", "created_at", "reviewer", "reviewer_kind", "family", "independent", "asset_id",
        "asset_version", "asset_sha256", "visual_version", "contract_version", "sequence",
        "previous_review_id", "verdict", "hard_gates", "score", "recommendation", "findings",
        "blocking_issues",
    }
    sequence_keys: set[tuple[str, str, int]] = set()
    for item in reviews:
        label = f"review {item.get('id', '<missing>')}"
        strict_keys(item, review_required, review_required, label, errors)
        if not isinstance(item.get("id"), str) or not REVIEW_ID_RE.fullmatch(item["id"]):
            errors.append(f"invalid review id: {item.get('id')}")
        if item.get("family") not in REVIEW_FAMILIES or item.get("verdict") not in VERDICTS:
            errors.append(f"invalid family/verdict for {label}")
        if item.get("reviewer_kind") not in REVIEWER_KINDS or not isinstance(item.get("independent"), bool):
            errors.append(f"invalid reviewer metadata for {label}")
        asset = next((a for a in assets if a.get("id") == item.get("asset_id")), None)
        if not asset:
            errors.append(f"{label} references missing asset {item.get('asset_id')}")
        elif item.get("asset_version") != asset.get("version") or item.get("asset_sha256") != asset.get("sha256"):
            # Historical reviews may remain after a version update, but assets are immutable in this tool.
            errors.append(f"{label} binding does not match immutable asset")
        sequence = item.get("sequence")
        key = (str(item.get("asset_id")), str(item.get("family")), sequence)
        if not isinstance(sequence, int) or sequence < 1 or key in sequence_keys:
            errors.append(f"invalid or duplicate review sequence for {label}")
        sequence_keys.add(key)
        previous = item.get("previous_review_id")
        if previous is not None and previous not in review_ids:
            errors.append(f"missing previous review {previous} for {label}")
        if item.get("score") is not None and (
            not isinstance(item["score"], (int, float)) or not 0 <= item["score"] <= 100
        ):
            errors.append(f"invalid score for {label}")
        if not isinstance(item.get("hard_gates"), dict) or not all(
            isinstance(key, str) and isinstance(value, bool) for key, value in item.get("hard_gates", {}).items()
        ):
            errors.append(f"hard_gates must be a string-to-boolean object for {label}")
        elif asset:
            errors.extend(f"{label}: {problem}" for problem in pass_review_errors(item, asset))
        for key in ("findings", "blocking_issues"):
            if not isinstance(item.get(key), list) or not all(isinstance(v, str) for v in item.get(key, [])):
                errors.append(f"{label}.{key} must be a string array")
        parse_iso(item.get("created_at"), f"{label}.created_at", errors)

    for asset_id in asset_ids:
        for family in REVIEW_FAMILIES:
            chain = sorted(
                (item for item in reviews if item.get("asset_id") == asset_id and item.get("family") == family),
                key=lambda item: item.get("sequence", 0),
            )
            for index, item in enumerate(chain, start=1):
                expected_previous = chain[index - 2]["id"] if index > 1 else None
                if item.get("sequence") != index or item.get("previous_review_id") != expected_previous:
                    errors.append(f"review chain is not contiguous for {asset_id}/{family} at {item.get('id')}")

    source_required = {
        "id", "asset_id", "title", "authority", "jurisdiction", "population", "gestational_stage",
        "source_version", "publication_date", "source_revision_date", "accessed_date", "source_url",
        "fixed_reference", "source_checksum", "document_path", "document_sha256", "notes", "created_at",
    }
    for item in sources:
        label = f"medical source {item.get('id', '<missing>')}"
        strict_keys(item, source_required, source_required, label, errors)
        if not isinstance(item.get("id"), str) or not SOURCE_ID_RE.fullmatch(item["id"]):
            errors.append(f"invalid medical source id: {item.get('id')}")
        if item.get("asset_id") not in asset_ids:
            errors.append(f"{label} references missing asset")
        for key in ("title", "authority", "jurisdiction", "population", "gestational_stage", "source_version"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{label}.{key} must be non-empty")
        for key in ("publication_date", "source_revision_date", "accessed_date"):
            if not isinstance(item.get(key), str) or not DATE_RE.fullmatch(item[key]):
                errors.append(f"{label}.{key} must be YYYY-MM-DD")
        if all(
            isinstance(item.get(key), str) and DATE_RE.fullmatch(item[key])
            for key in ("publication_date", "source_revision_date", "accessed_date")
        ):
            try:
                publication = dt.date.fromisoformat(item["publication_date"])
                revision = dt.date.fromisoformat(item["source_revision_date"])
                accessed = dt.date.fromisoformat(item["accessed_date"])
                if publication > revision or revision > accessed:
                    errors.append(f"{label} dates must satisfy publication <= revision <= accessed")
            except ValueError:
                errors.append(f"{label} has an invalid calendar date")
        url = item.get("source_url")
        document = item.get("document_path")
        if not url and not document:
            errors.append(f"{label} needs source_url or document_path")
        if url:
            parsed = urlparse(str(url))
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"invalid source_url for {label}")
        if document:
            try:
                document_path, document_rel = visual_path(
                    root, str(document), must_exist=check_files, allowed_prefixes=("visual/references/",),
                )
                if document_rel != document:
                    errors.append(f"non-canonical document_path for {label}")
                if check_files and document_path.is_file():
                    if sha256_file(document_path) != item.get("document_sha256"):
                        errors.append(f"medical document hash mismatch for {label}")
                    validate_local_provenance(
                        root, document_path, document_rel, purpose="medical source", require_rights=True,
                    )
            except VisualStateError as exc:
                errors.append(f"{label}: {exc}")
        elif item.get("document_sha256") is not None:
            errors.append(f"{label}.document_sha256 must be null without document_path")
        checksum = item.get("source_checksum")
        fixed_reference = item.get("fixed_reference")
        if checksum is not None and (not isinstance(checksum, str) or not SHA256_RE.fullmatch(checksum)):
            errors.append(f"{label}.source_checksum must be null or a lowercase SHA-256")
        if fixed_reference is not None and (
            not isinstance(fixed_reference, str) or not fixed_reference.strip() or len(fixed_reference) > 500
        ):
            errors.append(f"{label}.fixed_reference must be null or a non-empty stable identifier")
        if url and not item.get("document_sha256") and not checksum:
            errors.append(f"{label} URL source requires source_checksum or a locally archived document hash")
        if not item.get("document_sha256") and not checksum:
            errors.append(f"{label} lacks content-addressed source evidence; fixed_reference is locator-only")
        if not isinstance(item.get("notes"), list) or not all(isinstance(v, str) for v in item.get("notes", [])):
            errors.append(f"{label}.notes must be a string array")

    verification_required = {
        "id", "created_at", "asset_id", "asset_version", "asset_sha256", "sequence", "verifier",
        "verifier_kind", "professional_role", "credential_ref", "independent", "source_ids", "scope",
        "verdict", "attestation_path", "attestation_sha256", "notes",
    }
    verification_sequences: set[tuple[str, int]] = set()
    for item in verifications:
        label = f"medical verification {item.get('id', '<missing>')}"
        strict_keys(item, verification_required, verification_required, label, errors)
        if not isinstance(item.get("id"), str) or not VERIFICATION_ID_RE.fullmatch(item["id"]):
            errors.append(f"invalid medical verification id: {item.get('id')}")
        asset = next((a for a in assets if a.get("id") == item.get("asset_id")), None)
        if not asset:
            errors.append(f"{label} references missing asset")
        elif item.get("asset_version") != asset["version"] or item.get("asset_sha256") != asset["sha256"]:
            errors.append(f"{label} binding does not match immutable asset")
        if item.get("professional_role") not in PROFESSIONAL_ROLES or item.get("verdict") not in MEDICAL_VERDICTS:
            errors.append(f"invalid professional role/verdict for {label}")
        if item.get("verifier_kind") not in REVIEWER_KINDS:
            errors.append(f"invalid verifier_kind for {label}")
        if item.get("verdict") == "VERIFIED" and item.get("verifier_kind") not in {"human", "external_specialist"}:
            errors.append(f"custom-agent/subagent can never issue VERIFIED for {label}")
        for key in ("verifier", "credential_ref", "scope"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{label}.{key} must be non-empty")
        if not isinstance(item.get("independent"), bool):
            errors.append(f"independent must be boolean for {label}")
        if not isinstance(item.get("source_ids"), list) or not item.get("source_ids"):
            errors.append(f"{label} requires source_ids")
        else:
            for source_id in item["source_ids"]:
                source = next((s for s in sources if s.get("id") == source_id), None)
                if not source or source.get("asset_id") != item.get("asset_id"):
                    errors.append(f"{label} has invalid source {source_id}")
        seq_key = (str(item.get("asset_id")), item.get("sequence"))
        if not isinstance(item.get("sequence"), int) or item["sequence"] < 1 or seq_key in verification_sequences:
            errors.append(f"invalid or duplicate sequence for {label}")
        verification_sequences.add(seq_key)
        if not isinstance(item.get("notes"), list) or not all(isinstance(v, str) for v in item.get("notes", [])):
            errors.append(f"{label}.notes must be a string array")
        try:
            attestation, attestation_rel = visual_path(
                root, str(item.get("attestation_path", "")), must_exist=check_files,
                allowed_prefixes=("visual/reviews/medical/", "visual/system/attestations/"),
            )
            if attestation_rel != item.get("attestation_path"):
                errors.append(f"non-canonical attestation_path for {label}")
            if not SHA256_RE.fullmatch(str(item.get("attestation_sha256", ""))):
                errors.append(f"invalid attestation_sha256 for {label}")
            elif check_files and attestation.is_file() and sha256_file(attestation) != item.get("attestation_sha256"):
                errors.append(f"medical attestation hash mismatch for {label}")
            if check_files and attestation.is_file():
                validate_local_provenance(
                    root, attestation, attestation_rel,
                    purpose="medical attestation", require_rights=False,
                )
        except VisualStateError as exc:
            errors.append(f"{label}: {exc}")
        parse_iso(item.get("created_at"), f"{label}.created_at", errors)

    for asset_id in asset_ids:
        chain = sorted(
            (item for item in verifications if item.get("asset_id") == asset_id),
            key=lambda item: item.get("sequence", 0),
        )
        if any(item.get("sequence") != index for index, item in enumerate(chain, start=1)):
            errors.append(f"medical verification chain is not contiguous for {asset_id}")

    evidence_required = {
        "id", "created_at", "asset_id", "asset_version", "asset_sha256", "category", "sequence",
        "source_tag", "build_hash", "platform", "os", "device", "test_suite", "verifier",
        "verifier_role", "credential_or_attestation", "independent", "verdict", "privacy",
        "artifact_paths", "artifact_sha256", "notes",
    }
    evidence_sequences: set[tuple[str, str, int]] = set()
    for item in evidence:
        label = f"evidence {item.get('id', '<missing>')}"
        strict_keys(item, evidence_required, evidence_required, label, errors)
        if not isinstance(item.get("id"), str) or not EVIDENCE_ID_RE.fullmatch(item["id"]):
            errors.append(f"invalid evidence id: {item.get('id')}")
        if item.get("category") not in EVIDENCE_CATEGORIES or item.get("verdict") not in VERDICTS:
            errors.append(f"invalid category/verdict for {label}")
        if not isinstance(item.get("verifier"), str) or not item["verifier"].strip() or not isinstance(item.get("independent"), bool):
            errors.append(f"invalid verifier metadata for {label}")
        for field, minimum in (("source_tag", 2), ("build_hash", 7), ("os", 1), ("device", 1), ("test_suite", 2)):
            try:
                safe_text(item.get(field), label=f"{label}.{field}", minimum=minimum, maximum=300)
            except VisualStateError as exc:
                errors.append(str(exc))
        if item.get("platform") not in EVIDENCE_PLATFORMS:
            errors.append(f"invalid platform for {label}")
        role = item.get("verifier_role")
        if role not in EVIDENCE_VERIFIER_ROLES:
            errors.append(f"invalid verifier_role for {label}")
        if item.get("category") in EVIDENCE_ROLE_BY_CATEGORY and role not in EVIDENCE_ROLE_BY_CATEGORY[item["category"]]:
            errors.append(f"verifier_role {role} is not authorized for {label}")
        errors.extend(validate_privacy_record(item.get("privacy"), label=f"{label}.privacy"))
        asset = next((a for a in assets if a.get("id") == item.get("asset_id")), None)
        if not asset:
            errors.append(f"{label} references missing asset")
        elif item.get("asset_version") != asset["version"] or item.get("asset_sha256") != asset["sha256"]:
            errors.append(f"{label} binding does not match immutable asset")
        paths = item.get("artifact_paths")
        hashes = item.get("artifact_sha256")
        if not isinstance(paths, list) or not paths or not isinstance(hashes, dict) or set(paths) != set(hashes):
            errors.append(f"{label} requires matching non-empty artifact_paths/artifact_sha256")
        else:
            for value in paths:
                try:
                    path, rel = visual_path(
                        root, value, must_exist=check_files,
                        allowed_prefixes=("visual/reviews/", "visual/system/attestations/"),
                    )
                    if rel != value:
                        errors.append(f"non-canonical artifact path for {label}")
                    if check_files and path.is_file() and sha256_file(path) != hashes.get(value):
                        errors.append(f"artifact hash mismatch for {label}: {value}")
                except VisualStateError as exc:
                    errors.append(f"{label}: {exc}")
                if not SHA256_RE.fullmatch(str(hashes.get(value, ""))):
                    errors.append(f"invalid artifact SHA-256 for {label}: {value}")
        credential_path = item.get("credential_or_attestation")
        if not isinstance(credential_path, str) or credential_path not in (paths or []):
            errors.append(f"{label}.credential_or_attestation must name one hashed artifact_path")
        seq_key = (str(item.get("asset_id")), str(item.get("category")), item.get("sequence"))
        if not isinstance(item.get("sequence"), int) or item["sequence"] < 1 or seq_key in evidence_sequences:
            errors.append(f"invalid or duplicate evidence sequence for {label}")
        evidence_sequences.add(seq_key)
        if not isinstance(item.get("notes"), list) or not all(isinstance(v, str) for v in item.get("notes", [])):
            errors.append(f"{label}.notes must be a string array")
        parse_iso(item.get("created_at"), f"{label}.created_at", errors)

    for asset_id in asset_ids:
        for category in EVIDENCE_CATEGORIES:
            chain = sorted(
                (
                    item for item in evidence
                    if item.get("asset_id") == asset_id and item.get("category") == category
                ),
                key=lambda item: item.get("sequence", 0),
            )
            if any(item.get("sequence") != index for index, item in enumerate(chain, start=1)):
                errors.append(f"evidence chain is not contiguous for {asset_id}/{category}")

    operation_required = {"id", "command", "fingerprint", "committed_revision", "created_at", "result"}
    for item in operations:
        label = f"operation {item.get('id', '<missing>')}"
        strict_keys(item, operation_required, operation_required, label, errors)
        if not isinstance(item.get("id"), str) or not OPERATION_ID_RE.fullmatch(item["id"]):
            errors.append(f"invalid operation id: {item.get('id')}")
        if not SHA256_RE.fullmatch(str(item.get("fingerprint", ""))):
            errors.append(f"invalid fingerprint for {label}")
        if not isinstance(item.get("committed_revision"), int) or item["committed_revision"] < 1:
            errors.append(f"invalid committed_revision for {label}")
        if not isinstance(item.get("command"), str) or item["command"] not in COMMANDS:
            errors.append(f"invalid command for {label}")
        if not isinstance(item.get("result"), dict):
            errors.append(f"result must be an object for {label}")
        parse_iso(item.get("created_at"), f"{label}.created_at", errors)

    migration_required = {
        "from", "to_schema", "migrated_at", "backup_path", "backup_manifest_sha256", "warnings"
    }
    for index, item in enumerate(program["migration_history"]):
        label = f"migration_history[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        strict_keys(item, migration_required, migration_required, label, errors)
        if item.get("from") != "legacy-v2-projections" or item.get("to_schema") != PROGRAM_SCHEMA:
            errors.append(f"{label} has unsupported migration endpoints")
        parse_iso(item.get("migrated_at"), f"{label}.migrated_at", errors)
        backup_dir: Path | None = None
        try:
            backup_dir, backup_rel = visual_path(
                root, str(item.get("backup_path", "")), must_exist=False,
                allowed_prefixes=("visual/manifests/migration_backups/",),
            )
            if backup_rel != item.get("backup_path"):
                errors.append(f"{label}.backup_path is non-canonical")
        except VisualStateError as exc:
            errors.append(f"{label}: {exc}")
        if not SHA256_RE.fullmatch(str(item.get("backup_manifest_sha256", ""))):
            errors.append(f"{label}.backup_manifest_sha256 is invalid")
        elif check_files and backup_dir is not None:
            try:
                validate_backup_manifest(
                    backup_dir, expected_manifest_sha256=item.get("backup_manifest_sha256"),
                )
            except VisualStateError as exc:
                errors.append(f"{label}: {exc}")
        if not isinstance(item.get("warnings"), list) or not all(isinstance(v, str) for v in item.get("warnings", [])):
            errors.append(f"{label}.warnings must be a string array")

    slots = program.get("golden_slots")
    if not isinstance(slots, dict) or set(slots) != {*GOLDEN_SLOTS, "baby_anchors"}:
        errors.append("golden_slots has invalid keys")
    else:
        for slot in GOLDEN_SLOTS:
            asset_id = slots.get(slot)
            if asset_id is None:
                continue
            asset = next((a for a in assets if a.get("id") == asset_id), None)
            if not asset:
                errors.append(f"Golden slot {slot} references missing asset {asset_id}")
                continue
            allowed_classes, allowed_types = SLOT_RULES[slot]
            if (
                asset["class"] not in allowed_classes or asset["type"] not in allowed_types
                or asset["lifecycle_stage"] != "aesthetic_golden" or not asset.get("golden")
            ):
                errors.append(f"Golden slot {slot} violates class/type/Golden gate: {asset_id}")
        anchors = slots.get("baby_anchors")
        if not isinstance(anchors, dict) or not all(isinstance(k, str) and k.strip() for k in anchors):
            errors.append("golden_slots.baby_anchors must be an object with non-empty string stages")
        elif isinstance(anchors, dict):
            for stage, asset_id in anchors.items():
                asset = next((a for a in assets if a.get("id") == asset_id), None)
                if (
                    not asset or asset.get("class") not in {"S", "A"} or asset.get("type") != "baby"
                    or asset.get("lifecycle_stage") != "aesthetic_golden" or not asset.get("golden")
                ):
                    errors.append(f"Baby anchor {stage} violates class/type/Golden gate: {asset_id}")
                elif medical_status(program, asset) != "verified":
                    errors.append(f"Baby anchor {stage} is not professionally verified: {asset_id}")

    for asset in assets:
        if asset.get("lifecycle_stage") == "aesthetic_golden":
            latest = matching_reviews(program, asset)
            for family in required_promotion_reviews(asset):
                record = latest.get(family)
                if (
                    not record or record["verdict"] != "PASS" or not record["independent"]
                    or pass_review_errors(record, asset)
                ):
                    errors.append(f"{asset['id']} lacks current independent hard-gate-complete PASS {family} review")
            decision = next(
                (
                    item for item in decisions
                    if item.get("id") == (asset.get("golden") or {}).get("decision_id")
                    and item.get("kind") == "approval" and item.get("status") == "approved"
                    and asset["id"] in item.get("asset_ids", [])
                ),
                None,
            )
            if not decision:
                errors.append(f"{asset['id']} lacks a bound user aesthetic approval")
            if asset.get("medical_applicable") and medical_status(program, asset) != "verified":
                errors.append(f"Golden medical-applicable asset is not professionally verified: {asset['id']}")
        if asset.get("evidence_stage") != "concept" and asset.get("lifecycle_stage") != "aesthetic_golden":
            errors.append(f"advanced evidence requires aesthetic_golden lifecycle: {asset['id']}")
        if asset.get("lifecycle_stage") == "aesthetic_golden" and asset.get("evidence_stage") == "concept":
            errors.append(f"aesthetic Golden must have aesthetic_golden evidence_stage: {asset['id']}")
        if asset.get("evidence_stage") in {"integrated", "matrix_accepted", "release_signed"} and isinstance(
            asset.get("evidence_binding"), dict
        ):
            binding = asset["evidence_binding"]
            errors.extend(
                f"{asset['id']}: {problem}"
                for problem in evidence_gate_errors(
                    program, asset, target=asset["evidence_stage"],
                    source_tag=binding.get("source_tag", ""), build_hash=binding.get("build_hash", ""),
                )
            )

    errors.extend(validate_design_tokens(root, program))
    return sorted(set(errors))


def validate_design_tokens(root: Path, program: dict[str, Any] | None = None) -> list[str]:
    """Validate frozen Token coverage and fail closed on a false readiness claim.

    This intentionally mirrors the release-critical subset of
    ``design_tokens.schema.json`` using only the Python standard library.  The
    Skill must stay usable when an optional JSON-Schema package is unavailable.
    """
    path = root / "visual" / "system" / "design_tokens.json"
    try:
        tokens = load_json(path)
    except VisualStateError as exc:
        return [str(exc)]
    errors: list[str] = []
    top_required = {
        "schema_version", "token_version", "content_sha256", "status", "implementation_ready",
        "contract_decisions", "source_golden_ids", "governance", "semantic_priority",
        "primitive", "semantic", "platform_mappings",
    }
    strict_keys(tokens, top_required, top_required | {"$schema"}, "design_tokens", errors)
    if tokens.get("schema_version") != 1:
        errors.append("design_tokens.schema_version must be 1")
    if not isinstance(tokens.get("token_version"), str) or not SEMVER_RE.fullmatch(tokens["token_version"]):
        errors.append("design_tokens.token_version must be Semantic Versioning")
    content_fields = (
        "token_version", "contract_decisions", "source_golden_ids",
        "semantic_priority", "primitive", "semantic",
    )
    content_sha256 = tokens.get("content_sha256")
    if not isinstance(content_sha256, str) or not SHA256_RE.fullmatch(content_sha256):
        errors.append("design_tokens.content_sha256 must be SHA-256")
    elif all(field in tokens for field in content_fields):
        calculated_content_hash = sha256_value({field: tokens[field] for field in content_fields})
        if calculated_content_hash != content_sha256:
            errors.append("design_tokens.content_sha256 does not match the canonical content payload")
    status = tokens.get("status")
    if status not in {"bootstrap_provisional", "proposed", "approved", "deprecated"}:
        errors.append("design_tokens.status is outside the frozen enum")
    ready = tokens.get("implementation_ready")
    if not isinstance(ready, bool):
        errors.append("design_tokens.implementation_ready must be boolean")
        ready = False
    if (status == "approved") != bool(ready):
        errors.append("approved status and implementation_ready=true must occur together")
    for field in ("contract_decisions", "source_golden_ids"):
        value = tokens.get(field)
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"design_tokens.{field} must be a string array")
        elif len(value) != len(set(value)):
            errors.append(f"design_tokens.{field} must not contain duplicates")
    source_golden_ids = tokens.get("source_golden_ids") if isinstance(tokens.get("source_golden_ids"), list) else []
    if ready:
        if not source_golden_ids:
            errors.append("implementation-ready Tokens require at least one source Golden asset")
        for source_id in source_golden_ids:
            if not isinstance(source_id, str) or not ASSET_ID_RE.fullmatch(source_id):
                errors.append(f"invalid source Golden asset id: {source_id}")
                continue
            canonical_asset = next(
                (
                    item for item in (program.get("assets", []) if isinstance(program, dict) else [])
                    if isinstance(item, dict) and item.get("id") == source_id
                ),
                None,
            )
            if not canonical_asset:
                errors.append(f"source Golden is absent from the canonical visual program: {source_id}")
            elif (
                canonical_asset.get("lifecycle_stage") != "aesthetic_golden"
                or canonical_asset.get("freshness") != "current"
                or not isinstance(canonical_asset.get("golden"), dict)
            ):
                errors.append(f"Token source is not a current canonical aesthetic Golden: {source_id}")
    if tokens.get("semantic_priority") != TOKEN_PRIORITY:
        errors.append("design_tokens.semantic_priority must match frozen TOK-002 order")
    primitive = tokens.get("primitive")
    if not isinstance(primitive, dict) or len(primitive) < 8:
        errors.append("design_tokens.primitive must contain the complete primitive families")
    semantic_required = {
        "surface", "content", "action", "focus", "disabled", "icon", "highContrast",
        "safety", "destructive", "ambient", "touchTarget", "motion", "layer",
    }
    semantic = tokens.get("semantic")
    if not isinstance(semantic, dict):
        errors.append("design_tokens.semantic must be an object")
    else:
        strict_keys(semantic, semantic_required, semantic_required, "design_tokens.semantic", errors)
        for family in sorted(semantic_required & set(semantic)):
            if not isinstance(semantic[family], dict) or not semantic[family]:
                errors.append(f"design_tokens.semantic.{family} must be a non-empty object")

    governance_required = {
        "sole_implementation_source", "medical_severity_source", "breaking_change_requires",
        "required_approvals", "additional_approvals_for_safety_or_accessibility",
        "generator_version", "approved_content_sha256", "approval_records",
        "regression_evidence_records", "note",
    }
    governance = tokens.get("governance")
    approval_roles: set[str] = set()
    regression_categories: set[str] = set()
    regression_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(governance, dict):
        errors.append("design_tokens.governance must be an object")
        governance = {}
    else:
        strict_keys(governance, governance_required, governance_required, "design_tokens.governance", errors)
        if governance.get("sole_implementation_source") is not True:
            errors.append("Tokens must remain the sole implementation constant source")
        if governance.get("medical_severity_source") != "signed_local_rule_pack_not_tokens":
            errors.append("Tokens must not determine medical severity")
        if governance.get("breaking_change_requires") != "CHG-001":
            errors.append("breaking Token changes must require CHG-001")
        required_approvals = governance.get("required_approvals")
        if not isinstance(required_approvals, list) or not {"DESIGN", "ANDROID", "IOS", "QA"}.issubset(
            {item for item in required_approvals if isinstance(item, str)}
        ):
            errors.append("Token governance must require DESIGN, ANDROID, IOS, and QA")
        additional = governance.get("additional_approvals_for_safety_or_accessibility")
        if not isinstance(additional, list) or "MD" not in additional:
            errors.append("Safety/accessibility Token governance must require MD")
        generator_version = governance.get("generator_version")
        if generator_version is not None and (
            not isinstance(generator_version, str) or not SEMVER_RE.fullmatch(generator_version)
        ):
            errors.append("Token generator_version must be null or Semantic Versioning")
        if ready and generator_version is None:
            errors.append("implementation-ready Tokens require a versioned generator")
        approved_content_hash = governance.get("approved_content_sha256")
        if approved_content_hash is not None and (
            not isinstance(approved_content_hash, str) or not SHA256_RE.fullmatch(approved_content_hash)
        ):
            errors.append("Token approved_content_sha256 must be null or SHA-256")
        if ready and approved_content_hash != content_sha256:
            errors.append("implementation-ready Tokens must approve the current immutable content payload")

        approvals = governance.get("approval_records")
        if not isinstance(approvals, list):
            errors.append("Token approval_records must be an array")
        else:
            seen_approval_ids: set[str] = set()
            allowed_roles = {"DESIGN", "ANDROID", "IOS", "QA", "MD", "LEGAL", "SEC", "ETHICS", "PO", "TECH"}
            for index, record in enumerate(approvals):
                label = f"Token approval_records[{index}]"
                required = {
                    "role", "approval_id", "scope", "signed_at", "content_sha256",
                    "evidence_path", "evidence_sha256",
                }
                if not isinstance(record, dict):
                    errors.append(f"{label} must be an object")
                    continue
                strict_keys(record, required, required, label, errors)
                role = record.get("role")
                if role not in allowed_roles:
                    errors.append(f"{label}.role is invalid")
                else:
                    approval_roles.add(role)
                approval_id = record.get("approval_id")
                if not isinstance(approval_id, str) or not approval_id.strip():
                    errors.append(f"{label}.approval_id must be non-empty")
                elif approval_id in seen_approval_ids:
                    errors.append(f"duplicate Token approval_id: {approval_id}")
                else:
                    seen_approval_ids.add(approval_id)
                if not isinstance(record.get("scope"), str) or not record["scope"].strip():
                    errors.append(f"{label}.scope must be non-empty")
                parse_iso(record.get("signed_at"), f"{label}.signed_at", errors)
                if record.get("content_sha256") != content_sha256:
                    errors.append(f"{label} is not bound to the current Token content")
                evidence_path = record.get("evidence_path")
                evidence_hash = record.get("evidence_sha256")
                if not isinstance(evidence_hash, str) or not SHA256_RE.fullmatch(evidence_hash):
                    errors.append(f"{label}.evidence_sha256 must be SHA-256")
                if not isinstance(evidence_path, str):
                    errors.append(f"{label}.evidence_path must be a string")
                else:
                    try:
                        approval_file, _ = visual_path(
                            root,
                            evidence_path,
                            must_exist=True,
                            allowed_prefixes=("visual/reviews/", "visual/system/attestations/"),
                        )
                        if isinstance(evidence_hash, str) and SHA256_RE.fullmatch(evidence_hash):
                            if sha256_file(approval_file) != evidence_hash:
                                errors.append(f"{label}.evidence_sha256 does not match its artifact")
                    except VisualStateError as exc:
                        errors.append(str(exc))

        regressions = governance.get("regression_evidence_records")
        if not isinstance(regressions, list):
            errors.append("Token regression_evidence_records must be an array")
        else:
            seen_evidence_ids: set[str] = set()
            allowed_categories = {"golden", "contrast", "screen_reader", "reduce_motion", "platform_generation"}
            allowed_platforms = {"cross_platform", "flutter", "rive", "ios_widget", "android_widget"}
            for index, record in enumerate(regressions):
                label = f"Token regression_evidence_records[{index}]"
                required = {
                    "category", "evidence_id", "artifact_path", "sha256",
                    "content_sha256", "platform", "build_hash",
                }
                if not isinstance(record, dict):
                    errors.append(f"{label} must be an object")
                    continue
                strict_keys(record, required, required, label, errors)
                category = record.get("category")
                if category not in allowed_categories:
                    errors.append(f"{label}.category is invalid")
                else:
                    regression_categories.add(category)
                evidence_id = record.get("evidence_id")
                if not isinstance(evidence_id, str) or not evidence_id.strip():
                    errors.append(f"{label}.evidence_id must be non-empty")
                elif evidence_id in seen_evidence_ids:
                    errors.append(f"duplicate Token evidence_id: {evidence_id}")
                else:
                    seen_evidence_ids.add(evidence_id)
                    regression_by_id[evidence_id] = record
                if record.get("platform") not in allowed_platforms:
                    errors.append(f"{label}.platform is invalid")
                if record.get("content_sha256") != content_sha256:
                    errors.append(f"{label} is not bound to the current Token content")
                if not isinstance(record.get("build_hash"), str) or len(record["build_hash"].strip()) < 7:
                    errors.append(f"{label}.build_hash must bind a named build")
                artifact_value = record.get("artifact_path")
                if not isinstance(artifact_value, str):
                    errors.append(f"{label}.artifact_path must be a string")
                else:
                    try:
                        artifact, _ = visual_path(
                            root, artifact_value, must_exist=True, allowed_prefixes=("visual/reviews/",),
                        )
                        expected_hash = record.get("sha256")
                        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
                            errors.append(f"{label}.sha256 must be SHA-256")
                        elif sha256_file(artifact) != expected_hash:
                            errors.append(f"{label}.sha256 does not match its artifact")
                    except VisualStateError as exc:
                        errors.append(str(exc))

    if ready:
        missing_roles = sorted({"DESIGN", "ANDROID", "IOS", "QA", "MD"} - approval_roles)
        if missing_roles:
            errors.append("implementation-ready Tokens lack approvals: " + ", ".join(missing_roles))
        missing_categories = sorted(
            {"golden", "contrast", "screen_reader", "reduce_motion", "platform_generation"}
            - regression_categories
        )
        if missing_categories:
            errors.append("implementation-ready Tokens lack regressions: " + ", ".join(missing_categories))

    mappings = tokens.get("platform_mappings")
    if not isinstance(mappings, dict):
        errors.append("design_tokens.platform_mappings must be an object")
    else:
        strict_keys(mappings, TOKEN_PLATFORMS, TOKEN_PLATFORMS, "design_tokens.platform_mappings", errors)
        mapping_required = {
            "status", "target", "generator", "source_content_sha256",
            "output_sha256", "verification_evidence_ids",
        }
        for platform in sorted(TOKEN_PLATFORMS & set(mappings)):
            mapping = mappings[platform]
            label = f"design_tokens.platform_mappings.{platform}"
            if not isinstance(mapping, dict):
                errors.append(f"{label} must be an object")
                continue
            strict_keys(mapping, mapping_required, mapping_required, label, errors)
            if mapping.get("status") not in {"required_present_disabled", "proposed", "generated", "verified"}:
                errors.append(f"{label}.status is invalid")
            target = mapping.get("target")
            if not isinstance(target, str) or not target.strip():
                errors.append(f"{label}.target must be non-empty")
            generator = mapping.get("generator")
            if generator is not None and (not isinstance(generator, str) or not generator.strip()):
                errors.append(f"{label}.generator must be null or non-empty")
            source_content_hash = mapping.get("source_content_sha256")
            if source_content_hash is not None and (
                not isinstance(source_content_hash, str) or not SHA256_RE.fullmatch(source_content_hash)
            ):
                errors.append(f"{label}.source_content_sha256 must be null or SHA-256")
            output_hash = mapping.get("output_sha256")
            if output_hash is not None and (not isinstance(output_hash, str) or not SHA256_RE.fullmatch(output_hash)):
                errors.append(f"{label}.output_sha256 must be null or SHA-256")
            evidence_ids = mapping.get("verification_evidence_ids")
            if not isinstance(evidence_ids, list) or not all(
                isinstance(item, str) and item.strip() for item in evidence_ids
            ) or len(evidence_ids) != len(set(evidence_ids)):
                errors.append(f"{label}.verification_evidence_ids must be a unique string array")
                evidence_ids = []
            for evidence_id in evidence_ids:
                if evidence_id not in regression_by_id:
                    errors.append(f"{label} references missing Token evidence: {evidence_id}")
            if ready:
                if (
                    mapping.get("status") != "verified"
                    or generator is None
                    or source_content_hash != content_sha256
                    or output_hash is None
                    or not evidence_ids
                ):
                    errors.append(f"implementation-ready {label} must be verified with generator, hash, and evidence")
                if isinstance(target, str):
                    try:
                        output = (root / target).resolve()
                        output.relative_to(root)
                        if not output.is_file():
                            errors.append(f"implementation-ready Token output is missing: {target}")
                        elif isinstance(output_hash, str) and SHA256_RE.fullmatch(output_hash) and sha256_file(output) != output_hash:
                            errors.append(f"implementation-ready Token output hash mismatch: {target}")
                    except (OSError, ValueError):
                        errors.append(f"Token output target escapes or is invalid: {target}")
    return errors


def validate_or_raise(root: Path, program: dict[str, Any], *, check_files: bool = True) -> None:
    errors = validate_program(root, program, check_files=check_files)
    if errors:
        raise VisualStateError("visual program validation failed:\n- " + "\n- ".join(errors))


def projected_asset(program: dict[str, Any], asset: dict[str, Any]) -> dict[str, Any]:
    golden = asset.get("golden") or {}
    return {
        "id": asset["id"],
        "name": asset["name"],
        "class": asset["class"],
        "type": asset["type"],
        "status": asset["lifecycle_stage"],
        "lifecycle_stage": asset["lifecycle_stage"],
        "freshness": asset["freshness"],
        "evidence_stage": asset["evidence_stage"],
        "evidence_binding": asset["evidence_binding"],
        "stale_reasons": asset["stale_reasons"],
        "version": asset["version"],
        "path": asset["path"],
        "sha256": asset["sha256"],
        "golden_path": golden.get("path"),
        "golden_sha256": golden.get("sha256"),
        "parents": asset["parents"],
        "references": asset["references"],
        "depends_on": asset["depends_on"],
        "tool": asset["tool"],
        "model": asset["model"],
        "prompt_path": asset["prompt_path"],
        "medical_status": medical_status(program, asset),
        "privacy": asset["privacy"],
        "rights": asset["rights"],
        "medical_evidence": [
            item["id"] for item in program["medical_sources"] if item["asset_id"] == asset["id"]
        ],
        "user_decision_id": golden.get("decision_id"),
        "review_ids": [
            item["id"] for item in program["reviews"] if item["asset_id"] == asset["id"]
        ],
        "created_at": asset["created_at"],
        "updated_at": asset["updated_at"],
        "approved_at": golden.get("approved_at"),
        "notes": asset["notes"],
    }


def projection_payloads(program: dict[str, Any]) -> dict[str, Any]:
    canonical_hash = sha256_value(program)
    projection_meta = {
        "source": "visual/manifests/visual_program.json",
        "canonical_revision": program["revision"],
        "canonical_sha256": canonical_hash,
        "generated_at": program["updated_at"],
        "do_not_edit": True,
    }
    latest_decision = program["decisions"][-1]["id"] if program["decisions"] else None
    state = {
        "schema_version": 3,
        "visual_version": program["visual_version"],
        "contract_version": program["contract_version"],
        "current_gate": program["current_gate"],
        "user_role": "creative_approver",
        "implementation_focus": "android_first_dual_platform_contract",
        "golden": program["golden_slots"],
        "system_extracted": bool(program["golden_slots"].get("style_lock_sheet")),
        "last_user_decision_id": latest_decision,
        "medical_visual_sources_ready": any(
            medical_status(program, asset) == "verified" for asset in program["assets"]
        ),
        "release_evidence_status": program["release_status"],
        "notes": ["Derived projection; repair with visual_ops.py repair-projections."],
        "_projection": projection_meta,
    }
    assets = {
        "schema_version": 2,
        "revision": program["revision"],
        "assets": [projected_asset(program, item) for item in program["assets"]],
        "_projection": projection_meta,
    }
    decisions = {
        "schema_version": 1,
        "revision": program["revision"],
        "decisions": program["decisions"],
        "_projection": projection_meta,
    }
    reviews = {
        "schema_version": 1,
        "revision": program["revision"],
        "reviews": program["reviews"],
        "_projection": projection_meta,
    }
    return {"state": state, "assets": assets, "decisions": decisions, "reviews": reviews}


def render_decision_log(program: dict[str, Any]) -> str:
    lines = [
        "# Visual Decision Log",
        "",
        "> Derived projection of `visual/manifests/visual_program.json`. Do not edit.",
        "",
        f"Canonical revision: {program['revision']}",
        f"Canonical SHA-256: {sha256_value(program)}",
    ]
    for item in program["decisions"]:
        lines.extend([
            "",
            f"## {item['id']} — {item['occurred_at'][:10]}",
            f"Kind: {item['kind']}",
            f"Status: {item['status']}",
            f"Decided by: {item['decided_by']}",
            f"Assets: {', '.join(item['asset_ids']) or '-'}",
            f"Decision: {item['text']}",
        ])
        if item["preserve"]:
            lines.append("Preserve: " + "; ".join(item["preserve"]))
        if item["change"]:
            lines.append("Change: " + "; ".join(item["change"]))
    return "\n".join(lines) + "\n"


def repair_projections(root: Path, program: dict[str, Any]) -> list[str]:
    paths = projection_paths(root)
    payloads = projection_payloads(program)
    for key in ("state", "assets", "decisions", "reviews"):
        atomic_write_json(paths[key], payloads[key])
    atomic_write_text(paths["decision_log"], render_decision_log(program))
    return [path.relative_to(root).as_posix() for path in paths.values()]


def projection_drift(root: Path, program: dict[str, Any]) -> list[str]:
    paths = projection_paths(root)
    expected = projection_payloads(program)
    drift: list[str] = []
    for key in ("state", "assets", "decisions", "reviews"):
        try:
            actual = load_json(paths[key])
        except VisualStateError:
            drift.append(paths[key].relative_to(root).as_posix())
            continue
        if actual != expected[key]:
            drift.append(paths[key].relative_to(root).as_posix())
    try:
        actual_log = paths["decision_log"].read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError):
        actual_log = ""
    if actual_log != render_decision_log(program):
        drift.append(paths["decision_log"].relative_to(root).as_posix())
    return drift


def normalize_operation_id(value: str | None) -> str:
    operation_id = value or f"OP-{uuid.uuid4()}"
    if not OPERATION_ID_RE.fullmatch(operation_id):
        raise VisualStateError(
            "operation_id must match OP- followed by 8-128 letters, digits, dot, underscore, colon, or hyphen"
        )
    return operation_id


def operation_fingerprint(command: str, args: argparse.Namespace) -> str:
    ignored = {"project_root", "operation_id", "command", "no_fail", "func"}
    payload = {
        "command": command,
        "arguments": {key: value for key, value in vars(args).items() if key not in ignored},
    }
    return sha256_value(payload)


Mutation = Callable[[dict[str, Any]], dict[str, Any]]


def commit_operation(
    root: Path,
    program: dict[str, Any],
    *,
    operation_id: str | None,
    command: str,
    args: argparse.Namespace,
    mutate: Mutation,
) -> dict[str, Any]:
    op_id = normalize_operation_id(operation_id)
    fingerprint = operation_fingerprint(command, args)
    existing = next((item for item in program["operations"] if item["id"] == op_id), None)
    if existing:
        if existing["command"] != command or existing["fingerprint"] != fingerprint:
            raise VisualStateError(f"operation_id reuse with different request: {op_id}")
        # A prior canonical commit may have been followed by a projection write failure.
        repair_projections(root, program)
        result = dict(existing["result"])
        result["operation_id"] = op_id
        result["idempotent_replay"] = True
        return result

    result = mutate(program)
    program["revision"] += 1
    program["updated_at"] = utc_now()
    committed_result = dict(result)
    committed_result["operation_id"] = op_id
    committed_result["idempotent_replay"] = False
    program["operations"].append({
        "id": op_id,
        "command": command,
        "fingerprint": fingerprint,
        "committed_revision": program["revision"],
        "created_at": program["updated_at"],
        "result": committed_result,
    })
    validate_or_raise(root, program)
    atomic_write_json(program_path(root), program)
    repair_projections(root, program)
    return committed_result


def content_addressed_copy(root: Path, source: Path, digest: str) -> tuple[Path, str]:
    suffix = source.suffix.lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
        suffix = ".bin"
    destination = root / "visual" / "golden" / "sha256" / digest[:2] / f"{digest}{suffix}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if not destination.is_file() or sha256_file(destination) != digest:
            raise VisualStateError(f"content-addressed Golden collision or corruption: {destination}")
        return destination, destination.relative_to(root).as_posix()
    fd, temp_name = tempfile.mkstemp(prefix=f".{digest}.", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        shutil.copyfile(source, temp_path)
        if sha256_file(temp_path) != digest:
            raise VisualStateError("Golden copy hash mismatch")
        try:
            os.link(temp_path, destination)
        except FileExistsError:
            if sha256_file(destination) != digest:
                raise VisualStateError(f"Golden destination appeared with wrong content: {destination}")
        except OSError as exc:
            # Fail closed: an atomic no-clobber operation is required.
            raise VisualStateError(f"filesystem cannot atomically create no-overwrite Golden: {exc}") from exc
    finally:
        temp_path.unlink(missing_ok=True)
    return destination, destination.relative_to(root).as_posix()


def validate_reference(root: Path, value: str) -> str:
    raw = Path(value).expanduser()
    parsed = urlparse(value)
    if not raw.is_absolute() and parsed.scheme:
        raise VisualStateError(
            "remote reference URLs are not durable provenance; archive the source under visual/references/ first"
        )
    source, rel = visual_path(root, value, must_exist=True, allowed_prefixes=("visual/references/",))
    validate_local_provenance(root, source, rel, purpose="reference")
    return rel


def cmd_init(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    ensure_directories(root)
    canonical = program_path(root)
    if canonical.exists():
        program = load_program(root)
        validate_or_raise(root, program)
        if args.operation_id:
            op_id = normalize_operation_id(args.operation_id)
            fingerprint = operation_fingerprint("init", args)
            existing = next((item for item in program["operations"] if item["id"] == op_id), None)
            if not existing or existing["command"] != "init" or existing["fingerprint"] != fingerprint:
                raise VisualStateError(f"operation_id reuse with different request: {op_id}")
            repair_projections(root, program)
            result = dict(existing["result"])
            result["idempotent_replay"] = True
            return result
        repair_projections(root, program)
        return {"status": "already_initialized", "project_root": str(root)}
    legacy_present = any(path.exists() for path in projection_paths(root).values())
    if legacy_present:
        raise VisualStateError(
            "legacy visual registries exist; run the explicit `migrate` command so they are backed up and preserved"
        )
    program = initial_program()
    op_id = normalize_operation_id(args.operation_id)
    fingerprint = operation_fingerprint("init", args)
    program["revision"] = 1
    program["updated_at"] = utc_now()
    result = {
        "status": "initialized", "project_root": str(root), "operation_id": op_id,
        "idempotent_replay": False,
    }
    program["operations"].append({
        "id": op_id, "command": "init", "fingerprint": fingerprint, "committed_revision": 1,
        "created_at": program["updated_at"], "result": result,
    })
    validate_or_raise(root, program)
    atomic_write_json(canonical, program)
    repair_projections(root, program)
    return result


def legacy_files(root: Path) -> list[Path]:
    paths = projection_paths(root)
    return [paths[key] for key in ("state", "assets", "decisions", "reviews", "decision_log") if paths[key].exists()]


def canonical_backup_entry_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise VisualStateError(f"backup manifest path is not canonical: {value!r}")
    reject_ntfs_ads_syntax(value, label="backup manifest path")
    pure = PurePosixPath(value)
    if pure.is_absolute() or pure.as_posix() != value or any(part in {"", ".", ".."} for part in pure.parts):
        raise VisualStateError(f"backup manifest path is absolute, traversing, or non-canonical: {value}")
    if not pure.parts or pure.parts[0] != "visual":
        raise VisualStateError(f"backup manifest path must preserve a visual/ source path: {value}")
    return value


def backup_tree_files(backup: Path) -> dict[str, Path]:
    discovered: dict[str, Path] = {}
    for directory, dirnames, filenames in os.walk(backup, topdown=True, followlinks=False):
        directory_path = Path(directory)
        if is_reparse_or_symlink(directory_path):
            raise VisualStateError(f"backup tree contains a symlink/reparse directory: {directory_path}")
        for name in [*dirnames, *filenames]:
            reject_ntfs_ads_syntax(name, label="backup tree entry")
        for dirname in dirnames:
            child = directory_path / dirname
            if is_reparse_or_symlink(child):
                raise VisualStateError(f"backup tree contains a symlink/reparse directory: {child}")
        for filename in filenames:
            path = directory_path / filename
            if path.name == "BACKUP_MANIFEST.json" and path.parent == backup:
                continue
            verify_regular_single_link(path, label="backup file")
            rel = path.relative_to(backup).as_posix()
            canonical_backup_entry_path(rel)
            discovered[rel] = path
    return discovered


def validate_backup_manifest(backup: Path, *, expected_manifest_sha256: str | None = None) -> dict[str, Any]:
    """Validate manifest authenticity plus every backed-up file and the closed file set."""
    if is_reparse_or_symlink(backup) or not backup.is_dir():
        raise VisualStateError(f"backup path must be a regular non-reparse directory: {backup}")
    manifest_path = backup / "BACKUP_MANIFEST.json"
    verify_regular_single_link(manifest_path, label="backup manifest")
    actual_manifest_hash = sha256_file(manifest_path)
    if expected_manifest_sha256 is not None and actual_manifest_hash != expected_manifest_sha256:
        raise VisualStateError("backup_manifest_sha256 does not match BACKUP_MANIFEST.json")
    manifest = load_json(manifest_path)
    entries: dict[str, dict[str, Any]] = {}
    legacy = False
    if manifest.get("schema_version") == 2:
        if set(manifest) != {"schema_version", "created_at", "entries"}:
            raise VisualStateError("BACKUP_MANIFEST v2 has missing or unknown keys")
        raw_entries = manifest.get("entries")
        if not isinstance(raw_entries, list):
            raise VisualStateError("BACKUP_MANIFEST v2 entries must be an array")
        for index, entry in enumerate(raw_entries):
            if not isinstance(entry, dict) or set(entry) != {"path", "bytes", "sha256"}:
                raise VisualStateError(f"BACKUP_MANIFEST entry {index} must contain path/bytes/sha256")
            rel = canonical_backup_entry_path(entry.get("path"))
            if rel in entries:
                raise VisualStateError(f"duplicate backup manifest entry: {rel}")
            if not isinstance(entry.get("bytes"), int) or isinstance(entry.get("bytes"), bool) or entry["bytes"] < 0:
                raise VisualStateError(f"invalid byte count for backup manifest entry: {rel}")
            if not isinstance(entry.get("sha256"), str) or not SHA256_RE.fullmatch(entry["sha256"]):
                raise VisualStateError(f"invalid SHA-256 for backup manifest entry: {rel}")
            entries[rel] = entry
    elif set(manifest) == {"created_at", "files"} and isinstance(manifest.get("files"), dict):
        legacy = True
        for raw_rel, digest in manifest["files"].items():
            rel = canonical_backup_entry_path(raw_rel)
            if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                raise VisualStateError(f"invalid legacy backup SHA-256: {rel}")
            entries[rel] = {"path": rel, "bytes": None, "sha256": digest}
    else:
        raise VisualStateError("unsupported BACKUP_MANIFEST format")
    created_errors: list[str] = []
    parse_iso(manifest.get("created_at"), "BACKUP_MANIFEST.created_at", created_errors)
    if created_errors:
        raise VisualStateError(created_errors[0])
    discovered = backup_tree_files(backup)
    missing = sorted(set(entries) - set(discovered))
    unlisted = sorted(set(discovered) - set(entries))
    if missing:
        raise VisualStateError("backup manifest lists missing files: " + ", ".join(missing))
    if unlisted:
        raise VisualStateError("backup tree contains unlisted files: " + ", ".join(unlisted))
    for rel, entry in entries.items():
        path = discovered[rel]
        if entry["bytes"] is not None and path.stat().st_size != entry["bytes"]:
            raise VisualStateError(f"backup byte count mismatch: {rel}")
        if sha256_file(path) != entry["sha256"]:
            raise VisualStateError(f"backup SHA-256 mismatch: {rel}")
    return {
        "manifest_sha256": actual_manifest_hash,
        "legacy": legacy,
        "legacy_inventory_sha256": sha256_value(manifest.get("files")) if legacy else None,
        "entry_count": len(entries),
    }


def backup_legacy(root: Path, files: list[Path]) -> tuple[Path, dict[str, str]]:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = root / "visual" / "manifests" / "migration_backups"
    backup = base / f"{stamp}-legacy-v2"
    counter = 1
    while backup.exists():
        backup = base / f"{stamp}-legacy-v2-{counter:02d}"
        counter += 1
    backup.mkdir(parents=True, exist_ok=False)
    hashes: dict[str, str] = {}
    entries: list[dict[str, Any]] = []
    for source in files:
        rel = source.relative_to(root).as_posix()
        destination = backup / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if sha256_file(destination) != sha256_file(source):
            raise VisualStateError(f"legacy backup verification failed: {rel}")
        hashes[rel] = sha256_file(source)
        entries.append({"path": rel, "bytes": destination.stat().st_size, "sha256": hashes[rel]})
    manifest = {"schema_version": 2, "created_at": utc_now(), "entries": sorted(entries, key=lambda item: item["path"])}
    atomic_write_json(backup / "BACKUP_MANIFEST.json", manifest)
    validate_backup_manifest(backup, expected_manifest_sha256=sha256_file(backup / "BACKUP_MANIFEST.json"))
    return backup, hashes


def migrate_legacy(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    ensure_directories(root)
    if program_path(root).exists():
        program = load_program(root)
        validate_or_raise(root, program)
        if args.operation_id:
            op_id = normalize_operation_id(args.operation_id)
            fingerprint = operation_fingerprint("migrate", args)
            existing = next((item for item in program["operations"] if item["id"] == op_id), None)
            if existing and existing["command"] == "migrate" and existing["fingerprint"] == fingerprint:
                repair_projections(root, program)
                result = dict(existing["result"])
                result["idempotent_replay"] = True
                return result
        raise VisualStateError("canonical visual_program.json already exists; migration will not overwrite it")
    files = legacy_files(root)
    required = projection_paths(root)
    for key in ("state", "assets", "decisions", "reviews"):
        if not required[key].is_file():
            raise VisualStateError(f"legacy migration requires {required[key]}")
    state = load_json(required["state"])
    assets_doc = load_json(required["assets"])
    decisions_doc = load_json(required["decisions"])
    reviews_doc = load_json(required["reviews"])
    if state.get("schema_version") != 3 or assets_doc.get("schema_version") != 2:
        raise VisualStateError("unsupported legacy schema; expected DESIGN_STATE v3 and asset_registry v2")
    if decisions_doc.get("schema_version") != 1 or reviews_doc.get("schema_version") != 1:
        raise VisualStateError("unsupported legacy decision/review schema")
    if not all(isinstance(doc.get(key), list) for doc, key in (
        (assets_doc, "assets"), (decisions_doc, "decisions"), (reviews_doc, "reviews")
    )):
        raise VisualStateError("legacy registries must contain arrays")
    backup, hashes = backup_legacy(root, files)
    now = utc_now()
    program = initial_program()
    program.update({
        "visual_version": str(state.get("visual_version", "3.0.0")),
        "contract_version": str(state.get("contract_version", "YunMom_Engineering_Contracts_V1.0.0")),
        "current_gate": str(state.get("current_gate", "G1_YUNMOM_MASTER")),
        "release_status": str(state.get("release_evidence_status", "not_approved")),
        "assets": [], "decisions": [], "reviews": [],
    })
    warnings: list[str] = []
    legacy_to_asset: dict[str, dict[str, Any]] = {}
    for old in assets_doc["assets"]:
        if not isinstance(old, dict):
            raise VisualStateError("legacy asset entries must be objects")
        asset_id = str(old.get("id", ""))
        if not ASSET_ID_RE.fullmatch(asset_id):
            raise VisualStateError(f"legacy asset has unsupported id: {asset_id}")
        source, rel = visual_path(
            root, str(old.get("path", "")), must_exist=True,
            allowed_prefixes=ASSET_AREA_PREFIXES,
        )
        digest = sha256_file(source)
        if old.get("sha256") and old.get("sha256") != digest:
            raise VisualStateError(f"legacy asset hash mismatch: {asset_id}")
        old_status = str(old.get("lifecycle_stage", old.get("status", "candidate")))
        freshness = str(old.get("freshness", "stale" if old_status == "stale" else "current"))
        if freshness == "fresh":
            freshness = "current"
        if freshness not in FRESHNESS_STATES:
            freshness = "stale"
        lifecycle = old_status if old_status in LIFECYCLE_STAGES else "candidate"
        if old_status == "approved":
            lifecycle = "aesthetic_golden"
        elif old_status in {"release_ready", "production"}:
            lifecycle = "aesthetic_golden"
            warnings.append(
                f"{asset_id}: legacy {old_status} downgraded to aesthetic_golden; staged integration/matrix/release evidence must be recertified"
            )
        elif old_status == "stale":
            lifecycle = "candidate"
        medical_applicable = (
            old.get("type") in AUTO_MEDICAL_ASSET_TYPES
            or old.get("medical_status") not in {None, "not_applicable"}
        )
        if old.get("type") == "baby" and old.get("medical_status") == "verified":
            warnings.append(f"{asset_id}: legacy free-form medical flag downgraded to unverified pending structured verification")
        stale_reasons = list(old.get("stale_reasons", [])) if isinstance(old.get("stale_reasons"), list) else []
        if freshness in {"stale", "stale_contract_conflict"} and not stale_reasons:
            stale_reasons = [{
                "code": "contract_conflict" if freshness == "stale_contract_conflict" else "manual",
                "source_asset_id": None,
                "detail": "legacy stale state migrated without structured origin",
                "recorded_at": now,
            }]
        old_privacy = old.get("privacy") if isinstance(old.get("privacy"), dict) else {}
        classification = (
            old_privacy.get("classification")
            if old_privacy.get("classification") in PRIVACY_CLASSIFICATIONS else "unclassified"
        )
        content_origin = (
            old_privacy.get("content_origin")
            if old_privacy.get("content_origin") in CONTENT_ORIGINS else "unknown"
        )
        persistent_allowed = bool(old_privacy.get("persistent_evidence_allowed", False))
        if content_origin in {"real_sensitive", "unknown"} or classification == "unclassified":
            persistent_allowed = False
        old_egress = old_privacy.get("external_egress") if isinstance(old_privacy.get("external_egress"), dict) else {}
        egress_status = old_egress.get("status") if old_egress.get("status") in EGRESS_STATUSES else "prohibited"
        if content_origin == "unknown" or classification == "unclassified":
            egress_status = "prohibited"
        cleanup_scope = old_privacy.get("cleanup_scope")
        if not isinstance(cleanup_scope, list) or not cleanup_scope or any(item not in CLEANUP_SCOPES for item in cleanup_scope):
            cleanup_scope = DEFAULT_CLEANUP_SCOPE
        privacy = {
            "classification": classification,
            "content_origin": content_origin,
            "persistent_evidence_allowed": persistent_allowed,
            "external_egress": {
                "status": egress_status,
                "receipt_ref": old_egress.get("receipt_ref") if isinstance(old_egress.get("receipt_ref"), str) else None,
            },
            "cleanup_scope": list(dict.fromkeys(cleanup_scope)),
        }
        if classification == "unclassified" or content_origin in {"real_sensitive", "unknown"}:
            raise VisualStateError(
                f"legacy asset {asset_id} lacks repository-safe privacy provenance; annotate it as synthetic/"
                "irreversibly_deidentified/not_applicable or remove it from the repository before migration"
            )
        asset = {
            "id": asset_id,
            "name": str(old.get("name", asset_id)),
            "class": str(old.get("class", "C")),
            "type": str(old.get("type", "illustration")),
            "lifecycle_stage": lifecycle,
            "freshness": freshness,
            "evidence_stage": (
                str(old.get("evidence_stage"))
                if old.get("evidence_stage") in EVIDENCE_STAGES else "concept"
            ),
            "evidence_binding": None,
            "version": int(old.get("version", 1)),
            "path": rel,
            "sha256": digest,
            "golden": None,
            "parents": list(old.get("parents", [])),
            "references": list(old.get("references", [])),
            "depends_on": list(old.get("depends_on", [])),
            "created_by": str(old.get("created_by") or old.get("tool") or "legacy-migration"),
            "tool": old.get("tool"),
            "model": old.get("model"),
            "prompt_path": old.get("prompt_path"),
            "medical_applicable": bool(medical_applicable),
            "privacy": privacy,
            "rights": {
                "status": "unverified",
                "commercial_use_allowed": False,
                "derivative_use_allowed": False,
                "attribution_required": False,
                "attribution_text": None,
                "evidence_refs": [],
            },
            "stale_reasons": stale_reasons,
            "created_at": str(old.get("created_at", now)),
            "updated_at": str(old.get("updated_at", now)),
            "notes": [*list(old.get("notes", [])), "migrated from legacy visual registries"],
        }
        if asset["evidence_stage"] not in {"concept", "aesthetic_golden"}:
            asset["evidence_stage"] = "concept"
            warnings.append(f"{asset_id}: advanced evidence downgraded; no same-build evidence_binding exists")
        if lifecycle == "aesthetic_golden":
            decision_id = old.get("user_decision_id")
            if not decision_id:
                asset["lifecycle_stage"] = "finalist"
                asset["evidence_stage"] = "concept"
                warnings.append(f"{asset_id}: Golden state downgraded; no bound user approval")
            elif asset["type"] == "baby":
                asset["lifecycle_stage"] = "finalist"
                asset["evidence_stage"] = "concept"
                warnings.append(f"{asset_id}: Baby Golden downgraded until structured professional verification")
            elif not persistent_allowed or content_origin in {"real_sensitive", "unknown"}:
                asset["lifecycle_stage"] = "finalist"
                asset["evidence_stage"] = "concept"
                warnings.append(f"{asset_id}: Golden state downgraded by fail-closed privacy migration")
            else:
                asset["lifecycle_stage"] = "finalist"
                asset["evidence_stage"] = "concept"
                warnings.append(f"{asset_id}: Golden state downgraded; legacy rights are unverified")
        program["assets"].append(asset)
        legacy_to_asset[asset_id] = asset

    for old in decisions_doc["decisions"]:
        if not isinstance(old, dict):
            raise VisualStateError("legacy decisions must be objects")
        decision_id = str(old.get("id", ""))
        if not DECISION_ID_RE.fullmatch(decision_id):
            raise VisualStateError(f"legacy decision has unsupported id: {decision_id}")
        legacy_kind = str(old.get("kind", "feedback"))
        legacy_status = str(old.get("status", "recorded"))
        program["decisions"].append({
            "id": decision_id,
            "occurred_at": str(old.get("occurred_at", now)),
            "kind": legacy_kind if legacy_kind in DECISION_KINDS else "feedback",
            "status": legacy_status if legacy_status in DECISION_STATUSES else "recorded",
            "decided_by": str(old.get("decided_by", "legacy-user")),
            "asset_ids": list(old.get("asset_ids", [])),
            "text": str(old.get("text", "Legacy decision")),
            "preserve": list(old.get("preserve", [])),
            "change": list(old.get("change", [])),
        })
    if not program["decisions"]:
        program["decisions"] = initial_program()["decisions"]

    review_sequences: dict[tuple[str, str], int] = {}
    review_id_number = 0
    for old in sorted(reviews_doc["reviews"], key=lambda item: str(item.get("created_at", ""))):
        if not isinstance(old, dict):
            raise VisualStateError("legacy reviews must be objects")
        old_asset_ids = old.get("asset_ids") or [old.get("asset_id")]
        for asset_id in old_asset_ids:
            asset = legacy_to_asset.get(asset_id)
            if not asset:
                raise VisualStateError(f"legacy review references missing asset: {asset_id}")
            family = str(old.get("family", "visual"))
            if family not in REVIEW_FAMILIES:
                family = "visual"
            review_sequences[(asset_id, family)] = review_sequences.get((asset_id, family), 0) + 1
            sequence = review_sequences[(asset_id, family)]
            previous = next(
                (
                    item["id"] for item in reversed(program["reviews"])
                    if item["asset_id"] == asset_id and item["family"] == family
                ),
                None,
            )
            review_id_number += 1
            program["reviews"].append({
                "id": f"VR-{review_id_number:04d}",
                "created_at": str(old.get("created_at", now)),
                "reviewer": str(old.get("reviewer", "legacy-reviewer")),
                "reviewer_kind": (
                    str(old.get("reviewer_kind"))
                    if old.get("reviewer_kind") in REVIEWER_KINDS else "human"
                ),
                "family": family,
                "independent": bool(old.get("independent", False)),
                "asset_id": asset_id,
                "asset_version": asset["version"],
                "asset_sha256": asset["sha256"],
                "visual_version": program["visual_version"],
                "contract_version": program["contract_version"],
                "sequence": sequence,
                "previous_review_id": previous,
                "verdict": (
                    str(old.get("verdict")) if old.get("verdict") in VERDICTS else "NEEDS_REVISION"
                ),
                "hard_gates": dict(old.get("hard_gates", {"passed": False})),
                "score": old.get("score"),
                "recommendation": str(old.get("recommendation", "")),
                "findings": list(old.get("findings", [])),
                "blocking_issues": list(old.get("blocking_issues", [])),
            })
            migrated_review = program["reviews"][-1]
            gate_problems = pass_review_errors(migrated_review, asset)
            if gate_problems:
                migrated_review["verdict"] = "NEEDS_REVISION"
                migrated_review["blocking_issues"] = list(dict.fromkeys([
                    *migrated_review["blocking_issues"], *gate_problems,
                ]))
                warnings.append(f"{asset_id}: legacy PASS review {migrated_review['id']} downgraded; hard gates incomplete")

    # A legacy "approved" bit is not enough. Preserve the file and decision, but
    # downgrade lifecycle whenever current independent aesthetic reviews are absent.
    for asset in program["assets"]:
        if not asset.get("golden"):
            continue
        latest = matching_reviews(program, asset)
        missing = [
            family for family in required_promotion_reviews(asset)
            if (
                not latest.get(family) or latest[family]["verdict"] != "PASS"
                or not latest[family]["independent"] or pass_review_errors(latest[family], asset)
            )
        ]
        if missing:
            asset["lifecycle_stage"] = "finalist"
            asset["evidence_stage"] = "concept"
            asset["golden"] = None
            warnings.append(
                f"{asset['id']}: Golden state downgraded; missing current independent reviews: {', '.join(missing)}"
            )

    # Rebuild only slots whose migrated asset retained a valid Golden record.
    legacy_golden = state.get("golden", {}) if isinstance(state.get("golden"), dict) else {}
    for slot in GOLDEN_SLOTS:
        asset = legacy_to_asset.get(legacy_golden.get(slot))
        if asset and asset.get("golden"):
            allowed_classes, allowed_types = SLOT_RULES[slot]
            if asset["class"] in allowed_classes and asset["type"] in allowed_types:
                program["golden_slots"][slot] = asset["id"]
            else:
                warnings.append(f"{asset['id']}: removed from {slot}; class/type gate failed")

    op_id = normalize_operation_id(args.operation_id)
    program["migration_history"].append({
        "from": "legacy-v2-projections", "to_schema": PROGRAM_SCHEMA, "migrated_at": now,
        "backup_path": backup.relative_to(root).as_posix(),
        "backup_manifest_sha256": sha256_file(backup / "BACKUP_MANIFEST.json"),
        "warnings": warnings,
    })
    program["revision"] = 1
    program["updated_at"] = now
    result = {
        "status": "migrated", "backup_path": backup.relative_to(root).as_posix(),
        "warnings": warnings, "operation_id": op_id, "idempotent_replay": False,
    }
    program["operations"].append({
        "id": op_id, "command": "migrate", "fingerprint": operation_fingerprint("migrate", args),
        "committed_revision": 1, "created_at": now, "result": result,
    })
    validate_or_raise(root, program)
    atomic_write_json(program_path(root), program)
    repair_projections(root, program)
    return result


def cmd_repair_migration_hashes(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    """Explicitly upgrade the one legacy inventory-hash bug to the actual manifest-file hash.

    The repair is deliberately narrow: an unexpected value is rejected instead of
    being silently blessed.  The canonical revision and operation journal prove the
    repair, and all projections are regenerated by ``commit_operation``.
    """
    program = load_program(root)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        repaired: list[str] = []
        for index, item in enumerate(value.get("migration_history", [])):
            backup_dir, backup_rel = visual_path(
                root, str(item.get("backup_path", "")), must_exist=False,
                allowed_prefixes=("visual/manifests/migration_backups/",),
            )
            manifest_path = backup_dir / "BACKUP_MANIFEST.json"
            inspection = validate_backup_manifest(backup_dir)
            actual_hash = inspection["manifest_sha256"]
            current_hash = item.get("backup_manifest_sha256")
            if current_hash == actual_hash:
                continue
            if not inspection["legacy"] or current_hash != inspection["legacy_inventory_sha256"]:
                raise VisualStateError(
                    f"migration_history[{index}] is not the recognized legacy inventory-hash form; refusing repair"
                )
            item["backup_manifest_sha256"] = actual_hash
            repaired.append(backup_rel)
        return {
            "status": "repaired" if repaired else "already_correct",
            "repaired_backup_paths": repaired,
        }

    return commit_operation(
        root, program, operation_id=args.operation_id, command="repair-migration-hashes",
        args=args, mutate=mutate,
    )


def cmd_validate(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    errors = validate_program(root, program)
    drift = projection_drift(root, program) if not errors else []
    if drift:
        errors.append("repairable projection drift: " + ", ".join(drift))
    result = {
        "status": "OK" if not errors else "INVALID",
        "canonical_revision": program.get("revision"),
        "canonical_sha256": sha256_value(program),
        "errors": errors,
    }
    if errors and not args.no_fail:
        raise VisualStateError("visual program validation failed:\n- " + "\n- ".join(errors))
    return result


def cmd_repair(root: Path, _args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)
    repaired = repair_projections(root, program)
    return {"status": "repaired", "files": repaired, "canonical_revision": program["revision"]}


def cmd_register_asset(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        source, rel = visual_path(root, args.path, must_exist=True, allowed_prefixes=ASSET_AREA_PREFIXES)
        prompt_rel = None
        if args.prompt_path:
            prompt_file, prompt_rel = visual_path(
                root, args.prompt_path, must_exist=True, allowed_prefixes=("visual/prompts/",),
            )
            validate_local_provenance(root, prompt_file, prompt_rel, purpose="prompt")
        active_paths = {
            item["path"] for item in value["assets"]
            if item["lifecycle_stage"] not in {"deprecated", "rejected"}
        }
        if rel in active_paths:
            raise VisualStateError(f"active asset path is already registered: {rel}")
        related_ids = [*args.parent, *args.depends_on]
        for related_id in related_ids:
            asset_by_id(value, related_id)
        references = [validate_reference(root, item) for item in args.reference]
        cleanup_scope = list(dict.fromkeys(args.cleanup_scope or DEFAULT_CLEANUP_SCOPE))
        if args.content_origin in {"real_sensitive", "unknown"}:
            raise VisualStateError(
                "real_sensitive/unknown inputs cannot be registered under project visual/; use a controlled local temporary flow"
            )
        if args.privacy_classification == "unclassified":
            raise VisualStateError("unclassified inputs cannot be registered as repository visual assets")
        if args.egress_status == "confirmed_per_send" and not args.egress_receipt_ref:
            raise VisualStateError("confirmed_per_send requires --egress-receipt-ref")
        rights = {
            "status": args.rights_status,
            "commercial_use_allowed": bool(args.commercial_use_allowed),
            "derivative_use_allowed": bool(args.derivative_use_allowed),
            "attribution_required": bool(args.attribution_required),
            "attribution_text": args.attribution_text.strip() if args.attribution_text else None,
            "evidence_refs": list(dict.fromkeys(args.rights_evidence_ref)),
        }
        rights_problems = rights_errors(rights, label="rights")
        if rights_problems:
            raise VisualStateError("; ".join(rights_problems))
        now = utc_now()
        asset_id = f"VA-{dt.datetime.now(dt.timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:8]}"
        asset = {
            "id": asset_id,
            "name": args.name.strip(),
            "class": args.asset_class,
            "type": args.asset_type,
            "lifecycle_stage": args.stage,
            "freshness": "current",
            "evidence_stage": "concept",
            "evidence_binding": None,
            "version": 1,
            "path": rel,
            "sha256": sha256_file(source),
            "golden": None,
            "parents": list(dict.fromkeys(args.parent)),
            "references": list(dict.fromkeys(references)),
            "depends_on": list(dict.fromkeys(args.depends_on)),
            "created_by": args.creator.strip(),
            "tool": args.tool,
            "model": args.model,
            "prompt_path": prompt_rel,
            "medical_applicable": bool(args.medical_applicable or args.asset_type in AUTO_MEDICAL_ASSET_TYPES),
            "privacy": {
                "classification": args.privacy_classification,
                "content_origin": args.content_origin,
                "persistent_evidence_allowed": bool(args.allow_persistent_evidence),
                "external_egress": {
                    "status": args.egress_status,
                    "receipt_ref": args.egress_receipt_ref.strip() if args.egress_receipt_ref else None,
                },
                "cleanup_scope": cleanup_scope,
            },
            "rights": rights,
            "stale_reasons": [],
            "created_at": now,
            "updated_at": now,
            "notes": list(dict.fromkeys(args.note)),
        }
        value["assets"].append(asset)
        return {"status": "registered", "asset_id": asset_id, "sha256": asset["sha256"], "path": rel}

    return commit_operation(
        root, program, operation_id=args.operation_id, command="register-asset", args=args, mutate=mutate,
    )


def cmd_record_decision(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset_ids = list(dict.fromkeys(args.asset_id))
        for asset_id in asset_ids:
            asset_by_id(value, asset_id)
        if args.kind == "approval" and (args.status != "approved" or not asset_ids):
            raise VisualStateError("approval requires approved status and at least one asset")
        if args.kind == "approval":
            for asset_id in asset_ids:
                asset = asset_by_id(value, asset_id)
                if asset["lifecycle_stage"] not in {"finalist", "provisional", "aesthetic_golden"}:
                    raise VisualStateError("aesthetic approval may only name finalist/provisional/Golden assets")
        decision_id = next_numeric_id(value["decisions"], "D")
        value["decisions"].append({
            "id": decision_id, "occurred_at": utc_now(), "kind": args.kind, "status": args.status,
            "decided_by": args.decided_by.strip(), "asset_ids": asset_ids, "text": args.text.strip(),
            "preserve": list(dict.fromkeys(args.preserve)), "change": list(dict.fromkeys(args.change)),
        })
        if args.kind == "rejection" or args.status == "rejected":
            for asset_id in asset_ids:
                asset = asset_by_id(value, asset_id)
                asset["lifecycle_stage"] = "rejected"
                asset["updated_at"] = utc_now()
        return {"status": "recorded", "decision_id": decision_id}

    return commit_operation(
        root, program, operation_id=args.operation_id, command="record-decision", args=args, mutate=mutate,
    )


def cmd_record_review(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset = asset_by_id(value, args.asset_id)
        if args.independent and args.reviewer.strip().casefold() == asset["created_by"].strip().casefold():
            raise VisualStateError("independent reviewer must differ from the asset creator")
        prior = [
            item for item in value["reviews"]
            if item["asset_id"] == asset["id"] and item["family"] == args.family
        ]
        previous = max(prior, key=lambda item: item["sequence"], default=None)
        review_id = next_numeric_id(value["reviews"], "VR")
        hard_gates = {gate: True for gate in list(dict.fromkeys(args.gate))}
        record = {
            "id": review_id, "created_at": utc_now(), "reviewer": args.reviewer.strip(),
            "reviewer_kind": args.reviewer_kind, "family": args.family,
            "independent": bool(args.independent), "asset_id": asset["id"],
            "asset_version": asset["version"], "asset_sha256": asset["sha256"],
            "visual_version": value["visual_version"], "contract_version": value["contract_version"],
            "sequence": (previous["sequence"] + 1) if previous else 1,
            "previous_review_id": previous["id"] if previous else None,
            "verdict": args.verdict, "hard_gates": hard_gates,
            "score": args.score, "recommendation": args.recommendation or "",
            "findings": list(args.finding), "blocking_issues": list(args.blocking_issue),
        }
        problems = pass_review_errors(record, asset)
        if problems:
            raise VisualStateError("; ".join(problems))
        value["reviews"].append(record)
        return {"status": "recorded", "review_id": review_id, "asset_id": asset["id"]}

    return commit_operation(
        root, program, operation_id=args.operation_id, command="record-review", args=args, mutate=mutate,
    )


def cmd_add_medical_source(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset = asset_by_id(value, args.asset_id)
        if not asset["medical_applicable"]:
            raise VisualStateError("medical sources may only be attached to a medical-applicable asset")
        source_url = args.source_url
        if source_url:
            parsed = urlparse(source_url)
            if parsed.scheme != "https" or not parsed.netloc:
                raise VisualStateError("medical source URL must be an absolute HTTPS URL")
        document_rel = None
        document_hash = None
        if args.document_path:
            document, document_rel = visual_path(
                root, args.document_path, must_exist=True, allowed_prefixes=("visual/references/",),
            )
            validate_local_provenance(
                root, document, document_rel, purpose="medical source", require_rights=True,
            )
            document_hash = sha256_file(document)
        if not source_url and not document_rel:
            raise VisualStateError("medical source requires --source-url or --document-path")
        source_checksum = args.source_checksum.lower() if args.source_checksum else None
        if source_checksum and not SHA256_RE.fullmatch(source_checksum):
            raise VisualStateError("source checksum must be 64 lowercase hexadecimal SHA-256 characters")
        fixed_reference = args.fixed_reference.strip() if args.fixed_reference else None
        if source_url and not document_hash and not source_checksum:
            raise VisualStateError(
                "URL medical sources require --source-checksum or a locally archived --document-path; "
                "--fixed-reference is locator-only"
            )
        if not document_hash and not source_checksum:
            raise VisualStateError(
                "medical sources require content-addressed evidence via --source-checksum or --document-path"
            )
        publication = dt.date.fromisoformat(args.publication_date)
        revision = dt.date.fromisoformat(args.source_revision_date)
        accessed = dt.date.fromisoformat(args.accessed_date)
        if publication > revision or revision > accessed:
            raise VisualStateError("medical source dates must satisfy publication <= revision <= accessed")
        source_id = next_numeric_id(value["medical_sources"], "MS")
        value["medical_sources"].append({
            "id": source_id, "asset_id": asset["id"], "title": args.title.strip(),
            "authority": args.authority.strip(), "jurisdiction": args.jurisdiction.strip(),
            "population": args.population.strip(), "gestational_stage": args.gestational_stage.strip(),
            "source_version": args.source_version.strip(),
            "publication_date": args.publication_date,
            "source_revision_date": args.source_revision_date,
            "accessed_date": args.accessed_date,
            "source_url": source_url, "document_path": document_rel,
            "fixed_reference": fixed_reference, "source_checksum": source_checksum,
            "document_sha256": document_hash, "notes": list(args.note), "created_at": utc_now(),
        })
        return {"status": "recorded", "medical_source_id": source_id, "asset_id": asset["id"]}

    return commit_operation(
        root, program, operation_id=args.operation_id, command="add-medical-source", args=args, mutate=mutate,
    )


def cmd_verify_medical(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset = asset_by_id(value, args.asset_id)
        if not asset["medical_applicable"]:
            raise VisualStateError("asset is not medical-applicable")
        if not args.independent:
            raise VisualStateError("medical verification must be independent")
        if args.verdict == "VERIFIED" and args.verifier_kind not in {"human", "external_specialist"}:
            raise VisualStateError("custom-agent/subagent can never issue a VERIFIED medical decision")
        if args.verifier.strip().casefold() == asset["created_by"].strip().casefold():
            raise VisualStateError("independent medical verifier must differ from the asset creator")
        source_ids = list(dict.fromkeys(args.source_id))
        if not source_ids:
            raise VisualStateError("medical verification requires at least one structured source")
        for source_id in source_ids:
            source = next((item for item in value["medical_sources"] if item["id"] == source_id), None)
            if not source or source["asset_id"] != asset["id"]:
                raise VisualStateError(f"medical source is missing or belongs to another asset: {source_id}")
        attestation, attestation_rel = visual_path(
            root, args.attestation_path, must_exist=True,
            allowed_prefixes=("visual/reviews/medical/", "visual/system/attestations/"),
        )
        validate_local_provenance(
            root, attestation, attestation_rel,
            purpose="medical attestation", require_rights=False,
        )
        attestation_hash = sha256_file(attestation)
        prior = [item for item in value["medical_verifications"] if item["asset_id"] == asset["id"]]
        verification_id = next_numeric_id(value["medical_verifications"], "MV")
        value["medical_verifications"].append({
            "id": verification_id, "created_at": utc_now(), "asset_id": asset["id"],
            "asset_version": asset["version"], "asset_sha256": asset["sha256"],
            "sequence": max((item["sequence"] for item in prior), default=0) + 1,
            "verifier": args.verifier.strip(), "verifier_kind": args.verifier_kind,
            "professional_role": args.professional_role,
            "credential_ref": args.credential_ref.strip(), "independent": True,
            "source_ids": source_ids, "scope": args.scope.strip(), "verdict": args.verdict,
            "attestation_path": attestation_rel, "attestation_sha256": attestation_hash,
            "notes": list(args.note),
        })
        return {
            "status": "verified" if args.verdict == "VERIFIED" else "rejected",
            "medical_verification_id": verification_id, "asset_id": asset["id"],
        }

    return commit_operation(
        root, program, operation_id=args.operation_id, command="verify-medical", args=args, mutate=mutate,
    )


def cmd_record_evidence(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset = asset_by_id(value, args.asset_id)
        if not args.independent:
            raise VisualStateError("evidence certification must be independent")
        if args.verifier.strip().casefold() == asset["created_by"].strip().casefold():
            raise VisualStateError("independent evidence verifier must differ from the asset creator")
        source_tag = safe_text(args.source_tag, label="source_tag", minimum=2, maximum=200)
        build_hash = safe_text(args.build_hash, label="build_hash", minimum=7, maximum=200)
        safe_text(args.os_name, label="os", maximum=200)
        safe_text(args.device, label="device", maximum=300)
        safe_text(args.test_suite, label="test_suite", minimum=2, maximum=300)
        if args.verifier_role not in EVIDENCE_ROLE_BY_CATEGORY[args.category]:
            raise VisualStateError(
                f"verifier role {args.verifier_role} is not authorized for {args.category} evidence"
            )
        privacy = asset["privacy"]
        if not privacy["persistent_evidence_allowed"] or privacy["content_origin"] in {"real_sensitive", "unknown"}:
            raise VisualStateError(
                "privacy policy forbids persistent repository evidence for this asset; per-send egress does not override it"
            )
        evidence_privacy = {
            "classification": args.privacy_classification,
            "content_origin": args.content_origin,
            "persistent_evidence_allowed": True,
            "external_egress": {"status": "prohibited", "receipt_ref": None},
        }
        privacy_problems = validate_privacy_record(evidence_privacy, label="evidence privacy")
        if privacy_problems:
            raise VisualStateError("; ".join(privacy_problems))
        paths: list[str] = []
        hashes: dict[str, str] = {}
        for artifact_value in args.artifact_path:
            artifact, rel = visual_path(
                root, artifact_value, must_exist=True,
                allowed_prefixes=("visual/reviews/", "visual/system/attestations/"),
            )
            if rel in hashes:
                raise VisualStateError(f"duplicate/aliased evidence path: {rel}")
            paths.append(rel)
            hashes[rel] = sha256_file(artifact)
        if not paths:
            raise VisualStateError("evidence record requires at least one artifact")
        _, credential_rel = visual_path(
            root, args.credential_or_attestation, must_exist=True,
            allowed_prefixes=("visual/reviews/", "visual/system/attestations/"),
        )
        if credential_rel not in hashes:
            raise VisualStateError(
                "credential_or_attestation must be explicitly included as a hashed --artifact-path"
            )
        prior = [
            item for item in value["evidence_records"]
            if item["asset_id"] == asset["id"] and item["category"] == args.category
        ]
        evidence_id = next_numeric_id(value["evidence_records"], "EV")
        value["evidence_records"].append({
            "id": evidence_id, "created_at": utc_now(), "asset_id": asset["id"],
            "asset_version": asset["version"], "asset_sha256": asset["sha256"],
            "category": args.category, "sequence": max((item["sequence"] for item in prior), default=0) + 1,
            "source_tag": source_tag, "build_hash": build_hash, "platform": args.platform,
            "os": args.os_name.strip(), "device": args.device.strip(), "test_suite": args.test_suite.strip(),
            "verifier": args.verifier.strip(), "verifier_role": args.verifier_role,
            "credential_or_attestation": credential_rel,
            "independent": True, "verdict": args.verdict, "privacy": evidence_privacy,
            "artifact_paths": paths, "artifact_sha256": hashes, "notes": list(args.note),
        })
        return {"status": "recorded", "evidence_id": evidence_id, "category": args.category}

    return commit_operation(
        root, program, operation_id=args.operation_id, command="record-evidence", args=args, mutate=mutate,
    )


def add_structured_stale_reason(
    asset: dict[str, Any], *, code: str, source_asset_id: str | None, detail: str, recorded_at: str,
) -> bool:
    signature = (code, source_asset_id, detail)
    existing = {
        (item.get("code"), item.get("source_asset_id"), item.get("detail"))
        for item in asset["stale_reasons"]
    }
    appended = signature not in existing
    if appended:
        asset["stale_reasons"].append({
            "code": code,
            "source_asset_id": source_asset_id,
            "detail": detail,
            "recorded_at": recorded_at,
        })
    target_freshness = (
        "stale_contract_conflict"
        if any(item.get("code") == "contract_conflict" for item in asset["stale_reasons"])
        else "stale"
    )
    changed = appended or asset["freshness"] != target_freshness
    asset["freshness"] = target_freshness
    if changed:
        asset["updated_at"] = recorded_at
    return changed


def mark_assets_stale(
    program: dict[str, Any],
    source_id: str,
    *,
    code: str,
    detail: str,
    scope: str,
    excluded_ids: set[str] | None = None,
) -> list[str]:
    """Mark the explicit source and/or transitive dependents; exclusions are traversal barriers."""
    excluded = excluded_ids or set()
    changed: list[str] = []
    now = utc_now()
    if scope in {"source", "source-and-dependents"} and source_id not in excluded:
        source = asset_by_id(program, source_id)
        if source["lifecycle_stage"] not in {"deprecated", "rejected"} and add_structured_stale_reason(
            source, code=code, source_asset_id=source_id, detail=detail, recorded_at=now,
        ):
            changed.append(source_id)
    if scope == "source":
        return changed
    frontier = [source_id]
    seen = {source_id}
    while frontier:
        parent = frontier.pop(0)
        for asset in program["assets"]:
            asset_id = asset["id"]
            relations = set(asset["depends_on"]) | set(asset["parents"])
            if parent not in relations or asset_id in seen:
                continue
            seen.add(asset_id)
            if asset_id in excluded:
                # A replacement Golden derived from the old anchor is explicitly
                # accepted as the new root. It and its branch must not be invalidated.
                continue
            frontier.append(asset_id)
            if asset["lifecycle_stage"] not in {"deprecated", "rejected"} and add_structured_stale_reason(
                asset, code=code, source_asset_id=source_id, detail=detail, recorded_at=now,
            ):
                changed.append(asset_id)
    return changed


def cmd_mark_stale(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset_by_id(value, args.asset_id)
        changed = mark_assets_stale(
            value, args.asset_id, code=args.reason_code, detail=args.reason.strip(), scope=args.scope,
        )
        return {
            "status": "updated", "scope": args.scope, "reason_code": args.reason_code,
            "stale_asset_ids": changed,
        }

    return commit_operation(
        root, program, operation_id=args.operation_id, command="mark-stale", args=args, mutate=mutate,
    )


def approval_decision(program: dict[str, Any], decision_id: str, asset_id: str) -> dict[str, Any]:
    decision = next((item for item in program["decisions"] if item["id"] == decision_id), None)
    if not decision:
        raise VisualStateError(f"decision not found: {decision_id}")
    if decision["kind"] != "approval" or decision["status"] != "approved" or asset_id not in decision["asset_ids"]:
        raise VisualStateError("Golden promotion requires a user aesthetic approval naming the asset")
    return decision


def validate_slot(asset: dict[str, Any], slot: str) -> tuple[str, str | None]:
    if slot.startswith("baby_anchor:"):
        stage = slot.split(":", 1)[1].strip()
        if not stage or len(stage) > 80 or not re.fullmatch(r"[A-Za-z0-9_\-\u4e00-\u9fff]+", stage):
            raise VisualStateError("Baby anchor stage must be a non-empty safe identifier")
        if asset["class"] not in {"S", "A"} or asset["type"] != "baby":
            raise VisualStateError("Baby anchor requires an S/A-class Baby asset")
        return "baby_anchor", stage
    if slot not in SLOT_RULES:
        raise VisualStateError(f"invalid Golden slot: {slot}")
    classes, types = SLOT_RULES[slot]
    if asset["class"] not in classes or asset["type"] not in types:
        raise VisualStateError(
            f"Golden slot {slot} requires class {sorted(classes)} and type {sorted(types)}"
        )
    return slot, None


def cmd_promote_golden(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset = asset_by_id(value, args.asset_id)
        if asset["lifecycle_stage"] not in {"finalist", "provisional", "aesthetic_golden"}:
            raise VisualStateError("only finalist, provisional, or existing aesthetic Golden may be promoted")
        if asset["freshness"] != "current":
            raise VisualStateError("stale assets cannot be promoted")
        privacy = asset["privacy"]
        if not privacy["persistent_evidence_allowed"] or privacy["content_origin"] in {"real_sensitive", "unknown"}:
            raise VisualStateError("privacy policy forbids a persistent Golden for this asset")
        if not rights_are_promotable(asset.get("rights")):
            raise VisualStateError(
                "Golden promotion requires verified rights with commercial and derivative use allowed"
            )
        approval_decision(value, args.decision_id, asset["id"])
        slot_value = args.slot.strip() if isinstance(args.slot, str) else None
        no_slot = slot_value is None or slot_value.casefold() == "none"
        if no_slot and args.replace_slot:
            raise VisualStateError("--replace-slot is invalid when no canonical slot is requested")
        slot_kind: str | None
        stage: str | None
        if no_slot:
            slot_kind, stage = None, None
        else:
            slot_kind, stage = validate_slot(asset, slot_value)
        latest = matching_reviews(value, asset)
        missing = [
            family for family in sorted(required_promotion_reviews(asset))
            if (
                not latest.get(family) or latest[family]["verdict"] != "PASS"
                or not latest[family]["independent"] or pass_review_errors(latest[family], asset)
            )
        ]
        if missing:
            raise VisualStateError(
                "missing current independent hard-gate-complete PASS reviews: " + ", ".join(missing)
            )
        if asset["medical_applicable"] and medical_status(value, asset) != "verified":
            raise VisualStateError("medical-applicable Golden requires structured independent professional verification")
        current = None
        if slot_kind == "baby_anchor":
            current = value["golden_slots"]["baby_anchors"].get(stage)
        elif slot_kind is not None:
            current = value["golden_slots"][slot_kind]
        if current and current != asset["id"] and not args.replace_slot:
            raise VisualStateError("Golden slot is occupied; pass --replace-slot for explicit replacement")
        source, _ = visual_path(root, asset["path"], must_exist=True)
        digest = sha256_file(source)
        if digest != asset["sha256"]:
            raise VisualStateError("asset changed after registration; register a new immutable asset")
        _, golden_rel = content_addressed_copy(root, source, digest)
        old_slot_asset = current
        if slot_kind == "baby_anchor":
            value["golden_slots"]["baby_anchors"][stage] = asset["id"]
        elif slot_kind is not None:
            value["golden_slots"][slot_kind] = asset["id"]
        changed = []
        if slot_kind is not None and old_slot_asset and old_slot_asset != asset["id"]:
            changed = mark_assets_stale(
                value,
                old_slot_asset,
                code="golden_replaced",
                detail=f"Golden slot {slot_value} replaced by {asset['id']}",
                scope="dependents",
                excluded_ids={asset["id"]},
            )
        now = utc_now()
        asset["golden"] = {
            "path": golden_rel, "sha256": digest, "decision_id": args.decision_id,
            "approved_at": now, "asset_version": asset["version"],
        }
        # Creative/user approval intentionally stops here. Release readiness is a separate expert-evidence command.
        asset["lifecycle_stage"] = "aesthetic_golden"
        asset["evidence_stage"] = "aesthetic_golden"
        asset["evidence_binding"] = None
        asset["updated_at"] = now
        return {
            "status": "aesthetic_golden", "asset_id": asset["id"], "slot": slot_value if not no_slot else None,
            "golden_path": golden_rel, "golden_sha256": digest, "stale_asset_ids": changed,
        }

    return commit_operation(
        root, program, operation_id=args.operation_id, command="promote-golden", args=args, mutate=mutate,
    )


def cmd_advance_evidence(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    validate_or_raise(root, program)

    def mutate(value: dict[str, Any]) -> dict[str, Any]:
        asset = asset_by_id(value, args.asset_id)
        source_tag = safe_text(args.source_tag, label="source_tag", minimum=2, maximum=200)
        build_hash = safe_text(args.build_hash, label="build_hash", minimum=7, maximum=200)
        if asset["freshness"] != "current":
            raise VisualStateError("stale assets cannot advance evidence stage")
        if asset["lifecycle_stage"] != "aesthetic_golden":
            raise VisualStateError("advanced evidence requires aesthetic_golden lifecycle")
        if args.to == "integrated":
            if asset["evidence_stage"] != "aesthetic_golden":
                raise VisualStateError("integrated evidence requires aesthetic_golden evidence stage")
            problems = evidence_gate_errors(
                value, asset, target="integrated", source_tag=source_tag, build_hash=build_hash,
            )
            if problems:
                raise VisualStateError("; ".join(problems))
            asset["evidence_binding"] = {
                "source_tag": source_tag, "build_hash": build_hash, "bound_at": utc_now(),
            }
        elif args.to == "matrix_accepted":
            if asset["evidence_stage"] != "integrated":
                raise VisualStateError("matrix_accepted requires integrated evidence stage")
            binding = asset.get("evidence_binding")
            if not isinstance(binding, dict) or (
                binding.get("source_tag") != source_tag or binding.get("build_hash") != build_hash
            ):
                raise VisualStateError("matrix evidence must use the exact integration source_tag/build_hash")
            problems = evidence_gate_errors(
                value, asset, target="matrix_accepted", source_tag=source_tag, build_hash=build_hash,
            )
            if problems:
                raise VisualStateError("; ".join(problems))
        elif args.to == "release_signed":
            if asset["evidence_stage"] != "matrix_accepted":
                raise VisualStateError("release_signed requires matrix_accepted evidence stage")
            binding = asset.get("evidence_binding")
            if not isinstance(binding, dict) or (
                binding.get("source_tag") != source_tag or binding.get("build_hash") != build_hash
            ):
                raise VisualStateError("release evidence must use the exact integration source_tag/build_hash")
            problems = evidence_gate_errors(
                value, asset, target="release_signed", source_tag=source_tag, build_hash=build_hash,
            )
            if problems:
                raise VisualStateError("; ".join(problems))
        asset["evidence_stage"] = args.to
        asset["updated_at"] = utc_now()
        return {"status": "advanced", "asset_id": asset["id"], "evidence_stage": args.to}

    return commit_operation(
        root, program, operation_id=args.operation_id, command="advance-evidence", args=args, mutate=mutate,
    )


def cmd_status(root: Path, _args: argparse.Namespace) -> dict[str, Any]:
    program = load_program(root)
    errors = validate_program(root, program)
    drift = projection_drift(root, program) if not errors else []
    lifecycle_counts: dict[str, int] = {}
    freshness_counts: dict[str, int] = {}
    evidence_counts: dict[str, int] = {}
    for asset in program["assets"]:
        lifecycle_counts[asset["lifecycle_stage"]] = lifecycle_counts.get(asset["lifecycle_stage"], 0) + 1
        freshness_counts[asset["freshness"]] = freshness_counts.get(asset["freshness"], 0) + 1
        evidence_counts[asset["evidence_stage"]] = evidence_counts.get(asset["evidence_stage"], 0) + 1
    return {
        "status": "OK" if not errors and not drift else "INVALID",
        "canonical_revision": program["revision"],
        "canonical_sha256": sha256_value(program),
        "visual_version": program["visual_version"],
        "current_gate": program["current_gate"],
        "release_status": program["release_status"],
        "golden_slots": program["golden_slots"],
        "lifecycle_counts": lifecycle_counts,
        "freshness_counts": freshness_counts,
        "evidence_stage_counts": evidence_counts,
        "projection_drift": drift,
        "errors": errors,
    }


def add_operation_id(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument(
        "--operation-id",
        help="stable OP-* idempotency key; generated when omitted (pass one when retry safety matters)",
    )


def parser() -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser(description=__doc__)
    root_parser.add_argument("--project-root", help="YunMom project root; otherwise discover from strong markers")
    sub = root_parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a new canonical visual program")
    add_operation_id(init)
    migrate = sub.add_parser("migrate", help="explicitly back up and migrate legacy v2 projections")
    add_operation_id(migrate)
    repair_migration = sub.add_parser(
        "repair-migration-hashes",
        help="explicitly repair the legacy backup inventory-hash bug and journal the change",
    )
    add_operation_id(repair_migration)
    validate = sub.add_parser("validate", help="validate canonical state, files, and projections")
    validate.add_argument("--no-fail", action="store_true")
    sub.add_parser("repair-projections", help="regenerate all repairable projections from canonical state")

    register = sub.add_parser("register-asset", help="register a new immutable visual asset")
    add_operation_id(register)
    register.add_argument("--name", required=True)
    register.add_argument("--class", dest="asset_class", required=True, choices=sorted(ASSET_CLASSES))
    register.add_argument("--type", dest="asset_type", required=True, choices=sorted(ASSET_TYPES))
    register.add_argument("--path", required=True)
    register.add_argument("--stage", default="candidate", choices=sorted(REGISTERABLE_STAGES))
    register.add_argument("--creator", required=True)
    register.add_argument("--parent", action="append", default=[])
    register.add_argument("--depends-on", action="append", default=[])
    register.add_argument("--reference", action="append", default=[])
    register.add_argument("--tool")
    register.add_argument("--model")
    register.add_argument("--prompt-path")
    register.add_argument("--medical-applicable", action="store_true")
    register.add_argument(
        "--privacy-classification", default="unclassified", choices=sorted(PRIVACY_CLASSIFICATIONS),
        help="fail-closed data classification; unclassified disables persistence and egress",
    )
    register.add_argument("--content-origin", default="unknown", choices=sorted(CONTENT_ORIGINS))
    register.add_argument("--allow-persistent-evidence", action="store_true")
    register.add_argument("--egress-status", default="prohibited", choices=sorted(EGRESS_STATUSES))
    register.add_argument("--egress-receipt-ref")
    register.add_argument("--cleanup-scope", action="append", choices=sorted(CLEANUP_SCOPES), default=[])
    register.add_argument("--rights-status", default="unverified", choices=sorted(RIGHTS_STATUSES))
    register.add_argument("--commercial-use-allowed", action="store_true")
    register.add_argument("--derivative-use-allowed", action="store_true")
    register.add_argument("--attribution-required", action="store_true")
    register.add_argument("--attribution-text")
    register.add_argument("--rights-evidence-ref", action="append", default=[])
    register.add_argument("--note", action="append", default=[])

    decision = sub.add_parser("record-decision", help="record user feedback or aesthetic approval")
    add_operation_id(decision)
    decision.add_argument("--kind", required=True, choices=sorted(DECISION_KINDS))
    decision.add_argument("--status", required=True, choices=sorted(DECISION_STATUSES))
    decision.add_argument("--decided-by", default="user")
    decision.add_argument("--text", required=True)
    decision.add_argument("--asset-id", action="append", default=[])
    decision.add_argument("--preserve", action="append", default=[])
    decision.add_argument("--change", action="append", default=[])

    review = sub.add_parser("record-review", help="record one sequenced review bound to asset hash/version")
    add_operation_id(review)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--reviewer-kind", required=True, choices=sorted(REVIEWER_KINDS))
    review.add_argument("--family", required=True, choices=sorted(REVIEW_FAMILIES))
    review.add_argument("--verdict", required=True, choices=sorted(VERDICTS))
    review.add_argument("--asset-id", required=True)
    review.add_argument("--independent", action="store_true")
    review.add_argument("--score", type=float)
    review.add_argument("--gate", action="append", default=[])
    review.add_argument("--recommendation")
    review.add_argument("--finding", action="append", default=[])
    review.add_argument("--blocking-issue", action="append", default=[])

    source = sub.add_parser("add-medical-source", help="attach a structured clinical source to an asset")
    add_operation_id(source)
    source.add_argument("--asset-id", required=True)
    source.add_argument("--title", required=True)
    source.add_argument("--authority", required=True)
    source.add_argument("--jurisdiction", required=True)
    source.add_argument("--population", required=True)
    source.add_argument("--gestational-stage", required=True)
    source.add_argument("--source-version", required=True)
    source.add_argument("--publication-date", required=True, type=lambda value: checked_date(value, "publication-date"))
    source.add_argument("--source-revision-date", required=True, type=lambda value: checked_date(value, "source-revision-date"))
    source.add_argument("--accessed-date", default=today_utc(), type=lambda value: checked_date(value, "accessed-date"))
    source.add_argument("--source-url")
    source.add_argument("--fixed-reference")
    source.add_argument("--source-checksum")
    source.add_argument("--document-path")
    source.add_argument("--note", action="append", default=[])

    medical = sub.add_parser("verify-medical", help="record structured independent professional validation")
    add_operation_id(medical)
    medical.add_argument("--asset-id", required=True)
    medical.add_argument("--verifier", required=True)
    medical.add_argument("--verifier-kind", required=True, choices=sorted(REVIEWER_KINDS))
    medical.add_argument("--professional-role", required=True, choices=sorted(PROFESSIONAL_ROLES))
    medical.add_argument("--credential-ref", required=True)
    medical.add_argument("--source-id", action="append", required=True)
    medical.add_argument("--scope", required=True)
    medical.add_argument("--verdict", required=True, choices=sorted(MEDICAL_VERDICTS))
    medical.add_argument("--attestation-path", required=True)
    medical.add_argument("--independent", action="store_true")
    medical.add_argument("--note", action="append", default=[])

    evidence = sub.add_parser("record-evidence", help="record hash-bound integration, matrix, or release evidence")
    add_operation_id(evidence)
    evidence.add_argument("--asset-id", required=True)
    evidence.add_argument("--category", required=True, choices=sorted(EVIDENCE_CATEGORIES))
    evidence.add_argument("--source-tag", required=True)
    evidence.add_argument("--build-hash", required=True)
    evidence.add_argument("--platform", required=True, choices=sorted(EVIDENCE_PLATFORMS))
    evidence.add_argument("--os", dest="os_name", required=True)
    evidence.add_argument("--device", required=True)
    evidence.add_argument("--test-suite", required=True)
    evidence.add_argument("--verifier", required=True)
    evidence.add_argument("--verifier-role", required=True, choices=sorted(EVIDENCE_VERIFIER_ROLES))
    evidence.add_argument("--credential-or-attestation", required=True)
    evidence.add_argument("--verdict", required=True, choices=sorted(VERDICTS))
    evidence.add_argument("--artifact-path", action="append", required=True)
    evidence.add_argument(
        "--privacy-classification", required=True, choices=sorted(PRIVACY_CLASSIFICATIONS),
    )
    evidence.add_argument("--content-origin", required=True, choices=sorted(CONTENT_ORIGINS))
    evidence.add_argument("--independent", action="store_true")
    evidence.add_argument("--note", action="append", default=[])

    stale = sub.add_parser("mark-stale", help="mark source and/or transitive dependents with structured reasons")
    add_operation_id(stale)
    stale.add_argument("asset_id")
    stale.add_argument("--reason", required=True)
    stale.add_argument("--reason-code", default="manual", choices=sorted(STALE_REASON_CODES))
    stale.add_argument(
        "--scope", default="source-and-dependents",
        choices=("source", "dependents", "source-and-dependents"),
        help="explicitly choose whether the named source, its descendants, or both become stale",
    )

    promote = sub.add_parser("promote-golden", help="promote only to aesthetic_golden using content-addressed storage")
    add_operation_id(promote)
    promote.add_argument("asset_id")
    promote.add_argument("--decision-id", required=True)
    promote.add_argument(
        "--slot",
        help="optional canonical pointer: named master slot or baby_anchor:<stage>; omit/use 'none' for content-only Golden",
    )
    promote.add_argument("--replace-slot", action="store_true")

    advance = sub.add_parser("advance-evidence", help="advance evidence independently of asset lifecycle")
    add_operation_id(advance)
    advance.add_argument("asset_id")
    advance.add_argument("--to", required=True, choices=("integrated", "matrix_accepted", "release_signed"))
    advance.add_argument("--source-tag", required=True)
    advance.add_argument("--build-hash", required=True)

    sub.add_parser("status", help="report canonical lifecycle, freshness, and projection state")
    return root_parser


def checked_date(value: str, label: str) -> str:
    if not DATE_RE.fullmatch(value):
        raise argparse.ArgumentTypeError(f"{label} must be YYYY-MM-DD")
    try:
        dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} is not a valid date") from exc
    return value


COMMANDS: dict[str, Callable[[Path, argparse.Namespace], dict[str, Any]]] = {
    "init": cmd_init,
    "migrate": migrate_legacy,
    "repair-migration-hashes": cmd_repair_migration_hashes,
    "validate": cmd_validate,
    "repair-projections": cmd_repair,
    "register-asset": cmd_register_asset,
    "record-decision": cmd_record_decision,
    "record-review": cmd_record_review,
    "add-medical-source": cmd_add_medical_source,
    "verify-medical": cmd_verify_medical,
    "record-evidence": cmd_record_evidence,
    "mark-stale": cmd_mark_stale,
    "promote-golden": cmd_promote_golden,
    "advance-evidence": cmd_advance_evidence,
    "status": cmd_status,
}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = find_project_root(args.project_root)
        # validate/status are truly read-only; canonical writes are atomic, so they
        # need not create or touch the lock file merely to inspect a snapshot.
        if args.command in {"validate", "status"}:
            result = COMMANDS[args.command](root, args)
        else:
            with project_lock(root):
                result = COMMANDS[args.command](root, args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except VisualStateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
