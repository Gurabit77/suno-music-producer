#!/usr/bin/env python3
"""Audit reference-track style DNA before an AI music prompt is compiled."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


RIGHTS_PRECHECK_FILE = "02_references/rights-and-source-precheck.md"
SOURCE_RIGHTS_FILE = "02_references/source-rights-ledger.md"
REFERENCE_RIGHTS_FILE = "02_references/reference-rights.md"
REFERENCE_SET_FILE = "02_references/reference-set.md"
STYLE_DNA_FILE = "02_references/style-dna-card.md"
PROTECTED_REMOVAL_FILE = "02_references/protected-identity-removal.md"
REFERENCE_BOUNDARY_FILE = "02_references/reference-boundary.md"
STYLE_FILE = "04_prompt/style-field-map.md"
LYRICS_FILE = "04_prompt/lyrics-context-map.md"
EXCLUDE_FILE = "04_prompt/exclude-negative-aesthetic.md"
DEFAULT_OUTPUT = "02_references/reference-dna-audit.md"

EMPTY_VALUES = {"", '""', "''", "todo", "tbd", "n/a", "na", "none", "yes/no", "pass/fail", "-", "--"}
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


def is_yes(value: str) -> bool:
    return bool(re.search(r"\b(yes|true|allowed|cleared|approved|licensed|self-owned|own|original)\b|允许|已授权|自有|原创|通过", value, re.I))


def is_no_or_unknown(value: str) -> bool:
    return bool(re.search(r"\b(no|false|unknown|unclear|unlicensed|not allowed|forbidden|pending)\b|否|未知|不清楚|未授权|禁止|待定", value, re.I))


def wants_audio_tool(value: str) -> bool:
    if re.search(r"\b(no|not|without|do not|don't)\b[^.\n;]{0,40}\b(audio upload|upload audio|audio seed|sample|stem|stems)\b|不上传|不使用音频|不用音频", value, re.I):
        return False
    return bool(re.search(r"audio upload|upload audio|cover|remix|sample|stem|stems|uploaded audio|audio seed|原曲上传|上传音频|翻唱|采样", value, re.I))


def neutral_action(value: str) -> bool:
    return bool(re.search(r"neutral|style dna|abstract|text-only|manual listening|do not upload|remove|original|中性|抽象|文字|去身份|不上传|原创", value, re.I))


def protected_identity_hits(text: str) -> list[str]:
    hits: list[str] = []
    for name in PROTECTED_IDENTITY_NAMES:
        if re.fullmatch(r"[A-Za-z0-9 .'\-&]+", name):
            pattern = rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])"
            found = re.search(pattern, text, flags=re.I)
        else:
            found = name.casefold() in text.casefold()
        if found:
            hits.append(name)
    return hits


def removal_passed(text: str) -> bool:
    lowered = text.casefold()
    return (
        re.search(r"^Decision:\s*(pass|approved|removed|clear)\b", text, flags=re.I | re.M) is not None
        or "protected identity removed: yes" in lowered
        or "artist identity removed: yes" in lowered
        or "no protected identity" in lowered
    )


def analyze(docs: dict[str, str]) -> tuple[dict[str, str], list[Finding]]:
    reference_paths = [
        RIGHTS_PRECHECK_FILE,
        SOURCE_RIGHTS_FILE,
        REFERENCE_RIGHTS_FILE,
        REFERENCE_SET_FILE,
        STYLE_DNA_FILE,
        PROTECTED_REMOVAL_FILE,
        REFERENCE_BOUNDARY_FILE,
    ]
    fields = {
        "reference_set": extract_value(docs, reference_paths, ["Reference set", "Reference", "Reference title", "References"]),
        "material_type": extract_value(docs, reference_paths, ["Material type", "Source type"]),
        "owner": extract_value(docs, reference_paths, ["Owner", "Rights owner"]),
        "license_permission": extract_value(docs, reference_paths, ["License / permission", "Permission", "License"]),
        "can_upload_audio": extract_value(docs, reference_paths, ["Can upload audio?", "Can upload audio", "Audio upload allowed"]),
        "commercial_use": extract_value(docs, reference_paths, ["Can use for commercial release?", "Commercial use", "Commercial release"]),
        "contains_lyrics": extract_value(docs, reference_paths, ["Contains third-party lyrics?", "Contains lyrics"]),
        "contains_melody": extract_value(docs, reference_paths, ["Contains third-party melody/riff/sample?", "Contains melody", "Contains riff", "Contains sample"]),
        "contains_voice": extract_value(docs, reference_paths, ["Contains identifiable voice?", "Contains voice"]),
        "allowed_action": extract_value(docs, reference_paths, ["Allowed action", "Allowed use", "Allowed use in this project"]),
        "forbidden_use": extract_value(docs, reference_paths, ["Forbidden use", "Forbidden action", "Do not use"]),
        "rights_status": extract_value(docs, reference_paths, ["Rights status", "Reference rights status"]),
        "tempo_meter": extract_value(docs, [STYLE_DNA_FILE], ["Tempo / meter", "Tempo", "Meter"]),
        "groove": extract_value(docs, [STYLE_DNA_FILE], ["Groove"]),
        "form": extract_value(docs, [STYLE_DNA_FILE], ["Form"]),
        "energy_timeline": extract_value(docs, [STYLE_DNA_FILE], ["Energy timeline", "Emotional timeline"]),
        "hook_mechanism": extract_value(docs, [STYLE_DNA_FILE], ["Hook mechanism"]),
        "vocal_delivery": extract_value(docs, [STYLE_DNA_FILE], ["Vocal delivery"]),
        "arrangement_palette": extract_value(docs, [STYLE_DNA_FILE], ["Arrangement palette"]),
        "production_space": extract_value(docs, [STYLE_DNA_FILE], ["Production space"]),
        "do_not_copy": extract_value(docs, [STYLE_DNA_FILE, REFERENCE_SET_FILE, REFERENCE_BOUNDARY_FILE], ["Do-not-copy list", "Do not copy", "Do-not-copy", "Forbidden use"]),
        "original_contribution": extract_value(docs, [STYLE_DNA_FILE, REFERENCE_BOUNDARY_FILE], ["Original contribution required", "Original contribution", "What is original"]),
        "prompt_implication": extract_value(docs, [STYLE_DNA_FILE, REFERENCE_BOUNDARY_FILE], ["Prompt implication", "Neutral prompt", "Prompt-safe language"]),
        "suno_tool_choice": extract_value(docs, [STYLE_DNA_FILE, REFERENCE_BOUNDARY_FILE], ["Suno tool choice", "Tool choice", "Provider tool choice"]),
        "similarity_risk": extract_value(docs, [STYLE_DNA_FILE, REFERENCE_BOUNDARY_FILE], ["Similarity risk", "Similarity risk score", "Reference similarity"]),
        "reference_boundary": extract_value(docs, [REFERENCE_BOUNDARY_FILE], ["Reference boundary", "Boundary", "Allowed abstraction"]),
        "artist_names_present": extract_value(docs, reference_paths + [STYLE_FILE], ["Artist names present"]),
        "song_titles_present": extract_value(docs, reference_paths + [STYLE_FILE], ["Song titles present"]),
        "protected_removed": extract_value(docs, [PROTECTED_REMOVAL_FILE], ["Protected identity removed", "Artist identity removed", "Song identity removed"]),
        "protected_text": docs.get(PROTECTED_REMOVAL_FILE, ""),
    }

    findings: list[Finding] = []
    required = [
        ("reference_set_missing", fields["reference_set"] or fields["artist_names_present"], "Reference set or no-reference status is missing.", "fill reference-set.md"),
        ("allowed_action_missing", fields["allowed_action"], "Allowed action is missing.", "fill reference-rights.md"),
        ("forbidden_use_missing", fields["forbidden_use"], "Forbidden use is missing.", "fill reference-rights.md"),
        ("do_not_copy_missing", fields["do_not_copy"], "Do-not-copy list is missing.", "fill style-dna-card.md"),
        ("original_contribution_missing", fields["original_contribution"], "Original contribution requirement is missing.", "fill style-dna-card.md"),
        ("prompt_implication_missing", fields["prompt_implication"], "Prompt-safe implication is missing.", "fill style-dna-card.md"),
        ("reference_boundary_missing", fields["reference_boundary"], "Reference boundary is missing.", "fill reference-boundary.md"),
    ]
    for code, value, message, route in required:
        if not value:
            findings.append(Finding("blocker", code, message, route))

    style_fields = ["tempo_meter", "groove", "form", "energy_timeline", "hook_mechanism", "vocal_delivery", "arrangement_palette", "production_space"]
    missing_style = [name for name in style_fields if not fields[name]]
    if len(missing_style) > 3:
        findings.append(Finding("blocker", "style_dna_too_thin", "Style DNA card is too thin for neutral prompt translation.", "fill style-dna-card.md"))

    names_present = fields["artist_names_present"].casefold() in {"yes", "true"} or fields["song_titles_present"].casefold() in {"yes", "true"}
    protected_text = docs.get(PROTECTED_REMOVAL_FILE, "")
    if names_present and not removal_passed(protected_text):
        findings.append(Finding("blocker", "protected_identity_removal_missing", "Artist/song names are present but protected identity removal has not passed.", "fill protected-identity-removal.md"))

    if fields["allowed_action"] and not neutral_action(fields["allowed_action"]) and not is_yes(fields["license_permission"]):
        findings.append(Finding("blocker", "allowed_action_not_neutral", "Allowed action is not clearly neutral, self-owned, or licensed.", "repair reference-rights.md"))

    if wants_audio_tool(fields["suno_tool_choice"] + " " + fields["allowed_action"]):
        upload = fields["can_upload_audio"] or fields["license_permission"]
        if not is_yes(upload):
            findings.append(Finding("blocker", "audio_tool_without_upload_rights", "Audio Upload/Cover/sample-style tool choice requires explicit upload rights.", "repair reference-rights.md"))

    third_party_markers = " ".join([fields["contains_lyrics"], fields["contains_melody"], fields["contains_voice"]])
    if re.search(r"\byes\b|是|包含", third_party_markers, re.I) and not neutral_action(fields["allowed_action"]):
        findings.append(Finding("blocker", "third_party_material_not_neutralized", "Third-party lyrics, melody/riff/sample, or voice must be neutralized before prompting.", "repair reference boundary"))

    prompt_safe_text = "\n".join([fields["prompt_implication"], docs.get(STYLE_FILE, ""), docs.get(EXCLUDE_FILE, "")])
    hits = protected_identity_hits(prompt_safe_text)
    if hits:
        findings.append(Finding("blocker", "protected_identity_in_prompt_route", "Prompt-facing reference route contains protected names: " + ", ".join(hits[:5]), "remove names and write neutral style DNA"))

    if fields["do_not_copy"] and not re.search(r"melody|lyrics|riff|voice|artist|song|identity|sample|旋律|歌词|人声|艺人|歌名|采样", fields["do_not_copy"], re.I):
        findings.append(Finding("warning", "do_not_copy_too_vague", "Do-not-copy list should name melody, lyrics, riff, voice, artist identity, or sample.", "tighten style-dna-card.md"))
    if fields["similarity_risk"] and re.search(r"\b([3-5]|high|red)\b|高|红", fields["similarity_risk"], re.I):
        findings.append(Finding("blocker", "similarity_risk_high", "Similarity risk is too high for prompt compile.", "repair reference boundary or rewrite hook/riff/voice"))
    if fields["commercial_use"] and is_no_or_unknown(fields["commercial_use"]):
        findings.append(Finding("warning", "commercial_use_unclear", "Commercial use is unclear; release gate must re-check rights.", "route to release rights"))

    return fields, findings


def render_finding_table(findings: list[Finding]) -> str:
    if not findings:
        return "| severity | code | message | route |\n|---|---|---|---|\n| pass | none | reference style DNA approved | prompt compile |\n"
    rows = ["| severity | code | message | route |", "|---|---|---|---|"]
    for finding in findings:
        rows.append(f"| {finding.severity} | {finding.code} | {finding.message} | {finding.route} |")
    return "\n".join(rows) + "\n"


def reference_tags(fields: dict[str, str]) -> str:
    pieces = [fields["reference_set"], fields["allowed_action"], fields["reference_boundary"]]
    return ", ".join(piece for piece in pieces if piece) or "NEEDS_REPAIR: reference tags"


def style_dna_tags(fields: dict[str, str]) -> str:
    pieces = [
        fields["tempo_meter"],
        fields["groove"],
        fields["form"],
        fields["energy_timeline"],
        fields["hook_mechanism"],
        fields["vocal_delivery"],
        fields["arrangement_palette"],
        fields["production_space"],
    ]
    return ", ".join(piece for piece in pieces if piece) or "NEEDS_REPAIR: style DNA tags"


def render_audit(project_root: Path, fields: dict[str, str], findings: list[Finding]) -> str:
    blockers = [finding for finding in findings if finding.severity == "blocker"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    decision = "pass" if not blockers else "repair before prompt compile"
    return f"""# Reference DNA Audit

