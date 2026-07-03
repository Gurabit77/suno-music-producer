#!/usr/bin/env python3
"""Verify the conditional chord skeleton transfer gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
AUDIT = ROOT / "tools" / "audit_music_chord_skeleton_transfer.py"
COMPILER = ROOT / "tools" / "compile_music_prompt_package.py"
STATUS = ROOT / "tools" / "audit_music_song_project_status.py"
SKILL = Path("/path/to/codex-skills/suno-music-producer/SKILL.md")
REFERENCE_DOC = Path("/path/to/codex-skills/suno-music-producer/references/reference-upload-generation.md")
CHROME_DOC = Path("/path/to/codex-skills/suno-music-producer/references/chrome-suno-generation.md")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def scaffold(tmp: Path, slug: str) -> Path:
    result = run(
        [
            sys.executable,
            str(SCAFFOLD),
            "--output-dir",
            str(tmp),
            "--date",
            "20260630",
            "--language",
            "zh",
            "--lane",
            "pop",
            "--slug",
            slug,
            "--title",
            "Chord Skeleton Gate",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "demo",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return tmp / f"20260630_zh-pop_{slug}"


def fill_good(project: Path) -> None:
    write(
        project / "02_references" / "reference-rights.md",
        """# Reference Rights

Reference status: self-owned
Material type: original MIDI chord skeleton
Owner: Example Test Artist
License / permission: self-owned original writing
Can upload audio: yes
Commercial use: yes
Allowed action: upload self-owned chord skeleton as Suno Audio Upload / Cover seed
Forbidden use: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, original sample
""",
    )
    write(
        project / "02_references" / "audio-rights-ledger.md",
        """# Audio Rights Ledger

File: 02_references/audio/chord-skeleton.wav
Recorded by: Example Test Artist
Owner: Example Test Artist
Consent: yes
Commercial use: yes
Can upload to AI tool: yes
Can use in release: yes
""",
    )
    write(
        project / "02_references" / "chord-skeleton-transfer.md",
        """# Chord Skeleton Transfer

Reference status: self-owned
Allowed action: upload self-owned chord skeleton as Audio Upload seed
Forbidden use: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, original sample

Source section: original 4-bar loop
Bars: 4
BPM: 66
Key: Db
Progression: Db, Ab, Bbm7, Gb
Harmonic rhythm: one chord per bar
Emotional color: melancholic late-night pop
Bass/root direction: Db to Ab to Bb to Gb root anchors

Tool used: Song Master Pro plus manual DAW verification
Tool confidence: medium; manually corrected chord roots
Manual corrections: removed passing tones and confirmed root motion by ear
Removed: melody fragments, ornamental passing notes, recognizable riff contour
Extended: chord tones into long block chords
Retained: bass roots, chord color, one-chord-per-bar harmonic rhythm
Do-not-copy: no melody, lyrics, riff, voice, sample, original arrangement, or title phrase

Seed file: 02_references/audio/chord-skeleton.wav
Suno route: Audio Upload / Cover approved seed
Style field: [BPM: 66] [Key: Db] [Chord Progression: Db, Ab, Bbm7, Gb], melancholic Mandarin lo-fi pop, ambient piano, soft electric guitar
Exclude: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, muddy bass
Retention target: keep harmonic color and root motion; allow new arrangement and topline
Prompt pairing: style repeats BPM, key, and progression while exclude blocks melody/riff copying
Reverse analysis plan: after generation, inspect output with Song Master Pro for BPM, Key, and root progression, then blind review similarity risk
Similarity risk: low
""",
    )
    write(project / "04_prompt" / "retention-target.md", "# Retention Target\n\nRetention target: keep harmonic color and root motion; allow new arrangement and topline\n")
    write(project / "04_prompt" / "prompt-pairing.md", "# Prompt Pairing\n\nPrompt pairing: style repeats BPM, key, and progression while exclude blocks melody/riff copying\n")
    write(project / "04_prompt" / "style-field-map.md", "# Style Field Map\n\ngenre: melancholic Mandarin lo-fi pop, [BPM: 66], [Key: Db], [Chord Progression: Db, Ab, Bbm7, Gb]\ninstrumentation: ambient piano, soft electric guitar, warm bass, restrained drums\nproduction: late-night dry verse, wider chorus, short plate reverb\nmood: melancholy but warm\n")
    write(project / "04_prompt" / "exclude-negative-aesthetic.md", "# Exclude\n\nExclude: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, muddy bass\n")
    write(project / "04_prompt" / "slider-intent-map.md", "# Slider Intent\n\nModel: v5.5\nWeirdness: 35\nStyle Influence: 75\nAudio Influence: 60\n")


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, AUDIT, COMPILER, STATUS, SKILL, REFERENCE_DOC, CHROME_DOC]:
        if not path.exists():
            errors.append(f"missing required file: {path}")

    with tempfile.TemporaryDirectory(prefix="ai-music-chord-skeleton-") as tmp_name:
        tmp = Path(tmp_name)
        plain = scaffold(tmp, "plain")
        plain_result = run([sys.executable, str(AUDIT), "--project-root", str(plain), "--strict"])
        if plain_result.returncode != 0 or "Decision: not applicable" not in plain_result.stdout:
            errors.append("plain text project should not require chord skeleton gate")

        bad = scaffold(tmp, "bad")
        write(
            bad / "02_references" / "chord-skeleton-transfer.md",
            """# Chord Skeleton Transfer

