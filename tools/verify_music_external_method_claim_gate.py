#!/usr/bin/env python3
"""Verify the external method claim audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
TOOL = ROOT / "tools" / "audit_music_external_method_claims.py"
METHODOLOGY = ROOT / "tools" / "audit_music_methodology_transfer.py"
WIKI_PROMPT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Prompt 编译与生成前预检工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
WIKI_SINGLE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲制作总控与阶段闸门工作流.md")
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
            "external-claims",
            "--title",
            "External Claims",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "demo",
        ]
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip())
    return tmp_path / "20260625_zh-pop_external-claims"


def good_claim_ledger() -> str:
    return """# External Method Claim Ledger

| source/platform | url/path | claim | source type | confidence | target control surface | testable variable | adoption status | validation route | risk |
|---|---|---|---|---|---|---|---|---|---|
| Suno official help | /path/to/suno-prompt-methodology/sources/official-clean-md/official-creative-sliders.md | Creative Sliders define Weirdness, Style Influence, and Audio Influence as controllable generation surfaces | official | high | Creative Sliders | Style Influence only | foundation | prompt-iteration-discipline-gate + blind A/B | current model behavior may shift |
| local local Suno prompt methodology | /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md | Only one major variable should change in a reviewable iteration | local methodology | high | batch design | Changed variables | foundation | prompt-iteration-discipline-gate | too rigid for early exploration |
| GitHub prompt references | https://github.com/example/suno-style-tags | realism descriptors can inspire candidate style wording | community/GitHub | medium | Style of Music | recording realism descriptors | candidate experiment only | blind A/B, reverse caption, AI flavor survey | unverified tag lists may become vague |
| YouTube tutorial | https://www.youtube.com/watch?v=example | adding concrete performance language may improve vocal believability | community/video | low | Lyrics context | vocal performance language | candidate experiment only | one-variable batch, blind vocal review | creator claim may be anecdotal |
"""


def bad_magic_ledger() -> str:
    return """# External Method Claim Ledger

| source/platform | url/path | claim | source type | confidence | target control surface | testable variable | adoption status | validation route | risk |
|---|---|---|---|---|---|---|---|---|---|
| Douyin tutorial | https://www.douyin.com/video/example | secret prompt guarantees a viral hit song | community/video | low | Style of Music | secret tag bundle | adopted rule | none | may overfit platform hype |
"""


def methodology_plan(project: Path) -> str:
    return f"""# Methodology Transfer Plan

