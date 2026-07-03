#!/usr/bin/env python3
"""Compile a song project folder into a Suno-ready prompt package.

The compiler is intentionally conservative. It reads the structured files
created by tools/create_music_song_project.py, builds a prompt package, and
reports blockers before generation. It does not judge taste; it checks whether
the prompt has enough concrete musical intent to avoid common AI-flavor traps.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from audit_music_methodology_transfer import DEFAULT_OUTPUT as METHODOLOGY_AUDIT_FILE
from audit_music_methodology_transfer import MARKER as METHODOLOGY_AUDIT_MARKER
from audit_music_lyric_narrative import DEFAULT_OUTPUT as LYRIC_NARRATIVE_AUDIT_DEFAULT
from audit_music_lyric_narrative import MARKER as LYRIC_NARRATIVE_AUDIT_MARKER
from audit_music_genre_lane_authenticity import DEFAULT_OUTPUT as GENRE_LANE_AUDIT_FILE
from audit_music_genre_lane_authenticity import genre_lane_authenticity_audit_text_ready
from audit_music_prompt_specificity_budget import DEFAULT_OUTPUT as SPECIFICITY_AUDIT_FILE
from audit_music_prompt_specificity_budget import MARKER as SPECIFICITY_AUDIT_MARKER
from audit_music_personalization_hygiene import OUTPUT as PERSONALIZATION_HYGIENE_AUDIT_FILE
from audit_music_personalization_hygiene import personalization_hygiene_required_from_docs
from audit_music_chord_skeleton_transfer import (
    OUTPUT as CHORD_SKELETON_AUDIT_FILE,
    chord_skeleton_transfer_audit_ready_from_docs,
    chord_skeleton_transfer_required_from_docs,
)


STYLE_FILE = "04_prompt/style-field-map.md"
LYRICS_FILE = "04_prompt/lyrics-context-map.md"
EXCLUDE_FILE = "04_prompt/exclude-negative-aesthetic.md"
SLIDER_FILE = "04_prompt/slider-intent-map.md"
IDENTITY_FILE = "04_prompt/persona-voice-model-routing.md"
CONFLICT_FILE = "04_prompt/constraint-conflict-check.md"
REFERENCE_AUDIT_FILE = "02_references/reference-dna-audit.md"
CHORD_SKELETON_TRANSFER_AUDIT_FILE = CHORD_SKELETON_AUDIT_FILE
METHODOLOGY_TRANSFER_AUDIT_FILE = METHODOLOGY_AUDIT_FILE
PROMPT_SPECIFICITY_AUDIT_FILE = SPECIFICITY_AUDIT_FILE
GENRE_LANE_AUTHENTICITY_AUDIT_FILE = GENRE_LANE_AUDIT_FILE
LYRIC_NARRATIVE_AUDIT_FILE = LYRIC_NARRATIVE_AUDIT_DEFAULT
PROSODY_AUDIT_FILE = "03_writing/lyrics-prosody-audit.md"
TOPLINE_AUDIT_FILE = "03_writing/topline-hook-audit.md"
HARMONY_AUDIT_FILE = "03_writing/harmony-bass-audit.md"
GROOVE_AUDIT_FILE = "03_writing/groove-humanization-audit.md"
STRUCTURE_AUDIT_FILE = "03_writing/structure-dynamics-audit.md"
VOCAL_AUDIT_FILE = "03_writing/vocal-identity-audit.md"
PERSONALIZATION_AUDIT_FILE = PERSONALIZATION_HYGIENE_AUDIT_FILE
BRIEF_FILES = [
    "01_brief/song-brief.md",
    "01_brief/project-intake.md",
    "01_brief/success-definition.md",
    "04_prompt/prompt-compile-brief.md",
]
WRITING_FILES = [
    "03_writing/lyric-brief.md",
    "03_writing/title-phrase.md",
    "03_writing/prosody-check.md",
    "03_writing/topline-map.md",
    "03_writing/harmony-brief.md",
    "03_writing/progression-map.md",
    "03_writing/bassline-map.md",
    "03_writing/harmonic-rhythm-map.md",
    "03_writing/cadence-and-bridge-plan.md",
    "03_writing/groove-audit.md",
    "03_writing/drum-realism-map.md",
    "03_writing/instrument-role-map.md",
    "03_writing/section-performance-map.md",
    "03_writing/structure-brief.md",
    "03_writing/energy-map.md",
    "03_writing/section-function-map.md",
    "03_writing/contrast-continuity-matrix.md",
    "03_writing/transition-cue-sheet.md",
    "03_writing/second-verse-development.md",
    "03_writing/bridge-turn-plan.md",
    "03_writing/final-chorus-payoff.md",
    "03_writing/outro-end-plan.md",
    "03_writing/singer-brief.md",
    "03_writing/vocal-performance-map.md",
    "03_writing/vocal-arrangement-map.md",
    "03_writing/performance-brief.md",
]
RIGHTS_FILES = [
    "02_references/rights-and-source-precheck.md",
    "02_references/source-rights-ledger.md",
    "02_references/reference-rights.md",
    "02_references/reference-boundary.md",
    REFERENCE_AUDIT_FILE,
]

DEFAULT_PACKAGE = "04_prompt/prompt-package-v001.md"
DEFAULT_PREFLIGHT = "04_prompt/prompt-preflight-review.md"
DEFAULT_HANDOFF = "04_prompt/experiment-handoff.md"

EMPTY_VALUES = {
    "",
    '""',
    "''",
    "todo",
    "tbd",
    "n/a",
    "na",
    "none",
    "yes/no",
    "pass/fail",
    "-",
    "--",
}

GENERIC_STYLE_TERMS = {
    "emotional",
    "catchy",
    "professional",
    "high quality",
    "viral",
    "hit song",
    "trending",
    "beautiful",
    "powerful",
    "realistic",
}

PROTECTED_IDENTITY_NAMES = [
    "米津玄师",
    "YOASOBI",
    "Ado",
    "Official髭男dism",
    "King Gnu",
    "宇多田光",
    "Perfume",
    "あいみょん",
    "当山",
    "KOKIA",
    "周杰伦",
    "林俊杰",
    "陈奕迅",
    "邓紫棋",
    "薛之谦",
    "毛不易",
    "蔡徐坤",
    "BTS",
    "BLACKPINK",
    "IU",
    "EXO",
    "Stray Kids",
    "NewJeans",
    "aespa",
    "SEVENTEEN",
    "Taylor Swift",
    "The Weeknd",
    "Billie Eilish",
    "Dua Lipa",
    "Olivia Rodrigo",
    "Harry Styles",
    "Drake",
    "Ed Sheeran",
    "ONE OK ROCK",
    "MY FIRST STORY",
    "RADWIMPS",
    "Mrs. GREEN APPLE",
    "BUMP OF CHICKEN",
    "凛として時雨",
    "ASIAN KUNG-FU GENERATION",
    "Babymetal",
    "五月天",
    "万能青年旅店",
    "草东没有派对",
    "痛仰",
    "告五人",
    "回春丹",
    "DAY6",
    "FTISLAND",
    "CNBLUE",
    "JANNABI",
    "The Rose",
    "N.Flying",
    "Xdinary Heroes",
    "LUCY",
    "Arctic Monkeys",
    "Imagine Dragons",
    "Twenty One Pilots",
    "Foo Fighters",
    "Radiohead",
    "Måneskin",
    "Green Day",
    "The 1975",
]


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    route: str


@dataclass
class PromptContext:
    title: str = ""
    project: str = ""
    use_case: str = ""
    audience: str = ""
    language: str = ""
    lane: str = ""
    narrator: str = ""
    situation: str = ""
    title_phrase: str = ""
    hook_promise: str = ""
    methodology_audit_decision: str = ""
    prompt_specificity_audit_decision: str = ""
    genre_lane_authenticity_audit_decision: str = ""
    lyric_narrative_audit_decision: str = ""
    reference_audit_decision: str = ""
    chord_skeleton_transfer_audit_decision: str = ""
    chord_skeleton_transfer_required: bool = False
    topline_audit_decision: str = ""
    harmony_audit_decision: str = ""
    groove_audit_decision: str = ""
    structure_audit_decision: str = ""
    vocal_audit_decision: str = ""
    emotion_arc: str = ""
    genre: str = ""
    tempo_meter: str = ""
    key_mode: str = ""
    vocal: str = ""
    drums_groove: str = ""
    bass_role: str = ""
    harmony_instruments: str = ""
    lead_instruments: str = ""
    instrumentation: str = ""
    production: str = ""
    mood: str = ""
    prosody_notes: str = ""
    prosody_audit_decision: str = ""
    exclude: str = ""
    model: str = ""
    weirdness: str = ""
    style_influence: str = ""
    audio_influence: str = ""
    vocal_gender: str = ""
    instrumental: str = ""
    human_anchor_lane: str = ""
    voice_identity_source: str = ""
    persona_source: str = ""
    custom_model_source: str = ""
    custom_model_corpus: str = ""
    voice_verification: str = ""
    my_taste_state: str = ""
    my_taste_summary: str = ""
    prompt_boost_state: str = ""
    boosted_style_text: str = ""
    identity_rights_status: str = ""
    lyrics_block: str = ""
    package_path: str = DEFAULT_PACKAGE


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
    value = raw.strip()
    value = value.strip("`")
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1].strip()
    value = re.sub(r"\s+", " ", value)
    if value.lower() in EMPTY_VALUES:
        return ""
    if value.startswith("[") and value.endswith("]") and ":" in value:
        return ""
    return value


def scan_key_values(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("|") or stripped.startswith("#"):
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        match = re.match(r"^([^:]{1,80}):\s*(.*)$", stripped)
        if not match:
            continue
        label = re.sub(r"\s+", " ", match.group(1).strip()).casefold()
        value = normalize_value(match.group(2))
        pairs.append((label, value))
    return pairs


def extract_value(docs: dict[str, str], paths: list[str], labels: list[str]) -> str:
    wanted = {re.sub(r"\s+", " ", label.strip()).casefold() for label in labels}
    for rel in paths:
        text = docs.get(rel, "")
        for label, value in scan_key_values(text):
            if label in wanted and value:
                return value
    return ""


def extract_any(docs: dict[str, str], labels: list[str]) -> str:
    wanted = {re.sub(r"\s+", " ", label.strip()).casefold() for label in labels}
    for text in docs.values():
        for label, value in scan_key_values(text):
            if label in wanted and value:
                return value
    return ""


def extract_code_blocks(text: str) -> list[str]:
    return [block.strip() for block in re.findall(r"```(?:text|markdown)?\s*\n(.*?)```", text, flags=re.S)]


def extract_lyrics_block(docs: dict[str, str]) -> str:
    for rel in [LYRICS_FILE]:
        text = docs.get(rel, "")
        for block in extract_code_blocks(text):
            if "[Verse" in block or "[Chorus" in block or "[Intro" in block:
                return block.strip()

    text = docs.get(LYRICS_FILE, "")
    lines: list[str] = []
    capture = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and "]" in stripped:
            capture = True
        if capture:
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            lines.append(stripped)
            if stripped == "[End]":
                break
    return "\n".join(lines).strip()


def collect_exclude(docs: dict[str, str]) -> str:
    explicit = extract_value(docs, [EXCLUDE_FILE], ["Exclude", "Exclude term", "Must-not-have"])
    if explicit:
        return explicit

    text = docs.get(EXCLUDE_FILE, "")
    terms: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        if ":" in stripped:
            label, value = stripped.split(":", 1)
            if label.strip().casefold() in {"exclude term", "must-not-have", "exclude"}:
                value = normalize_value(value)
                if value:
                    terms.append(value)
        elif stripped.startswith("- "):
            value = normalize_value(stripped[2:])
            if value:
                terms.append(value)
    return ", ".join(dict.fromkeys(terms))


def compose_context(docs: dict[str, str]) -> PromptContext:
    all_brief = BRIEF_FILES + WRITING_FILES + [STYLE_FILE, LYRICS_FILE, SLIDER_FILE, IDENTITY_FILE]
    ctx = PromptContext()

    ctx.title = extract_value(docs, all_brief + ["README.md"], ["Song", "Song title", "Title", "Working title"])
    ctx.project = extract_value(docs, all_brief + ["README.md"], ["Project", "Artist / catalog", "Project / artist", "Catalog identity", "Artist project"])
    ctx.use_case = extract_value(docs, all_brief + ["README.md"], ["Use case", "Goal"])
    ctx.audience = extract_value(docs, all_brief, ["Audience", "Listener"])
    ctx.language = extract_value(docs, all_brief + [STYLE_FILE], ["Language", "Language lane"])
    ctx.lane = extract_value(docs, all_brief + [STYLE_FILE], ["Genre lane", "Pop / rock lane", "Lane"])
    ctx.narrator = extract_value(docs, all_brief + WRITING_FILES, ["Narrator", "Singer persona", "Point of view"])
    ctx.situation = extract_value(docs, all_brief + WRITING_FILES, ["Situation", "Scene", "Concrete place"])
    ctx.title_phrase = extract_value(docs, all_brief + WRITING_FILES, ["Title phrase", "Hook phrase", "Chorus title phrase"])
    ctx.hook_promise = extract_value(docs, all_brief + WRITING_FILES, ["Hook promise", "Hook idea", "Hook"])
    ctx.methodology_audit_decision = extract_value(docs, [METHODOLOGY_TRANSFER_AUDIT_FILE], ["Decision"])
    ctx.prompt_specificity_audit_decision = extract_value(docs, [PROMPT_SPECIFICITY_AUDIT_FILE], ["Decision"])
    ctx.genre_lane_authenticity_audit_decision = extract_value(docs, [GENRE_LANE_AUTHENTICITY_AUDIT_FILE], ["Decision"])
    ctx.lyric_narrative_audit_decision = extract_value(docs, [LYRIC_NARRATIVE_AUDIT_FILE], ["Decision"])
    ctx.reference_audit_decision = extract_value(docs, [REFERENCE_AUDIT_FILE], ["Decision"])
    ctx.chord_skeleton_transfer_audit_decision = extract_value(docs, [CHORD_SKELETON_TRANSFER_AUDIT_FILE], ["Decision"])
    ctx.chord_skeleton_transfer_required = chord_skeleton_transfer_required_from_docs(docs)
    ctx.topline_audit_decision = extract_value(docs, [TOPLINE_AUDIT_FILE], ["Decision"])
    ctx.harmony_audit_decision = extract_value(docs, [HARMONY_AUDIT_FILE], ["Decision"])
    ctx.groove_audit_decision = extract_value(docs, [GROOVE_AUDIT_FILE], ["Decision"])
    ctx.structure_audit_decision = extract_value(docs, [STRUCTURE_AUDIT_FILE], ["Decision"])
    ctx.vocal_audit_decision = extract_value(docs, [VOCAL_AUDIT_FILE], ["Decision"])
    ctx.emotion_arc = extract_value(docs, all_brief + WRITING_FILES, ["Emotion arc", "Mood arc", "Emotional arc"])

    ctx.genre = extract_value(docs, [STYLE_FILE], ["genre"])
    ctx.tempo_meter = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["tempo / meter", "tempo", "meter", "tempo feel"])
    ctx.key_mode = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["key / mode", "key", "mode", "harmonic color"])
    ctx.vocal = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["vocal", "singer brief", "vocal identity"])
    ctx.drums_groove = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["drums / groove", "drums", "groove", "groove role"])
    ctx.bass_role = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["bass role", "bass"])
    ctx.harmony_instruments = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["harmony instruments", "harmony instrument", "chords", "harmony"])
    ctx.lead_instruments = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["lead / hook instruments", "lead instrument", "hook instrument"])
    ctx.instrumentation = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["instrumentation", "core instruments"])
    if not ctx.instrumentation:
        ctx.instrumentation = ", ".join(
            part
            for part in [ctx.drums_groove, ctx.bass_role, ctx.harmony_instruments, ctx.lead_instruments]
            if part
        )
    ctx.production = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["production", "production texture", "mix", "space"])
    ctx.mood = extract_value(docs, [STYLE_FILE] + WRITING_FILES, ["mood", "mood / energy arc", "energy arc"])
    if not ctx.mood:
        ctx.mood = ctx.emotion_arc
    ctx.prosody_notes = extract_value(docs, [LYRICS_FILE] + WRITING_FILES, ["Prosody notes", "Prosody", "Diction", "Singability"])
    ctx.prosody_audit_decision = extract_value(docs, [PROSODY_AUDIT_FILE], ["Decision"])

    ctx.exclude = collect_exclude(docs)
    ctx.model = extract_value(docs, [SLIDER_FILE], ["Model"])
    ctx.weirdness = extract_value(docs, [SLIDER_FILE], ["Weirdness"])
    ctx.style_influence = extract_value(docs, [SLIDER_FILE], ["Style Influence"])
    ctx.audio_influence = extract_value(docs, [SLIDER_FILE], ["Audio Influence"])
    ctx.vocal_gender = extract_value(docs, [STYLE_FILE], ["Vocal Gender", "Vocal gender"])
    ctx.instrumental = extract_value(docs, [STYLE_FILE], ["Instrumental"])
    ctx.human_anchor_lane = extract_value(
        docs,
        [IDENTITY_FILE] + all_brief,
        ["Human anchor lane", "Anchor lane", "Feature type"],
    )
    ctx.voice_identity_source = extract_value(docs, [IDENTITY_FILE] + RIGHTS_FILES, ["Voice identity source", "Voice source"])
    ctx.persona_source = extract_value(docs, [IDENTITY_FILE] + RIGHTS_FILES, ["Persona source", "Source song"])
    ctx.custom_model_source = extract_value(docs, [IDENTITY_FILE] + RIGHTS_FILES, ["Custom Model source", "Custom model source"])
    ctx.custom_model_corpus = extract_value(docs, [IDENTITY_FILE] + RIGHTS_FILES, ["Custom model corpus", "Custom Model corpus", "Source song / voice / dataset"])
    ctx.voice_verification = extract_value(docs, [IDENTITY_FILE] + RIGHTS_FILES, ["Voice verification", "Verification status"])
    ctx.my_taste_state = extract_value(docs, [IDENTITY_FILE], ["My Taste state", "My Taste enabled"])
    ctx.my_taste_summary = extract_value(docs, [IDENTITY_FILE], ["My Taste summary"])
    ctx.prompt_boost_state = extract_value(docs, [IDENTITY_FILE], ["Prompt boost state", "Prompt Boost enabled"])
    ctx.boosted_style_text = extract_value(docs, [IDENTITY_FILE], ["Boosted style text", "Boosted prompt"])
    ctx.identity_rights_status = extract_value(docs, [IDENTITY_FILE] + RIGHTS_FILES, ["Rights status", "Identity rights status"])
    ctx.lyrics_block = extract_lyrics_block(docs)
    return ctx


def is_too_generic(value: str) -> bool:
    compact = re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
    if compact in {"pop", "rock", "j pop", "k pop", "c pop", "mandarin pop", "english pop"}:
        return True
    return any(term in compact for term in GENERIC_STYLE_TERMS)


def protected_identity_hits(text: str) -> list[str]:
    hits: list[str] = []
    for name in PROTECTED_IDENTITY_NAMES:
        if not name:
            continue
        if re.fullmatch(r"[A-Za-z0-9 .'\-&]+", name):
            pattern = rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])"
            found = re.search(pattern, text, flags=re.I)
        else:
            found = name.casefold() in text.casefold()
        if found:
            hits.append(name)
    return hits


def methodology_transfer_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(METHODOLOGY_TRANSFER_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        METHODOLOGY_AUDIT_MARKER.casefold() in lowered
        and "decision: pass" in lowered
        and "## methodology transfer evidence" in lowered
        and "local source status: ready" in lowered
        and "external method claims: pass" in lowered
        and "source confidence split:" in lowered
        and "official control surfaces:" in lowered
        and "model/version rationale:" in lowered
        and "primary tool route:" in lowered
        and "human-likeness transfer:" in lowered
        and "variable discipline:" in lowered
        and "anti-magic safeguards:" in lowered
    )


def prompt_specificity_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(PROMPT_SPECIFICITY_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        SPECIFICITY_AUDIT_MARKER.casefold() in lowered
        and "decision: pass" in lowered
        and "## specificity budget evidence" in lowered
        and "methodology transfer: pass" in lowered
        and "style specificity tags:" in lowered
        and "recording realism tags:" in lowered
        and "performance realism tags:" in lowered
        and "section/director tags:" in lowered
        and "field budget tags:" in lowered
        and "prompt compile handoff: pass" in lowered
        and "needs_repair" not in lowered
    )


def genre_lane_authenticity_audit_ready(docs: dict[str, str]) -> bool:
    return genre_lane_authenticity_audit_text_ready(docs.get(GENRE_LANE_AUTHENTICITY_AUDIT_FILE, ""))


def lyric_narrative_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(LYRIC_NARRATIVE_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        LYRIC_NARRATIVE_AUDIT_MARKER.casefold() in lowered
        and "decision: pass" in lowered
        and "## lyric narrative evidence" in lowered
        and "narrator/situation tags:" in lowered
        and "concrete image tags:" in lowered
        and "title phrase function:" in lowered
        and "central metaphor:" in lowered
        and "section information tags:" in lowered
        and "cliche removal:" in lowered
        and "verse 2 development:" in lowered
        and "bridge perspective:" in lowered
        and "lyrics rewrite handoff: pass" in lowered
        and "needs_repair" not in lowered
    )


def prosody_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(PROSODY_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_lyrics_prosody.py".casefold() in lowered
        and "decision: pass" in lowered
        and "lyrics tags:" in lowered
        and "blind-listening red flags:" in lowered
        and "## section metrics" in lowered
    )


def reference_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(REFERENCE_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_reference_dna.py".casefold() in lowered
        and "decision: pass" in lowered
        and "reference tags:" in lowered
        and "style dna tags:" in lowered
        and "protected identity removal:" in lowered
        and "similarity blind test:" in lowered
        and "## reference design" in lowered
    )


def chord_skeleton_transfer_audit_ready(docs: dict[str, str]) -> bool:
    if not chord_skeleton_transfer_required_from_docs(docs):
        return True
    return chord_skeleton_transfer_audit_ready_from_docs(docs)


def topline_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(TOPLINE_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_topline_hook.py".casefold() in lowered
        and "decision: pass" in lowered
        and "topline tags:" in lowered
        and "blind hook test:" in lowered
        and "## hook design" in lowered
    )


def harmony_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(HARMONY_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_harmony_bass.py".casefold() in lowered
        and "decision: pass" in lowered
        and "harmony tags:" in lowered
        and "bass tags:" in lowered
        and "topline/harmony fit:" in lowered
        and "## harmony design" in lowered
    )


def groove_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(GROOVE_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_groove_humanization.py".casefold() in lowered
        and "decision: pass" in lowered
        and "groove tags:" in lowered
        and "instrument performance tags:" in lowered
        and "rhythm-section blind test:" in lowered
        and "## groove design" in lowered
    )


def structure_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(STRUCTURE_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_structure_dynamics.py".casefold() in lowered
        and "decision: pass" in lowered
        and "structure tags:" in lowered
        and "section tags:" in lowered
        and "structure blind test:" in lowered
        and "## structure design" in lowered
    )


def vocal_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(VOCAL_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_vocal_identity.py".casefold() in lowered
        and "decision: pass" in lowered
        and "vocal tags:" in lowered
        and "vocal performance tags:" in lowered
        and "vocal arrangement tags:" in lowered
        and "vocal blind test:" in lowered
        and "## vocal design" in lowered
    )


def personalization_audit_ready(docs: dict[str, str]) -> bool:
    text = docs.get(PERSONALIZATION_AUDIT_FILE, "")
    lowered = text.casefold()
    return (
        "Generated by: tools/audit_music_personalization_hygiene.py".casefold() in lowered
        and "decision: pass" in lowered
        and "personalization hygiene: pass" in lowered
        and "prompt compile handoff: pass" in lowered
    )


def issue_context(ctx: PromptContext, docs: dict[str, str]) -> list[Issue]:
    issues: list[Issue] = []

    required = [
        ("title", ctx.title, "repair brief", "Song title is missing."),
        ("language", ctx.language, "repair brief", "Language is missing."),
        ("human_anchor_lane", ctx.human_anchor_lane, "repair identity routing", "Human anchor lane is missing; choose text-only, audio seed, voice/persona, custom model, or My Taste."),
        ("narrator", ctx.narrator, "route to lyric workflow", "Narrator or point of view is missing."),
        ("title_phrase", ctx.title_phrase or ctx.hook_promise, "route to topline workflow", "Title phrase or hook promise is missing."),
        ("vocal", ctx.vocal, "route to vocal identity workflow", "Vocal identity is missing."),
        ("instrumentation", ctx.instrumentation, "repair style", "Instrumentation is missing."),
        ("production", ctx.production, "repair style", "Production or mix texture is missing."),
        ("mood", ctx.mood, "repair brief", "Mood or energy arc is missing."),
        ("exclude", ctx.exclude, "repair exclude", "Exclude field is missing."),
        ("model", ctx.model, "repair slider intent", "Model/version is missing; generation will not be reproducible."),
        ("weirdness", ctx.weirdness, "repair slider intent", "Weirdness is missing; exploration/convergence intent is unclear."),
        ("style_influence", ctx.style_influence, "repair slider intent", "Style Influence is missing; prompt adherence cannot be attributed."),
    ]
    for code, value, route, message in required:
        if not value:
            issues.append(Issue("blocker", code, message, route))

    if not ctx.genre and not ctx.lane:
        issues.append(Issue("blocker", "genre", "Genre lane is missing.", "repair style"))
    elif is_too_generic(ctx.genre or ctx.lane):
        issues.append(Issue("warning", "generic_genre", "Genre/style field is too generic to be blind-testable.", "repair style"))

    if ctx.vocal and is_too_generic(ctx.vocal):
        issues.append(Issue("warning", "generic_vocal", "Vocal field uses generic adjectives instead of register, diction, and delivery.", "route to vocal identity workflow"))

    if not ctx.lyrics_block:
        issues.append(Issue("blocker", "lyrics_context", "Lyrics context map or section-tagged lyrics block is missing.", "repair lyrics"))
    else:
        lowered = ctx.lyrics_block.casefold()
        if "[verse" not in lowered or "[chorus" not in lowered:
            issues.append(Issue("blocker", "lyrics_sections", "Lyrics block needs at least verse and chorus section tags.", "repair lyrics"))
        if "[bridge" not in lowered and "[final chorus" not in lowered:
            issues.append(Issue("warning", "limited_form", "Lyrics block has no bridge or final-chorus payoff marker.", "route to structure workflow"))

    if not ctx.prosody_notes:
        issues.append(Issue("warning", "prosody", "Prosody notes are missing; language stress and diction may drift.", "route to prosody workflow"))

    if not methodology_transfer_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "methodology_transfer_audit",
                "Methodology transfer audit must be generated by tools/audit_music_methodology_transfer.py and pass before prompt compile.",
                "run audit_music_methodology_transfer.py",
            )
        )

    if not prompt_specificity_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "prompt_specificity_budget_audit",
                "Prompt specificity budget audit must be generated by tools/audit_music_prompt_specificity_budget.py and pass before prompt compile.",
                "run audit_music_prompt_specificity_budget.py",
            )
        )

    if not genre_lane_authenticity_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "genre_lane_authenticity_audit",
                "Genre/lane authenticity audit must be generated by tools/audit_music_genre_lane_authenticity.py and pass before prompt compile.",
                "run audit_music_genre_lane_authenticity.py",
            )
        )

    if not lyric_narrative_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "lyric_narrative_audit",
                "Lyric narrative/cliche-cut audit must be generated by tools/audit_music_lyric_narrative.py and pass before prompt compile.",
                "run audit_music_lyric_narrative.py",
            )
        )

    if not prosody_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "lyrics_prosody_audit",
                "Lyrics prosody audit must be generated by tools/audit_music_lyrics_prosody.py and pass before prompt compile.",
                "run audit_music_lyrics_prosody.py",
            )
        )

    if not reference_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "reference_dna_audit",
                "Reference DNA audit must be generated by tools/audit_music_reference_dna.py and pass before prompt compile.",
                "run audit_music_reference_dna.py",
            )
        )

    if not chord_skeleton_transfer_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "chord_skeleton_transfer_audit",
                "Chord skeleton transfer audit must pass when reference upload, Audio Upload/Cover, nonzero Audio Influence, or chord progression transfer is active.",
                "run audit_music_chord_skeleton_transfer.py",
            )
        )

    if not topline_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "topline_hook_audit",
                "Topline hook audit must be generated by tools/audit_music_topline_hook.py and pass before prompt compile.",
                "run audit_music_topline_hook.py",
            )
        )

    if not harmony_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "harmony_bass_audit",
                "Harmony/bass audit must be generated by tools/audit_music_harmony_bass.py and pass before prompt compile.",
                "run audit_music_harmony_bass.py",
            )
        )

    if not groove_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "groove_humanization_audit",
                "Groove humanization audit must be generated by tools/audit_music_groove_humanization.py and pass before prompt compile.",
                "run audit_music_groove_humanization.py",
            )
        )

    if not structure_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "structure_dynamics_audit",
                "Structure dynamics audit must be generated by tools/audit_music_structure_dynamics.py and pass before prompt compile.",
                "run audit_music_structure_dynamics.py",
            )
        )

    if not vocal_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "vocal_identity_audit",
                "Vocal identity/performance audit must be generated by tools/audit_music_vocal_identity.py and pass before prompt compile.",
                "run audit_music_vocal_identity.py",
            )
        )

    if personalization_hygiene_required_from_docs(docs) and not personalization_audit_ready(docs):
        issues.append(
            Issue(
                "blocker",
                "personalization_hygiene_audit",
                "Personalization hygiene audit must be generated by tools/audit_music_personalization_hygiene.py and pass when Voice, Persona, Custom Model, My Taste, or Prompt Boost is active.",
                "run audit_music_personalization_hygiene.py",
            )
        )

    if not ctx.weirdness or not ctx.style_influence:
        issues.append(Issue("blocker", "sliders", "Model, Weirdness, and Style Influence must be documented before generation.", "repair slider intent"))

    anchor = ctx.human_anchor_lane.casefold()
    if anchor:
        allowed_anchor_terms = ["text", "audio", "seed", "voice", "persona", "custom", "model", "my taste", "taste"]
        if not any(term in anchor for term in allowed_anchor_terms):
            issues.append(
                Issue(
                    "warning",
                    "human_anchor_lane_unknown",
                    f"Human anchor lane is not a known lane: {ctx.human_anchor_lane}.",
                    "repair identity routing",
                )
            )
        if ("voice" in anchor or "persona" in anchor) and not (ctx.voice_identity_source or ctx.persona_source):
            issues.append(
                Issue(
                    "blocker",
                    "identity_source_missing",
                    "Voice/Persona lane requires Voice identity source or Persona source.",
                    "route to voice rights",
                )
            )
        if ("voice" in anchor and ctx.voice_identity_source) and not ctx.voice_verification:
            issues.append(
                Issue(
                    "blocker",
                    "voice_verification_missing",
                    "Voice lane requires voice verification status before generation.",
                    "route to voice rights",
                )
            )
        if "custom" in anchor and not (ctx.custom_model_source or ctx.custom_model_corpus):
            issues.append(
                Issue(
                    "blocker",
                    "custom_model_corpus_missing",
                    "Custom Model lane requires custom model source or corpus evidence.",
                    "route to catalog identity and rights",
                )
            )
        if ("my taste" in anchor or "taste" in anchor) and not (ctx.my_taste_state or ctx.my_taste_summary):
            issues.append(
                Issue(
                    "blocker",
                    "my_taste_state_missing",
                    "My Taste lane requires enabled/disabled state or preference summary.",
                    "repair identity routing",
                )
            )

    if positive_value(ctx.my_taste_state) and not ctx.my_taste_summary:
        issues.append(Issue("blocker", "my_taste_summary_missing", "My Taste is enabled but no preference summary is recorded.", "repair identity routing"))
    if positive_value(ctx.prompt_boost_state) and not ctx.boosted_style_text:
        issues.append(Issue("blocker", "prompt_boost_text_missing", "Prompt Boost is enabled but boosted style text is not recorded.", "repair identity routing"))

    exclude_terms = [term.strip() for term in re.split(r"[,;]", ctx.exclude) if term.strip()]
    if len(exclude_terms) > 12:
        issues.append(Issue("warning", "exclude_overload", "Exclude field has more than 12 terms; attribution may become noisy.", "repair exclude"))

    conflict_decision = extract_value(docs, [CONFLICT_FILE], ["Decision"])
    if conflict_decision and "compile approved" not in conflict_decision.casefold():
        issues.append(Issue("blocker", "conflict_decision", f"Constraint decision is not approved: {conflict_decision}", "repair conflict check"))

    artist_names = extract_value(docs, RIGHTS_FILES + ["04_prompt/source-and-rights-routing.md"], ["Artist names present"])
    song_titles = extract_value(docs, RIGHTS_FILES + ["04_prompt/source-and-rights-routing.md"], ["Song titles present"])
    allowed_action = extract_value(docs, RIGHTS_FILES + ["04_prompt/source-and-rights-routing.md"], ["Allowed action"])
    if (artist_names.casefold() in {"yes", "true"} or song_titles.casefold() in {"yes", "true"}) and not re.search(
        r"neutral|style dna|cleared|abstract|remove", allowed_action, flags=re.I
    ):
        issues.append(Issue("blocker", "protected_identity", "Artist or song names are present without a neutralized allowed action.", "route to reference DNA and rights"))

    generation_text = "\n".join([ctx.genre, ctx.vocal, ctx.instrumentation, ctx.production, ctx.mood, ctx.exclude])
    identity_hits = protected_identity_hits(generation_text)
    if identity_hits:
        preview = ", ".join(identity_hits[:5])
        issues.append(
            Issue(
                "blocker",
                "protected_identity_in_prompt",
                f"Generation-facing fields contain protected artist/band names: {preview}. Translate references into neutral style DNA first.",
                "route to reference DNA and rights",
            )
        )

    voice_source = " ".join(
        part
        for part in [ctx.voice_identity_source, ctx.persona_source, ctx.custom_model_source, ctx.custom_model_corpus, ctx.identity_rights_status]
        if part
    ) or extract_any(docs, ["Voice identity source", "Persona source", "Custom Model source"])
    if re.search(r"third[- ]party|unknown|unclear|unlicensed", voice_source, flags=re.I):
        issues.append(Issue("blocker", "voice_rights", "Voice/Persona/Custom Model source appears unclear or third-party.", "route to voice rights"))

    return issues


def positive_value(value: str) -> bool:
    return bool(re.search(r"\b(yes|enabled|on|true|use|active)\b|开启|使用|启用", value, flags=re.I))


def fallback(value: str, label: str) -> str:
    return value if value else f"NEEDS_REPAIR: {label}"


def style_line(ctx: PromptContext) -> str:
    pieces = [ctx.genre or ctx.lane, ctx.tempo_meter, ctx.key_mode]
    return ", ".join(piece for piece in pieces if piece)


def default_lyrics_block(ctx: PromptContext) -> str:
    intent = ctx.hook_promise or ctx.situation or ctx.emotion_arc or "NEEDS_REPAIR: song intent"
    prosody = ctx.prosody_notes or "NEEDS_REPAIR: prosody notes"
    title = ctx.title_phrase or "NEEDS_REPAIR: title phrase"
    return "\n".join(
        [
            f"[Song intent: {intent}]",
            f"[Prosody notes: {prosody}]",
            "[Intro | short motif | establishes scene]",
            f"[Verse 1 | {ctx.narrator or 'narrator action'} | concrete image]",
            "[Pre-Chorus | rising tension | fewer words]",
            f"[Chorus | {title} | melodic landing]",
            "[Verse 2 | new information | groove deepens]",
            "[Bridge | contrast | new perspective]",
            "[Final Chorus | payoff | controlled ad-lib]",
            "[Outro | clean ending]",
            "[End]",
        ]
    )


def render_issue_table(issues: list[Issue]) -> str:
    if not issues:
        return "| severity | code | message | route |\n|---|---|---|---|\n| pass | none | compile approved | experiment handoff |\n"
    rows = ["| severity | code | message | route |", "|---|---|---|---|"]
    for issue in issues:
        rows.append(f"| {issue.severity} | {issue.code} | {issue.message} | {issue.route} |")
    return "\n".join(rows) + "\n"


def render_package(ctx: PromptContext, issues: list[Issue], args: argparse.Namespace) -> str:
    lyrics_block = ctx.lyrics_block or default_lyrics_block(ctx)
    blockers = [issue for issue in issues if issue.severity == "blocker"]
    decision = "compile approved" if not blockers else "repair before generation"
    genre = fallback(style_line(ctx), "genre / tempo / key")
    vocal = fallback(ctx.vocal, "vocal identity")
    instrumentation = fallback(ctx.instrumentation, "instrumentation")
    production = fallback(ctx.production, "production texture")
    mood = fallback(ctx.mood, "mood / energy arc")

    return f"""# Prompt Package {args.version}

