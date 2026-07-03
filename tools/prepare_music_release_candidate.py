#!/usr/bin/env python3
"""Prepare an AI music release-candidate evidence gate.

This tool starts after mix/master QC, external listener feedback, rights review,
and any DAW/humanization work. It does not inspect audio waveforms itself and it
is not legal advice. It checks whether required project evidence is present,
filled, and free of obvious unresolved blockers before writing a release-
candidate package and rights gate.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from audit_music_audio_seed_retention import (
    AUDIO_SEED_AUDIT_MARKER,
    AUDIO_SEED_AUDIT_REQUIRED_TERMS,
    OUTPUT as AUDIO_SEED_AUDIT,
    audio_seed_required,
)
from audit_music_release_listener_evidence import (
    OUTPUT as RELEASE_LISTENER_AUDIT,
    RELEASE_LISTENER_AUDIT_MARKER,
    RELEASE_LISTENER_AUDIT_REQUIRED_TERMS,
)
from audit_music_prompt_iteration_discipline import (
    OUTPUT as PROMPT_ITERATION_DISCIPLINE_AUDIT,
    PROMPT_ITERATION_DISCIPLINE_MARKER,
    PROMPT_ITERATION_DISCIPLINE_REQUIRED_TERMS,
)
from audit_music_post_production_mix_lock import (
    OUTPUT as POST_PRODUCTION_MIX_LOCK_AUDIT,
    POST_PRODUCTION_MIX_LOCK_MARKER,
    POST_PRODUCTION_MIX_LOCK_REQUIRED_TERMS,
)


AUDIO_EXTENSIONS = {".wav", ".aiff", ".aif", ".flac", ".mp3", ".m4a"}

OUTPUTS = {
    "audit": "11_release/release-candidate-evidence-audit.md",
    "rights_gate": "11_release/release-candidate-rights-gate.md",
    "package": "11_release/release-candidate-package.md",
    "manifest": "11_release/release_candidate/metadata/release-candidate-manifest.md",
}


@dataclass(frozen=True)
class EvidenceSpec:
    label: str
    paths: tuple[str, ...]
    required: bool = True


@dataclass
class EvidenceResult:
    spec: EvidenceSpec
    path: str = ""
    exists: bool = False
    has_approval: bool = False
    empty_fields: list[str] = field(default_factory=list)
    blocking_lines: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.exists and self.has_approval and not self.empty_fields and not self.blocking_lines

    @property
    def status(self) -> str:
        if not self.exists:
            return "missing"
        if self.ok:
            return "pass"
        return "hold"


REQUIRED_EVIDENCE = [
    EvidenceSpec("release intent", ("11_release/release-intent.md",)),
    EvidenceSpec("prompt package", ("04_prompt/prompt-package-v001.md",)),
    EvidenceSpec("prompt preflight review", ("04_prompt/prompt-preflight-review.md",)),
    EvidenceSpec("prompt iteration discipline audit", (PROMPT_ITERATION_DISCIPLINE_AUDIT,)),
    EvidenceSpec("generation evidence audit", ("05_generations/generation-evidence-audit.md",)),
    EvidenceSpec("reference rights", ("02_references/reference-rights.md",)),
    EvidenceSpec("voice rights", ("09_vocal/voice-rights.md",)),
    EvidenceSpec("final humanized master review", ("08_stems-daw/final-humanized-master-review.md",)),
    EvidenceSpec("post-production mix lock audit", (POST_PRODUCTION_MIX_LOCK_AUDIT,)),
    EvidenceSpec("release audio technical inspection", ("10_mix-master/release-audio-technical-inspection.md",)),
    EvidenceSpec("release audio QC", ("10_mix-master/release-audio-qc-report.md",)),
    EvidenceSpec("release listener evidence audit", (RELEASE_LISTENER_AUDIT,)),
    EvidenceSpec("external listener panel", ("06_review/external-listener-panel.md",)),
    EvidenceSpec("first 20 second test", ("06_review/first-20-second-test.md",)),
    EvidenceSpec("hook memory test", ("06_review/hook-memory-test.md",)),
    EvidenceSpec("AI flavor red flag survey", ("06_review/ai-flavor-red-flag-survey.md",)),
    EvidenceSpec("source rights ledger", ("11_release/source-rights-ledger.md",)),
    EvidenceSpec("subscription and generation context", ("11_release/subscription-and-generation-context.md",)),
    EvidenceSpec("human contribution ledger", ("11_release/human-contribution-ledger.md",)),
    EvidenceSpec("copyrightability notes", ("11_release/copyrightability-notes.md",)),
    EvidenceSpec("similarity and impersonation review", ("11_release/similarity-and-impersonation-review.md",)),
    EvidenceSpec("platform distribution matrix", ("11_release/platform-distribution-matrix.md", "11_release/platform-policy-matrix.md")),
    EvidenceSpec("AI use disclosure", ("11_release/ai-use-disclosure.md",)),
    EvidenceSpec("anti-spam release policy", ("11_release/anti-spam-release-policy.md",)),
    EvidenceSpec("distributor preflight", ("11_release/distributor-preflight.md",)),
]

OPTIONAL_EVIDENCE = [
    EvidenceSpec("DAW session pack", ("08_stems-daw/session-pack.md",), False),
    EvidenceSpec("human contribution rights link", ("08_stems-daw/human-contribution-and-rights-link.md",), False),
    EvidenceSpec("translation listen matrix", ("10_mix-master/translation-listen-matrix.md",), False),
    EvidenceSpec("codec preview", ("10_mix-master/codec-preview.md",), False),
    EvidenceSpec("loudness true peak report", ("10_mix-master/loudness-true-peak-report.md",), False),
]

APPROVAL_RE = re.compile(
    r"\b(pass|passed|approved|clear|cleared|resolved|complete|completed|ready|green|ok|release[- ]candidate)\b"
    r"|通过|已通过|批准|清楚|已解决|完整|完成|可发布|可发行",
    re.I,
)

BLOCKING_RE = re.compile(
    r"\b(todo|tbd|pending|unknown|unresolved|unclear|missing|fail(?:ed)?|hold|blocked|not approved|red flag)\b"
    r"|待定|未知|未解决|不清楚|缺失|失败|不通过|暂停|阻塞|红灯|红旗",
    re.I,
)

CLEARING_RE = re.compile(
    r"\b(no|none|0|zero|resolved|clear|cleared|pass|passed|approved|not applicable|n/a|low)\b"
    r"|无|否|已解决|通过|清楚|可发布|低风险",
    re.I,
)

EMPTY_FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?[^:#|`][^:]{1,78}:\s*$")
PROMPT_COMPILER_MARKER = "Generated by: tools/compile_music_prompt_package.py"
PROMPT_PACKAGE_REQUIRED_TERMS = [
    "## metadata",
    "## style of music",
    "## lyrics",
    "## prompt rationale",
    "## preflight summary",
    "model:",
    "weirdness:",
    "style influence:",
    "methodology transfer:",
    "prompt specificity:",
    "lyric narrative:",
    "reference audit:",
    "prosody audit:",
    "topline audit:",
    "harmony/bass audit:",
    "groove audit:",
    "structure audit:",
    "vocal audit:",
    "human anchor lane:",
    "voice identity source:",
    "persona source:",
    "custom model source:",
    "custom model corpus:",
    "my taste state:",
    "prompt boost state:",
    "exclude:",
    "genre:",
    "vocal:",
    "instrumentation:",
    "production:",
    "mood:",
]
PROMPT_PREFLIGHT_REQUIRED_TERMS = [
    "field completeness:",
    "lyrics context:",
    "methodology transfer:",
    "prompt specificity:",
    "lyric narrative:",
    "reference audit:",
    "prosody audit:",
    "topline audit:",
    "harmony/bass audit:",
    "groove audit:",
    "structure audit:",
    "vocal audit:",
    "exclude rationale:",
    "slider intent:",
    "model/version:",
    "human anchor lane:",
    "identity routing:",
    "my taste / boost:",
    "identity / rights:",
    "conflict check:",
    "blockers:",
    "## issues",
]
AUDIO_INSPECTION_MARKER = "Generated by: tools/inspect_music_release_audio.py"
RELEASE_AUDIO_QC_MARKER = "Generated by: tools/prepare_music_release_audio_qc.py"
AUDIO_INSPECTION_METRICS = [
    "duration",
    "sample rate",
    "bit depth",
    "channels",
    "peak",
    "rms",
    "dc offset",
    "clipped ratio",
]
RELEASE_AUDIO_QC_REQUIRED_TERMS = [
    "## required evidence",
    "## measurements",
    "integrated lufs:",
    "lra:",
    "true peak:",
    "clipped samples:",
    "sample rate:",
    "bit depth:",
    "## listening",
    "loudness-matched reference a/b:",
    "codec preview:",
    "translation matrix:",
    "mono/phase:",
    "low end:",
    "intro/outro:",
    "## ai artifact check",
    "vocal tail:",
    "cymbals:",
    "backing vocal smear:",
    "stem bleed:",
    "over-limiting:",
    "## blocking items",
]
GENERATION_AUDIT_MARKER = "Generated by: tools/audit_music_generation_evidence.py"
GENERATION_AUDIT_REQUIRED_TERMS = [
    "Decision: pass",
    "## Generation Evidence",
    "Take provenance tags:",
    "Batch tags:",
    "Provider metadata tags:",
    "Blind review handoff:",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def first_existing(project_root: Path, rel_paths: tuple[str, ...]) -> tuple[str, str]:
    for rel in rel_paths:
        path = project_root / rel
        if path.exists():
            return rel, read_text(path)
    return rel_paths[0], ""


def line_is_blocking(line: str) -> bool:
    text = line.strip()
    if not text:
        return False
    if text.startswith("#"):
        return False
    if text.startswith("|"):
        return False
    lower = text.lower()
    if "not legal advice" in lower:
        return False
    if not BLOCKING_RE.search(text):
        return False
    return not CLEARING_RE.search(text)


def empty_evidence_fields(text: str) -> list[str]:
    fields: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|") or stripped.startswith("```"):
            continue
        if EMPTY_FIELD_RE.match(stripped):
            fields.append(stripped)
    return fields[:8]


def field_value(text: str, labels: list[str]) -> str:
    wanted = {label.lower() for label in labels}
    for line in text.splitlines():
        stripped = re.sub(r"^[-*]\s+", "", line.strip())
        match = re.match(r"^([^:]{1,80}):\s*(.*)$", stripped)
        if not match:
            continue
        label = match.group(1).strip().lower()
        value = match.group(2).strip()
        if label in wanted and value:
            return value
    return ""


def low_risk_value(value: str) -> bool:
    return bool(re.search(r"^(no|none|0|zero|low|pass|passed|clear|cleared|ok|n/a|not applicable)\b", value.strip(), re.I))


def positive_value(value: str) -> bool:
    return bool(re.search(r"\b(pass|passed|yes|clear|cleared|ok|approved|strong|remembered|recalled|low)\b|通过|记住|低风险", value, re.I))


def prompt_package_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    decision = field_value(text, ["Decision"])
    if PROMPT_COMPILER_MARKER not in text:
        blockers.append("prompt package must be generated by tools/compile_music_prompt_package.py")
    if not decision or not re.search(r"^compile approved\b", decision.strip(), re.I):
        blockers.append("prompt package needs Decision: compile approved")
    lowered = text.lower()
    missing_terms = [term for term in PROMPT_PACKAGE_REQUIRED_TERMS if term not in lowered]
    if missing_terms:
        blockers.append("prompt package missing compiler sections/fields: " + ", ".join(missing_terms[:4]))
    return blockers


def prompt_preflight_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    decision = field_value(text, ["Decision"])
    if PROMPT_COMPILER_MARKER not in text:
        blockers.append("prompt preflight review must be generated by tools/compile_music_prompt_package.py")
    if not decision or not re.search(r"^compile approved\b", decision.strip(), re.I):
        blockers.append("prompt preflight review needs Decision: compile approved")
    lowered = text.lower()
    missing_terms = [term for term in PROMPT_PREFLIGHT_REQUIRED_TERMS if term not in lowered]
    if missing_terms:
        blockers.append("prompt preflight review missing compiler fields: " + ", ".join(missing_terms[:4]))
    for label in [
        "Field completeness",
        "Lyrics context",
        "Methodology transfer",
        "Prompt specificity",
        "Lyric narrative",
        "Reference audit",
        "Prosody audit",
        "Topline audit",
        "Harmony/Bass audit",
        "Groove audit",
        "Structure audit",
        "Vocal audit",
        "Exclude rationale",
        "Slider intent",
        "Model/version",
        "Human anchor lane",
        "Identity routing",
        "My Taste / boost",
        "Identity / rights",
        "Conflict check",
    ]:
        value = field_value(text, [label])
        if not value or not re.search(r"^pass\b", value.strip(), re.I):
            blockers.append(f"prompt preflight review requires {label}: pass")
            break
    blockers_value = field_value(text, ["Blockers"])
    if blockers_value and not re.search(r"^0\b", blockers_value.strip()):
        blockers.append("prompt preflight review must have Blockers: 0")
    return blockers


def audio_technical_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    decision = field_value(text, ["Decision"])
    if AUDIO_INSPECTION_MARKER not in text:
        blockers.append("release audio technical inspection must be generated by tools/inspect_music_release_audio.py")
    if not decision or not re.search(r"^(pass|approved|approve)\b", decision.strip(), re.I):
        blockers.append("release audio technical inspection needs Decision: pass")

    lowered = text.lower()
    if "## results" not in lowered:
        blockers.append("release audio technical inspection must include a Results section")
    missing_metrics = [metric for metric in AUDIO_INSPECTION_METRICS if metric not in lowered]
    if missing_metrics:
        blockers.append("release audio technical inspection missing metrics: " + ", ".join(missing_metrics[:4]))

    table_rows = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    data_rows = [
        row
        for row in table_rows
        if row.count("|") >= 10 and not re.search(r"^\|\s*-", row) and "sample rate" not in row.lower()
    ]
    if not any(re.search(r"\|\s*pass\s*\|\s*$", row, re.I) for row in data_rows):
        blockers.append("release audio technical inspection needs at least one passing inspected audio row")
    return blockers


def release_audio_qc_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    decision = field_value(text, ["Decision"])
    if RELEASE_AUDIO_QC_MARKER not in text:
        blockers.append("release audio QC report must be generated by tools/prepare_music_release_audio_qc.py")
    if not decision or not re.search(r"^(pass|approved|approve)\b", decision.strip(), re.I):
        blockers.append("release audio QC report needs Decision: pass")
    lowered = text.lower()
    missing_terms = [term for term in RELEASE_AUDIO_QC_REQUIRED_TERMS if term not in lowered]
    if missing_terms:
        blockers.append("release audio QC report missing fields: " + ", ".join(missing_terms[:4]))
    blockers_value = field_value(text, ["Blocking Items", "Blockers"])
    if blockers_value and not re.search(r"^(none|no|0|zero|n/a|not applicable)\b", blockers_value.strip(), re.I):
        blockers.append("release audio QC report has blocking items")
    return blockers


def generation_evidence_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    if GENERATION_AUDIT_MARKER not in text:
        blockers.append("generation evidence audit must be generated by tools/audit_music_generation_evidence.py")
    if "Decision: pass" not in text:
        blockers.append("generation evidence audit needs Decision: pass")
    missing_terms = [term for term in GENERATION_AUDIT_REQUIRED_TERMS if term not in text]
    if missing_terms:
        blockers.append("generation evidence audit missing fields: " + ", ".join(missing_terms[:4]))
    return blockers


def prompt_iteration_discipline_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    if PROMPT_ITERATION_DISCIPLINE_MARKER not in text:
        blockers.append("prompt iteration discipline audit must be generated by tools/audit_music_prompt_iteration_discipline.py")
    if "Decision: pass" not in text:
        blockers.append("prompt iteration discipline audit needs Decision: pass")
    missing_terms = [term for term in PROMPT_ITERATION_DISCIPLINE_REQUIRED_TERMS if term not in text]
    if missing_terms:
        blockers.append("prompt iteration discipline audit missing fields: " + ", ".join(missing_terms[:4]))
    return blockers


def audio_seed_retention_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    if AUDIO_SEED_AUDIT_MARKER not in text:
        blockers.append("audio seed retention audit must be generated by tools/audit_music_audio_seed_retention.py")
    if "Decision: pass" not in text:
        blockers.append("audio seed retention audit needs Decision: pass")
    missing_terms = [term for term in AUDIO_SEED_AUDIT_REQUIRED_TERMS if term not in text]
    if missing_terms:
        blockers.append("audio seed retention audit missing fields: " + ", ".join(missing_terms[:4]))
    return blockers


def release_listener_evidence_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    if RELEASE_LISTENER_AUDIT_MARKER not in text:
        blockers.append("release listener evidence audit must be generated by tools/audit_music_release_listener_evidence.py")
    if "Decision: pass" not in text:
        blockers.append("release listener evidence audit needs Decision: pass")
    missing_terms = [term for term in RELEASE_LISTENER_AUDIT_REQUIRED_TERMS if term not in text]
    if missing_terms:
        blockers.append("release listener evidence audit missing fields: " + ", ".join(missing_terms[:4]))
    return blockers


def post_production_mix_lock_blockers(text: str) -> list[str]:
    blockers: list[str] = []
    if POST_PRODUCTION_MIX_LOCK_MARKER not in text:
        blockers.append("post-production mix lock audit must be generated by tools/audit_music_post_production_mix_lock.py")
    if "Decision: pass" not in text:
        blockers.append("post-production mix lock audit needs Decision: pass")
    missing_terms = [term for term in POST_PRODUCTION_MIX_LOCK_REQUIRED_TERMS if term not in text]
    if missing_terms:
        blockers.append("post-production mix lock audit missing fields: " + ", ".join(missing_terms[:4]))
    return blockers


def external_listener_blockers(label: str, text: str) -> list[str]:
    blockers: list[str] = []
    if label == "external listener panel":
        ai_flags = field_value(text, ["AI flavor red flags", "AI-flavor red flags", "AI flavor concern", "Red flags"])
        if not ai_flags or not low_risk_value(ai_flags):
            blockers.append("external listener panel must show no/low AI-flavor red flags")
        release_verdict = field_value(text, ["Release listener verdict", "Listener release verdict", "Panel decision", "Decision"])
        if not release_verdict or not positive_value(release_verdict):
            blockers.append("external listener panel needs a positive release/listener verdict")
    elif label == "first 20 second test":
        skip_risk = field_value(text, ["Skip risk", "First 20 second skip risk", "Drop-off risk"])
        if not skip_risk or not low_risk_value(skip_risk):
            blockers.append("first 20 second test must show low/no skip risk")
        pull = field_value(text, ["First 20 second decision", "First 20-second decision", "Decision", "Pull"])
        if not pull or not positive_value(pull):
            blockers.append("first 20 second test needs a positive pull/listen decision")
    elif label == "hook memory test":
        hook_recall = field_value(text, ["Hook recalled", "Hook recall", "Title hook recalled", "Memory result"])
        if not hook_recall or not positive_value(hook_recall):
            blockers.append("hook memory test must prove listeners can recall the title hook")
    elif label == "AI flavor red flag survey":
        ai_flags = field_value(text, ["AI flavor red flags", "AI-flavor red flags", "Red flags", "AI flavor concern"])
        if not ai_flags or not low_risk_value(ai_flags):
            blockers.append("AI flavor red flag survey must show no/low AI-flavor red flags")
        verdict = field_value(text, ["AI flavor release verdict", "Release verdict", "Decision"])
        if not verdict or not positive_value(verdict):
            blockers.append("AI flavor red flag survey needs a pass/clear release verdict")
    return blockers


def evaluate_spec(project_root: Path, spec: EvidenceSpec) -> EvidenceResult:
    rel, text = first_existing(project_root, spec.paths)
    result = EvidenceResult(spec=spec, path=rel, exists=bool(text))
    if not text:
        return result
    result.has_approval = bool(APPROVAL_RE.search(text))
    result.empty_fields = empty_evidence_fields(text)
    result.blocking_lines = [line.strip() for line in text.splitlines() if line_is_blocking(line)][:8]
    if spec.label == "prompt package":
        result.blocking_lines.extend(prompt_package_blockers(text))
    elif spec.label == "prompt preflight review":
        result.blocking_lines.extend(prompt_preflight_blockers(text))
    elif spec.label == "generation evidence audit":
        result.blocking_lines.extend(generation_evidence_blockers(text))
    elif spec.label == "prompt iteration discipline audit":
        result.blocking_lines.extend(prompt_iteration_discipline_blockers(text))
    elif spec.label == "audio seed retention audit":
        result.blocking_lines.extend(audio_seed_retention_blockers(text))
    elif spec.label == "release listener evidence audit":
        result.blocking_lines.extend(release_listener_evidence_blockers(text))
    elif spec.label == "post-production mix lock audit":
        result.blocking_lines.extend(post_production_mix_lock_blockers(text))
    if spec.label == "release audio technical inspection":
        result.blocking_lines.extend(audio_technical_blockers(text))
    elif spec.label == "release audio QC":
        result.blocking_lines.extend(release_audio_qc_blockers(text))
    result.blocking_lines.extend(external_listener_blockers(spec.label, text))
    result.blocking_lines = result.blocking_lines[:8]
    return result


def audio_files(project_root: Path) -> list[str]:
    audio_dir = project_root / "11_release" / "release_candidate" / "audio"
    if not audio_dir.exists():
        return []
    files: list[str] = []
    for path in sorted(audio_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(path.relative_to(project_root).as_posix())
    return files


def value_from_files(project_root: Path, rel_paths: list[str], labels: list[str]) -> str:
    wanted = {label.lower() for label in labels}
    for rel in rel_paths:
        text = read_text(project_root / rel)
        for line in text.splitlines():
            stripped = re.sub(r"^[-*]\s+", "", line.strip())
            match = re.match(r"^([^:]{1,80}):\s*(.+)$", stripped)
            if not match:
                continue
            label = match.group(1).strip().lower()
            value = match.group(2).strip().strip('"')
            if label in wanted and value and not BLOCKING_RE.search(value):
                return value
    return ""


def project_context(project_root: Path) -> dict[str, str]:
    return {
        "project": value_from_files(project_root, ["README.md", "01_brief/project-intake.md"], ["project / artist", "project", "artist / catalog"]),
        "song": value_from_files(project_root, ["README.md", "01_brief/song-brief.md"], ["song", "song title", "title"]) or project_root.name,
        "language": value_from_files(project_root, ["README.md", "01_brief/song-brief.md"], ["language"]),
        "lane": value_from_files(project_root, ["README.md", "01_brief/song-brief.md"], ["lane", "genre lane"]),
    }


def evaluate_project(project_root: Path) -> tuple[list[EvidenceResult], list[EvidenceResult], list[str], list[str], list[str]]:
    required_specs = list(REQUIRED_EVIDENCE)
    if audio_seed_required(project_root):
        required_specs.append(EvidenceSpec("audio seed retention audit", (AUDIO_SEED_AUDIT,)))
    required = [evaluate_spec(project_root, spec) for spec in required_specs]
    optional = [evaluate_spec(project_root, spec) for spec in OPTIONAL_EVIDENCE]
    files = audio_files(project_root)

    errors: list[str] = []
    warnings: list[str] = []
    for item in required:
        if not item.exists:
            errors.append(f"missing required evidence: {item.spec.label} ({' or '.join(item.spec.paths)})")
        elif not item.has_approval:
            errors.append(f"{item.path} has no approval marker")
        if item.empty_fields:
            errors.append(f"{item.path} has unresolved empty fields: {', '.join(item.empty_fields[:3])}")
        if item.blocking_lines:
            errors.append(f"{item.path} has blocking evidence: {item.blocking_lines[0]}")

    if not files:
        errors.append("missing release candidate audio file in 11_release/release_candidate/audio/")

    for item in optional:
        if item.exists and not item.ok:
            warnings.append(f"optional evidence should be reviewed: {item.path} ({item.status})")

    return required, optional, files, errors, warnings


def render_result_rows(results: list[EvidenceResult]) -> str:
    rows = ["| evidence | file | status | approval | blockers | empty fields |", "|---|---|---|---|---|---|"]
    for item in results:
        blockers = "; ".join(item.blocking_lines[:2]) or ""
        empty = "; ".join(item.empty_fields[:2]) or ""
        rows.append(
            f"| {item.spec.label} | {item.path or 'missing'} | {item.status} | "
            f"{'yes' if item.has_approval else 'no'} | {blockers} | {empty} |"
        )
    return "\n".join(rows)


def render_audit(project_root: Path, required: list[EvidenceResult], optional: list[EvidenceResult], files: list[str], errors: list[str], warnings: list[str]) -> str:
    decision = "approve release-candidate" if not errors else "hold"
    return f"""# Release Candidate Evidence Audit

