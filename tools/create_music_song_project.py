#!/usr/bin/env python3
"""Create an AI music single-song project folder scaffold.

The scaffold mirrors the Obsidian note:
"AI 音乐单曲项目文件夹与证据包模板".
It is intentionally local and non-destructive: existing files are not
overwritten.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DIRS = [
    "00_admin",
    "01_brief",
    "02_references",
    "02_references/audio",
    "03_writing",
    "04_prompt",
    "05_generations",
    "05_generations/audio",
    "05_generations/metadata",
    "06_review",
    "07_repair",
    "08_stems-daw",
    "09_vocal",
    "10_mix-master",
    "10_mix-master/masters",
    "11_release",
    "11_release/release_candidate",
    "11_release/release_candidate/audio",
    "11_release/release_candidate/artwork",
    "11_release/release_candidate/metadata",
    "12_catalog-memory",
]


@dataclass(frozen=True)
class FileSpec:
    path: str
    title: str
    role: str
    mutable: bool
    gate: str


FILE_SPECS = [
    FileSpec("README.md", "Song Project README", "Human-readable project summary", True, "admin"),
    FileSpec("00_admin/generation-route-plan.md", "Suno Generation Route Plan", "Product-facing route decision for ordinary generation, reference upload, or safe fallback", True, "generation-route"),
    FileSpec("00_admin/effect-first-suno-run.md", "Effect-First Suno Run", "User-facing route card, generation confirmation card, state model, and next action", True, "effect-first"),
    FileSpec("00_admin/song-production-control-board.md", "Song Production Control Board", "Current stage and next action", True, "single-production-gate"),
    FileSpec("00_admin/project-status-audit.md", "Project Status Audit", "Automated status audit and gate evidence", True, "single-production-gate"),
    FileSpec("00_admin/next-action.md", "Next Action", "Current next command and blocker", True, "single-production-gate"),
    FileSpec("00_admin/decision-log.md", "Decision Log", "Chronological decisions and reasons", True, "admin"),
    FileSpec("00_admin/version-ledger.md", "Version Ledger", "Version changes and non-overwrite record", True, "admin"),
    FileSpec("00_admin/file-manifest.md", "File Manifest", "Project file index and evidence map", True, "admin"),
    FileSpec("00_admin/immutable_inputs.md", "Immutable Inputs", "Raw evidence that must not be overwritten", False, "admin"),
    FileSpec("00_admin/mutable_working.md", "Mutable Working Files", "Drafts allowed to evolve with version notes", True, "admin"),
    FileSpec("01_brief/project-intake.md", "Project Intake", "Project purpose and production scope", True, "project-intake"),
    FileSpec("01_brief/song-brief.md", "Song Brief", "Song premise, language, lane, narrator, title phrase", True, "song-brief"),
    FileSpec("01_brief/success-definition.md", "Success Definition", "What success sounds like", True, "project-intake"),
    FileSpec("01_brief/audience-and-use-case.md", "Audience And Use Case", "Listener and distribution context", True, "project-intake"),
    FileSpec("01_brief/catalog-fit.md", "Catalog Fit", "Fit to artist or catalog identity", True, "catalog-memory"),
    FileSpec("01_brief/catalog-fit-audit.md", "Catalog Fit Audit", "Tool-generated artist/catalog identity fit gate", True, "catalog-fit"),
    FileSpec("01_brief/kill-criteria.md", "Kill Criteria", "Stop, hold, or abandon conditions", True, "project-intake"),
    FileSpec("02_references/rights-and-source-precheck.md", "Rights And Source Precheck", "Early source and rights triage", True, "rights-precheck"),
    FileSpec("02_references/source-rights-ledger.md", "Source Rights Ledger", "All source materials and permissions", True, "release-rights"),
    FileSpec("02_references/human-seed-intent.md", "Human Seed Intent", "Why a human audio seed is needed and what it must preserve", True, "audio-seed-retention"),
    FileSpec("02_references/audio-rights-ledger.md", "Audio Rights Ledger", "Human audio seed source and upload/release permission", True, "audio-seed-retention"),
    FileSpec("02_references/seed-type-classification.md", "Seed Type Classification", "Human audio seed type and audible features", True, "audio-seed-retention"),
    FileSpec("02_references/capture-and-cleanup.md", "Capture And Cleanup", "Human seed recording and cleanup notes", True, "audio-seed-retention"),
    FileSpec("02_references/reference-rights.md", "Reference Rights", "Reference-track use boundary", True, "reference-dna"),
    FileSpec("02_references/reference-set.md", "Reference Set", "Reference roles and do-not-copy rules", True, "reference-dna"),
    FileSpec("02_references/reference-dna-card.md", "Reference DNA Card", "Neutral reference DNA extracted for effect-first prompt building", True, "effect-first"),
    FileSpec("02_references/style-dna-card.md", "Style DNA Card", "Neutral transferable style DNA", True, "reference-dna"),
    FileSpec("02_references/protected-identity-removal.md", "Protected Identity Removal", "Artist/song identity removal before prompting", True, "artist-study"),
    FileSpec("02_references/artist-study-intake.md", "Artist Study Intake", "Artist study purpose", True, "artist-study"),
    FileSpec("02_references/representative-song-triad.md", "Representative Song Triad", "Three-song study roles", True, "artist-study"),
    FileSpec("02_references/song-dna-card.md", "Song DNA Card", "Per-song craft extraction", True, "artist-study"),
    FileSpec("02_references/reference-boundary.md", "Reference Boundary", "Allowed and forbidden reference use", True, "reference-dna"),
    FileSpec("02_references/reference-dna-audit.md", "Reference DNA Audit", "Tool-generated reference style DNA and protected identity gate before prompt compile", True, "reference-dna"),
    FileSpec("02_references/chord-skeleton-transfer.md", "Chord Skeleton Transfer", "Reference BPM, key, chord progression, MIDI simplification, upload route, and reverse-analysis plan", True, "chord-skeleton-transfer"),
    FileSpec("02_references/chord-skeleton-transfer-audit.md", "Chord Skeleton Transfer Audit", "Tool-generated conditional gate for reference upload / chord skeleton Suno generation", True, "chord-skeleton-transfer"),
    FileSpec("02_references/chord-skeleton-build-report.md", "Chord Skeleton MIDI Seed Build Report", "Tool-generated safe MIDI block-chord seed report; upload remains human-confirmed", True, "chord-skeleton-transfer"),
    FileSpec("03_writing/lyric-brief.md", "Lyric Brief", "Narrator, situation, images, title phrase", True, "lyric-narrative"),
    FileSpec("03_writing/image-bank.md", "Image Bank", "Concrete images and objects", True, "lyric-narrative"),
    FileSpec("03_writing/section-information-map.md", "Section Information Map", "What each section adds", True, "lyric-narrative"),
    FileSpec("03_writing/cliche-cut.md", "Cliche Cut", "Generic phrase removal", True, "lyric-narrative"),
    FileSpec("03_writing/lyric-narrative-audit.md", "Lyric Narrative Audit", "Tool-generated narrator, image, section-information, and cliche gate before prosody and prompt compile", True, "lyric-narrative"),
    FileSpec("03_writing/prosody-check.md", "Prosody Check", "Language stress, tone, and singability", True, "prosody"),
    FileSpec("03_writing/lyrics-prosody-audit.md", "Lyrics Prosody Audit", "Tool-generated singability gate before prompt compile", True, "prosody"),
    FileSpec("03_writing/title-phrase.md", "Title Phrase", "Hook phrase and function", True, "topline"),
    FileSpec("03_writing/topline-map.md", "Topline Map", "Melodic hook contour and phrase plan", True, "topline"),
    FileSpec("03_writing/topline-hook-audit.md", "Topline Hook Audit", "Tool-generated hook and motif gate before prompt compile", True, "topline"),
    FileSpec("03_writing/melody-contour.md", "Melody Contour", "Verse, pre, chorus, bridge contour", True, "topline"),
    FileSpec("03_writing/harmony-brief.md", "Harmony Brief", "Chord color and harmonic rhythm", True, "harmony-bass"),
    FileSpec("03_writing/progression-map.md", "Progression Map", "Section chord direction", True, "harmony-bass"),
    FileSpec("03_writing/bassline-map.md", "Bassline Map", "Bass role and kick relationship", True, "harmony-bass"),
    FileSpec("03_writing/harmonic-rhythm-map.md", "Harmonic Rhythm Map", "Chord-change rate and harmonic pacing", True, "harmony-bass"),
    FileSpec("03_writing/cadence-and-bridge-plan.md", "Cadence And Bridge Plan", "Chorus arrival, bridge turn, and ending cadence", True, "harmony-bass"),
    FileSpec("03_writing/harmony-bass-audit.md", "Harmony Bass Audit", "Tool-generated harmony and bass gate before prompt compile", True, "harmony-bass"),
    FileSpec("03_writing/groove-audit.md", "Groove Audit", "Drums, bass, and player pocket", True, "groove-humanization"),
    FileSpec("03_writing/drum-realism-map.md", "Drum Realism Map", "Kick, snare, hats, fills, timing, and velocity", True, "groove-humanization"),
    FileSpec("03_writing/instrument-role-map.md", "Instrument Role Map", "Guitar, keys, synth, and instrument playability roles", True, "groove-humanization"),
    FileSpec("03_writing/section-performance-map.md", "Section Performance Map", "Verse, pre, chorus, bridge, and final chorus performance changes", True, "groove-humanization"),
    FileSpec("03_writing/groove-humanization-audit.md", "Groove Humanization Audit", "Tool-generated groove and instrument-performance gate before prompt compile", True, "groove-humanization"),
    FileSpec("03_writing/structure-brief.md", "Structure Brief", "Song form and section function", True, "structure-dynamics"),
    FileSpec("03_writing/energy-map.md", "Energy Map", "Energy and density curve", True, "structure-dynamics"),
    FileSpec("03_writing/section-function-map.md", "Section Function Map", "Section purpose, hook arrival, development, and ending logic", True, "structure-dynamics"),
    FileSpec("03_writing/contrast-continuity-matrix.md", "Contrast Continuity Matrix", "What stays consistent and what develops by section", True, "structure-dynamics"),
    FileSpec("03_writing/transition-cue-sheet.md", "Transition Cue Sheet", "Section-to-section musical cue plan", True, "structure-dynamics"),
    FileSpec("03_writing/second-verse-development.md", "Second Verse Development", "Verse 2 information and arrangement development", True, "structure-dynamics"),
    FileSpec("03_writing/bridge-turn-plan.md", "Bridge Turn Plan", "Bridge reveal, contrast, and return cue", True, "structure-dynamics"),
    FileSpec("03_writing/final-chorus-payoff.md", "Final Chorus Payoff", "Final chorus repeat, development, and payoff", True, "structure-dynamics"),
    FileSpec("03_writing/outro-end-plan.md", "Outro End Plan", "Outro ending logic and last sound", True, "structure-dynamics"),
    FileSpec("03_writing/structure-dynamics-audit.md", "Structure Dynamics Audit", "Tool-generated structure, energy, and transition gate before prompt compile", True, "structure-dynamics"),
    FileSpec("03_writing/singer-brief.md", "Singer Brief", "Range, timbre, diction, breath, delivery", True, "vocal-identity"),
    FileSpec("03_writing/vocal-performance-map.md", "Vocal Performance Map", "Section-by-section vocal performance direction", True, "vocal-identity"),
    FileSpec("03_writing/vocal-arrangement-map.md", "Vocal Arrangement Map", "Lead, doubles, harmonies, ad-libs, and group vocal plan", True, "vocal-identity"),
    FileSpec("03_writing/vocal-identity-audit.md", "Vocal Identity Performance Audit", "Tool-generated vocal identity and performance gate before prompt compile", True, "vocal-identity"),
    FileSpec("03_writing/performance-brief.md", "Performance Brief", "Instrument and vocal performance direction", True, "performance"),
    FileSpec("04_prompt/prompt-compile-brief.md", "Prompt Compile Brief", "Prompt compilation intent", True, "prompt-compile"),
    FileSpec("04_prompt/external-method-claim-ledger.md", "External Method Claim Ledger", "Source-ranked official/local/community method claims before methodology transfer", True, "prompt-methodology"),
    FileSpec("04_prompt/external-method-claim-audit.md", "External Method Claim Audit", "Tool-generated source-ranking gate for external method claims", True, "prompt-methodology"),
    FileSpec("04_prompt/methodology-transfer-plan.md", "Methodology Transfer Plan", "How local and external Suno methodology transfers into this song", True, "prompt-methodology"),
    FileSpec("04_prompt/methodology-transfer-audit.md", "Methodology Transfer Audit", "Tool-generated methodology transfer gate before prompt compile", True, "prompt-methodology"),
    FileSpec("04_prompt/field-responsibility-map.md", "Field Responsibility Map", "What each AI music field owns", True, "prompt-compile"),
    FileSpec("04_prompt/style-field-map.md", "Style Field Map", "Style of Music field plan", True, "prompt-compile"),
    FileSpec("04_prompt/lyrics-context-map.md", "Lyrics Context Map", "Lyrics box and section context", True, "prompt-compile"),
    FileSpec("04_prompt/exclude-negative-aesthetic.md", "Exclude Negative Aesthetic", "Negative aesthetic and AI-flavor exclusions", True, "prompt-compile"),
    FileSpec("04_prompt/field-length-and-specificity-budget.md", "Field Length And Specificity Budget", "Audible terms, vague-term removals, and field budget before prompt compile", True, "prompt-specificity"),
    FileSpec("04_prompt/prompt-specificity-budget-audit.md", "Prompt Specificity Budget Audit", "Tool-generated prompt specificity and realism-descriptor gate before prompt compile", True, "prompt-specificity"),
    FileSpec("04_prompt/genre-lane-authenticity-audit.md", "Genre Lane Authenticity Audit", "Tool-generated genre/lane authenticity gate before prompt compile", True, "genre-lane-authenticity"),
    FileSpec("04_prompt/slider-intent-map.md", "Slider Intent Map", "Weirdness, Style Influence, Audio Influence intent", True, "prompt-compile"),
    FileSpec("04_prompt/persona-voice-model-routing.md", "Persona Voice Model Routing", "Persona, Voice, Custom Model source routing", True, "prompt-compile"),
    FileSpec("04_prompt/personalization-state.md", "Personalization State", "Voice, Persona, Custom Model, My Taste, and Prompt Boost hygiene state", True, "personalization-hygiene"),
    FileSpec("04_prompt/personalization-hygiene-audit.md", "Personalization Hygiene Audit", "Tool-generated personalization state hygiene gate before prompt compile", True, "personalization-hygiene"),
    FileSpec("04_prompt/retention-target.md", "Retention Target", "Audio seed retention target and transformation boundary", True, "audio-seed-retention"),
    FileSpec("04_prompt/prompt-pairing.md", "Prompt Pairing", "How prompt fields and Audio Influence pair with the seed", True, "audio-seed-retention"),
    FileSpec("04_prompt/constraint-conflict-check.md", "Constraint Conflict Check", "Field and rights conflicts", True, "prompt-compile"),
    FileSpec("04_prompt/effect-first-prompt-package.md", "Effect-First Prompt Package", "Effect-first title, lyrics, Style, Exclude, model/settings, batch plan, and review rubric", True, "effect-first"),
    FileSpec("04_prompt/prompt-linter-report.md", "Prompt Linter Report", "Effect-first prompt lint decision, findings, and suggested fixes", True, "effect-first"),
    FileSpec("04_prompt/prompt-preflight-review.md", "Prompt Preflight Review", "Compile approval checklist", True, "prompt-compile"),
    FileSpec("04_prompt/experiment-handoff.md", "Experiment Handoff", "Batch experiment handoff", True, "prompt-experiment"),
    FileSpec("04_prompt/prompt-package-v001.md", "Prompt Package v001", "Initial Suno or provider prompt package", True, "prompt-compile"),
    FileSpec("04_prompt/prompt-memory-update.md", "Prompt Memory Update", "Reusable prompt lesson", True, "prompt-experiment"),
    FileSpec("05_generations/take-ledger.md", "Take Ledger", "Generated takes and metadata index", True, "take-selection"),
    FileSpec("05_generations/experiment-intent.md", "Experiment Intent", "Generation round question, metric, phase, and stop condition", True, "prompt-experiment"),
    FileSpec("05_generations/brief-freeze.md", "Brief Freeze", "Frozen song target before generation batch", True, "prompt-experiment"),
    FileSpec("05_generations/variable-inventory.md", "Variable Inventory", "Prompt/provider variables and allowed changed variables", True, "prompt-experiment"),
    FileSpec("05_generations/prompt-candidate-set.md", "Prompt Candidate Set", "Baseline and variant prompt hypotheses before generation", True, "prompt-experiment"),
    FileSpec("05_generations/batch-generation-plan.md", "Batch Generation Plan", "Generation batch design", True, "prompt-experiment"),
    FileSpec("05_generations/provider-result-ledger.md", "Provider Result Ledger", "Provider/model outputs and scores", True, "provider-routing"),
    FileSpec("05_generations/prompt-iteration-discipline-audit.md", "Prompt Iteration Discipline Audit", "Tool-generated single-variable attribution gate before generation evidence", True, "prompt-experiment"),
    FileSpec("05_generations/generation-evidence-audit.md", "Generation Evidence Audit", "Tool-generated take provenance gate before blind review", True, "prompt-experiment"),
    FileSpec("06_review/anchor-retention-review.md", "Anchor Retention Review", "Specialized listening review for human audio seed retention", True, "audio-seed-retention"),
    FileSpec("06_review/audio-seed-retention-audit.md", "Audio Seed Retention Audit", "Tool-generated conditional human audio seed gate", True, "audio-seed-retention"),
    FileSpec("06_review/blind-review.md", "Blind Review", "Blind listening notes and scores", True, "blind-review"),
    FileSpec("06_review/effect-first-take-review.md", "Effect-First Take Review", "Effect-first take review fields and next changed variable", True, "effect-first"),
    FileSpec("06_review/reverse-caption.md", "Reverse Caption", "What the audio sounds like without prompt context", True, "blind-review"),
    FileSpec("06_review/hook-memory-test.md", "Hook Memory Test", "Hook recall and 20-30 second test", True, "blind-review"),
    FileSpec("06_review/vocal-reverse-caption.md", "Vocal Reverse Caption", "Vocal-only identity and artifact review", True, "vocal-review"),
    FileSpec("06_review/ten-dimension-score.md", "Ten Dimension Score", "Human-feel scorecard", True, "blind-review"),
    FileSpec("06_review/alignment-vs-preference.md", "Alignment Vs Preference", "Brief fit versus song quality", True, "blind-review"),
    FileSpec("06_review/take-selection-decision.md", "Take Selection Decision", "Best take decision and repair route", True, "blind-review"),
    FileSpec("06_review/external-listener-panel.md", "External Listener Panel", "External listener sample notes", True, "external-feedback"),
    FileSpec("06_review/first-20-second-test.md", "First 20 Second Test", "Early skip and attention test", True, "external-feedback"),
    FileSpec("06_review/ai-flavor-red-flag-survey.md", "AI Flavor Red Flag Survey", "Listener AI-flavor flags", True, "external-feedback"),
    FileSpec("06_review/release-listener-evidence-audit.md", "Release Listener Evidence Audit", "Tool-generated external listener release gate", True, "external-feedback"),
    FileSpec("07_repair/repair-route-map.md", "Repair Route Map", "Problem layer and repair route", True, "repair-routing"),
    FileSpec("07_repair/artifact-audit-intent.md", "Artifact Audit Intent", "Artifact diagnosis purpose", True, "artifact-diagnosis"),
    FileSpec("07_repair/blind-first-listen.md", "Blind First Listen", "First-pass artifact notes", True, "artifact-diagnosis"),
    FileSpec("07_repair/20-second-red-flag-scan.md", "20 Second Red Flag Scan", "Fast artifact scan", True, "artifact-diagnosis"),
    FileSpec("07_repair/vocal-artifact-sheet.md", "Vocal Artifact Sheet", "Vocal artifact details", True, "artifact-diagnosis"),
    FileSpec("07_repair/stem-solo-diagnosis.md", "Stem Solo Diagnosis", "Stem bleed and artifact check", True, "artifact-diagnosis"),
    FileSpec("07_repair/artifact-severity-score.md", "Artifact Severity Score", "Severity and routing decision", True, "artifact-diagnosis"),
    FileSpec("07_repair/regression-listen.md", "Regression Listen", "Repair regression comparison", True, "repair-routing"),
    FileSpec("07_repair/repair-log.md", "Repair Log", "Repair attempts and outcomes", True, "repair-routing"),
    FileSpec("07_repair/artifact-memory-bank.md", "Artifact Memory Bank", "Reusable artifact lessons", True, "artifact-diagnosis"),
    FileSpec("08_stems-daw/best-take-lock.md", "Best Take Lock", "Locked take for DAW or stems", True, "daw-humanization"),
    FileSpec("08_stems-daw/daw-handoff-intent.md", "DAW Handoff Intent", "Purpose and collaborator for DAW handoff", True, "daw-humanization"),
    FileSpec("08_stems-daw/export-and-stems-ledger.md", "Export And Stems Ledger", "Exports, stems, and source formats", True, "daw-humanization"),
    FileSpec("08_stems-daw/tempo-map-and-section-grid.md", "Tempo Map And Section Grid", "Tempo and section grid", True, "daw-humanization"),
    FileSpec("08_stems-daw/lead-sheet-and-chord-chart.md", "Lead Sheet And Chord Chart", "Lead sheet and chord chart", True, "daw-humanization"),
    FileSpec("08_stems-daw/midi-transcription-and-correction.md", "MIDI Transcription And Correction", "MIDI correction notes", True, "daw-humanization"),
    FileSpec("08_stems-daw/stem-quality-triage.md", "Stem Quality Triage", "Stem usability and artifacts", True, "daw-humanization"),
    FileSpec("08_stems-daw/human-overdub-priority.md", "Human Overdub Priority", "Human performance replacement priority", True, "daw-humanization"),
    FileSpec("08_stems-daw/vocal-rerecord-plan.md", "Vocal Rerecord Plan", "Human lead vocal rerecord plan", True, "daw-humanization"),
    FileSpec("08_stems-daw/rhythm-section-rerecord-plan.md", "Rhythm Section Rerecord Plan", "Drums and bass rerecord plan", True, "daw-humanization"),
    FileSpec("08_stems-daw/hybrid-arrangement-session.md", "Hybrid Arrangement Session", "Human core layers and AI textures", True, "daw-humanization"),
    FileSpec("08_stems-daw/mix-replacement-map.md", "Mix Replacement Map", "Which AI layers are kept or replaced", True, "daw-humanization"),
    FileSpec("08_stems-daw/session-versioning.md", "Session Versioning", "DAW session versioning and folder plan", True, "daw-humanization"),
    FileSpec("08_stems-daw/human-contribution-and-rights-link.md", "Human Contribution And Rights Link", "Human contribution and release rights handoff", True, "daw-humanization"),
    FileSpec("08_stems-daw/final-humanized-master-review.md", "Final Humanized Master Review", "Final humanized master blind review", True, "daw-humanization"),
    FileSpec("08_stems-daw/session-pack.md", "Session Pack", "DAW handoff package", True, "daw-humanization"),
    FileSpec("09_vocal/voice-rights.md", "Voice Rights", "Voice source and permission", True, "vocal-production"),
    FileSpec("09_vocal/key-range-and-lyric-markup.md", "Key Range And Lyric Markup", "Vocal range and lyric markup", True, "vocal-production"),
    FileSpec("09_vocal/vocal-session-prep.md", "Vocal Session Prep", "Vocal session plan", True, "vocal-production"),
    FileSpec("09_vocal/guide-vocal-notes.md", "Guide Vocal Notes", "Guide vocal performance notes", True, "vocal-production"),
    FileSpec("09_vocal/lead-vocal-comp.md", "Lead Vocal Comp", "Lead vocal comp plan", True, "vocal-production"),
    FileSpec("09_vocal/pitch-timing-emotion-pass.md", "Pitch Timing Emotion Pass", "Subtle pitch/timing/emotion pass", True, "vocal-production"),
    FileSpec("09_vocal/breath-sibilance-mouth-noise-pass.md", "Breath Sibilance Mouth Noise Pass", "Breath and sibilance pass", True, "vocal-production"),
    FileSpec("09_vocal/doubles-harmonies-adlibs-plan.md", "Doubles Harmonies Adlibs Plan", "Vocal arrangement plan", True, "vocal-production"),
    FileSpec("09_vocal/vocal-chain-and-space.md", "Vocal Chain And Space", "Vocal chain and spatial design", True, "vocal-production"),
    FileSpec("09_vocal/ai-stem-integration.md", "AI Stem Integration", "Human vocal and AI stems integration", True, "vocal-production"),
    FileSpec("09_vocal/human-contribution-ledger-link.md", "Human Contribution Ledger Link", "Link to release contribution ledger", True, "vocal-production"),
    FileSpec("10_mix-master/post-review.md", "Post Review", "Post-production review", True, "mix-master"),
    FileSpec("10_mix-master/arrangement-density-triage.md", "Arrangement Density Triage", "Arrangement density and clutter", True, "post-production"),
    FileSpec("10_mix-master/mix-plan.md", "Mix Plan", "Mix direction and priorities", True, "mix-master"),
    FileSpec("10_mix-master/mix-lock-preflight.md", "Mix Lock Preflight", "Pre-master mix lock check", True, "mix-master"),
    FileSpec("10_mix-master/post-production-mix-lock-audit.md", "Post Production Mix Lock Audit", "Tool-generated arrangement density, vocal center, low-end, space, transition, artifact, and mix-lock gate before release listener", True, "post-production"),
    FileSpec("10_mix-master/final-master-intent.md", "Final Master Intent", "Mastering intent", True, "master-qc"),
    FileSpec("10_mix-master/release-audio-technical-inspection.md", "Release Audio Technical Inspection", "Basic WAV delivery inspection", True, "master-qc"),
    FileSpec("10_mix-master/loudness-true-peak-report.md", "Loudness True Peak Report", "LUFS and true peak report", True, "master-qc"),
    FileSpec("10_mix-master/codec-preview.md", "Codec Preview", "Codec translation preview", True, "master-qc"),
    FileSpec("10_mix-master/translation-listen-matrix.md", "Translation Listen Matrix", "Device and platform listen matrix", True, "master-qc"),
    FileSpec("10_mix-master/mono-phase-low-end-check.md", "Mono Phase Low End Check", "Mono, phase, low-end checks", True, "master-qc"),
    FileSpec("10_mix-master/transient-and-limiter-audit.md", "Transient And Limiter Audit", "Limiter and transient audit", True, "master-qc"),
    FileSpec("10_mix-master/release-audio-qc-report.md", "Release Audio QC Report", "Release audio quality gate", True, "master-qc"),
    FileSpec("11_release/release-intent.md", "Release Intent", "Release goal and platform context", True, "release-rights"),
    FileSpec("11_release/source-rights-ledger.md", "Source Rights Ledger", "Release copy of source rights", True, "release-rights"),
    FileSpec("11_release/release-rights-link.md", "Release Rights Link", "Human audio seed rights link into release evidence", True, "release-rights"),
    FileSpec("11_release/subscription-and-generation-context.md", "Subscription And Generation Context", "Tool plan and generation context", True, "release-rights"),
    FileSpec("11_release/human-contribution-ledger.md", "Human Contribution Ledger", "Human creative contribution record", True, "release-rights"),
    FileSpec("11_release/copyrightability-notes.md", "Copyrightability Notes", "Copyrightability notes and uncertainty", True, "release-rights"),
    FileSpec("11_release/similarity-and-impersonation-review.md", "Similarity And Impersonation Review", "Reference and voice similarity risk", True, "release-rights"),
    FileSpec("11_release/platform-distribution-matrix.md", "Platform Distribution Matrix", "Platform and distributor AI policy matrix", True, "release-rights"),
    FileSpec("11_release/ai-use-disclosure.md", "AI Use Disclosure", "Platform or distributor disclosure", True, "release-rights"),
    FileSpec("11_release/platform-policy-matrix.md", "Platform Policy Matrix", "Platform policy checks", True, "release-rights"),
    FileSpec("11_release/anti-spam-release-policy.md", "Anti Spam Release Policy", "Anti-spam and artificial streaming guardrails", True, "release-rights"),
    FileSpec("11_release/distributor-preflight.md", "Distributor Preflight", "Distributor readiness check", True, "release-rights"),
    FileSpec("11_release/release-candidate-evidence-audit.md", "Release Candidate Evidence Audit", "Release candidate evidence audit", True, "release-rights"),
    FileSpec("11_release/release-candidate-rights-gate.md", "Release Candidate Rights Gate", "Final release rights decision", True, "release-rights"),
    FileSpec("11_release/release-candidate-package.md", "Release Candidate Package", "Final release candidate package", True, "release-rights"),
    FileSpec("11_release/post-release-monitoring.md", "Post Release Monitoring", "Post-release platform and rights monitoring", True, "release-rights"),
    FileSpec("11_release/release_candidate/metadata/release-candidate-manifest.md", "Release Candidate Manifest", "Release candidate file manifest", True, "release-rights"),
    FileSpec("12_catalog-memory/catalog-seed-hygiene.md", "Catalog Seed Hygiene", "Human seed reuse boundary for catalog memory", True, "catalog-memory"),
    FileSpec("12_catalog-memory/user-preference-profile.md", "User Preference Profile", "Stable and provisional user preferences for effect-first Suno runs", True, "effect-first"),
    FileSpec("12_catalog-memory/catalog-memory-update.md", "Catalog Memory Update", "Catalog memory writeback", True, "catalog-memory"),
    FileSpec("12_catalog-memory/prompt-memory-update.md", "Prompt Memory Update", "Prompt memory writeback", True, "catalog-memory"),
    FileSpec("12_catalog-memory/artifact-memory-update.md", "Artifact Memory Update", "Artifact memory writeback", True, "catalog-memory"),
    FileSpec("12_catalog-memory/sonic-signature-update.md", "Sonic Signature Update", "Sonic signature writeback", True, "catalog-memory"),
    FileSpec("12_catalog-memory/lyric-universe-update.md", "Lyric Universe Update", "Lyric universe writeback", True, "catalog-memory"),
    FileSpec("12_catalog-memory/reference-boundary-update.md", "Reference Boundary Update", "Reference boundary writeback", True, "catalog-memory"),
    FileSpec("12_catalog-memory/next-song-brief-seed.md", "Next Song Brief Seed", "Next song seed from catalog memory", True, "catalog-memory"),
    FileSpec("12_catalog-memory/catalog-writeback-manifest.md", "Catalog Writeback Manifest", "Catalog memory evidence manifest", True, "catalog-memory"),
    FileSpec("12_catalog-memory/postmortem-and-prompt-memory.md", "Postmortem And Prompt Memory", "Postmortem and reusable lessons", True, "catalog-memory"),
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "song"


def today_stamp() -> str:
    return dt.date.today().strftime("%Y%m%d")


def project_dir_name(args: argparse.Namespace) -> str:
    date = re.sub(r"[^0-9]", "", args.date)
    if len(date) != 8:
        raise ValueError("--date must be YYYYMMDD or YYYY-MM-DD")
    language = slugify(args.language)
    lane = slugify(args.lane)
    slug = slugify(args.slug or args.title)
    return f"{date}_{language}-{lane}_{slug}"


def common_header(title: str, args: argparse.Namespace, rel_path: str) -> str:
    return f"""# {title}

