#!/usr/bin/env python3
"""Verify the AI music release-listener evidence gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
TOOL = ROOT / "tools" / "audit_music_release_listener_evidence.py"
WIKI_EXTERNAL = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐外部听众反馈与发行数据闭环工作流.md")
WIKI_RIGHTS = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐权利发布与平台披露工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
WIKI_STATUS = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲制作总控与阶段闸门工作流.md")
WIKI_CATALOG = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐艺人身份与 Catalog Bible 工作流.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scaffold_project(tmp_path: Path) -> Path:
    result = run(
        [
            sys.executable,
            str(SCAFFOLD),
            "--output-dir",
            str(tmp_path),
            "--date",
            "20260624",
            "--language",
            "zh",
            "--lane",
            "pop",
            "--slug",
            "night-bus",
            "--title",
            "Night Bus Confession",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "release-single",
        ]
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip())
    return tmp_path / "20260624_zh-pop_night-bus"


def write_passing_listener_files(project: Path) -> None:
    write(
        project / "06_review" / "external-listener-panel.md",
        """# External Listener Panel

Target audience: late-night Mandarin pop listeners
Panel size: 8
Blind condition: prompt, provider, and creator preference hidden
Playback context: phone speaker and headphones
AI flavor red flags: none
Release listener verdict: pass
Decision: pass
""",
    )
    write(
        project / "06_review" / "first-20-second-test.md",
        """# First 20 Second Test

Skip risk: low
First 20 second decision: continue listening
Synthetic / fake feeling: none
Decision: pass
""",
    )
    write(
        project / "06_review" / "hook-memory-test.md",
        """# Hook Memory Test

Hook recalled: yes
Title phrase remembered: 末班车还亮着
Melody contour remembered: rising title phrase then fall
Memory result: pass
Decision: pass
""",
    )
    write(
        project / "06_review" / "ai-flavor-red-flag-survey.md",
        """# AI Flavor Red Flag Survey

AI flavor red flags: none
AI flavor release verdict: pass
Severity 0-3: 0
Decision: pass
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, TOOL, WIKI_EXTERNAL, WIKI_RIGHTS, WIKI_PROJECT, WIKI_STATUS, WIKI_CATALOG, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-release-listener-") as tmp:
        project = scaffold_project(Path(tmp))
        empty = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if empty.returncode == 0:
            errors.append("empty listener evidence should fail in strict mode")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["panel_size_missing", "first20_skip_risk_missing", "hook_recall_missing", "ai_flavor_flags_missing"]:
            if term not in empty_text:
                errors.append(f"empty listener blocker missing term: {term}")

        write_passing_listener_files(project)
        passing = run([sys.executable, str(TOOL), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if passing.returncode != 0:
            errors.append(f"passing listener evidence should pass: {passing.stderr.strip()}")
        audit = (project / "06_review" / "release-listener-evidence-audit.md").read_text(encoding="utf-8")
        for term in [
            "Decision: pass",
            "## Release Listener Evidence",
            "Panel tags:",
            "First 20 second tags:",
            "Hook memory tags:",
            "AI flavor tags:",
            "Release gate handoff: ready",
            "tools/audit_music_release_listener_evidence.py",
        ]:
            if term not in audit:
                errors.append(f"passing listener audit missing term: {term}")

        no_overwrite = run([sys.executable, str(TOOL), "--project-root", str(project), "--write", "--strict"])
        if no_overwrite.returncode != 2:
            errors.append("release listener evidence tool should refuse overwrite without --allow-overwrite")

        write(
            project / "06_review" / "hook-memory-test.md",
            """# Hook Memory Test

Hook recalled: no
Title phrase remembered:
Memory result: fail
Decision: fail
""",
        )
        hook_fail = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if hook_fail.returncode == 0:
            errors.append("failed hook memory should block strict mode")
        hook_text = hook_fail.stdout + "\n" + hook_fail.stderr
        for term in ["hook_not_recalled", "hook_memory_no_trace"]:
            if term not in hook_text:
                errors.append(f"hook failure blocker missing term: {term}")

        write_passing_listener_files(project)
        write(
            project / "06_review" / "ai-flavor-red-flag-survey.md",
            """# AI Flavor Red Flag Survey

AI flavor red flags: obvious vocal tail artifact
AI flavor release verdict: fail
Severity 0-3: 2
Decision: fail
""",
        )
        ai_fail = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if ai_fail.returncode == 0:
            errors.append("AI flavor red flags should block strict mode")
        ai_text = ai_fail.stdout + "\n" + ai_fail.stderr
        for term in ["ai_flavor_flags_not_low", "ai_flavor_verdict_not_positive", "ai_flavor_severity_too_high"]:
            if term not in ai_text:
                errors.append(f"AI flavor blocker missing term: {term}")

    for page, terms in [
        (WIKI_EXTERNAL, ["tools/audit_music_release_listener_evidence.py", "release-listener-evidence-audit.md", "Release gate handoff"]),
        (WIKI_RIGHTS, ["tools/audit_music_release_listener_evidence.py", "release-listener-evidence-audit.md"]),
        (WIKI_PROJECT, ["tools/audit_music_release_listener_evidence.py", "release-listener-evidence-audit.md"]),
        (WIKI_STATUS, ["release-listener-gate", "tools/audit_music_release_listener_evidence.py", "release-listener-evidence-audit.md"]),
        (WIKI_CATALOG, ["tools/audit_music_release_listener_evidence.py", "release-listener-evidence-audit.md"]),
    ]:
        text = page.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{page.name} missing term: {term}")

    log_text = LOG.read_text(encoding="utf-8")
    if "AI 音乐 Release Listener Evidence 工具闸门" not in log_text:
        errors.append("wiki log missing Release Listener Evidence tool entry")

    if errors:
        print("AI music release listener evidence gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music release listener evidence gate verification passed.")
    print(f"tool: {TOOL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
