#!/usr/bin/env python3
"""Verify the AI music provider routing workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐多模型工具链与 Provider 路由工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐多模型工具链与 Provider 路由资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "single_gate": WIKI / "分析" / "音乐" / "AI 音乐单曲制作总控与阶段闸门工作流.md",
    "suno": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "codex_selection": WIKI / "分析" / "模型与工具对比" / "Codex AI 音乐生成工作流与 Suno 接入选型.md",
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
    "provider-routing-brief.md",
    "provider-capability-matrix.md",
    "provider-rights-and-risk-check.md",
    "provider-parameter-map.md",
    "provider-batch-plan.md",
    "provider-result-ledger.md",
    "cross-provider-blind-review.md",
    "provider-handoff-decision.md",
    "provider-memory-bank.md",
    "Suno",
    "ElevenLabs",
    "Lyria",
    "Udio",
    "Stable Audio",
    "ACE-Step",
    "DAW",
    "full song",
    "loop",
    "instrumental",
    "SFX",
    "stems",
    "API",
    "local",
    "Finetune",
    "LoRA",
    "Voice",
    "Persona",
    "Custom Model",
    "seed",
    "force_instrumental",
    "timed lyrics",
    "inpainting",
    "Continuation",
    "provider-rights-notes.md",
    "release-candidate-rights-gate.md",
]

SOURCE_TERMS = [
    "Suno",
    "Eleven Music",
    "Music API",
    "Music Finetunes",
    "duration",
    "seed",
    "force_instrumental",
    "Google Lyria",
    "Lyria 3 Clip",
    "Lyria 3 Pro",
    "44.1 kHz",
    "timed lyrics",
    "Stable Audio 3",
    "Stems & Solo Instruments",
    "Audio Samples & SFX",
    "Init Audio",
    "Inpainting",
    "Continuation",
    "ACE-Step 1.5",
    "50+ languages",
    "vocal-to-BGM",
    "Udio",
    "Extend",
    "Inpaint",
    "Session",
    "Remix",
    "Style",
    "/path/to/suno-prompt-methodology",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[AI 音乐单曲制作总控与阶段闸门工作流]]",
    "[[Suno 真人感歌曲生成工作流]]",
    "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]",
    "[[AI 音乐人类音频草稿到成品工作流]]",
    "[[AI 音乐 DAW 复刻与真人重录工作流]]",
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

    if compact_len(workflow) < 9000:
        errors.append("workflow page is too thin")
    if compact_len(source) < 7500:
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

    workflow_name = "AI 音乐多模型工具链与 Provider 路由工作流"
    source_name = "AI 音乐多模型工具链与 Provider 路由资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "single_gate",
        "suno",
        "codex_selection",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    if "不要问“哪个模型最强”" not in workflow:
        errors.append("workflow missing first-principles routing principle")
    if "非官方" not in workflow or "rights" not in workflow:
        errors.append("workflow missing API/rights risk framing")

    if errors:
        print("AI music provider routing workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music provider routing workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
