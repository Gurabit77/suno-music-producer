#!/usr/bin/env python3
"""Verify the AI music harmony/bass audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
PROSODY_AUDIT = ROOT / "tools" / "audit_music_lyrics_prosody.py"
TOPLINE_AUDIT = ROOT / "tools" / "audit_music_topline_hook.py"
HARMONY_AUDIT = ROOT / "tools" / "audit_music_harmony_bass.py"
WIKI_HARMONY = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐和声与低音方向工作流.md")
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
        "demo",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return tmp_path / "20260624_zh-pop_night-bus"


def fill_good_lyrics_and_topline(project: Path) -> None:
    write(
        project / "04_prompt" / "prompt-compile-brief.md",
        """# Prompt Compile Brief

Language: zh
Title phrase: 末班车还亮着
Hook promise: title phrase lands like a held confession
Narrator: first-person commuter
Emotion arc: restrained verse to warm release
""",
    )
    write(
        project / "03_writing" / "prosody-check.md",
        """# Prosody Check

Prosody notes: keep Mandarin long notes on stable vowels; leave a breath before the chorus title.
""",
    )
    write(
        project / "04_prompt" / "lyrics-context-map.md",
        """# Lyrics Context Map

```text
[Song intent: restrained Mandarin confession]
[Prosody notes: keep Mandarin long notes on stable vowels]
[Intro | short motif]
[Verse 1 | intimate vocal | concrete image]
车窗把霓虹揉成一条河
[Pre-Chorus | fewer words | breath before chorus]
我把讯息停在发送之前
[Chorus | 末班车还亮着 | title phrase on a long note]
末班车还亮着 可我没说破
[Verse 2 | new detail | groove deepens]
座位空着 像你还会经过
[Bridge | stripped piano | new perspective]
我终于承认 不只是路过
[Final Chorus | warmer harmony | title phrase returns softer]
末班车还亮着 我把名字收着
[Outro | clean ending]
[End]
```
""",
    )
    write(
        project / "03_writing" / "title-phrase.md",
        """# Title Phrase

Title phrase: 末班车还亮着
Meaning: the confession is still possible but almost missed
Natural spoken stress: 末班车 / 还亮着
Long-note word: 亮
Must-not-distort words: 末班车, 亮
""",
    )
    write(
        project / "03_writing" / "topline-map.md",
        """# Topline Map

Rhythm cell: short-short-long with a breath before the title
Motif contour: small rise into 亮, step down after 着
Target interval: rising fourth on 亮
Start position: chorus title enters on the downbeat
Repeat plan: title repeats twice; second repeat holds 亮 longer
Contrast plan: verse stays low and conversational, chorus jumps to mid-high register
Chorus title landing: long note on 亮 over the tonic arrival chord
Demo file: none
Source: none
Rights: none
""",
    )
    write(
        project / "03_writing" / "melody-contour.md",
        """# Melody Contour

Verse contour: low - low - small rise - fall
Pre contour: mid - rising - suspended
Chorus contour: jump up - hold - step down - repeat
Bridge contrast: lower, narrower, less rhythmic
Final chorus variation: same hook, one restrained lift
""",
    )


def fill_good_harmony(project: Path) -> None:
    write(
        project / "03_writing" / "harmony-brief.md",
        """# Harmony Brief

Language: zh
Genre: Mandarin pop ballad
Tempo / meter: 78 BPM 4/4
Song emotion: restrained night-bus loneliness to warm confession
Lyric turning point: the message is almost sent before the chorus title
Topline hook status: pass
Key / mode target: minor verse color resolving to bright major chorus lift
Main chord color: warm add9 piano voicings, clear tonic arrival
Tension level: moderate pre-chorus suspension
Bass identity: warm root bass with short melodic pickup
Must avoid: same four-chord loop all song, random key change, muddy bass, bass unrelated to kick, unresolved chorus
Exact harmony required? no
If exact: n/a
""",
    )
    write(
        project / "03_writing" / "progression-map.md",
        """# Progression Map

[Verse 1]
Progression: vi-IV-I-V, sparse piano
Function: starts unresolved and leaves room for the bus-window narrative
Density: low
Why it fits lyrics: keeps the confession withheld

[Pre-Chorus]
Progression / color: ii-Vsus with stepwise bass climb
Tension device: suspended dominant before the chorus
Target chord: I at chorus downbeat

[Chorus]
Progression: I-V-vi-IV
Arrival point: title phrase lands clearly on I with open voicing
Title phrase chord: I tonic under 亮

[Verse 2]
Variation: same verse color, bass answers the vocal

[Bridge]
New color: relative minor with reduced bass movement
Reason: admits the hidden feeling before returning

[Final Chorus]
Return / lift: same progression, wider voicing, one restrained borrowed iv before final I
""",
    )
    write(
        project / "03_writing" / "bassline-map.md",
        """# Bassline Map

Primary bass role: warm root anchor with melodic pickup into chorus
Kick relationship: bass follows kick accents, avoids busy fills under the title
Range / sound: warm electric bass, low-mid, not sub-heavy
Verse motion: sparse roots, enters after vocal image
Pre motion: stepwise rising bass toward I
Chorus motion: octave root bass locks the title landing
Bridge motion: reduced pedal bass under relative minor color
Fills / pickups: one short pickup before final chorus
Avoid: muddy bass, bass unrelated to kick
""",
    )
    write(
        project / "03_writing" / "harmonic-rhythm-map.md",
        """# Harmonic Rhythm Map

