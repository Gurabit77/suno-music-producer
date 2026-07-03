#!/usr/bin/env python3
"""Verify the AI music DAW reconstruction and human re-record workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐 DAW 复刻与真人重录工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐 DAW 复刻与真人重录资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "postproduction": WIKI / "分析" / "音乐" / "AI 音乐编曲密度与混音后期修作工作流.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "release_rights": WIKI / "分析" / "音乐" / "AI 音乐权利发布与平台披露工作流.md",
    "human_audio_seed": WIKI / "分析" / "音乐" / "AI 音乐人类音频草稿到成品工作流.md",
    "vocal_identity": WIKI / "分析" / "音乐" / "AI 音乐声线身份与演唱表演工作流.md",
    "ai_flavor": WIKI / "概念" / "音乐" / "AI 音乐去 AI 味核心控制面.md",
    "blind_review": WIKI / "分析" / "音乐" / "AI 音乐盲听评审与版本归档工作流.md",
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
    "best-take-lock.md",
    "daw-handoff-intent.md",
    "export-and-stems-ledger.md",
    "tempo-map-and-section-grid.md",
    "lead-sheet-and-chord-chart.md",
    "midi-transcription-and-correction.md",
    "stem-quality-triage.md",
    "human-overdub-priority.md",
    "vocal-rerecord-plan.md",
    "rhythm-section-rerecord-plan.md",
    "hybrid-arrangement-session.md",
    "mix-replacement-map.md",
    "session-versioning.md",
    "human-contribution-and-rights-link.md",
    "final-humanized-master-review.md",
    "Multitrack",
    "stems",
    "DAW",
    "MIDI",
    "Basic Pitch",
    "Demucs",
    "Ableton",
    "lead sheet",
    "chord chart",
    "tempo map",
    "human overdub",
    "re-record",
    "guide vocal",
    "session pack",
    "tools/prepare_music_daw_handoff.py",
    "daw-handoff-intent.md",
    "human-contribution-and-rights-link.md",
    "human-contribution-ledger.md",
    "release-candidate-rights-gate.md",
]

SOURCE_TERMS = [
    "Suno",
    "Studio",
    "Exporting from Studio",
    "Multitrack",
    "Selected Time Range",
    "Get MIDI",
    "Fixing Tempo Drift",
    "Stem Cover",
    "Basic Pitch",
    "audio-to-MIDI",
    "Ableton",
    "Convert Harmony",
    "Convert Melody",
    "Convert Drums",
    "Demucs",
    "source separation",
    "lead sheet",
    "Berklee",
    "Music Demo Production",
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

    if compact_len(workflow) < 11000:
        errors.append("workflow page is too thin")
    if compact_len(source) < 7000:
        errors.append("source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    workflow_link = "[[AI 音乐 DAW 复刻与真人重录工作流]]"
    source_link = "[[AI 音乐 DAW 复刻与真人重录资料组]]"

    workflow_link_pages = [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "postproduction",
        "suno_workflow",
        "release_rights",
        "human_audio_seed",
        "vocal_identity",
        "ai_flavor",
        "blind_review",
    ]
    for key in workflow_link_pages:
        text = read(PAGES[key])
        if workflow_link not in text and "AI 音乐 DAW 复刻与真人重录工作流" not in text:
            errors.append(f"{PAGES[key]} missing workflow link")

    source_link_pages = [
        "workflow",
        "source_index",
        "analysis_index",
        "map",
        "postproduction",
        "suno_workflow",
        "release_rights",
        "human_audio_seed",
        "vocal_identity",
        "ai_flavor",
        "blind_review",
    ]
    for key in source_link_pages:
        if source_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link")

    log = read(PAGES["log"])
    if "AI 音乐 DAW 复刻与真人重录工作流" not in log:
        errors.append("wiki/log.md missing DAW rerecord workflow entry")

    if errors:
        print("AI music DAW rerecord workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music DAW rerecord workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
