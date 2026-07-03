#!/usr/bin/env python3
"""Audit lyrics prosody before an AI music prompt is compiled.

The audit is intentionally lightweight and conservative. It does not replace a
songwriter or vocal director; it checks whether the current lyrics/context have
the minimum singability evidence needed before generation.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LYRICS_FILE = "04_prompt/lyrics-context-map.md"
PROSODY_FILE = "03_writing/prosody-check.md"
PROMPT_BRIEF_FILE = "04_prompt/prompt-compile-brief.md"
SONG_BRIEF_FILE = "01_brief/song-brief.md"
DEFAULT_OUTPUT = "03_writing/lyrics-prosody-audit.md"

EMPTY_VALUES = {"", '""', "''", "todo", "tbd", "n/a", "na", "none", "-", "--"}

SECTION_NAMES = {
    "intro",
    "verse",
    "pre-chorus",
    "pre chorus",
    "prechorus",
    "chorus",
    "bridge",
    "final chorus",
    "outro",
}

ENGLISH_FUNCTION_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}

MANDARIN_FUNCTION_ENDINGS = ("的", "了", "着", "在", "和", "与", "而")
COMMON_AI_CLICHES = {
    "neon",
    "static",
    "echoes",
    "void",
    "fragments",
    "shattered",
    "city lights",
    "midnight rain",
    "endless night",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    route: str


@dataclass(frozen=True)
class LyricLine:
    section: str
    text: str
    unit_count: int


def read_project(project_root: Path) -> dict[str, str]:
    docs: dict[str, str] = {}
    for path in project_root.rglob("*.md"):
        rel = path.relative_to(project_root).as_posix()
        try:
            docs[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            docs[rel] = path.read_text(errors="replace")
    return docs


def normalize_value(raw: str) -> str:
    value = raw.strip().strip("`")
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1].strip()
    value = re.sub(r"\s+", " ", value)
    return "" if value.casefold() in EMPTY_VALUES else value


def scan_key_values(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        match = re.match(r"^([^:]{1,80}):\s*(.*)$", stripped)
        if match:
            label = re.sub(r"\s+", " ", match.group(1).strip()).casefold()
            value = normalize_value(match.group(2))
            pairs.append((label, value))
    return pairs


def extract_value(docs: dict[str, str], paths: list[str], labels: list[str]) -> str:
    wanted = {re.sub(r"\s+", " ", label.strip()).casefold() for label in labels}
    for rel in paths:
        for label, value in scan_key_values(docs.get(rel, "")):
            if label in wanted and value:
                return value
    return ""


def extract_code_blocks(text: str) -> list[str]:
    return [block.strip() for block in re.findall(r"```(?:text|markdown)?\s*\n(.*?)```", text, flags=re.S)]


def extract_lyrics_block(docs: dict[str, str]) -> str:
    text = docs.get(LYRICS_FILE, "")
    for block in extract_code_blocks(text):
        if "[Verse" in block or "[Chorus" in block or "[Intro" in block:
            return block.strip()

    lines: list[str] = []
    capture = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and "]" in stripped:
            capture = True
        if capture and stripped and not stripped.startswith("#"):
            lines.append(stripped)
            if stripped == "[End]":
                break
    return "\n".join(lines).strip()


def extract_bracket_value(block: str, label: str) -> str:
    pattern = rf"^\[\s*{re.escape(label)}\s*:\s*(.*?)\s*\]$"
    for line in block.splitlines():
        match = re.match(pattern, line.strip(), flags=re.I)
        if match:
            return normalize_value(match.group(1))
    return ""


def section_name(tag: str) -> str:
    inner = tag.strip()[1:-1].strip().casefold()
    head = inner.split("|", 1)[0].strip()
    head = re.sub(r"\s+\d+$", "", head)
    return head


def is_section_tag(line: str) -> bool:
    stripped = line.strip()
    if not (stripped.startswith("[") and "]" in stripped):
        return False
    head = section_name(stripped)
    return head in SECTION_NAMES or head.startswith("verse") or head.endswith("chorus")


def count_units(line: str, language: str) -> int:
    cleaned = re.sub(r"\([^)]*\)", "", line)
    cjk = re.findall(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", cleaned)
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", cleaned)
    if language_kind(language) == "en":
        return sum(max(1, len(re.findall(r"[aeiouy]+", word.casefold()))) for word in words)
    return len(cjk) + len(words)


def language_kind(language: str) -> str:
    text = language.casefold()
    if any(term in text for term in ["zh", "中文", "华语", "mandarin", "chinese"]):
        return "zh"
    if any(term in text for term in ["ja", "jp", "日本", "日语", "japanese"]):
        return "ja"
    if any(term in text for term in ["ko", "kr", "韩", "korean"]):
        return "ko"
    if any(term in text for term in ["en", "英语", "english"]):
        return "en"
    return "mixed"


def thresholds(language: str, section: str) -> tuple[int, int]:
    kind = language_kind(language)
    chorus = "chorus" in section
    base = {
        "zh": (14 if chorus else 18, 24 if chorus else 28),
        "ja": (22 if chorus else 30, 34 if chorus else 42),
        "ko": (20 if chorus else 28, 32 if chorus else 38),
        "en": (11 if chorus else 15, 17 if chorus else 22),
        "mixed": (16 if chorus else 22, 28 if chorus else 34),
    }
    return base[kind]


def parse_lyric_lines(block: str, language: str) -> tuple[list[LyricLine], list[str]]:
    current = "unsectioned"
    tags: list[str] = []
    lyric_lines: list[LyricLine] = []
    for raw in block.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("[") and "]" in stripped:
            tags.append(stripped)
            if is_section_tag(stripped):
                current = section_name(stripped)
            continue
        if stripped.startswith("#") or stripped.startswith("|"):
            continue
        if re.match(r"^[A-Za-z ]{1,32}:\s*", stripped):
            continue
        lyric_lines.append(LyricLine(current, stripped, count_units(stripped, language)))
    return lyric_lines, tags


def section_metrics(lines: list[LyricLine]) -> dict[str, tuple[int, float, int]]:
    grouped: dict[str, list[int]] = {}
    for line in lines:
        grouped.setdefault(line.section, []).append(line.unit_count)
    metrics: dict[str, tuple[int, float, int]] = {}
    for section, counts in grouped.items():
        metrics[section] = (len(counts), sum(counts) / len(counts), max(counts))
    return metrics


def title_in_chorus(lines: list[LyricLine], title_phrase: str) -> bool:
    if not title_phrase:
        return False
    compact_title = re.sub(r"\s+", "", title_phrase.casefold())
    for line in lines:
        if "chorus" in line.section:
            compact_line = re.sub(r"\s+", "", line.text.casefold())
            if compact_title and compact_title in compact_line:
                return True
    return False


def analyze(docs: dict[str, str]) -> tuple[str, str, str, list[LyricLine], list[str], list[Finding]]:
    language = extract_value(
        docs,
        [PROMPT_BRIEF_FILE, SONG_BRIEF_FILE, LYRICS_FILE, PROSODY_FILE],
        ["Language", "Language lane"],
    )
    title_phrase = extract_value(
        docs,
        [PROMPT_BRIEF_FILE, SONG_BRIEF_FILE, LYRICS_FILE, PROSODY_FILE, "03_writing/title-phrase.md"],
        ["Title phrase", "Hook phrase", "Chorus title phrase"],
    )
    prosody_notes = extract_value(
        docs,
        [LYRICS_FILE, PROSODY_FILE],
        ["Prosody notes", "Prosody", "Diction", "Singability", "Natural stress / tone notes"],
    )
    block = extract_lyrics_block(docs)
    if not prosody_notes and block:
        prosody_notes = extract_bracket_value(block, "Prosody notes")
    lines, tags = parse_lyric_lines(block, language)
    findings: list[Finding] = []

    if not language:
        findings.append(Finding("blocker", "language_missing", "Language is missing; prosody thresholds cannot be selected.", "repair song brief"))
    if not title_phrase:
        findings.append(Finding("blocker", "title_phrase_missing", "Title phrase or chorus hook is missing.", "route to topline workflow"))
    if not prosody_notes:
        findings.append(Finding("blocker", "prosody_notes_missing", "Prosody notes are missing before generation.", "fill prosody-check.md"))
    if not block:
        findings.append(Finding("blocker", "lyrics_block_missing", "Lyrics context map has no section-tagged lyrics block.", "repair lyrics-context-map.md"))
    if not any("[verse" in tag.casefold() for tag in tags):
        findings.append(Finding("blocker", "verse_missing", "Lyrics block needs a Verse tag.", "repair lyrics structure"))
    if not any("[chorus" in tag.casefold() or "[final chorus" in tag.casefold() for tag in tags):
        findings.append(Finding("blocker", "chorus_missing", "Lyrics block needs a Chorus tag.", "repair lyrics structure"))
    if lines and not title_in_chorus(lines, title_phrase):
        findings.append(Finding("blocker", "title_phrase_not_in_chorus", "Title phrase must appear in a chorus line before prompt compile.", "repair chorus hook"))

    for lyric_line in lines:
        soft, hard = thresholds(language, lyric_line.section)
        if lyric_line.unit_count > hard:
            findings.append(
                Finding(
                    "blocker",
                    "line_too_long",
                    f"{lyric_line.section} line is too long to be reliably sung ({lyric_line.unit_count} units): {lyric_line.text}",
                    "split line or reduce syllables",
                )
            )
        elif lyric_line.unit_count > soft:
            findings.append(
                Finding(
                    "warning",
                    "line_dense",
                    f"{lyric_line.section} line is dense ({lyric_line.unit_count} units): {lyric_line.text}",
                    "check breath and melody landing",
                )
            )

    metrics = section_metrics(lines)
    verse_avgs = [avg for section, (_, avg, _) in metrics.items() if section.startswith("verse")]
    chorus_avgs = [avg for section, (_, avg, _) in metrics.items() if "chorus" in section]
    if verse_avgs and chorus_avgs and max(chorus_avgs) > max(verse_avgs) * 1.25:
        findings.append(
            Finding(
                "warning",
                "chorus_denser_than_verse",
                "Chorus is much denser than verse; hook may not breathe.",
                "shorten chorus or move detail into verse",
            )
        )

    if language_kind(language) == "en" and title_phrase:
        last = re.findall(r"[A-Za-z]+", title_phrase.casefold())
        if last and last[-1] in ENGLISH_FUNCTION_WORDS:
            findings.append(Finding("warning", "title_ends_function_word", "English title phrase ends on a function word.", "move hook landing to content word"))
    if language_kind(language) == "zh" and title_phrase and title_phrase.endswith(MANDARIN_FUNCTION_ENDINGS):
        findings.append(Finding("warning", "mandarin_title_function_ending", "Mandarin title phrase may end on a weak function/aspect word.", "verify long-note landing"))

    lowered = "\n".join(line.text.casefold() for line in lines)
    cliche_hits = sorted(term for term in COMMON_AI_CLICHES if term in lowered)
    if len(cliche_hits) >= 3:
        findings.append(
            Finding(
                "warning",
                "ai_cliche_cluster",
                "Several common AI-lyric cliches appear together: " + ", ".join(cliche_hits),
                "run cliche-cut.md before prompt compile",
            )
        )

    return language, title_phrase, prosody_notes, lines, tags, findings


def recommended_tags(language: str) -> str:
    kind = language_kind(language)
    return {
        "zh": "natural Mandarin phrasing, title phrase on stable long vowel, clear diction",
        "ja": "agile Japanese verse phrasing, chorus title phrase on long vowel, dense but intelligible",
        "ko": "short Korean-English hook, crisp consonant rhythm, distinct vocal handoff",
        "en": "conversational English phrasing, stressed words on strong beats, crisp consonants",
        "mixed": "natural language phrasing, short chorus hook, clear diction",
    }[kind]


def recommended_exclude(language: str) -> str:
    kind = language_kind(language)
    return {
        "zh": "awkward translated Mandarin, forced rhyme, long notes on function words, unclear diction",
        "ja": "overstuffed Japanese lyrics, chorus without long note, muddy consonants",
        "ko": "random rap verse, childish chant, anonymous group vocals, overstacked English hook",
        "en": "generic heartbreak cliches, long notes on function words, forced rhyme, vague abstract imagery",
        "mixed": "unclear diction, forced rhyme, overstuffed lyrics, vague abstract imagery",
    }[kind]


def render_finding_table(findings: list[Finding]) -> str:
    if not findings:
        return "| severity | code | message | route |\n|---|---|---|---|\n| pass | none | lyrics prosody approved | prompt compile |\n"
    rows = ["| severity | code | message | route |", "|---|---|---|---|"]
    for finding in findings:
        rows.append(f"| {finding.severity} | {finding.code} | {finding.message} | {finding.route} |")
    return "\n".join(rows) + "\n"


def render_metrics(lines: list[LyricLine]) -> str:
    metrics = section_metrics(lines)
    if not metrics:
        return "| section | lines | average units | max units |\n|---|---:|---:|---:|\n| none | 0 | 0.0 | 0 |\n"
    rows = ["| section | lines | average units | max units |", "|---|---:|---:|---:|"]
    for section in sorted(metrics):
        count, avg, max_count = metrics[section]
        rows.append(f"| {section} | {count} | {avg:.1f} | {max_count} |")
    return "\n".join(rows) + "\n"


def render_audit(project_root: Path, language: str, title_phrase: str, prosody_notes: str, lines: list[LyricLine], tags: list[str], findings: list[Finding]) -> str:
    blockers = [finding for finding in findings if finding.severity == "blocker"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    decision = "pass" if not blockers else "repair before prompt compile"
    return f"""# Lyrics Prosody Audit