Generated by: tools/compile_music_prompt_package.py
Project root: {args.project_root}
Decision: {decision}

## Metadata

- Title: {fallback(ctx.title, "title")}
- Project: {fallback(ctx.project, "project")}
- Use case: {fallback(ctx.use_case, "use case")}
- Audience: {fallback(ctx.audience, "audience")}
- Language: {fallback(ctx.language, "language")}
- Lane: {fallback(ctx.lane, "lane")}
- Version: {args.version}
- Model: {ctx.model}
- Weirdness: {ctx.weirdness}
- Style Influence: {ctx.style_influence}
- Audio Influence: {ctx.audio_influence}
- Vocal Gender: {ctx.vocal_gender}
- Instrumental: {ctx.instrumental}
- Exclude: {fallback(ctx.exclude, "exclude field")}
- Human Anchor Lane: {fallback(ctx.human_anchor_lane, "human anchor lane")}
- Voice Identity Source: {ctx.voice_identity_source}
- Persona Source: {ctx.persona_source}
- Custom Model Source: {ctx.custom_model_source}
- Custom Model Corpus: {ctx.custom_model_corpus}
- Voice Verification: {ctx.voice_verification}
- My Taste State: {ctx.my_taste_state}
- My Taste Summary: {ctx.my_taste_summary}
- Prompt Boost State: {ctx.prompt_boost_state}
- Boosted Style Text: {ctx.boosted_style_text}

