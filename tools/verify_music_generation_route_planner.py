#!/usr/bin/env python3
"""Verify the effect-first Suno generation route planner."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
PLANNER = ROOT / "tools" / "plan_music_generation_route.py"
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
CHORD_AUDIT = ROOT / "tools" / "audit_music_chord_skeleton_transfer.py"
README = ROOT / "README.md"
SKILL = Path("/path/to/codex-skills/suno-music-producer/SKILL.md")
REFERENCE_DOC = Path("/path/to/codex-skills/suno-music-producer/references/reference-upload-generation.md")
LOCAL_DOC = Path("/path/to/codex-skills/suno-music-producer/references/local-ai-music-project.md")


def run(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
            "Route Planner Test",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "demo",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return tmp / f"20260630_zh-pop_{slug}"


def fill_ready_reference_upload(project: Path) -> None:
    write(
        project / "02_references" / "reference-rights.md",
        """# Reference Rights

Reference status: self-owned
Material type: original chord skeleton
Owner: Example Test Artist
Can upload audio: yes
Commercial use: yes
Allowed action: upload self-owned chord skeleton as Suno Audio Upload seed
Forbidden use: copied melody, copied lyrics, recognizable riff, artist imitation, reference voice, original sample
""",
    )
    write(
        project / "02_references" / "audio-rights-ledger.md",
        """# Audio Rights Ledger

File: 02_references/audio/chord-skeleton.wav
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
Tool confidence: medium; manually corrected roots
Manual corrections: removed passing tones and confirmed root motion
Removed: melody fragments, ornamental passing notes, recognizable riff contour
Extended: chord tones into long block chords
Retained: bass roots, chord color, one-chord-per-bar harmonic rhythm
Do-not-copy: no melody, lyrics, riff, voice, sample, original arrangement, or title phrase
Seed file: 02_references/audio/chord-skeleton.wav
Suno route: Audio Upload / Cover approved seed
Style field: [BPM: 66] [Key: Db] [Chord Progression: Db, Ab, Bbm7, Gb], melancholic Mandarin lo-fi pop, ambient piano
Exclude: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, muddy bass
Retention target: keep harmonic color and root motion; allow new arrangement and topline
Prompt pairing: style repeats BPM, key, and progression while exclude blocks melody/riff copying
Reverse analysis plan: inspect output for BPM, Key, root progression, and similarity risk
Similarity risk: low
""",
    )
    write(project / "04_prompt" / "retention-target.md", "# Retention Target\n\nRetention target: keep harmonic color and root motion; allow new arrangement and topline\n")
    write(project / "04_prompt" / "prompt-pairing.md", "# Prompt Pairing\n\nPrompt pairing: style repeats BPM, key, and progression while exclude blocks melody/riff copying\n")
    write(project / "04_prompt" / "style-field-map.md", "# Style Field Map\n\ngenre: melancholic Mandarin lo-fi pop, [BPM: 66], [Key: Db], [Chord Progression: Db, Ab, Bbm7, Gb]\ninstrumentation: ambient piano, soft electric guitar\nproduction: late-night dry verse, wider chorus\nmood: melancholy but warm\n")
    write(project / "04_prompt" / "exclude-negative-aesthetic.md", "# Exclude\n\nExclude: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, muddy bass\n")
    write(project / "04_prompt" / "slider-intent-map.md", "# Slider Intent\n\nAudio Influence: 60\nStyle Influence: 75\nWeirdness: 35\n")


def main() -> int:
    errors: list[str] = []

    for path in [PLANNER, SCAFFOLD, CHORD_AUDIT, README, SKILL, REFERENCE_DOC, LOCAL_DOC]:
        if not path.exists():
            errors.append(f"missing required file: {path}")

    ordinary = run([sys.executable, str(PLANNER), "--brief", "做一首华语流行歌，夜晚、钢琴、女声，直接给 Suno prompt"])
    if ordinary.returncode != 0 or "Decision: ordinary_generation" not in ordinary.stdout:
        errors.append("ordinary brief should route to ordinary_generation")

    unsafe = run([sys.executable, str(PLANNER), "--brief", "上传一首第三方商业发行曲作为参考曲，用 Cover 做一首很像的歌，但没有授权"])
    if unsafe.returncode != 0:
        errors.append(f"unsafe brief planner failed: {unsafe.stderr}")
    for term in ["blocked_reference_upload_use_listen_only_dna", "do not upload", "listen-only"]:
        if term not in unsafe.stdout:
            errors.append(f"unsafe reference route missing term: {term}")

    with tempfile.TemporaryDirectory(prefix="ai-music-route-planner-") as tmp_name:
        tmp = Path(tmp_name)
        plain = scaffold(tmp, "plain")
        plain_result = run([sys.executable, str(PLANNER), "--project-root", str(plain)])
        if plain_result.returncode != 0 or "Decision: ordinary_generation" not in plain_result.stdout:
            errors.append("plain scaffold should route to ordinary_generation")
        if "chord skeleton transfer" in plain_result.stdout.casefold() and "Decision: ordinary_generation" not in plain_result.stdout:
            errors.append("plain scaffold should not expose chord skeleton blockers")

        ready = scaffold(tmp, "ready")
        fill_ready_reference_upload(ready)
        audit = run([sys.executable, str(CHORD_AUDIT), "--project-root", str(ready), "--write", "--allow-overwrite", "--strict"])
        if audit.returncode != 0:
            errors.append(f"ready chord audit failed: {audit.stdout} {audit.stderr}")
        ready_result = run([sys.executable, str(PLANNER), "--project-root", str(ready), "--write", "--allow-overwrite"])
        if ready_result.returncode != 0:
            errors.append(f"ready planner failed: {ready_result.stdout} {ready_result.stderr}")
        output = (ready / "00_admin" / "generation-route-plan.md").read_text(encoding="utf-8")
        for term in [
            "Generated by: tools/plan_music_generation_route.py",
            "Decision: reference_upload_generation_ready",
            "确认上传并生成",
            "Effect-first check",
        ]:
            if term not in output:
                errors.append(f"ready route plan missing term: {term}")

    docs = {
        README: ["plan_music_generation_route.py", "00_admin/generation-route-plan.md"],
        SKILL: ["Route Planner", "plan_music_generation_route.py", "blocked_reference_upload_use_listen_only_dna"],
        REFERENCE_DOC: ["First Step: Route Planning", "plan_music_generation_route.py"],
        LOCAL_DOC: ["00_admin/generation-route-plan.md", "plan_music_generation_route.py"],
    }
    for path, terms in docs.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{path} missing term: {term}")

    if errors:
        print("AI music generation route planner verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music generation route planner verification passed.")
    print(f"tool: {PLANNER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
