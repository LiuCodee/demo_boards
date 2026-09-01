#!/usr/bin/env python3
"""Check whether a Board Manager catalog supports a chip for the active IDF."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Callable, Tuple


EXIT_UNSUPPORTED = 10
IDF_VERSION_RE = re.compile(r"^\s*set\s*\(\s*IDF_VERSION_([A-Z]{5})\s+(\d+)")


def _normalize_chip(chip: str) -> str:
    return chip.strip().lower().replace("-", "")


def _load_provider(bmgr_root: Path, idf_version: str):
    catalog_dir = bmgr_root / "private_inc" / "soc_capability_catalog"
    if not catalog_dir.is_dir():
        raise FileNotFoundError(f"missing Board Manager catalog: {catalog_dir}")
    sys.path.insert(0, str(bmgr_root))
    from generators.utils.soc_capabilities import SocCapabilityProvider

    return SocCapabilityProvider.load_for_idf_version(catalog_dir, idf_version)


def check_compatibility(
    bmgr_root: Path,
    idf_version: str,
    chip: str,
    provider_loader: Callable[[Path, str], object] = _load_provider,
) -> Tuple[bool, str]:
    """Return whether the selected BMGR catalog profile contains ``chip``."""
    provider = provider_loader(bmgr_root, idf_version)
    profile = str(provider.selected_profile_id)
    try:
        provider.chip(_normalize_chip(chip))
    except KeyError:
        return False, profile
    return True, profile


def _idf_version(idf_path: Path) -> str:
    version_file = idf_path / "tools" / "cmake" / "version.cmake"
    parts = {}
    with version_file.open(encoding="utf-8") as file:
        for line in file:
            match = IDF_VERSION_RE.match(line)
            if match:
                parts[match.group(1)] = match.group(2)
    try:
        return "{MAJOR}.{MINOR}.{PATCH}".format(**parts)
    except KeyError as error:
        raise RuntimeError(f"could not read ESP-IDF version from {version_file}") from error


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check active ESP-IDF chip support in the resolved BMGR catalog."
    )
    parser.add_argument("--chip", required=True)
    parser.add_argument(
        "--bmgr-root",
        type=Path,
        default=Path("managed_components/espressif__esp_board_manager"),
    )
    parser.add_argument("--idf-path", type=Path, default=os.environ.get("IDF_PATH"))
    args = parser.parse_args()

    if args.idf_path is None:
        print("IDF_PATH is not set", file=sys.stderr)
        return 2
    try:
        idf_version = _idf_version(args.idf_path)
        supported, profile = check_compatibility(
            args.bmgr_root, idf_version, args.chip
        )
    except Exception as error:
        print(f"failed to inspect Board Manager catalog: {error}", file=sys.stderr)
        return 2

    if supported:
        print(
            f"Board Manager catalog profile {profile} supports "
            f"{_normalize_chip(args.chip)}."
        )
        return 0

    print(
        f"Board Manager catalog profile {profile} does not support "
        f"{_normalize_chip(args.chip)} for ESP-IDF {idf_version}."
    )
    return EXIT_UNSUPPORTED


if __name__ == "__main__":
    sys.exit(main())
