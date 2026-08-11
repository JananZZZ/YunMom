#!/usr/bin/env python3
"""Fail-closed, read-only verifier for a YunMom Art Director MANIFEST v2.

Immutable and seed inventories must be complete: an undeclared file beneath a
managed root is an error.  Runtime inventory is explicitly declared but never
hashed or enumerated, so installed projects can accumulate governed runtime
state without invalidating the distributable package.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Iterator


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
ROLES = {"immutable", "seed", "runtime"}
INVENTORY_KEYS = {
    "immutable_roots", "immutable_files",
    "seed_roots", "seed_files",
    "runtime_roots", "runtime_files",
}
MINIMUM_ROOTS = {"immutable": {".agents", ".codex"}, "seed": {"visual"}}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def error(
    code: str,
    message: str,
    *,
    path: str | None = None,
    expected: Any = None,
    actual: Any = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"code": code, "message": message}
    if path is not None:
        item["path"] = path
    if expected is not None:
        item["expected"] = expected
    if actual is not None:
        item["actual"] = actual
    return item


def find_package_root(explicit: str | None) -> Path:
    if explicit:
        lexical = Path(explicit).expanduser().absolute()
        if is_reparse(lexical):
            raise ValueError("package root may not be a symlink/reparse point")
        root = lexical.resolve()
        if not root.is_dir():
            raise ValueError(f"package root is not a directory: {root}")
        return root
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / "MANIFEST.json").is_file() and (
            (candidate / ".agents" / "skills" / "yunmom-art-director" / "SKILL.md").is_file()
        ):
            return candidate
    raise ValueError("cannot locate package root; pass --package-root")


def canonical_rel(value: Any) -> tuple[str | None, dict[str, Any] | None]:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return None, error(
            "invalid_path", "path must be a non-empty canonical POSIX relative path", path=str(value)
        )
    pure = PurePosixPath(value)
    if (
        pure.is_absolute()
        or value == "."
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.as_posix() != value
    ):
        return None, error(
            "invalid_path", "path is absolute, traversing, root-wide, or non-canonical", path=value
        )
    return value, None


def lexical_path(root: Path, rel: str) -> Path:
    return root.joinpath(*PurePosixPath(rel).parts)


def is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except OSError:
        return False
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & reparse_flag)


def named_streams(path: Path) -> list[str]:
    """Return non-default NTFS streams; unsupported filesystems have none."""
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
        if code in {2, 38, 50, 87}:  # absent, EOF, unsupported, invalid-on-non-NTFS
            return []
        raise OSError(code, f"cannot enumerate alternate data streams for {path}")
    found: list[str] = []
    try:
        while True:
            name = str(data.stream_name)
            if name and name != "::$DATA":
                found.append(name)
            if not next_stream(handle, ctypes.byref(data)):
                code = ctypes.get_last_error()
                if code == 38:
                    break
                raise OSError(code, f"cannot continue alternate data stream scan for {path}")
    finally:
        close(handle)
    return found


def reject_hidden_aliases(path: Path, *, regular_file: bool) -> None:
    info = path.stat()
    if regular_file and getattr(info, "st_nlink", 1) != 1:
        raise RuntimeError(f"hard-linked managed file is forbidden: {path}")
    streams = named_streams(path)
    if streams:
        raise RuntimeError(f"alternate data streams are forbidden for {path}: {streams}")


def alias_in_chain(root: Path, target: Path) -> Path | None:
    """Return the first symlink/reparse component at or beneath root."""
    try:
        relative = target.relative_to(root)
    except ValueError:
        return target
    current = root
    if is_reparse(current):
        return current
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if is_reparse(current):
                return current
    return None


def safe_path(root: Path, rel: str) -> tuple[Path | None, dict[str, Any] | None]:
    canonical, path_error = canonical_rel(rel)
    if path_error:
        return None, path_error
    assert canonical is not None
    target = lexical_path(root, canonical)
    alias = alias_in_chain(root, target)
    if alias is not None:
        return None, error(
            "alias_or_reparse", "symlink/reparse points are forbidden in managed package paths", path=canonical
        )
    try:
        resolved = target.resolve(strict=False)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        return None, error("path_escape", f"path cannot be safely resolved beneath package root: {exc}", path=canonical)
    return target, None


def parse_zoned_iso(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or not value.strip()
        or not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", value)
    ):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def iter_tree(root: Path, rel_root: str) -> Iterator[str]:
    """Yield regular-file paths without following aliases; reject aliases."""
    start = lexical_path(root, rel_root)
    pending = [start]
    while pending:
        directory = pending.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name.casefold(), reverse=True)
        except OSError as exc:
            raise RuntimeError(f"cannot scan inventory root {directory}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            rel = path.relative_to(root).as_posix()
            if entry.is_symlink() or is_reparse(path):
                raise RuntimeError(f"symlink/reparse entry is forbidden: {rel}")
            try:
                if entry.is_dir(follow_symlinks=False):
                    reject_hidden_aliases(path, regular_file=False)
                    pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    reject_hidden_aliases(path, regular_file=True)
                    yield rel
                else:
                    raise RuntimeError(f"non-regular inventory entry is forbidden: {rel}")
            except OSError as exc:
                raise RuntimeError(f"cannot classify inventory entry {rel}: {exc}") from exc


def under(rel: str, root_rel: str) -> bool:
    pure = PurePosixPath(rel)
    base = PurePosixPath(root_rel)
    return pure == base or base in pure.parents


def validate_inventory(
    root: Path,
    raw: Any,
    errors: list[dict[str, Any]],
) -> dict[str, dict[str, list[str]]]:
    result = {role: {"roots": [], "files": []} for role in ROLES}
    if not isinstance(raw, dict):
        errors.append(error("inventory_wrong_type", "inventory must be an object"))
        return result
    missing = sorted(INVENTORY_KEYS - set(raw))
    unknown = sorted(set(raw) - INVENTORY_KEYS)
    if missing:
        errors.append(error("inventory_missing_keys", "inventory keys are missing", expected=missing))
    if unknown:
        errors.append(error("inventory_unknown_keys", "unknown inventory keys are forbidden", actual=unknown))

    owner_by_unit: dict[str, tuple[str, str]] = {}
    for role in sorted(ROLES):
        for kind in ("roots", "files"):
            key = f"{role}_{kind}"
            values = raw.get(key, [])
            if not isinstance(values, list):
                errors.append(error("inventory_list_required", f"{key} must be an array", path=key))
                continue
            seen: set[str] = set()
            for value in values:
                rel, path_error = canonical_rel(value)
                if path_error:
                    path_error["path"] = f"{key}:{value}"
                    errors.append(path_error)
                    continue
                assert rel is not None
                if len(PurePosixPath(rel).parts) != 1:
                    errors.append(error(
                        "inventory_not_top_level",
                        "inventory roots/files must be direct package-root entries so the package surface is closed",
                        path=rel,
                    ))
                    continue
                if rel == "MANIFEST.json":
                    errors.append(error("manifest_self_inventory", "MANIFEST.json must stay outside its own inventory", path=key))
                    continue
                if rel in seen:
                    errors.append(error("duplicate_inventory_path", "inventory path is duplicated", path=rel))
                    continue
                seen.add(rel)
                identity = os.path.normcase(str(lexical_path(root, rel).absolute()))
                prior = owner_by_unit.get(identity)
                if prior is not None:
                    errors.append(error(
                        "inventory_role_collision", "inventory path belongs to multiple groups or aliases another path",
                        path=rel, actual=[f"{prior[0]}:{prior[1]}", key],
                    ))
                    continue
                owner_by_unit[identity] = (key, rel)
                target, safe_error = safe_path(root, rel)
                if safe_error:
                    errors.append(safe_error)
                    continue
                assert target is not None
                if role != "runtime":
                    if kind == "roots" and not target.is_dir():
                        errors.append(error("inventory_root_missing", "managed inventory root must exist", path=rel))
                    if kind == "files" and not target.is_file():
                        errors.append(error("inventory_file_missing", "managed inventory file must exist", path=rel))
                elif target.exists():
                    if kind == "roots" and not target.is_dir():
                        errors.append(error("runtime_root_type", "runtime root exists but is not a directory", path=rel))
                    if kind == "files" and not target.is_file():
                        errors.append(error("runtime_file_type", "runtime file exists but is not a regular file", path=rel))
                result[role][kind].append(rel)

    # No root may contain another root or an explicit file; such overlap makes
    # role ownership and completeness ambiguous.
    units: list[tuple[str, str, str]] = []
    for role in sorted(ROLES):
        units.extend((role, "root", rel) for rel in result[role]["roots"])
        units.extend((role, "file", rel) for rel in result[role]["files"])
    for index, (left_role, left_kind, left) in enumerate(units):
        for right_role, right_kind, right in units[index + 1:]:
            if left_kind == "root" and under(right, left):
                errors.append(error("inventory_overlap", "inventory units overlap", path=right, expected=f"outside {left_role}:{left}"))
            elif right_kind == "root" and under(left, right):
                errors.append(error("inventory_overlap", "inventory units overlap", path=left, expected=f"outside {right_role}:{right}"))

    for role, required in MINIMUM_ROOTS.items():
        missing_roots = sorted(required - set(result[role]["roots"]))
        if missing_roots:
            errors.append(error(
                "minimum_inventory_roots", f"{role} inventory omits fixed package roots", expected=missing_roots
            ))
    return result


def validate_package_surface(
    root: Path,
    inventory: dict[str, dict[str, list[str]]],
    errors: list[dict[str, Any]],
) -> None:
    allowed = {"MANIFEST.json"}
    for role in ROLES:
        allowed.update(inventory[role]["roots"])
        allowed.update(inventory[role]["files"])
    try:
        entries = sorted(os.scandir(root), key=lambda item: item.name.casefold())
    except OSError as exc:
        errors.append(error("package_scan_failed", f"cannot scan package root: {exc}"))
        return
    for entry in entries:
        path = Path(entry.path)
        if entry.is_symlink() or is_reparse(path):
            errors.append(error("package_alias", "top-level symlink/reparse entry is forbidden", path=entry.name))
            continue
        try:
            reject_hidden_aliases(path, regular_file=entry.is_file(follow_symlinks=False))
        except (OSError, RuntimeError) as exc:
            errors.append(error("hidden_alias", str(exc), path=entry.name))
            continue
        if entry.name not in allowed:
            errors.append(error(
                "unlisted_package_entry",
                "top-level package entry is absent from immutable/seed/runtime inventory",
                path=entry.name,
            ))


def verify(root: Path, include_seeds: bool) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    manifest_path = root / "MANIFEST.json"
    if is_reparse(root):
        errors.append(error("package_root_alias", "package root itself may not be a symlink/reparse point"))
    if is_reparse(manifest_path):
        errors.append(error("manifest_alias", "MANIFEST.json may not be a symlink/reparse point", path="MANIFEST.json"))
    elif manifest_path.exists():
        try:
            reject_hidden_aliases(manifest_path, regular_file=True)
        except (OSError, RuntimeError) as exc:
            errors.append(error("manifest_hidden_alias", str(exc), path="MANIFEST.json"))
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"status": "INVALID", "package_root": str(root), "checked": 0, "errors": [
            error("manifest_missing", "MANIFEST.json does not exist", path="MANIFEST.json")
        ]}
    except OSError as exc:
        return {"status": "INVALID", "package_root": str(root), "checked": 0, "errors": [
            error("manifest_unreadable", str(exc), path="MANIFEST.json")
        ]}
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {"status": "INVALID", "package_root": str(root), "checked": 0, "errors": [
            error("manifest_invalid_json", str(exc), path="MANIFEST.json")
        ]}
    if not isinstance(manifest, dict):
        return {"status": "INVALID", "package_root": str(root), "checked": 0, "errors": [
            error("manifest_wrong_type", "manifest root must be an object", expected="object", actual=type(manifest).__name__)
        ]}

    allowed_top = {"schema_version", "package_version", "generated_at", "algorithm", "inventory", "files"}
    required_top = allowed_top
    missing = sorted(required_top - set(manifest))
    unknown = sorted(set(manifest) - allowed_top)
    if missing:
        errors.append(error("manifest_missing_keys", "required top-level keys are missing", expected=missing))
    if unknown:
        errors.append(error("manifest_unknown_keys", "unknown top-level keys are not allowed", actual=unknown))
    if manifest.get("schema_version") != 2:
        errors.append(error("schema_version", "only MANIFEST schema v2 is supported", expected=2, actual=manifest.get("schema_version")))
    if not isinstance(manifest.get("package_version"), str) or not SEMVER_RE.fullmatch(manifest.get("package_version", "")):
        errors.append(error("package_version", "package_version must be Semantic Versioning", actual=manifest.get("package_version")))
    if not parse_zoned_iso(manifest.get("generated_at")):
        errors.append(error("generated_at", "generated_at must be an ISO-8601 timestamp with timezone", actual=manifest.get("generated_at")))
    if manifest.get("algorithm") != "sha256":
        errors.append(error("algorithm", "algorithm must be exactly 'sha256'", expected="sha256", actual=manifest.get("algorithm")))

    inventory = validate_inventory(root, manifest.get("inventory"), errors)
    validate_package_surface(root, inventory, errors)
    files = manifest.get("files")
    if not isinstance(files, dict):
        errors.append(error("files_wrong_type", "files must be an object keyed by canonical path", expected="object", actual=type(files).__name__))
        files = {}

    checked = 0
    listed_by_role: dict[str, set[str]] = {role: set() for role in ROLES}
    selected_roles = {"immutable", "seed"} if include_seeds else {"immutable"}
    record_identities: dict[str, str] = {}
    for rel in sorted(files):
        record = files[rel]
        target, path_error = safe_path(root, rel)
        if path_error:
            errors.append(path_error)
            continue
        if rel == "MANIFEST.json":
            errors.append(error("manifest_self_record", "MANIFEST.json must not hash itself", path=rel))
            continue
        assert target is not None
        identity = os.path.normcase(str(target.absolute()))
        if identity in record_identities:
            errors.append(error(
                "record_path_alias", "multiple manifest records address the same filesystem path",
                path=rel, actual=record_identities[identity],
            ))
            continue
        record_identities[identity] = rel
        if not isinstance(record, dict):
            errors.append(error("record_wrong_type", "file record must be an object", path=rel, expected="object", actual=type(record).__name__))
            continue
        required = {"bytes", "sha256", "role"}
        record_missing = sorted(required - set(record))
        record_unknown = sorted(set(record) - required)
        if record_missing:
            errors.append(error("record_missing_keys", "file record is incomplete", path=rel, expected=record_missing))
        if record_unknown:
            errors.append(error("record_unknown_keys", "unknown file record keys are not allowed", path=rel, actual=record_unknown))
        role = record.get("role")
        if role not in ROLES:
            errors.append(error("invalid_role", "role must be immutable, seed, or runtime", path=rel, actual=role))
            continue
        listed_by_role[role].add(rel)
        covered = rel in inventory[role]["files"] or any(under(rel, base) for base in inventory[role]["roots"])
        if not covered:
            errors.append(error("record_outside_inventory", "file record is not covered by matching inventory", path=rel, actual=role))
        expected_bytes = record.get("bytes")
        expected_hash = record.get("sha256")
        if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool) or expected_bytes < 0:
            errors.append(error("invalid_bytes", "bytes must be a non-negative integer", path=rel, actual=expected_bytes))
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
            errors.append(error("invalid_sha256", "sha256 must be 64 lowercase hex characters", path=rel, actual=expected_hash))
        if role not in selected_roles:
            continue
        checked += 1
        if not target.is_file():
            errors.append(error("file_missing", "manifest-selected file does not exist", path=rel))
            continue
        try:
            actual_bytes = target.stat().st_size
            actual_hash = sha256_file(target)
        except OSError as exc:
            errors.append(error("file_unreadable", str(exc), path=rel))
            continue
        if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) and expected_bytes >= 0 and actual_bytes != expected_bytes:
            errors.append(error("bytes_mismatch", "file size differs", path=rel, expected=expected_bytes, actual=actual_bytes))
        if isinstance(expected_hash, str) and SHA256_RE.fullmatch(expected_hash) and actual_hash != expected_hash:
            errors.append(error("sha256_mismatch", "file digest differs", path=rel, expected=expected_hash, actual=actual_hash))

    # Completeness is structural and therefore always checked for immutable and
    # seed inventories. --include-seeds adds seed digest/size verification.
    for role in ("immutable", "seed"):
        discovered = set(inventory[role]["files"])
        for rel_root in inventory[role]["roots"]:
            try:
                discovered.update(iter_tree(root, rel_root))
            except RuntimeError as exc:
                errors.append(error("inventory_scan_failed", str(exc), path=rel_root))
        extras = sorted(discovered - listed_by_role[role])
        omissions = sorted(listed_by_role[role] - discovered)
        for rel in extras:
            errors.append(error("unlisted_inventory_file", "managed inventory contains an unlisted file", path=rel, actual=role))
        for rel in omissions:
            # A role record covered by a root but absent physically is already a
            # digest-mode error only when selected; inventory remains invalid in all modes.
            errors.append(error("listed_inventory_file_missing", "listed inventory file is absent", path=rel, actual=role))

    return {
        "status": "OK" if not errors else "INVALID",
        "package_root": str(root),
        "mode": "immutable+seed" if include_seeds else "immutable (seed inventory only)",
        "checked": checked,
        "errors": errors,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--package-root", help="package directory containing MANIFEST.json")
    result.add_argument("--include-seeds", action="store_true", help="also verify role=seed digests and sizes")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        root = find_package_root(args.package_root)
        result = verify(root, args.include_seeds)
    except ValueError as exc:
        result = {"status": "INVALID", "package_root": None, "checked": 0, "errors": [error("package_root", str(exc))]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