Generated by: tools/audit_music_reference_dna.py
Project root: {project_root}
Decision: {decision}

Reference set: {fields['reference_set'] or 'NEEDS_REPAIR: reference set'}
Allowed action: {fields['allowed_action'] or 'NEEDS_REPAIR: allowed action'}
Forbidden use: {fields['forbidden_use'] or 'NEEDS_REPAIR: forbidden use'}
Can upload audio: {fields['can_upload_audio'] or ''}
Commercial use: {fields['commercial_use'] or ''}
Protected identity removed: {fields['protected_removed'] or ('yes' if removal_passed(fields.get('protected_text', '')) else 'NEEDS_REPAIR: protected identity removal')}
Reference boundary: {fields['reference_boundary'] or 'NEEDS_REPAIR: reference boundary'}
Similarity risk: {fields['similarity_risk'] or 'NEEDS_REPAIR: similarity risk'}
Blockers: {len(blockers)}
Warnings: {len(warnings)}

## Reference Design

| field | value |
|---|---|
| material type | {fields['material_type'] or ''} |
| owner | {fields['owner'] or ''} |
| license / permission | {fields['license_permission'] or ''} |
| tempo / meter | {fields['tempo_meter'] or ''} |
| groove | {fields['groove'] or ''} |
| form | {fields['form'] or ''} |
| energy timeline | {fields['energy_timeline'] or ''} |
| hook mechanism | {fields['hook_mechanism'] or ''} |
| vocal delivery | {fields['vocal_delivery'] or ''} |
| arrangement palette | {fields['arrangement_palette'] or ''} |
| production space | {fields['production_space'] or ''} |
| do-not-copy list | {fields['do_not_copy'] or ''} |
| original contribution | {fields['original_contribution'] or ''} |
| prompt implication | {fields['prompt_implication'] or ''} |
| Suno tool choice | {fields['suno_tool_choice'] or ''} |

## Findings

{render_finding_table(findings)}
## Prompt Routing

Reference tags: {reference_tags(fields)}
Style DNA tags: {style_dna_tags(fields)}
Protected identity removal: {'pass' if decision == 'pass' else 'repair'}
Similarity blind test: ordinary listener should not name a protected reference, melody, lyric, riff, singer, or signature arrangement
Prompt-safe reference route: {fields['prompt_implication'] or fields['allowed_action'] or 'NEEDS_REPAIR: prompt-safe route'}
Exclude additions: artist imitation, recognizable melody, copied lyrics, signature riff, unauthorized audio upload, reference singer voice
Repair route: reference-rights, style-dna-card, protected-identity-removal, reference-boundary, prompt fields, similarity review, or original topline rewrite
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
        print(f"reference DNA audit has {len(blockers)} blocker(s).", file=sys.stderr)
        for finding in blockers:
            print(f"- {finding.code}: {finding.message} -> {finding.route}", file=sys.stderr)
        return 1 if args.strict else 0

    print("reference DNA audit passed.")
    print(f"audit: {project_root / args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
