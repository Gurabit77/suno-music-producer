#!/usr/bin/env python3
"""Verify the AI music mastering translation and release audio QC notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐母带翻译与发行前音频 QC 工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐母带翻译与发行前音频 QC 资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "postproduction": WIKI / "分析" / "音乐" / "AI 音乐编曲密度与混音后期修作工作流.md",
    "daw": WIKI / "分析" / "音乐" / "AI 音乐 DAW 复刻与真人重录工作流.md",
    "artifact": WIKI / "分析" / "音乐" / "AI 音乐 AI味伪影诊断与修复路由工作流.md",
    "suno": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "release": WIKI / "分析" / "音乐" / "AI 音乐权利发布与平台披露工作流.md",
    "sound_concept": WIKI / "概念" / "音乐" / "声音设计与录音制作基础.md",
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
    "final-master-intent.md",
    "mix-lock-preflight.md",
    "reference-loudness-match.md",
    "release-audio-technical-inspection.md",
    "tools/inspect_music_release_audio.py",
    "loudness-true-peak-report.md",
    "codec-preview.md",
    "translation-listen-matrix.md",
    "mono-phase-low-end-check.md",
    "transient-and-limiter-audit.md",
    "intro-outro-silence-and-tail-check.md",
    "album-balance-and-versioning.md",
    "platform-deliverable-check.md",
    "release-audio-qc-report.md",
    "rollback-if-mastering-hurts.md",
    "LUFS",
    "True Peak",
    "ITU BS.1770",
    "EBU R 128",
    "Spotify",
    "Apple Digital Masters",
    "Sound Check",
    "AAC",
    "ALAC",
    "WAV",
    "FLAC",
    "sample rate",
    "bit depth",
    "codec",
    "normalization",
    "loudness match",
    "mono",
    "phase",
    "low end",
    "limiter",
    "headroom",
]

SOURCE_TERMS = [
    "Spotify",
    "-14 dB LUFS",
    "-1 dB TP",
    "-2 dB",
    "ITU 1770",
    "Apple Digital Masters",
    "24-bit",
    "Apple AAC encoder",
    "clipping",
    "Sound Check",
    "Apple Video and Audio Asset Guide",
    "EBU R 128",
    "-23 LUFS",
    "Loudness Range",
    "Maximum True Peak Level",
    "iZotope",
    "YouTube",
    "stable volume",
    "/path/to/suno-prompt-methodology",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[Suno 真人感歌曲生成工作流]]",
    "[[AI 音乐编曲密度与混音后期修作工作流]]",
    "[[AI 音乐 DAW 复刻与真人重录工作流]]",
    "[[AI 音乐 AI味伪影诊断与修复路由工作流]]",
    "[[AI 音乐盲听评审与版本归档工作流]]",
    "[[AI 音乐权利发布与平台披露工作流]]",
    "[[声音设计与录音制作基础]]",
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

    if compact_len(workflow) < 10000:
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

    workflow_name = "AI 音乐母带翻译与发行前音频 QC 工作流"
    source_name = "AI 音乐母带翻译与发行前音频 QC 资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "postproduction",
        "daw",
        "artifact",
        "suno",
        "release",
        "sound_concept",
        "ai_flavor",
        "framework",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    if "release-candidate" not in workflow:
        errors.append("workflow missing release-candidate gate")
    if "codec preview" not in workflow and "codec-preview.md" not in workflow:
        errors.append("workflow missing codec preview")

    if errors:
        print("AI music mastering QC workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music mastering QC workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