Project root: {args.project_dir_name}
Song title: {args.title}
Artist / catalog: {args.artist_project}
Language: {args.language}
Lane: {args.lane}
Use case: {args.use_case}
File: {rel_path}
Created: {args.date}
Generated by: tools/create_music_song_project.py

"""


def render_file(spec: FileSpec, args: argparse.Namespace) -> str:
    header = common_header(spec.title, args, spec.path)
    if spec.path == "README.md":
        return f"""# {args.title}

Project / artist: {args.artist_project}
Language: {args.language}
Lane: {args.lane}
Use case: {args.use_case}
Status: design
Best take:
Current blocker:
Next action: Fill 00_admin/song-production-control-board.md
Do-not-publish-if: rights, source, voice, audio QC, or catalog gates are unresolved.
Last updated: {args.date}

## Core Paths

- 00_admin/song-production-control-board.md
- 01_brief/song-brief.md
- 04_prompt/external-method-claim-audit.md
- 02_references/chord-skeleton-transfer-audit.md
- 04_prompt/prompt-package-v001.md
- 05_generations/take-ledger.md
- 05_generations/generation-evidence-audit.md
- 06_review/audio-seed-retention-audit.md
- 06_review/blind-review.md
- 07_repair/repair-route-map.md
- 10_mix-master/post-production-mix-lock-audit.md
- 10_mix-master/release-audio-qc-report.md
- 11_release/release-candidate-rights-gate.md
- 12_catalog-memory/postmortem-and-prompt-memory.md
"""
    if spec.path == "00_admin/file-manifest.md":
        rows = [
            "| path | role | source | mutable | linked gate | notes |",
            "|---|---|---|---|---|---|",
        ]
        for item in FILE_SPECS:
            rows.append(
                f"| {item.path} | {item.role} | scaffold | {'yes' if item.mutable else 'no'} | {item.gate} | |"
            )
        return header + "\n".join(rows) + "\n"
    if spec.path == "00_admin/song-production-control-board.md":
        return header + """Current stage: methodology-transfer-gate
