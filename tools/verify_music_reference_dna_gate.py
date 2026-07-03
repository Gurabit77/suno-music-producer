#!/usr/bin/env python3
"""Verify the AI music reference DNA audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
REFERENCE_AUDIT = ROOT / "tools" / "audit_music_reference_dna.py"
WIKI_REFERENCE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐参考曲风格 DNA 与合法转译工作流.md")
WIKI_PROMPT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Prompt 编译与生成前预检工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
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
        "reference-gate",
        "--title",
        "Reference Gate",
        "--artist-project",
        "Example Test Artist",
        "--use-case",
        "demo",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return tmp_path / "20260625_zh-pop_reference-gate"


def fill_good_reference(project: Path) -> None:
    write(
        project / "02_references" / "rights-and-source-precheck.md",
        """# Rights And Source Precheck

Artist names present: no
Song titles present: no
Allowed action: text-only neutral style DNA, no reference audio upload
""",
    )
    write(
        project / "02_references" / "reference-rights.md",
        """# Reference Rights

Reference set: no third-party reference, original text-only style DNA
Material type: original prompt design
Owner: Example Test Artist
License / permission: self-owned original writing
Can upload audio: no, text-only
Can use for commercial release?: yes, original text only
Contains third-party lyrics?: no
Contains third-party melody/riff/sample?: no
Contains identifiable voice?: no
Allowed action: text-only neutral style DNA, no reference audio upload
Forbidden use: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice
""",
    )
    write(project / "02_references" / "reference-set.md", "# Reference Set\n\nReference set: no protected artist or song reference; original Mandarin pop coordinates only\nDo not copy: melody, lyrics, riff, singer identity, arrangement signature, audio recording\n")
    write(
        project / "02_references" / "style-dna-card.md",
        """# Style DNA Card

Reference set: no third-party reference
Rights status: self-owned original text-only style DNA
Tempo / meter: 78 BPM 4/4
Groove: brushed electronic-acoustic hybrid backbeat with warm bass pocket
Form: short intro, verse, pre, chorus, verse 2, bridge, final chorus, outro
Energy timeline: restrained verse to warm final chorus peak
Hook mechanism: title phrase on downbeat with one long note
Vocal delivery: dry close-mic Mandarin lead, controlled mixed chorus
Arrangement palette: piano, muted electric guitar, warm bass, soft drums, bell motif
Production space: narrow dry verse, wider chorus harmonies, short plate
Do-not-copy list: no reference melody, lyrics, riff, voice, artist identity, song title, sample
Original contribution required: original title phrase, lyrics, topline contour, chord pacing, singer brief
Prompt implication: neutral Mandarin pop ballad style DNA only, no artist or song names, no audio upload
Suno tool choice: Custom Mode text-only
Similarity risk: low
""",
    )
    write(project / "02_references" / "protected-identity-removal.md", "# Protected Identity Removal\n\nDecision: pass\nProtected identity removed: yes\nArtist identity removed: yes\nSong identity removed: yes\nRemaining prompt-safe language: neutral style DNA only\n")
    write(project / "02_references" / "reference-boundary.md", "# Reference Boundary\n\nReference boundary: use only neutral tempo, groove, form, energy, instrument, production, and vocal-delivery abstractions\nAllowed abstraction: tempo, pocket, density curve, dry vocal space, title-hook function\nForbidden use: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, unauthorized audio upload\nOriginal contribution: original title phrase, lyric images, topline map, singer brief, and section structure\nPrompt implication: text-only neutral prompt route with no protected names\nSuno tool choice: Custom Mode text-only\nSimilarity risk: low\n")


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, REFERENCE_AUDIT, WIKI_REFERENCE, WIKI_PROMPT, WIKI_PROJECT, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-reference-gate-") as tmp:
        project = scaffold_project(Path(tmp))

        empty = subprocess.run([sys.executable, str(REFERENCE_AUDIT), "--project-root", str(project), "--strict"], cwd=ROOT, text=True, capture_output=True)
        if empty.returncode == 0:
            errors.append("strict reference audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["reference_set_missing", "allowed_action_missing", "do_not_copy_missing", "style_dna_too_thin"]:
            if term not in empty_text:
                errors.append(f"empty reference audit missing blocker term: {term}")

        fill_good_reference(project)
        good = subprocess.run(
            [sys.executable, str(REFERENCE_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if good.returncode != 0:
            errors.append(f"good reference audit failed: stdout={good.stdout.strip()} stderr={good.stderr.strip()}")
        audit_path = project / "02_references" / "reference-dna-audit.md"
        if not audit_path.exists():
            errors.append("reference audit did not write output")
        else:
            audit_text = audit_path.read_text(encoding="utf-8")
            for term in ["Generated by: tools/audit_music_reference_dna.py", "Decision: pass", "Reference tags:", "Style DNA tags:", "Protected identity removal:", "Similarity blind test:", "Prompt-safe reference route:", "## Reference Design"]:
                if term not in audit_text:
                    errors.append(f"reference audit output missing term: {term}")

        no_overwrite = subprocess.run([sys.executable, str(REFERENCE_AUDIT), "--project-root", str(project), "--write", "--strict"], cwd=ROOT, text=True, capture_output=True)
        if no_overwrite.returncode == 0 or "output exists" not in no_overwrite.stderr:
            errors.append("reference audit should refuse overwrite without --allow-overwrite")

        write(project / "02_references" / "rights-and-source-precheck.md", "# Rights And Source Precheck\n\nArtist names present: yes\nSong titles present: yes\nAllowed action: do something similar\n")
        write(project / "02_references" / "style-dna-card.md", "# Style DNA Card\n\nReference set: Taylor Swift song\nPrompt implication: Taylor Swift style chorus\nSuno tool choice: Audio Upload\nSimilarity risk: high\n")
        write(project / "02_references" / "protected-identity-removal.md", "# Protected Identity Removal\n\nDecision: repair\n")
        bad = subprocess.run([sys.executable, str(REFERENCE_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"], cwd=ROOT, text=True, capture_output=True)
        if bad.returncode == 0:
            errors.append("strict reference audit should reject protected reference route")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["protected_identity_removal_missing", "audio_tool_without_upload_rights", "protected_identity_in_prompt_route", "similarity_risk_high"]:
            if term not in bad_text:
                errors.append(f"bad reference audit missing blocker term: {term}")

    docs = {
        WIKI_REFERENCE: ["tools/audit_music_reference_dna.py", "reference-dna-audit.md"],
        WIKI_PROMPT: ["tools/audit_music_reference_dna.py", "Reference audit"],
        WIKI_PROJECT: ["reference-dna-audit.md", "audit_music_reference_dna.py"],
        LOG: ["AI 音乐 Reference DNA 工具闸门"],
    }
    for path, terms in docs.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{path} missing doc term: {term}")

    if errors:
        print("AI music reference DNA gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music reference DNA gate verification passed.")
    print(f"tool: {REFERENCE_AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
