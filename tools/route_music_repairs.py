#!/usr/bin/env python3
"""Route a selected AI music take into concrete repair files.

The router starts after tools/review_music_takes.py. It reads the take decision
and blind-review score evidence, then writes repair-route-map,
artifact-severity-score, repair-log, and regression-listen starter files.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from review_music_takes import TakeScore, decision_for_take, load_project


TAKE_DECISION = "06_review/take-selection-decision.md"
ARTIFACT_SCORE = "07_repair/artifact-severity-score.md"
REPAIR_ROUTE = "07_repair/repair-route-map.md"
REPAIR_LOG = "07_repair/repair-log.md"
REGRESSION_LISTEN = "07_repair/regression-listen.md"


@dataclass(frozen=True)
class RepairIssue:
    problem: str
    layer: str
    severity: int
    evidence: str
    route: str
    expected_output: str
    regression: str


@dataclass(frozen=True)
class SunoEditRoute:
    tool: str
    action: str
    official_basis: str
    regression: str


FIELD_ROUTES = {
    "alignment": (
        "brief / prompt alignment mismatch",
        "brief/prompt",
        "AI 音乐 Prompt 编译与生成前预检工作流",
        "04_prompt/prompt-package-v002.md or repaired brief-freeze",
        "blind review alignment improves without losing preference",
    ),
    "preference": (
        "song is aligned but not compelling",
        "song idea / arrangement payoff",
        "AI 音乐 Prompt 实验矩阵与版本收敛工作流",
        "single-variable batch with clearer hook, payoff, or arrangement role",
        "preference improves while alignment stays stable",
    ),
    "hook": (
        "chorus hook or title phrase is weak",
        "topline",
        "AI 音乐 Topline Hook 与旋律草稿工作流",
        "03_writing/topline-map.md and revised chorus title phrase",
        "20-30 second hook memory test improves",
    ),
    "vocal_identity": (
        "lead vocal identity or performance is weak",
        "vocal identity",
        "AI 音乐声线身份与演唱表演工作流",
        "03_writing/singer-brief.md and 06_review/vocal-reverse-caption.md",
        "vocal-only blind review identifies a specific singer identity",
    ),
    "groove": (
        "groove or rhythm-section believability is weak",
        "groove",
        "AI 音乐乐器演奏真实感与 Groove Humanization 工作流",
        "03_writing/groove-audit.md and master pocket repair note",
        "instrument-only blind review and body-feel score improve",
    ),
    "form": (
        "song form or section payoff is weak",
        "structure",
        "AI 音乐结构动态与段落转场工作流",
        "03_writing/energy-map.md and structure-repair-log.md",
        "verse 2, bridge, final chorus, and outro feel intentional",
    ),
}


def suno_edit_route_for_issue(issue: RepairIssue, take: TakeScore, action: str) -> SunoEditRoute:
    layer = issue.layer.casefold()
    problem = issue.problem.casefold()
    evidence = issue.evidence.casefold()

    if "rights" in layer:
        return SunoEditRoute(
            tool="Hold before Suno edit",
            action="Resolve source rights, voice rights, reference distance, and release eligibility before any regeneration or public share.",
            official_basis="rights gate plus Suno feature-source rules in local official notes",
            regression="rights status becomes publishable or the project stays held",
        )

    if "lyric" in layer or "prosody" in layer:
        return SunoEditRoute(
            tool="Suno Song Editor / Edit Lyrics + Replace Section",
            action="Highlight the affected phrase or section, replace only the lyric/prosody problem, audition the two section versions, then rebuild the whole song.",
            official_basis="official-song-editor.md and official-replace-section.md",
            regression="diction, stress, tone, and title phrase improve while melody identity remains stable",
        )

    if "topline" in layer or "hook" in problem:
        return SunoEditRoute(
            tool="Suno Song Editor / Replace Section",
            action="Replace the chorus or pre-chorus window around the title hook; if the hook concept itself is weak, return to a one-variable prompt batch instead.",
            official_basis="official-song-editor.md and official-replace-section.md",
            regression="20-30 second hook recall improves without changing the song identity",
        )

    if "structure" in layer or "form" in layer:
        return SunoEditRoute(
            tool="Suno Song Editor / Move, Crop, Create Section, or Extend",
            action="Use move/crop/split for ordering problems, create a new section for missing contrast, and Extend only when the ending or post-chorus needs continuation.",
            official_basis="official-song-editor.md and official-extend.md",
            regression="section payoff improves while verse/chorus identity and tempo feel remain intact",
        )

    if "vocal identity" in layer:
        if action == "repair candidate":
            tool = "Suno Replace Section or Voice/Persona regeneration"
            action_text = "If the issue is localized, replace the affected vocal section; if the singer identity is global, regenerate with the Voice/Persona route as the only changed variable."
        else:
            tool = "Suno Voice/Persona or Add Vocals route"
            action_text = "For a new vocal pass, use a verified Voice/Persona source or Add Vocals on a valid instrumental, keeping lyrics and style stable."
        return SunoEditRoute(
            tool=tool,
            action=action_text,
            official_basis="official-song-editor.md, official-personas.md, and official-add-vocals.md",
            regression="vocal-only blind review hears one specific singer, not an anonymous AI voice",
        )

    if "groove" in layer:
        return SunoEditRoute(
            tool="Suno Reuse Prompt or Studio stems / DAW handoff",
            action="If groove is global, regenerate with one rhythm-section variable; if the take is otherwise locked, export/use stems and repair pocket in DAW.",
            official_basis="official-song-editor.md plus DAW handoff workflow",
            regression="body-feel score improves without flattening the chorus or vocal phrasing",
        )

    if "mix/post" in layer:
        return SunoEditRoute(
            tool="Suno Studio stems / DAW handoff",
            action="Preserve the selected take and move to stems, balance, translation listen, and post-production instead of changing prompt language.",
            official_basis="official-song-editor.md mentions stems; local DAW handoff workflow defines the repair path",
            regression="translation listen improves while hook, vocal identity, and groove stay preserved",
        )

    if "ai artifacts" in layer:
        localized = any(term in evidence for term in ["tail", "line", "word", "section", "timestamp"])
        if localized:
            action_text = "Use Replace Section around the artifact timestamp first; if the artifact survives, export stems and repair or re-record that layer."
        else:
            action_text = "Run artifact diagnosis; use Replace Section for a bounded timestamp, or stems/DAW if the artifact is global or separation-related."
        return SunoEditRoute(
            tool="Suno Song Editor / Replace Section or Studio stems",
            action=action_text,
            official_basis="official-song-editor.md, official-replace-section.md, and DAW repair workflow",
            regression="artifact risk decreases without damaging hook memory, vocal identity, or groove",
        )

    if "brief/prompt" in layer or "prompt" in layer:
        return SunoEditRoute(
            tool="Suno Reuse Prompt / controlled regeneration",
            action="Repair the prompt package and regenerate with exactly one changed variable; do not spend edits on a take that missed the brief.",
            official_basis="local prompt review checklist and official detailed style instructions",
            regression="alignment improves while the fixed brief, title phrase, and rights boundary stay unchanged",
        )

    if "song idea" in layer or "arrangement" in layer or "preference" in problem:
        strong_hook = (take.values.get("hook") or 0) >= 4.0
        if strong_hook:
            return SunoEditRoute(
                tool="Suno Cover or Reuse Prompt",
                action="Keep the melody/hook if it is the keeper; test a style-only Cover/Reuse Prompt route as a candidate, not a guaranteed fix.",
                official_basis="official-cover.md plus prompt iteration discipline",
                regression="listener preference improves while hook recall stays stable",
            )
        return SunoEditRoute(
            tool="Suno Reuse Prompt / controlled regeneration",
            action="Regenerate a new batch after strengthening the musical payoff; keep only one primary prompt or slider variable changed.",
            official_basis="local prompt review checklist and official creative sliders",
            regression="preference improves without losing alignment",
        )

    return SunoEditRoute(
        tool="Producer decision",
        action="Choose Replace Section, Extend, Reuse Prompt, or DAW repair only after the failing timestamp/layer is identified.",
        official_basis="official-song-editor.md plus local repair router",
        regression=issue.regression,
    )

KNOWN_ISSUE_ROUTES = [
    (
        re.compile(r"lyric|cliche|generic|translated|abstract|歌词|陈词|翻译腔|空泛", re.I),
        RepairIssue(
            "ledger flags lyric or narrative weakness",
            "lyric",
            2,
            "known issue text",
            "AI 音乐歌词叙事与反陈词滥调工作流",
            "03_writing/lyric-brief.md, image-bank.md, cliche-cut.md",
            "blind read and chorus recall improve",
        ),
    ),
    (
        re.compile(r"prosody|diction|stress|tone|mora|咬字|重音|声调|音节", re.I),
        RepairIssue(
            "ledger flags prosody or diction risk",
            "prosody",
            2,
            "known issue text",
            "四语种歌词 Prosody 与 AI 音乐咬字审查表",
            "03_writing/prosody-check.md",
            "language-specific stress or tone errors decrease",
        ),
    ),
    (
        re.compile(r"mix|master|muddy|plastic|loud|reverb|低频|混音|母带|塑料", re.I),
        RepairIssue(
            "ledger flags mix or master artifact",
            "mix/post",
            1,
            "known issue text",
            "AI 音乐编曲密度与混音后期修作工作流",
            "10_mix-master/post-review.md or mix-plan.md",
            "translation listen improves without hurting hook",
        ),
    ),
    (
        re.compile(r"stem|bleed|phase|separation|halo|分轨|相位|残留", re.I),
        RepairIssue(
            "ledger flags stem or separation artifact",
            "AI artifacts / stems",
            2,
            "known issue text",
            "AI 音乐 DAW 复刻与真人重录工作流",
            "08_stems-daw/stem-quality-triage.md",
            "stem-solo diagnosis confirms keep / guide / replace / discard",
        ),
    ),
    (
        re.compile(r"rights|reference|voice right|copyright|授权|权利|参考过近", re.I),
        RepairIssue(
            "ledger flags rights or reference risk",
            "rights",
            3,
            "known issue text",
            "AI 音乐权利发布与平台披露工作流",
            "11_release/source-rights-ledger.md and release-candidate-rights-gate.md",
            "rights status becomes publishable or project holds",
        ),
    ),
]


def score_to_severity(score: float, mild: float, medium: float, severe: float) -> int:
    if score < severe:
        return 3
    if score < medium:
        return 2
    if score < mild:
        return 1
    return 0


def artifact_risk_to_severity(risk: float | None) -> int:
    if risk is None:
        return 0
    if risk >= 3.0:
        return 3
    if risk > 2.0:
        return 2
    if risk > 1.2:
        return 1
    return 0


def parse_decision_file(project_root: Path) -> tuple[str, str, list[str]]:
    path = project_root / TAKE_DECISION
    if not path.exists():
        return "", "", [f"missing {TAKE_DECISION}; run tools/review_music_takes.py first"]
    text = path.read_text(encoding="utf-8")
    best_match = re.search(r"^Best take:\s*(.+)$", text, flags=re.M)
    action_match = re.search(r"^Action:\s*(.+)$", text, flags=re.M)
    best = best_match.group(1).strip() if best_match else ""
    action = action_match.group(1).strip() if action_match else ""
    errors: list[str] = []
    if not best:
        errors.append(f"{TAKE_DECISION} missing Best take")
    if not action:
        errors.append(f"{TAKE_DECISION} missing Action")
    return best, action, errors


def issue_for_field(take: TakeScore, field_name: str, score: float) -> RepairIssue | None:
    thresholds = {
        "alignment": (4.0, 3.5, 2.8),
        "preference": (4.0, 3.5, 2.8),
        "hook": (4.0, 3.8, 3.0),
        "vocal_identity": (4.0, 3.8, 3.0),
        "groove": (3.9, 3.6, 2.8),
        "form": (3.9, 3.6, 2.8),
    }
    severity = score_to_severity(score, *thresholds[field_name])
    if severity == 0:
        return None
    problem, layer, route, output, regression = FIELD_ROUTES[field_name]
    return RepairIssue(
        problem=problem,
        layer=layer,
        severity=severity,
        evidence=f"{field_name} score {score:.2f} on {take.take_id}",
        route=route,
        expected_output=output,
        regression=regression,
    )


def issues_from_take(take: TakeScore, action: str) -> list[RepairIssue]:
    issues: list[RepairIssue] = []
    for field_name in ["alignment", "preference", "hook", "vocal_identity", "groove", "form"]:
        score = take.values.get(field_name)
        if score is None:
            continue
        issue = issue_for_field(take, field_name, score)
        if issue:
            issues.append(issue)

    artifact_severity = artifact_risk_to_severity(take.artifact_risk)
    if artifact_severity:
        issues.append(
            RepairIssue(
                problem="AI artifact risk is audible",
                layer="AI artifacts",
                severity=artifact_severity,
                evidence=f"artifact risk {take.artifact_risk:.2f} on {take.take_id}",
                route="AI 音乐 AI味伪影诊断与修复路由工作流",
                expected_output="07_repair/artifact-severity-score.md and stem/vocal artifact sheets",
                regression="artifact risk decreases without damaging hook, vocal identity, or groove",
            )
        )

    known_issue = " ".join(
        take.ledger.get(key, "")
        for key in ["known_issue", "first_impression", "review_status", "decision"]
    )
    for pattern, template in KNOWN_ISSUE_ROUTES:
        if pattern.search(known_issue):
            issues.append(
                RepairIssue(
                    problem=template.problem,
                    layer=template.layer,
                    severity=template.severity,
                    evidence=known_issue.strip() or template.evidence,
                    route=template.route,
                    expected_output=template.expected_output,
                    regression=template.regression,
                )
            )

    if not issues:
        if action == "lock for post-production":
            issues.append(
                RepairIssue(
                    problem="take is strong enough for post-production gate",
                    layer="mix/post",
                    severity=1,
                    evidence=f"{take.take_id} passed core blind-review thresholds",
                    route="AI 音乐编曲密度与混音后期修作工作流",
                    expected_output="08_stems-daw/best-take-lock.md and 10_mix-master/post-review.md",
                    regression="post-production improves translation without reducing hook, vocal identity, or groove",
                )
            )
        else:
            issues.append(
                RepairIssue(
                    problem=f"take action is {action}",
                    layer="prompt experiment",
                    severity=2,
                    evidence=f"{take.take_id} did not produce a specific repair blocker",
                    route="AI 音乐 Prompt 实验矩阵与版本收敛工作流",
                    expected_output="05_generations/batch-generation-plan.md with one changed variable",
                    regression="next batch improves the weakest blind-review dimension",
                )
            )

    deduped: dict[tuple[str, str, str], RepairIssue] = {}
    for issue in issues:
        key = (issue.problem, issue.layer, issue.route)
        current = deduped.get(key)
        if current is None or issue.severity > current.severity:
            deduped[key] = issue
    return sorted(deduped.values(), key=lambda item: (-item.severity, item.layer, item.problem))


def save_decision(action: str) -> str:
    if action == "lock for post-production":
        return "yes / postproduction"
    if action == "repair candidate":
        return "yes / local repair"
    if action == "controlled regeneration":
        return "yes / regenerate with one variable"
    if action == "discard and repair brief":
        return "no / repair brief or regenerate"
    return "needs producer decision"


def render_issue_rows(issues: list[RepairIssue]) -> str:
    rows = ["| problem | layer | severity | evidence | route |", "|---|---|---:|---|---|"]
    for issue in issues:
        rows.append(f"| {issue.problem} | {issue.layer} | {issue.severity} | {issue.evidence} | {issue.route} |")
    return "\n".join(rows)


def render_suno_tool_rows(issues: list[RepairIssue], take: TakeScore, action: str) -> str:
    rows = [
        "| problem | official Suno edit tool | tool action | official/local basis | regression check |",
        "|---|---|---|---|---|",
    ]
    for issue in issues:
        tool_route = suno_edit_route_for_issue(issue, take, action)
        rows.append(
            f"| {issue.problem} | {tool_route.tool} | {tool_route.action} | {tool_route.official_basis} | {tool_route.regression} |"
        )
    return "\n".join(rows)


def render_artifact_score(project_root: Path, take: TakeScore, action: str, issues: list[RepairIssue]) -> str:
    top = issues[:3]
    top_lines = "\n".join(f"{index}. {issue.problem} -> {issue.route}" for index, issue in enumerate(top, start=1))
    return f"""# Artifact Severity Score

