#!/usr/bin/env python3
"""Verify release audio QC report preparation."""

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
QC = ROOT / "tools" / "prepare_music_release_audio_qc.py"
WIKI_MASTER = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐母带翻译与发行前音频 QC 工作流.md")
WIKI_TEMPLATE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_wav(path: Path, *, duration: float = 1.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    frames = int(sample_rate * duration)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        data = bytearray()
        for index in range(frames):
            sample = int(math.sin(2 * math.pi * 440 * index / sample_rate) * 12000)
            data.extend(struct.pack("<hh", sample, sample))
        handle.writeframes(bytes(data))


def write_qc_sources(project: Path) -> None:
    write(
        project / "10_mix-master" / "loudness-true-peak-report.md",
        """# Loudness True Peak Report

Decision: pass
Integrated LUFS: -14.0
LRA: 6.0
True Peak: -1.0 dBTP
Clipped samples: 0
Loudness-matched reference A/B: pass
""",
    )
    write(
        project / "10_mix-master" / "codec-preview.md",
        """# Codec Preview

Decision: pass
Codec preview: pass
Codec: AAC / MP3 preview
Platform notes: codec and platform previews passed
""",
    )
    write(
        project / "10_mix-master" / "translation-listen-matrix.md",
        """# Translation Listen Matrix

Decision: pass
Translation matrix: pass
Headphones: pass
Phone speaker: pass
Car: pass
Intro/outro: pass
Rejected files: none
""",
    )
    write(
        project / "10_mix-master" / "mono-phase-low-end-check.md",
        """# Mono Phase Low End Check

Decision: pass
Mono/phase: pass
Phase: pass
Low end: pass
""",
    )
    write(
        project / "10_mix-master" / "transient-and-limiter-audit.md",
        """# Transient And Limiter Audit

Decision: pass
Transient: pass
Limiter: pass
Over-limiting: none
Vocal tail: pass
Cymbals: pass
Backing vocal smear: none
Stem bleed: none
""",
    )


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, INSPECT, QC, WIKI_MASTER, WIKI_TEMPLATE]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-release-audio-qc-") as tmp:
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

        empty = run([sys.executable, str(QC), "--project-root", str(project), "--strict"])
        if empty.returncode == 0:
            errors.append("empty release audio QC should fail in strict mode")

        audio = project / "11_release" / "release_candidate" / "audio" / "night-bus-master.wav"
        write_wav(audio)
        inspection = run(
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
        if inspection.returncode != 0:
            errors.append(f"release audio inspection should pass: {inspection.stderr.strip()}")

        missing_sources = run([sys.executable, str(QC), "--project-root", str(project), "--strict"])
        if missing_sources.returncode == 0:
            errors.append("release audio QC should require mastering QC source evidence")
        missing_text = missing_sources.stdout + "\n" + missing_sources.stderr
        for term in ["loudness-true-peak-report.md", "codec-preview.md", "translation-listen-matrix.md"]:
            if term not in missing_text:
                errors.append(f"missing-source blocker absent: {term}")

        write_qc_sources(project)
        ok = run(
            [
                sys.executable,
                str(QC),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ]
        )
        if ok.returncode != 0:
            errors.append(f"release audio QC should pass: {ok.stderr.strip()}")
        report = project / "10_mix-master" / "release-audio-qc-report.md"
        if not report.is_file():
            errors.append("missing release audio QC report")
        else:
            text = report.read_text(encoding="utf-8")
            for term in [
                "Generated by: tools/prepare_music_release_audio_qc.py",
                "Decision: pass",
                "integrated LUFS",
                "True Peak",
                "codec preview",
                "translation matrix",
                "mono/phase",
                "over-limiting",
                "Blocking Items",
            ]:
                if term not in text:
                    errors.append(f"release audio QC report missing term: {term}")

        no_overwrite = run([sys.executable, str(QC), "--project-root", str(project), "--write", "--strict"])
        if no_overwrite.returncode == 0:
            errors.append("release audio QC should refuse overwrite without --allow-overwrite")

        write(
            project / "10_mix-master" / "codec-preview.md",
            """# Codec Preview

Decision: hold
Codec preview: fail
Codec: AAC preview
Platform notes: distorted after codec preview
""",
        )
        blocked = run([sys.executable, str(QC), "--project-root", str(project), "--strict"])
        if blocked.returncode == 0:
            errors.append("release audio QC should block failed codec preview")

    master_text = WIKI_MASTER.read_text(encoding="utf-8")
    for term in ["tools/prepare_music_release_audio_qc.py", "release-audio-qc-report.md", "--strict"]:
        if term not in master_text:
            errors.append(f"master workflow missing term: {term}")

    template_text = WIKI_TEMPLATE.read_text(encoding="utf-8")
    for term in ["tools/prepare_music_release_audio_qc.py", "release-audio-qc-report.md"]:
        if term not in template_text:
            errors.append(f"project template missing term: {term}")

    log_text = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    if "AI 音乐 Release Audio QC 汇总工具" not in log_text:
        errors.append("wiki log missing release audio QC entry")

    if errors:
        print("AI music release audio QC verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music release audio QC verification passed.")
    print(f"tool: {QC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
