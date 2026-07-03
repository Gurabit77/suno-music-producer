#!/usr/bin/env python3
"""Prepare DAW/stems handoff files for a selected AI music take.

This tool starts after take review and repair routing. It does not transcribe
audio or inspect stems; it turns existing project evidence into a production
handoff skeleton for DAW, musicians, vocalists, and mix replacement work.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from review_music_takes import TakeScore, load_project, parse_markdown_tables
from route_music_repairs import parse_decision_file


TAKE_DECISION = "06_review/take-selection-decision.md"
REPAIR_ROUTE = "07_repair/repair-route-map.md"

OUTPUTS = {
    "best_take_lock": "08_stems-daw/best-take-lock.md",
    "handoff_intent": "08_stems-daw/daw-handoff-intent.md",
    "export_ledger": "08_stems-daw/export-and-stems-ledger.md",
    "tempo_grid": "08_stems-daw/tempo-map-and-section-grid.md",
    "lead_sheet": "08_stems-daw/lead-sheet-and-chord-chart.md",
    "midi_correction": "08_stems-daw/midi-transcription-and-correction.md",
    "stem_triage": "08_stems-daw/stem-quality-triage.md",
    "overdub_priority": "08_stems-daw/human-overdub-priority.md",
    "vocal_rerecord": "08_stems-daw/vocal-rerecord-plan.md",
    "rhythm_plan": "08_stems-daw/rhythm-section-rerecord-plan.md",
    "hybrid_session": "08_stems-daw/hybrid-arrangement-session.md",
    "mix_replacement": "08_stems-daw/mix-replacement-map.md",
    "session_versioning": "08_stems-daw/session-versioning.md",
    "rights_link": "08_stems-daw/human-contribution-and-rights-link.md",
    "final_review": "08_stems-daw/final-humanized-master-review.md",
    "session_pack": "08_stems-daw/session-pack.md",
}


@dataclass(frozen=True)
class RepairRoute:
    problem: str
    layer: str
    severity: str
    route: str
    expected_output: str
    regression: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def key_value_from_files(project_root: Path, rel_paths: list[str], labels: list[str]) -> str:
    wanted = {label.lower() for label in labels}
    for rel in rel_paths:
        text = read_text(project_root / rel)
        for line in text.splitlines():
            stripped = re.sub(r"^[-*]\s+", "", line.strip())
            match = re.match(r"^([^:]{1,80}):\s*(.+)$", stripped)
            if match and match.group(1).strip().lower() in wanted:
                value = match.group(2).strip().strip('"')
                if value and value.lower() not in {"todo", "tbd", "n/a", "none"}:
                    return value
    return ""


def parse_repair_routes(project_root: Path) -> tuple[list[RepairRoute], list[str]]:
    path = project_root / REPAIR_ROUTE
    if not path.exists():
        return [], [f"missing {REPAIR_ROUTE}; run tools/route_music_repairs.py first"]
    routes: list[RepairRoute] = []
    for table in parse_markdown_tables(path.read_text(encoding="utf-8")):
        headers = set(table[0].keys()) if table else set()
        if "problem" not in headers or "layer" not in headers:
            continue
        for row in table:
            problem = row.get("problem", "").strip()
            if not problem or problem.lower() == "problem":
                continue
            routes.append(
                RepairRoute(
                    problem=problem,
                    layer=row.get("layer", "").strip(),
                    severity=row.get("severity", "").strip(),
                    route=(row.get("repair_route") or row.get("route") or "").strip(),
                    expected_output=row.get("expected_output", "").strip(),
                    regression=(row.get("regression_listen") or row.get("regression") or "").strip(),
                )
            )
    if not routes:
        return [], [f"no repair routes found in {REPAIR_ROUTE}"]
    return routes, []


def daw_ready(action: str, routes: list[RepairRoute]) -> bool:
    if action == "lock for post-production":
        return True
    if action != "repair candidate":
        return False
    daw_terms = re.compile(r"daw|stem|vocal|groove|drum|bass|mix|post|artifact|human|re[- ]?record|overdub", re.I)
    return any(daw_terms.search(" ".join([route.layer, route.route, route.expected_output])) for route in routes)


def keep_list(take: TakeScore) -> list[str]:
    keeps: list[str] = []
    if take.values.get("hook", 0) >= 4.0:
        keeps.append("title phrase / chorus hook")
    if take.values.get("vocal_identity", 0) >= 4.0:
        keeps.append("vocal identity direction")
    if take.values.get("groove", 0) >= 4.0:
        keeps.append("drums-bass pocket direction")
    if take.values.get("form", 0) >= 4.0:
        keeps.append("section form and payoff")
    if take.values.get("alignment", 0) >= 4.0:
        keeps.append("brief alignment")
    return keeps or ["best musical idea from locked take"]


def replace_list(routes: list[RepairRoute]) -> list[str]:
    replacements: list[str] = []
    text = " ".join(" ".join([route.problem, route.layer, route.route]) for route in routes).lower()
    if "vocal" in text or "声线" in text:
        replacements.append("lead vocal guide may need human rerecord or vocal production")
    if "groove" in text or "drum" in text or "bass" in text:
        replacements.append("rhythm section may need MIDI correction or human overdub")
    if "stem" in text or "artifact" in text or "separation" in text:
        replacements.append("artifact-heavy stems should be guide/replace, not final")
    if "mix" in text or "post" in text:
        replacements.append("mix/post layers require stem cleanup and replacement map")
    return replacements or ["replace or mute any AI layer that fails stem-quality triage"]


def lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def context(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> dict[str, str]:
    title = key_value_from_files(project_root, ["01_brief/song-brief.md", "04_prompt/prompt-compile-brief.md", "README.md"], ["song", "song title", "title"]) or project_root.name
    project = key_value_from_files(project_root, ["01_brief/project-intake.md", "04_prompt/prompt-compile-brief.md", "README.md"], ["project", "artist / catalog", "project / artist"]) or ""
    language = key_value_from_files(project_root, ["01_brief/song-brief.md", "04_prompt/prompt-compile-brief.md", "README.md"], ["language"]) or ""
    lane = key_value_from_files(project_root, ["01_brief/song-brief.md", "04_prompt/prompt-compile-brief.md", "README.md"], ["genre lane", "lane"]) or ""
    primary = routes[0]
    return {
        "title": title,
        "project": project,
        "language": language,
        "lane": lane,
        "take": take.take_id,
        "action": action,
        "primary_problem": primary.problem,
        "primary_layer": primary.layer,
        "primary_route": primary.route,
        "known_issue": take.ledger.get("known_issue", ""),
        "provider_model": take.ledger.get("provider_model", ""),
        "prompt_package": take.ledger.get("prompt_package", "04_prompt/prompt-package-v001.md"),
        "settings": take.ledger.get("settings", ""),
    }


def render_best_take_lock(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    ctx = context(project_root, take, action, routes)
    return f"""# Best Take Lock

