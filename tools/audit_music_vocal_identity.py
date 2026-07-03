#!/usr/bin/env python3
"""Audit vocal identity and performance direction before an AI music prompt is compiled."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SINGER_BRIEF_FILE = "03_writing/singer-brief.md"
VOCAL_PERFORMANCE_FILE = "03_writing/vocal-performance-map.md"
VOCAL_ARRANGEMENT_FILE = "03_writing/vocal-arrangement-map.md"
PROSODY_AUDIT_FILE = "03_writing/lyrics-prosody-audit.md"
TOPLINE_AUDIT_FILE = "03_writing/topline-hook-audit.md"
STRUCTURE_AUDIT_FILE = "03_writing/structure-dynamics-audit.md"
TITLE_FILE = "03_writing/title-phrase.md"
LYRICS_FILE = "04_prompt/lyrics-context-map.md"
STYLE_FILE = "04_prompt/style-field-map.md"
IDENTITY_FILE = "04_prompt/persona-voice-model-routing.md"
VOICE_RIGHTS_FILE = "09_vocal/voice-rights.md"
PROMPT_BRIEF_FILE = "04_prompt/prompt-compile-brief.md"
SONG_BRIEF_FILE = "01_brief/song-brief.md"
DEFAULT_OUTPUT = "03_writing/vocal-identity-audit.md"

EMPTY_VALUES = {"", '""', "''", "todo", "tbd", "n/a", "na", "none", "yes/no", "pass/fail", "-", "--"}
GENERIC_VOCAL = {
    "female vocal",
    "male vocal",
    "beautiful voice",
    "emotional vocal",
    "realistic vocal",
    "human vocal",
    "good singer",
    "pop singer",
    "rock singer",
}
AI_VOCAL_RED_FLAGS = (
    "anonymous vocalist",
    "excessive vocal runs",
    "unclear diction",
    "over-autotuned vocal",
    "fake gasping",
    "same tail every line",
    "choir pad everywhere",
    "lead buried by doubles",
    "random rap verse",
)
PROTECTED_IDENTITY_NAMES = [
    "米津玄师",
    "YOASOBI",
    "Ado",
    "Official髭男dism",
    "King Gnu",
    "宇多田光",
    "Perfume",
    "あいみょん",
    "周杰伦",
    "林俊杰",
    "陈奕迅",
    "邓紫棋",
    "BTS",
    "BLACKPINK",
    "IU",
    "EXO",
    "Taylor Swift",
    "The Weeknd",
    "Billie Eilish",
    "Dua Lipa",
    "Olivia Rodrigo",
    "Harry Styles",
    "Drake",
    "Ed Sheeran",
    "ONE OK ROCK",
    "RADWIMPS",
    "Arctic Monkeys",
    "Radiohead",
    "Green Day",
    "The 1975",
]


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    route: str


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
    if value.casefold() in EMPTY_VALUES:
        return ""
    if value.startswith("[") and value.endswith("]") and ":" in value:
        return ""
    return value


def scan_key_values(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        stripped = re.sub(r"^[-*]\s+", "", stripped)
        match = re.match(r"^([^:]{1,95}):\s*(.*)$", stripped)
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


SECTION_HEADS = ["verse 1", "verse 2", "pre-chorus", "pre chorus", "pre", "chorus", "bridge", "final chorus", "outro"]


def section_block(text: str, names: list[str]) -> str:
    wanted = [name.casefold() for name in names]
    lines = text.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        stripped = line.strip().strip("[]").rstrip(":").casefold()
        if any(stripped == name or stripped.startswith(name + " |") for name in wanted):
            start = idx + 1
            break
    if start is None:
        return ""
    block: list[str] = []
    for line in lines[start:]:
        stripped = line.strip().strip("[]").rstrip(":").casefold()
        if stripped in SECTION_HEADS or any(stripped.startswith(head + " |") for head in SECTION_HEADS):
            break
        block.append(line)
    return "\n".join(block)


def extract_section_value(docs: dict[str, str], path: str, sections: list[str], labels: list[str]) -> str:
    block = section_block(docs.get(path, ""), sections)
    wanted = {label.casefold() for label in labels}
    for label, value in scan_key_values(block):
        if label in wanted and value:
            return value
    return ""


def audit_passed(docs: dict[str, str], path: str, marker: str) -> bool:
    text = docs.get(path, "")
    return marker in text and re.search(r"^Decision:\s*pass\b", text, flags=re.I | re.M) is not None


def positive_value(value: str) -> bool:
    return bool(re.search(r"\b(yes|true|on|enabled|active|voice|persona|custom|my taste|taste)\b", value, re.I))


def is_text_only_lane(value: str) -> bool:
    lowered = value.casefold()
    return "text" in lowered and not any(term in lowered for term in ["voice", "persona", "custom", "taste", "audio"])


def is_generic(value: str) -> bool:
    compact = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", value.casefold()).strip()
    return compact in GENERIC_VOCAL or any(term in compact for term in GENERIC_VOCAL)


def protected_identity_hits(text: str) -> list[str]:
    hits: list[str] = []
    for name in PROTECTED_IDENTITY_NAMES:
        if name.casefold() in text.casefold():
            hits.append(name)
    return hits


def has_ai_vocal_avoid_terms(value: str) -> bool:
    lowered = value.casefold()
    return any(term in lowered for term in AI_VOCAL_RED_FLAGS) or bool(re.search(r"匿名歌手|过度转音|咬字不清|假气口|尾音统一|和声糊主唱", value))


def analyze(docs: dict[str, str]) -> tuple[dict[str, str], list[Finding]]:
    paths = [
        SINGER_BRIEF_FILE,
        VOCAL_PERFORMANCE_FILE,
        VOCAL_ARRANGEMENT_FILE,
        TITLE_FILE,
        LYRICS_FILE,
        STYLE_FILE,
        IDENTITY_FILE,
        VOICE_RIGHTS_FILE,
        PROMPT_BRIEF_FILE,
        SONG_BRIEF_FILE,
    ]
    fields = {
        "song": extract_value(docs, paths, ["Song", "Song title", "Title"]),
        "language": extract_value(docs, paths, ["Language", "Language lane"]),
        "narrator": extract_value(docs, paths, ["Narrator", "Point of view"]),
        "vocal_role": extract_value(docs, paths, ["Vocal role", "Role", "Lead role"]),
        "range_tessitura": extract_value(docs, paths, ["Range / tessitura", "Range", "Tessitura"]),
        "register_plan": extract_value(docs, paths, ["Register plan", "Register"]),
        "timbre": extract_value(docs, paths, ["Timbre", "Tone", "Vocal color"]),
        "diction": extract_value(docs, paths, ["Diction", "Pronunciation"]),
        "breath": extract_value(docs, paths, ["Breath", "Breath plan"]),
        "vibrato": extract_value(docs, paths, ["Vibrato / straight tone", "Vibrato", "Straight tone"]),
        "dynamics": extract_value(docs, paths, ["Dynamics", "Vocal dynamics"]),
        "emotional_restraint": extract_value(docs, paths, ["Emotional restraint", "Emotion control", "Restraint"]),
        "must_not_sound_like": extract_value(docs, paths, ["Must not sound like", "Do not", "Avoid"]),
        "rights_source": extract_value(docs, paths, ["Rights source", "Voice source", "Voice identity source"]),
        "human_anchor_lane": extract_value(docs, paths, ["Human anchor lane", "Anchor lane", "Feature type"]),
        "voice_identity_source": extract_value(docs, paths, ["Voice identity source", "Voice source"]),
        "persona_source": extract_value(docs, paths, ["Persona source"]),
        "custom_model_source": extract_value(docs, paths, ["Custom Model source", "Custom model source"]),
        "custom_model_corpus": extract_value(docs, paths, ["Custom model corpus", "Custom Model corpus"]),
        "voice_verification": extract_value(docs, paths, ["Voice verification", "Verification status"]),
        "my_taste_state": extract_value(docs, paths, ["My Taste state", "My Taste enabled"]),
        "prompt_boost_state": extract_value(docs, paths, ["Prompt boost state", "Prompt Boost enabled"]),
        "identity_rights_status": extract_value(docs, paths, ["Rights status", "Identity rights status", "Consent"]),
        "verse_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Verse 1", "Verse"], ["performance", "vocal delivery", "delivery"]),
        "pre_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Pre-Chorus", "Pre"], ["performance", "tension method", "delivery"]),
        "chorus_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Chorus"], ["performance", "delivery"]),
        "verse2_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Verse 2"], ["performance", "delivery"]),
        "bridge_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Bridge"], ["performance", "delivery"]),
        "final_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Final Chorus"], ["performance", "delivery"]),
        "outro_performance": extract_section_value(docs, VOCAL_PERFORMANCE_FILE, ["Outro"], ["performance", "delivery"]),
        "lead_plan": extract_value(docs, [VOCAL_ARRANGEMENT_FILE, SINGER_BRIEF_FILE], ["Lead vocal", "Lead plan", "Lead"]),
        "doubles_plan": extract_value(docs, [VOCAL_ARRANGEMENT_FILE], ["Doubles", "Doubles plan"]),
        "harmonies_plan": extract_value(docs, [VOCAL_ARRANGEMENT_FILE], ["Harmonies", "Harmony vocals", "Backing vocals"]),
        "adlibs_plan": extract_value(docs, [VOCAL_ARRANGEMENT_FILE], ["Ad-libs", "Adlibs", "Ad-lib plan"]),
        "group_duet_plan": extract_value(docs, [VOCAL_ARRANGEMENT_FILE], ["Duet / group vocal", "Group vocal", "Duet"]),
        "lead_center": extract_value(docs, [VOCAL_ARRANGEMENT_FILE, STYLE_FILE], ["Lead center", "Lead vocal center", "Lead remains center"]),
    }
    findings: list[Finding] = []

    required = [
        ("language_missing", fields["language"], "Language is missing; diction and prosody direction depend on it.", "repair song brief"),
        ("narrator_missing", fields["narrator"], "Narrator or point of view is missing.", "repair singer-brief.md"),
        ("vocal_role_missing", fields["vocal_role"], "Vocal role is missing.", "fill singer-brief.md"),
        ("range_missing", fields["range_tessitura"], "Range/tessitura is missing.", "fill singer-brief.md"),
        ("register_missing", fields["register_plan"], "Register plan is missing.", "fill singer-brief.md"),
        ("timbre_missing", fields["timbre"], "Timbre is missing.", "fill singer-brief.md"),
        ("diction_missing", fields["diction"], "Diction direction is missing.", "fill singer-brief.md"),
        ("breath_missing", fields["breath"], "Breath plan is missing.", "fill singer-brief.md"),
        ("vibrato_missing", fields["vibrato"], "Vibrato/straight-tone rule is missing.", "fill singer-brief.md"),
        ("dynamics_missing", fields["dynamics"], "Vocal dynamics are missing.", "fill singer-brief.md"),
        ("emotional_restraint_missing", fields["emotional_restraint"], "Emotional restraint is missing.", "fill singer-brief.md"),
        ("verse_performance_missing", fields["verse_performance"], "Verse vocal performance task is missing.", "fill vocal-performance-map.md"),
        ("pre_performance_missing", fields["pre_performance"], "Pre-chorus vocal performance task is missing.", "fill vocal-performance-map.md"),
        ("chorus_performance_missing", fields["chorus_performance"], "Chorus vocal performance task is missing.", "fill vocal-performance-map.md"),
        ("bridge_performance_missing", fields["bridge_performance"], "Bridge vocal performance task is missing.", "fill vocal-performance-map.md"),
        ("final_performance_missing", fields["final_performance"], "Final chorus vocal performance task is missing.", "fill vocal-performance-map.md"),
        ("lead_plan_missing", fields["lead_plan"], "Lead vocal arrangement plan is missing.", "fill vocal-arrangement-map.md"),
        ("doubles_plan_missing", fields["doubles_plan"], "Doubles plan is missing.", "fill vocal-arrangement-map.md"),
        ("harmonies_plan_missing", fields["harmonies_plan"], "Harmonies/backing vocal plan is missing.", "fill vocal-arrangement-map.md"),
        ("adlibs_plan_missing", fields["adlibs_plan"], "Ad-lib plan is missing.", "fill vocal-arrangement-map.md"),
        ("lead_center_missing", fields["lead_center"], "Lead-center rule is missing.", "fill vocal-arrangement-map.md"),
        ("avoid_list_missing", fields["must_not_sound_like"], "AI vocal red-flag avoid list is missing.", "fill singer-brief.md"),
        ("rights_source_missing", fields["rights_source"] or fields["identity_rights_status"], "Voice rights/source status is missing.", "fill singer-brief.md or voice-rights.md"),
        ("human_anchor_lane_missing", fields["human_anchor_lane"], "Human anchor lane is missing.", "fill persona-voice-model-routing.md"),
    ]
    for code, value, message, route in required:
        if not value:
            findings.append(Finding("blocker", code, message, route))

    if not audit_passed(docs, PROSODY_AUDIT_FILE, "Generated by: tools/audit_music_lyrics_prosody.py"):
        findings.append(Finding("blocker", "prosody_audit_missing", "Vocal audit requires a passing lyrics prosody audit first.", "run audit_music_lyrics_prosody.py"))
    if not audit_passed(docs, TOPLINE_AUDIT_FILE, "Generated by: tools/audit_music_topline_hook.py"):
        findings.append(Finding("blocker", "topline_audit_missing", "Vocal audit requires a passing topline hook audit first.", "run audit_music_topline_hook.py"))
    if not audit_passed(docs, STRUCTURE_AUDIT_FILE, "Generated by: tools/audit_music_structure_dynamics.py"):
        findings.append(Finding("blocker", "structure_audit_missing", "Vocal audit requires a passing structure dynamics audit first.", "run audit_music_structure_dynamics.py"))

    lane = fields["human_anchor_lane"]
    if lane and not is_text_only_lane(lane):
        if ("voice" in lane.casefold() or "audio" in lane.casefold()) and not fields["voice_identity_source"]:
            findings.append(Finding("blocker", "voice_source_missing", "Voice/audio lane requires voice identity source.", "fill voice-rights.md"))
        if "voice" in lane.casefold() and not fields["voice_verification"]:
            findings.append(Finding("blocker", "voice_verification_missing", "Voice lane requires voice verification status.", "fill voice-rights.md"))
        if "persona" in lane.casefold() and not fields["persona_source"]:
            findings.append(Finding("blocker", "persona_source_missing", "Persona lane requires persona source.", "fill persona-voice-model-routing.md"))
        if "custom" in lane.casefold() and not (fields["custom_model_source"] or fields["custom_model_corpus"]):
            findings.append(Finding("blocker", "custom_model_source_missing", "Custom Model lane requires source or corpus.", "fill persona-voice-model-routing.md"))
        if "taste" in lane.casefold() and not fields["my_taste_state"]:
            findings.append(Finding("blocker", "my_taste_state_missing", "My Taste lane requires state or preference summary.", "fill persona-voice-model-routing.md"))

    all_identity_text = "\n".join(
        docs.get(rel, "")
        for rel in [SINGER_BRIEF_FILE, VOCAL_PERFORMANCE_FILE, VOCAL_ARRANGEMENT_FILE, STYLE_FILE, IDENTITY_FILE, VOICE_RIGHTS_FILE]
    )
    hits = protected_identity_hits(all_identity_text)
    if hits:
        findings.append(Finding("blocker", "protected_vocal_identity", "Vocal direction contains protected artist/person identity: " + ", ".join(hits), "remove protected vocal identity and write neutral vocal DNA"))

    if fields["timbre"] and is_generic(fields["timbre"]):
        findings.append(Finding("warning", "generic_timbre", "Timbre is too generic to be blind-testable.", "write range, texture, edge, and mic distance"))
    if fields["must_not_sound_like"] and not has_ai_vocal_avoid_terms(fields["must_not_sound_like"]):
        findings.append(Finding("warning", "ai_vocal_avoid_terms_missing", "Avoid list should name anonymous vocalist, excessive runs, unclear diction, fake breath, same tail, or overstacked doubles.", "add vocal Exclude terms"))
    if not fields["verse2_performance"]:
        findings.append(Finding("warning", "verse2_performance_missing", "Verse 2 vocal development is missing.", "fill vocal-performance-map.md"))
    if not fields["outro_performance"]:
        findings.append(Finding("warning", "outro_performance_missing", "Outro vocal ending is missing.", "fill vocal-performance-map.md"))
    if positive_value(fields["prompt_boost_state"]):
        findings.append(Finding("warning", "prompt_boost_vocal_variable", "Prompt Boost is active; preserve original and boosted vocal text for attribution.", "record boosted style text"))

    return fields, findings


def render_finding_table(findings: list[Finding]) -> str:
    if not findings:
        return "| severity | code | message | route |\n|---|---|---|---|\n| pass | none | vocal identity and performance approved | prompt compile |\n"
    rows = ["| severity | code | message | route |", "|---|---|---|---|"]
    for finding in findings:
        rows.append(f"| {finding.severity} | {finding.code} | {finding.message} | {finding.route} |")
    return "\n".join(rows) + "\n"


def vocal_tags(fields: dict[str, str]) -> str:
    pieces = [fields["vocal_role"], fields["range_tessitura"], fields["register_plan"], fields["timbre"], fields["diction"]]
    text = ", ".join(piece for piece in pieces if piece)
    return text or "NEEDS_REPAIR: vocal tags"


def performance_tags(fields: dict[str, str]) -> str:
    pieces = [fields["verse_performance"], fields["pre_performance"], fields["chorus_performance"], fields["bridge_performance"], fields["final_performance"]]
    text = ", ".join(piece for piece in pieces if piece)
    return text or "NEEDS_REPAIR: vocal performance tags"


def arrangement_tags(fields: dict[str, str]) -> str:
    pieces = [fields["lead_plan"], fields["doubles_plan"], fields["harmonies_plan"], fields["adlibs_plan"], fields["lead_center"]]
    text = ", ".join(piece for piece in pieces if piece)
    return text or "NEEDS_REPAIR: vocal arrangement tags"


def render_audit(project_root: Path, fields: dict[str, str], findings: list[Finding]) -> str:
    blockers = [finding for finding in findings if finding.severity == "blocker"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    decision = "pass" if not blockers else "repair before prompt compile"
    return f"""# Vocal Identity Performance Audit

