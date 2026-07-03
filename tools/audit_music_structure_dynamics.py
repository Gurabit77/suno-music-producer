#!/usr/bin/env python3
"""Audit structure, energy arc, and section-transition evidence before prompt compile."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


STRUCTURE_BRIEF_FILE = "03_writing/structure-brief.md"
ENERGY_FILE = "03_writing/energy-map.md"
SECTION_FUNCTION_FILE = "03_writing/section-function-map.md"
CONTRAST_FILE = "03_writing/contrast-continuity-matrix.md"
TRANSITION_FILE = "03_writing/transition-cue-sheet.md"
SECOND_VERSE_FILE = "03_writing/second-verse-development.md"
BRIDGE_FILE = "03_writing/bridge-turn-plan.md"
FINAL_CHORUS_FILE = "03_writing/final-chorus-payoff.md"
OUTRO_FILE = "03_writing/outro-end-plan.md"
SECTION_INFORMATION_FILE = "03_writing/section-information-map.md"
SECTION_PERFORMANCE_FILE = "03_writing/section-performance-map.md"
GROOVE_AUDIT_FILE = "03_writing/groove-humanization-audit.md"
LYRICS_FILE = "04_prompt/lyrics-context-map.md"
STYLE_FILE = "04_prompt/style-field-map.md"
PROMPT_BRIEF_FILE = "04_prompt/prompt-compile-brief.md"
SONG_BRIEF_FILE = "01_brief/song-brief.md"
DEFAULT_OUTPUT = "03_writing/structure-dynamics-audit.md"

EMPTY_VALUES = {"", '""', "''", "todo", "tbd", "n/a", "na", "none", "yes/no", "pass/fail", "-", "--"}
GENERIC_STRUCTURE = {
    "dynamic",
    "good structure",
    "song structure",
    "more energy",
    "build up",
    "natural transitions",
    "emotional arc",
}
AI_STRUCTURE_RED_FLAGS = (
    "flat energy throughout",
    "same arrangement every section",
    "random genre switch",
    "third verse disguised as bridge",
    "endless outro",
    "sudden cutoff",
    "overblown riser",
    "fake crowd",
    "choir pad everywhere",
    "muddy final chorus",
)


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


SECTION_HEADS = [
    "intro",
    "verse 1",
    "verse 2",
    "pre-chorus",
    "pre chorus",
    "pre",
    "chorus",
    "chorus 2",
    "bridge",
    "final chorus",
    "outro",
]


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


def section_present(text: str, names: list[str]) -> bool:
    lowered = text.casefold()
    for name in names:
        name_cf = name.casefold()
        pattern = r"\[\s*" + re.escape(name_cf).replace(r"\ ", r"\s+")
        table_pattern = rf"(?m)^\s*\|\s*{re.escape(name_cf)}\s*\|"
        line_pattern = rf"(?m)^\s*{re.escape(name_cf)}\b"
        if re.search(pattern, lowered) or re.search(table_pattern, lowered) or re.search(line_pattern, lowered):
            return True
    return False


def groove_audit_passed(docs: dict[str, str]) -> bool:
    text = docs.get(GROOVE_AUDIT_FILE, "")
    return "Generated by: tools/audit_music_groove_humanization.py" in text and re.search(r"^Decision:\s*pass\b", text, flags=re.I | re.M) is not None


def is_positive(value: str) -> bool:
    return bool(re.search(r"\b(yes|true|required|exact|must|必须|需要)\b", value, re.I))


def is_generic(value: str) -> bool:
    compact = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", value.casefold()).strip()
    return compact in GENERIC_STRUCTURE or any(term in compact for term in GENERIC_STRUCTURE)


def has_ai_structure_avoid_terms(value: str) -> bool:
    lowered = value.casefold()
    return any(term in lowered for term in AI_STRUCTURE_RED_FLAGS) or bool(re.search(r"平铺|随机转场|随机换风格|结尾拖沓|突兀停止|副歌糊", value))


def analyze(docs: dict[str, str]) -> tuple[dict[str, str], list[Finding]]:
    paths = [
        STRUCTURE_BRIEF_FILE,
        ENERGY_FILE,
        SECTION_FUNCTION_FILE,
        CONTRAST_FILE,
        TRANSITION_FILE,
        SECOND_VERSE_FILE,
        BRIDGE_FILE,
        FINAL_CHORUS_FILE,
        OUTRO_FILE,
        SECTION_INFORMATION_FILE,
        SECTION_PERFORMANCE_FILE,
        LYRICS_FILE,
        STYLE_FILE,
        PROMPT_BRIEF_FILE,
        SONG_BRIEF_FILE,
    ]
    fields = {
        "language": extract_value(docs, paths, ["Language", "Language lane"]),
        "genre": extract_value(docs, paths, ["Genre", "Genre lane", "Style"]),
        "tempo_meter": extract_value(docs, paths, ["Tempo / meter", "Tempo", "Meter", "Tempo feel"]),
        "target_length": extract_value(docs, paths, ["Target length", "Length", "Duration"]),
        "use_case": extract_value(docs, paths, ["Use case", "Usage", "Goal"]),
        "core_hook": extract_value(docs, paths, ["Core hook", "Title hook", "Hook", "Title phrase"]),
        "narrative_arc": extract_value(docs, paths, ["Narrative arc", "Story arc"]),
        "emotional_arc": extract_value(docs, paths, ["Emotional arc", "Emotion arc", "Mood / energy arc"]),
        "highest_energy_section": extract_value(docs, paths, ["Highest energy section", "Energy peak"]),
        "highest_tension_section": extract_value(docs, paths, ["Highest tension section", "Tension peak"]),
        "must_have": extract_value(docs, paths, ["Must have"]),
        "must_avoid": extract_value(docs, paths, ["Must avoid", "Do not", "Avoid", "Forbidden cues"]),
        "exact_structure_required": extract_value(docs, paths, ["Exact structure required?", "Exact structure required"]),
        "exact_structure_plan": extract_value(docs, paths, ["If exact", "If exact: demo / reference energy map / DAW guide", "Demo / reference energy map / DAW guide", "DAW guide"]),
        "energy_rule": extract_value(docs, [ENERGY_FILE, STRUCTURE_BRIEF_FILE], ["Energy rule", "Energy arc"]),
        "lean_in": extract_value(docs, [ENERGY_FILE], ["Where should the listener lean in", "Lean in"]),
        "release": extract_value(docs, [ENERGY_FILE], ["Where should the listener feel release", "Release"]),
        "breathe": extract_value(docs, [ENERGY_FILE], ["Where should the song breathe", "Breathe"]),
        "keep_across": extract_value(docs, [CONTRAST_FILE], ["Keep across song"]),
        "change_by_section": extract_value(docs, [CONTRAST_FILE], ["Change by section"]),
        "never_change": extract_value(docs, [CONTRAST_FILE], ["Never change"]),
        "allowed_surprise": extract_value(docs, [CONTRAST_FILE], ["Allowed surprise"]),
        "intro_identity": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Intro"], ["musical identity", "identity"]),
        "verse1_information": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Verse 1"], ["information", "new information"]),
        "pre_tension_method": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Pre-Chorus", "Pre"], ["tension method", "tension"]),
        "chorus_title_hook": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Chorus"], ["title hook", "hook"]),
        "chorus_arrival": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Chorus"], ["arrival method", "arrival"]),
        "verse2_new_information": extract_value(docs, [SECOND_VERSE_FILE, SECTION_INFORMATION_FILE], ["New information", "Verse 2 new information"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Verse 2"], ["new information", "information"]),
        "verse2_new_arrangement": extract_value(docs, [SECOND_VERSE_FILE, SECTION_PERFORMANCE_FILE], ["New arrangement detail", "New groove", "New counter melody"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Verse 2"], ["new arrangement detail", "arrangement"]),
        "verse2_stays": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Verse 2"], ["what stays from Verse 1", "what stays"]),
        "bridge_reveals": extract_value(docs, [BRIDGE_FILE], ["Bridge reveals", "Reveals"]),
        "bridge_contrast": extract_value(docs, [BRIDGE_FILE], ["Musical contrast", "Lyric contrast", "Contrast method"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Bridge"], ["contrast method", "contrast"]),
        "bridge_new_perspective": extract_section_value(docs, SECTION_FUNCTION_FILE, ["Bridge"], ["new perspective", "perspective"]),
        "bridge_return_cue": extract_value(docs, [BRIDGE_FILE, TRANSITION_FILE], ["Return cue to final chorus", "Bridge -> Final Chorus"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Bridge"], ["return cue"]),
        "final_repeats": extract_value(docs, [FINAL_CHORUS_FILE], ["What repeats exactly", "What repeats"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Final Chorus"], ["what repeats"]),
        "final_develops": extract_value(docs, [FINAL_CHORUS_FILE], ["What changes", "What develops"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Final Chorus"], ["what develops"]),
        "final_payoff": extract_value(docs, [FINAL_CHORUS_FILE], ["Vocal payoff", "Mix payoff", "Payoff"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Final Chorus"], ["payoff"]),
        "outro_ending_logic": extract_value(docs, [OUTRO_FILE], ["Ending logic", "Ending", "Outro plan"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Outro"], ["ending logic"]),
        "outro_last_sound": extract_value(docs, [OUTRO_FILE], ["Last sound", "Ending cue"]) or extract_section_value(docs, SECTION_FUNCTION_FILE, ["Outro"], ["last sound"]),
        "intro_to_verse": extract_value(docs, [TRANSITION_FILE], ["Intro -> Verse"]),
        "verse_to_pre": extract_value(docs, [TRANSITION_FILE], ["Verse -> Pre", "Verse -> Pre-Chorus"]),
        "pre_to_chorus": extract_value(docs, [TRANSITION_FILE], ["Pre -> Chorus", "Pre-Chorus -> Chorus"]),
        "chorus_to_verse2": extract_value(docs, [TRANSITION_FILE], ["Chorus -> Verse 2"]),
        "chorus2_to_bridge": extract_value(docs, [TRANSITION_FILE], ["Chorus 2 -> Bridge"]),
        "bridge_to_final": extract_value(docs, [TRANSITION_FILE], ["Bridge -> Final Chorus"]),
        "final_to_outro": extract_value(docs, [TRANSITION_FILE], ["Final Chorus -> Outro"]),
        "allowed_cues": extract_value(docs, [TRANSITION_FILE], ["Allowed cues"]),
        "forbidden_cues": extract_value(docs, [TRANSITION_FILE], ["Forbidden cues"]),
    }
    findings: list[Finding] = []

    required = [
        ("language_missing", fields["language"], "Language is missing; structure defaults depend on lane and language.", "repair song brief"),
        ("target_length_missing", fields["target_length"], "Target length is missing; intro, bridge, and outro scale depend on duration.", "fill structure-brief.md"),
        ("core_hook_missing", fields["core_hook"], "Core hook is missing; section design needs a payoff target.", "fill structure-brief.md"),
        ("arc_missing", fields["narrative_arc"] or fields["emotional_arc"], "Narrative or emotional arc is missing.", "fill structure-brief.md"),
        ("highest_energy_missing", fields["highest_energy_section"], "Highest energy section is missing.", "fill structure-brief.md"),
        ("highest_tension_missing", fields["highest_tension_section"], "Highest tension section is missing.", "fill structure-brief.md"),
        ("energy_rule_missing", fields["energy_rule"], "Energy rule is missing.", "fill energy-map.md"),
        ("lean_in_missing", fields["lean_in"], "Listener lean-in point is missing.", "fill energy-map.md"),
        ("release_missing", fields["release"], "Release point is missing.", "fill energy-map.md"),
        ("breathe_missing", fields["breathe"], "Breathing/dropout point is missing.", "fill energy-map.md"),
        ("verse1_function_missing", fields["verse1_information"], "Verse 1 section information/function is missing.", "fill section-function-map.md"),
        ("pre_function_missing", fields["pre_tension_method"], "Pre-chorus tension method is missing.", "fill section-function-map.md"),
        ("chorus_function_missing", fields["chorus_title_hook"] and fields["chorus_arrival"], "Chorus hook and arrival method must be stated.", "fill section-function-map.md"),
        ("verse2_development_missing", fields["verse2_new_information"] and fields["verse2_new_arrangement"], "Verse 2 needs new information and a restrained arrangement development.", "fill second-verse-development.md"),
        ("bridge_turn_missing", fields["bridge_reveals"] and fields["bridge_contrast"] and fields["bridge_return_cue"], "Bridge needs reveal, contrast, and return cue.", "fill bridge-turn-plan.md"),
        ("final_chorus_payoff_missing", fields["final_repeats"] and fields["final_develops"] and fields["final_payoff"], "Final chorus needs repeat/development/payoff evidence.", "fill final-chorus-payoff.md"),
        ("outro_plan_missing", fields["outro_ending_logic"] and fields["outro_last_sound"], "Outro ending logic and last sound are missing.", "fill outro-end-plan.md"),
        ("contrast_continuity_missing", fields["keep_across"] and fields["change_by_section"] and fields["never_change"], "Contrast/continuity matrix is incomplete.", "fill contrast-continuity-matrix.md"),
        ("transition_cues_missing", fields["pre_to_chorus"] and fields["bridge_to_final"] and fields["final_to_outro"], "Critical transition cues are missing.", "fill transition-cue-sheet.md"),
        ("avoid_list_missing", fields["must_avoid"] or fields["forbidden_cues"], "Structure AI-flavor avoid list is missing.", "fill structure-brief.md or transition-cue-sheet.md"),
    ]
    for code, value, message, route in required:
        if not value:
            findings.append(Finding("blocker", code, message, route))

    energy_text = docs.get(ENERGY_FILE, "")
    for label, names in [
        ("verse_energy_missing", ["Verse 1", "Verse"]),
        ("pre_energy_missing", ["Pre", "Pre-Chorus"]),
        ("chorus_energy_missing", ["Chorus"]),
        ("verse2_energy_missing", ["Verse 2"]),
        ("bridge_energy_missing", ["Bridge"]),
        ("final_chorus_energy_missing", ["Final Chorus"]),
        ("outro_energy_missing", ["Outro"]),
    ]:
        if not section_present(energy_text, names):
            findings.append(Finding("blocker", label, f"Energy map is missing {names[0]}.", "fill energy-map.md"))

    lyrics_text = docs.get(LYRICS_FILE, "")
    if not section_present(lyrics_text, ["Verse 2"]):
        findings.append(Finding("blocker", "lyrics_verse2_missing", "Lyrics context has no Verse 2 tag; structure development cannot be verified.", "repair lyrics-context-map.md"))
    if not (section_present(lyrics_text, ["Bridge"]) or section_present(lyrics_text, ["Final Chorus"])):
        findings.append(Finding("blocker", "lyrics_payoff_missing", "Lyrics context needs Bridge or Final Chorus payoff tags.", "repair lyrics-context-map.md"))

    if not groove_audit_passed(docs):
        findings.append(Finding("blocker", "groove_audit_missing", "Structure audit requires a passing groove humanization audit first.", "run audit_music_groove_humanization.py"))

    if fields["exact_structure_required"] and is_positive(fields["exact_structure_required"]) and not fields["exact_structure_plan"]:
        findings.append(Finding("blocker", "exact_structure_plan_missing", "Exact structure is required, but no self-made demo/reference energy map/DAW guide is recorded.", "add self-made structure guide"))

    if fields["energy_rule"] and is_generic(fields["energy_rule"]):
        findings.append(Finding("warning", "generic_energy_rule", "Energy rule is too generic to be blind-testable.", "write section-by-section energy/tension movement"))
    avoid_text = fields["must_avoid"] or fields["forbidden_cues"]
    if avoid_text and not has_ai_structure_avoid_terms(avoid_text):
        findings.append(Finding("warning", "ai_structure_avoid_terms_missing", "Avoid list should name flat energy, same arrangement, random genre switch, endless outro, or sudden cutoff risks.", "add structure Exclude terms"))
    if not fields["intro_to_verse"]:
        findings.append(Finding("warning", "intro_transition_missing", "Intro -> Verse transition cue is missing.", "fill transition-cue-sheet.md"))
    if not fields["allowed_surprise"]:
        findings.append(Finding("warning", "allowed_surprise_missing", "Allowed surprise is missing; contrast may become random.", "fill contrast-continuity-matrix.md"))

    return fields, findings


def render_finding_table(findings: list[Finding]) -> str:
    if not findings:
        return "| severity | code | message | route |\n|---|---|---|---|\n| pass | none | structure dynamics approved | prompt compile |\n"
    rows = ["| severity | code | message | route |", "|---|---|---|---|"]
    for finding in findings:
        rows.append(f"| {finding.severity} | {finding.code} | {finding.message} | {finding.route} |")
    return "\n".join(rows) + "\n"


def structure_tags(fields: dict[str, str]) -> str:
    pieces = [
        fields["target_length"],
        fields["energy_rule"],
        f"energy peak: {fields['highest_energy_section']}" if fields["highest_energy_section"] else "",
        f"tension peak: {fields['highest_tension_section']}" if fields["highest_tension_section"] else "",
        fields["bridge_contrast"],
        fields["final_payoff"],
        fields["outro_ending_logic"],
    ]
    text = ", ".join(piece for piece in pieces if piece)
    return text or "NEEDS_REPAIR: structure tags"


def section_tags(fields: dict[str, str]) -> str:
    pieces = [
        f"[Verse 2 | {fields['verse2_new_information']} | {fields['verse2_new_arrangement']}]" if fields["verse2_new_information"] or fields["verse2_new_arrangement"] else "",
        f"[Bridge | {fields['bridge_contrast']} | {fields['bridge_return_cue']}]" if fields["bridge_contrast"] or fields["bridge_return_cue"] else "",
        f"[Final Chorus | {fields['final_develops']} | {fields['final_payoff']}]" if fields["final_develops"] or fields["final_payoff"] else "",
        f"[Outro | {fields['outro_ending_logic']} | {fields['outro_last_sound']}]" if fields["outro_ending_logic"] or fields["outro_last_sound"] else "",
    ]
    text = "\n".join(piece for piece in pieces if piece)
    return text or "NEEDS_REPAIR: section tags"


def render_audit(project_root: Path, fields: dict[str, str], findings: list[Finding]) -> str:
    blockers = [finding for finding in findings if finding.severity == "blocker"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    decision = "pass" if not blockers else "repair before prompt compile"
    return f"""# Structure Dynamics Audit

