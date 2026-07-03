#!/usr/bin/env python3
"""Verify the AI music prompt-specificity budget gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
METHODOLOGY_AUDIT = ROOT / "tools" / "audit_music_methodology_transfer.py"
EXTERNAL_CLAIMS = ROOT / "tools" / "audit_music_external_method_claims.py"
AUDIT = ROOT / "tools" / "audit_music_prompt_specificity_budget.py"
COMPILER = ROOT / "tools" / "compile_music_prompt_package.py"
SOURCE_ROOT = Path("/path/to/suno-prompt-methodology")
WIKI_PROMPT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Prompt 编译与生成前预检工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
WIKI_SINGLE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲制作总控与阶段闸门工作流.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


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
        "specificity-gate",
        "--title",
        "Specificity Gate",
        "--artist-project",
        "Example Test Artist",
        "--use-case",
        "demo",
    ]
    result = run(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return tmp_path / "20260625_zh-pop_specificity-gate"


def fill_methodology_inputs(project: Path) -> None:
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
    external = run([sys.executable, str(EXTERNAL_CLAIMS), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
    if external.returncode != 0:
        raise AssertionError(external.stderr.strip())
    write(
        project / "04_prompt" / "slider-intent-map.md",
        """# Slider Intent Map

Model: Suno current
Weirdness: 28
Style Influence: 70
Audio Influence: 0
Phase: converge
What this tests: style wording specificity while title phrase and singer brief stay fixed
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
    write(
        project / "04_prompt" / "methodology-transfer-plan.md",
        """# Methodology Transfer Plan

Local method sources: /path/to/suno-prompt-methodology/local Suno prompt methodology知识笔记.md; /path/to/suno-prompt-methodology/GitHub/suno-song-creator-plugin/skills/suno-song-creator/references/realism-descriptors.md; /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md
Official control surfaces: Style of Music, Lyrics box, Exclude, Creative Sliders, Persona/Voice/Custom Model/My Taste only if source evidence is active
Community / external candidates: GitHub realism descriptors and video-platform prompt tips remain candidate experiments only; no secret tag is adopted.
Source confidence split: official facts define field behavior; local local Suno prompt methodology supplies workflow/template/checklist; community sources remain A/B hypotheses.
Adopted method: five-part style field, lyrics section context, Exclude as negative aesthetic, slider intent, and one-variable convergence batch.
Song-specific transfer: replace vague realism claims with dry close vocal, brushed drums, warm bass, short plate reverb, title phrase section direction, and controlled width changes.
Model/version rationale: Suno current is used for fixture validation; real releases must recheck current model behavior.
Primary Suno tool route: Custom Mode text-only; no Audio Upload, Voice, Persona, Custom Model, My Taste, or Prompt Boost in this round.
Human-likeness hypothesis: physical recording descriptors plus performance and section direction reduce anonymous AI-demo feel.
Variable discipline: one primary variable per batch; keep title phrase, language, rights boundary, human anchor lane, and slider baseline fixed.
Rejected magic prompt claims: reject guaranteed-hit tags, celebrity-copy prompts, secret codes, and prompt bundles not tied to blind validation.
Protected-identity safeguard: no artist, band, producer, song, album, or identifiable voice names enter generation-facing fields.
Validation metric: blind review must recall the title phrase within 20 seconds and report low AI-flavor red flags.
Drift/rollback condition: if vocals become anonymous, diction twists the title, or the arrangement drifts into glossy EDM, roll back style/exclude/slider inputs.
Source freshness: checked 2026-06-25 against local local Suno prompt methodology folder and current project prompt files.
""",
    )


