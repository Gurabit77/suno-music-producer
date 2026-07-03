#!/usr/bin/env python3
"""Verify the AI music lyric narrative and cliche-cut audit gate."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
AUDIT = ROOT / "tools" / "audit_music_lyric_narrative.py"
COMPILER = ROOT / "tools" / "compile_music_prompt_package.py"
WIKI_LYRIC = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐歌词叙事与反陈词滥调工作流.md")
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
        "lyric-narrative",
        "--title",
        "Lyric Narrative Gate",
        "--artist-project",
        "Example Test Artist",
        "--use-case",
        "demo",
    ]
    result = run(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return tmp_path / "20260625_zh-pop_lyric-narrative"


def fill_good_inputs(project: Path) -> None:
    write(
        project / "03_writing" / "lyric-brief.md",
        """# Lyric Brief

Narrator: first-person commuter who keeps an unsent confession on the phone
Situation: 00:47 on the last bus, sitting by the back window after a cancelled dinner
Title phrase: 末班车还亮着
Title phrase function: the chorus turns the bus light into proof that the confession still has one last chance
Central metaphor: the last bus light is a held breath, not a generic hope symbol
Emotion arc: denial in Verse 1, concrete admission in Verse 2, self-ownership in Bridge, softer acceptance in Final Chorus
""",
    )
    write(
        project / "03_writing" / "title-phrase.md",
        """# Title Phrase

Title phrase: 末班车还亮着
Title phrase function: chorus hook; the light means there is still time to say one true sentence
Central metaphor: the bus light as held breath
""",
    )
    write(
        project / "03_writing" / "image-bank.md",
        """# Image Bank

Concrete images:
- back-row bus window with finger marks
- unsent phone message
- wet sleeve over a paper ticket
- empty seat beside the narrator
- steamed convenience-store cup
- 00:47 station clock
Sensory anchors: bus brake hiss, cold sleeve, phone screen glare, paper ticket crease
""",
    )
    write(
        project / "03_writing" / "section-information-map.md",
        """# Section Information Map

Verse 1: narrator hides the phone and describes the bus window, setting the cancelled dinner without explaining it.
Chorus: title phrase becomes the hook and states the emotional question.
Verse 2 development: new information reveals the message was written before the dinner was cancelled; the empty seat changes meaning.
Bridge perspective: turn from blaming the missed timing to admitting the narrator chose silence.
Final chorus payoff: title returns softer as a decision to send one honest sentence after leaving the bus.
""",
    )
    write(
        project / "03_writing" / "cliche-cut.md",
        """# Cliche Cut

Removed cliches: forever, lonely heart, dream, neon rain
Replacement images: unsent phone message, wet sleeve over paper ticket, bus-window finger marks, 00:47 station clock
Cliche cut decision: ready for rewrite
""",
    )
    write(
        project / "04_prompt" / "lyrics-context-map.md",
        """# Lyrics Context Map

```text
[Song intent: restrained Mandarin confession]
[Prosody notes: keep title vowels stable]
[Verse 1 | back-row bus window | narrator hides the phone]
后排的窗 留着我指尖的雾
纸票贴着袖口 一点点凉住
[Chorus | title hook | held-breath light]
末班车还亮着 我却没按发送
末班车还亮着 像替我撑住沉默
[Verse 2 | new information | empty seat changes meaning]
你没来的座位 还向车门空着
那句早写好的话 被我锁进屏幕
[Bridge | new perspective | chosen silence]
我怪过时间 其实是我先退后
[Final Chorus | payoff | title returns softer]
末班车还亮着 我把真话说出口
[End]
```
""",
    )


def fill_bad_inputs(project: Path) -> None:
    write(
        project / "03_writing" / "lyric-brief.md",
        """# Lyric Brief

Narrator: someone sad
Situation: somewhere at night
Title phrase: Forever in the Light
Title phrase function: emotional chorus
Central metaphor: light and shadow
""",
    )
    write(project / "03_writing" / "image-bank.md", "# Image Bank\n\nConcrete images:\n- light\n- heart\n")
    write(
        project / "03_writing" / "section-information-map.md",
        """# Section Information Map

Verse 1: sad feelings.
Chorus: repeat the title.
Verse 2: same sad feelings.
""",
    )
    write(
        project / "03_writing" / "cliche-cut.md",
        """# Cliche Cut