Verse chord-change rate: one chord per bar, sparse voicing
Pre chord-change rate: slightly faster with suspension into V
Chorus chord-change rate: stable one chord per bar, pause under title word
Bridge chord-change rate: slower, pedal feel
Where harmony should pause: on 亮 in the chorus title
Where harmony should accelerate: pre-chorus second half
""",
    )
    write(
        project / "03_writing" / "cadence-and-bridge-plan.md",
        """# Cadence And Bridge Plan

Chorus arrival: title phrase lands on I with open voicing and octave bass
Pre target: Vsus resolves to I
Bridge contrast: relative minor, reduced bass movement, stripped piano
Final chorus lift: wider harmony, same hook, one restrained borrowed iv before final I
Ending cadence: clean tonic ending after the final title
Do not use: same four-chord loop all song, random key change, unresolved chorus, muddy bass
""",
    )


def fill_bad_harmony(project: Path) -> None:
    write(project / "03_writing" / "harmony-brief.md", "# Harmony Brief\n\nKey / mode target: emotional chords\nExact harmony required?: yes\n")
    write(project / "03_writing" / "progression-map.md", "# Progression Map\n\n[Verse]\nProgression: four chords\n")
    write(project / "03_writing" / "bassline-map.md", "# Bassline Map\n\nPrimary bass role: bass\n")
    write(project / "03_writing" / "harmonic-rhythm-map.md", "# Harmonic Rhythm Map\n\n")
    write(project / "03_writing" / "cadence-and-bridge-plan.md", "# Cadence And Bridge Plan\n\n")


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, PROSODY_AUDIT, TOPLINE_AUDIT, HARMONY_AUDIT, WIKI_HARMONY, WIKI_PROMPT, WIKI_PROJECT, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-harmony-bass-gate-") as tmp:
        tmp_path = Path(tmp)
        project = scaffold_project(tmp_path)

        empty = subprocess.run(
            [sys.executable, str(HARMONY_AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if empty.returncode == 0:
            errors.append("strict harmony/bass audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["key_mode_missing", "bass_identity_missing", "harmonic_rhythm_missing", "topline_audit_missing"]:
            if term not in empty_text:
                errors.append(f"empty harmony/bass audit output missing term: {term}")

        fill_good_lyrics_and_topline(project)
        prosody = subprocess.run(
            [sys.executable, str(PROSODY_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if prosody.returncode != 0:
            errors.append(f"prosody audit failed before harmony/bass: stdout={prosody.stdout.strip()} stderr={prosody.stderr.strip()}")
        topline = subprocess.run(
            [sys.executable, str(TOPLINE_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if topline.returncode != 0:
            errors.append(f"topline audit failed before harmony/bass: stdout={topline.stdout.strip()} stderr={topline.stderr.strip()}")

        fill_good_harmony(project)
        good = subprocess.run(
            [sys.executable, str(HARMONY_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if good.returncode != 0:
            errors.append(f"good harmony/bass audit failed: stdout={good.stdout.strip()} stderr={good.stderr.strip()}")

        audit_path = project / "03_writing" / "harmony-bass-audit.md"
        if not audit_path.exists():
            errors.append("harmony/bass audit output missing")
        else:
            audit_text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/audit_music_harmony_bass.py",
                "Decision: pass",
                "Harmony tags:",
                "Bass tags:",
                "Topline/harmony fit:",
                "## Harmony Design",
                "I tonic under 亮",
            ]:
                if term not in audit_text:
                    errors.append(f"harmony/bass audit output missing term: {term}")

        no_overwrite = subprocess.run(
            [sys.executable, str(HARMONY_AUDIT), "--project-root", str(project), "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if no_overwrite.returncode != 2:
            errors.append("harmony/bass audit should refuse overwrite without --allow-overwrite")

        fill_bad_harmony(project)
        bad = subprocess.run(
            [sys.executable, str(HARMONY_AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if bad.returncode == 0:
            errors.append("strict harmony/bass audit should reject missing chorus arrival, kick relationship, and harmonic rhythm")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["chorus_arrival_missing", "kick_relationship_missing", "harmonic_rhythm_missing", "exact_harmony_plan_missing"]:
            if term not in bad_text:
                errors.append(f"bad harmony/bass audit output missing term: {term}")

    for page, terms in {
        WIKI_HARMONY: ["tools/audit_music_harmony_bass.py", "harmony-bass-audit.md"],
        WIKI_PROMPT: ["tools/audit_music_harmony_bass.py", "Harmony/Bass audit"],
        WIKI_PROJECT: ["harmony-bass-audit.md", "audit_music_harmony_bass.py"],
    }.items():
        text = page.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{page} missing harmony/bass gate term: {term}")

    if "AI 音乐 Harmony Bass 工具闸门" not in LOG.read_text(encoding="utf-8"):
        errors.append("wiki log missing harmony/bass gate entry")

    if errors:
        print("AI music harmony/bass gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music harmony/bass gate verification passed.")
    print(f"tool: {HARMONY_AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
