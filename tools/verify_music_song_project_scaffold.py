#!/usr/bin/env python3
"""Verify the AI music song-project scaffold CLI."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCRIPT = ROOT / "tools" / "create_music_song_project.py"
WIKI_PAGE = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")

EXPECTED_DIR = "20260624_zh-pop_night-bus"
EXPECTED_FILES = [
    "README.md",
    "00_admin/song-production-control-board.md",
    "00_admin/project-status-audit.md",
    "00_admin/next-action.md",
    "00_admin/file-manifest.md",
    "01_brief/song-brief.md",
    "01_brief/catalog-fit-audit.md",
    "02_references/source-rights-ledger.md",
    "02_references/human-seed-intent.md",
    "02_references/audio-rights-ledger.md",
    "02_references/seed-type-classification.md",
    "02_references/capture-and-cleanup.md",
    "02_references/reference-dna-audit.md",
    "03_writing/lyric-brief.md",
    "03_writing/lyric-narrative-audit.md",
    "03_writing/lyrics-prosody-audit.md",
    "04_prompt/methodology-transfer-plan.md",
    "04_prompt/methodology-transfer-audit.md",
    "04_prompt/field-length-and-specificity-budget.md",
    "04_prompt/prompt-specificity-budget-audit.md",
    "04_prompt/genre-lane-authenticity-audit.md",
    "04_prompt/persona-voice-model-routing.md",
    "04_prompt/personalization-state.md",
    "04_prompt/personalization-hygiene-audit.md",
    "04_prompt/retention-target.md",
    "04_prompt/prompt-pairing.md",
    "03_writing/topline-hook-audit.md",
    "03_writing/harmonic-rhythm-map.md",
    "03_writing/cadence-and-bridge-plan.md",
    "03_writing/harmony-bass-audit.md",
    "03_writing/drum-realism-map.md",
    "03_writing/instrument-role-map.md",
    "03_writing/section-performance-map.md",
    "03_writing/groove-humanization-audit.md",
    "03_writing/section-function-map.md",
    "03_writing/contrast-continuity-matrix.md",
    "03_writing/transition-cue-sheet.md",
    "03_writing/second-verse-development.md",
    "03_writing/bridge-turn-plan.md",
    "03_writing/final-chorus-payoff.md",
    "03_writing/outro-end-plan.md",
    "03_writing/structure-dynamics-audit.md",
    "03_writing/vocal-performance-map.md",
    "03_writing/vocal-arrangement-map.md",
    "03_writing/vocal-identity-audit.md",
    "04_prompt/external-method-claim-ledger.md",
    "04_prompt/external-method-claim-audit.md",
    "04_prompt/prompt-package-v001.md",
    "04_prompt/prompt-preflight-review.md",
    "05_generations/experiment-intent.md",
    "05_generations/brief-freeze.md",
    "05_generations/variable-inventory.md",
    "05_generations/prompt-candidate-set.md",
    "05_generations/prompt-iteration-discipline-audit.md",
    "05_generations/take-ledger.md",
    "05_generations/generation-evidence-audit.md",
    "06_review/anchor-retention-review.md",
    "06_review/audio-seed-retention-audit.md",
    "06_review/release-listener-evidence-audit.md",
    "06_review/blind-review.md",
    "06_review/take-selection-decision.md",
    "07_repair/repair-route-map.md",
    "08_stems-daw/session-pack.md",
    "08_stems-daw/daw-handoff-intent.md",
    "08_stems-daw/human-contribution-and-rights-link.md",
    "09_vocal/voice-rights.md",
    "10_mix-master/post-production-mix-lock-audit.md",
    "10_mix-master/release-audio-technical-inspection.md",
    "10_mix-master/release-audio-qc-report.md",
    "11_release/similarity-and-impersonation-review.md",
    "11_release/release-rights-link.md",
    "11_release/platform-distribution-matrix.md",
    "11_release/anti-spam-release-policy.md",
    "11_release/release-candidate-evidence-audit.md",
    "11_release/release-candidate-rights-gate.md",
    "11_release/release-candidate-package.md",
    "11_release/post-release-monitoring.md",
    "11_release/release_candidate/metadata/release-candidate-manifest.md",
    "12_catalog-memory/catalog-seed-hygiene.md",
    "12_catalog-memory/next-song-brief-seed.md",
    "12_catalog-memory/catalog-writeback-manifest.md",
    "12_catalog-memory/postmortem-and-prompt-memory.md",
]

EXPECTED_DIRS = [
    "05_generations/audio",
    "05_generations/metadata",
    "10_mix-master/masters",
    "11_release/release_candidate/audio",
    "11_release/release_candidate/artwork",
    "11_release/release_candidate/metadata",
]


def main() -> int:
    errors: list[str] = []

    if not SCRIPT.exists():
        errors.append(f"missing scaffold script: {SCRIPT}")
    if not WIKI_PAGE.exists():
        errors.append(f"missing wiki page: {WIKI_PAGE}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-scaffold-") as tmp:
        tmp_path = Path(tmp)
        cmd = [
            sys.executable,
            str(SCRIPT),
            "--output-dir",
            str(tmp_path),
            "--date",
            "20260624",
            "--language",
            "zh",
            "--lane",
            "pop",
            "--slug",
            "night-bus",
            "--title",
            "Night Bus",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "demo",
        ]
        first = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if first.returncode != 0:
            errors.append(f"scaffold command failed: {first.stderr.strip()}")
        project = tmp_path / EXPECTED_DIR
        if not project.exists():
            errors.append(f"expected project directory missing: {project}")
        else:
            for rel in EXPECTED_FILES:
                if not (project / rel).is_file():
                    errors.append(f"missing scaffold file: {rel}")
            for rel in EXPECTED_DIRS:
                if not (project / rel).is_dir():
                    errors.append(f"missing scaffold directory: {rel}")

            manifest = (project / "00_admin" / "file-manifest.md").read_text(encoding="utf-8")
            for rel in ["00_admin/project-status-audit.md", "01_brief/catalog-fit-audit.md", "02_references/audio-rights-ledger.md", "03_writing/lyric-narrative-audit.md", "03_writing/lyrics-prosody-audit.md", "03_writing/topline-hook-audit.md", "03_writing/harmony-bass-audit.md", "03_writing/groove-humanization-audit.md", "04_prompt/external-method-claim-ledger.md", "04_prompt/external-method-claim-audit.md", "04_prompt/methodology-transfer-plan.md", "04_prompt/methodology-transfer-audit.md", "04_prompt/field-length-and-specificity-budget.md", "04_prompt/prompt-specificity-budget-audit.md", "04_prompt/genre-lane-authenticity-audit.md", "04_prompt/personalization-state.md", "04_prompt/personalization-hygiene-audit.md", "04_prompt/prompt-package-v001.md", "04_prompt/retention-target.md", "05_generations/experiment-intent.md", "05_generations/brief-freeze.md", "05_generations/variable-inventory.md", "05_generations/prompt-candidate-set.md", "05_generations/prompt-iteration-discipline-audit.md", "05_generations/take-ledger.md", "05_generations/generation-evidence-audit.md", "06_review/audio-seed-retention-audit.md", "06_review/release-listener-evidence-audit.md", "10_mix-master/post-production-mix-lock-audit.md", "10_mix-master/release-audio-technical-inspection.md", "11_release/release-candidate-rights-gate.md", "11_release/release-candidate-package.md", "12_catalog-memory/next-song-brief-seed.md"]:
                if rel not in manifest:
                    errors.append(f"manifest missing: {rel}")

            control = (project / "00_admin" / "song-production-control-board.md").read_text(encoding="utf-8")
            for term in ["Song Production Control Board", "tools/audit_music_song_project_status.py", "Current stage", "Next command"]:
                if term not in control:
                    errors.append(f"control board missing term: {term}")
            if "methodology-transfer-gate" not in control:
                errors.append("control board should start at methodology-transfer-gate")

            catalog_fit_audit = (project / "01_brief" / "catalog-fit-audit.md").read_text(encoding="utf-8")
            for term in ["Catalog Fit Audit", "tools/audit_music_catalog_fit.py", "Decision: hold", "Artist/catalog fit", "Catalog evolution", "Prompt handoff", "Catalog memory handoff"]:
                if term not in catalog_fit_audit:
                    errors.append(f"catalog-fit audit scaffold missing term: {term}")

            methodology_plan = (project / "04_prompt" / "methodology-transfer-plan.md").read_text(encoding="utf-8")
            for term in ["Local method sources", "Official control surfaces", "Community / external candidates", "Source confidence split", "Model/version rationale", "Primary Suno tool route", "Human-likeness hypothesis", "Rejected magic prompt claims", "Protected-identity safeguard", "Drift/rollback condition"]:
                if term not in methodology_plan:
                    errors.append(f"methodology transfer plan missing term: {term}")

            external_claim_audit = (project / "04_prompt" / "external-method-claim-audit.md").read_text(encoding="utf-8")
            for term in ["External Method Claim Audit", "tools/audit_music_external_method_claims.py", "Decision: hold", "External method claims", "Official/local foundations", "Community candidates", "Methodology transfer handoff"]:
                if term not in external_claim_audit:
                    errors.append(f"external method claim audit scaffold missing term: {term}")

            methodology_audit = (project / "04_prompt" / "methodology-transfer-audit.md").read_text(encoding="utf-8")
            for term in ["Methodology Transfer Audit", "tools/audit_music_methodology_transfer.py", "Decision: hold", "Local source root", "External method claims", "Source confidence split", "Official control surfaces", "Human-likeness transfer", "Variable discipline"]:
                if term not in methodology_audit:
                    errors.append(f"methodology transfer audit scaffold missing term: {term}")

            budget = (project / "04_prompt" / "field-length-and-specificity-budget.md").read_text(encoding="utf-8")
            for term in ["Must-hear terms", "Remove vague terms", "Move to Lyrics context", "Move to Exclude", "Field budget decision", "Source / rationale", "realism-descriptors.md"]:
                if term not in budget:
                    errors.append(f"specificity budget scaffold missing term: {term}")

            specificity_audit = (project / "04_prompt" / "prompt-specificity-budget-audit.md").read_text(encoding="utf-8")
            for term in ["Prompt Specificity Budget Audit", "tools/audit_music_prompt_specificity_budget.py", "Decision: hold", "Style specificity tags", "Recording realism tags", "Performance realism tags", "Prompt compile handoff"]:
                if term not in specificity_audit:
                    errors.append(f"specificity audit scaffold missing term: {term}")

            genre_lane_audit = (project / "04_prompt" / "genre-lane-authenticity-audit.md").read_text(encoding="utf-8")
            for term in ["Genre Lane Authenticity Audit", "tools/audit_music_genre_lane_authenticity.py", "Decision: hold", "Primary lane", "Style-lyric fit", "Genre/lane authenticity", "Prompt compile handoff"]:
                if term not in genre_lane_audit:
                    errors.append(f"genre-lane authenticity audit scaffold missing term: {term}")

            prompt = (project / "04_prompt" / "prompt-package-v001.md").read_text(encoding="utf-8")
            for term in ["Style Of Music", "Lyrics", "Prompt Rationale", "Weirdness", "Style Influence", "Audio Influence", "Human Anchor Lane", "My Taste State", "Custom Model Corpus"]:
                if term not in prompt:
                    errors.append(f"prompt package missing term: {term}")

            identity = (project / "04_prompt" / "persona-voice-model-routing.md").read_text(encoding="utf-8")
            for term in ["Human anchor lane", "Voice identity source", "Custom Model source", "Custom model corpus", "My Taste state", "Prompt boost state", "Lane options"]:
                if term not in identity:
                    errors.append(f"persona/voice routing missing term: {term}")

            personalization_state = (project / "04_prompt" / "personalization-state.md").read_text(encoding="utf-8")
            for term in ["Active personalization features", "Account / profile scope", "Source / rights evidence", "Catalog fit link", "Isolation boundary", "Attribution plan", "Rollback condition", "Prompt Boost state", "Original style text", "Boosted style text"]:
                if term not in personalization_state:
                    errors.append(f"personalization-state scaffold missing term: {term}")

            personalization_audit = (project / "04_prompt" / "personalization-hygiene-audit.md").read_text(encoding="utf-8")
            for term in ["Personalization Hygiene Audit", "tools/audit_music_personalization_hygiene.py", "Decision: not applicable", "Personalization hygiene", "Prompt compile handoff"]:
                if term not in personalization_audit:
                    errors.append(f"personalization-hygiene audit scaffold missing term: {term}")

            reference_audit = (project / "02_references" / "reference-dna-audit.md").read_text(encoding="utf-8")
            for term in ["Reference DNA Audit", "tools/audit_music_reference_dna.py", "Decision: hold", "Reference tags", "Style DNA tags", "Protected identity removal", "Similarity blind test"]:
                if term not in reference_audit:
                    errors.append(f"reference-dna audit scaffold missing term: {term}")

            lyric_narrative_audit = (project / "03_writing" / "lyric-narrative-audit.md").read_text(encoding="utf-8")
            for term in ["Lyric Narrative Audit", "tools/audit_music_lyric_narrative.py", "Decision: hold", "Narrator/situation tags", "Concrete image tags", "Title phrase function", "Central metaphor", "Section information tags", "Cliche removal", "Lyrics rewrite handoff"]:
                if term not in lyric_narrative_audit:
                    errors.append(f"lyric-narrative audit scaffold missing term: {term}")

            prosody_audit = (project / "03_writing" / "lyrics-prosody-audit.md").read_text(encoding="utf-8")
            for term in ["Lyrics Prosody Audit", "tools/audit_music_lyrics_prosody.py", "Decision: hold", "Lyrics tags", "Blind-listening red flags"]:
                if term not in prosody_audit:
                    errors.append(f"lyrics-prosody audit scaffold missing term: {term}")

            topline_audit = (project / "03_writing" / "topline-hook-audit.md").read_text(encoding="utf-8")
            for term in ["Topline Hook Audit", "tools/audit_music_topline_hook.py", "Decision: hold", "Topline tags", "Blind hook test"]:
                if term not in topline_audit:
                    errors.append(f"topline-hook audit scaffold missing term: {term}")

            harmony_audit = (project / "03_writing" / "harmony-bass-audit.md").read_text(encoding="utf-8")
            for term in ["Harmony Bass Audit", "tools/audit_music_harmony_bass.py", "Decision: hold", "Harmony tags", "Bass tags", "Topline/harmony fit"]:
                if term not in harmony_audit:
                    errors.append(f"harmony-bass audit scaffold missing term: {term}")

            groove_audit = (project / "03_writing" / "groove-humanization-audit.md").read_text(encoding="utf-8")
            for term in ["Groove Humanization Audit", "tools/audit_music_groove_humanization.py", "Decision: hold", "Groove tags", "Instrument performance tags", "Rhythm-section blind test"]:
                if term not in groove_audit:
                    errors.append(f"groove-humanization audit scaffold missing term: {term}")

            structure_audit = (project / "03_writing" / "structure-dynamics-audit.md").read_text(encoding="utf-8")
            for term in ["Structure Dynamics Audit", "tools/audit_music_structure_dynamics.py", "Decision: hold", "Structure tags", "Section tags", "Structure blind test"]:
                if term not in structure_audit:
                    errors.append(f"structure-dynamics audit scaffold missing term: {term}")

            vocal_audit = (project / "03_writing" / "vocal-identity-audit.md").read_text(encoding="utf-8")
            for term in ["Vocal Identity Performance Audit", "tools/audit_music_vocal_identity.py", "Decision: hold", "Vocal tags", "Vocal performance tags", "Vocal arrangement tags", "Vocal blind test"]:
                if term not in vocal_audit:
                    errors.append(f"vocal-identity audit scaffold missing term: {term}")

            rights_gate = (project / "11_release" / "release-candidate-rights-gate.md").read_text(encoding="utf-8")
            for term in ["Do not publish", "prompt-package-v001.md", "prompt-preflight-review.md", "source-rights-ledger.md", "release-audio-technical-inspection.md", "release-audio-qc-report.md", "tools/prepare_music_release_candidate.py"]:
                if term not in rights_gate:
                    errors.append(f"release gate missing term: {term}")

            technical = (project / "10_mix-master" / "release-audio-technical-inspection.md").read_text(encoding="utf-8")
            for term in ["Release Audio Technical Inspection", "tools/inspect_music_release_audio.py", "clipped sample ratio"]:
                if term not in technical:
                    errors.append(f"technical inspection scaffold missing term: {term}")

            release_package = (project / "11_release" / "release-candidate-package.md").read_text(encoding="utf-8")
            for term in ["Release Candidate Package", "release-candidate-evidence-audit.md", "release-candidate-rights-gate.md", "tools/prepare_music_release_candidate.py"]:
                if term not in release_package:
                    errors.append(f"release package missing term: {term}")

            decision = (project / "06_review" / "take-selection-decision.md").read_text(encoding="utf-8")
            for term in ["Take Selection Decision", "Best take", "tools/review_music_takes.py"]:
                if term not in decision:
                    errors.append(f"take-selection decision missing term: {term}")

            generation_audit = (project / "05_generations" / "generation-evidence-audit.md").read_text(encoding="utf-8")
            for term in ["Generation Evidence Audit", "tools/audit_music_generation_evidence.py", "Decision: hold", "Take provenance tags", "Batch tags", "Provider metadata tags", "Blind review handoff"]:
                if term not in generation_audit:
                    errors.append(f"generation evidence audit scaffold missing term: {term}")

            prompt_iteration_audit = (project / "05_generations" / "prompt-iteration-discipline-audit.md").read_text(encoding="utf-8")
            for term in ["Prompt Iteration Discipline Audit", "tools/audit_music_prompt_iteration_discipline.py", "Decision: hold", "Experiment question", "Changed variables", "Attribution strength", "Generation evidence handoff"]:
                if term not in prompt_iteration_audit:
                    errors.append(f"prompt iteration discipline audit scaffold missing term: {term}")

            audio_seed_audit = (project / "06_review" / "audio-seed-retention-audit.md").read_text(encoding="utf-8")
            for term in ["Audio Seed Retention Audit", "tools/audit_music_audio_seed_retention.py", "Decision: not applicable", "Seed rights tags", "Retention target tags", "Prompt pairing tags", "Anchor retention tags", "Blind review handoff"]:
                if term not in audio_seed_audit:
                    errors.append(f"audio seed retention audit scaffold missing term: {term}")

            release_listener_audit = (project / "06_review" / "release-listener-evidence-audit.md").read_text(encoding="utf-8")
            for term in ["Release Listener Evidence Audit", "tools/audit_music_release_listener_evidence.py", "Decision: hold", "Panel tags", "First 20 second tags", "Hook memory tags", "AI flavor tags", "Release gate handoff"]:
                if term not in release_listener_audit:
                    errors.append(f"release listener evidence audit scaffold missing term: {term}")

            retention_target = (project / "04_prompt" / "retention-target.md").read_text(encoding="utf-8")
            for term in ["Seed file", "Primary retention", "Strict keep", "Listening proof"]:
                if term not in retention_target:
                    errors.append(f"retention-target scaffold missing term: {term}")

            prompt_pairing = (project / "04_prompt" / "prompt-pairing.md").read_text(encoding="utf-8")
            for term in ["Audio seed", "Retention target", "Audio Influence", "tools/audit_music_audio_seed_retention.py"]:
                if term not in prompt_pairing:
                    errors.append(f"prompt-pairing scaffold missing term: {term}")

            repair_route = (project / "07_repair" / "repair-route-map.md").read_text(encoding="utf-8")
            for term in ["repair route", "tools/route_music_repairs.py"]:
                if term not in repair_route:
                    errors.append(f"repair-route map missing term: {term}")

            session_pack = (project / "08_stems-daw" / "session-pack.md").read_text(encoding="utf-8")
            for term in ["Session Pack", "daw-handoff-intent.md", "human-contribution-and-rights-link.md", "tools/prepare_music_daw_handoff.py"]:
                if term not in session_pack:
                    errors.append(f"session pack missing term: {term}")

            post_mix_lock = (project / "10_mix-master" / "post-production-mix-lock-audit.md").read_text(encoding="utf-8")
            for term in ["Post Production Mix Lock Audit", "tools/audit_music_post_production_mix_lock.py", "Decision: hold", "Arrangement density tags", "Low-end/kick-bass", "Mix lock handoff"]:
                if term not in post_mix_lock:
                    errors.append(f"post-production mix-lock scaffold missing term: {term}")

            postmortem = (project / "12_catalog-memory" / "postmortem-and-prompt-memory.md").read_text(encoding="utf-8")
            for term in ["Postmortem", "catalog-memory-update.md", "tools/prepare_music_catalog_memory.py"]:
                if term not in postmortem:
                    errors.append(f"catalog postmortem missing term: {term}")

        second = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if second.returncode == 0:
            errors.append("scaffold should refuse existing non-empty project without --allow-existing")

        fill = subprocess.run(cmd + ["--allow-existing"], cwd=ROOT, text=True, capture_output=True)
        if fill.returncode != 0:
            errors.append(f"scaffold --allow-existing failed: {fill.stderr.strip()}")

    wiki = WIKI_PAGE.read_text(encoding="utf-8")
    for term in [
        "tools/create_music_song_project.py",
        "tools/verify_music_song_project_scaffold.py",
        "--output-dir",
        "--allow-existing",
        "tools/audit_music_song_project_status.py",
        "project-status-audit.md",
        "catalog-fit-audit.md",
        "tools/audit_music_catalog_fit.py",
        "external-method-claim-ledger.md",
        "external-method-claim-audit.md",
        "tools/audit_music_external_method_claims.py",
        "reference-dna-audit.md",
        "tools/audit_music_reference_dna.py",
        "lyrics-prosody-audit.md",
        "tools/audit_music_lyrics_prosody.py",
        "lyric-narrative-audit.md",
        "tools/audit_music_lyric_narrative.py",
        "topline-hook-audit.md",
        "tools/audit_music_topline_hook.py",
        "harmony-bass-audit.md",
        "tools/audit_music_harmony_bass.py",
        "groove-humanization-audit.md",
        "tools/audit_music_groove_humanization.py",
        "structure-dynamics-audit.md",
        "tools/audit_music_structure_dynamics.py",
        "vocal-identity-audit.md",
        "tools/audit_music_vocal_identity.py",
        "persona-voice-model-routing.md",
        "Human Anchor",
        "field-length-and-specificity-budget.md",
        "prompt-specificity-budget-audit.md",
        "tools/audit_music_prompt_specificity_budget.py",
        "genre-lane-authenticity-audit.md",
        "tools/audit_music_genre_lane_authenticity.py",
        "Genre/lane authenticity",
        "personalization-state.md",
        "personalization-hygiene-audit.md",
        "tools/audit_music_personalization_hygiene.py",
        "tools/prepare_music_release_candidate.py",
        "tools/inspect_music_release_audio.py",
        "release-audio-technical-inspection.md",
        "release-candidate-package.md",
        "tools/prepare_music_catalog_memory.py",
        "next-song-brief-seed.md",
        "generation-evidence-audit.md",
        "tools/audit_music_generation_evidence.py",
        "experiment-intent.md",
        "brief-freeze.md",
        "variable-inventory.md",
        "prompt-candidate-set.md",
        "prompt-iteration-discipline-audit.md",
        "tools/audit_music_prompt_iteration_discipline.py",
        "tools/audit_music_audio_seed_retention.py",
        "audio-seed-retention-audit.md",
        "tools/audit_music_release_listener_evidence.py",
        "release-listener-evidence-audit.md",
        "post-production-mix-lock-audit.md",
        "tools/audit_music_post_production_mix_lock.py",
        "audio-rights-ledger.md",
        "retention-target.md",
        "prompt-pairing.md",
    ]:
        if term not in wiki:
            errors.append(f"wiki page missing scaffold tool term: {term}")

    log_text = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    if "AI 音乐单曲项目脚手架工具" not in log_text:
        errors.append("wiki log missing scaffold tool entry")

    if errors:
        print("AI music song project scaffold verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music song project scaffold verification passed.")
    print(f"script: {SCRIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
