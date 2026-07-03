#!/usr/bin/env python3
"""Inspect release-candidate WAV files for basic technical delivery issues.

This is not a loudness meter and it does not judge musical quality. It checks
that release-candidate audio is a readable PCM WAV with basic delivery specs
and no obvious silence or clipping before release-candidate packaging.
"""

from __future__ import annotations

import argparse
import math
import sys
import wave
from dataclasses import dataclass, field
from pathlib import Path


OUTPUT = "10_mix-master/release-audio-technical-inspection.md"


@dataclass
class AudioInspection:
    path: Path
    ok: bool = False
    errors: list[str] = field(default_factory=list)
    channels: int = 0
    sample_rate: int = 0
    sample_width_bits: int = 0
    frames: int = 0
    duration: float = 0.0
    peak: float = 0.0
    rms: float = 0.0
    dc_offset: float = 0.0
    clipped_ratio: float = 0.0


def wav_files(project_root: Path) -> list[Path]:
    audio_dir = project_root / "11_release" / "release_candidate" / "audio"
    if not audio_dir.exists():
        return []
    return sorted(path for path in audio_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".wav", ".wave"})


def sample_values(data: bytes, sample_width: int) -> tuple[list[int], int]:
    values: list[int] = []
    if sample_width == 1:
        return [byte - 128 for byte in data], 128
    if sample_width == 2:
        for index in range(0, len(data) - 1, 2):
            values.append(int.from_bytes(data[index : index + 2], "little", signed=True))
        return values, 32768
    if sample_width == 3:
        for index in range(0, len(data) - 2, 3):
            values.append(int.from_bytes(data[index : index + 3], "little", signed=True))
        return values, 8388608
    if sample_width == 4:
        for index in range(0, len(data) - 3, 4):
            values.append(int.from_bytes(data[index : index + 4], "little", signed=True))
        return values, 2147483648
    return values, 1


def inspect_wav(path: Path, min_duration: float, min_sample_rate: int, min_peak: float, max_clipped_ratio: float) -> AudioInspection:
    result = AudioInspection(path=path)
    try:
        with wave.open(str(path), "rb") as handle:
            result.channels = handle.getnchannels()
            result.sample_rate = handle.getframerate()
            sample_width = handle.getsampwidth()
            result.sample_width_bits = sample_width * 8
            result.frames = handle.getnframes()
            result.duration = result.frames / result.sample_rate if result.sample_rate else 0.0
            if sample_width not in {1, 2, 3, 4}:
                result.errors.append(f"unsupported PCM sample width: {sample_width} bytes")
                return result

            total = 0
            total_sq = 0.0
            total_sum = 0.0
            peak_abs = 0
            clipped = 0
            max_abs = 1
            while True:
                chunk = handle.readframes(8192)
                if not chunk:
                    break
                values, max_abs = sample_values(chunk, sample_width)
                for value in values:
                    abs_value = abs(value)
                    peak_abs = max(peak_abs, abs_value)
                    if abs_value >= max_abs * 0.999:
                        clipped += 1
                    total += 1
                    total_sum += value
                    total_sq += value * value
            if total:
                result.peak = peak_abs / max_abs
                result.rms = math.sqrt(total_sq / total) / max_abs
                result.dc_offset = total_sum / total / max_abs
                result.clipped_ratio = clipped / total
    except wave.Error as exc:
        result.errors.append(f"invalid WAV: {exc}")
        return result
    except OSError as exc:
        result.errors.append(f"cannot read audio: {exc}")
        return result

    if result.channels not in {1, 2}:
        result.errors.append(f"unexpected channel count: {result.channels}")
    if result.sample_rate < min_sample_rate:
        result.errors.append(f"sample rate below {min_sample_rate} Hz: {result.sample_rate}")
    if result.sample_width_bits < 16:
        result.errors.append(f"sample width below 16-bit: {result.sample_width_bits}")
    if result.duration < min_duration:
        result.errors.append(f"duration below {min_duration:.1f}s: {result.duration:.2f}s")
    if result.peak < min_peak:
        result.errors.append(f"peak below silence threshold {min_peak:.4f}: {result.peak:.6f}")
    if result.clipped_ratio > max_clipped_ratio:
        result.errors.append(f"clipped sample ratio above {max_clipped_ratio:.6f}: {result.clipped_ratio:.6f}")

    result.ok = not result.errors
    return result