Status: design
Current blocker: methodology transfer audit has not been generated
Next action: run tools/audit_music_song_project_status.py after filling or generating evidence
Why this action: the audit tool keeps the unattended workflow on the correct stage gate
Do not do: do not generate, repair, master, release, or catalog-promote without evidence gates
Next command:
```bash
python3 tools/audit_music_song_project_status.py --project-root . --write --allow-overwrite
```

Generated / updated by: tools/audit_music_song_project_status.py
"""
    if spec.path == "00_admin/project-status-audit.md":
        return header + """Current stage:
Status:
Current blocker:
Next action:
Next command:

## Gate Evidence

Generated / updated by: tools/audit_music_song_project_status.py
"""
    if spec.path == "00_admin/next-action.md":
        return header + """Stage:
Status:
Action:
Blocker:

Generated / updated by: tools/audit_music_song_project_status.py
"""
    if spec.path == "01_brief/catalog-fit.md":
        return header + """Catalog mode:
- one-off / artist-catalog / demo
Artist / catalog:
Song role:
Catalog lane:
Identity fit:
Sonic signature fit:
Lyric universe fit:
Vocal identity fit:
Difference from previous songs:
Do not repeat:
Protected identity boundary:
Validation route:
Catalog decision:

Not a catalog project:
- yes / no