## Style Of Music

```text
genre: "{genre}"
vocal: "{vocal}"
instrumentation: "{instrumentation}"
production: "{production}"
mood: "{mood}"
```

## Lyrics

```text
{lyrics_block}
```

## Prompt Rationale

- Narrator: {fallback(ctx.narrator, "narrator")}
- Situation: {fallback(ctx.situation, "situation")}
- Title phrase: {fallback(ctx.title_phrase, "title phrase")}
- Hook promise: {fallback(ctx.hook_promise, "hook promise")}
- Methodology transfer: {'pass' if ctx.methodology_audit_decision.casefold() == 'pass' else fallback(ctx.methodology_audit_decision, 'methodology transfer audit')}
- Prompt specificity: {'pass' if ctx.prompt_specificity_audit_decision.casefold() == 'pass' else fallback(ctx.prompt_specificity_audit_decision, 'prompt specificity budget audit')}
- Genre/lane authenticity: {'pass' if ctx.genre_lane_authenticity_audit_decision.casefold() == 'pass' else fallback(ctx.genre_lane_authenticity_audit_decision, 'genre/lane authenticity audit')}
- Lyric narrative: {'pass' if ctx.lyric_narrative_audit_decision.casefold() == 'pass' else fallback(ctx.lyric_narrative_audit_decision, 'lyric narrative audit')}
- Reference audit: {'pass' if ctx.reference_audit_decision.casefold() == 'pass' else fallback(ctx.reference_audit_decision, 'reference DNA audit')}
- Chord skeleton transfer: {'not required' if not ctx.chord_skeleton_transfer_required else ('pass' if ctx.chord_skeleton_transfer_audit_decision.casefold() == 'pass' else fallback(ctx.chord_skeleton_transfer_audit_decision, 'chord skeleton transfer audit'))}
- Topline audit: {'pass' if ctx.topline_audit_decision.casefold() == 'pass' else fallback(ctx.topline_audit_decision, 'topline hook audit')}
- Harmony/Bass audit: {'pass' if ctx.harmony_audit_decision.casefold() == 'pass' else fallback(ctx.harmony_audit_decision, 'harmony/bass audit')}
- Groove audit: {'pass' if ctx.groove_audit_decision.casefold() == 'pass' else fallback(ctx.groove_audit_decision, 'groove humanization audit')}
- Structure audit: {'pass' if ctx.structure_audit_decision.casefold() == 'pass' else fallback(ctx.structure_audit_decision, 'structure dynamics audit')}
- Vocal audit: {'pass' if ctx.vocal_audit_decision.casefold() == 'pass' else fallback(ctx.vocal_audit_decision, 'vocal identity audit')}
- Prosody notes: {fallback(ctx.prosody_notes, "prosody notes")}
- Prosody audit: {'pass' if ctx.prosody_audit_decision.casefold() == 'pass' else fallback(ctx.prosody_audit_decision, 'lyrics prosody audit')}
- Genre anchor: {genre}
- Vocal identity: {vocal}
- Core instruments: {instrumentation}
- Production texture: {production}
- Emotional arc: {mood}
- Why these exclusions: {fallback(ctx.exclude, "exclude rationale")}
- What to test first: first 20 seconds, title hook recall, vocal identity, groove lock, and AI-flavor red flags.
- Human anchor routing: {fallback(ctx.human_anchor_lane, "human anchor lane")}; use text-only for quick exploration, audio seed / Voice / Persona / Custom Model / My Taste only when the source and rights evidence are recorded.
- Identity continuity: voice={ctx.voice_identity_source or 'none'}, persona={ctx.persona_source or 'none'}, custom model={ctx.custom_model_source or ctx.custom_model_corpus or 'none'}, My Taste={ctx.my_taste_state or 'not recorded'}.