Generated by: tools/audit_music_lyrics_prosody.py
Project root: {project_root}
Decision: {decision}

Language: {language or 'NEEDS_REPAIR: language'}
Title phrase: {title_phrase or 'NEEDS_REPAIR: title phrase'}
Prosody notes: {prosody_notes or 'NEEDS_REPAIR: prosody notes'}
Section tags: {len(tags)}
Lyric lines: {len(lines)}
Blockers: {len(blockers)}
Warnings: {len(warnings)}

## Section Metrics

{render_metrics(lines)}
## Findings

{render_finding_table(findings)}
## Prompt Routing

Lyrics tags: {recommended_tags(language)}
Exclude additions: {recommended_exclude(language)}
Blind-listening red flags: unclear diction, title phrase not recalled, awkward stress/tone, breathless chorus, over-dense lyric line

## Line Audit

| section | units | lyric line |
|---|---:|---|
{chr(10).join(f'| {line.section} | {line.unit_count} | {line.text} |' for line in lines) if lines else '| none | 0 | |'}
"""


def write_if_allowed(path: Path, text: str, allow_overwrite: bool) -> None:
    if path.exists() and not allow_overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Song project root created by create_music_song_project.py.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Relative output path.")
    parser.add_argument("--write", action="store_true", help="Write the audit markdown file.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow overwriting an existing audit file.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when blockers remain.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"error: project root not found: {project_root}", file=sys.stderr)
        return 2

    docs = read_project(project_root)
    language, title_phrase, prosody_notes, lines, tags, findings = analyze(docs)
    audit = render_audit(project_root, language, title_phrase, prosody_notes, lines, tags, findings)
    blockers = [finding for finding in findings if finding.severity == "blocker"]

    if args.write:
        try:
            write_if_allowed(project_root / args.output, audit, args.allow_overwrite)
        except FileExistsError as exc:
            print(f"error: output exists, use --allow-overwrite: {exc}", file=sys.stderr)
            return 2
    else:
        print(audit)

    if blockers:
        print(f"lyrics prosody audit has {len(blockers)} blocker(s).", file=sys.stderr)
        for finding in blockers:
            print(f"- {finding.code}: {finding.message} -> {finding.route}", file=sys.stderr)
        return 1 if args.strict else 0

    print("lyrics prosody audit passed.")
    print(f"audit: {project_root / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