Rule: if this is an artist/catalog song, define what identity it preserves and what it changes before prompt work starts.
"""
    if spec.path == "01_brief/catalog-fit-audit.md":
        return header + """Decision: hold

## Catalog Fit Evidence

Catalog mode:
Artist / catalog:
Song role:
Catalog lane:
Artist/catalog fit:
Identity fit:
Sonic signature fit:
Lyric universe fit:
Vocal identity fit:
Catalog evolution:
Difference from previous songs:
Do not repeat:
Protected identity boundary:
Validation route:
Catalog decision:
Prompt handoff:
Catalog memory handoff:

Generated by: tools/audit_music_catalog_fit.py
"""
    if spec.path == "00_admin/generation-route-plan.md":
        return header + """Generated by: tools/plan_music_generation_route.py
Decision: pending
Operating mode:
Confidence:

## First-Principles Decision

- User outcome:
- Primary route:
- Fallback route:
- Effect lever:
- User effort:
- Risk level:
- Next action:

## User-Facing Confirmation Card

- Mode:
- Decision:
- Upload action expected:
- Approval phrase required:
- Credits/account action expected:
- Effect-first check:

Run:
```bash
python3 tools/plan_music_generation_route.py --project-root "$PROJECT" --write --allow-overwrite
```
"""
    if spec.path == "00_admin/effect-first-suno-run.md":
        return header + """Generated by: tools/prepare_music_effect_first_suno_run.py
Decision: pending

## SongRun

- Route decision:
- Operating mode:
- Primary route:
- Risk level:
- Next action:

## Generation Confirmation Card

- Title:
- Use case:
- Language:
- Mode:
- Model/settings:
- Batch count:
- Changed variable:
- Style of Music:
- Exclude:
- Upload action expected:
- Approval phrase required:

Run:
```bash
python3 tools/prepare_music_effect_first_suno_run.py --project-root "$PROJECT" --write --allow-overwrite
```
"""
    if spec.path == "02_references/reference-dna-card.md":
        return header + """Generated by: tools/prepare_music_effect_first_suno_run.py

- tempo:
- key_or_mode:
- harmonic_color:
- groove:
- instrumentation:
- production_texture:
- vocal_register:
- energy_curve:
- do_not_copy: no artist name, song title, melody, lyrics, riff, vocal identity, sample, stem, or signature arrangement
- similarity_risk:
"""
    if spec.path == "04_prompt/effect-first-prompt-package.md":
        return header + """Generated by: tools/prepare_music_effect_first_suno_run.py
Decision: hold

## PromptVersion

- Title:
- Creative brief:
- Changed variable:

## Lyrics

## Style of Music

genre: ; vocal: ; instrumentation: ; production: ; mood:

## Exclude Styles

robotic vocal, muddy mix, harsh sibilance, abrupt ending, random rap verse, artist imitation, copied melody, copied lyrics, recognizable riff, reference singer voice

## Model / Slider Intent

## Batch Plan

## Review Rubric
"""
    if spec.path == "04_prompt/prompt-linter-report.md":
        return header + """Generated by: tools/prepare_music_effect_first_suno_run.py
Decision: hold

Required checks: style_too_generic, genre_soup, artist_name_risk, voice_imitation_risk, exclude_conflict, lyrics_too_short, lyrics_too_dense, missing_hook, missing_vocal_identity, missing_production_detail, section_tag_overload, reference_identity_leak, slider_conflict

| code | severity | message | suggested fix |
|---|---|---|---|
| pending | warning | run the effect-first preparation tool | python3 tools/prepare_music_effect_first_suno_run.py --project-root "$PROJECT" --write --allow-overwrite |
"""
    if spec.path == "06_review/effect-first-take-review.md":
        return header + """Generated by: tools/prepare_music_effect_first_suno_run.py
Next changed variable:

## Take Review Fields

- first_20s:
- hook_memory:
- vocal_identity:
- lyrics_intelligibility:
- groove:
- chorus_lift:
- arrangement:
- ai_artifacts:
- fit_to_brief:
- similarity_risk:
- user_preference:
- next_action:
"""
    if spec.path == "12_catalog-memory/user-preference-profile.md":
        return header + """Generated by: tools/prepare_music_effect_first_suno_run.py

## Fields

- default_language:
- default_use_case:
- default_batch_size:
- preferred_genres:
- preferred_vocals:
- avoid_styles:
- default_exclude:
- rights_default:
- project_mode_default:
- successful_patterns:
- rejected_patterns:

## Rule

Do not promote one-off feedback into permanent memory. Stable preferences require explicit user confirmation or repeated evidence across sessions.
"""
    if spec.path == "04_prompt/external-method-claim-ledger.md":
        return header + """| source/platform | url/path | claim | source type | confidence | target control surface | testable variable | adoption status | validation route | risk |
|---|---|---|---|---|---|---|---|---|---|
| Suno official help | /path/to/suno-prompt-methodology/sources/official-clean-md/official-creative-sliders.md | Creative Sliders define Weirdness, Style Influence, and Audio Influence as controllable generation surfaces | official | high | Creative Sliders | Style Influence only | foundation | prompt-iteration-discipline-gate + blind A/B | current model behavior may shift |
| local local Suno prompt methodology | /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md | Only one major variable should change in a reviewable iteration | local methodology | high | batch design | Changed variables | foundation | prompt-iteration-discipline-gate | too rigid for early exploration |
| community source candidate | URL or local path | claim to test | community/video/GitHub | low/medium | Style of Music / Lyrics context / Exclude / sliders | one variable | candidate experiment only | blind A/B, reverse caption, AI flavor survey | unverified; do not promote without evidence |
"""
    if spec.path == "02_references/chord-skeleton-transfer.md":
        return header + """Reference status:
- none / self-owned / authorized / third-party listen-only
Allowed action:
Forbidden use:

Source section:
Bars:
BPM:
Key:
Progression:
Harmonic rhythm:
Emotional color:
Bass/root direction:

Tool used:
Tool confidence:
Manual corrections:

MIDI simplification:
Removed:
Extended:
Retained:
Do-not-copy:

Seed file:
Suno route:
- text-only / Audio Upload / Cover / Custom Mode
Style field:
Exclude:
Retention target:
Prompt pairing:
Reverse analysis plan:
Similarity risk:

Rule: if this route uses Audio Upload, Cover, nonzero Audio Influence, or exported MIDI/audio from a reference, prove ownership or authorization before upload.
"""
    if spec.path == "02_references/chord-skeleton-transfer-audit.md":
        return header + """Generated by: tools/audit_music_chord_skeleton_transfer.py
Decision: not applicable

## Chord Skeleton Transfer

Rights route:
Skeleton tags:
MIDI simplification:
Suno upload route:
Reverse analysis plan:
Prompt compile handoff: not applicable
"""
    if spec.path == "02_references/chord-skeleton-build-report.md":
        return header + """Generated by: tools/build_music_chord_skeleton_seed.py
Decision: not applicable

MIDI file: not written
Suno action: not opened; not uploaded; awaiting explicit upload confirmation

## Rights And Boundary

Rights route:
Allowed action:
Can upload audio:
Commercial use:
Do-not-copy:

## Skeleton Spec

- BPM:
- Key:
- Progression:
- Harmonic rhythm:
- Bass/root direction:

## Builder Boundary

- Generates long block chords only.
- Does not generate melody, lyric rhythm, riff contour, voice, sample, drum groove, or arrangement timing.
- Keeps upload as a separate human-confirmed sensitive action.
"""
    if spec.path == "04_prompt/external-method-claim-audit.md":
        return header + """Decision: hold

## External Method Claim Evidence

External method claims:
Official/local foundations:
Community candidates:
Candidate-only handoff:
Validation route:
Rejected claims:
Methodology transfer handoff:

Generated by: tools/audit_music_external_method_claims.py
"""
    if spec.path == "04_prompt/personalization-state.md":
        return header + """Active personalization features:
- none / Voice / Persona / Custom Model / My Taste / Prompt Boost
Account / profile scope:
Source / rights evidence:
Catalog fit link:
Isolation boundary:
Attribution plan:
Rollback condition:

Voice source:
Voice verification:
Persona source:
Persona role:
Custom Model source:
Custom Model corpus:
Custom Model rights:
My Taste state:
My Taste summary:
Prompt Boost state:
Original style text:
Boosted style text:
Boost delta:
Personalization decision:

Rule: if any personalization feature is active, preserve source, isolation, attribution, and rollback evidence before prompt compile.
"""
    if spec.path == "04_prompt/personalization-hygiene-audit.md":
        return header + """Decision: not applicable

## Personalization Hygiene Evidence

Active personalization features: none
Personalization hygiene: not applicable
Account / profile scope:
Source / rights evidence:
Catalog fit link:
Isolation boundary:
Attribution plan:
Rollback condition:
Prompt compile handoff: not applicable

Generated by: tools/audit_music_personalization_hygiene.py
"""
    if spec.path == "04_prompt/methodology-transfer-plan.md":
        return header + """Local method sources:
- /path/to/suno-prompt-methodology/local Suno prompt methodology知识笔记.md
- /path/to/suno-prompt-methodology/templates/suno-prompt-template.md
- /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md

Official control surfaces:
- Style of Music
- Lyrics box
- Exclude
- Creative Sliders
- Voice / Persona / Custom Model / My Taste only if source evidence is active

Community / external candidates:
- Use only claims that pass external-method-claim-audit.md; treat Bilibili / Douyin / YouTube / GitHub prompt tips as experiment candidates, not rules.

Source confidence split:
- official facts = platform controls and field behavior; local methodology = workflow/template/checklist; community/external = candidate hypotheses that need A/B and blind listening.

Adopted method:

Song-specific transfer:

Model/version rationale:

Primary Suno tool route:

Human-likeness hypothesis:

Variable discipline:
- one primary variable per generation batch; keep brief, title phrase, language, human anchor lane, and rights boundary fixed.

Rejected magic prompt claims:
- reject guaranteed-hit tags, celebrity-copy prompts, unverified secret codes, and prompt bundles that are not tied to a blind validation metric.

Protected-identity safeguard:
- do not use artist, band, producer, song, album, or identifiable voice names in generation-facing fields; route references through style DNA.

Validation metric:

Drift/rollback condition:

Source freshness:
"""
    if spec.path == "04_prompt/methodology-transfer-audit.md":
        return header + """Decision: hold

## Methodology Transfer Evidence

Local source root: /path/to/suno-prompt-methodology
Local source status: not audited
External method claims:
Source confidence split:
Official control surfaces:
Community candidates:
Model/version rationale:
Primary tool route:
Human-likeness transfer:
Song-specific transfer:
Variable discipline:
Anti-magic safeguards:
Protected-identity safeguard:
Validation metric:
Rollback condition:
Source freshness:

Generated by: tools/audit_music_methodology_transfer.py
"""
    if spec.path == "04_prompt/field-length-and-specificity-budget.md":
        return header + """Must-hear terms:
Nice-to-have terms:
Remove vague terms:
Remove duplicated terms:
Move to Lyrics context:
Move to Exclude:
Move to experiment note:
Field budget decision:
Source / rationale: Use /path/to/suno-prompt-methodology and realism-descriptors.md; replace vague prompt words with recording, performance, and section language.
"""
    if spec.path == "04_prompt/prompt-specificity-budget-audit.md":
        return header + """Generated by: tools/audit_music_prompt_specificity_budget.py
Decision: hold

## Specificity Budget Evidence

Style source: 04_prompt/style-field-map.md
Budget source: 04_prompt/field-length-and-specificity-budget.md
Methodology transfer: missing or repair
Style specificity tags:
Recording realism tags:
Performance realism tags:
Section/director tags:
Field budget tags:
Vague term removals:
Protected identity check:
Prompt compile handoff:
"""
    if spec.path == "04_prompt/genre-lane-authenticity-audit.md":
        return header + """Generated by: tools/audit_music_genre_lane_authenticity.py
Decision: hold

## Genre/Lane Evidence

Prompt specificity: missing or repair
Primary lane:
Genre terms detected:
Language lane:
Secondary lane purpose:
Era / scene anchor:
Tempo / meter:
Vocal lane:
Arrangement lane:
Production lane:
Lyric stance:
Hook mechanism:
Style-lyric fit:
Arrangement fit:
Production fit:
Anti-drift / exclude plan:
Genre/lane authenticity:
Prompt compile handoff:
"""
    if spec.path == "04_prompt/prompt-package-v001.md":
        return header + """## Metadata

- Title:
- Project:
- Version: v001
- Model:
- Weirdness:
- Style Influence:
- Audio Influence:
- Vocal Gender:
- Instrumental:
- Exclude:
- Human Anchor Lane:
- Voice Identity Source:
- Persona Source:
- Custom Model Source:
- Custom Model Corpus:
- Voice Verification:
- My Taste State:
- My Taste Summary:
- Prompt Boost State:
- Boosted Style Text:

## Style Of Music

```text
genre:
vocal:
instrumentation:
production:
mood:
```

## Lyrics

```text
[Song intent:]
[Tempo feel:]

[Intro | function | arrangement note]

[Verse 1 | narrator action | vocal delivery]

[Pre-Chorus | tension action | fewer words]

[Chorus | title hook | melodic landing]

[Verse 2 | new information | groove change]

[Bridge | contrast | new perspective]

[Final Chorus | payoff | harmony/double note]

[Outro | ending plan]
[End]
```

## Prompt Rationale

- Genre anchor:
- Vocal identity:
- Core instruments:
- Production texture:
- Emotional arc:
- Why these exclusions:
- What to test first:
- Human anchor routing:
- Identity continuity:
"""
    if spec.path == "02_references/human-seed-intent.md":
        return header + """Project:
Song:
Human creator:
Seed purpose:
- melody / rhythm / harmony / vocal / texture / arrangement / catalog

Why text prompt is not enough:
What must remain audible:
What may change:
What must not happen:

Target workflow:
- Audio Upload
- Cover
- Extend
- Add Vocals
- Studio section
- Inspire
- Voice / Persona / Custom Model
"""
    if spec.path == "02_references/audio-rights-ledger.md":
        return header + """File:
Recorded by:
Performer:
Contains:
- vocal / instrument / loop / sample / field recording / generated audio

Owner:
Consent:
Commercial use:
Can upload to AI tool:
Can use in release:
Can use in Persona / Voice / Custom Model / Inspire:

Third-party material:
Suno plan at upload:
Tool:
Date:
Reviewer:
"""
    if spec.path == "02_references/seed-type-classification.md":
        return header + """Primary seed type:
Secondary seed type:
Section:
Duration:
Tempo / meter:
Key guess:
Strongest audible feature:
Weakest audible feature:
Keep:
May transform:
Should ignore:
"""
    if spec.path == "02_references/capture-and-cleanup.md":
        return header + """Seed file:
Capture device / chain:
Noise:
Timing / count-in:
Tempo confidence:
Pitch confidence:
Cleanup performed:
What the model should hear:
What the model should ignore:
Export path:
"""
    if spec.path == "03_writing/lyrics-prosody-audit.md":
        return header + """Decision: hold

Language:
Title phrase:
Prosody notes:
Section tags:
Lyric lines:
Blockers:
Warnings:

## Section Metrics

| section | lines | average units | max units |
|---|---:|---:|---:|

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Lyrics tags:
Exclude additions:
Blind-listening red flags:

Generated by: tools/audit_music_lyrics_prosody.py
"""
    if spec.path == "03_writing/lyric-narrative-audit.md":
        return header + """Generated by: tools/audit_music_lyric_narrative.py