Generated by: tools/route_music_repairs.py
Project root: {project_root}
Selected take: {take.take_id}
Take action: {action}

## Score Table

{render_issue_rows(issues)}

## Top 3 Blockers

{top_lines}

## Can This Take Be Saved?

- {save_decision(action)}

## Official Suno Edit Tool Routes

{render_suno_tool_rows(top, take, action)}

## Notes

- Severity uses the 0-3 scale from AI 音乐 AI味伪影诊断与修复路由工作流.
- This file is a routing summary, not a substitute for listening notes.
"""


def render_repair_route(project_root: Path, take: TakeScore, action: str, issues: list[RepairIssue]) -> str:
    rows = ["| problem | layer | severity | repair route | official Suno edit tool | expected output | regression listen |", "|---|---|---:|---|---|---|---|"]
    for issue in issues:
        tool_route = suno_edit_route_for_issue(issue, take, action)
        rows.append(
            f"| {issue.problem} | {issue.layer} | {issue.severity} | {issue.route} | {tool_route.tool} | {issue.expected_output} | {issue.regression} |"
        )
    primary = issues[0]
    primary_tool = suno_edit_route_for_issue(primary, take, action)
    return f"""# Repair Route Map

Generated by: tools/route_music_repairs.py
Project root: {project_root}
Selected take: {take.take_id}
Take action: {action}

