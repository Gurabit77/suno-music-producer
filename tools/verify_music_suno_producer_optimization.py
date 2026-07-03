#!/usr/bin/env python3
"""Verify the local Suno Music Producer skill optimization package.

This verifier checks that the personal Codex skill has moved beyond a basic
"write prompt and click Suno" flow into the productized workflow described in
the desktop optimization plan:

  /path/to/private-product-plan.md

It intentionally verifies local skill/docs only. It must not open Chrome,
contact Suno, spend credits, or require account state.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path("/path/to/codex-skills/suno-music-producer")
PLAN = Path("/path/to/private-product-plan.md")
QUICK_VALIDATE = Path("/path/to/codex-skills/.system/skill-creator/scripts/quick_validate.py")

REQUIRED_FILES = {
    "skill": SKILL_ROOT / "SKILL.md",
    "openai_yaml": SKILL_ROOT / "agents" / "openai.yaml",
    "prompt_methodology": SKILL_ROOT / "references" / "prompt-methodology.md",
    "chrome_generation": SKILL_ROOT / "references" / "chrome-suno-generation.md",
    "reference_upload_generation": SKILL_ROOT / "references" / "reference-upload-generation.md",
    "local_project": SKILL_ROOT / "references" / "local-ai-music-project.md",
    "extract_script": SKILL_ROOT / "scripts" / "extract_suno_payload.py",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def all_skill_text() -> str:
    parts: list[str] = []
    for path in sorted(SKILL_ROOT.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".yaml", ".py"}:
            parts.append(f"\n\n# FILE: {path}\n")
            parts.append(read(path))
    return "\n".join(parts)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).casefold()


def require_terms(text: str, label: str, terms: list[str], errors: list[str]) -> None:
    lowered = text.casefold()
    missing = [term for term in terms if term.casefold() not in lowered]
    if missing:
        errors.append(f"{label} missing terms: {', '.join(missing)}")


def require_any(text: str, label: str, terms: list[str], errors: list[str]) -> None:
    lowered = text.casefold()
    if not any(term.casefold() in lowered for term in terms):
        errors.append(f"{label} missing any of: {', '.join(terms)}")


def require_regex(text: str, label: str, pattern: str, errors: list[str]) -> None:
    if not re.search(pattern, text, re.I | re.S):
        errors.append(f"{label} missing pattern: {pattern}")


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def verify_extract_script(errors: list[str]) -> None:
    script = REQUIRED_FILES["extract_script"]
    code, output = run([sys.executable, "-m", "py_compile", str(script)])
    if code != 0:
        errors.append(f"extract script py_compile failed: {output}")
        return

    sample = """# Prompt Package v001
Decision: compile approved

## Metadata

- Title: Test Song
- Model: v5.5
- Weirdness: 30
- Style Influence: 70
- Audio Influence: n/a
- Vocal Gender: female
- Instrumental: false
- Exclude: robotic vocal, muddy mix

## Style Of Music

```text
genre: "pop, 120 BPM"
vocal: "clear lead"
```

## Lyrics

