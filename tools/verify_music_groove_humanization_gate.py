#!/usr/bin/env python3
"""Verify the AI music groove humanization audit gate."""

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
GROOVE_AUDIT = ROOT / "tools" / "audit_music_groove_humanization.py"
WIKI_GROOVE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐乐器演奏真实感与 Groove Humanization 工作流.md")
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
    return tmp_path / "20260625_zh-pop_night-bus"


def fill_good_lyrics_topline_harmony(project: Path) -> None:
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
    write(project / "03_writing" / "prosody-check.md", "# Prosody Check\n\nProsody notes: keep Mandarin long notes on stable vowels.\n")
    write(
        project / "04_prompt" / "lyrics-context-map.md",
        """# Lyrics Context Map

```text
[Song intent: restrained Mandarin confession]
[Prosody notes: keep Mandarin long notes on stable vowels]
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
    write(
        project / "03_writing" / "harmony-brief.md",
        """# Harmony Brief

Language: zh
Genre: Mandarin pop ballad
Tempo / meter: 78 BPM 4/4
Song emotion: restrained night-bus loneliness to warm confession
Lyric turning point: message almost sent before chorus
Topline hook status: pass
Key / mode target: minor verse color resolving to bright major chorus lift
Main chord color: warm add9 piano voicings, clear tonic arrival
Tension level: moderate pre-chorus suspension
Bass identity: warm root bass with short melodic pickup
Must avoid: same four-chord loop all song, random key change, muddy bass, bass unrelated to kick, unresolved chorus
Exact harmony required?: no
If exact: n/a
""",
    )
    write(
        project / "03_writing" / "progression-map.md",
        """# Progression Map

[Verse 1]
Progression: vi-IV-I-V, sparse piano
Function: starts unresolved and leaves room for the bus-window narrative

[Pre-Chorus]
Progression / color: ii-Vsus with stepwise bass climb
Tension device: suspended dominant before the chorus
Target chord: I at chorus downbeat

[Chorus]
Progression: I-V-vi-IV
Arrival point: title phrase lands clearly on I with open voicing
Title phrase chord: I tonic under 亮

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


def fill_good_groove(project: Path) -> None:
    write(
        project / "03_writing" / "performance-brief.md",
        """# Performance Brief

Song: Night Bus Confession
Language: zh
Style: Mandarin pop ballad
Tempo / meter: 78 BPM 4/4
Master pocket: laid-back verse, straighter chorus, snare slightly behind
Drum role: soft kick/snare pocket, light ghost notes, no busy fills under vocal
Bass role: follows kick in chorus, sparse muted notes in verse
Guitar role: muted electric guitar answers only between vocal phrases
Keys / synth role: sparse piano comping, short bell synth motif
Vocal-rhythm relationship: title words land on strong beats and drums leave space
Verse feel: intimate, sparse drums, muted bass
Pre-chorus feel: bass rises, snare fill only into chorus
Chorus feel: straighter groove, bass locks with kick, open but not loud-only
Bridge feel: half-time drums, bass drops out first half
Must not sound like: plastic quantized drums, random drum fills, fake live band, constant eighth-note bass, constant pad
Repair priority: rhythm-section pocket before mix polish
""",
    )
    write(
        project / "03_writing" / "drum-realism-map.md",
        """# Drum Realism Map

Kick: soft root pulse, locks with bass on chorus downbeats
Snare: backbeat slightly behind, never flammy
Hats / ride: steady light hats with subtle velocity variation
Ghost notes: very soft, only in pre-chorus lift
Fills: one short snare fill into chorus and final chorus only
Cymbals: mark chorus entry, no constant wash
Velocity shape: hats vary slightly, ghost notes much softer than backbeat
Timing shape: kick stable, snare slightly behind, chorus straighter than verse
Section changes: verse sparse, pre lifts, chorus locks, bridge half-time
Do not: plastic quantized drums, random drum fills
""",
    )
    write(
        project / "03_writing" / "instrument-role-map.md",
        """# Instrument Role Map

Guitar role: muted electric answers between vocal phrases
Guitar playability: simple two-note answer, playable without impossible jumps
Keys / synth role: sparse piano comping and short bell motif
Keys / synth playability: piano leaves left hand out when bass enters
Lead / hook instrument: bell synth mirrors intro only
Vocal space: guitars answer after vocal, keys avoid constant full-range bed
Texture control: pad only in final chorus, not full song
Playable: yes, each part has a realistic hand role
Do not: wall of guitars, constant pad, endless shred
""",
    )
    write(
        project / "03_writing" / "section-performance-map.md",
        """# Section Performance Map

[Verse 1]
Performance: light drums, muted bass, piano leaves vocal space

[Pre-Chorus]
Performance: bass rises, short snare fill into chorus

[Chorus]
Performance: straighter groove, bass locks with kick, open guitar widens after title

[Verse 2]
Performance: new hat pattern, guitar answer after vocal

[Bridge]
Performance: half-time drums, bass drops out first half

[Final Chorus]
Performance: full band, same pocket, short fill before ending
""",
    )
    write(
        project / "03_writing" / "groove-audit.md",
        """# Groove Audit

Master pocket: laid-back verse, straighter chorus, snare slightly behind
Timing humanization: kick stable, snare slightly behind, chorus straighter than verse
Velocity humanization: hats vary slightly, ghost notes much softer than backbeat
Articulation humanization: muted bass in verse, sustained chorus roots, short guitar answers
Bass articulation: muted bass in verse, sustained chorus roots
Instrument-only reverse caption: restrained ballad band with real rhythm-section pocket
Does the groove match the brief?: yes
""",
    )


def fill_bad_groove(project: Path) -> None:
    write(project / "03_writing" / "performance-brief.md", "# Performance Brief\n\nMaster pocket: humanized\nDrum role: realistic band\n")
    write(project / "03_writing" / "drum-realism-map.md", "# Drum Realism Map\n\nKick: four-on-floor\n")
    write(project / "03_writing" / "instrument-role-map.md", "# Instrument Role Map\n\n")
    write(project / "03_writing" / "section-performance-map.md", "# Section Performance Map\n\n[Verse 1]\nPerformance: same loop\n")
    write(project / "03_writing" / "groove-audit.md", "# Groove Audit\n\n")


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, PROSODY_AUDIT, TOPLINE_AUDIT, HARMONY_AUDIT, GROOVE_AUDIT, WIKI_GROOVE, WIKI_PROMPT, WIKI_PROJECT, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-groove-gate-") as tmp:
        tmp_path = Path(tmp)
        project = scaffold_project(tmp_path)

        empty = subprocess.run([sys.executable, str(GROOVE_AUDIT), "--project-root", str(project), "--strict"], cwd=ROOT, text=True, capture_output=True)
        if empty.returncode == 0:
            errors.append("strict groove audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["master_pocket_missing", "kick_missing", "bass_articulation_missing", "harmony_audit_missing"]:
            if term not in empty_text:
                errors.append(f"empty groove audit output missing term: {term}")

        fill_good_lyrics_topline_harmony(project)
        for tool, label in [(PROSODY_AUDIT, "prosody"), (TOPLINE_AUDIT, "topline"), (HARMONY_AUDIT, "harmony/bass")]:
            result = subprocess.run([sys.executable, str(tool), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"], cwd=ROOT, text=True, capture_output=True)
            if result.returncode != 0:
                errors.append(f"{label} audit failed before groove: stdout={result.stdout.strip()} stderr={result.stderr.strip()}")

        fill_good_groove(project)
        good = subprocess.run([sys.executable, str(GROOVE_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"], cwd=ROOT, text=True, capture_output=True)
        if good.returncode != 0:
            errors.append(f"good groove audit failed: stdout={good.stdout.strip()} stderr={good.stderr.strip()}")

        audit_path = project / "03_writing" / "groove-humanization-audit.md"
        if not audit_path.exists():
            errors.append("groove humanization audit output missing")
        else:
            audit_text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/audit_music_groove_humanization.py",
                "Decision: pass",
                "Groove tags:",
                "Instrument performance tags:",
                "Rhythm-section blind test:",
                "## Groove Design",
                "snare slightly behind",
            ]:
                if term not in audit_text:
                    errors.append(f"groove audit output missing term: {term}")

        no_overwrite = subprocess.run([sys.executable, str(GROOVE_AUDIT), "--project-root", str(project), "--write"], cwd=ROOT, text=True, capture_output=True)
        if no_overwrite.returncode != 2:
            errors.append("groove audit should refuse overwrite without --allow-overwrite")

        fill_bad_groove(project)
        bad = subprocess.run([sys.executable, str(GROOVE_AUDIT), "--project-root", str(project), "--strict"], cwd=ROOT, text=True, capture_output=True)
        if bad.returncode == 0:
            errors.append("strict groove audit should reject missing drum map, section plan, playability, and humanization")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["tempo_meter_missing", "snare_missing", "hats_missing", "humanization_missing", "playability_missing"]:
            if term not in bad_text:
                errors.append(f"bad groove audit output missing term: {term}")

    for page, terms in {
        WIKI_GROOVE: ["tools/audit_music_groove_humanization.py", "groove-humanization-audit.md"],
        WIKI_PROMPT: ["tools/audit_music_groove_humanization.py", "Groove audit"],
        WIKI_PROJECT: ["groove-humanization-audit.md", "audit_music_groove_humanization.py"],
    }.items():
        text = page.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{page} missing groove gate term: {term}")

    if "AI 音乐 Groove Humanization 工具闸门" not in LOG.read_text(encoding="utf-8"):
        errors.append("wiki log missing groove humanization gate entry")

    if errors:
        print("AI music groove humanization gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music groove humanization gate verification passed.")
    print(f"tool: {GROOVE_AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