## Primary Repair

- Problem: {primary.problem}
- Layer: {primary.layer}
- Severity: {primary.severity}
- Route: {primary.route}
- Official Suno edit tool: {primary_tool.tool}
- Tool action: {primary_tool.action}
- Official/local basis: {primary_tool.official_basis}
- Expected output: {primary.expected_output}
- Regression listen: {primary.regression}
- Suno regression check: {primary_tool.regression}

## Route Table

{chr(10).join(rows)}

## Official Suno Edit Tool Routes

{render_suno_tool_rows(issues, take, action)}

## Rule

Repair only one primary blocker before the next blind review unless there is a rights red light.
"""


def render_repair_log(project_root: Path, take: TakeScore, action: str, issues: list[RepairIssue]) -> str:
    primary = issues[0]
    keep = []
    for field_name in ["alignment", "preference", "hook", "vocal_identity", "groove", "form"]:
        score = take.values.get(field_name)
        if score is not None and score >= 4.0:
            keep.append(f"{field_name} {score:.2f}")
    keep_text = ", ".join(keep) if keep else "no stable keeper yet"
    primary_tool = suno_edit_route_for_issue(primary, take, action)
    return f"""# Repair Log

Generated by: tools/route_music_repairs.py
Project root: {project_root}

Chosen take: {take.take_id}
Take action: {action}
Keep: {keep_text}
Reject / repair: {primary.problem}
One thing to repair: {primary.layer}
Repair tool: {primary.route}
Official Suno edit tool: {primary_tool.tool}
Tool action: {primary_tool.action}
Expected improvement: {primary.regression}
Suno regression check: {primary_tool.regression}
Result:
Next action: run the repair, then update 07_repair/regression-listen.md and 06_review/blind-review.md.

