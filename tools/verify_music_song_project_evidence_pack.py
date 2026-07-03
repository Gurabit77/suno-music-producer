#!/usr/bin/env python3
"""Verify the AI music single-song project folder and evidence-pack template."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐单曲项目文件夹与证据包模板.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "music_map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "suno": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "single_gate": WIKI / "分析" / "音乐" / "AI 音乐单曲制作总控与阶段闸门工作流.md",
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
    "song-project-root/",
    "00_admin/",
    "01_brief/",
    "02_references/",
    "03_writing/",
    "04_prompt/",
    "05_generations/",
    "06_review/",
    "07_repair/",
    "08_stems-daw/",
    "09_vocal/",
    "10_mix-master/",
    "11_release/",
    "12_catalog-memory/",
    "song-production-control-board.md",
    "prompt-package-v001.md",
    "prompt-preflight-review.md",
    "take-ledger.md",
    "blind-review.md",
    "artifact-severity-score.md",
    "session-pack.md",
    "release-audio-technical-inspection.md",
    "release-audio-qc-report.md",
    "release-candidate-rights-gate.md",
    "catalog-memory-update.md",
    "postmortem-and-prompt-memory.md",
    "suno-prompt-template.md",
    "suno-prompt-review-checklist.md",
    "immutable_inputs.md",
    "mutable_working.md",
    "release_candidate/",
    "evidence-pack/",
    "do-not-publish-if",
    "AI 味",
    "真人感",
    "rights",
    "Catalog Bible",
]

REQUIRED_LINKS = [
    "[[AI 音乐单曲制作总控与阶段闸门工作流]]",
    "[[Suno 真人感歌曲生成工作流]]",
    "[[AI 音乐 Prompt 编译与生成前预检工作流]]",
    "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]",
    "[[AI 音乐盲听评审与版本归档工作流]]",
    "[[AI 音乐 AI味伪影诊断与修复路由工作流]]",
    "[[AI 音乐 DAW 复刻与真人重录工作流]]",
    "[[AI 音乐人声录音与 Vocal Production 工作流]]",
    "[[AI 音乐母带翻译与发行前音频 QC 工作流]]",
    "[[AI 音乐权利发布与平台披露工作流]]",
    "[[AI 音乐艺人身份与 Catalog Bible 工作流]]",
    "[[标杆艺人逐曲拆解与 AI 音乐转译学习路径]]",
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
    if not has_type(workflow, "analysis"):
        errors.append("workflow page must have type: analysis")

    if compact_len(workflow) < 12000:
        errors.append("workflow page is too thin")

    missing_terms = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_terms:
        errors.append("workflow missing terms: " + ", ".join(missing_terms))

    missing_links = [link for link in REQUIRED_LINKS if link not in workflow]
    if missing_links:
        errors.append("workflow missing links: " + ", ".join(missing_links))

    workflow_name = "AI 音乐单曲项目文件夹与证据包模板"
    for key in ["analysis_index", "music_map", "root_index", "suno", "single_gate", "blind_review", "log"]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    single_gate = read(PAGES["single_gate"])
    if "song-project-root/" not in single_gate or "12 文件最小包" not in single_gate:
        errors.append("single production gate missing project folder/evidence pack integration")

    suno = read(PAGES["suno"])
    if "song-project-root/" not in suno or "release-candidate-rights-gate.md" not in suno:
        errors.append("Suno workflow missing project folder evidence integration")

    blind_review = read(PAGES["blind_review"])
    if "06_review/" not in blind_review or "05_generations/take-ledger.md" not in blind_review:
        errors.append("blind review workflow missing folder routing integration")

    if errors:
        print("AI music song project evidence-pack verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music song project evidence-pack verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
