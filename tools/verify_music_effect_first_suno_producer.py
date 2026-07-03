#!/usr/bin/env python3
"""Verify the effect-first Suno Music Producer optimization."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from prepare_music_effect_first_suno_run import (
    BLOCKER_STATES,
    DATA_MODELS,
    GENERATION_EXECUTOR_STATES,
    MAIN_STATE_MACHINE,
    PROMPT_LINTER_CODES,
    REFERENCE_UPLOAD_STATE_MACHINE,
    SENSITIVE_ACTIONS,
    TAKE_REVIEW_FIELDS,
    USER_PREFERENCE_FIELDS,
    PromptPackage,
    build_effect_first_run,
    feedback_to_variable,
    lint_prompt,
)
from plan_music_generation_route import RoutePlan


ROOT = Path("/path/to/suno-music-producer")
PLAN = Path("/path/to/private-effect-first-plan.md")
SKILL = Path("/path/to/codex-skills/suno-music-producer/SKILL.md")
EFFECT_REF = Path("/path/to/codex-skills/suno-music-producer/references/effect-first-orchestration.md")
LOCAL_REF = Path("/path/to/codex-skills/suno-music-producer/references/local-ai-music-project.md")
UPLOAD_REF = Path("/path/to/codex-skills/suno-music-producer/references/reference-upload-generation.md")
PREPARE = ROOT / "tools" / "prepare_music_effect_first_suno_run.py"
PLANNER = ROOT / "tools" / "plan_music_generation_route.py"
BUILD_SKELETON = ROOT / "tools" / "build_music_chord_skeleton_seed.py"
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
LOOP_PROMPT = ROOT / "loop-prompts" / "suno-music-producer-effect-first-autopilot.md"


def run(cmd: list[str], *, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scaffold(tmp: Path) -> Path:
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
            "effect-first",
            "--title",
            "Effect First Test",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "demo",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return tmp / "20260630_zh-pop_effect-first"


def fake_route() -> RoutePlan:
    return RoutePlan(
        decision="ordinary_generation",
        operating_mode="quick_idea",
        confidence="high",
        primary_route="text-only",
        fallback_route="none",
        effect_lever="style",
        user_effort="low",
        risk_level="low",
        next_action="confirm",
    )


def verify_linter_behavior(errors: list[str]) -> None:
    prompt = PromptPackage(
        title="Test Hook",
        creative_brief="test",
        lyrics="[Verse]\n一句太短\n[Chorus]\n没有标题",
        style="genre: pop rock r&b edm folk jazz metal; vocal: imitate reference singer voice like 周杰伦; instrumentation: piano, guitar; production: bright; mood: emotional",
        exclude="piano, robotic vocal",
        model_settings="Audio Influence: 40",
        batch_plan="2 candidates",
        review_rubric="first_20s",
        changed_variable="style",
    )
    issues = lint_prompt(prompt, fake_route())
    codes = {issue.code for issue in issues}
    for code in ["genre_soup", "artist_name_risk", "voice_imitation_risk", "exclude_conflict", "lyrics_too_short", "missing_hook", "slider_conflict"]:
        if code not in codes:
            errors.append(f"prompt linter did not catch {code}")


def verify_feedback_mapping(errors: list[str]) -> None:
    cases = {
        "A 版人声好，但副歌不够炸": "vocal_identity",
        "副歌没有记忆点": "topline_or_chorus_lift",
        "歌词太空泛": "lyrics_context",
        "律动太机械": "groove",
        "太像参考曲": "reference_distance",
    }
    for text, expected in cases.items():
        actual = feedback_to_variable(text)
        if actual != expected:
            errors.append(f"feedback mapping failed for {text!r}: expected {expected}, got {actual}")


def verify_direct_build(errors: list[str]) -> None:
    ordinary = build_effect_first_run(None, "想做一首夜晚开车听的华语女声，伤感但不苦", "A 版人声好，但副歌不够炸")
    if ordinary.route.decision != "ordinary_generation":
        errors.append("ordinary brief should build ordinary_generation run")
    for segment in ["genre:", "vocal:", "instrumentation:", "production:", "mood:"]:
        if segment not in ordinary.prompt.style:
            errors.append(f"prompt builder missing style segment: {segment}")
    for field in TAKE_REVIEW_FIELDS:
        if field not in ordinary.take_review.fields:
            errors.append(f"take review missing field: {field}")
    for field in USER_PREFERENCE_FIELDS:
        if field not in ordinary.preference.fields:
            errors.append(f"user preference missing field: {field}")

    unsafe = build_effect_first_run(None, "上传一首第三方商业发行曲作为参考曲，用 Cover 做一首很像的歌，但没有授权", "")
    if unsafe.route.decision != "blocked_reference_upload_use_listen_only_dna":
        errors.append("unsafe third-party upload should route to listen-only DNA fallback")
    if "no artist name" not in unsafe.reference_dna.do_not_copy:
        errors.append("reference DNA do_not_copy boundary is too weak")


def fill_chord_skeleton_ready(project: Path) -> None:
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

File: 02_references/audio/chord-skeleton.mid
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
Do-not-copy: no melody, lyrics, riff, voice, sample, original arrangement, artist name, or song title

Seed file: 02_references/audio/chord-skeleton.mid
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


def verify_chord_skeleton_builder(errors: list[str], tmp: Path) -> None:
    good = scaffold(tmp)
    fill_chord_skeleton_ready(good)
    good_result = run(
        [
            sys.executable,
            str(BUILD_SKELETON),
            "--project-root",
            str(good),
            "--write",
            "--allow-overwrite",
            "--strict",
        ]
    )
    if good_result.returncode != 0:
        errors.append(f"safe chord skeleton builder failed: {good_result.stdout} {good_result.stderr}")
    midi = good / "02_references" / "audio" / "chord-skeleton.mid"
    if not midi.exists() or not midi.read_bytes().startswith(b"MThd"):
        errors.append("safe chord skeleton builder did not write a valid MIDI header")
    report = read(good / "02_references" / "chord-skeleton-build-report.md")
    for term in [
        "Generated by: tools/build_music_chord_skeleton_seed.py",
        "Decision: pass",
        "long block chords only",
        "not uploaded",
        "melody",
        "lyrics",
        "riff",
        "voice",
        "sample",
        "artist name",
        "song title",
    ]:
        if term not in report:
            errors.append(f"chord skeleton build report missing term: {term}")

    bad = scaffold(tmp / "bad-root")
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
    bad_result = run(
        [
            sys.executable,
            str(BUILD_SKELETON),
            "--project-root",
            str(bad),
            "--write",
            "--allow-overwrite",
            "--strict",
        ]
    )
    if bad_result.returncode == 0:
        errors.append("unsafe third-party chord skeleton builder should fail strict mode")
    if (bad / "02_references" / "audio" / "chord-skeleton.mid").exists():
        errors.append("unsafe third-party chord skeleton builder should not write MIDI")
    if "third_party_upload_not_allowed" not in read(bad / "02_references" / "chord-skeleton-build-report.md"):
        errors.append("unsafe chord skeleton report should include third_party_upload_not_allowed")


def main() -> int:
    errors: list[str] = []
    required_paths = [PLAN, SKILL, EFFECT_REF, LOCAL_REF, UPLOAD_REF, PREPARE, PLANNER, BUILD_SKELETON, SCAFFOLD, LOOP_PROMPT]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing required path: {path}")

    compile_result = run([sys.executable, "-m", "py_compile", str(PREPARE), str(PLANNER), str(BUILD_SKELETON), str(SCAFFOLD), __file__])
    if compile_result.returncode != 0:
        errors.append(f"py_compile failed: {compile_result.stderr}")

    ordinary = run([sys.executable, str(PREPARE), "--brief", "想做一首夜晚开车听的华语女声，伤感但不苦", "--feedback", "A 版人声好，但副歌不够炸"])
    if ordinary.returncode != 0:
        errors.append(f"ordinary effect-first CLI failed: {ordinary.stderr}")
    for term in [
        "Effect-First Suno Run",
        "Route decision: ordinary_generation",
        "Generation Confirmation Card",
        "Prompt Linter",
        "SunoCreatePage.open",
        "Data Models",
        "Main State Machine",
        "User Preference Profile",
    ]:
        if term not in ordinary.stdout:
            errors.append(f"ordinary effect-first output missing term: {term}")

    unsafe = run([sys.executable, str(PREPARE), "--brief", "上传一首第三方商业发行曲作为参考曲，用 Cover 做一首很像的歌，但没有授权"])
    if unsafe.returncode != 0:
        errors.append(f"unsafe effect-first CLI failed: {unsafe.stderr}")
    for term in ["blocked_reference_upload_use_listen_only_dna", "blocked; use listen-only DNA text route", "no artist name"]:
        if term not in unsafe.stdout:
            errors.append(f"unsafe effect-first output missing term: {term}")

    verify_linter_behavior(errors)
    verify_feedback_mapping(errors)
    verify_direct_build(errors)

    with tempfile.TemporaryDirectory(prefix="ai-music-effect-first-") as tmp_name:
        project = scaffold(Path(tmp_name))
        for rel in [
            "00_admin/effect-first-suno-run.md",
            "04_prompt/effect-first-prompt-package.md",
            "04_prompt/prompt-linter-report.md",
            "02_references/reference-dna-card.md",
            "02_references/chord-skeleton-build-report.md",
            "06_review/effect-first-take-review.md",
            "12_catalog-memory/user-preference-profile.md",
        ]:
            if not (project / rel).exists():
                errors.append(f"scaffold missing effect-first file: {rel}")
        prepare = run(
            [
                sys.executable,
                str(PREPARE),
                "--project-root",
                str(project),
                "--brief",
                "想做一首夜晚开车听的华语女声，伤感但不苦",
                "--feedback",
                "A 版人声好，但副歌不够炸",
                "--write",
                "--allow-overwrite",
            ]
        )
        if prepare.returncode != 0:
            errors.append(f"project effect-first write failed: {prepare.stdout} {prepare.stderr}")
        main_text = read(project / "00_admin" / "effect-first-suno-run.md")
        for term in [
            "Generated by: tools/prepare_music_effect_first_suno_run.py",
            "Route Card",
            "Generation Confirmation Card",
            "Prompt Linter",
            "Generation Executor Contract",
            "Data Models",
            "Blocker States",
            "Take Review",
            "User Preference Profile",
        ]:
            if term not in main_text:
                errors.append(f"written effect-first run missing term: {term}")
        linter_text = read(project / "04_prompt" / "prompt-linter-report.md")
        for code in PROMPT_LINTER_CODES:
            if code not in linter_text:
                errors.append(f"prompt linter report missing required code: {code}")
        verify_chord_skeleton_builder(errors, Path(tmp_name) / "chord")

    docs = {
        PLAN: ["效果优先", "Route Planner", "Prompt Linter", "Take Reviewer", "Memory Learner"],
        SKILL: ["Effect-First Run Preparation", "prepare_music_effect_first_suno_run.py", "Prompt Builder", "Prompt Linter", "Reference DNA", "build_music_chord_skeleton_seed.py"],
        EFFECT_REF: ["Effect-First Orchestration", "Prompt Builder", "Prompt Linter", "Reference DNA Builder", "Memory Learner", "build_music_chord_skeleton_seed.py"],
        LOCAL_REF: ["00_admin/effect-first-suno-run.md", "prepare_music_effect_first_suno_run.py", "chord-skeleton-build-report.md"],
        UPLOAD_REF: ["prepare_music_effect_first_suno_run.py", "Prompt Builder", "Prompt Linter", "Reference DNA", "build_music_chord_skeleton_seed.py"],
        LOOP_PROMPT: ["Prompt Builder", "Prompt Linter", "Memory Learner", "Self-regression tests"],
    }
    for path, terms in docs.items():
        text = read(path)
        for term in terms:
            if term not in text:
                errors.append(f"{path} missing term: {term}")

    constants = {
        "data model": DATA_MODELS,
        "main state": MAIN_STATE_MACHINE,
        "reference upload state": REFERENCE_UPLOAD_STATE_MACHINE,
        "blocker": BLOCKER_STATES,
        "executor state": GENERATION_EXECUTOR_STATES,
        "sensitive action": SENSITIVE_ACTIONS,
    }
    for label, values in constants.items():
        if not values:
            errors.append(f"{label} constants are empty")

    if errors:
        print("Effect-first Suno Producer verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Effect-first Suno Producer verification passed.")
    print(f"tool: {PREPARE}")
    print(f"skill: {SKILL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
