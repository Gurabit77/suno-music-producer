#!/usr/bin/env python3
"""Verify the AI music personalization hygiene gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
TOOL = ROOT / "tools" / "audit_music_personalization_hygiene.py"
COMPILER = ROOT / "tools" / "compile_music_prompt_package.py"
WIKI_PROMPT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Prompt 编译与生成前预检工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
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
            "20260625",
            "--language",
            "zh",
            "--lane",
            "pop",
            "--slug",
            "personalization-hygiene",
            "--title",
            "Personalization Hygiene",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "artist-catalog",
        ]
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip())
    return tmp_path / "20260625_zh-pop_personalization-hygiene"


def routing_active() -> str:
    return """# Persona Voice Model Routing

Human anchor lane: My Taste / Prompt Boost
Voice identity source: none
Persona source: none
Custom Model source: none
Custom model corpus: none
Voice verification: n/a
My Taste state: enabled
My Taste summary: Mandarin night pop, dry close vocal, restrained band texture
Prompt Boost state: enabled
Boosted style text: Mandarin night pop ballad, dry close lead vocal, warm bass, sparse drums, wider chorus
Rights status: no voice/persona/custom model source used
"""


def good_state() -> str:
    return """# Personalization State

Active personalization features: My Taste, Prompt Boost
Account / profile scope: dedicated Example Test Artist profile, not shared with external projects
Source / rights evidence: no external voice/persona/custom model; text-only identity, My Taste preference summary recorded
Catalog fit link: 01_brief/catalog-fit-audit.md Decision: pass
Isolation boundary: project/catalog profile is isolated from external project and experiment accounts
Attribution plan: original vs boosted style text A/B, one variable, blind review before prompt memory
Rollback condition: disable My Taste and Prompt Boost if boosted text weakens title hook, vocal identity, or catalog lane

Voice source: none
Voice verification: n/a
Persona source: none
Persona role: none
Custom Model source: none
Custom Model corpus: none
Custom Model rights: n/a
My Taste state: enabled
My Taste summary: Mandarin night pop, dry close vocal, restrained band texture
Prompt Boost state: enabled
Original style text: Mandarin night pop, dry close vocal, warm bass, sparse live drums
Boosted style text: Mandarin night pop ballad, dry close lead vocal, warm bass, sparse drums, wider chorus
Boost delta: added ballad and wider chorus language; no protected artist identity
Personalization decision: proceed with A/B attribution
"""


def contaminated_state() -> str:
    return """# Personalization State

Active personalization features: My Taste, Prompt Boost
Account / profile scope: unknown account with random likes and other client music
Source / rights evidence: mixed client history
Catalog fit link: none
Isolation boundary: shared taste across other client projects
Attribution plan: secret boost guarantees viral result
Rollback condition: none
My Taste state: enabled
My Taste summary: mixed client taste
Prompt Boost state: enabled
Original style text: pop
Boosted style text: viral magic pop
Boost delta: secret
Personalization decision: proceed
"""


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, TOOL, COMPILER, WIKI_PROMPT, WIKI_PROJECT, WIKI_CATALOG, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-personalization-hygiene-") as tmp:
        project = scaffold_project(Path(tmp))

        text_only = run([sys.executable, str(TOOL), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if text_only.returncode != 0:
            errors.append(f"text-only personalization audit should be not applicable: {text_only.stderr.strip()}")
        text = (project / "04_prompt" / "personalization-hygiene-audit.md").read_text(encoding="utf-8")
        for term in ["Decision: not applicable", "Active personalization features: none", "Prompt compile handoff: not applicable"]:
            if term not in text:
                errors.append(f"text-only personalization audit missing term: {term}")

        write(project / "04_prompt" / "persona-voice-model-routing.md", routing_active())
        missing = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if missing.returncode == 0:
            errors.append("active personalization without hygiene state should fail")
        missing_text = missing.stdout + "\n" + missing.stderr
        for term in ["account_profile_scope_missing", "source_rights_evidence_missing", "prompt_boost_original_style_text_missing"]:
            if term not in missing_text.casefold():
                errors.append(f"missing personalization blocker term: {term}")

        compiler = run([sys.executable, str(COMPILER), "--project-root", str(project), "--strict"])
        if "personalization_hygiene_audit" not in (compiler.stdout + compiler.stderr):
            errors.append("compiler should surface personalization_hygiene_audit when personalization is active without audit")

        write(project / "04_prompt" / "personalization-state.md", good_state())
        ok = run([sys.executable, str(TOOL), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if ok.returncode != 0:
            errors.append(f"personalization hygiene audit should pass: stdout={ok.stdout.strip()} stderr={ok.stderr.strip()}")
        audit_text = (project / "04_prompt" / "personalization-hygiene-audit.md").read_text(encoding="utf-8")
        for term in [
            "Generated by: tools/audit_music_personalization_hygiene.py",
            "Decision: pass",
            "Active personalization features: my_taste, prompt_boost",
            "Personalization hygiene: pass",
            "Prompt compile handoff: pass",
        ]:
            if term not in audit_text:
                errors.append(f"personalization hygiene output missing term: {term}")

        no_overwrite = run([sys.executable, str(TOOL), "--project-root", str(project), "--write"])
        if no_overwrite.returncode != 2:
            errors.append("personalization hygiene audit should refuse overwrite without --allow-overwrite")

        write(project / "04_prompt" / "personalization-state.md", contaminated_state())
        bad = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if bad.returncode == 0:
            errors.append("contaminated personalization state should fail")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["personalization_contamination_risk", "personalization_magic_claim", "attribution_plan_not_testable"]:
            if term not in bad_text:
                errors.append(f"contaminated personalization blocker missing term: {term}")

    compiler_source = COMPILER.read_text(encoding="utf-8")
    for term in ["personalization_hygiene_required_from_docs", "personalization_hygiene_audit", "Personalization hygiene"]:
        if term not in compiler_source:
            errors.append(f"compiler missing personalization integration term: {term}")

    for page, label in [
        (WIKI_PROMPT.read_text(encoding="utf-8"), "prompt"),
        (WIKI_PROJECT.read_text(encoding="utf-8"), "project"),
        (WIKI_CATALOG.read_text(encoding="utf-8"), "catalog"),
    ]:
        for term in ["tools/audit_music_personalization_hygiene.py", "personalization-state.md", "personalization-hygiene-audit.md"]:
            if term not in page:
                errors.append(f"{label} wiki page missing personalization hygiene term: {term}")
    if "AI 音乐 Personalization Hygiene 工具闸门" not in LOG.read_text(encoding="utf-8"):
        errors.append("wiki log missing personalization hygiene gate entry")

    if errors:
        print("AI music personalization hygiene gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music personalization hygiene gate verification passed.")
    print(f"tool: {TOOL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