Decision: hold

## Lyric Narrative Evidence

Narrator/situation tags:
Concrete image tags:
Title phrase function:
Central metaphor:
Section information tags:
Cliche removal:
Verse 2 development:
Bridge perspective:
Lyrics rewrite handoff:

## Findings

| severity | code | message | route |
|---|---|---|---|
| hold | not_generated | Run tools/audit_music_lyric_narrative.py before prosody and prompt compile | lyric-narrative |

## Prompt Routing

Lyrics context source: 04_prompt/lyrics-context-map.md
Rewrite route: lyric-brief.md -> image-bank.md -> section-information-map.md -> cliche-cut.md -> lyrics-context-map.md -> lyrics-prosody-audit.md
Blind-listening red flags: anonymous narrator, abstract slogan chorus, Verse 2 repeat, no bridge/payoff turn, title not recalled, concrete images not heard
"""
    if spec.path == "02_references/reference-dna-audit.md":
        return header + """Decision: hold

Reference set:
Allowed action:
Forbidden use:
Can upload audio:
Commercial use:
Protected identity removed:
Reference boundary:
Similarity risk:
Blockers:
Warnings:

## Reference Design

| field | value |
|---|---|
| material type | |
| owner | |
| license / permission | |
| tempo / meter | |
| groove | |
| form | |
| energy timeline | |
| hook mechanism | |
| vocal delivery | |
| arrangement palette | |
| production space | |
| do-not-copy list | |
| original contribution | |
| prompt implication | |
| Suno tool choice | |

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Reference tags:
Style DNA tags:
Protected identity removal:
Similarity blind test:
Prompt-safe reference route:
Exclude additions:
Repair route:

Generated by: tools/audit_music_reference_dna.py
"""
    if spec.path == "03_writing/topline-hook-audit.md":
        return header + """Decision: hold

Language:
Title phrase:
Title units:
Natural spoken stress:
Long-note word:
Rhythm cell:
Motif contour:
Start position:
Repeat plan:
Contrast plan:
Chorus title landing:
Demo source:
Demo rights:
Blockers:
Warnings:

## Hook Design

| field | value |
|---|---|
| meaning | |
| target interval | |
| bridge contrast | |
| final chorus variation | |
| demo keep | |

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Topline tags:
Audio seed routing:
Blind hook test:
Repair route:

Generated by: tools/audit_music_topline_hook.py
"""
    if spec.path == "03_writing/harmony-brief.md":
        return header + """Project:
Language:
Genre:
Tempo / meter:
Song emotion:
Lyric turning point:
Topline hook status:

Key / mode target:
Main chord color:
Tension level:
Bass identity:
Must avoid:
Exact harmony required? yes/no
If exact: self-made demo / MIDI / audio plan:
"""
    if spec.path == "03_writing/progression-map.md":
        return header + """[Verse 1]
Progression:
Function:
Density:
Why it fits lyrics:

[Pre-Chorus]
Progression / color:
Tension device:
Target chord:

[Chorus]
Progression:
Arrival point:
Title phrase chord:

[Verse 2]
Variation:

[Bridge]
New color:
Reason:

[Final Chorus]
Return / lift:
"""
    if spec.path == "03_writing/bassline-map.md":
        return header + """Primary bass role:
Kick relationship:
Range / sound:
Verse motion:
Pre motion:
Chorus motion:
Bridge motion:
Fills / pickups:
Avoid:
"""
    if spec.path == "03_writing/harmonic-rhythm-map.md":
        return header + """Verse chord-change rate:
Pre chord-change rate:
Chorus chord-change rate:
Bridge chord-change rate:
Where harmony should pause:
Where harmony should accelerate:
"""
    if spec.path == "03_writing/cadence-and-bridge-plan.md":
        return header + """Chorus arrival:
Pre target:
Bridge contrast:
Final chorus lift:
Ending cadence:
Do not use:
"""
    if spec.path == "03_writing/harmony-bass-audit.md":
        return header + """Decision: hold

Language:
Genre:
Tempo / meter:
Key / mode target:
Main chord color:
Tension level:
Bass identity:
Chorus arrival:
Title phrase chord:
Kick relationship:
Harmonic rhythm:
Ending / lift:
Exact harmony required:
Blockers:
Warnings:

## Harmony Design

| field | value |
|---|---|
| song emotion | |
| lyric turning point | |
| verse function | |
| pre tension | |
| bridge contrast | |
| final chorus lift | |
| bass range / sound | |
| avoid | |

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Harmony tags:
Bass tags:
Topline/harmony fit:
Exclude additions:
Repair route:

Generated by: tools/audit_music_harmony_bass.py
"""
    if spec.path == "03_writing/performance-brief.md":
        return header + """Song:
Language:
Style:
Tempo / meter:
Master pocket:
Drum role:
Bass role:
Guitar role:
Keys / synth role:
Vocal-rhythm relationship:
Verse feel:
Pre-chorus feel:
Chorus feel:
Bridge feel:
Must not sound like:
Repair priority:
"""
    if spec.path == "03_writing/drum-realism-map.md":
        return header + """Kick:
Snare:
Hats / ride:
Ghost notes:
Fills:
Cymbals:
Velocity shape:
Timing shape:
Section changes:
Do not:
"""
    if spec.path == "03_writing/instrument-role-map.md":
        return header + """Guitar role:
Guitar playability:
Keys / synth role:
Keys / synth playability:
Lead / hook instrument:
Vocal space:
Texture control:
Playable:
Do not:
"""
    if spec.path == "03_writing/section-performance-map.md":
        return header + """[Verse 1]
Performance:

[Pre-Chorus]
Performance:

[Chorus]
Performance:

[Verse 2]
Performance:

[Bridge]
Performance:

[Final Chorus]
Performance:
"""
    if spec.path == "03_writing/groove-humanization-audit.md":
        return header + """Decision: hold

Language:
Style:
Tempo / meter:
Master pocket:
Drum role:
Bass role:
Guitar role:
Keys / synth role:
Vocal-rhythm relationship:
Timing humanization:
Velocity humanization:
Articulation humanization:
Must not sound like:
Blockers:
Warnings:

## Groove Design

| field | value |
|---|---|
| verse feel | |
| pre feel | |
| chorus feel | |
| bridge feel | |
| kick | |
| snare | |
| hats / ride | |
| ghost notes | |
| fills | |
| cymbals | |
| bass/kick | |
| bass articulation | |
| playability | |

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Groove tags:
Instrument performance tags:
Rhythm-section blind test:
Exclude additions:
Repair route:

Generated by: tools/audit_music_groove_humanization.py
"""
    if spec.path == "03_writing/structure-brief.md":
        return header + """Project:
Language:
Genre:
Tempo / meter:
Target length:
Use case:
Core hook:
Narrative arc:
Emotional arc:
Highest energy section:
Highest tension section:
Must have:
Must avoid:
Exact structure required?:
If exact:
"""
    if spec.path == "03_writing/energy-map.md":
        return header + """| Section | Energy 1-9 | Tension 1-9 | Density | Vocal intensity | Width | Low-end |
|---|---:|---:|---|---|---|---|
| Intro | | | | | | |
| Verse 1 | | | | | | |
| Pre-Chorus | | | | | | |
| Chorus | | | | | | |
| Verse 2 | | | | | | |
| Chorus 2 | | | | | | |
| Bridge | | | | | | |
| Final Chorus | | | | | | |
| Outro | | | | | | |

Energy rule:
Where should the listener lean in:
Where should the listener feel release:
Where should the song breathe:
"""
    if spec.path == "03_writing/section-function-map.md":
        return header + """Intro:
- musical identity:
- lyric/vocal status:
- max length:

Verse 1:
- information:
- vocal posture:
- arrangement:

Pre-Chorus:
- tension method:
- lyric density:
- melodic direction:

Chorus:
- title hook:
- arrival method:
- repeatable element:

Verse 2:
- new information:
- new arrangement detail:
- what stays from Verse 1:

Bridge:
- contrast method:
- new perspective:
- return cue:

Final Chorus:
- what repeats:
- what develops:
- payoff:

Outro:
- ending logic:
- last sound:
"""
    if spec.path == "03_writing/contrast-continuity-matrix.md":
        return header + """Keep across song:
Change by section:
Never change:
Allowed surprise:
"""
    if spec.path == "03_writing/transition-cue-sheet.md":
        return header + """Intro -> Verse:
Verse -> Pre:
Pre -> Chorus:
Chorus -> Verse 2:
Verse 2 -> Pre 2:
Chorus 2 -> Bridge:
Bridge -> Final Chorus:
Final Chorus -> Outro:

Allowed cues:
Forbidden cues:
"""
    if spec.path == "03_writing/second-verse-development.md":
        return header + """New information:
New arrangement detail:
What stays from Verse 1:
What must not happen:
"""
    if spec.path == "03_writing/bridge-turn-plan.md":
        return header + """Before bridge, listener knows:
Bridge reveals:
Musical contrast:
Lyric contrast:
Return cue to final chorus:
Do not:
"""
    if spec.path == "03_writing/final-chorus-payoff.md":
        return header + """What repeats exactly:
What changes:
New layer:
Vocal payoff:
Mix payoff:
Final line:
Ending cue:
"""
    if spec.path == "03_writing/outro-end-plan.md":
        return header + """Ending logic:
Last sound:
Outro length:
Fade / stop / tag:
Do not:
"""
    if spec.path == "03_writing/structure-dynamics-audit.md":
        return header + """Decision: hold

Language:
Genre:
Tempo / meter:
Target length:
Use case:
Core hook:
Narrative arc:
Emotional arc:
Highest energy section:
Highest tension section:
Must have:
Must avoid:
Blockers:
Warnings:

## Structure Design

| field | value |
|---|---|
| energy rule | |
| lean in | |
| release | |
| breathe | |
| keep across song | |
| change by section | |
| never change | |
| verse 2 development | |
| bridge turn | |
| final chorus payoff | |
| outro | |
| critical transitions | |

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Structure tags:
Section tags:
Structure blind test:
Exclude additions:
Repair route:

Generated by: tools/audit_music_structure_dynamics.py
"""
    if spec.path == "03_writing/singer-brief.md":
        return header + """Song:
