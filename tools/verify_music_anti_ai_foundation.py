#!/usr/bin/env python3
"""Verify the anti-AI-flavor music foundation notes exist and are substantial."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")

FILES = {
    "source": VAULT / "wiki/来源/外部资料/音乐/Suno 官方创作功能资料组.md",
    "concept": VAULT / "wiki/概念/音乐/AI 音乐去 AI 味核心控制面.md",
    "analysis": VAULT / "wiki/分析/音乐/Suno 真人感歌曲生成工作流.md",
    "concept_index": VAULT / "wiki/概念/音乐/index.md",
    "analysis_index": VAULT / "wiki/分析/音乐/index.md",
    "source_index": VAULT / "wiki/来源/外部资料/音乐/index.md",
    "map": VAULT / "wiki/地图/音乐知识地图.md",
    "root_index": VAULT / "wiki/index.md",
    "log": VAULT / "wiki/log.md",
}

REQUIRED_TERMS = [
    "Custom Mode",
    "Lyrics",
    "Style",
    "Exclude",
    "Creative Sliders",
    "Personas",
    "Voices",
    "Custom Models",
    "Studio",
    "Add Vocals",
    "歌词",
    "旋律",
    "和声",
    "律动",
    "声线",
    "编曲",
    "制作",
    "迭代",
    "盲听评分",
]


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def main() -> int:
    errors: list[str] = []

    for name, path in FILES.items():
        if not path.exists():
            errors.append(f"missing {name}: {path}")

    if errors:
        print("Anti-AI foundation verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    source = FILES["source"].read_text(encoding="utf-8")
    concept = FILES["concept"].read_text(encoding="utf-8")
    analysis = FILES["analysis"].read_text(encoding="utf-8")

    if compact_len(source) < 1200:
        errors.append("Suno source page is too thin")
    if compact_len(concept) < 3200:
        errors.append("anti-AI-flavor concept page is too thin")
    if compact_len(analysis) < 3600:
        errors.append("Suno human-feel workflow analysis page is too thin")

    combined = "\n".join([source, concept, analysis])
    missing_terms = [term for term in REQUIRED_TERMS if term not in combined]
    if missing_terms:
        errors.append("missing required method terms: " + ", ".join(missing_terms))

    for key in ["concept_index", "analysis_index", "source_index", "map", "root_index", "log"]:
        text = FILES[key].read_text(encoding="utf-8")
        for title in ["AI 音乐去 AI 味核心控制面", "Suno 真人感歌曲生成工作流"]:
            if title not in text and key not in {"source_index"}:
                errors.append(f"{FILES[key]} missing {title}")
        if key == "source_index" and "Suno 官方创作功能资料组" not in text:
            errors.append(f"{FILES[key]} missing Suno source entry")

    if errors:
        print("Anti-AI foundation verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Anti-AI foundation verification passed.")
    print(f"- source chars: {compact_len(source)}")
    print(f"- concept chars: {compact_len(concept)}")
    print(f"- analysis chars: {compact_len(analysis)}")
    print(f"- vault: {VAULT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