Generated by: tools/prepare_music_release_candidate.py
Project root: {project_root}
Decision: {decision}

This is a production evidence gate, not legal advice. It checks whether the
project has enough documented audio QC, listener feedback, rights, human
contribution, platform disclosure, and release-package evidence to be reviewed
as a release candidate.

## Required Evidence

{render_result_rows(required)}

## Optional Supporting Evidence

{render_result_rows(optional)}

## Release Candidate Audio

{chr(10).join(f"- {path}" for path in files) if files else "- missing"}

## Blocking Items

{chr(10).join(f"- {error}" for error in errors) if errors else "- none"}

## Warnings

{chr(10).join(f"- {warning}" for warning in warnings) if warnings else "- none"}
"""


def render_rights_gate(project_root: Path, required: list[EvidenceResult], files: list[str], errors: list[str], warnings: list[str]) -> str:
    ctx = project_context(project_root)
    decision = "approve release-candidate" if not errors else "hold"
    return f"""# Release Candidate Rights Gate

Generated by: tools/prepare_music_release_candidate.py
Project root: {project_root}

Project: {ctx['project']}
Song: {ctx['song']}
Language: {ctx['language']}
Lane: {ctx['lane']}
Decision: {decision}

This gate is not legal advice. For commercial releases, sync, client work,
copyright registration, samples, cover songs, or licensed voices, confirm with
qualified legal/distribution review.

