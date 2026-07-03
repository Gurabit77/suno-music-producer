#!/usr/bin/env python3
"""Verify the AI music listening-test and versioning workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐盲听评审与版本归档工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐评估与听测资料组.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
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
    "盲听",
    "A/B",
    "反向 caption",
    "alignment",
    "preference",
    "brief.md",
    "takes.md",
    "blind-review.md",
    "take-selection-decision.md",
    "repair-log.md",
    "匿名",
    "短片段",
    "十二维评分",
    "AI味红旗",
    "修作决策矩阵",
    "版本命名",
    "失败样本库",
    "tools/review_music_takes.py",
    "lock for post-production",
    "Suno",
    "Replace Section",
    "Extend",
    "Song Editor",
    "Persona",
    "权利",
]

SOURCE_TERMS = [
    "MUSHRA",
    "webMUSHRA",
    "ITU-R BS.1534",
    "pairwise",
    "human preference",
    "MusicCaps",
    "MusicLM",
    "alignment",
    "preference",
    "反向 caption",
    "客观指标",
    "人类听感",
    "待验证",
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
        if not under_vault(path):
            errors.append(f"path outside vault ({name}): {path}")
        if not path.exists():
            errors.append(f"missing page ({name}): {path}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    workflow = read(PAGES["workflow"])
    source = read(PAGES["source"])

    if not has_type(workflow, "analysis"):
        errors.append("workflow page must have type: analysis")
    if not has_type(source, "source"):
        errors.append("source page must have type: source")

    if compact_len(workflow) < 4200:
        errors.append("workflow page is too thin")
    if compact_len(source) < 2200:
        errors.append("source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    workflow_link = "[[AI 音乐盲听评审与版本归档工作流]]"
    source_link = "[[AI 音乐评估与听测资料组]]"

    for key in ["suno_workflow", "framework", "map", "analysis_index"]:
        if workflow_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link")

    root_index = read(PAGES["root_index"])
    if workflow_link not in root_index and "AI 音乐盲听评审与版本归档工作流" not in root_index:
        errors.append(f"{PAGES['root_index']} missing workflow link")

    for key in ["source_index", "map"]:
        if source_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link")

    log = read(PAGES["log"])
    if "AI 音乐盲听评审与版本归档工作流" not in log:
        errors.append("wiki/log.md missing evaluation workflow entry")

    if errors:
        print("AI music evaluation workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music evaluation workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