## Preflight Summary

{render_issue_table(issues)}
"""


def render_preflight(ctx: PromptContext, issues: list[Issue], args: argparse.Namespace) -> str:
    blockers = [issue for issue in issues if issue.severity == "blocker"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    decision = "compile approved" if not blockers else "repair before generation"
    return f"""# Prompt Preflight Review

Generated by: tools/compile_music_prompt_package.py
Project root: {args.project_root}
Prompt package: {ctx.package_path}

Field completeness: {'pass' if not blockers else 'fail'}
Style specificity: {'pass' if not any(issue.code.startswith('generic') for issue in issues) else 'review'}
Lyrics context: {'pass' if ctx.lyrics_block else 'fail'}
Prosody risk: {'pass' if ctx.prosody_notes else 'review'}
Methodology transfer: {'pass' if not any(issue.code == 'methodology_transfer_audit' for issue in issues) else 'fail'}
Prompt specificity: {'pass' if not any(issue.code == 'prompt_specificity_budget_audit' for issue in issues) else 'fail'}
Genre/lane authenticity: {'pass' if not any(issue.code == 'genre_lane_authenticity_audit' for issue in issues) else 'fail'}
Lyric narrative: {'pass' if not any(issue.code == 'lyric_narrative_audit' for issue in issues) else 'fail'}
Prosody audit: {'pass' if not any(issue.code == 'lyrics_prosody_audit' for issue in issues) else 'fail'}
Reference audit: {'pass' if not any(issue.code == 'reference_dna_audit' for issue in issues) else 'fail'}
Chord skeleton transfer: {'pass' if not any(issue.code == 'chord_skeleton_transfer_audit' for issue in issues) else 'fail'}
Topline audit: {'pass' if not any(issue.code == 'topline_hook_audit' for issue in issues) else 'fail'}
Harmony/Bass audit: {'pass' if not any(issue.code == 'harmony_bass_audit' for issue in issues) else 'fail'}
Groove audit: {'pass' if not any(issue.code == 'groove_humanization_audit' for issue in issues) else 'fail'}
Structure audit: {'pass' if not any(issue.code == 'structure_dynamics_audit' for issue in issues) else 'fail'}
Vocal audit: {'pass' if not any(issue.code == 'vocal_identity_audit' for issue in issues) else 'fail'}
Personalization hygiene: {'pass' if not any(issue.code == 'personalization_hygiene_audit' for issue in issues) else 'fail'}
Hook clarity: {'pass' if ctx.title_phrase or ctx.hook_promise else 'fail'}
Exclude rationale: {'pass' if ctx.exclude else 'fail'}
Slider intent: {'pass' if ctx.model and ctx.weirdness and ctx.style_influence else 'fail'}
Model/version: {'pass' if ctx.model else 'fail'}
Human anchor lane: {'pass' if ctx.human_anchor_lane else 'fail'}
Identity routing: {'pass' if not any(issue.code in {'human_anchor_lane', 'identity_source_missing', 'voice_verification_missing', 'custom_model_corpus_missing', 'my_taste_state_missing', 'my_taste_summary_missing', 'prompt_boost_text_missing'} for issue in issues) else 'fail'}
My Taste / boost: {'pass' if not any(issue.code in {'my_taste_state_missing', 'my_taste_summary_missing', 'prompt_boost_text_missing'} for issue in issues) else 'fail'}
Identity / rights: {'pass' if not any(issue.code in {'protected_identity', 'protected_identity_in_prompt', 'voice_rights'} for issue in issues) else 'fail'}
Variable discipline: review
Conflict check: {'pass' if not any(issue.code == 'conflict_decision' for issue in issues) else 'fail'}

