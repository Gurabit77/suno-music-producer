#!/usr/bin/env python3
"""Verify the AI music methodology-transfer gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
AUDIT = ROOT / "tools" / "audit_music_methodology_transfer.py"
EXTERNAL_CLAIMS = ROOT / "tools" / "audit_music_external_method_claims.py"
COMPILER = ROOT / "tools" / "compile_music_prompt_package.py"
SOURCE_ROOT = Path("/path/to/suno-prompt-methodology")
WIKI_PROMPT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Prompt 编译与生成前预检工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
WIKI_SINGLE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲制作总控与阶段闸门工作流.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scaffold_project(tmp_path: Path) -> Path:
    cmd = [
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
        "method-gate",
        "--title",
        "Method Gate",
        "--artist-project",
        "Example Test Artist",
        "--use-case",
        "demo",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"scaffold failed: {result.stderr.strip()}")
    return tmp_path / "20260625_zh-pop_method-gate"


def fill_external_claim_inputs(project: Path) -> None:
    write(
        project / "04_prompt" / "external-method-claim-ledger.md",
        """# External Method Claim Ledger

| source/platform | url/path | claim | source type | confidence | target control surface | testable variable | adoption status | validation route | risk |
|---|---|---|---|---|---|---|---|---|---|
| Suno official help | /path/to/suno-prompt-methodology/sources/official-clean-md/official-creative-sliders.md | Creative Sliders define Weirdness, Style Influence, and Audio Influence as controllable generation surfaces | official | high | Creative Sliders | Style Influence only | foundation | prompt-iteration-discipline-gate + blind A/B | current model behavior may shift |
| local local Suno prompt methodology | /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md | Only one major variable should change in a reviewable iteration | local methodology | high | batch design | Changed variables | foundation | prompt-iteration-discipline-gate | too rigid for early exploration |
| GitHub prompt references | https://github.com/example/suno-style-tags | realism descriptors can inspire candidate style wording | community/GitHub | medium | Style of Music | recording realism descriptors | candidate experiment only | blind A/B, reverse caption, AI flavor survey | unverified tag lists may become vague |
""",
    )
    result = subprocess.run(
        [sys.executable, str(EXTERNAL_CLAIMS), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip())


def fill_prompt_inputs(project: Path, *, magic_claim: bool = False) -> None:
    write(
        project / "04_prompt" / "slider-intent-map.md",
        """# Slider Intent Map

Model: Suno current
Weirdness: 30
Style Influence: 72
Audio Influence: 0
Phase: converge
What this tests: one primary variable, style wording, while title phrase and vocal brief stay fixed
""",
    )
    write(
        project / "04_prompt" / "persona-voice-model-routing.md",
        """# Persona Voice Model Routing

Human anchor lane: text-only
Voice identity source: none
Persona source: none
Custom Model source: none
Custom model corpus: none
Voice verification: n/a
My Taste state: off
My Taste summary: n/a
Prompt boost state: off
Boosted style text: n/a
Rights status: no voice/persona/custom model source used
""",
    )
    community = (
        "YouTube and GitHub tips are candidate experiments only; no secret tag or guaranteed formula is adopted."
        if not magic_claim
        else "Use a guaranteed viral secret prompt bundle that always makes a hit song."
    )
    write(
        project / "04_prompt" / "methodology-transfer-plan.md",
        f"""# Methodology Transfer Plan

