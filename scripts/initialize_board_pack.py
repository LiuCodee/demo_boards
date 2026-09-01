#!/usr/bin/env python3
"""Interactively initialize board-pack metadata and README files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, NamedTuple

from update_supported_boards_table import update_readme


class BoardPackConfig(NamedTuple):
    vendor_name: str
    namespace: str
    use_repository_owner: bool
    component_name: str
    description: str
    copyright_holder: str


def _git_remote_owner(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        return None
    match = re.search(r"github\.com[:/]([^/]+)/", result.stdout.strip())
    return match.group(1) if match else None


def _prompt(
    input_fn: Callable[[str], str], chinese: str, english: str, default: str
) -> str:
    value = input_fn(f"{chinese} / {english} [{default}]: ").strip()
    return value or default


def collect_config(
    repo_root: Path,
    input_fn: Callable[[str], str] = input,
    default_namespace: str | None = None,
) -> BoardPackConfig:
    vendor_name = _prompt(input_fn, "厂商名称", "Vendor name", "YOUR_VENDOR_NAME")
    namespace_default = (
        default_namespace or _git_remote_owner(repo_root) or "YOUR_NAMESPACE"
    )
    namespace_input = input_fn(
        f"组件命名空间 / Component namespace [{namespace_default}]: "
    ).strip()
    namespace = namespace_input or namespace_default
    use_repository_owner = not namespace_input or namespace == namespace_default
    component_name = _prompt(
        input_fn, "组件名", "Component name", repo_root.name
    )
    description = _prompt(
        input_fn,
        "组件描述",
        "Component description",
        f"ESP Board Manager board definitions for {vendor_name} development boards",
    )
    copyright_holder = _prompt(
        input_fn, "版权持有人", "Copyright holder", vendor_name
    )
    return BoardPackConfig(
        vendor_name,
        namespace,
        use_repository_owner,
        component_name,
        description,
        copyright_holder,
    )


def _replace_readme_tokens(readme_path: Path, config: BoardPackConfig) -> None:
    content = readme_path.read_text(encoding="utf-8")
    content = content.replace("YOUR_VENDOR_NAME", config.vendor_name)
    content = content.replace("YOUR_NAMESPACE", config.namespace)
    content = content.replace("YOUR_COMPONENT_NAME", config.component_name)
    readme_path.write_text(content, encoding="utf-8")


def _update_manifest(repo_root: Path, config: BoardPackConfig) -> None:
    manifest_path = repo_root / "idf_component.yml"
    content = manifest_path.read_text(encoding="utf-8")
    description = config.description.replace("\\", "\\\\").replace('"', '\\"')
    updated, replacements = re.subn(
        r"^description:\s*.*$",
        f'description: "{description}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if replacements != 1:
        raise SystemExit(f"missing description field in {manifest_path}")
    manifest_path.write_text(updated, encoding="utf-8")


def _update_license(repo_root: Path, config: BoardPackConfig) -> None:
    license_path = repo_root / "LICENSE"
    content = license_path.read_text(encoding="utf-8")
    updated, replacements = re.subn(
        r"^(\s*Copyright\s+\d{4}\s+).*$",
        lambda match: f"{match.group(1)}{config.copyright_holder}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if replacements != 1:
        raise SystemExit(f"missing copyright notice in {license_path}")
    license_path.write_text(updated, encoding="utf-8")


def _update_workflow(repo_root: Path, config: BoardPackConfig) -> None:
    workflow_path = repo_root / ".github" / "workflows" / "ci.yml"
    content = workflow_path.read_text(encoding="utf-8")
    workflow_namespace = (
        "${{ github.repository_owner }}"
        if config.use_repository_owner
        else config.namespace
    )
    updated, namespace_replacements = re.subn(
        r'^(\s*--namespace\s+)"[^"]*"(.*)$',
        lambda match: f'{match.group(1)}"{workflow_namespace}"{match.group(2)}',
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if namespace_replacements != 1:
        raise SystemExit(f"missing upload --namespace argument in {workflow_path}")
    component_name = (
        "${{ github.event.repository.name }}"
        if config.component_name == repo_root.name
        else config.component_name
    )
    updated, name_replacements = re.subn(
        r'^(\s*--name\s+)"[^"]*"(.*)$',
        lambda match: f'{match.group(1)}"{component_name}"{match.group(2)}',
        updated,
        count=1,
        flags=re.MULTILINE,
    )
    if name_replacements != 1:
        raise SystemExit(f"missing upload --name argument in {workflow_path}")
    workflow_path.write_text(updated, encoding="utf-8")


def apply_config(repo_root: Path, config: BoardPackConfig) -> None:
    _replace_readme_tokens(repo_root / "README.md", config)
    _replace_readme_tokens(repo_root / "README_CN.md", config)
    _update_manifest(repo_root, config)
    _update_license(repo_root, config)
    _update_workflow(repo_root, config)
    update_readme(repo_root / "README.md", repo_root, "en")
    update_readme(repo_root / "README_CN.md", repo_root, "cn")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    config = collect_config(repo_root)
    apply_config(repo_root, config)
    print(
        "已更新 README、组件清单、许可证和 CI。"
        " / Updated the README files, manifest, license, and CI."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