Generated by: tools/audit_music_vocal_identity.py
Project root: {project_root}
Decision: {decision}

Song: {fields['song'] or ''}
Language: {fields['language'] or 'NEEDS_REPAIR: language'}
Narrator: {fields['narrator'] or 'NEEDS_REPAIR: narrator'}
Vocal role: {fields['vocal_role'] or 'NEEDS_REPAIR: vocal role'}
Range / tessitura: {fields['range_tessitura'] or 'NEEDS_REPAIR: range / tessitura'}
Register plan: {fields['register_plan'] or 'NEEDS_REPAIR: register plan'}
Timbre: {fields['timbre'] or 'NEEDS_REPAIR: timbre'}
Diction: {fields['diction'] or 'NEEDS_REPAIR: diction'}
Breath: {fields['breath'] or 'NEEDS_REPAIR: breath'}
Vibrato / straight tone: {fields['vibrato'] or 'NEEDS_REPAIR: vibrato / straight tone'}
Dynamics: {fields['dynamics'] or 'NEEDS_REPAIR: dynamics'}
Emotional restraint: {fields['emotional_restraint'] or 'NEEDS_REPAIR: emotional restraint'}
Human anchor lane: {fields['human_anchor_lane'] or 'NEEDS_REPAIR: human anchor lane'}
Rights source: {fields['rights_source'] or fields['identity_rights_status'] or 'NEEDS_REPAIR: rights source'}
Must not sound like: {fields['must_not_sound_like'] or 'NEEDS_REPAIR: avoid list'}
Blockers: {len(blockers)}
Warnings: {len(warnings)}