Decision: {decision}

Blockers: {len(blockers)}
Warnings: {len(warnings)}

## Issues

{render_issue_table(issues)}
"""


def render_handoff(ctx: PromptContext, issues: list[Issue], args: argparse.Namespace) -> str:
    blockers = [issue for issue in issues if issue.severity == "blocker"]
    return f"""# Experiment Handoff

Generated by: tools/compile_music_prompt_package.py
Prompt package: {ctx.package_path}
Preflight decision: {'compile approved' if not blockers else 'repair before generation'}

Compiler package:
- {ctx.package_path}

Frozen brief:
- Title: {fallback(ctx.title, "title")}
- Language: {fallback(ctx.language, "language")}
- Lane: {fallback(ctx.lane, "lane")}
- Narrator: {fallback(ctx.narrator, "narrator")}
- Title phrase: {fallback(ctx.title_phrase, "title phrase")}
- Human anchor lane: {fallback(ctx.human_anchor_lane, "human anchor lane")}

Allowed variables:
- One primary variable per batch: style wording, lyrics context, exclude, sliders, Persona/Voice, Custom Model, My Taste/Prompt Boost, or audio influence.

Locked variables:
- Narrator, title phrase, language, core genre lane, human anchor lane, rights boundary, and do-not-copy rules.

