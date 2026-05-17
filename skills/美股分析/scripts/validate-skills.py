#!/usr/bin/env python3
"""Validate US stock analysis skill source directories and .skill packages."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from zipfile import ZipFile


LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")


def _frontmatter(text: str) -> dict[str, str] | None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def _local_link_target(raw: str) -> str:
    return raw.split("#", 1)[0].strip()


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill_files = sorted(root.glob("*/*/SKILL.md"))

    if not skill_files:
        return [f"no skill files found under {root}"]

    for skill_file in skill_files:
        skill_dir = skill_file.parent
        slug = skill_dir.name
        package = skill_dir.parent / f"{slug}.skill"
        text = skill_file.read_text(encoding="utf-8")

        frontmatter = _frontmatter(text)
        if frontmatter is None:
            errors.append(f"missing frontmatter: {skill_file}")
        else:
            name = frontmatter.get("name", "")
            description = frontmatter.get("description", "")
            if name != slug:
                errors.append(f"name mismatch: {skill_file} has {name!r}, expected {slug!r}")
            if not description:
                errors.append(f"missing description: {skill_file}")
            elif not description.startswith("Use when"):
                errors.append(f"description must start with 'Use when': {skill_file}")
            if len(description.encode("utf-8")) >= 1024:
                errors.append(f"description too long: {skill_file}")

        for markdown_file in skill_dir.rglob("*.md"):
            markdown_text = markdown_file.read_text(encoding="utf-8")
            for raw_target in LINK_RE.findall(markdown_text):
                target = _local_link_target(raw_target)
                if not target or target.startswith("<"):
                    continue
                if not (markdown_file.parent / target).exists():
                    errors.append(f"broken link: {markdown_file} -> {raw_target}")

        if not package.is_file():
            errors.append(f"missing package: {package}")
            continue

        with ZipFile(package) as archive:
            names = archive.namelist()
            top_level = {name.split("/", 1)[0] for name in names if name.strip("/")}
            if top_level != {slug}:
                errors.append(f"package top-level mismatch: {package}: {sorted(top_level)}")
            bad_entries = [
                name
                for name in names
                if name.endswith(".DS_Store") or name.endswith(".bak") or "ABCL" in name
            ]
            if bad_entries:
                errors.append(f"bad package entries: {package}: {bad_entries[:5]}")
            packaged_skill = f"{slug}/SKILL.md"
            if packaged_skill not in names:
                errors.append(f"package missing SKILL.md: {package}")
            elif archive.read(packaged_skill).decode("utf-8") != text:
                errors.append(f"package SKILL.md differs from source: {package}")

    empty_dirs = [path for path in root.rglob("*") if path.is_dir() and not any(path.iterdir())]
    for path in empty_dirs:
        errors.append(f"empty directory: {path}")

    bad_source_files = [
        path
        for path in root.rglob("*")
        if path.name == ".DS_Store" or path.suffix == ".bak" or "ABCL" in path.name
    ]
    for path in bad_source_files:
        errors.append(f"bad source artifact: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        nargs="?",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to the 美股分析 skill bundle root.",
    )
    args = parser.parse_args()

    errors = validate(args.root.resolve())
    if errors:
        print("\n".join(errors))
        return 1
    print("all skill checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