Generated by: tools/prepare_music_daw_handoff.py
Project root: {project_root}

Project: {ctx['project']}
Song: {ctx['title']}
Locked take: {ctx['take']}
Take action: {ctx['action']}
Source provider/model: {ctx['provider_model']}
Prompt package: {ctx['prompt_package']}
Settings: {ctx['settings']}

## Why This Take

- Composite decision comes from `06_review/take-selection-decision.md`.
- Primary repair route: {ctx['primary_problem']} -> {ctx['primary_route']}

## Must Preserve

{lines(keep_list(take))}

## May Replace

{lines(replace_list(routes))}

## Do Not Proceed If

- `07_repair/repair-route-map.md` is unresolved.
- rights/source records are unclear.
- no full mix reference or export plan exists.
"""


def render_handoff_intent(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    ctx = context(project_root, take, action, routes)
    collaborator = "vocalist / producer / mix engineer"
    if "vocal" in ctx["primary_layer"].lower():
        collaborator = "vocalist or vocal producer"
    elif "groove" in ctx["primary_layer"].lower():
        collaborator = "drummer, bassist, or rhythm producer"
    elif "mix" in ctx["primary_layer"].lower() or "post" in ctx["primary_layer"].lower():
        collaborator = "mix engineer or producer"
    return f"""# DAW Handoff Intent

Generated by: tools/prepare_music_daw_handoff.py

Intent: turn the selected AI take into an editable DAW/session pack.
Primary collaborator: {collaborator}
Final target: demo / release master / vocalist demo / band production
Human contribution target:
- lyrics:
- melody:
- vocal:
- instruments:
- arrangement:
- mix:

AI material role:
- guide reference mix
- guide vocal or instrumental stems where useful
- keep selected textures only if they pass stem-quality triage

Primary blocker: {ctx['primary_problem']}
Repair route: {ctx['primary_route']}
"""


def render_export_ledger(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    ctx = context(project_root, take, action, routes)
    return f"""# Export And Stems Ledger

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {ctx['take']}