Batch size:
- 2-4 candidates before blind review.

Success metric:
- First 20 seconds hold attention; title hook can be recalled; vocal identity is specific; groove and form fit the brief; no major AI-flavor red flags.

Failure route:
- If blockers remain, do not generate. Repair the routed files first.
"""


def write_if_allowed(path: Path, text: str, allow_overwrite: bool) -> None:
    if path.exists() and not allow_overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Song project root created by create_music_song_project.py.")
    parser.add_argument("--version", default="v001", help="Prompt package version label.")
    parser.add_argument("--package-output", default=DEFAULT_PACKAGE, help="Relative output path for the prompt package.")
    parser.add_argument("--preflight-output", default=DEFAULT_PREFLIGHT, help="Relative output path for preflight review.")
    parser.add_argument("--handoff-output", default=DEFAULT_HANDOFF, help="Relative output path for experiment handoff.")
    parser.add_argument("--write", action="store_true", help="Write package, preflight, and handoff files.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow overwriting existing generated markdown files.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when blockers remain.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    args.project_root = str(project_root)

    if not project_root.exists() or not project_root.is_dir():
        print(f"error: project root not found: {project_root}", file=sys.stderr)
        return 2

    docs = read_project(project_root)
    ctx = compose_context(docs)
    ctx.package_path = args.package_output
    issues = issue_context(ctx, docs)
    package = render_package(ctx, issues, args)
    preflight = render_preflight(ctx, issues, args)
    handoff = render_handoff(ctx, issues, args)
    blockers = [issue for issue in issues if issue.severity == "blocker"]

    if args.write:
        try:
            write_if_allowed(project_root / args.package_output, package, args.allow_overwrite)
            write_if_allowed(project_root / args.preflight_output, preflight, args.allow_overwrite)
            write_if_allowed(project_root / args.handoff_output, handoff, args.allow_overwrite)
        except FileExistsError as exc:
            print(f"error: output exists, use --allow-overwrite: {exc}", file=sys.stderr)
            return 2
    else:
        print(package)

    if blockers:
        print(f"prompt compile has {len(blockers)} blocker(s).", file=sys.stderr)
        for issue in blockers:
            print(f"- {issue.code}: {issue.message} -> {issue.route}", file=sys.stderr)
        return 1 if args.strict else 0

    print("prompt compile approved.")
    print(f"package: {project_root / args.package_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
