#!/usr/bin/env python3
"""Build an auditable, bounded YunMom PNG contact sheet.

Every input must be a current asset in the canonical visual program, match its
registered path and SHA-256, and permit persistent evidence.  The output and
its provenance sidecar are each atomically created beneath ``visual/reviews/``
and never overwrite existing files.  Caught failures remove any partial pair;
the sidecar hash binding detects interruption between the two filesystem links.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any
import warnings


MAX_INPUTS = 48
MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_TOTAL_INPUT_BYTES = 512 * 1024 * 1024
MAX_INPUT_PIXELS = 40_000_000
MAX_TOTAL_INPUT_PIXELS = 240_000_000
MAX_OUTPUT_PIXELS = 100_000_000
MAX_DIMENSION = 16_384
MAX_FONT_BYTES = 64 * 1024 * 1024
GENERATOR_VERSION = "2.0.0"


class ContactSheetError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_handle(handle: Any) -> str:
    digest = hashlib.sha256()
    handle.seek(0)
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    handle.seek(0)
    return digest.hexdigest()


def find_project_root(explicit: str, visual_ops: Any) -> Path:
    try:
        return visual_ops.secure_project_root(explicit)
    except visual_ops.VisualStateError as exc:
        raise ContactSheetError(str(exc)) from exc


def contained_path(root: Path, value: str, visual_ops: Any, *, output: bool = False) -> Path:
    required_prefix = "visual/reviews/" if output else "visual/"
    try:
        path, _rel = visual_ops.visual_path(
            root, value, must_exist=not output, allowed_prefixes=(required_prefix,),
        )
        return path
    except visual_ops.VisualStateError as exc:
        raise ContactSheetError(str(exc)) from exc


def reject_aliases(inputs: list[Path], output: Path, sidecar: Path) -> None:
    canonical_inputs: set[str] = set()
    for path in inputs:
        if getattr(path.stat(), "st_nlink", 1) != 1:
            raise ContactSheetError(f"hard-linked input is forbidden: {path}")
        key = os.path.normcase(str(path.resolve(strict=True)))
        if key in canonical_inputs:
            raise ContactSheetError(f"duplicate or aliased input path: {path}")
        canonical_inputs.add(key)
    for target in (output, sidecar):
        if target.exists():
            raise ContactSheetError(f"output already exists; no-overwrite policy: {target}")
        if os.path.normcase(str(target.resolve(strict=False))) in canonical_inputs:
            raise ContactSheetError("output or sidecar aliases an input path")
    for left_index, left in enumerate(inputs):
        for right in inputs[left_index + 1:]:
            try:
                if os.path.samefile(left, right):
                    raise ContactSheetError(f"duplicate hard-link inputs: {left} and {right}")
            except OSError as exc:
                raise ContactSheetError(f"cannot verify input identity: {exc}") from exc


def load_visual_ops() -> Any:
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import visual_ops  # type: ignore
    except Exception as exc:
        raise ContactSheetError(f"visual_ops cannot be loaded: {exc}") from exc
    return visual_ops


def load_and_validate_program(root: Path, visual_ops: Any) -> tuple[dict[str, Any], str]:
    try:
        canonical, _ = visual_ops.visual_path(
            root, "visual/manifests/visual_program.json", must_exist=True,
            allowed_prefixes=("visual/manifests/",),
        )
        payload = canonical.read_bytes()
        program = json.loads(payload.decode("utf-8"))
        errors = visual_ops.validate_program(root, program, check_files=True)
    except Exception as exc:
        raise ContactSheetError(f"canonical visual program cannot be loaded: {exc}") from exc
    if errors:
        preview = "; ".join(errors[:8])
        if len(errors) > 8:
            preview += f"; ... ({len(errors)} errors total)"
        raise ContactSheetError(f"canonical visual program is invalid: {preview}")
    return program, hashlib.sha256(payload).hexdigest()


def registered_assets(root: Path, program: dict[str, Any], inputs: list[Path]) -> list[dict[str, Any]]:
    by_path: dict[str, dict[str, Any]] = {}
    for asset in program["assets"]:
        path = (root / Path(asset["path"])).resolve(strict=False)
        key = os.path.normcase(str(path))
        if key in by_path:
            raise ContactSheetError(f"canonical program maps multiple assets to one path: {asset['path']}")
        by_path[key] = asset

    selected: list[dict[str, Any]] = []
    for path in inputs:
        key = os.path.normcase(str(path.resolve(strict=True)))
        asset = by_path.get(key)
        if asset is None:
            raise ContactSheetError(f"input is not a registered canonical asset: {path}")
        if asset.get("freshness") != "current" or asset.get("lifecycle_stage") in {"deprecated", "rejected"}:
            raise ContactSheetError(f"input asset is not current/active: {asset.get('id')}")
        actual_hash = sha256_file(path)
        if asset.get("sha256") != actual_hash:
            raise ContactSheetError(f"input hash differs from canonical asset: {asset.get('id')}")
        privacy = asset.get("privacy", {})
        if (
            privacy.get("persistent_evidence_allowed") is not True
            or privacy.get("content_origin") in {"real_sensitive", "unknown"}
            or privacy.get("classification") == "unclassified"
        ):
            raise ContactSheetError(
                f"asset privacy forbids persistent contact-sheet evidence: {asset.get('id')}"
            )
        selected.append(asset)
    return selected


def alpha_label(index: int) -> str:
    value = index + 1
    parts: list[str] = []
    while value:
        value, remainder = divmod(value - 1, 26)
        parts.append(chr(ord("A") + remainder))
    return "".join(reversed(parts))


def load_pillow() -> tuple[Any, Any, Any, Any, Any, Any, str, str | None, str | None]:
    try:
        import PIL
        from PIL import Image, ImageCms, ImageColor, ImageDraw, ImageFont, ImageOps, features
    except ImportError as exc:
        raise ContactSheetError(
            "Pillow 12.2.0 is required for contact sheets; install scripts/requirements-contact-sheet.txt"
        ) from exc
    if PIL.__version__ != "12.2.0":
        raise ContactSheetError(
            f"Pillow 12.2.0 is required for deterministic evidence; found {PIL.__version__}"
        )
    Image.MAX_IMAGE_PIXELS = MAX_INPUT_PIXELS
    return (
        Image, ImageCms, ImageColor, ImageDraw, ImageFont, ImageOps,
        PIL.__version__, features.version("littlecms2"), features.version("freetype2"),
    )


def auto_cjk_font(visual_ops: Any) -> Path | None:
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates = (
        windir / "Fonts" / "msyh.ttc",
        windir / "Fonts" / "msyhbd.ttc",
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
    )
    for item in candidates:
        if not item.is_file():
            continue
        try:
            return visual_ops.secure_external_file(item, label="font")
        except visual_ops.VisualStateError:
            continue
    return None


def load_font(
    ImageFont: Any, requested: str | None, size: int, labels: list[str], visual_ops: Any,
) -> tuple[Any, dict[str, Any]]:
    needs_cjk = any(any(ord(character) > 127 for character in label) for label in labels)
    font_path: Path | None = None
    source = "pillow_default"
    if requested:
        try:
            font_path = visual_ops.secure_external_file(requested, label="font")
        except visual_ops.VisualStateError as exc:
            raise ContactSheetError(str(exc)) from exc
        source = "explicit"
    elif needs_cjk:
        font_path = auto_cjk_font(visual_ops)
        source = "known_system_cjk"
        if font_path is None:
            raise ContactSheetError(
                "non-ASCII labels require --font pointing to a trusted CJK .ttf/.otf/.ttc font"
            )
    if font_path is not None:
        if font_path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
            raise ContactSheetError("font must use .ttf, .otf, or .ttc")
        if font_path.stat().st_size > MAX_FONT_BYTES:
            raise ContactSheetError(f"font exceeds {MAX_FONT_BYTES:,} bytes")
        try:
            font = ImageFont.truetype(str(font_path), size=size)
        except Exception as exc:
            raise ContactSheetError(f"cannot load requested font {font_path}: {exc}") from exc
        provenance = {
            "source": source,
            "path": str(font_path),
            "sha256": sha256_file(font_path),
            "size": size,
        }
        return font, provenance
    try:
        font = ImageFont.load_default(size=size)
    except Exception as exc:
        raise ContactSheetError(f"cannot load Pillow default Latin font: {exc}") from exc
    provenance = {
        "source": source,
        "path": "Pillow:load_default",
        "sha256": None,
        "size": size,
    }
    return font, provenance


def normalized_rgb(source: Any, Image: Any, ImageCms: Any, ImageOps: Any, path: Path) -> Any:
    try:
        frame_count = int(getattr(source, "n_frames", 1))
    except Exception as exc:
        raise ContactSheetError(f"cannot inspect frame count for {path}: {exc}") from exc
    if frame_count != 1:
        raise ContactSheetError(f"animated/multi-frame inputs are forbidden: {path}")
    image = ImageOps.exif_transpose(source)
    embedded = image.info.get("icc_profile")
    alpha = image.getchannel("A") if "A" in image.getbands() else None
    if embedded:
        try:
            input_profile = ImageCms.ImageCmsProfile(io.BytesIO(embedded))
            output_profile = ImageCms.createProfile("sRGB")
            base = image.convert("RGB") if alpha is not None or image.mode in {"P", "LA"} else image
            converted = ImageCms.profileToProfile(
                base, input_profile, output_profile, outputMode="RGB", renderingIntent=0
            )
        except Exception as exc:
            raise ContactSheetError(f"invalid or unsupported embedded ICC profile in {path}: {exc}") from exc
    else:
        if image.mode in {"CMYK", "LAB", "HSV"}:
            raise ContactSheetError(f"unprofiled {image.mode} input has ambiguous color space: {path}")
        converted = image.convert("RGB")
    if alpha is not None:
        rgba = converted.convert("RGBA")
        rgba.putalpha(alpha)
        return rgba
    return converted.convert("RGBA")


def fit_label(draw: Any, text: str, font: Any, max_width: int) -> str:
    cleaned = " ".join(text.split())
    if draw.textbbox((0, 0), cleaned, font=font)[2] <= max_width:
        return cleaned
    suffix = "..."
    low, high = 0, len(cleaned)
    while low < high:
        midpoint = (low + high + 1) // 2
        candidate = cleaned[:midpoint].rstrip() + suffix
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            low = midpoint
        else:
            high = midpoint - 1
    return cleaned[:low].rstrip() + suffix


def safe_asset_name(value: Any) -> str:
    """Keep predictable Latin/CJK label glyphs and replace emoji/control text."""
    text = str(value)
    result: list[str] = []
    for character in text:
        point = ord(character)
        if character in "\t\r\n":
            result.append(" ")
        elif 0x20 <= point <= 0x7E:
            result.append(character)
        elif (
            0x3400 <= point <= 0x4DBF
            or 0x4E00 <= point <= 0x9FFF
            or 0xF900 <= point <= 0xFAFF
            or 0x3000 <= point <= 0x303F
            or 0xFF00 <= point <= 0xFFEF
        ):
            result.append(character)
        else:
            result.append("_")
    return "".join(result)


def atomic_pair(image: Any, sidecar_data: dict[str, Any], output: Path, sidecar: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fd_image, temp_image_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".png", dir=output.parent)
    os.close(fd_image)
    fd_json, temp_json_name = tempfile.mkstemp(prefix=f".{sidecar.name}.", suffix=".json", dir=output.parent)
    os.close(fd_json)
    temp_image = Path(temp_image_name)
    temp_json = Path(temp_json_name)
    linked_output = False
    try:
        image.save(temp_image, format="PNG", compress_level=9, optimize=False)
        with temp_image.open("r+b") as handle:
            os.fsync(handle.fileno())
        sidecar_data["sheet"]["sha256"] = sha256_file(temp_image)
        sidecar_data["sheet"]["bytes"] = temp_image.stat().st_size
        serialized = json.dumps(
            sidecar_data, ensure_ascii=False, sort_keys=True, indent=2, separators=(",", ": ")
        ) + "\n"
        with temp_json.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temp_image, output)
            linked_output = True
            os.link(temp_json, sidecar)
        except FileExistsError as exc:
            raise ContactSheetError("output or sidecar appeared concurrently; refusing overwrite") from exc
        except OSError as exc:
            raise ContactSheetError(f"filesystem cannot atomically create no-overwrite evidence: {exc}") from exc
    except Exception:
        if linked_output:
            try:
                if output.exists() and os.path.samefile(output, temp_image):
                    output.unlink()
            except OSError:
                pass
        raise
    finally:
        temp_image.unlink(missing_ok=True)
        temp_json.unlink(missing_ok=True)


def build_sheet(
    root: Path,
    image_paths: list[Path],
    assets: list[dict[str, Any]],
    output: Path,
    sidecar: Path,
    columns: int,
    cell_width: int,
    cell_height: int,
    gutter: int,
    label_height: int,
    background_hex: str,
    font_path: str | None,
    font_size: int,
    program: dict[str, Any],
    program_sha256: str,
    visual_ops: Any,
) -> None:
    (
        Image, ImageCms, ImageColor, ImageDraw, ImageFont, ImageOps,
        pillow_version, littlecms_version, freetype_version,
    ) = load_pillow()
    try:
        background = ImageColor.getrgb(background_hex)
    except ValueError as exc:
        raise ContactSheetError(f"invalid background color: {background_hex}") from exc
    if len(background) != 3:
        raise ContactSheetError("background must be an opaque RGB color")
    canonical_background = "#" + "".join(f"{channel:02X}" for channel in background)
    labels = [
        f"{alpha_label(index)}  {asset['id']} v{asset['version']}  {safe_asset_name(asset['name'])}"
        for index, asset in enumerate(assets)
    ]
    font, font_provenance = load_font(ImageFont, font_path, font_size, labels, visual_ops)

    rows = math.ceil(len(image_paths) / columns)
    width = gutter + columns * (cell_width + gutter)
    height = gutter + rows * (cell_height + label_height + gutter)
    if width > MAX_DIMENSION or height > MAX_DIMENSION or width * height > MAX_OUTPUT_PIXELS:
        raise ContactSheetError(
            f"requested output {width}x{height} exceeds {MAX_DIMENSION}px / {MAX_OUTPUT_PIXELS:,}-pixel limits"
        )
    sheet = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(sheet)
    total_pixels = 0
    total_bytes = 0

    for index, (path, asset) in enumerate(zip(image_paths, assets, strict=True)):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with path.open("rb") as binary:
                    before_info = os.fstat(binary.fileno())
                    size_bytes = before_info.st_size
                    if size_bytes > MAX_INPUT_BYTES:
                        raise ContactSheetError(f"input exceeds {MAX_INPUT_BYTES:,} bytes: {path}")
                    total_bytes += size_bytes
                    if total_bytes > MAX_TOTAL_INPUT_BYTES:
                        raise ContactSheetError(f"inputs exceed {MAX_TOTAL_INPUT_BYTES:,} total bytes")
                    before_hash = sha256_handle(binary)
                    if before_hash != asset["sha256"]:
                        raise ContactSheetError(f"input changed before decode: {asset['id']}")
                    with Image.open(binary) as source:
                        width_in, height_in = source.size
                        pixels = width_in * height_in
                        if width_in > MAX_DIMENSION or height_in > MAX_DIMENSION or pixels > MAX_INPUT_PIXELS:
                            raise ContactSheetError(f"input dimensions exceed limits: {path}")
                        total_pixels += pixels
                        if total_pixels > MAX_TOTAL_INPUT_PIXELS:
                            raise ContactSheetError(f"inputs exceed {MAX_TOTAL_INPUT_PIXELS:,} total pixels")
                        source.load()
                        image = normalized_rgb(source, Image, ImageCms, ImageOps, path)
                    after_hash = sha256_handle(binary)
                    after_info = os.fstat(binary.fileno())
                    identity_before = (
                        before_info.st_dev, before_info.st_ino, before_info.st_size,
                        getattr(before_info, "st_mtime_ns", int(before_info.st_mtime * 1_000_000_000)),
                    )
                    identity_after = (
                        after_info.st_dev, after_info.st_ino, after_info.st_size,
                        getattr(after_info, "st_mtime_ns", int(after_info.st_mtime * 1_000_000_000)),
                    )
                    if after_hash != before_hash or identity_after != identity_before:
                        raise ContactSheetError(f"input changed while decoding: {asset['id']}")
        except ContactSheetError:
            raise
        except Exception as exc:
            raise ContactSheetError(f"cannot decode input image {path}: {exc}") from exc
        canvas = Image.new("RGBA", image.size, (*background, 255))
        canvas.alpha_composite(image)
        fitted = ImageOps.contain(
            canvas.convert("RGB"), (cell_width, cell_height), method=Image.Resampling.LANCZOS
        )
        row, column = divmod(index, columns)
        left = gutter + column * (cell_width + gutter)
        top = gutter + row * (cell_height + label_height + gutter)
        x = left + (cell_width - fitted.width) // 2
        y = top + label_height + (cell_height - fitted.height) // 2
        sheet.paste(fitted, (x, y))
        label = fit_label(draw, labels[index], font, cell_width - 16)
        draw.text((left + 8, top + max(0, (label_height - font_size) // 2 - 1)), label, fill=(24, 22, 28), font=font)
        draw.rounded_rectangle(
            (left, top + label_height, left + cell_width - 1, top + label_height + cell_height - 1),
            radius=10, outline=(218, 213, 220), width=1,
        )

    output_rel = output.relative_to(root).as_posix()
    sidecar_data: dict[str, Any] = {
        "schema_version": 1,
        "kind": "yunmom_contact_sheet_provenance",
        "generator_version": GENERATOR_VERSION,
        "pillow_version": pillow_version,
        "littlecms_version": littlecms_version,
        "freetype_version": freetype_version,
        "visual_program": {
            "program_id": program["program_id"],
            "schema_version": program["schema_version"],
            "revision": program["revision"],
            "contract_version": program["contract_version"],
            "sha256": program_sha256,
        },
        "inputs": [
            {
                "asset_id": asset["id"],
                "asset_version": asset["version"],
                "path": path.relative_to(root).as_posix(),
                "sha256": asset["sha256"],
                "privacy_classification": asset["privacy"]["classification"],
                "content_origin": asset["privacy"]["content_origin"],
            }
            for path, asset in zip(image_paths, assets, strict=True)
        ],
        "sheet": {
            "path": output_rel,
            "sha256": None,
            "bytes": None,
            "format": "PNG",
            "width": width,
            "height": height,
        },
        "parameters": {
            "columns": columns,
            "cell_width": cell_width,
            "cell_height": cell_height,
            "gutter": gutter,
            "label_height": label_height,
            "background": canonical_background,
            "resampling": "LANCZOS",
            "png_compress_level": 9,
            "png_optimize": False,
            "font": font_provenance,
        },
    }
    canonical = root / "visual" / "manifests" / "visual_program.json"
    if sha256_file(canonical) != program_sha256:
        raise ContactSheetError("canonical visual program changed while building the sheet")
    for path, asset in zip(image_paths, assets, strict=True):
        if sha256_file(path) != asset["sha256"]:
            raise ContactSheetError(f"input changed before evidence commit: {asset['id']}")
    atomic_pair(sheet, sidecar_data, output, sidecar)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--out", required=True, help="new .png path beneath visual/reviews/")
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--cell-width", type=int, default=640)
    parser.add_argument("--cell-height", type=int, default=640)
    parser.add_argument("--gutter", type=int, default=24)
    parser.add_argument("--label-height", type=int, default=44)
    parser.add_argument("--font", help="trusted .ttf/.otf/.ttc; required if no known CJK font is available")
    parser.add_argument("--font-size", type=int, default=18)
    parser.add_argument("--background", default="#FFFDFC")
    args = parser.parse_args(argv)
    if not 1 <= len(args.images) <= MAX_INPUTS:
        parser.error(f"contact sheets require 1-{MAX_INPUTS} images")
    if not 1 <= args.columns <= MAX_INPUTS:
        parser.error(f"columns must be 1-{MAX_INPUTS}")
    if not 64 <= args.cell_width <= 4096 or not 64 <= args.cell_height <= 4096:
        parser.error("cell width/height must be 64-4096")
    if not 0 <= args.gutter <= 256 or not 24 <= args.label_height <= 256:
        parser.error("gutter must be 0-256 and label height 24-256")
    if not 12 <= args.font_size <= 64 or args.label_height < args.font_size + 6:
        parser.error("font size must be 12-64 and label height at least font size + 6")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        visual_ops = load_visual_ops()
        root = find_project_root(args.project_root, visual_ops)
        inputs = [contained_path(root, value, visual_ops) for value in args.images]
        for path in inputs:
            if not path.is_file():
                raise ContactSheetError(f"input does not exist: {path}")
        output = contained_path(root, args.out, visual_ops, output=True)
        if output.suffix.lower() != ".png":
            raise ContactSheetError("contact-sheet output must use .png")
        sidecar = output.with_suffix(output.suffix + ".json")
        contained_path(root, str(sidecar), visual_ops, output=True)
        reject_aliases(inputs, output, sidecar)
        # Use the same advisory lock as visual_ops so canonical state cannot be
        # revised by a cooperating command between validation and evidence commit.
        try:
            with visual_ops.project_lock(root):
                program, program_sha256 = load_and_validate_program(root, visual_ops)
                assets = registered_assets(root, program, inputs)
                build_sheet(
                    root, inputs, assets, output, sidecar,
                    args.columns, args.cell_width, args.cell_height,
                    args.gutter, args.label_height, args.background,
                    args.font, args.font_size, program, program_sha256,
                    visual_ops,
                )
        except visual_ops.VisualStateError as exc:
            raise ContactSheetError(f"visual-program lock/state failure: {exc}") from exc
        print(json.dumps({
            "status": "created",
            "output": str(output),
            "sidecar": str(sidecar),
            "input_assets": [asset["id"] for asset in assets],
        }, ensure_ascii=False))
        return 0
    except (ContactSheetError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