Language:
Narrator:
Vocal role:
Range / tessitura:
Register plan:
Timbre:
Diction:
Breath:
Vibrato / straight tone:
Dynamics:
Emotional restraint:
Must not sound like:
Rights source:
"""
    if spec.path == "03_writing/vocal-performance-map.md":
        return header + """[Verse 1]
Performance:

[Pre-Chorus]
Performance:

[Chorus]
Performance:

[Verse 2]
Performance:

[Bridge]
Performance:

[Final Chorus]
Performance:

[Outro]
Performance:
"""
    if spec.path == "03_writing/vocal-arrangement-map.md":
        return header + """Lead vocal:
Doubles:
Harmonies:
Ad-libs:
Duet / group vocal:
Lead center:
Do not:
"""
    if spec.path == "03_writing/vocal-identity-audit.md":
        return header + """Decision: hold

Song:
Language:
Narrator:
Vocal role:
Range / tessitura:
Register plan:
Timbre:
Diction:
Breath:
Vibrato / straight tone:
Dynamics:
Emotional restraint:
Human anchor lane:
Rights source:
Must not sound like:
Blockers:
Warnings:

## Vocal Design

| field | value |
|---|---|
| verse performance | |
| pre performance | |
| chorus performance | |
| verse 2 performance | |
| bridge performance | |
| final chorus performance | |
| outro performance | |
| lead plan | |
| doubles | |
| harmonies | |
| ad-libs | |
| group / duet | |
| lead center | |

## Findings

| severity | code | message | route |
|---|---|---|---|

## Prompt Routing

Vocal tags:
Vocal performance tags:
Vocal arrangement tags:
Vocal blind test:
Exclude additions:
Repair route:

Generated by: tools/audit_music_vocal_identity.py
"""
    if spec.path == "04_prompt/persona-voice-model-routing.md":
        return header + """Use identity feature:
Feature type:
Human anchor lane:
Voice identity source:
Persona source:
Custom Model source:
Custom model corpus:
Voice verification:
My Taste state:
My Taste summary:
Prompt boost state:
Boosted style text:
Source song / voice / dataset:
Rights status:
Catalog role:
Expected continuity:
Risk:
Do not use if:

Lane options:
- text-only
- human audio seed
- voice/persona
- custom model
- My Taste

Rules:
- Use text-only for quick exploration when no human seed exists.
- Use human audio seed only with audio-rights-ledger.md and retention-target.md.
- Use Voice / Persona only with voice-rights.md and singer/performance evidence.
- Use Custom Model only with owned corpus and catalog-memory evidence.
- Use My Taste / Prompt Boost only when original and boosted text are both recorded.
"""
    if spec.path == "04_prompt/retention-target.md":
        return header + """Seed file:
Tool:
Primary retention:
Retention level:
Strict keep:
Allowed transformations:
Must change:
Risk if over-retained:
Risk if under-retained:
Listening proof:
"""
    if spec.path == "04_prompt/prompt-pairing.md":
        return header + """Audio seed:
Seed type:
Retention target:
Style prompt:
Lyrics prompt:
Exclude:
Audio Influence:
Audio Strength:

## Pairing Rule

- Keep prompt language aligned with `04_prompt/retention-target.md`.
- Do not ask the model to copy every element if only one seed feature matters.
- Do not enter blind review until `tools/audit_music_audio_seed_retention.py` writes `06_review/audio-seed-retention-audit.md` with `Decision: pass`, unless no audio seed is used.
"""
    if spec.path == "05_generations/take-ledger.md":
        return header + """| take id | prompt package | provider/model | settings | source audio | persona/voice | first impression | known issue | review status |
|---|---|---|---|---|---|---|---|---|
| take-A01 | 04_prompt/prompt-package-v001.md | | | | | | | pending |
"""
    if spec.path == "05_generations/experiment-intent.md":
        return header + """Experiment question:
Success metric:
Stop condition:
Experiment phase:
- exploration
- convergence
- local repair

Attribution goal:
Next route if pass:
Next route if fail:
"""
    if spec.path == "05_generations/brief-freeze.md":
        return header + """Use case:
Language:
Audience:
Genre lane:
Artist / catalog lane:
Narrator:
Title phrase:
Tempo / groove:
Vocal identity:
Instrumentation:
Production space:
Must keep:
Must avoid:
Rights boundary:
"""
    if spec.path == "05_generations/variable-inventory.md":
        return header + """Changed variables:

| variable | allowed this round | reason | notes |
|---|---|---|---|
| Style prompt | no | | |
| Lyrics text | no | | |
| Lyrics context | no | | |
| Exclude | no | | |
| Model | no | | |
| Weirdness | no | | |
| Style Influence | no | | |
| Audio Influence | no | | |
| Persona / Voice | no | | |
| Audio Upload seed | no | | |

Rule: exploration allows at most two changed variables; convergence and local repair allow one.
"""
    if spec.path == "05_generations/prompt-candidate-set.md":
        return header + """Candidate ID: C01
Candidate type: baseline
Hypothesis:
What this tests:
What it keeps constant:
What it changes:
Risk:

## Candidate Matrix

| candidate id | type | hypothesis | changed variable | keeps constant | risk |
|---|---|---|---|---|---|
| C01 | baseline | | | | |

Boosted comparison:
"""
    if spec.path == "05_generations/batch-generation-plan.md":
        return header + """Candidate IDs:
Takes per candidate:
Total takes:
Generation date:
Expected listen order:
Anonymization rule:
Experiment phase:
Changed variables:

## Variable Discipline

| candidate | changed variable | keep fixed | reason | expected risk |
|---|---|---|---|---|

## Batch Guardrail

- Change one major variable per candidate.
- Run `tools/audit_music_prompt_iteration_discipline.py` before spending generation attempts or auditing generated takes.
- Do not continue to blind review until `tools/audit_music_generation_evidence.py` writes `05_generations/generation-evidence-audit.md` with `Decision: pass`.
"""
    if spec.path == "05_generations/provider-result-ledger.md":
        return header + """| take id | provider/model | settings | generated url | downloaded file | prompt package | metadata | status |
|---|---|---|---|---|---|---|---|
| take-A01 | | | | | 04_prompt/prompt-package-v001.md | | pending |
"""
    if spec.path == "05_generations/generation-evidence-audit.md":
        return header + """Decision: hold

## Generation Evidence

Prompt package: 04_prompt/prompt-package-v001.md
Prompt preflight: 04_prompt/prompt-preflight-review.md
Batch plan: 05_generations/batch-generation-plan.md
Take ledger: 05_generations/take-ledger.md
Provider result ledger: 05_generations/provider-result-ledger.md
Take provenance tags:
Batch tags:
Provider metadata tags:
Blind review handoff: blocked

Generated by: tools/audit_music_generation_evidence.py
"""
    if spec.path == "05_generations/prompt-iteration-discipline-audit.md":
        return header + """Generated by: tools/audit_music_prompt_iteration_discipline.py
Decision: hold

## Prompt Iteration Discipline Evidence

Experiment question:
Frozen brief:
Allowed variable count:
Changed variables:
Candidate hypotheses:
Batch discipline:
Attribution strength:
Generation evidence handoff: hold

## Findings

| severity | code | message | route |
|---|---|---|---|
| hold | not_generated | Run tools/audit_music_prompt_iteration_discipline.py before generation evidence | prompt-experiment |

## Next Route

- pass: run `tools/audit_music_generation_evidence.py` after generating/exporting takes.
- hold: reduce variables, freeze the brief, or rewrite candidate hypotheses before spending generation attempts.
"""
    if spec.path == "06_review/anchor-retention-review.md":
        return header + """Seed:
Hidden take IDs:

## Seed Retention

- melody:
- rhythm:
- harmony:
- vocal phrase:
- texture:
- arrangement:

## Scores

Seed identity:
Musical transformation:
Prosody fit:
Groove lock:
Vocal support:
Rights clarity:
Decision:
- keep
- repair
- reseed
- discard

Generated / updated by: tools/audit_music_audio_seed_retention.py
"""
    if spec.path == "06_review/audio-seed-retention-audit.md":
        return header + """Decision: not applicable

## Audio Seed Evidence

Human audio seed required: no
Seed rights tags: not applicable
Seed classification tags: not applicable
Retention target tags: not applicable
Prompt pairing tags: not applicable
Generation evidence: missing/incomplete
Anchor retention tags: not applicable
Blind review handoff: not applicable

Generated by: tools/audit_music_audio_seed_retention.py
"""
    if spec.path == "06_review/blind-review.md":
        return header + """## Blind Setup

Hidden prompt: yes/no
Anonymous files:

## Reverse Caption

| take | genre/scene | vocal | groove | arrangement | production | AI-flavor red flags |
|---|---|---|---|---|---|---|

## Scores

| take | alignment | preference | hook | vocal identity | groove | form | artifact risk | decision |
|---|---|---|---|---|---|---|---|
"""
    if spec.path == "06_review/take-selection-decision.md":
        return header + """## Decision

Best take:
Action:
Evidence status:
Missing score fields:
Composite score:
Core minimum:
Primary route:

## Ranking

| rank | take | evidence | missing score fields | composite | alignment | preference | hook | vocal identity | groove | form | artifact risk | action | route |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|

Generated / updated by: tools/review_music_takes.py
"""
    if spec.path == "06_review/release-listener-evidence-audit.md":
        return header + """Decision: hold

## Release Listener Evidence

Panel tags:
First 20 second tags:
Hook memory tags:
AI flavor tags:
Release gate handoff: blocked

Generated by: tools/audit_music_release_listener_evidence.py
"""
    if spec.path == "07_repair/repair-route-map.md":
        return header + """| problem | layer | severity | repair route | official Suno edit tool | expected output | regression listen |
|---|---|---|---|---|---|---|

Layer options: lyric, prosody, topline, harmony/bass, groove, structure, vocal identity, vocal recording, arrangement density, mix/post, AI artifacts, master/QC, rights, catalog.
Official Suno edit tool options: Song Editor / Replace Section, Edit Lyrics, Extend, Cover, Add Vocals, Reuse Prompt, Studio stems / DAW handoff, hold before edit.