Local method sources: /path/to/suno-prompt-methodology/local Suno prompt methodology知识笔记.md; /path/to/suno-prompt-methodology/templates/suno-prompt-template.md; /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md
Official control surfaces: Style of Music, Lyrics box, Exclude, Creative Sliders, Voice / Persona / Custom Model / My Taste only if source evidence is active
Community / external candidates: GitHub and YouTube tips are candidate experiments only; no secret tag or guaranteed formula is adopted.
Source confidence split: official facts define field behavior; local local Suno prompt methodology supplies workflow/template/checklist; community/external sources remain candidate hypotheses for A/B testing.
Adopted method: source-ranked method claims only; community tips stay in experiment matrix.
Song-specific transfer: dry close vocal, section-tagged lyrics, explicit Exclude, and one-variable Style Influence batch for {project.name}.
Model/version rationale: Suno current is used for a fixture; real releases recheck model behavior.
Primary Suno tool route: Custom Mode text-only.
Human-likeness hypothesis: concrete title hook, restrained vocal direction, and one-variable iteration reduce AI-demo feel.
Variable discipline: one primary variable per batch; keep title phrase, language, human anchor lane, and rights boundary fixed.
Rejected magic prompt claims: reject guaranteed-hit tags, celebrity-copy prompts, secret codes, and prompt bundles not tied to blind validation.
Protected-identity safeguard: no artist, band, producer, song, album, or identifiable voice names enter generation-facing fields.
Validation metric: blind review recalls title phrase and reports low AI-flavor red flags.
Drift/rollback condition: roll back if vocal diction twists title or arrangement drifts into glossy EDM.
Source freshness: checked 2026-06-25 against local local Suno prompt methodology and current web/community candidates.
"""


def prompt_inputs(project: Path) -> None:
    write(project / "04_prompt" / "methodology-transfer-plan.md", methodology_plan(project))
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
My Taste state: off
Prompt boost state: off
Rights status: no voice/persona/custom model source used
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, TOOL, METHODOLOGY, WIKI_PROMPT, WIKI_PROJECT, WIKI_SINGLE, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-external-method-claims-") as tmp:
        project = scaffold_project(Path(tmp))

        empty = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if empty.returncode == 0:
            errors.append("strict external method claim audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["claim_field_missing", "claim"]:
            if term not in empty_text:
                errors.append(f"empty external claim audit missing term: {term}")

        write(project / "04_prompt" / "external-method-claim-ledger.md", good_claim_ledger())
        ok = run([sys.executable, str(TOOL), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if ok.returncode != 0:
            errors.append(f"external method claim audit should pass: stdout={ok.stdout.strip()} stderr={ok.stderr.strip()}")
        audit_path = project / "04_prompt" / "external-method-claim-audit.md"
        if not audit_path.exists():
            errors.append("missing external-method-claim-audit.md output")
        else:
            text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/audit_music_external_method_claims.py",
                "Decision: pass",
                "## External Method Claim Evidence",
                "External method claims: 4",
                "Official/local foundations: 2",
                "Community candidates: 2",
                "Candidate-only handoff: pass",
                "Methodology transfer handoff: pass",
            ]:
                if term not in text:
                    errors.append(f"external claim audit output missing term: {term}")

        no_overwrite = run([sys.executable, str(TOOL), "--project-root", str(project), "--write"])
        if no_overwrite.returncode != 2:
            errors.append("external method claim audit should refuse overwrite without --allow-overwrite")

        write(project / "04_prompt" / "external-method-claim-ledger.md", bad_magic_ledger())
        magic = run([sys.executable, str(TOOL), "--project-root", str(project), "--strict"])
        if magic.returncode == 0:
            errors.append("external method claim audit should reject magic/guaranteed claims")
        magic_text = magic.stdout + "\n" + magic.stderr
        for term in ["magic_claim_not_allowed", "community_claim_adopted_as_rule"]:
            if term not in magic_text:
                errors.append(f"magic claim audit missing blocker: {term}")

        write(project / "04_prompt" / "external-method-claim-ledger.md", good_claim_ledger())
        write(project / "04_prompt" / "external-method-claim-audit.md", "# External Method Claim Audit\n\nDecision: pass\n")
        prompt_inputs(project)
        methodology = run([sys.executable, str(METHODOLOGY), "--project-root", str(project), "--strict"])
        if methodology.returncode == 0:
            errors.append("methodology transfer should reject hand-written external method claim audit")
        methodology_text = methodology.stdout + "\n" + methodology.stderr
        for term in ["external_method_claim_audit_not_passed", "tools/audit_music_external_method_claims.py"]:
            if term not in methodology_text:
                errors.append(f"methodology blocker missing external claim term: {term}")

    for page, label in [
        (WIKI_PROMPT.read_text(encoding="utf-8"), "prompt"),
        (WIKI_PROJECT.read_text(encoding="utf-8"), "project"),
        (WIKI_SINGLE.read_text(encoding="utf-8"), "single"),
    ]:
        for term in ["tools/audit_music_external_method_claims.py", "external-method-claim-ledger.md", "external-method-claim-audit.md"]:
            if term not in page:
                errors.append(f"{label} wiki page missing external method claim term: {term}")
    log_text = LOG.read_text(encoding="utf-8")
    if "AI 音乐 External Method Claim 工具闸门" not in log_text:
        errors.append("wiki log missing external method claim gate entry")

    if errors:
        print("AI music external method claim gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music external method claim gate verification passed.")
    print(f"tool: {TOOL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
