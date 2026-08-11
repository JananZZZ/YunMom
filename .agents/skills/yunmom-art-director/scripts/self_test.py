#!/usr/bin/env python3
"""Hermetic positive/negative tests for YunMom visual-program tooling."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


HERE = Path(__file__).resolve().parent
OPS = HERE / "visual_ops.py"
CONTACT = HERE / "build_contact_sheet.py"
MANIFEST_VERIFY = HERE / "verify_package_manifest.py"
TOKEN_PRIORITY = [
    "system_accessibility_high_contrast",
    "medical_safety_crisis",
    "error_permission_destructive_confirmation",
    "temporary_interaction",
    "silent_day_mood_ambient",
    "task",
    "time_weather_decoration",
]
SOURCE_TAG = "refs/tags/yunmom-v1.0.0-test"
BUILD_HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
RELEASE_ROLES = ("PO", "TECH", "QA", "MD", "LEGAL", "SEC", "ETHICS")
BASE_GATES = {
    "brand": ("BRAND_DISTINCTIVENESS", "BRAND_CONSISTENCY"),
    "visual": ("VISUAL_HIERARCHY", "VISUAL_COHERENCE", "NON_TEMPLATE_QUALITY"),
    "production": ("IMPLEMENTATION_FEASIBILITY", "TOKEN_COMPLIANCE", "PERFORMANCE_RISK"),
    "medical": ("MEDICAL_SCOPE_ACCURACY", "SAFETY_SEVERITY_PRESERVED", "NO_DIAGNOSIS_TREATMENT"),
    "accessibility_safety": (
        "WCAG_2_2_AA", "SCREEN_READER", "TEXT_SCALE_200", "REDUCE_MOTION", "NON_COLOR_SAFETY",
    ),
}
TYPE_GATES = {
    "screen": {"accessibility_safety": ("P0_FLOW_COMPLETABLE",)},
    "motion": {"accessibility_safety": ("REDUCE_MOTION_EQUIVALENCE",)},
    "widget": {"accessibility_safety": (
        "WIDGET_PRIVACY_MINIMIZATION", "WIDGET_READ_ONLY", "WIDGET_MAX_24H_EXPIRY",
    )},
    "safety": {
        "medical": ("R0_R3_SEVERITY_ACTION", "DISMISS_NOT_RESOLVE"),
        "accessibility_safety": ("R0_R3_TEXT_ICON_ACTION", "DISMISS_NOT_RESOLVE"),
    },
    "gentle_closure": {
        "medical": ("GENTLE_CLOSURE_CLINICAL_BOUNDARY",),
        "accessibility_safety": ("TRAUMA_INFORMED_COMPLETION", "GENTLE_CLOSURE_PRIVACY"),
    },
}


def invoke(script: Path, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [sys.executable, str(script), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != expect:
        raise AssertionError(
            f"{script.name}: expected exit {expect}, got {completed.returncode}\n"
            f"args={args}\nstdout={completed.stdout}\nstderr={completed.stderr}"
        )
    return completed


def run_ops(root: Path, *args: str, expect: int = 0) -> dict[str, Any] | None:
    completed = invoke(OPS, "--project-root", str(root), *args, expect=expect)
    if expect:
        return None
    return json.loads(completed.stdout)


def seed_tokens(root: Path) -> None:
    path = root / "visual" / "system" / "design_tokens.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    tokens = {
        "schema_version": 1,
        "token_version": "1.0.0",
        "status": "bootstrap_provisional",
        "implementation_ready": False,
        "contract_decisions": ["TOK-001", "TOK-002", "TOK-003"],
        "source_golden_ids": [],
        "governance": {
            "sole_implementation_source": True,
            "medical_severity_source": "signed_local_rule_pack_not_tokens",
            "breaking_change_requires": "CHG-001",
            "required_approvals": ["DESIGN", "ANDROID", "IOS", "QA"],
            "additional_approvals_for_safety_or_accessibility": ["MD"],
            "generator_version": None,
            "approved_content_sha256": None,
            "approval_records": [],
            "regression_evidence_records": [],
            "note": "Self-test provisional Token bundle.",
        },
        "semantic_priority": TOKEN_PRIORITY,
        "primitive": {
            "color": {}, "fontFamily": {}, "fontSize": {}, "fontWeight": {},
            "lineHeight": {}, "space": {}, "radius": {}, "elevation": {},
        },
        "semantic": {
            family: {"selfTest": True} for family in (
                "surface", "content", "action", "focus", "disabled", "icon", "highContrast",
                "safety", "destructive", "ambient", "touchTarget", "motion", "layer",
            )
        },
        "platform_mappings": {
            platform: {
                "status": "required_present_disabled",
                "target": f"generated/{platform}.tokens",
                "generator": None,
                "source_content_sha256": None,
                "output_sha256": None,
                "verification_evidence_ids": [],
            }
            for platform in ("flutter", "rive", "ios_widget", "android_widget")
        },
    }
    content_fields = (
        "token_version", "contract_decisions", "source_golden_ids",
        "semantic_priority", "primitive", "semantic",
    )
    canonical = json.dumps(
        {field: tokens[field] for field in content_fields},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    tokens["content_sha256"] = hashlib.sha256(canonical).hexdigest()
    path.write_text(json.dumps(tokens, indent=2) + "\n", encoding="utf-8")


def make_ppm(path: Path, rgb: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 32, 24
    pixels = bytes(rgb) * width * height
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + pixels)


def write_provenance(
    root: Path,
    source: Path,
    *,
    reference_role: str = "production_input",
    classification: str = "public_product",
    content_origin: str = "synthetic",
    rights_status: str = "owned",
    rights_evidence: tuple[str, ...] = ("RIGHTS-SELFTEST-OWNED",),
) -> Path:
    rel = source.relative_to(root).as_posix()
    sidecar = source.with_suffix(".provenance.json")
    sidecar.write_text(json.dumps({
        "schema_version": 1,
        "path": rel,
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "reference_role": reference_role,
        "privacy": {
            "classification": classification,
            "content_origin": content_origin,
            "persistent_evidence_allowed": True,
            "external_egress": {"status": "prohibited", "receipt_ref": None},
        },
        "rights": {
            "status": rights_status,
            "commercial_use_allowed": rights_status != "unverified",
            "derivative_use_allowed": rights_status != "unverified",
            "attribution_required": False,
            "attribution_text": None,
            "evidence_refs": list(rights_evidence),
        },
    }, indent=2), encoding="utf-8")
    return sidecar


def register(
    root: Path,
    path: Path,
    *,
    op: str,
    name: str,
    asset_class: str,
    asset_type: str,
    stage: str = "finalist",
    creator: str = "generator",
    extra: tuple[str, ...] = (),
) -> dict[str, Any]:
    result = run_ops(
        root, "register-asset", "--operation-id", op,
        "--name", name, "--class", asset_class, "--type", asset_type,
        "--path", str(path), "--stage", stage, "--creator", creator,
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--egress-status", "prohibited", *extra,
        "--rights-status", "owned", "--commercial-use-allowed", "--derivative-use-allowed",
        "--rights-evidence-ref", "RIGHTS-SELFTEST-OWNED",
    )
    assert result is not None
    return result


def review(
    root: Path, asset_id: str, family: str, op: str, reviewer: str, *, asset_type: str,
) -> str:
    gates = [*BASE_GATES[family], *TYPE_GATES.get(asset_type, {}).get(family, ())]
    result = run_ops(
        root, "record-review", "--operation-id", op,
        "--reviewer", reviewer, "--reviewer-kind", "subagent",
        "--family", family, "--verdict", "PASS", "--asset-id", asset_id,
        "--independent", "--score", "96",
        *(item for gate in gates for item in ("--gate", gate)),
    )
    assert result is not None
    return result["review_id"]


def approve(root: Path, asset_id: str, op: str) -> str:
    result = run_ops(
        root, "record-decision", "--operation-id", op,
        "--kind", "approval", "--status", "approved", "--decided-by", "test-user",
        "--asset-id", asset_id, "--text", "Aesthetic direction approved for test.",
    )
    assert result is not None
    return result["decision_id"]


def read_program(root: Path) -> dict[str, Any]:
    return json.loads((root / "visual" / "manifests" / "visual_program.json").read_text(encoding="utf-8"))


def evidence(
    root: Path,
    asset_id: str,
    *,
    category: str,
    op: str,
    verifier: str,
    role: str,
    platform: str = "cross_platform",
    source_tag: str = SOURCE_TAG,
    build_hash: str = BUILD_HASH,
    verdict: str = "PASS",
    content_origin: str = "synthetic",
    privacy_classification: str = "public_product",
    artifact: Path | None = None,
    expect: int = 0,
) -> dict[str, Any] | None:
    artifact = artifact or (root / "visual" / "reviews" / "evidence" / f"{op}.txt")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    if not artifact.exists():
        artifact.write_text(
            f"signed synthetic evidence\ncategory={category}\nrole={role}\nverifier={verifier}\n"
            f"source_tag={source_tag}\nbuild_hash={build_hash}\n",
            encoding="utf-8",
        )
    result = run_ops(
        root, "record-evidence", "--operation-id", op,
        "--asset-id", asset_id, "--category", category,
        "--source-tag", source_tag, "--build-hash", build_hash,
        "--platform", platform, "--os", "selftest-os-1", "--device", f"selftest-{platform}-device",
        "--test-suite", f"selftest-{category}-suite", "--verifier", verifier,
        "--verifier-role", role, "--credential-or-attestation", str(artifact),
        "--verdict", verdict, "--artifact-path", str(artifact), "--independent",
        "--privacy-classification", privacy_classification, "--content-origin", content_origin,
        expect=expect,
    )
    if expect:
        return None
    assert result is not None
    return result


def medical_source_from_document(
    root: Path, asset_id: str, document: Path, *, op: str, expect: int = 0,
) -> dict[str, Any] | None:
    return run_ops(
        root, "add-medical-source", "--operation-id", op,
        "--asset-id", asset_id, "--title", "Archived public clinical source",
        "--authority", "Test Clinical Authority", "--jurisdiction", "CN",
        "--population", "adult pregnancy", "--gestational-stage", "all validated stages",
        "--source-version", "2025.1", "--publication-date", "2025-01-01",
        "--source-revision-date", "2025-06-01", "--accessed-date", "2026-01-01",
        "--document-path", str(document), expect=expect,
    )


def verify_medical_fixture(
    root: Path,
    asset_id: str,
    source_id: str,
    attestation: Path,
    *,
    op: str,
    verifier: str = "Dr Test",
    verifier_kind: str = "external_specialist",
    expect: int = 0,
) -> dict[str, Any] | None:
    return run_ops(
        root, "verify-medical", "--operation-id", op,
        "--asset-id", asset_id, "--verifier", verifier, "--verifier-kind", verifier_kind,
        "--professional-role", "obstetrician", "--credential-ref", "CRED-TEST-001",
        "--source-id", source_id,
        "--scope", "visual anatomy and gestational-stage appropriateness", "--verdict", "VERIFIED",
        "--attestation-path", str(attestation), "--independent", expect=expect,
    )


def assert_slotless_medical_golden_flow(
    root: Path, asset_id: str, asset_type: str, *, prefix: str,
) -> None:
    for family in ("brand", "visual", "production", "accessibility_safety", "medical"):
        review(
            root, asset_id, family, f"OP-{prefix}-review-{family}", f"{prefix}-{family}-reviewer",
            asset_type=asset_type,
        )
    decision_id = approve(root, asset_id, f"OP-{prefix}-approval")
    source = run_ops(
        root, "add-medical-source", "--operation-id", f"OP-{prefix}-source",
        "--asset-id", asset_id, "--title", f"{asset_type} clinical source",
        "--authority", "Test Clinical Authority", "--jurisdiction", "CN",
        "--population", "adult pregnancy", "--gestational-stage", "validated range",
        "--source-version", "2025.1", "--publication-date", "2025-01-01",
        "--source-revision-date", "2025-06-01", "--accessed-date", "2026-01-01",
        "--source-url", f"https://example.test/{prefix}-clinical-source",
        "--source-checksum", hashlib.sha256(f"{prefix}-source".encode()).hexdigest(),
    )
    assert source is not None
    attestation = root / "visual" / "reviews" / "medical" / f"{prefix}-attestation.txt"
    attestation.parent.mkdir(parents=True, exist_ok=True)
    attestation.write_text(
        f"signed {asset_type} medical attestation; asset={asset_id}; source={source['medical_source_id']}\n",
        encoding="utf-8",
    )
    write_provenance(root, attestation, reference_role="medical_attestation")
    verified = verify_medical_fixture(
        root, asset_id, source["medical_source_id"], attestation,
        op=f"OP-{prefix}-medical-verify", verifier=f"Dr {prefix}",
    )
    assert verified and verified["status"] == "verified"
    promoted = run_ops(
        root, "promote-golden", "--operation-id", f"OP-{prefix}-golden",
        asset_id, "--decision-id", decision_id,
    )
    assert promoted and promoted["status"] == "aesthetic_golden" and promoted["slot"] is None
    evidence(
        root, asset_id, category="integration", op=f"OP-{prefix}-integration-evidence",
        verifier=f"{prefix}-integration-owner", role="TECH",
    )
    integrated = run_ops(
        root, "advance-evidence", "--operation-id", f"OP-{prefix}-integrated",
        asset_id, "--to", "integrated", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
    )
    assert integrated and integrated["evidence_stage"] == "integrated"


def assert_registration_filesystem_guards(root: Path) -> None:
    candidate = root / "visual" / "candidates" / "filesystem-guard.ppm"
    make_ppm(candidate, (1, 2, 3))
    if sys.platform == "win32":
        ads = Path(str(candidate) + ":yunmom-test")
        ads.write_bytes(b"forbidden alternate stream")
        run_ops(
            root, "register-asset", "--operation-id", "OP-test-register-ads",
            "--name", "ADS", "--class", "C", "--type", "prop", "--path", str(ads),
            "--creator", "test", expect=2,
        )
        ads.unlink(missing_ok=True)
    hardlink = root / "visual" / "candidates" / "filesystem-guard-hardlink.ppm"
    try:
        os.link(candidate, hardlink)
    except OSError:
        hardlink = None
    if hardlink is not None:
        run_ops(
            root, "register-asset", "--operation-id", "OP-test-register-hardlink",
            "--name", "Hardlink", "--class", "C", "--type", "prop", "--path", str(hardlink),
            "--creator", "test", expect=2,
        )
        hardlink.unlink()
    symlink = root / "visual" / "candidates" / "filesystem-guard-symlink.ppm"
    try:
        os.symlink(candidate, symlink)
    except OSError:
        symlink = None
    if symlink is not None:
        run_ops(
            root, "register-asset", "--operation-id", "OP-test-register-reparse",
            "--name", "Reparse", "--class", "C", "--type", "prop", "--path", str(symlink),
            "--creator", "test", expect=2,
        )
        symlink.unlink()


def assert_main_flow(root: Path) -> None:
    seed_tokens(root)
    initialized = run_ops(root, "init", "--operation-id", "OP-test-init-0001")
    assert initialized and initialized["status"] == "initialized"
    replay = run_ops(root, "init", "--operation-id", "OP-test-init-0001")
    assert replay and replay["idempotent_replay"] is True

    master_path = root / "visual" / "candidates" / "yunmom_master.ppm"
    make_ppm(master_path, (190, 224, 248))
    master = register(
        root, master_path, op="OP-test-register-master", name="YunMom Master",
        asset_class="S", asset_type="character",
    )
    revision = read_program(root)["revision"]
    # Simulate a process crash after canonical commit but before projections were
    # completed. Replaying the same operation repairs projections without a new revision.
    (root / "visual" / "manifests" / "asset_registry.json").write_text("{}\n", encoding="utf-8")
    replay = register(
        root, master_path, op="OP-test-register-master", name="YunMom Master",
        asset_class="S", asset_type="character",
    )
    assert replay["asset_id"] == master["asset_id"] and replay["idempotent_replay"] is True
    assert read_program(root)["revision"] == revision
    # The same idempotency key cannot authorize a different request.
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-register-master",
        "--name", "Changed request", "--class", "S", "--type", "character",
        "--path", str(master_path), "--stage", "finalist", "--creator", "generator",
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--egress-status", "prohibited",
        expect=2,
    )

    master_id = master["asset_id"]
    run_ops(
        root, "record-review", "--operation-id", "OP-test-review-empty-gates",
        "--reviewer", "empty-gate-reviewer", "--reviewer-kind", "subagent",
        "--family", "visual", "--verdict", "PASS", "--asset-id", master_id,
        "--independent", expect=2,
    )
    first_brand = review(root, master_id, "brand", "OP-test-review-brand-01", "brand-reviewer", asset_type="character")
    second_brand = review(root, master_id, "brand", "OP-test-review-brand-02", "brand-reviewer", asset_type="character")
    assert first_brand != second_brand
    review(root, master_id, "visual", "OP-test-review-visual-01", "visual-reviewer", asset_type="character")
    decision_id = approve(root, master_id, "OP-test-approve-master")
    promoted = run_ops(
        root, "promote-golden", "--operation-id", "OP-test-promote-master",
        master_id, "--decision-id", decision_id, "--slot", "yunmom_master",
    )
    assert promoted and promoted["status"] == "aesthetic_golden"
    golden = root / promoted["golden_path"]
    assert golden.is_file() and golden.name.startswith(promoted["golden_sha256"])
    canonical_asset = next(item for item in read_program(root)["assets"] if item["id"] == master_id)
    assert canonical_asset["lifecycle_stage"] == "aesthetic_golden"
    assert canonical_asset["freshness"] == "current"
    assert canonical_asset["evidence_stage"] == "aesthetic_golden"

    unverified_path = root / "visual" / "candidates" / "rights_unverified.ppm"
    make_ppm(unverified_path, (220, 220, 220))
    unverified = run_ops(
        root, "register-asset", "--operation-id", "OP-test-register-unverified-rights",
        "--name", "Unverified Rights", "--class", "S", "--type", "character",
        "--path", str(unverified_path), "--stage", "finalist", "--creator", "generator-two",
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--egress-status", "prohibited",
    )
    assert unverified is not None
    review(
        root, unverified["asset_id"], "brand", "OP-test-unverified-brand", "rights-brand",
        asset_type="character",
    )
    review(
        root, unverified["asset_id"], "visual", "OP-test-unverified-visual", "rights-visual",
        asset_type="character",
    )
    unverified_decision = approve(root, unverified["asset_id"], "OP-test-unverified-approval")
    run_ops(
        root, "promote-golden", "--operation-id", "OP-test-unverified-promote",
        unverified["asset_id"], "--decision-id", unverified_decision,
        "--slot", "yunmom_master", "--replace-slot", expect=2,
    )

    # User approval is not release evidence and cannot skip lifecycle stages.
    run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-skip-release",
        master_id, "--to", "release_signed", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
        expect=2,
    )

    child_path = root / "visual" / "candidates" / "dependent.ppm"
    make_ppm(child_path, (246, 204, 223))
    child = register(
        root, child_path, op="OP-test-register-child", name="Dependent",
        asset_class="B", asset_type="prop", stage="candidate",
        extra=("--depends-on", master_id),
    )
    replacement_path = root / "visual" / "candidates" / "yunmom_master_v2.ppm"
    make_ppm(replacement_path, (176, 216, 246))
    replacement = register(
        root, replacement_path, op="OP-test-register-master-v2", name="YunMom Master V2",
        asset_class="S", asset_type="character", extra=("--depends-on", master_id),
    )
    replacement_id = replacement["asset_id"]
    review(root, replacement_id, "brand", "OP-test-master-v2-brand", "brand-v2", asset_type="character")
    review(root, replacement_id, "visual", "OP-test-master-v2-visual", "visual-v2", asset_type="character")
    replacement_decision = approve(root, replacement_id, "OP-test-master-v2-approval")
    replacement_result = run_ops(
        root, "promote-golden", "--operation-id", "OP-test-master-v2-promote", replacement_id,
        "--decision-id", replacement_decision, "--slot", "yunmom_master", "--replace-slot",
    )
    assert replacement_result and child["asset_id"] in replacement_result["stale_asset_ids"]
    replacement_state = next(item for item in read_program(root)["assets"] if item["id"] == replacement_id)
    assert replacement_state["freshness"] == "current"  # replacement derived from old Golden is traversal barrier

    stale = run_ops(
        root, "mark-stale", "--operation-id", "OP-test-stale-contract",
        child["asset_id"], "--reason", "frozen contract changed", "--reason-code", "contract_conflict",
        "--scope", "source",
    )
    assert stale and stale["scope"] == "source" and child["asset_id"] in stale["stale_asset_ids"]
    child_state = next(item for item in read_program(root)["assets"] if item["id"] == child["asset_id"])
    assert child_state["freshness"] == "stale_contract_conflict"
    assert child_state["lifecycle_stage"] == "candidate" and len(child_state["stale_reasons"]) == 2
    assert {item["code"] for item in child_state["stale_reasons"]} == {"golden_replaced", "contract_conflict"}

    # Baby assets default to unverified and cannot become Golden from a free-form assertion.
    baby_path = root / "visual" / "candidates" / "baby.ppm"
    make_ppm(baby_path, (252, 228, 200))
    baby = register(
        root, baby_path, op="OP-test-register-baby", name="Baby 20w",
        asset_class="A", asset_type="baby",
    )
    baby_id = baby["asset_id"]
    review(root, baby_id, "brand", "OP-test-baby-brand", "baby-brand", asset_type="baby")
    review(root, baby_id, "visual", "OP-test-baby-visual", "baby-visual", asset_type="baby")
    review(root, baby_id, "medical", "OP-test-baby-medical", "baby-medical", asset_type="baby")
    baby_decision = approve(root, baby_id, "OP-test-baby-approval")
    run_ops(
        root, "promote-golden", "--operation-id", "OP-test-baby-promote-too-early",
        baby_id, "--decision-id", baby_decision, "--slot", "baby_anchor:w20", expect=2,
    )
    run_ops(
        root, "add-medical-source", "--operation-id", "OP-test-med-source-locator-only",
        "--asset-id", baby_id, "--title", "Locator is not content evidence",
        "--authority", "Test Clinical Authority", "--jurisdiction", "CN",
        "--population", "adult pregnancy", "--gestational-stage", "20 weeks",
        "--source-version", "2025.1", "--publication-date", "2025-01-01",
        "--source-revision-date", "2025-06-01", "--accessed-date", "2026-01-01",
        "--source-url", "https://example.test/clinical-source",
        "--fixed-reference", "TEST-GUIDELINE:2025.1", expect=2,
    )
    clinical_document = root / "visual" / "references" / "medical" / "clinical-source.txt"
    clinical_document.parent.mkdir(parents=True, exist_ok=True)
    clinical_document.write_text("synthetic archived public clinical guidance fixture\n", encoding="utf-8")
    medical_source_from_document(
        root, baby_id, clinical_document, op="OP-test-med-doc-no-sidecar", expect=2,
    )
    write_provenance(
        root, clinical_document, reference_role="medical_source",
        classification="health_intimate", content_origin="real_sensitive",
    )
    medical_source_from_document(
        root, baby_id, clinical_document, op="OP-test-med-doc-real-sensitive", expect=2,
    )
    write_provenance(root, clinical_document, reference_role="medical_source", content_origin="unknown")
    medical_source_from_document(
        root, baby_id, clinical_document, op="OP-test-med-doc-unknown", expect=2,
    )
    write_provenance(root, clinical_document, reference_role="medical_source", classification="unclassified")
    medical_source_from_document(
        root, baby_id, clinical_document, op="OP-test-med-doc-unclassified", expect=2,
    )
    write_provenance(
        root, clinical_document, reference_role="medical_source",
        rights_status="unverified", rights_evidence=(),
    )
    medical_source_from_document(
        root, baby_id, clinical_document, op="OP-test-med-doc-rights-unverified", expect=2,
    )
    write_provenance(
        root, clinical_document, reference_role="medical_source",
        rights_status="public_domain",
        rights_evidence=("PUBLIC-CLINICAL-SOURCE:SELFTEST-2025.1",),
    )
    source = medical_source_from_document(
        root, baby_id, clinical_document, op="OP-test-med-source",
    )
    assert source is not None
    attestation = root / "visual" / "reviews" / "medical" / "baby-attestation.txt"
    attestation.parent.mkdir(parents=True, exist_ok=True)
    attestation.write_text(
        f"signed medical attestation for {baby_id}; source={source['medical_source_id']}; "
        "scope=visual anatomy and gestational-stage appropriateness\n",
        encoding="utf-8",
    )
    write_provenance(
        root, attestation, reference_role="medical_attestation",
        classification="health_intimate", content_origin="real_sensitive",
    )
    verify_medical_fixture(
        root, baby_id, source["medical_source_id"], attestation,
        op="OP-test-med-attestation-real-sensitive", expect=2,
    )
    write_provenance(root, attestation, reference_role="medical_attestation", content_origin="unknown")
    verify_medical_fixture(
        root, baby_id, source["medical_source_id"], attestation,
        op="OP-test-med-attestation-unknown", expect=2,
    )
    write_provenance(root, attestation, reference_role="medical_attestation", classification="unclassified")
    verify_medical_fixture(
        root, baby_id, source["medical_source_id"], attestation,
        op="OP-test-med-attestation-unclassified", expect=2,
    )
    write_provenance(root, attestation, reference_role="medical_attestation")
    run_ops(
        root, "verify-medical", "--operation-id", "OP-test-med-no-independent",
        "--asset-id", baby_id, "--verifier", "Dr Test", "--verifier-kind", "human",
        "--professional-role", "obstetrician",
        "--credential-ref", "CRED-TEST-001", "--source-id", source["medical_source_id"],
        "--scope", "visual anatomy and gestational-stage appropriateness", "--verdict", "VERIFIED",
        "--attestation-path", str(attestation),
        expect=2,
    )
    run_ops(
        root, "verify-medical", "--operation-id", "OP-test-med-model-cannot-verify",
        "--asset-id", baby_id, "--verifier", "medical-custom-agent", "--verifier-kind", "custom_agent",
        "--professional-role", "clinical_reviewer", "--credential-ref", "MODEL-NO-CREDENTIAL",
        "--source-id", source["medical_source_id"],
        "--scope", "visual anatomy and gestational-stage appropriateness", "--verdict", "VERIFIED",
        "--attestation-path", str(attestation), "--independent", expect=2,
    )
    verification = run_ops(
        root, "verify-medical", "--operation-id", "OP-test-med-verified",
        "--asset-id", baby_id, "--verifier", "Dr Test", "--verifier-kind", "external_specialist",
        "--professional-role", "obstetrician",
        "--credential-ref", "CRED-TEST-001", "--source-id", source["medical_source_id"],
        "--scope", "visual anatomy and gestational-stage appropriateness", "--verdict", "VERIFIED",
        "--attestation-path", str(attestation), "--independent",
    )
    assert verification and verification["status"] == "verified"
    baby_promoted = run_ops(
        root, "promote-golden", "--operation-id", "OP-test-baby-promote",
        baby_id, "--decision-id", baby_decision, "--slot", "baby_anchor:w20",
    )
    assert baby_promoted and baby_promoted["status"] == "aesthetic_golden"

    # Production/accessibility/release evidence are hash-bound and staged separately.
    screen_path = root / "visual" / "candidates" / "home.ppm"
    make_ppm(screen_path, (242, 248, 252))
    screen = register(
        root, screen_path, op="OP-test-register-screen", name="Home Canonical",
        asset_class="S", asset_type="screen",
    )
    screen_id = screen["asset_id"]
    safety_path = root / "visual" / "candidates" / "safety.ppm"
    make_ppm(safety_path, (220, 80, 80))
    safety = register(
        root, safety_path, op="OP-test-register-safety", name="R3 Safety Card",
        asset_class="A", asset_type="safety", stage="finalist",
    )
    safety_state = next(item for item in read_program(root)["assets"] if item["id"] == safety["asset_id"])
    assert safety_state["medical_applicable"] is True
    gentle_path = root / "visual" / "candidates" / "gentle_closure.ppm"
    make_ppm(gentle_path, (232, 218, 230))
    gentle = register(
        root, gentle_path, op="OP-test-register-gentle", name="Gentle Closure",
        asset_class="A", asset_type="gentle_closure", stage="finalist",
    )
    assert_slotless_medical_golden_flow(
        root, safety["asset_id"], "safety", prefix="test-safety-slotless",
    )
    assert_slotless_medical_golden_flow(
        root, gentle["asset_id"], "gentle_closure", prefix="test-gentle-slotless",
    )
    review(root, screen_id, "brand", "OP-test-screen-brand", "screen-brand", asset_type="screen")
    review(root, screen_id, "visual", "OP-test-screen-visual", "screen-visual", asset_type="screen")
    review(root, screen_id, "production", "OP-test-screen-production", "screen-production", asset_type="screen")
    review(
        root, screen_id, "accessibility_safety", "OP-test-screen-accessibility-review",
        "screen-accessibility", asset_type="screen",
    )
    screen_decision = approve(root, screen_id, "OP-test-screen-approval")
    run_ops(
        root, "promote-golden", "--operation-id", "OP-test-screen-golden", screen_id,
        "--decision-id", screen_decision, "--slot", "home_canonical",
    )
    run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-advance-early",
        screen_id, "--to", "integrated", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
        expect=2,
    )
    unsafe_artifact = root / "visual" / "reviews" / "evidence" / "unsafe.txt"
    unsafe_artifact.parent.mkdir(parents=True, exist_ok=True)
    unsafe_artifact.write_text("must never be accepted as persistent real-sensitive evidence\n", encoding="utf-8")
    evidence(
        root, screen_id, category="integration", op="OP-test-evidence-unsafe",
        verifier="unsafe-reviewer", role="TECH", artifact=unsafe_artifact,
        content_origin="real_sensitive", privacy_classification="health_intimate", expect=2,
    )
    evidence(
        root, screen_id, category="integration", op="OP-test-evidence-unknown",
        verifier="unknown-reviewer", role="TECH", content_origin="unknown", expect=2,
    )
    evidence(
        root, screen_id, category="integration", op="OP-test-evidence-unclassified",
        verifier="unclassified-reviewer", role="TECH", privacy_classification="unclassified", expect=2,
    )
    integration = evidence(
        root, screen_id, category="integration", op="OP-test-evidence-integration",
        verifier="integration-reviewer", role="TECH",
    )
    assert integration and integration["category"] == "integration"
    run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-wrong-binding",
        screen_id, "--to", "integrated", "--source-tag", SOURCE_TAG,
        "--build-hash", "f" * 64, expect=2,
    )
    integrated = run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-integrated",
        screen_id, "--to", "integrated", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
    )
    assert integrated and integrated["evidence_stage"] == "integrated"

    # One dummy artifact and one human identity cannot satisfy the three matrix families.
    dummy = root / "visual" / "reviews" / "evidence" / "one-dummy.txt"
    dummy.write_text("one unsigned-looking dummy cannot advance matrix acceptance\n", encoding="utf-8")
    evidence(
        root, screen_id, category="production", op="OP-test-dummy-production",
        verifier="one-person", role="TECH", artifact=dummy,
    )
    evidence(
        root, screen_id, category="accessibility", op="OP-test-dummy-accessibility",
        verifier="one-person", role="QA", artifact=dummy,
    )
    evidence(
        root, screen_id, category="matrix", op="OP-test-dummy-matrix",
        verifier="one-person", role="QA", platform="android", artifact=dummy,
    )
    run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-matrix-dummy-fails",
        screen_id, "--to", "matrix_accepted", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
        expect=2,
    )

    evidence(
        root, screen_id, category="production", op="OP-test-evidence-production",
        verifier="production-specialist", role="PRODUCTION",
    )
    evidence(
        root, screen_id, category="accessibility", op="OP-test-evidence-accessibility",
        verifier="accessibility-specialist", role="ACCESSIBILITY",
    )
    evidence(
        root, screen_id, category="matrix", op="OP-test-evidence-matrix-android",
        verifier="android-matrix-owner", role="ANDROID", platform="android",
    )
    evidence(
        root, screen_id, category="matrix", op="OP-test-evidence-matrix-ios",
        verifier="ios-matrix-owner", role="IOS", platform="ios",
    )
    advanced = run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-matrix",
        screen_id, "--to", "matrix_accepted", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
    )
    assert advanced and advanced["evidence_stage"] == "matrix_accepted"
    evidence(
        root, screen_id, category="release", op="OP-test-evidence-release-po",
        verifier="po-signer", role="PO",
    )
    run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-release-one-role-fails",
        screen_id, "--to", "release_signed", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
        expect=2,
    )
    duplicate_release_dir = root / "visual" / "reviews" / "evidence" / "duplicate-release"
    duplicate_release_dir.mkdir(parents=True, exist_ok=True)
    for role in RELEASE_ROLES:
        duplicate_artifact = duplicate_release_dir / f"{role.lower()}.txt"
        duplicate_artifact.write_text("byte-identical copied signature is not an independent attestation\n", encoding="utf-8")
        evidence(
            root, screen_id, category="release", op=f"OP-test-release-duplicate-{role.lower()}",
            verifier=f"duplicate-{role.lower()}-signer", role=role, artifact=duplicate_artifact,
        )
    run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-release-same-hash-fails",
        screen_id, "--to", "release_signed", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
        expect=2,
    )
    for role in RELEASE_ROLES:
        evidence(
            root, screen_id, category="release", op=f"OP-test-evidence-release-final-{role.lower()}",
            verifier=f"{role.lower()}-signer", role=role,
        )
    production = run_ops(
        root, "advance-evidence", "--operation-id", "OP-test-screen-release-signed",
        screen_id, "--to", "release_signed", "--source-tag", SOURCE_TAG, "--build-hash", BUILD_HASH,
    )
    assert production and production["evidence_stage"] == "release_signed"
    screen_state = next(item for item in read_program(root)["assets"] if item["id"] == screen_id)
    assert screen_state["lifecycle_stage"] == "aesthetic_golden"
    assert screen_state["evidence_binding"]["source_tag"] == SOURCE_TAG
    assert screen_state["evidence_binding"]["build_hash"] == BUILD_HASH
    projected_assets = json.loads(
        (root / "visual" / "manifests" / "asset_registry.json").read_text(encoding="utf-8")
    )["assets"]
    projected_screen = next(item for item in projected_assets if item["id"] == screen_id)
    assert projected_screen["evidence_binding"] == screen_state["evidence_binding"]
    assert projected_screen["rights"]["status"] == "owned"

    # Path containment is fail-closed.
    assert_registration_filesystem_guards(root)
    outside = root.parent / "outside.ppm"
    make_ppm(outside, (0, 0, 0))
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-path-escape",
        "--name", "Escape", "--class", "C", "--type", "prop", "--path", str(outside),
        "--creator", "test", expect=2,
    )
    sensitive = root / "visual" / "candidates" / "real_sensitive.ppm"
    make_ppm(sensitive, (12, 12, 12))
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-real-sensitive-reject",
        "--name", "Real sensitive", "--class", "C", "--type", "illustration",
        "--path", str(sensitive), "--creator", "test",
        "--privacy-classification", "health_intimate", "--content-origin", "real_sensitive",
        "--egress-status", "confirmed_per_send", "--egress-receipt-ref", "RCT-TEST",
        expect=2,
    )
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-unknown-privacy-reject",
        "--name", "Unknown", "--class", "C", "--type", "illustration",
        "--path", str(sensitive), "--creator", "test", expect=2,
    )
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-egress-receipt-required",
        "--name", "Missing receipt", "--class", "C", "--type", "illustration",
        "--path", str(sensitive), "--creator", "test",
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--egress-status", "confirmed_per_send",
        expect=2,
    )

    prompt = root / "visual" / "prompts" / "owned_prompt.md"
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text("Create an original, non-medical YunMom test prop.\n", encoding="utf-8")
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-prompt-sidecar-required",
        "--name", "Prompt without provenance", "--class", "C", "--type", "prop",
        "--path", str(sensitive), "--creator", "test", "--prompt-path", str(prompt),
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--rights-status", "owned", "--commercial-use-allowed",
        "--derivative-use-allowed", "--rights-evidence-ref", "RIGHTS-SELFTEST-OWNED", expect=2,
    )
    write_provenance(root, prompt)
    prompted_path = root / "visual" / "candidates" / "prompted.ppm"
    make_ppm(prompted_path, (88, 99, 111))
    prompted = register(
        root, prompted_path, op="OP-test-prompt-provenance-positive", name="Prompted prop",
        asset_class="C", asset_type="prop", stage="candidate", extra=("--prompt-path", str(prompt)),
    )
    assert prompted["status"] == "registered"

    local_reference = root / "visual" / "references" / "test-reference.txt"
    local_reference.parent.mkdir(parents=True, exist_ok=True)
    local_reference.write_text("synthetic local reference\n", encoding="utf-8")
    reference_asset = root / "visual" / "candidates" / "reference_asset.ppm"
    make_ppm(reference_asset, (90, 100, 110))
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-reference-sidecar-required",
        "--name", "Reference without provenance", "--class", "C", "--type", "prop",
        "--path", str(reference_asset), "--creator", "test", "--reference", str(local_reference),
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--rights-status", "owned", "--commercial-use-allowed",
        "--derivative-use-allowed", "--rights-evidence-ref", "RIGHTS-SELFTEST-OWNED", expect=2,
    )
    write_provenance(root, local_reference)
    referenced = register(
        root, reference_asset, op="OP-test-reference-provenance-positive", name="Referenced prop",
        asset_class="C", asset_type="prop", stage="candidate",
        extra=("--reference", str(local_reference)),
    )
    assert referenced["status"] == "registered"
    remote_path = root / "visual" / "candidates" / "remote_reference.ppm"
    make_ppm(remote_path, (91, 101, 111))
    run_ops(
        root, "register-asset", "--operation-id", "OP-test-remote-reference-rejected",
        "--name", "Remote reference", "--class", "C", "--type", "prop",
        "--path", str(remote_path), "--creator", "test", "--reference", "https://example.test/image.png",
        "--privacy-classification", "public_product", "--content-origin", "synthetic",
        "--allow-persistent-evidence", "--rights-status", "owned", "--commercial-use-allowed",
        "--derivative-use-allowed", "--rights-evidence-ref", "RIGHTS-SELFTEST-OWNED", expect=2,
    )

    # Canonical schema and review hash/version bindings fail closed on tamper.
    canonical_path = root / "visual" / "manifests" / "visual_program.json"
    untampered = canonical_path.read_text(encoding="utf-8")
    tampered = json.loads(untampered)
    tampered["assets"][0]["unexpected"] = True
    canonical_path.write_text(json.dumps(tampered), encoding="utf-8")
    schema_invalid = run_ops(root, "validate", "--no-fail")
    assert schema_invalid and schema_invalid["status"] == "INVALID"
    canonical_path.write_text(untampered, encoding="utf-8")
    tampered = json.loads(untampered)
    tampered["reviews"][0]["asset_sha256"] = "0" * 64
    canonical_path.write_text(json.dumps(tampered), encoding="utf-8")
    binding_invalid = run_ops(root, "validate", "--no-fail")
    assert binding_invalid and binding_invalid["status"] == "INVALID"
    canonical_path.write_text(untampered, encoding="utf-8")
    evidence_record = read_program(root)["evidence_records"][0]
    evidence_artifact = root / evidence_record["artifact_paths"][0]
    original_evidence = evidence_artifact.read_bytes()
    evidence_artifact.write_bytes(original_evidence + b"tampered\n")
    artifact_invalid = run_ops(root, "validate", "--no-fail")
    assert artifact_invalid and artifact_invalid["status"] == "INVALID"
    evidence_artifact.write_bytes(original_evidence)
    medical_record = read_program(root)["medical_verifications"][0]
    medical_artifact = root / medical_record["attestation_path"]
    original_attestation = medical_artifact.read_bytes()
    medical_artifact.write_bytes(original_attestation + b"tampered\n")
    medical_invalid = run_ops(root, "validate", "--no-fail")
    assert medical_invalid and medical_invalid["status"] == "INVALID"
    medical_artifact.write_bytes(original_attestation)
    reference_sidecar = local_reference.with_suffix(".provenance.json")
    original_sidecar = reference_sidecar.read_text(encoding="utf-8")
    sidecar_document = json.loads(original_sidecar)
    sidecar_document["sha256"] = "0" * 64
    reference_sidecar.write_text(json.dumps(sidecar_document), encoding="utf-8")
    provenance_invalid = run_ops(root, "validate", "--no-fail")
    assert provenance_invalid and provenance_invalid["status"] == "INVALID"
    reference_sidecar.write_text(original_sidecar, encoding="utf-8")

    # Projection drift is detected, and read-only validation does not repair it.
    projected = root / "visual" / "state" / "DESIGN_STATE.json"
    projected.write_text("{}\n", encoding="utf-8")
    invalid = run_ops(root, "validate", "--no-fail")
    assert invalid and invalid["status"] == "INVALID" and "{}\n" == projected.read_text(encoding="utf-8")
    repaired = run_ops(root, "repair-projections")
    assert repaired and repaired["status"] == "repaired"
    valid = run_ops(root, "validate")
    assert valid and valid["status"] == "OK"


def assert_migration(root: Path) -> None:
    seed_tokens(root)
    legacy_asset_path = root / "visual" / "candidates" / "legacy_master.ppm"
    make_ppm(legacy_asset_path, (120, 160, 200))
    legacy_asset_id = "VA-20260101-abcdef12"
    legacy_hash = hashlib.sha256(legacy_asset_path.read_bytes()).hexdigest()
    state = root / "visual" / "state" / "DESIGN_STATE.json"
    assets = root / "visual" / "manifests" / "asset_registry.json"
    decisions = root / "visual" / "decisions" / "decision_registry.json"
    reviews = root / "visual" / "reviews" / "review_registry.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    assets.parent.mkdir(parents=True, exist_ok=True)
    decisions.parent.mkdir(parents=True, exist_ok=True)
    reviews.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({
        "schema_version": 3, "visual_version": "3.0.0",
        "contract_version": "YunMom_Engineering_Contracts_V1.0.0",
        "current_gate": "G1_YUNMOM_MASTER", "golden": {"yunmom_master": legacy_asset_id},
        "release_evidence_status": "not_approved",
    }), encoding="utf-8")
    assets.write_text(json.dumps({"schema_version": 2, "revision": 0, "assets": [{
        "id": legacy_asset_id, "name": "Legacy Master", "class": "S", "type": "character",
        "status": "approved", "lifecycle_stage": "approved", "version": 1,
        "path": legacy_asset_path.relative_to(root).as_posix(), "sha256": legacy_hash,
        "parents": [], "references": [], "depends_on": [], "tool": "legacy-generator",
        "model": "legacy-model", "prompt_path": None, "medical_status": "not_applicable",
        "privacy": {
            "classification": "public_product", "content_origin": "synthetic",
            "persistent_evidence_allowed": True,
            "external_egress": {"status": "prohibited", "receipt_ref": None},
            "cleanup_scope": ["source_asset"],
        },
        "user_decision_id": "D-0002", "approved_at": "2026-01-01T00:00:00+00:00",
        "created_at": "2026-01-01T00:00:00+00:00", "updated_at": "2026-01-01T00:00:00+00:00",
        "notes": [],
    }]}), encoding="utf-8")
    decisions.write_text(json.dumps({
        "schema_version": 1, "revision": 1, "decisions": [{
            "id": "D-0001", "occurred_at": "2026-01-01T00:00:00+00:00", "kind": "baseline",
            "status": "approved", "asset_ids": [], "text": "Legacy baseline", "preserve": [], "change": [],
        }, {
            "id": "D-0002", "occurred_at": "2026-01-01T00:00:00+00:00", "kind": "approval",
            "status": "approved", "decided_by": "legacy-user", "asset_ids": [legacy_asset_id],
            "text": "Legacy aesthetic approval", "preserve": [], "change": [],
        }],
    }), encoding="utf-8")
    reviews.write_text(json.dumps({"schema_version": 1, "revision": 0, "reviews": []}), encoding="utf-8")
    run_ops(root, "init", "--operation-id", "OP-test-legacy-init-refusal", expect=2)
    migrated = run_ops(root, "migrate", "--operation-id", "OP-test-migrate-0001")
    assert migrated and migrated["status"] == "migrated"
    migrated_asset = next(item for item in read_program(root)["assets"] if item["id"] == legacy_asset_id)
    assert migrated_asset["rights"]["status"] == "unverified"
    assert migrated_asset["evidence_binding"] is None
    assert migrated_asset["lifecycle_stage"] == "finalist" and migrated_asset["golden"] is None
    backup = root / migrated["backup_path"]
    backup_manifest = backup / "BACKUP_MANIFEST.json"
    assert backup_manifest.is_file()
    migrated_program = read_program(root)
    assert migrated_program["migration_history"][0]["backup_manifest_sha256"] == hashlib.sha256(
        backup_manifest.read_bytes()
    ).hexdigest()
    replay = run_ops(root, "migrate", "--operation-id", "OP-test-migrate-0001")
    assert replay and replay["idempotent_replay"] is True
    # Reproduce the historical inventory-map hash bug and require a narrow,
    # explicit, journaled repair rather than a silent canonical edit.
    canonical = root / "visual" / "manifests" / "visual_program.json"
    document = json.loads(canonical.read_text(encoding="utf-8"))
    manifest_doc = json.loads(backup_manifest.read_text(encoding="utf-8"))
    legacy_files = {entry["path"]: entry["sha256"] for entry in manifest_doc["entries"]}
    backup_manifest.write_text(json.dumps({
        "created_at": manifest_doc["created_at"], "files": legacy_files,
    }, indent=2) + "\n", encoding="utf-8")
    legacy_payload = json.dumps(
        legacy_files, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    document["migration_history"][0]["backup_manifest_sha256"] = hashlib.sha256(legacy_payload).hexdigest()
    canonical.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    invalid = run_ops(root, "validate", "--no-fail")
    assert invalid and invalid["status"] == "INVALID"
    repaired = run_ops(
        root, "repair-migration-hashes", "--operation-id", "OP-test-repair-migration-hashes",
    )
    assert repaired and repaired["status"] == "repaired"
    replay_repair = run_ops(
        root, "repair-migration-hashes", "--operation-id", "OP-test-repair-migration-hashes",
    )
    assert replay_repair and replay_repair["idempotent_replay"] is True
    baseline_program = canonical.read_text(encoding="utf-8")
    baseline_manifest = backup_manifest.read_bytes()
    legacy_manifest = json.loads(baseline_manifest.decode("utf-8"))
    first_backup_rel = next(iter(legacy_manifest["files"]))
    first_backup_file = backup / first_backup_rel
    first_backup_bytes = first_backup_file.read_bytes()
    first_backup_file.write_bytes(first_backup_bytes + b"tampered\n")
    assert run_ops(root, "validate", "--no-fail")["status"] == "INVALID"  # type: ignore[index]
    first_backup_file.write_bytes(first_backup_bytes)
    extra = backup / "visual" / "unlisted-extra.txt"
    extra.parent.mkdir(parents=True, exist_ok=True)
    extra.write_text("unlisted\n", encoding="utf-8")
    assert run_ops(root, "validate", "--no-fail")["status"] == "INVALID"  # type: ignore[index]
    extra.unlink()
    invalid_manifest = dict(legacy_manifest)
    invalid_files = dict(legacy_manifest["files"])
    digest = invalid_files.pop(first_backup_rel)
    invalid_files["../escape"] = digest
    invalid_manifest["files"] = invalid_files
    backup_manifest.write_text(json.dumps(invalid_manifest, indent=2) + "\n", encoding="utf-8")
    invalid_program = json.loads(baseline_program)
    invalid_program["migration_history"][0]["backup_manifest_sha256"] = hashlib.sha256(
        backup_manifest.read_bytes()
    ).hexdigest()
    canonical.write_text(json.dumps(invalid_program, indent=2) + "\n", encoding="utf-8")
    assert run_ops(root, "validate", "--no-fail")["status"] == "INVALID"  # type: ignore[index]
    backup_manifest.write_bytes(baseline_manifest)
    canonical.write_text(baseline_program, encoding="utf-8")
    assert run_ops(root, "validate")["status"] == "OK"  # type: ignore[index]


def assert_contact_sheet(root: Path) -> str:
    if importlib.util.find_spec("PIL") is None:
        completed = invoke(
            CONTACT, str(root / "visual" / "candidates" / "yunmom_master_v2.ppm"),
            "--project-root", str(root), "--out", str(root / "visual" / "reviews" / "sheet.png"),
            expect=2,
        )
        assert "Pillow 12.2.0 is required" in completed.stderr
        return "contact sheet skipped (Pillow unavailable; friendly failure verified)"
    first = root / "visual" / "candidates" / "yunmom_master_v2.ppm"
    second = root / "visual" / "candidates" / "home.ppm"
    output = root / "visual" / "reviews" / "sheet.png"
    invoke(
        CONTACT, str(first), str(second), "--project-root", str(root),
        "--out", str(output), "--columns", "2", "--cell-width", "128", "--cell-height", "96",
    )
    assert output.is_file()
    if sys.platform == "win32":
        input_ads = Path(str(first) + ":contact-test")
        input_ads.write_bytes(b"forbidden stream")
        invoke(
            CONTACT, str(first), "--project-root", str(root),
            "--out", str(root / "visual" / "reviews" / "ads-input.png"), expect=2,
        )
        input_ads.unlink(missing_ok=True)
        invoke(
            CONTACT, str(first), "--project-root", str(root),
            "--out", str(root / "visual" / "reviews" / "ads-output.png:stream"), expect=2,
        )
        fake_font = root / "visual" / "reviews" / "fake-font.ttf"
        fake_font.write_bytes(b"not a real font")
        font_ads = Path(str(fake_font) + ":font-stream")
        font_ads.write_bytes(b"forbidden font stream")
        invoke(
            CONTACT, str(first), "--project-root", str(root),
            "--out", str(root / "visual" / "reviews" / "ads-font.png"),
            "--font", str(font_ads), expect=2,
        )
        font_ads.unlink(missing_ok=True)
        fake_font.unlink()
    hardlink = root / "visual" / "candidates" / "contact-hardlink.ppm"
    try:
        os.link(first, hardlink)
    except OSError:
        hardlink = None
    if hardlink is not None:
        invoke(
            CONTACT, str(first), "--project-root", str(root),
            "--out", str(root / "visual" / "reviews" / "hardlink-input.png"), expect=2,
        )
        hardlink.unlink()
    symlink = root / "visual" / "candidates" / "contact-symlink.ppm"
    try:
        os.symlink(first, symlink)
    except OSError:
        symlink = None
    if symlink is not None:
        invoke(
            CONTACT, str(symlink), "--project-root", str(root),
            "--out", str(root / "visual" / "reviews" / "reparse-input.png"), expect=2,
        )
        symlink.unlink()
    invoke(
        CONTACT, str(first), str(second), "--project-root", str(root),
        "--out", str(output), expect=2,
    )
    invoke(
        CONTACT, str(first), str(first), "--project-root", str(root),
        "--out", str(root / "visual" / "reviews" / "duplicate.png"), expect=2,
    )
    invoke(
        CONTACT, str(first), "--project-root", str(root), "--out", str(first), expect=2,
    )
    invoke(
        CONTACT, str(first), "--project-root", str(root),
        "--out", str(root / "outside-sheet.png"), expect=2,
    )
    return "contact sheet positive/no-overwrite/alias/path tests passed"


def assert_manifest_verifier(root: Path) -> None:
    immutable = root / ".agents" / "immutable.txt"
    seed = root / "visual" / "seed.txt"
    runtime = root / "runtime-state" / "runtime.txt"
    (root / ".codex").mkdir(parents=True)
    immutable.parent.mkdir(parents=True)
    seed.parent.mkdir(parents=True)
    runtime.parent.mkdir(parents=True)
    immutable.write_text("immutable\n", encoding="utf-8")
    seed.write_text("seed\n", encoding="utf-8")
    runtime.write_text("runtime changed\n", encoding="utf-8")

    def record(path: Path, role: str, *, wrong: bool = False) -> dict[str, Any]:
        data = path.read_bytes()
        return {
            "bytes": len(data) + (1 if wrong else 0),
            "sha256": hashlib.sha256(data).hexdigest(),
            "role": role,
        }

    manifest = {
        "schema_version": 2,
        "package_version": "3.0.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "algorithm": "sha256",
        "inventory": {
            "immutable_roots": [".agents", ".codex"],
            "immutable_files": [],
            "seed_roots": ["visual"],
            "seed_files": [],
            "runtime_roots": ["runtime-state"],
            "runtime_files": [],
        },
        "files": {
            ".agents/immutable.txt": record(immutable, "immutable"),
            "visual/seed.txt": record(seed, "seed", wrong=True),
            "runtime-state/runtime.txt": {"bytes": 0, "sha256": "0" * 64, "role": "runtime"},
        },
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    default = invoke(MANIFEST_VERIFY, "--package-root", str(root))
    assert json.loads(default.stdout)["status"] == "OK"
    seeds = invoke(MANIFEST_VERIFY, "--package-root", str(root), "--include-seeds", expect=2)
    parsed = json.loads(seeds.stdout)
    assert parsed["status"] == "INVALID" and any(item["code"] == "bytes_mismatch" for item in parsed["errors"])


def main() -> int:
    notes: list[str] = []
    with tempfile.TemporaryDirectory(prefix="yunmom-visual-selftest-") as temp:
        base = Path(temp)
        main_root = base / "main"
        main_root.mkdir()
        assert_main_flow(main_root)
        notes.append(assert_contact_sheet(main_root))
        migration_root = base / "migration"
        migration_root.mkdir()
        assert_migration(migration_root)
        manifest_root = base / "manifest"
        manifest_root.mkdir()
        assert_manifest_verifier(manifest_root)
    print("OK: YunMom visual tooling self-test passed")
    for note in notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