def fill_specific_inputs(project: Path, *, vague: bool = False) -> None:
    genre = "emotional realistic high quality viral pop" if vague else "Mandarin pop ballad, 78 BPM 4/4, restrained late-night band"
    production = "professional realistic production" if vague else "dry close-mic lead vocal, short plate reverb, narrow verse, wider chorus"
    write(
        project / "04_prompt" / "style-field-map.md",
        f"""# Style Field Map

genre: {genre}
tempo / meter: 78 BPM 4/4
key / mode: minor verse color resolving to major lift in chorus
vocal: clear Mandarin diction, intimate low verse, controlled chorus lift, restrained vibrato
drums / groove: brushed drums, soft backbeat, no trap hats
bass role: warm bass following kick accents, simple pickup before chorus
harmony instruments: close piano voicings, muted electric guitar texture
lead / hook instruments: small bell-like synth motif in intro and outro
production: {production}
mood / energy arc: night-bus loneliness to quiet confession, verse narrow and chorus wider
""",
    )
    write(
        project / "04_prompt" / "lyrics-context-map.md",
        """# Lyrics Context Map

```text
[Song intent: restrained Mandarin confession]
[Prosody notes: keep title vowels stable]
[Intro | short bell motif]
[Verse 1 | intimate vocal | bus-window image]
[Pre-Chorus | fewer words | breath before title]
[Chorus | title phrase on long note]
[Verse 2 | new detail | bass answers vocal]
[Bridge | stripped piano | new perspective]
[Final Chorus | payoff | wider harmony]
[Outro | clean ending]
[End]
```
""",
    )
    write(
        project / "04_prompt" / "exclude-negative-aesthetic.md",
        """# Exclude Negative Aesthetic

Exclude: awkward translated Mandarin, vague inspirational lyrics, forced rhyme, over-autotuned vocal, EDM festival drop
""",
    )
    remove_vague = "realistic only" if vague else "none after replacement; do not use realistic/professional/high quality as positive style targets"
    write(
        project / "04_prompt" / "field-length-and-specificity-budget.md",
        f"""# Field Length And Specificity Budget

Must-hear terms: dry close-mic lead vocal, short plate reverb, brushed drums, warm bass pickup, title phrase on long note
Nice-to-have terms: bell-like intro motif, narrow verse, wider chorus, muted electric guitar answer
Remove vague terms: {remove_vague}
Remove duplicated terms: repeated intimacy tags beyond close/dry vocal
Move to Lyrics context: title phrase landing, section functions, bridge perspective, final chorus payoff
Move to Exclude: awkward translated Mandarin, EDM festival drop, over-autotuned vocal
Move to experiment note: try one alternate chorus width in the next batch only
Field budget decision: ready for audit
Source / rationale: Use /path/to/suno-prompt-methodology and realism-descriptors.md; replace vague prompt words with recording, performance, and section language.
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, METHODOLOGY_AUDIT, EXTERNAL_CLAIMS, AUDIT, COMPILER, SOURCE_ROOT, WIKI_PROMPT, WIKI_PROJECT, WIKI_SINGLE, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-specificity-gate-") as tmp:
        project = scaffold_project(Path(tmp))

        empty = run([sys.executable, str(AUDIT), "--project-root", str(project), "--strict"])
        if empty.returncode == 0:
            errors.append("strict specificity audit should reject an empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["must_hear_terms_sparse", "methodology_transfer_not_ready", "recording_descriptor_missing"]:
            if term not in empty_text:
                errors.append(f"empty specificity audit output missing term: {term}")

        fill_methodology_inputs(project)
        methodology = run([sys.executable, str(METHODOLOGY_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if methodology.returncode != 0:
            errors.append(f"methodology audit failed: {methodology.stderr.strip()}")

        fill_specific_inputs(project)
        passed = run([sys.executable, str(AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if passed.returncode != 0:
            errors.append(f"specificity audit should pass: stdout={passed.stdout.strip()} stderr={passed.stderr.strip()}")
        audit_path = project / "04_prompt" / "prompt-specificity-budget-audit.md"
        if not audit_path.exists():
            errors.append("specificity audit output was not written")
        else:
            text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Decision: pass",
                "Generated by: tools/audit_music_prompt_specificity_budget.py",
                "## Specificity Budget Evidence",
                "Methodology transfer: pass",
                "Style specificity tags:",
                "Recording realism tags:",
                "Performance realism tags:",
                "Section/director tags:",
                "Field budget tags:",
                "Prompt compile handoff: pass",
            ]:
                if term not in text:
                    errors.append(f"specificity audit output missing term: {term}")

        no_overwrite = run([sys.executable, str(AUDIT), "--project-root", str(project), "--write"])
        if no_overwrite.returncode != 2:
            errors.append("specificity audit should refuse overwrite without --allow-overwrite")

        fill_specific_inputs(project, vague=True)
        vague = run([sys.executable, str(AUDIT), "--project-root", str(project), "--strict"])
        if vague.returncode == 0:
            errors.append("specificity audit should reject vague generation-facing style terms")
        vague_text = vague.stdout + "\n" + vague.stderr
        for term in ["vague_terms_unremoved", "recording_descriptor_missing", "professional"]:
            if term not in vague_text:
                errors.append(f"vague specificity audit output missing term: {term}")

        audit_path.unlink(missing_ok=True)
        compile_without_audit = run([sys.executable, str(COMPILER), "--project-root", str(project), "--strict"])
        if "prompt_specificity_budget_audit" not in (compile_without_audit.stdout + compile_without_audit.stderr):
            errors.append("compiler should surface prompt_specificity_budget_audit when the audit is absent/invalid")

    prompt_page = WIKI_PROMPT.read_text(encoding="utf-8")
    project_page = WIKI_PROJECT.read_text(encoding="utf-8")
    single_page = WIKI_SINGLE.read_text(encoding="utf-8")
    log_text = LOG.read_text(encoding="utf-8")
    for term in ["tools/audit_music_prompt_specificity_budget.py", "field-length-and-specificity-budget.md", "prompt-specificity-budget-audit.md", "Prompt specificity"]:
        if term not in prompt_page:
            errors.append(f"prompt workflow missing specificity term: {term}")
    for term in ["field-length-and-specificity-budget.md", "prompt-specificity-budget-audit.md", "prompt-specificity"]:
        if term not in project_page:
            errors.append(f"project template missing specificity term: {term}")
    for term in ["prompt-specificity-gate", "audit_music_prompt_specificity_budget.py", "prompt-specificity-budget-audit.md"]:
        if term not in single_page:
            errors.append(f"single production workflow missing specificity gate term: {term}")
    if "AI 音乐 Prompt Specificity Budget 工具闸门" not in log_text:
        errors.append("wiki log missing prompt specificity budget gate entry")

    if errors:
        print("AI music prompt specificity budget gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music prompt specificity budget gate verification passed.")
    print(f"audit: {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
