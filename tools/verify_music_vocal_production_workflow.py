#!/usr/bin/env python3
"""Verify the AI music vocal recording and production workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐人声录音与 Vocal Production 工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐人声录音与 Vocal Production 资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "vocal_identity": WIKI / "分析" / "音乐" / "AI 音乐声线身份与演唱表演工作流.md",
    "daw": WIKI / "分析" / "音乐" / "AI 音乐 DAW 复刻与真人重录工作流.md",
    "postproduction": WIKI / "分析" / "音乐" / "AI 音乐编曲密度与混音后期修作工作流.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "artifact_diagnosis": WIKI / "分析" / "音乐" / "AI 音乐 AI味伪影诊断与修复路由工作流.md",
    "voice_concept": WIKI / "概念" / "音乐" / "人声、声部与咬字.md",
    "sound_concept": WIKI / "概念" / "音乐" / "声音设计与录音制作基础.md",
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
    "vocal-production-intent.md",
    "voice-rights-and-role.md",
    "key-range-and-lyric-markup.md",
    "vocal-session-prep.md",
    "capture-chain-and-room.md",
    "cue-mix-and-performance-direction.md",
    "take-plan-and-comp-map.md",
    "lead-vocal-comp.md",
    "pitch-timing-emotion-pass.md",
    "breath-sibilance-mouth-noise-pass.md",
    "doubles-harmonies-adlibs-plan.md",
    "vocal-chain-and-space.md",
    "ai-stem-integration.md",
    "vocal-regression-listen.md",
    "human-contribution-ledger-link.md",
    "comping",
    "subtle tuning",
    "de-ess",
    "Auto-Tune",
    "Melodyne",
    "doubles",
    "harmonies",
    "ad-libs",
    "Mandarin",
    "Japanese",
    "Korean",
    "English",
]

SOURCE_TERMS = [
    "Berklee",
    "Vocal Production",
    "Commercial Vocal Production",
    "Topline and Vocal Production",
    "Suno Voices",
    "acapella",
    "neutral environment",
    "iZotope",
    "de-esser",
    "Nectar",
    "/path/to/suno-prompt-methodology",
    "Bilibili",
    "Douyin",
    "YouTube",
    "GitHub",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[AI 音乐声线身份与演唱表演工作流]]",
    "[[AI 音乐 AI味伪影诊断与修复路由工作流]]",
    "[[AI 音乐 DAW 复刻与真人重录工作流]]",
    "[[AI 音乐编曲密度与混音后期修作工作流]]",
    "[[AI 音乐权利发布与平台披露工作流]]",
    "[[Suno 真人感歌曲生成工作流]]",
    "[[AI 音乐人类音频草稿到成品工作流]]",
    "[[AI 音乐 Topline Hook 与旋律草稿工作流]]",
    "[[四语种歌词 Prosody 与 AI 音乐咬字审查表]]",
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

    if compact_len(workflow) < 11000:
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

    workflow_name = "AI 音乐人声录音与 Vocal Production 工作流"
    source_name = "AI 音乐人声录音与 Vocal Production 资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "vocal_identity",
        "daw",
        "postproduction",
        "suno_workflow",
        "artifact_diagnosis",
        "voice_concept",
        "sound_concept",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    if "release vocal" not in workflow:
        errors.append("workflow missing release vocal target")
    if "acapella" not in workflow:
        errors.append("workflow missing acapella capture guidance")
    if "stem" not in workflow.lower():
        errors.append("workflow missing stem integration")

    if errors:
        print("AI music vocal production workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music vocal production workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