Export date:
Platform / provider: {ctx['provider_model']}
Plan / subscription:
Prompt package: {ctx['prompt_package']}

Files:
- full_mix_reference.wav:
- multitrack_stems.zip:
- selected_range_hook.wav:
- selected_range_bridge.wav:
- individual_clips/:
- midi/:
- lyrics.md:
- prompt.md:
- rights-notes.md:

Stem ledger:
| stem | source | export method | quality | intended use | rights note |
|---|---|---|---|---|---|
| lead vocal | AI / human / upload | Multitrack | guide / keep / replace | guide vocal / rerecord reference | |
| drums | AI / human / upload | Multitrack | keep / replace | drummer reference | |
| bass | AI / human / upload | Multitrack | keep / replace | MIDI + bassist chart | |
| harmony / instruments | AI / MIDI / human | Multitrack | keep / guide / replace | arrangement reference | |

Do not put uncleared third-party reference audio into this session pack.
"""


def render_tempo_grid(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Tempo Map And Section Grid

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

Project BPM:
Manual BPM in Studio:
DAW BPM:
Time signature:
Pickup:
Swing / shuffle:
Tempo drift:
- keep:
- lock:
- manual tempo map:

Section grid:
| bar | timestamp | section | notes |
|---|---|---|---|
| 1 | 0:00 | intro | identity motif |
| | | verse 1 | vocal entrance |
| | | pre-chorus | lift begins |
| | | chorus | title hook |
| | | bridge | contrast |
| | | final chorus | payoff |
| | | outro | clean ending |
"""


