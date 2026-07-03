#!/usr/bin/env python3
"""Verify release-candidate audio technical inspection."""

from __future__ import annotations

import math
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
INSPECT = ROOT / "tools" / "inspect_music_release_audio.py"
WIKI_MASTER = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐母带翻译与发行前音频 QC 工作流.md")
WIKI_TEMPLATE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def write_wav(path: Path, *, duration: float = 1.0, clipped: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    frames = int(sample_rate * duration)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        data = bytearray()
        for index in range(frames):
            sample = 32767 if clipped else int(math.sin(2 * math.pi * 440 * index / sample_rate) * 12000)
            data.extend(struct.pack("<hh", sample, sample))
        handle.writeframes(bytes(data))


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, INSPECT, WIKI_MASTER, WIKI_TEMPLATE]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-audio-inspect-") as tmp:
        tmp_path = Path(tmp)
        scaffold = run(
            [
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
                "release-single",
            ]
        )
        if scaffold.returncode != 0:
            errors.append(f"scaffold failed: {scaffold.stderr.strip()}")
            print("\n".join(errors), file=sys.stderr)
            return 1
        project = tmp_path / "20260624_zh-pop_night-bus"

        empty = run([sys.executable, str(INSPECT), "--project-root", str(project), "--strict"])
        if empty.returncode == 0:
            errors.append("empty audio folder should fail strict inspection")

        invalid = project / "11_release" / "release_candidate" / "audio" / "broken.wav"
        invalid.parent.mkdir(parents=True, exist_ok=True)
        invalid.write_bytes(b"not a wav")
        bad = run([sys.executable, str(INSPECT), "--project-root", str(project), "--strict", "--min-duration-seconds", "0.5"])
        if bad.returncode == 0:
            errors.append("invalid wav should fail strict inspection")
        invalid.unlink()

        good = project / "11_release" / "release_candidate" / "audio" / "night-bus-master.wav"
        write_wav(good, duration=1.0)
        ok = run(
            [
                sys.executable,
                str(INSPECT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
                "--min-duration-seconds",
                "0.5",
            ]
        )
        if ok.returncode != 0:
            errors.append(f"valid wav should pass: {ok.stderr.strip()}")
        report = project / "10_mix-master" / "release-audio-technical-inspection.md"
        if not report.is_file():
            errors.append("missing technical inspection report")
        else:
            text = report.read_text(encoding="utf-8")
            for term in ["Decision: pass", "tools/inspect_music_release_audio.py", "44100", "night-bus-master.wav", "clipped ratio"]:
                if term not in text:
                    errors.append(f"technical report missing term: {term}")

        no_overwrite = run([sys.executable, str(INSPECT), "--project-root", str(project), "--write", "--strict", "--min-duration-seconds", "0.5"])
        if no_overwrite.returncode == 0:
            errors.append("inspection should refuse overwrite without --allow-overwrite")

        clipped = project / "11_release" / "release_candidate" / "audio" / "clipped.wav"
        write_wav(clipped, duration=1.0, clipped=True)
        clipped_result = run([sys.executable, str(INSPECT), "--project-root", str(project), "--strict", "--min-duration-seconds", "0.5"])
        if clipped_result.returncode == 0:
            errors.append("clipped wav should fail strict inspection")

    master_text = WIKI_MASTER.read_text(encoding="utf-8")
    for term in ["tools/inspect_music_release_audio.py", "release-audio-technical-inspection.md", "basic PCM WAV", "--strict"]:
        if term not in master_text:
            errors.append(f"master workflow missing term: {term}")

    template_text = WIKI_TEMPLATE.read_text(encoding="utf-8")
    for term in ["tools/inspect_music_release_audio.py", "release-audio-technical-inspection.md"]:
        if term not in template_text:
            errors.append(f"project template missing term: {term}")

    log_text = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    if "AI 音乐 Release Audio 技术检查工具" not in log_text:
        errors.append("wiki log missing release audio inspection entry")

    if errors:
        print("AI music release audio inspection verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music release audio inspection verification passed.")
    print(f"tool: {INSPECT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
