#!/usr/bin/env python3
"""Import hash-verified compressed packages into pub.experimental.

Accepted transports under .build/pubexp_import/packages/:
  * package.tar.xz
  * package.tar.xz.b64.part000of003, part001of003, ...

Incomplete split transports are ignored until all declared parts exist. Each
decoded tar.xz must contain MANIFEST.json with ``files`` entries carrying a
``name`` (or ``path``), ``size`` and ``sha256``. Every output byte is verified
before write. Successful transport files are removed after import.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / ".build" / "pubexp_import" / "packages"
DEST = ROOT / "pub.experimental"
PART_RE = re.compile(r"^(?P<base>.+\.tar\.xz)\.b64\.part(?P<num>\d+)of(?P<total>\d+)$")


def safe_relative(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if not name or p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError(f"unsafe package path: {name!r}")
    if any(part.startswith(".") for part in p.parts):
        raise ValueError(f"hidden package path not allowed: {name!r}")
    return p


def read_transports() -> list[tuple[str, bytes, list[Path]]]:
    out: list[tuple[str, bytes, list[Path]]] = []
    for p in sorted(PACKAGES.glob("*.tar.xz"), key=lambda x: x.name.casefold()):
        out.append((p.name, p.read_bytes(), [p]))

    groups: dict[tuple[str, int], list[tuple[int, Path]]] = {}
    for p in PACKAGES.glob("*.tar.xz.b64.part*of*"):
        m = PART_RE.match(p.name)
        if m:
            key = (m.group("base"), int(m.group("total")))
            groups.setdefault(key, []).append((int(m.group("num")), p))
    for (base, total), parts in sorted(groups.items()):
        parts.sort()
        nums = [n for n, _ in parts]
        if len(parts) != total or nums != list(range(total)):
            print(f"waiting for complete transport {base}: have {nums}, need 0..{total-1}")
            continue
        text = "".join(p.read_text(encoding="ascii").strip() for _, p in parts)
        try:
            raw = base64.b64decode(text, validate=True)
        except Exception as exc:
            raise ValueError(f"{base}: invalid Base64 transport") from exc
        out.append((base, raw, [p for _, p in parts]))
    return out


def load_package(name: str, raw: bytes) -> list[tuple[PurePosixPath, bytes]]:
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:xz") as tf:
        try:
            mf = tf.extractfile(tf.getmember("MANIFEST.json"))
        except KeyError as exc:
            raise ValueError(f"{name}: missing MANIFEST.json") from exc
        if mf is None:
            raise ValueError(f"{name}: unreadable MANIFEST.json")
        specs = json.loads(mf.read().decode("utf-8")).get("files")
        if not isinstance(specs, list) or not specs:
            raise ValueError(f"{name}: manifest has no files")
        output: list[tuple[PurePosixPath, bytes]] = []
        for spec in specs:
            if not isinstance(spec, dict):
                raise ValueError(f"{name}: invalid manifest entry")
            rel_name = str(spec.get("path") or spec.get("name") or spec.get("filename") or "")
            rel = safe_relative(rel_name)
            try:
                member = tf.getmember(rel.as_posix())
            except KeyError as exc:
                raise ValueError(f"{name}: missing {rel}") from exc
            if not member.isfile():
                raise ValueError(f"{name}: {rel} is not a regular file")
            src = tf.extractfile(member)
            if src is None:
                raise ValueError(f"{name}: cannot read {rel}")
            data = src.read()
            expected_size = int(spec["size"])
            expected_hash = str(spec["sha256"]).lower()
            actual_hash = hashlib.sha256(data).hexdigest()
            if len(data) != expected_size or actual_hash != expected_hash:
                raise ValueError(
                    f"{name}: verification failed for {rel}: "
                    f"size {len(data)}/{expected_size}, sha256 {actual_hash}/{expected_hash}"
                )
            output.append((rel, data))
        return output


def main() -> None:
    if not PACKAGES.exists():
        print("no pub.experimental import packages")
        return
    transports = read_transports()
    if not transports:
        print("no complete pub.experimental import packages")
        return

    # Verify all complete packages before writing any output.
    verified = [(name, load_package(name, raw), sources) for name, raw, sources in transports]
    DEST.mkdir(parents=True, exist_ok=True)
    written = 0
    for name, files, sources in verified:
        for rel, data in files:
            target = DEST.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_bytes() != data:
                target.write_bytes(data)
                written += 1
        for source in sources:
            source.unlink()
        print(f"verified {name}: {len(files)} file(s)")
    print(f"imported/updated {written} experimental file(s)")


if __name__ == "__main__":
    main()
