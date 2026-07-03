#!/usr/bin/env python3
"""Verify the AI music external listener feedback and release data workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐外部听众反馈与发行数据闭环工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐外部听众反馈与发行数据资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "blind": WIKI / "分析" / "音乐" / "AI 音乐盲听评审与版本归档工作流.md",
    "single_gate": WIKI / "分析" / "音乐" / "AI 音乐单曲制作总控与阶段闸门工作流.md",
    "release": WIKI / "分析" / "音乐" / "AI 音乐权利发布与平台披露工作流.md",
    "catalog": WIKI / "分析" / "音乐" / "AI 音乐艺人身份与 Catalog Bible 工作流.md",
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
    "external-listener-panel.md",
    "listener-screening.md",
    "listener-bias-control.md",
    "first-20-second-test.md",
    "hook-memory-test.md",
    "ai-flavor-red-flag-survey.md",
    "replay-intent-and-save-intent.md",
    "external-feedback-synthesis.md",
    "release-metrics-baseline.md",
    "day-7-release-review.md",
    "day-28-release-review.md",
    "day-90-catalog-review.md",
    "feedback-to-repair-router.md",
    "catalog-feedback-update.md",
    "release-candidate",
    "Spotify",
    "Audience segments",
    "monthly active listeners",
    "programmed listeners",
    "super listeners",
    "Release engagement",
    "YouTube",
    "audience retention",
    "SoundCloud",
    "Insights",
    "hook memory",
    "AI-flavor",
    "replay intent",
    "save intent",
    "active listener",
    "retention",
    "Day 7",
    "Day 28",
    "Day 90",
]

SOURCE_TERMS = [
    "Spotify",
    "monthly active listeners",
    "programmed listeners",
    "super listeners",
    "Release engagement",
    "first 28 days",
    "UTC",
    "streams/saves",
    "audience data",
    "playlist data",
    "YouTube",
    "audience retention",
    "1-2 days",
    "spikes",
    "SoundCloud Insights",
    "Top Fans",
    "Locations",
    "MUSHRA-like",
    "pairwise",
    "reverse caption",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[AI 音乐盲听评审与版本归档工作流]]",
    "[[AI 音乐单曲制作总控与阶段闸门工作流]]",
    "[[AI 音乐 AI味伪影诊断与修复路由工作流]]",
    "[[AI 音乐母带翻译与发行前音频 QC 工作流]]",
    "[[AI 音乐权利发布与平台披露工作流]]",
    "[[AI 音乐艺人身份与 Catalog Bible 工作流]]",
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

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    workflow = read(PAGES["workflow"])
    source = read(PAGES["source"])

    if not has_type(workflow, "analysis"):
        errors.append("workflow page must have type: analysis")
    if not has_type(source, "source"):
        errors.append("source page must have type: source")

    if compact_len(workflow) < 7000:
        errors.append("workflow page is too thin")
    if compact_len(source) < 4500:
        errors.append("source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    missing_links = [link for link in REQUIRED_WORKFLOW_LINKS if link not in workflow]
    if missing_links:
        errors.append("workflow missing links: " + ", ".join(missing_links))

    workflow_name = "AI 音乐外部听众反馈与发行数据闭环工作流"
    source_name = "AI 音乐外部听众反馈与发行数据资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "blind",
        "single_gate",
        "release",
        "catalog",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    if "repair and retest" not in workflow:
        errors.append("workflow missing repair-and-retest decision")
    if "programmed listeners" not in workflow or "monthly active listeners" not in workflow:
        errors.append("workflow missing active/programmed listener contrast")
    if "平台数据只提供信号" not in source and "平台数据只提供信号" not in workflow:
        errors.append("workflow/source missing platform-data boundary")

    if errors:
        print("AI music external listener feedback workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music external listener feedback workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
