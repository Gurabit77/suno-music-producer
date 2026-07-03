#!/usr/bin/env python3
"""Verify the Suno first-principles Obsidian expansion."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

REQUIRED_GUARD_FILES = [
    VAULT / "CLAUDE.md",
    VAULT / "CODEX.md",
    WIKI / "系统" / "自动记录价值闸门.md",
    WIKI / "系统" / "知识新增工作流.md",
    WIKI / "index.md",
]

PAGES = {
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "local Suno prompt methodology本地资料与全网方法补充.md",
    "control": WIKI / "概念" / "音乐" / "AI 音乐去 AI 味核心控制面.md",
    "workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "translation": WIKI / "概念" / "音乐" / "AI 音乐提示词如何转译音乐语言.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "concept_index": WIKI / "概念" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "source_group": WIKI / "来源" / "外部资料" / "2026-06-23 local Suno prompt methodology与 AI 音乐生成资料组.md",
    "log": WIKI / "log.md",
}

FRAMEWORK_TERMS = [
    "第一性原理",
    "local Suno prompt methodology",
    "真人感",
    "AI味",
    "十二维",
    "参考拆解",
    "语言重音",
    "prosody",
    "topline",
    "groove",
    "bass",
    "编曲密度",
    "声线身份",
    "盲听",
    "版本记录",
    "局部修作",
    "Exclude",
    "Creative Sliders",
    "Personas",
    "Studio",
    "版权",
    "待验证",
]

SOURCE_TERMS = [
    "/path/to/suno-prompt-methodology",
    "official-clean-md",
    "templates/suno-prompt-template.md",
    "suno-prompt-review-checklist.md",
    "Suno",
    "Google Lyria",
    "ElevenLabs",
    "Stable Audio",
    "ACE-Step",
    "GitHub",
    "Bilibili",
    "YouTube",
    "社区资料",
    "待验证",
    "可信度分层",
]

BACKLINK_PAGES = [
    PAGES["control"],
    PAGES["workflow"],
    PAGES["translation"],
    PAGES["map"],
    PAGES["concept_index"],
    PAGES["analysis_index"],
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def assert_under_vault(path: Path) -> None:
    resolved = path.resolve()
    vault = VAULT.resolve()
    if vault not in [resolved, *resolved.parents]:
        raise AssertionError(f"path outside vault: {path}")


def has_frontmatter_type(text: str, expected_type: str) -> bool:
    return text.startswith("---\n") and f"type: {expected_type}" in text.split("---", 2)[1]


def main() -> int:
    errors: list[str] = []

    if not VAULT.exists():
        errors.append(f"vault missing: {VAULT}")

    for path in REQUIRED_GUARD_FILES:
        if not path.exists():
            errors.append(f"guard file missing: {path}")

    for name, path in PAGES.items():
        try:
            assert_under_vault(path)
        except AssertionError as exc:
            errors.append(str(exc))
        if not path.exists():
            errors.append(f"required page missing ({name}): {path}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    framework = read(PAGES["framework"])
    source = read(PAGES["source"])

    if not has_frontmatter_type(framework, "analysis"):
        errors.append("framework page must have type: analysis")
    if not has_frontmatter_type(source, "source"):
        errors.append("source page must have type: source")

    if compact_len(framework) < 4500:
        errors.append("framework page is too thin")
    if compact_len(source) < 2500:
        errors.append("source page is too thin")

    missing_framework = [term for term in FRAMEWORK_TERMS if term not in framework]
    if missing_framework:
        errors.append("framework missing terms: " + ", ".join(missing_framework))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    for path in BACKLINK_PAGES:
        text = read(path)
        if "[[AI 音乐真人感第一性原理审查框架]]" not in text:
            errors.append(f"missing framework backlink in {path}")

    source_links = [
        "[[local Suno prompt methodology本地资料与全网方法补充]]",
        "[[AI 音乐真人感第一性原理审查框架]]",
    ]
    for path in [PAGES["source_index"], PAGES["source_group"], PAGES["map"]]:
        text = read(path)
        for link in source_links:
            if link not in text and link.replace("[[", "[[wiki/分析/音乐/") not in text:
                errors.append(f"missing link {link} in {path}")

    log = read(PAGES["log"])
    if "Suno 方法论第一性原理扩充" not in log:
        errors.append("wiki/log.md missing Suno first-principles entry")

    if errors:
        print("Suno first-principles verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Suno first-principles Obsidian expansion verification passed.")
    print(f"framework: {PAGES['framework']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