Generated / updated by: tools/route_music_repairs.py
"""
    if spec.path == "07_repair/artifact-severity-score.md":
        return header + """## Score Table

| problem | layer | severity | evidence | route |
|---|---|---:|---|---|

Severity uses the 0-3 scale from AI 音乐 AI味伪影诊断与修复路由工作流.
Generated / updated by: tools/route_music_repairs.py
"""
    if spec.path == "07_repair/repair-log.md":
        return header + """Chosen take:
Take action:
Keep:
Reject / repair:
One thing to repair:
Repair tool:
Official Suno edit tool:
Tool action:
Expected improvement:
Suno regression check:
Result:
Next action:

Generated / updated by: tools/route_music_repairs.py
"""
    if spec.path == "07_repair/regression-listen.md":
        return header + """Original issue:
Repair action:
Official Suno edit tool:
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

Generated / updated by: tools/route_music_repairs.py
"""
    if spec.path == "08_stems-daw/best-take-lock.md":
        return header + """Locked take:
Take action:
Source provider/model:
Prompt package:

## Must Preserve

- title phrase / chorus hook
- vocal identity direction
- drums-bass pocket direction

## May Replace

- lead vocal
- drums / bass
- artifact-heavy stems

Generated / updated by: tools/prepare_music_daw_handoff.py
"""
    if spec.path == "08_stems-daw/session-pack.md":
        return header + """## Required Files

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
what to rerecord:
what to keep from AI:
known artifacts:
human contribution plan:

Generated / updated by: tools/prepare_music_daw_handoff.py
"""
    if spec.path == "10_mix-master/post-production-mix-lock-audit.md":
        return header + """Generated by: tools/audit_music_post_production_mix_lock.py
Decision: hold

## Post Production Mix Lock Evidence

Locked take:
Arrangement density tags:
Vocal center:
Low-end/kick-bass:
Space/dynamics automation:
Transition/outro:
AI artifact repair:
Stem/DAW handoff:
Reference A/B:
Mix lock handoff: hold

## Findings

| severity | code | message | route |
|---|---|---|---|
| hold | not_generated | Run tools/audit_music_post_production_mix_lock.py before release listener and release rights | post-production |

## Release Routing

- pass: run release-listener evidence and release-candidate gates.
- hold: repair the named post-production layer before audio QC, listener release tests, or rights packaging.
"""
    if spec.path == "10_mix-master/release-audio-technical-inspection.md":
        return header + """Decision: hold

## WAV Inspection

- release candidate audio:
- duration:
- sample rate:
- bit depth:
- channels:
- peak:
- RMS:
- clipped sample ratio:

Generated / updated by: tools/inspect_music_release_audio.py
"""
    if spec.path == "10_mix-master/release-audio-qc-report.md":
        return header + """Decision: hold

## Required Evidence

- release-audio-technical-inspection.md:
- loudness-true-peak-report.md:
- codec-preview.md:
- translation-listen-matrix.md:
- mono-phase-low-end-check.md:
- transient-and-limiter-audit.md:

## Measurements

- integrated LUFS:
- LRA:
- True Peak:
- clipped samples:
- sample rate:
- bit depth:

## Listening

- loudness-matched reference A/B:
- codec preview:
- translation matrix:
- mono/phase:
- low end:
- intro/outro:

## AI Artifact Check

- vocal tail:
- cymbals:
- backing vocal smear:
- stem bleed:
- over-limiting:

Generated / updated by: tools/prepare_music_release_audio_qc.py
"""
    if spec.path == "11_release/release-candidate-rights-gate.md":
        return header + """## Release Gate

Decision: hold

Do not publish if any item is unresolved:

- prompt-package-v001.md or prompt-preflight-review.md is missing, stale, or not approved
- source-rights-ledger.md has unknown source or permission
- subscription-and-generation-context.md is incomplete
- human-contribution-ledger.md is incomplete
- ai-use-disclosure.md is unresolved
- voice rights are unclear
- reference similarity risk is unresolved
- release-audio-technical-inspection.md is missing or hold
- release-audio-qc-report.md has red flags
- external listener feedback flags AI flavor or weak hook memory
- release_candidate/audio/ has no final master file

Generated / updated by: tools/prepare_music_release_candidate.py

## Notes
"""
    if spec.path == "11_release/release-candidate-evidence-audit.md":
        return header + """## Required Evidence

- release-intent.md
- prompt-package-v001.md
- prompt-preflight-review.md
- source-rights-ledger.md
- subscription-and-generation-context.md
- human-contribution-ledger.md
- copyrightability-notes.md
- similarity-and-impersonation-review.md
- platform-distribution-matrix.md
- ai-use-disclosure.md
- anti-spam-release-policy.md
- distributor-preflight.md
- release-audio-technical-inspection.md
- release-audio-qc-report.md
- external-listener-panel.md

Generated / updated by: tools/prepare_music_release_candidate.py
"""
    if spec.path == "11_release/release-candidate-package.md":
        return header + """## Required Package

- release_candidate/audio/
- release_candidate/metadata/release-candidate-manifest.md
- prompt-package-v001.md
- prompt-preflight-review.md
- release-candidate-evidence-audit.md
- release-candidate-rights-gate.md
- release-audio-technical-inspection.md
- release-audio-qc-report.md
- source-rights-ledger.md
- human-contribution-ledger.md
- ai-use-disclosure.md

Generated / updated by: tools/prepare_music_release_candidate.py
"""
    if spec.path == "11_release/release-rights-link.md":
        return header + """Human audio seed used:
audio-rights-ledger.md:
retention-target.md:
audio-seed-retention-audit.md:
human-contribution-ledger.md:
source-rights-ledger.md:
Release implication:
Disclosure implication:
Reviewer:
Decision:
"""
    if spec.path == "11_release/release_candidate/metadata/release-candidate-manifest.md":
        return header + """## Files

- audio:
- artwork:
- metadata:
- evidence:

Generated / updated by: tools/prepare_music_release_candidate.py
"""
    if spec.path == "12_catalog-memory/catalog-seed-hygiene.md":
        return header + """Human audio seed used:
Reusable as catalog seed:
Allowed reuse:
Forbidden reuse:
Requires new consent before:
Voice / Persona / Custom Model boundary:
Inspire / My Taste boundary:
Linked audio-seed-retention-audit.md:
Decision:

Generated / updated by: tools/prepare_music_catalog_memory.py
"""
    if spec.path == "12_catalog-memory/catalog-memory-update.md":
        return header + """Song:
Locked take:
Release decision:
Catalog promotion:

## What Worked

- lyric:
- topline:
- groove:
- vocal:
- arrangement:
- production:

## What Failed Or Needed Control

-

Generated / updated by: tools/prepare_music_catalog_memory.py
"""
    if spec.path == "12_catalog-memory/postmortem-and-prompt-memory.md":
        return header + """## Evidence Links

- 04_prompt/prompt-package-v001.md
- 05_generations/take-ledger.md
- 06_review/take-selection-decision.md
- 07_repair/repair-route-map.md
- 11_release/release-candidate-rights-gate.md
- 12_catalog-memory/catalog-memory-update.md

## Producer Postmortem

- Best decision:
- Worst default:
- Biggest AI-flavor risk:
- One rule to reuse:
- One rule to ban:

Generated / updated by: tools/prepare_music_catalog_memory.py
"""
    if spec.path == "12_catalog-memory/next-song-brief-seed.md":
        return header + """## Next Song Should Preserve

- artist promise:
- vocal identity:
- strongest hook mechanism:
- production space:

## Next Song Should Change

- title image:
- tempo or groove:
- verse situation:
- arrangement role:

## Do Not Repeat

- unresolved repair route:
- reference similarity:
- release gate blocker:

Generated / updated by: tools/prepare_music_catalog_memory.py
"""
    if spec.path == "12_catalog-memory/catalog-writeback-manifest.md":
        return header + """## Files

- catalog-memory-update.md
- prompt-memory-update.md
- artifact-memory-update.md
- sonic-signature-update.md
- lyric-universe-update.md
- reference-boundary-update.md
- postmortem-and-prompt-memory.md
- next-song-brief-seed.md

Generated / updated by: tools/prepare_music_catalog_memory.py
"""
    return header + f"""## Role

{spec.role}

## Gate

{spec.gate}

## Fill In

- Current status:
- Evidence:
- Decision:
- Next action:
- Linked files:

## Notes
"""


def write_project(root: Path, args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    root.mkdir(parents=True, exist_ok=True)
    for rel_dir in DIRS:
        (root / rel_dir).mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    skipped: list[Path] = []
    for spec in FILE_SPECS:
        path = root / spec.path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            skipped.append(path)
            continue
        path.write_text(render_file(spec, args), encoding="utf-8")
        written.append(path)
    return written, skipped


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="Parent directory for the generated song project.")
    parser.add_argument("--title", required=True, help="Song title or working title.")
    parser.add_argument("--language", default="zh", help="Language lane, e.g. zh, jp, kr, en.")
    parser.add_argument("--lane", default="pop", help="Music lane, e.g. pop, rock, rnb, dance-pop.")
    parser.add_argument("--slug", default="", help="ASCII slug for the project directory. Defaults to title-derived slug.")
    parser.add_argument("--artist-project", default="", help="Artist, catalog, or project identity.")
    parser.add_argument("--use-case", default="demo", help="demo, release-single, EP, client, experiment, etc.")
    parser.add_argument("--date", default=today_stamp(), help="Project start date as YYYYMMDD or YYYY-MM-DD.")
    parser.add_argument("--allow-existing", action="store_true", help="Allow filling missing files in an existing project directory.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        args.project_dir_name = project_dir_name(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    root = output_dir / args.project_dir_name
    if root.exists() and any(root.iterdir()) and not args.allow_existing:
        print(f"error: project directory already exists and is not empty: {root}", file=sys.stderr)
        print("use --allow-existing to fill missing scaffold files without overwriting existing files", file=sys.stderr)
        return 2

    written, skipped = write_project(root, args)
    print(f"created project: {root}")
    print(f"written files: {len(written)}")
    print(f"skipped existing files: {len(skipped)}")
    print("next: fill 00_admin/song-production-control-board.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