```text
[Verse 1]
line one
```
"""
    sample_path = SKILL_ROOT / "scripts" / ".extract_suno_payload_sample.md"
    sample_path.write_text(sample, encoding="utf-8")
    try:
        code, output = run([sys.executable, str(script), str(sample_path), "--json"])
    finally:
        sample_path.unlink(missing_ok=True)
    if code != 0:
        errors.append(f"extract script sample run failed: {output}")
        return
    require_terms(output, "extract script JSON output", ["Test Song", "style_of_music", "lyrics", "exclude"], errors)


def main() -> int:
    errors: list[str] = []

    if not SKILL_ROOT.exists():
        errors.append(f"skill root missing: {SKILL_ROOT}")
    if not PLAN.exists():
        errors.append(f"optimization plan missing: {PLAN}")

    for name, path in REQUIRED_FILES.items():
        if not path.exists():
            errors.append(f"required file missing ({name}): {path}")

    if errors:
        print("Suno Music Producer optimization verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    skill = read(REQUIRED_FILES["skill"])
    chrome = read(REQUIRED_FILES["chrome_generation"])
    methodology = read(REQUIRED_FILES["prompt_methodology"])
    corpus = all_skill_text()
    flat = compact(corpus)

    if "todo" in skill.casefold():
        errors.append("SKILL.md still contains TODO text")

    code, output = run([sys.executable, str(QUICK_VALIDATE), str(SKILL_ROOT)])
    if code != 0:
        errors.append(f"skill quick_validate failed: {output}")

    require_terms(
        corpus,
        "four operating modes",
        [
            "quick_idea",
            "guided_creation",
            "professional_project",
            "iterate_existing_take",
            "快速灵感",
            "引导创作",
            "专业制作",
            "迭代修歌",
        ],
        errors,
    )

    require_terms(
        corpus,
        "mode router",
        ["request_type", "lyrics_only", "prompt_only", "reference_upload_generation", "chrome_generation"],
        errors,
    )

    require_terms(
        corpus,
        "reference upload generation mode",
        [
            "Reference Upload",
            "参考曲上传模式",
            "chord-skeleton-transfer.md",
            "chord-skeleton-transfer-audit.md",
            "audio-rights-ledger.md",
            "retention-target.md",
            "prompt-pairing.md",
            "确认上传并生成",
        ],
        errors,
    )

    require_terms(
        corpus,
        "generation confirmation card",
        ["生成确认卡", "Title", "Style of Music", "Exclude", "batch", "credits", "确认生成"],
        errors,
    )

    require_terms(
        corpus,
        "prompt diff",
        ["Prompt Diff", "Before", "After", "changed variable", "保持不变"],
        errors,
    )

    require_terms(
        corpus,
        "take review table",
        [
            "Take Review",
            "first_20s",
            "hook_memory",
            "vocal_identity",
            "lyrics_intelligibility",
            "ai_artifacts",
            "next_action",
        ],
        errors,
    )

    require_terms(
        corpus,
        "prompt linter",
        [
            "Prompt Linter",
            "style_generic_terms",
            "exclude_conflict",
            "lyrics_too_dense",
            "artist_name_risk",
            "genre_soup",
            "blocker",
        ],
        errors,
    )

    require_terms(
        corpus,
        "user preference profile",
        [
            "User Preference",
            "default_language",
            "preferred_genres",
            "preferred_vocals",
            "avoid_styles",
            "default_exclude",
        ],
        errors,
    )

    require_terms(
        corpus,
        "preset library",
        ["Prompt Preset", "preset_id", "bpm_range", "recommended_exclude", "不适合场景"],
        errors,
    )

    require_terms(
        corpus,
        "data models",
        ["SongRun", "PromptVersion", "Batch", "Take", "ReviewScore"],
        errors,
    )

    require_terms(
        chrome,
        "chrome page object and state model",
        [
            "SunoCreatePage",
            "ensure_logged_in",
            "set_lyrics",
            "set_style",
            "upload_audio_seed",
            "click_generate",
            "collect_take_metadata",
            "blocked_login",
            "blocked_captcha",
            "blocked_credit",
            "blocked_payment",
            "blocked_ui_unknown",
            "failed_timeout",
        ],
        errors,
    )

    require_terms(
        methodology,
        "first-principles prompt method",
        ["Field Responsibilities", "Style Field Formula", "Reference Handling", "Generation Discipline"],
        errors,
    )

    require_any(corpus, "desktop plan citation", [str(PLAN), "自动化项目优化方案书"], errors)
    require_regex(
        flat,
        "explicit no-unattended-account-action boundary",
        r"(do not|不要).{0,120}(generate|click|spend|publish|上传|发布|额度|付款).{0,160}(confirm|确认|approval)",
        errors,
    )
    require_regex(
        flat,
        "offline verifier boundary",
        r"(do not|不要).{0,120}(chrome|suno|browser|账号|浏览器).{0,160}(during validation|验证|verifier|测试)",
        errors,
    )

    verify_extract_script(errors)

    if errors:
        print("Suno Music Producer optimization verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Suno Music Producer optimization verification passed.")
    print(f"skill: {SKILL_ROOT}")
    print(f"plan: {PLAN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