## Release Candidate Audio

{chr(10).join(f"- {path}" for path in files) if files else "- missing"}

## Required Gate

{render_result_rows(required)}

## Do Not Publish If

- any source owner, license, reference, sample, voice, or uploaded audio status is unknown.
- a used human audio seed lacks `06_review/audio-seed-retention-audit.md` with `Decision: pass`.
- `prompt-package-v001.md` or `prompt-preflight-review.md` is missing, stale, or not approved.
- `prompt-iteration-discipline-audit.md` is missing, hand-written, hold, or cannot prove the generation batch was attributable.
- `human-contribution-ledger.md` cannot explain human authorship and production choices.
- `ai-use-disclosure.md` does not map AI roles to distributor/platform disclosure.
- external listeners flag obvious AI flavor, weak first-20-second pull, or failed hook memory.
- `post-production-mix-lock-audit.md` is missing, hold, hand-written, or lacks arrangement/vocal/low-end/space/artifact lock evidence.
- `release-audio-technical-inspection.md` is missing, hold, hand-written, or lacks tool-generated audio metrics.
- `release-audio-qc-report.md` has audio QC red flags.
- platform/distributor policy review is missing, stale, or blocked.
- release-candidate audio file is missing from `11_release/release_candidate/audio/`.

## Blocking Items