## Vocal Design

| field | value |
|---|---|
| verse performance | {fields['verse_performance'] or ''} |
| pre performance | {fields['pre_performance'] or ''} |
| chorus performance | {fields['chorus_performance'] or ''} |
| verse 2 performance | {fields['verse2_performance'] or ''} |
| bridge performance | {fields['bridge_performance'] or ''} |
| final chorus performance | {fields['final_performance'] or ''} |
| outro performance | {fields['outro_performance'] or ''} |
| lead plan | {fields['lead_plan'] or ''} |
| doubles | {fields['doubles_plan'] or ''} |
| harmonies | {fields['harmonies_plan'] or ''} |
| ad-libs | {fields['adlibs_plan'] or ''} |
| group / duet | {fields['group_duet_plan'] or ''} |
| lead center | {fields['lead_center'] or ''} |

## Findings

{render_finding_table(findings)}
## Prompt Routing

Vocal tags: {vocal_tags(fields)}
Vocal performance tags: {performance_tags(fields)}
Vocal arrangement tags: {arrangement_tags(fields)}
Vocal blind test: vocal-only reverse caption should identify role, range/register, timbre, diction, breath, vibrato, dynamics, doubles/harmonies, ad-libs, and AI vocal red flags
Exclude additions: {fields['must_not_sound_like'] or 'anonymous vocalist, excessive vocal runs, unclear diction, over-autotuned vocal, fake gasping, same tail every line, choir pad everywhere'}
Repair route: singer brief, vocal-performance map, vocal-arrangement map, persona/voice routing, voice-rights, prosody/topline, Studio/stems, or human vocal production
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
    fields, findings = analyze(docs)
    audit = render_audit(project_root, fields, findings)
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
        print(f"vocal identity audit has {len(blockers)} blocker(s).", file=sys.stderr)
        for finding in blockers:
            print(f"- {finding.code}: {finding.message} -> {finding.route}", file=sys.stderr)
        return 1 if args.strict else 0

    print("vocal identity audit passed.")
    print(f"audit: {project_root / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
