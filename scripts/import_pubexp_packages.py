#!/usr/bin/env python3
"""Import verified compressed packages into pub.experimental.

Packages are tar.xz archives placed in .build/pubexp_import/packages/. Each
archive must contain a MANIFEST.json with a ``files`` list whose entries have
``path``, ``size``, and ``sha256``. Only files named in that manifest are
written, and every file is verified before anything is committed by CI.

This is a transport mechanism only: extracted bytes must exactly match the
manifest. Successful package archives are deleted after import so they do not
remain as publication artifacts.
"""
from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / ".build" / "pubexp_import" / "packages"
DEST = ROOT / "pub.experimental"


def safe_relative(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if not name or p.is_absolute() or any(part in {"", ".", ".."} for part in p.parts):
        raise ValueError(f"unsafe package path: {name!r}")
    if any(part.startswith(".") for part in p.parts):
        raise ValueError(f"hidden package path not allowed: {name!r}")
    return p


def load_package(package: Path) -> tuple[list[tuple[PurePosixPath, bytes]], int]:
    with tarfile.open(package, mode="r:xz") as tf:
        try:
            manifest_member = tf.getmember("MANIFEST.json")
        except KeyError as exc:
            raise ValueError(f"{package.name}: missing MANIFEST.json") from exc
        f = tf.extractfile(manifest_member)
        if f is None:
            raise ValueError(f"{package.name}: unreadable MANIFEST.json")
        manifest = json.loads(f.read().decode("utf-8"))
        specs = manifest.get("files")
        if not isinstance(specs, list) or not specs:
            raise ValueError(f"{package.name}: manifest has no files")

        output: list[tuple[PurePosixPath, bytes]] = []
        for spec in specs:
            if not isinstance(spec, dict):
                raise ValueError(f"{package.name}: invalid manifest entry")
            rel = safe_relative(str(spec.get("path") or ""))
            expected_size = int(spec["size"])
            expected_sha256 = str(spec["sha256"]).lower()
            try:
                member = tf.getmember(rel.as_posix())
            except KeyError as exc:
                raise ValueError(f"{package.name}: missing {rel}") from exc
            if not member.isfile():
                raise ValueError(f"{package.name}: {rel} is not a regular file")
            src = tf.extractfile(member)
            if src is None:
                raise ValueError(f"{package.name}: cannot read {rel}")
            data = src.read()
            actual_sha256 = hashlib.sha256(data).hexdigest()
            if len(data) != expected_size or actual_sha256 != expected_sha256:
                raise ValueError(
                    f"{package.name}: verification failed for {rel}: "
                    f"size {len(data)}/{expected_size}, sha256 {actual_sha256}/{expected_sha256}"
                )
            output.append((rel, data))
        return output, len(specs)


def main() -> None:
    if not PACKAGES.exists():
        print("no pub.experimental import packages")
        return

    DEST.mkdir(parents=True, exist_ok=True)
    packages = sorted(PACKAGES.glob("*.tar.xz"), key=lambda p: p.name.casefold())
    if not packages:
        print("no pub.experimental import packages")
        return

    # Verify every package first. If one is bad, write nothing.
    verified: list[tuple[Path, list[tuple[PurePosixPath, bytes]], int]] = []
    for package in packages:
        files, count = load_package(package)
        verified.append((package, files, count))

    written = 0
    for package, files, _ in verified:
        for rel, data in files:
            target = DEST.joinpath(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() == data:
                continue
            target.write_bytes(data)
            written += 1
        package.unlink()

    print(f"verified {len(verified)} package(s); imported/updated {written} experimental file(s)")


if __name__ == "__main__":
    main()