Removed cliches: dream
Replacement images: light
Cliche cut decision: hold
""",
    )
    write(
        project / "04_prompt" / "lyrics-context-map.md",
        """# Lyrics Context Map

```text
[Verse 1]
In the neon rain my broken heart follows dreams into the endless sky
[Chorus]
Forever in the light, forever in the shadow, lost in city lights tonight
[Verse 2]
In the neon rain my broken heart follows dreams into the endless sky
[End]
```
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, AUDIT, COMPILER, WIKI_LYRIC, WIKI_PROMPT, WIKI_PROJECT, WIKI_SINGLE, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-lyric-narrative-gate-") as tmp:
        project = scaffold_project(Path(tmp))

        empty = run([sys.executable, str(AUDIT), "--project-root", str(project), "--strict"])
        if empty.returncode == 0:
            errors.append("strict lyric narrative audit should reject empty scaffold")
        empty_text = empty.stdout + "\n" + empty.stderr
        for term in ["narrator_missing", "image_bank_sparse", "cliche_replacements_sparse"]:
            if term not in empty_text:
                errors.append(f"empty lyric narrative audit output missing term: {term}")

        fill_good_inputs(project)
        passed = run([sys.executable, str(AUDIT), "--project-root", str(project), "--write", "--allow-overwrite", "--strict"])
        if passed.returncode != 0:
            errors.append(f"good lyric narrative audit failed: stdout={passed.stdout.strip()} stderr={passed.stderr.strip()}")
        audit_path = project / "03_writing" / "lyric-narrative-audit.md"
        if not audit_path.exists():
            errors.append("lyric narrative audit output missing")
        else:
            text = audit_path.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/audit_music_lyric_narrative.py",
                "Decision: pass",
                "## Lyric Narrative Evidence",
                "Narrator/situation tags:",
                "Concrete image tags:",
                "Title phrase function:",
                "Central metaphor:",
                "Section information tags:",
                "Cliche removal:",
                "Verse 2 development:",
                "Bridge perspective:",
                "Lyrics rewrite handoff: pass",
            ]:
                if term not in text:
                    errors.append(f"lyric narrative audit output missing term: {term}")

        no_overwrite = run([sys.executable, str(AUDIT), "--project-root", str(project), "--write"])
        if no_overwrite.returncode != 2:
            errors.append("lyric narrative audit should refuse overwrite without --allow-overwrite")

        audit_path.unlink(missing_ok=True)
        compile_without_audit = run([sys.executable, str(COMPILER), "--project-root", str(project), "--strict"])
        if "lyric_narrative_audit" not in (compile_without_audit.stdout + compile_without_audit.stderr):
            errors.append("compiler should surface lyric_narrative_audit when the audit is absent/invalid")

        fill_bad_inputs(project)
        bad = run([sys.executable, str(AUDIT), "--project-root", str(project), "--strict"])
        if bad.returncode == 0:
            errors.append("strict lyric narrative audit should reject vague/cliche lyric evidence")
        bad_text = bad.stdout + "\n" + bad.stderr
        for term in ["image_bank_sparse", "bridge_or_payoff_missing", "verse2_development_missing", "cliche_terms_unhandled"]:
            if term not in bad_text:
                errors.append(f"bad lyric narrative audit output missing term: {term}")

    for page, terms in {
        WIKI_LYRIC: ["tools/audit_music_lyric_narrative.py", "lyric-narrative-audit.md", "Lyrics rewrite handoff"],
        WIKI_PROMPT: ["tools/audit_music_lyric_narrative.py", "Lyric narrative"],
        WIKI_PROJECT: ["lyric-narrative-audit.md", "audit_music_lyric_narrative.py", "lyric-narrative"],
        WIKI_SINGLE: ["lyric-narrative-gate", "audit_music_lyric_narrative.py"],
    }.items():
        text = page.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                errors.append(f"{page} missing lyric narrative gate term: {term}")

    if "AI 音乐 Lyric Narrative 工具闸门" not in LOG.read_text(encoding="utf-8"):
        errors.append("wiki log missing lyric narrative gate entry")

    if errors:
        print("AI music lyric narrative gate verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music lyric narrative gate verification passed.")
    print(f"tool: {AUDIT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
