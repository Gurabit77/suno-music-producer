#!/usr/bin/env python3
"""Verify the representative artist study and AI music translation path."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "标杆艺人逐曲拆解与 AI 音乐转译学习路径.md",
    "artist_index": WIKI / "实体" / "音乐人" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "music_map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "log": WIKI / "log.md",
}

GUARDS = [
    VAULT / "CLAUDE.md",
    VAULT / "CODEX.md",
    WIKI / "系统" / "自动记录价值闸门.md",
    WIKI / "系统" / "知识新增工作流.md",
    WIKI / "index.md",
]

WORKFLOW_TERMS = [
    "artist-study-intake.md",
    "representative-song-triad.md",
    "deep-listening-pass.md",
    "song-dna-card.md",
    "protected-identity-removal.md",
    "pattern-synthesis.md",
    "prompt-translation-lab.md",
    "four-language-style-drill.md",
    "blind-transfer-review.md",
    "catalog-originality-check.md",
    "study-memory-bank.md",
    "reference",
    "Do-not-copy",
    "AI prompt 转译",
    "Suno 实作提醒",
    "盲听评审重点",
    "63",
    "米津玄师",
    "周杰伦",
    "King Gnu",
    "BTS",
    "Taylor Swift",
    "Radiohead",
    "五月天",
    "NewJeans",
    "/path/to/suno-prompt-methodology",
    "suno-prompt-template.md",
    "suno-prompt-review-checklist.md",
    "suno-song-creator-plugin",
]

REQUIRED_LINKS = [
    "[[wiki/实体/音乐人/index|音乐人索引]]",
    "[[AI 音乐参考曲风格 DNA 与合法转译工作流]]",
    "[[AI 音乐 Prompt 编译与生成前预检工作流]]",
    "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]",
    "[[AI 音乐艺人身份与 Catalog Bible 工作流]]",
    "[[四语种流行摇滚 AI 音乐 Prompt 模板套件]]",
    "[[AI 音乐提示词如何转译音乐语言]]",
    "[[AI 音乐盲听评审与版本归档工作流]]",
    "[[AI 音乐权利发布与平台披露工作流]]",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def under_vault(path: Path) -> bool:
    resolved = path.resolve()
    vault = VAULT.resolve()
    return vault in [resolved, *resolved.parents]


def has_type(text: str, expected: str) -> bool:
    if not text.startswith("---\n"):
        return False
    frontmatter = text.split("---", 2)[1]
    return f"type: {expected}" in frontmatter


def main() -> int:
    errors: list[str] = []

    for path in GUARDS:
        if not path.exists():
            errors.append(f"missing guard: {path}")

    for name, path in PAGES.items():
        if name != "log" and not under_vault(path):
            errors.append(f"path outside vault ({name}): {path}")
        if not path.exists():
            errors.append(f"missing page ({name}): {path}")

    artist_quality_gate = Path("tools/verify_music_artist_analysis_quality_gate.py")
    if not artist_quality_gate.exists():
        errors.append("missing artist analysis quality gate verifier")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    workflow = read(PAGES["workflow"])
    if not has_type(workflow, "analysis"):
        errors.append("workflow page must have type: analysis")

    if compact_len(workflow) < 9000:
        errors.append("workflow page is too thin")

    missing_terms = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_terms:
        errors.append("workflow missing terms: " + ", ".join(missing_terms))

    missing_links = [link for link in REQUIRED_LINKS if link not in workflow]
    if missing_links:
        errors.append("workflow missing links: " + ", ".join(missing_links))

    workflow_name = "标杆艺人逐曲拆解与 AI 音乐转译学习路径"
    for key in ["artist_index", "analysis_index", "music_map", "root_index", "log"]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    artist_index = read(PAGES["artist_index"])
    if "生成 prompt 中不直接保留艺人名" not in artist_index:
        errors.append("artist index missing no-direct-artist-name usage guidance")

    if "protected-identity-removal.md" not in artist_index:
        errors.append("artist index missing protected identity removal routing")

    music_map = read(PAGES["music_map"])
    if "代表艺人" not in music_map or "song-dna-card.md" not in music_map:
        errors.append("music map missing representative artist study integration")

    if errors:
        print("Representative artist study translation path verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Representative artist study translation path verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
