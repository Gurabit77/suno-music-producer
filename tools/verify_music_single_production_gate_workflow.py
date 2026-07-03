#!/usr/bin/env python3
"""Verify the AI music single production control and stage-gate notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐单曲制作总控与阶段闸门工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐单曲制作总控与阶段闸门资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "suno": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "ai_flavor": WIKI / "概念" / "音乐" / "AI 音乐去 AI 味核心控制面.md",
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
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
    "song-production-control-board.md",
    "project-status-audit.md",
    "next-action.md",
    "tools/audit_music_song_project_status.py",
    "project-intake.md",
    "rights-and-source-precheck.md",
    "song-brief.md",
    "style-dna-and-catalog-fit.md",
    "writing-design-gate.md",
    "prompt-experiment-gate.md",
    "take-selection-gate.md",
    "repair-routing-gate.md",
    "repair-regression-gate",
    "regression-listen.md",
    "editor-studio-stems-gate.md",
    "daw-humanization-gate.md",
    "vocal-production-gate.md",
    "mix-lock-gate.md",
    "master-audio-qc-gate.md",
    "release-rights-gate.md",
    "catalog-memory-gate.md",
    "postmortem-and-prompt-memory.md",
    "release-candidate",
    "publish-ready",
    "hold",
    "abandon",
    "Studio/stems",
    "DAW session",
    "Multitrack",
    "Manual BPM",
    "Voice",
    "Persona",
    "Custom Model",
    "take-ledger.md",
    "repair-route-map.md",
    "release-audio-qc-report.md",
    "release-candidate-rights-gate.md",
    "compile_music_prompt_package.py",
    "Model",
    "Weirdness",
    "Style Influence",
    "style DNA 去身份化",
    "review_music_takes.py",
    "route_music_repairs.py",
    "prepare_music_daw_handoff.py",
    "prepare_music_release_candidate.py",
    "prepare_music_catalog_memory.py",
]

SOURCE_TERMS = [
    "Berklee",
    "Music Demo Production for Songwriters",
    "Music Production Fundamentals for Songwriters",
    "Arranging for Songwriters",
    "Art of Mixing",
    "Suno Song Editor",
    "Exporting from Studio",
    "Fixing Tempo Drift",
    "Remix FAQ",
    "ownership",
    "Full Song",
    "Selected Time Range",
    "Multitrack",
    "Manual BPM",
    "Cover",
    "Extend",
    "Reuse",
    "Speed",
    "Pro/Premier",
    "/path/to/suno-prompt-methodology",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[Suno 真人感歌曲生成工作流]]",
    "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]",
    "[[AI 音乐 AI味伪影诊断与修复路由工作流]]",
    "[[AI 音乐编曲密度与混音后期修作工作流]]",
    "[[AI 音乐 DAW 复刻与真人重录工作流]]",
    "[[AI 音乐人声录音与 Vocal Production 工作流]]",
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

    if compact_len(workflow) < 10500:
        errors.append("workflow page is too thin")
    if compact_len(source) < 6500:
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

    workflow_name = "AI 音乐单曲制作总控与阶段闸门工作流"
    source_name = "AI 音乐单曲制作总控与阶段闸门资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "suno",
        "ai_flavor",
        "framework",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    if "阶段闸门" not in workflow or "制作总控" not in workflow:
        errors.append("workflow missing stage-gate/control framing")
    if "继续生成" not in workflow or "局部修" not in workflow or "放弃" not in workflow:
        errors.append("workflow missing decision exits")

    if errors:
        print("AI music single production gate workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music single production gate workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
