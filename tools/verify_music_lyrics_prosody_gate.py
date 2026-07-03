#!/usr/bin/env python3
"""Verify the AI music lyrics prosody audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
AUDIT = ROOT / "tools" / "audit_music_lyrics_prosody.py"
WIKI_PROSODY = Path("/path/to/obsidian-vault/wiki/分析/音乐/四语种歌词 Prosody 与 AI 音乐咬字审查表.md")
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
Narrator: first-person commuter
""",
    )
    write(
        project / "03_writing" / "prosody-check.md",
        """# Prosody Check

Prosody notes: keep Mandarin long notes on stable vowels; leave a breath before the chorus title.
Natural stress / tone notes: title phrase should land on content words.
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


def fill_bad_lyrics(project: Path) -> None:
    write(
        project / "04_prompt" / "prompt-compile-brief.md",
        """# Prompt Compile Brief

Language: en
Title phrase: After the Rain
Narrator: first-person narrator
""",
    )
    write(
        project / "03_writing" / "prosody-check.md",
        """# Prosody Check

Prosody notes: keep stressed words on strong beats.
""",
    )
    write(
        project / "04_prompt" / "lyrics-context-map.md",
        """# Lyrics Context Map

```text
[Verse 1 | conversational English]
I was wandering through the endless midnight rain with shattered neon echoes in the void around me
[Chorus | generic chorus]
We keep running through the city lights and never say the thing we wanted
[End]
```
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, AUDIT, WIKI_PROSODY, WIKI_PROMPT, WIKI_PROJECT, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-prosody-gate-") as tmp:
        tmp_path = Path(tmp)
        project = scaffold_project(tmp_path)

        empty = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if empty.returncode == 0:
            errors.append("strict prosody audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["title_phrase_missing", "prosody_notes_missing", "lyrics_block_missing"]:
            if term not in empty_text:
                errors.append(f"empty prosody audit output missing term: {term}")

        fill_good_lyrics(project)
        good = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if good.returncode != 0:
            errors.append(f"good prosody audit failed: stdout={good.stdout.strip()} stderr={good.stderr.strip()}")

        audit_path = project / "03_writing" / "lyrics-prosody-audit.md"
        if not audit_path.exists():
            errors.append("prosody audit output missing")
        else:
            audit_text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/audit_music_lyrics_prosody.py",
                "Decision: pass",
                "Lyrics tags: natural Mandarin phrasing",
                "Exclude additions: awkward translated Mandarin",
                "Blind-listening red flags",
                "## Section Metrics",
            ]:
                if term not in audit_text:
                    errors.append(f"prosody audit output missing term: {term}")

        no_overwrite = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if no_overwrite.returncode != 2:
            errors.append("prosody audit should refuse overwrite without --allow-overwrite")

        fill_bad_lyrics(project)
        bad = subprocess.run(
            [sys.executable, str(AUDIT), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if bad.returncode == 0:
            errors.append("strict prosody audit should reject missing chorus title and overlong lines")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["title_phrase_not_in_chorus", "line_too_long", "After the Rain"]:
            if term not in bad_text:
                errors.append(f"bad prosody audit output missing term: {term}")

    for page, terms in {
        WIKI_PROSODY: ["tools/audit_music_lyrics_prosody.py", "lyrics-prosody-audit.md"],
        WIKI_PROMPT: ["tools/audit_music_lyrics_prosody.py", "Prosody audit"],
        WIKI_PROJECT: ["lyrics-prosody-audit.md", "audit_music_lyrics_prosody.py"],
    }.items():
        text = page.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{page} missing prosody gate term: {term}")

    if "AI 音乐 Lyrics Prosody 工具闸门" not in LOG.read_text(encoding="utf-8"):
        errors.append("wiki log missing lyrics prosody gate entry")

    if errors:
        print("AI music lyrics prosody gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music lyrics prosody gate verification passed.")
    print(f"tool: {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