{chr(10).join(f"- {error}" for error in errors) if errors else "- none"}

## Warnings

{chr(10).join(f"- {warning}" for warning in warnings) if warnings else "- none"}

## Next Action

{"Package can proceed to final human/distributor review." if not errors else "Resolve blocking items, then rerun this tool with --strict."}
"""


def render_package(project_root: Path, required: list[EvidenceResult], optional: list[EvidenceResult], files: list[str], errors: list[str]) -> str:
    ctx = project_context(project_root)
    decision = "approve release-candidate" if not errors else "hold"
    evidence_files = [item.path for item in required if item.exists]
    supporting_files = [item.path for item in optional if item.exists]
    return f"""# Release Candidate Package

Generated by: tools/prepare_music_release_candidate.py
Project root: {project_root}
Decision: {decision}

Project: {ctx['project']}
Song: {ctx['song']}
Language: {ctx['language']}
Lane: {ctx['lane']}

## Audio Files

{chr(10).join(f"- {path}" for path in files) if files else "- missing"}

## Required Evidence Files

{chr(10).join(f"- {path}" for path in evidence_files) if evidence_files else "- missing"}

## Supporting Evidence Files

{chr(10).join(f"- {path}" for path in supporting_files) if supporting_files else "- none"}

## Review Statement