Local method sources: /path/to/suno-prompt-methodology/local Suno prompt methodology知识笔记.md; /path/to/suno-prompt-methodology/templates/suno-prompt-template.md; /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md
Official control surfaces: Style of Music, Lyrics box, Exclude, Creative Sliders, Persona/Voice/Custom Model/My Taste only if source evidence is active
Community / external candidates: {community}
Source confidence split: official facts define field behavior; local local Suno prompt methodology supplies workflow/template/checklist; community/external sources remain candidate hypotheses for A/B testing.
Adopted method: five-part style field, lyrics section context, Exclude as negative aesthetic, slider intent, one-variable convergence batch.
Song-specific transfer: the method becomes a dry close lead vocal, section-tagged lyrics, explicit Exclude against translated Mandarin and glossy EDM drift, and convergent slider settings for this song.
Model/version rationale: Suno current is used for a demo fixture because this gate validates evidence discipline; real releases must recheck current model behavior.
Primary Suno tool route: Custom Mode text-only; no Audio Upload, Voice, Persona, Custom Model, My Taste, or Prompt Boost in this round.
Human-likeness hypothesis: specific title hook, clear diction, restrained performance, and one-variable iteration reduce anonymous AI-demo feel.
Variable discipline: one primary variable per batch; keep title phrase, language, human anchor lane, rights boundary, and slider baseline fixed.
Rejected magic prompt claims: reject guaranteed-hit tags, celebrity-copy prompts, secret codes, and prompt bundles not tied to blind validation.
Protected-identity safeguard: no artist, band, producer, song, album, or identifiable voice names enter generation-facing fields; references must be neutral style DNA.
Validation metric: blind review must recall the title phrase within 20 seconds and report low AI-flavor red flags.
Drift/rollback condition: if vocals become anonymous, diction twists the title, or arrangement drifts into glossy EDM, roll back style/exclude/slider inputs.
Source freshness: checked 2026-06-25 against local local Suno prompt methodology folder and current project prompt files.
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, AUDIT, EXTERNAL_CLAIMS, COMPILER, SOURCE_ROOT, WIKI_PROMPT, WIKI_PROJECT, WIKI_SINGLE, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-methodology-gate-") as tmp:
        project = scaffold_project(Path(tmp))

        empty = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if empty.returncode == 0:
            errors.append("strict methodology audit should reject an empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["local_method_sources_missing", "source_confidence_split_missing", "model_rationale_missing"]:
            if term not in empty_text:
                errors.append(f"empty methodology audit output missing term: {term}")

        fill_external_claim_inputs(project)
        fill_prompt_inputs(project)
        passed = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if passed.returncode != 0:
            errors.append(f"methodology audit should pass: stdout={passed.stdout.strip()} stderr={passed.stderr.strip()}")
        audit_path = project / "04_prompt" / "methodology-transfer-audit.md"
        if not audit_path.exists():
            errors.append("methodology audit output was not written")
        else:
            text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Decision: pass",
                "Generated by: tools/audit_music_methodology_transfer.py",
                "Local source status: ready",
                "External method claims: pass",
                "Source confidence split:",
                "Official control surfaces:",
                "Model/version rationale:",
                "Primary tool route:",
                "Human-likeness transfer:",
                "Variable discipline:",
                "Anti-magic safeguards:",
            ]:
                if term not in text:
                    errors.append(f"methodology audit output missing term: {term}")

        no_overwrite = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if no_overwrite.returncode != 2:
            errors.append("methodology audit should refuse overwrite without --allow-overwrite")

        fill_prompt_inputs(project, magic_claim=True)
        magic = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if magic.returncode == 0:
            errors.append("methodology audit should reject magic/guaranteed community claims")
        magic_text = magic.stdout + "\n" + magic.stderr
        for term in ["community_magic_claim", "guaranteed", "experiment hypotheses"]:
            if term not in magic_text:
                errors.append(f"magic-claim audit output missing term: {term}")

        audit_path.unlink(missing_ok=True)
        compile_without_clean_audit = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if "methodology_transfer_audit" not in (compile_without_clean_audit.stdout + compile_without_clean_audit.stderr):
            errors.append("compiler should surface methodology_transfer_audit when the audit is absent/invalid")

    prompt_page = WIKI_PROMPT.read_text(encoding="utf-8")
    project_page = WIKI_PROJECT.read_text(encoding="utf-8")
    single_page = WIKI_SINGLE.read_text(encoding="utf-8")
    log_text = LOG.read_text(encoding="utf-8")
    for term in ["tools/audit_music_external_method_claims.py", "external-method-claim-ledger.md", "external-method-claim-audit.md", "tools/audit_music_methodology_transfer.py", "methodology-transfer-plan.md", "methodology-transfer-audit.md", "Methodology transfer"]:
        if term not in prompt_page:
            errors.append(f"prompt workflow missing methodology term: {term}")
    for term in ["external-method-claim-ledger.md", "external-method-claim-audit.md", "methodology-transfer-plan.md", "methodology-transfer-audit.md", "prompt-methodology"]:
        if term not in project_page:
            errors.append(f"project template missing methodology term: {term}")
    for term in ["methodology-transfer-gate", "audit_music_external_method_claims.py", "external-method-claim-audit.md", "audit_music_methodology_transfer.py", "methodology-transfer-audit.md"]:
        if term not in single_page:
            errors.append(f"single production workflow missing methodology gate term: {term}")
    for term in ["AI 音乐 External Method Claim 工具闸门", "AI 音乐 Methodology Transfer 工具闸门"]:
        if term not in log_text:
            errors.append(f"wiki log missing methodology transfer gate entry: {term}")

    if errors:
        print("AI music methodology transfer gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music methodology transfer gate verification passed.")
    print(f"audit: {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