def inspect_project(project_root: Path, min_duration: float, min_sample_rate: int, min_peak: float, max_clipped_ratio: float) -> tuple[list[AudioInspection], list[str]]:
    files = wav_files(project_root)
    if not files:
        return [], ["no WAV files found in 11_release/release_candidate/audio/"]
    inspections = [inspect_wav(path, min_duration, min_sample_rate, min_peak, max_clipped_ratio) for path in files]
    errors: list[str] = []
    for item in inspections:
        for error in item.errors:
            errors.append(f"{item.path.relative_to(project_root).as_posix()}: {error}")
    return inspections, errors


def render_report(project_root: Path, inspections: list[AudioInspection], errors: list[str], min_duration: float, min_sample_rate: int, min_peak: float, max_clipped_ratio: float) -> str:
    decision = "pass" if not errors else "hold"
    rows = ["| file | duration | sample rate | bit depth | channels | peak | RMS | DC offset | clipped ratio | status |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for item in inspections:
        rel = item.path.relative_to(project_root).as_posix()
        rows.append(
            f"| {rel} | {item.duration:.2f}s | {item.sample_rate} | {item.sample_width_bits} | {item.channels} | "
            f"{item.peak:.4f} | {item.rms:.4f} | {item.dc_offset:.5f} | {item.clipped_ratio:.6f} | {'pass' if item.ok else 'hold'} |"
        )
    return f"""# Release Audio Technical Inspection

Generated by: tools/inspect_music_release_audio.py
Project root: {project_root}
Decision: {decision}

This is a basic PCM WAV delivery inspection. It is not LUFS, True Peak, codec,
or musical-quality analysis. Use it before release-candidate packaging to catch
damaged, silent, clipped, or low-spec files.

## Thresholds

- minimum duration seconds: {min_duration:.1f}
- minimum sample rate: {min_sample_rate}
- minimum normalized peak: {min_peak:.4f}
- maximum clipped sample ratio: {max_clipped_ratio:.6f}

## Results

{chr(10).join(rows)}

## Blocking Items

{chr(10).join(f"- {error}" for error in errors) if errors else "- none"}

## Next Action

{"Continue to release-audio-qc-report.md and release-candidate gate." if not errors else "Replace or repair the WAV export, then rerun this tool."}
"""


def write_report(project_root: Path, text: str, allow_overwrite: bool) -> Path:
    path = project_root / OUTPUT
    if path.exists() and not allow_overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {OUTPUT}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Song project root.")
    parser.add_argument("--write", action="store_true", help="Write release-audio-technical-inspection.md.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow overwriting the inspection report.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when inspection fails.")
    parser.add_argument("--min-duration-seconds", type=float, default=30.0, help="Minimum duration for a release WAV.")
    parser.add_argument("--min-sample-rate", type=int, default=44100, help="Minimum sample rate.")
    parser.add_argument("--min-peak", type=float, default=0.001, help="Minimum normalized peak to avoid silent files.")
    parser.add_argument("--max-clipped-ratio", type=float, default=0.001, help="Maximum ratio of clipped samples.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        print(f"error: project root does not exist: {project_root}", file=sys.stderr)
        return 2
    inspections, errors = inspect_project(project_root, args.min_duration_seconds, args.min_sample_rate, args.min_peak, args.max_clipped_ratio)
    report = render_report(project_root, inspections, errors, args.min_duration_seconds, args.min_sample_rate, args.min_peak, args.max_clipped_ratio)
    if args.write:
        try:
            written = write_report(project_root, report, args.allow_overwrite)
        except FileExistsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"wrote {written.relative_to(project_root).as_posix()}")
    else:
        print("release audio technical inspection")
        print(f"decision: {'pass' if not errors else 'hold'}")
        for error in errors:
            print(f"- {error}")
    if errors and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
