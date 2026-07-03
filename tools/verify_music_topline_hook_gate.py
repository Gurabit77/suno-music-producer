#!/usr/bin/env python3
"""Verify the AI music topline hook audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
PROSODY_AUDIT = ROOT / "tools" / "audit_music_lyrics_prosody.py"
TOPLINE_AUDIT = ROOT / "tools" / "audit_music_topline_hook.py"
WIKI_TOPLINE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Topline Hook 与旋律草稿工作流.md")
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


def fill_good_lyrics(project: Path) -> None:
    write(
        project / "04_prompt" / "prompt-compile-brief.md",
        """# Prompt Compile Brief

Language: zh
Title phrase: 末班车还亮着
Hook promise: title phrase lands like a held confession
Narrator: first-person commuter
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


def fill_good_topline(project: Path) -> None:
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
Chorus title landing: long note on 亮 over the chorus arrival chord
Demo file: none
Source: none
Rights: none
""",
    )
    write(
        project / "03_writing" / "melody-contour.md",
        """# Melody Contour

Verse contour: low - low - small rise - fall
Verse rhythm: conversational short phrases
Pre contour: mid - rising - suspended
Pre rhythm: fewer syllables before chorus
Chorus contour: jump up - hold - step down - repeat
Chorus title landing: 亮 is the long-note word
Bridge contrast: lower, narrower, less rhythmic
Final chorus variation: same hook, one restrained lift
""",
    )


def fill_bad_topline(project: Path) -> None:
    write(
        project / "03_writing" / "title-phrase.md",
        """# Title Phrase

Title phrase: Dream Light Forever
Meaning: generic emotion
""",
    )
    write(project / "03_writing" / "topline-map.md", "# Topline Map\n\nDemo file: none\n")
    write(project / "03_writing" / "melody-contour.md", "# Melody Contour\n\nVerse contour: flat\n")


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, PROSODY_AUDIT, TOPLINE_AUDIT, WIKI_TOPLINE, WIKI_PROMPT, WIKI_PROJECT, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-topline-gate-") as tmp:
        tmp_path = Path(tmp)
        project = scaffold_project(tmp_path)

        empty = subprocess.run(
            [sys.executable, str(TOPLINE_AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if empty.returncode == 0:
            errors.append("strict topline audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["title_phrase_missing", "spoken_stress_missing", "rhythm_cell_missing", "prosody_audit_missing"]:
            if term not in empty_text:
                errors.append(f"empty topline audit output missing term: {term}")

        fill_good_lyrics(project)
        prosody = subprocess.run(
            [sys.executable, str(PROSODY_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if prosody.returncode != 0:
            errors.append(f"prosody audit failed before topline: stdout={prosody.stdout.strip()} stderr={prosody.stderr.strip()}")

        fill_good_topline(project)
        good = subprocess.run(
            [sys.executable, str(TOPLINE_AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if good.returncode != 0:
            errors.append(f"good topline audit failed: stdout={good.stdout.strip()} stderr={good.stderr.strip()}")

        audit_path = project / "03_writing" / "topline-hook-audit.md"
        if not audit_path.exists():
            errors.append("topline audit output missing")
        else:
            audit_text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/audit_music_topline_hook.py",
                "Decision: pass",
                "Topline tags:",
                "Blind hook test:",
                "## Hook Design",
                "末班车还亮着",
            ]:
                if term not in audit_text:
                    errors.append(f"topline audit output missing term: {term}")

        no_overwrite = subprocess.run(
            [sys.executable, str(TOPLINE_AUDIT), "--project-root", str(project), "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if no_overwrite.returncode != 2:
            errors.append("topline audit should refuse overwrite without --allow-overwrite")

        fill_bad_topline(project)
        bad = subprocess.run(
            [sys.executable, str(TOPLINE_AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if bad.returncode == 0:
            errors.append("strict topline audit should reject missing motif, contour, and chorus title")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["title_phrase_not_in_chorus", "spoken_stress_missing", "rhythm_cell_missing", "contour_missing"]:
            if term not in bad_text:
                errors.append(f"bad topline audit output missing term: {term}")

    for page, terms in {
        WIKI_TOPLINE: ["tools/audit_music_topline_hook.py", "topline-hook-audit.md"],
        WIKI_PROMPT: ["tools/audit_music_topline_hook.py", "Topline audit"],
        WIKI_PROJECT: ["topline-hook-audit.md", "audit_music_topline_hook.py"],
    }.items():
        text = page.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{page} missing topline gate term: {term}")

    if "AI 音乐 Topline Hook 工具闸门" not in LOG.read_text(encoding="utf-8"):
        errors.append("wiki log missing topline hook gate entry")

    if errors:
        print("AI music topline hook gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music topline hook gate verification passed.")
    print(f"tool: {TOPLINE_AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