This package says the project is ready for release-candidate review only when
the gate decision is `approve release-candidate`. It does not claim legal
clearance, platform acceptance, copyright registration, or audio quality by
itself.

## Final Human Review

- Producer approval:
- Rights/distribution approval:
- Audio QC approval:
- Metadata/artwork approval:
- Catalog memory writeback needed:
"""


def render_manifest(project_root: Path, required: list[EvidenceResult], optional: list[EvidenceResult], files: list[str], errors: list[str]) -> str:
    decision = "approve release-candidate" if not errors else "hold"
    paths = files + [item.path for item in required + optional if item.exists]
    return f"""# Release Candidate Manifest

Generated by: tools/prepare_music_release_candidate.py
Project root: {project_root}
Decision: {decision}

## Files

{chr(10).join(f"- {path}" for path in paths) if paths else "- missing"}

## Required External Review

- final human listening review
- rights/distribution review
- platform disclosure review
- metadata/artwork review
"""


def output_contents(project_root: Path, required: list[EvidenceResult], optional: list[EvidenceResult], files: list[str], errors: list[str], warnings: list[str]) -> dict[str, str]:
    return {
        OUTPUTS["audit"]: render_audit(project_root, required, optional, files, errors, warnings),
        OUTPUTS["rights_gate"]: render_rights_gate(project_root, required, files, errors, warnings),
        OUTPUTS["package"]: render_package(project_root, required, optional, files, errors),
        OUTPUTS["manifest"]: render_manifest(project_root, required, optional, files, errors),
    }


def write_outputs(project_root: Path, contents: dict[str, str], allow_overwrite: bool) -> list[Path]:
    targets = [project_root / rel for rel in contents]
    existing = [path for path in targets if path.exists()]
    if existing and not allow_overwrite:
        raise FileExistsError("refusing to overwrite existing files: " + ", ".join(path.relative_to(project_root).as_posix() for path in existing))
    written: list[Path] = []
    for rel, text in contents.items():
        path = project_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, help="Song project root.")
    parser.add_argument("--write", action="store_true", help="Write release candidate gate files.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Allow overwriting release candidate gate files.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when evidence is missing or blocked.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        print(f"error: project root does not exist: {project_root}", file=sys.stderr)
        return 2

    required, optional, files, errors, warnings = evaluate_project(project_root)
    if errors and args.strict:
        print("release candidate gate blocked:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    contents = output_contents(project_root, required, optional, files, errors, warnings)
    if args.write:
        try:
            written = write_outputs(project_root, contents, args.allow_overwrite)
        except FileExistsError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        for path in written:
            print(f"wrote {path.relative_to(project_root).as_posix()}")
    else:
        print("release candidate gate preview")
        print(f"decision: {'approve release-candidate' if not errors else 'hold'}")
        print(f"required evidence: {sum(1 for item in required if item.ok)}/{len(required)} pass")
        print(f"audio files: {len(files)}")
    if warnings:
        print("warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