def render_lead_sheet(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    ctx = context(project_root, take, action, routes)
    return f"""# Lead Sheet And Chord Chart

Generated by: tools/prepare_music_daw_handoff.py

Title: {ctx['title']}
Key:
BPM:
Meter:
Feel / lane: {ctx['lane']}
Language: {ctx['language']}

Lead sheet requirements:
- melody / guide contour:
- lyrics aligned to bars:
- breath and long-note marks:
- chord symbols:
- section roadmap:
- ensemble hooks:

Chord chart:
Intro:
Verse:
Pre:
Chorus:
Bridge:
Final chorus:
Outro:

Prosody check:
- Mandarin tone / Japanese mora / Korean-English hook / English stress:
"""


def render_midi(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# MIDI Transcription And Correction

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

MIDI source:
Tool:
Stem:
Audio quality:
Confidence:
- pitch:
- rhythm:
- articulation:
- harmony:

Human correction:
- wrong notes:
- missing pickup:
- quantization:
- octave:
- chord spelling:
- swing / groove:

Final MIDI role:
- guide melody
- bassist chart
- drum programming
- harmony sketch
- replacement instrument
"""


def render_stem_triage(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Stem Quality Triage

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

| stem | grade | role | artifact / issue | action |
|---|---|---|---|---|
| full mix reference | A/B/C/D | reference | | archive immutable |
| lead vocal | A/B/C/D | keep / guide / replace | | |
| backing vocal | A/B/C/D | keep / guide / replace | | |
| drums | A/B/C/D | keep / guide / replace | | |
| bass | A/B/C/D | keep / guide / replace | | |
| guitar / piano / keys | A/B/C/D | keep / guide / replace | | |
| synth / pad / FX | A/B/C/D | keep / guide / replace | | |

Grades:
- A: can keep in final mix.
- B: usable with editing / EQ / automation.
- C: guide or texture only.
- D: mute, regenerate, or rerecord.
"""


def render_overdub(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    route_text = " ".join([route.layer + " " + route.route for route in routes]).lower()
    lead_priority = "1" if "vocal" in route_text else "2"
    rhythm_priority = "1" if "groove" in route_text or "drum" in route_text or "bass" in route_text else "2"
    return f"""# Human Overdub Priority

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

| priority | layer | reason | musician | source reference | deliverable |
|---:|---|---|---|---|---|
| {lead_priority} | lead vocal | vocal identity, breath, diction, or tail vowels need human choice | singer / vocal producer | guide vocal + lead sheet | comped vocal WAV |
| {rhythm_priority} | drums / bass | groove and body feel need human pocket | drummer / bassist | tempo map + stems + MIDI | multitrack drums / DI bass |
| 3 | signature riff / hook instrument | identity layer must be playable | guitarist / keyboardist | MIDI + full mix | rerecorded hook stem |
| 4 | chorus doubles / harmonies | reduce AI choir smear | vocalist | harmony map | stacked vocal stems |
| 5 | AI texture | keep only if it supports identity | producer | stem triage | cleaned texture stem |
"""


def render_vocal_rerecord(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Vocal Rerecord Plan

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

Singer:
Key:
Range:
Tone:
Verse delivery:
Pre delivery:
Chorus delivery:
Bridge delivery:
Ad-libs:
Doubles:
Harmony stack:

Prosody notes:
- Mandarin tone / stress:
- Japanese mora density:
- Korean-English hook:
- English stress and consonants:

Keep from AI guide:
{lines(keep_list(take))}

Change from AI guide:
- breath placement:
- tail vowels:
- vibrato:
- emotional pacing:
"""


def render_rhythm(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Rhythm Section Rerecord Plan

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

Groove:
Kick role:
Bass role:
Snare/backbeat:
Hi-hat/cymbal density:
Swing / push / laid-back:

Verse:
Pre:
Chorus:
Bridge:
Final chorus:

Must hit:
- bar:
- cue:

Must avoid:
- overplaying:
- generic fill:
- muddy sub:
- machine-like quantization:
"""


def render_hybrid(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Hybrid Arrangement Session

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

| layer | category | action | reason |
|---|---|---|---|
| lead vocal | core human performance | rerecord / keep guide | |
| drums | core human performance | rerecord / reinforce | |
| bass | core human performance | rerecord / MIDI replace | |
| piano / guitar hook | core human performance | rerecord / MIDI replace | |
| synth / pad / FX | AI texture | keep low / redesign / mute | |

Principle: human core layers should dominate timing, dynamics, and emotional causality; AI textures must not hide the lead vocal, groove, or hook.
"""


def render_mix_replacement(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Mix Replacement Map

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

| original AI stem | action | new source | mix note |
|---|---|---|---|
| lead_vocal_ai.wav | guide / mute / blend | lead_vocal_comp.wav | keep AI guide archived only if rerecorded |
| drums_ai.wav | reinforce / mute | live_drums_multitrack / programmed drums | align downbeats, keep room |
| bass_ai.wav | mute / blend | bass_DI.wav / MIDI bass | lock with kick |
| pad_ai.wav | keep low | AI stem / redesigned pad | high-pass, duck under vocal |
| hook_synth_ai.wav | keep / MIDI layer | AI stem + MIDI layer | automate chorus only |

A/B references:
- original AI mix
- hybrid mix
- human-core mix
"""


def render_session_versioning(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Session Versioning

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

Recommended session directory:

```text
song-title_session/
  00_admin/
  01_reference/
  02_exports/
  03_transcription/
  04_overdubs/
  05_session/
  06_mix/
  07_review/
```

Version rule:
- keep AI guide and human overdubs in separate folders
- every bounce includes date, version, and source
- no final_final filenames
"""


def render_rights_link(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Human Contribution And Rights Link

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

Human contribution ledger:
- lyrics by:
- melody/topline by:
- chord chart by:
- lead sheet transcription by:
- lead vocal by:
- drums by:
- bass by:
- guitar/keys by:
- arrangement by:
- editing/mix/master by:

AI contribution:
- generated reference mix:
- stems:
- MIDI extraction:
- retained AI textures:

Rights gate:
- commercial use allowed:
- upload source cleared:
- voice rights cleared:
- sample/reference cleared:
- distributor disclosure needed:

Link to release file: 11_release/human-contribution-ledger.md
"""


def render_final_review(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    return f"""# Final Humanized Master Review

Generated by: tools/prepare_music_daw_handoff.py
Locked take: {take.take_id}

Blind review package:
- original AI mix:
- hybrid mix:
- human-core mix:
- final master:

Questions:
- Does the lead vocal sound like a performed take?
- Do drums and bass feel played, programmed with intention, or convincingly edited?
- Did the hook survive replacement work?
- Are retained AI textures clearly subordinate to human core layers?
- Are rights and human contribution records complete?

Decision:
- keep
- repair again
- route to mix/master QC
- hold release
"""


def render_session_pack(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> str:
    ctx = context(project_root, take, action, routes)
    return f"""# Session Pack

Generated by: tools/prepare_music_daw_handoff.py
Project root: {project_root}

Project: {ctx['project']}
Song: {ctx['title']}
Locked take: {ctx['take']}
Take action: {ctx['action']}
Primary route: {ctx['primary_problem']} -> {ctx['primary_route']}

## Required Files

- 08_stems-daw/best-take-lock.md
- 08_stems-daw/daw-handoff-intent.md
- 08_stems-daw/export-and-stems-ledger.md
- 08_stems-daw/tempo-map-and-section-grid.md
- 08_stems-daw/lead-sheet-and-chord-chart.md
- 08_stems-daw/midi-transcription-and-correction.md
- 08_stems-daw/stem-quality-triage.md
- 08_stems-daw/human-overdub-priority.md
- 08_stems-daw/vocal-rerecord-plan.md
- 08_stems-daw/rhythm-section-rerecord-plan.md
- 08_stems-daw/hybrid-arrangement-session.md
- 08_stems-daw/mix-replacement-map.md
- 08_stems-daw/human-contribution-and-rights-link.md

## Handoff Summary

tempo:
meter:
key:
section grid:
stems:
MIDI:
lead sheet:
chord chart:
what to rerecord: {', '.join(replace_list(routes))}
what to keep from AI: {', '.join(keep_list(take))}
known artifacts: {ctx['known_issue']}
human contribution plan:
"""


def build_outputs(project_root: Path, take: TakeScore, action: str, routes: list[RepairRoute]) -> dict[str, str]:
    return {
        OUTPUTS["best_take_lock"]: render_best_take_lock(project_root, take, action, routes),
        OUTPUTS["handoff_intent"]: render_handoff_intent(project_root, take, action, routes),
        OUTPUTS["export_ledger"]: render_export_ledger(project_root, take, action, routes),
        OUTPUTS["tempo_grid"]: render_tempo_grid(project_root, take, action, routes),
        OUTPUTS["lead_sheet"]: render_lead_sheet(project_root, take, action, routes),
        OUTPUTS["midi_correction"]: render_midi(project_root, take, action, routes),
        OUTPUTS["stem_triage"]: render_stem_triage(project_root, take, action, routes),
        OUTPUTS["overdub_priority"]: render_overdub(project_root, take, action, routes),
        OUTPUTS["vocal_rerecord"]: render_vocal_rerecord(project_root, take, action, routes),
        OUTPUTS["rhythm_plan"]: render_rhythm(project_root, take, action, routes),
        OUTPUTS["hybrid_session"]: render_hybrid(project_root, take, action, routes),
        OUTPUTS["mix_replacement"]: render_mix_replacement(project_root, take, action, routes),
        OUTPUTS["session_versioning"]: render_session_versioning(project_root, take, action, routes),
        OUTPUTS["rights_link"]: render_rights_link(project_root, take, action, routes),
        OUTPUTS["final_review"]: render_final_review(project_root, take, action, routes),
        OUTPUTS["session_pack"]: render_session_pack(project_root, take, action, routes),
    }


def write_if_allowed(path: Path, text: str, allow_overwrite: bool) -> None:
    if path.exists() and not allow_overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Song project root.")
    parser.add_argument("--write", action="store_true", help="Write DAW handoff files.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow overwriting existing DAW handoff files.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when take/review/repair evidence is missing or not DAW-ready.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"error: project root not found: {project_root}", file=sys.stderr)
        return 2

    best_take, action, decision_errors = parse_decision_file(project_root)
    _, scores, review_errors = load_project(project_root)
    routes, route_errors = parse_repair_routes(project_root)
    errors = decision_errors + review_errors + route_errors
    if best_take and best_take not in scores:
        errors.append(f"best take {best_take} is not present in blind-review scores")
    if errors:
        for error in errors:
            print(f"daw handoff evidence error: {error}", file=sys.stderr)
        return 1 if args.strict else 0

    take = scores[best_take]
    if not daw_ready(action, routes):
        message = f"take action {action!r} is not ready for DAW/stems handoff"
        print(f"daw handoff evidence error: {message}", file=sys.stderr)
        return 1 if args.strict else 0

    outputs = build_outputs(project_root, take, action, routes)
    if args.write:
        try:
            for rel, text in outputs.items():
                write_if_allowed(project_root / rel, text, args.allow_overwrite)
        except FileExistsError as exc:
            print(f"error: output exists, use --allow-overwrite: {exc}", file=sys.stderr)
            return 2
    else:
        print(outputs[OUTPUTS["session_pack"]])

    print(f"selected take: {take.take_id}")
    print(f"action: {action}")
    print("daw handoff files prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