## Secondary Issues

{render_issue_rows(issues[1:] or issues)}
"""


def render_regression(project_root: Path, take: TakeScore, action: str, issues: list[RepairIssue]) -> str:
    primary = issues[0]
    primary_tool = suno_edit_route_for_issue(primary, take, action)
    return f"""# Regression Listen

Generated by: tools/route_music_repairs.py
Project root: {project_root}
Selected take: {take.take_id}

Original issue: {primary.problem}
Repair action: {primary.route}
Official Suno edit tool: {primary_tool.tool}
Tool action used:
Before timestamp:
After timestamp:
Did issue improve? 0-3:
New artifacts introduced:
Hook preserved:
Vocal identity preserved:
Groove preserved:
Rights status changed:
Decision:
- keep
- repair again
- route elsewhere
- abandon

## Preserve Checks

- Take action before repair: {action}
- Expected regression check: {primary.regression}
- Suno tool regression check: {primary_tool.regression}
"""


def write_if_allowed(path: Path, text: str, allow_overwrite: bool) -> None:
    if path.exists() and not allow_overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Song project root.")
    parser.add_argument("--write", action="store_true", help="Write repair routing files.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow overwriting existing repair routing files.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when take decision or scored review evidence is missing.")
    parser.add_argument("--artifact-score-output", default=ARTIFACT_SCORE, help="Relative output path for artifact severity score.")
    parser.add_argument("--repair-route-output", default=REPAIR_ROUTE, help="Relative output path for repair route map.")
    parser.add_argument("--repair-log-output", default=REPAIR_LOG, help="Relative output path for repair log.")
    parser.add_argument("--regression-output", default=REGRESSION_LISTEN, help="Relative output path for regression listen.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"error: project root not found: {project_root}", file=sys.stderr)
        return 2

    best_take, action, decision_errors = parse_decision_file(project_root)
    _, scores, review_errors = load_project(project_root)
    errors = decision_errors + review_errors
    if best_take and best_take not in scores:
        errors.append(f"best take {best_take} is not present in blind-review scores")

    if errors:
        for error in errors:
            print(f"repair routing evidence error: {error}", file=sys.stderr)
        return 1 if args.strict else 0

    take = scores[best_take]
    computed_action = decision_for_take(take)
    if action != computed_action:
        print(f"warning: decision action {action!r} differs from recomputed action {computed_action!r}", file=sys.stderr)
    issues = issues_from_take(take, action)

    outputs = {
        args.artifact_score_output: render_artifact_score(project_root, take, action, issues),
        args.repair_route_output: render_repair_route(project_root, take, action, issues),
        args.repair_log_output: render_repair_log(project_root, take, action, issues),
        args.regression_output: render_regression(project_root, take, action, issues),
    }

    if args.write:
        try:
            for rel, text in outputs.items():
                write_if_allowed(project_root / rel, text, args.allow_overwrite)
        except FileExistsError as exc:
            print(f"error: output exists, use --allow-overwrite: {exc}", file=sys.stderr)
            return 2
    else:
        print(outputs[args.repair_route_output])

    print(f"selected take: {take.take_id}")
    print(f"action: {action}")
    print(f"primary repair: {issues[0].problem} -> {issues[0].route}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