Generated by: tools/audit_music_structure_dynamics.py
Project root: {project_root}
Decision: {decision}

Language: {fields['language'] or 'NEEDS_REPAIR: language'}
Genre: {fields['genre'] or 'NEEDS_REPAIR: genre'}
Tempo / meter: {fields['tempo_meter'] or 'NEEDS_REPAIR: tempo / meter'}
Target length: {fields['target_length'] or 'NEEDS_REPAIR: target length'}
Use case: {fields['use_case'] or ''}
Core hook: {fields['core_hook'] or 'NEEDS_REPAIR: core hook'}
Narrative arc: {fields['narrative_arc'] or ''}
Emotional arc: {fields['emotional_arc'] or 'NEEDS_REPAIR: emotional arc'}
Highest energy section: {fields['highest_energy_section'] or 'NEEDS_REPAIR: highest energy section'}
Highest tension section: {fields['highest_tension_section'] or 'NEEDS_REPAIR: highest tension section'}
Must have: {fields['must_have'] or ''}
Must avoid: {fields['must_avoid'] or fields['forbidden_cues'] or 'NEEDS_REPAIR: avoid list'}
Blockers: {len(blockers)}
Warnings: {len(warnings)}

## Structure Design

| field | value |
|---|---|
| energy rule | {fields['energy_rule'] or ''} |
| lean in | {fields['lean_in'] or ''} |
| release | {fields['release'] or ''} |
| breathe | {fields['breathe'] or ''} |
| keep across song | {fields['keep_across'] or ''} |
| change by section | {fields['change_by_section'] or ''} |
| never change | {fields['never_change'] or ''} |
| verse 2 development | {(fields['verse2_new_information'] + '; ' + fields['verse2_new_arrangement']).strip('; ') or ''} |
| bridge turn | {(fields['bridge_reveals'] + '; ' + fields['bridge_contrast'] + '; ' + fields['bridge_return_cue']).strip('; ') or ''} |
| final chorus payoff | {(fields['final_repeats'] + '; ' + fields['final_develops'] + '; ' + fields['final_payoff']).strip('; ') or ''} |
| outro | {(fields['outro_ending_logic'] + '; ' + fields['outro_last_sound']).strip('; ') or ''} |
| critical transitions | {', '.join(piece for piece in [fields['pre_to_chorus'], fields['bridge_to_final'], fields['final_to_outro']] if piece)} |

## Findings

{render_finding_table(findings)}
## Prompt Routing

Structure tags: {structure_tags(fields)}
Section tags:
{section_tags(fields)}
Structure blind test: blind-map sections by time, confirm Verse 2 development, Bridge turn, Final Chorus payoff, Outro ending, and transition cues without reading the prompt
Exclude additions: {fields['must_avoid'] or fields['forbidden_cues'] or 'flat energy throughout, same arrangement every section, random genre switch, endless outro, sudden cutoff'}
Repair route: structure brief, energy map, section-function map, transition cue sheet, second-verse development, bridge turn, final chorus payoff, outro end plan, Song Editor, Replace Section, or Extend
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
        print(f"structure dynamics audit has {len(blockers)} blocker(s).", file=sys.stderr)
        for finding in blockers:
            print(f"- {finding.code}: {finding.message} -> {finding.route}", file=sys.stderr)
        return 1 if args.strict else 0

    print("structure dynamics audit passed.")
    print(f"audit: {project_root / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