Reference status: third-party listen-only
Allowed action: upload reference MIDI into Suno Cover
BPM: 66
Key: Db
Progression: Db, Ab, Bbm7, Gb
Suno route: Audio Upload / Cover
""",
        )
        bad_result = run([sys.executable, str(AUDIT), "--project-root", str(bad), "--strict"])
        bad_text = bad_result.stdout + "\n" + bad_result.stderr
        if bad_result.returncode == 0:
            errors.append("bad third-party upload route should fail strict audit")
        for term in ["forbidden_use_missing", "upload_rights_missing", "third_party_upload_not_allowed"]:
            if term not in bad_text:
                errors.append(f"bad audit missing blocker term: {term}")

        good = scaffold(tmp, "good")
        fill_good(good)
        good_result = run([sys.executable, str(AUDIT), "--project-root", str(good), "--write", "--allow-overwrite", "--strict"])
        if good_result.returncode != 0:
            errors.append(f"good chord skeleton audit failed: {good_result.stdout} {good_result.stderr}")
        audit_text = (good / "02_references" / "chord-skeleton-transfer-audit.md").read_text(encoding="utf-8")
        for term in [
            "Generated by: tools/audit_music_chord_skeleton_transfer.py",
            "Decision: pass",
            "## Chord Skeleton Transfer",
            "Rights route:",
            "Skeleton tags:",
            "MIDI simplification:",
            "Suno upload route:",
            "Reverse analysis plan:",
            "Prompt compile handoff:",
        ]:
            if term not in audit_text:
                errors.append(f"good audit output missing term: {term}")

        status_result = run([sys.executable, str(STATUS), "--project-root", str(good), "--write", "--allow-overwrite"])
        if status_result.returncode != 0:
            errors.append(f"status audit failed: {status_result.stdout} {status_result.stderr}")
        board_text = (good / "00_admin" / "song-production-control-board.md").read_text(encoding="utf-8")
        if "chord skeleton transfer" not in board_text.casefold():
            errors.append("status audit evidence table should mention chord skeleton transfer")

        compile_result = run([sys.executable, str(COMPILER), "--project-root", str(good)])
        compile_text = compile_result.stdout + "\n" + compile_result.stderr
        if "Chord skeleton transfer: pass" not in compile_text:
            errors.append("prompt compiler should report chord skeleton transfer pass when route is active")

    docs = {
        SKILL: ["reference_upload_generation", "参考曲上传模式", "确认上传并生成", "chord-skeleton-transfer-audit"],
        REFERENCE_DOC: ["Reference Upload Generation", "audit_music_chord_skeleton_transfer.py", "参考上传确认卡"],
        CHROME_DOC: ["upload_audio_seed", "chord-skeleton-transfer-audit.md", "Audio Upload / Cover seed"],
    }
    for path, terms in docs.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{path} missing term: {term}")

    if errors:
        print("AI music chord skeleton transfer gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music chord skeleton transfer gate verification passed.")
    print(f"tool: {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
