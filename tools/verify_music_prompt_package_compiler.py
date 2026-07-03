#!/usr/bin/env python3
"""Verify the AI music prompt package compiler CLI."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path("/path/to/suno-music-producer")
SCAFFOLD = ROOT / "tools" / "create_music_song_project.py"
COMPILER = ROOT / "tools" / "compile_music_prompt_package.py"
METHODOLOGY_AUDIT = ROOT / "tools" / "audit_music_methodology_transfer.py"
EXTERNAL_METHOD_CLAIM_AUDIT = ROOT / "tools" / "audit_music_external_method_claims.py"
SPECIFICITY_AUDIT = ROOT / "tools" / "audit_music_prompt_specificity_budget.py"
GENRE_LANE_AUDIT = ROOT / "tools" / "audit_music_genre_lane_authenticity.py"
LYRIC_NARRATIVE_AUDIT = ROOT / "tools" / "audit_music_lyric_narrative.py"
REFERENCE_AUDIT = ROOT / "tools" / "audit_music_reference_dna.py"
PROSODY_AUDIT = ROOT / "tools" / "audit_music_lyrics_prosody.py"
TOPLINE_AUDIT = ROOT / "tools" / "audit_music_topline_hook.py"
HARMONY_AUDIT = ROOT / "tools" / "audit_music_harmony_bass.py"
GROOVE_AUDIT = ROOT / "tools" / "audit_music_groove_humanization.py"
STRUCTURE_AUDIT = ROOT / "tools" / "audit_music_structure_dynamics.py"
VOCAL_AUDIT = ROOT / "tools" / "audit_music_vocal_identity.py"
WIKI_PROMPT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐 Prompt 编译与生成前预检工作流.md")
WIKI_PROJECT = Path("/path/to/obsidian-vault/wiki/分析/音乐/AI 音乐单曲项目文件夹与证据包模板.md")
LOG = Path("/path/to/obsidian-vault/wiki/log.md")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    for path in [SCAFFOLD, COMPILER, EXTERNAL_METHOD_CLAIM_AUDIT, METHODOLOGY_AUDIT, SPECIFICITY_AUDIT, LYRIC_NARRATIVE_AUDIT, REFERENCE_AUDIT, PROSODY_AUDIT, TOPLINE_AUDIT, HARMONY_AUDIT, GROOVE_AUDIT, STRUCTURE_AUDIT, VOCAL_AUDIT, WIKI_PROMPT, WIKI_PROJECT, LOG]:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ai-music-prompt-compiler-") as tmp:
        tmp_path = Path(tmp)
        scaffold_cmd = [
            sys.executable,
            str(SCAFFOLD),
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
            "Night Bus Confession",
            "--artist-project",
            "Example Test Artist",
            "--use-case",
            "demo",
        ]
        scaffold = subprocess.run(scaffold_cmd, cwd=ROOT, text=True, capture_output=True)
        if scaffold.returncode != 0:
            errors.append(f"scaffold failed: {scaffold.stderr.strip()}")
            print("\n".join(errors), file=sys.stderr)
            return 1

        project = tmp_path / "20260624_zh-pop_night-bus"
        strict_empty = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if strict_empty.returncode == 0:
            errors.append("strict compiler should reject an empty scaffold project")

        write(
            project / "04_prompt" / "prompt-compile-brief.md",
            """# Prompt Compile Brief

Project: Example Test Artist
Song: Night Bus Confession
Use case: demo
Audience: late-night city pop listeners
Language: zh
Genre lane: Mandarin pop ballad
Narrator: first-person commuter who cannot send the final message
Situation: last bus after rain, neon reflected on the window
Title phrase: 末班车还亮着
Hook promise: the chorus holds the title phrase like a confession that almost leaves the mouth
Emotion arc: restrained verse to warm, unresolved release
Human seed available: no
Reference set: neutral style DNA only
Catalog identity: intimate urban pop
Release ambition: demo
""",
        )
        write(
            project / "04_prompt" / "style-field-map.md",
            """# Style Field Map

genre: Mandarin pop ballad, 78 BPM 4/4, warm contemporary arrangement
Secondary lane purpose: ballad intimacy with restrained contemporary pop chorus lift; no EDM drop.
Era / scene anchor: 2020s Mandarin night-commute playlist, headphones-first, intimate urban pop.
tempo / meter: 78 BPM 4/4
key / mode: minor verse color resolving to major lift in chorus
vocal: clear Mandarin diction, intimate low verse, controlled chorus lift, restrained vibrato
drums / groove: brushed electronic-acoustic hybrid drums, soft backbeat, no trap hats
bass role: warm bass following kick accents, simple melodic answer before chorus
harmony instruments: close piano voicings, muted electric guitar texture
lead / hook instruments: small bell-like synth motif in intro and outro
production: dry close lead vocal, short plate reverb, centered verse, wider chorus without EDM drop
mood / energy arc: night-bus loneliness to quiet confession, never melodramatic
""",
        )
        write(
            project / "04_prompt" / "lyrics-context-map.md",
            """# Lyrics Context Map

```text
[Song intent: a restrained Mandarin confession on the last bus]
[Prosody notes: keep Mandarin long notes on stable vowels; avoid twisting tones on the title phrase]
[Intro | short bell motif | rain ambience implied]
[Verse 1 | intimate vocal | bus-window image]
车窗把霓虹揉成一条河
[Pre-Chorus | fewer words | breath before title]
我把讯息停在发送之前
[Chorus | 末班车还亮着 | title phrase on a long note]
末班车还亮着 可我没说破
[Verse 2 | new detail | bass answers the vocal]
座位空着 像你还会经过
[Bridge | stripped piano | new perspective]
我终于承认 是我先退后
[Final Chorus | warmer harmony | title phrase returns softer]
末班车还亮着 我把真话收着
[Outro | clean ending]
[End]
```
""",
        )
        write(
            project / "03_writing" / "lyric-brief.md",
            """# Lyric Brief

Narrator: first-person commuter who cannot send the final message
Situation: last bus after rain, back-row seat, phone message waiting unsent
Title phrase: 末班车还亮着
Title phrase function: the chorus turns the bus light into the last chance to confess
Central metaphor: the last bus light is a held breath before truth
Emotion arc: restraint, almost-confession, self-admission, quiet unresolved release
""",
        )
        write(
            project / "03_writing" / "image-bank.md",
            """# Image Bank

Concrete images:
- bus window with finger marks
- unsent phone message
- paper ticket against a wet sleeve
- empty seat beside the narrator
- 00:47 station clock
- convenience-store cup cooling in one hand
Movement: hiding the phone, looking at the empty seat, stepping off before sending
""",
        )
        write(
            project / "03_writing" / "section-information-map.md",
            """# Section Information Map

Verse 1: narrator establishes the bus window and unsent phone message.
Chorus: title phrase turns the bus light into the core confession question.
Verse 2 development: new information reveals the other person did not come and the empty seat changes meaning.
Bridge perspective: turn from blaming timing to admitting the narrator chose silence.
Final chorus payoff: title returns softer as the narrator almost accepts the truth.
""",
        )
        write(
            project / "03_writing" / "cliche-cut.md",
            """# Cliche Cut

Removed cliches: forever, lonely heart, dream, neon rain
Replacement images: unsent phone message, bus window finger marks, paper ticket against wet sleeve, empty seat beside narrator
Cliche cut decision: ready for rewrite
""",
        )
        write(
            project / "04_prompt" / "exclude-negative-aesthetic.md",
            """# Exclude Negative Aesthetic

Exclude: awkward translated Mandarin, vague inspirational lyrics, forced rhyme, excessive melisma, over-autotuned vocal, EDM festival drop, cinematic trailer drums
""",
        )
        write(
            project / "04_prompt" / "slider-intent-map.md",
            """# Slider Intent Map

Model: Suno current
Weirdness: 25
Style Influence: 70
Audio Influence: 0
Phase: converge
What this tests: whether the title phrase lands naturally without generic ballad gloss
""",
        )
        write(
            project / "04_prompt" / "persona-voice-model-routing.md",
            """# Persona Voice Model Routing

Use identity feature: no
Feature type: text-only
Human anchor lane: text-only
Voice identity source: none
Persona source: none
Custom Model source: none
Custom model corpus: none
Voice verification: n/a
My Taste state: off
My Taste summary: n/a
Prompt boost state: off
Boosted style text: n/a
Rights status: no voice/persona/custom model source used
Catalog role: demo exploration
Expected continuity: text prompt only
Risk: no identity feature in this round
Do not use if: a human audio seed, Voice, Persona, Custom Model, or My Taste becomes active without evidence
""",
        )
        write(
            project / "04_prompt" / "constraint-conflict-check.md",
            """# Constraint Conflict Check

Positive field conflicts: none
Negative field conflicts: none
Lyrics/style mismatch: none
Sliders/prompt mismatch: none
Persona/voice mismatch: none
Rights mismatch: none
Decision: compile approved
""",
        )
        write(
            project / "04_prompt" / "field-length-and-specificity-budget.md",
            """# Field Length And Specificity Budget

Must-hear terms: dry close lead vocal, short plate reverb, brushed drums, warm bass pickup, title phrase on long note
Nice-to-have terms: bell-like intro motif, narrow verse, wider chorus, muted electric guitar answer
Remove vague terms: none after replacement; do not use realistic/professional/high quality as positive style targets
Remove duplicated terms: repeated intimacy tags beyond close/dry vocal
Move to Lyrics context: title phrase landing, section functions, bridge perspective, final chorus payoff
Move to Exclude: awkward translated Mandarin, EDM festival drop, over-autotuned vocal
Move to experiment note: try one alternate chorus width in the next batch only
Field budget decision: ready for audit
Source / rationale: Use /path/to/suno-prompt-methodology and realism-descriptors.md; replace vague prompt words with recording, performance, and section language.
""",
        )
        write(
            project / "04_prompt" / "external-method-claim-ledger.md",
            """# External Method Claim Ledger

| source/platform | url/path | claim | source type | confidence | target control surface | testable variable | adoption status | validation route | risk |
|---|---|---|---|---|---|---|---|---|---|
| Suno official help | /path/to/suno-prompt-methodology/sources/official-clean-md/official-creative-sliders.md | Creative Sliders define Weirdness, Style Influence, and Audio Influence as controllable generation surfaces | official | high | Creative Sliders | Style Influence only | foundation | prompt-iteration-discipline-gate + blind A/B | current model behavior may shift |
| local local Suno prompt methodology | /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md | Only one major variable should change in a reviewable iteration | local methodology | high | batch design | Changed variables | foundation | prompt-iteration-discipline-gate | too rigid for early exploration |
| GitHub prompt references | https://github.com/example/suno-style-tags | realism descriptors can inspire candidate style wording | community/GitHub | medium | Style of Music | recording realism descriptors | candidate experiment only | blind A/B, reverse caption, AI flavor survey | unverified tag lists may become vague |
""",
        )
        write(
            project / "04_prompt" / "methodology-transfer-plan.md",
            """# Methodology Transfer Plan

Local method sources: /path/to/suno-prompt-methodology/local Suno prompt methodology知识笔记.md; /path/to/suno-prompt-methodology/templates/suno-prompt-template.md; /path/to/suno-prompt-methodology/templates/suno-prompt-review-checklist.md
Official control surfaces: Style of Music, Lyrics box, Exclude, Creative Sliders, Persona/Voice/Custom Model/My Taste only if source evidence is active
Community / external candidates: Bilibili, Douyin, YouTube, and GitHub tips are candidate experiments only; this fixture adopts no secret tag or guaranteed-hit formula.
Source confidence split: official facts define field behavior; local local Suno prompt methodology supplies workflow/template/checklist; community/external sources remain candidate hypotheses for A/B testing.
Adopted method: five-part style field, lyrics section context, Exclude as negative aesthetic, slider intent, one-variable convergence batch.
Song-specific transfer: for this Mandarin ballad, the local method becomes a dry close lead vocal, section-tagged lyrics, explicit Exclude against translated Mandarin and EDM gloss, and convergent slider settings.
Model/version rationale: Suno current is used for a demo fixture because the test validates evidence discipline, not a paid model comparison; date-sensitive model choice must be rechecked on real projects.
Primary Suno tool route: Custom Mode text-only; no Audio Upload, Voice, Persona, Custom Model, My Taste, or Prompt Boost in this round.
Human-likeness hypothesis: clear Mandarin diction, a specific title hook, restrained vocal performance, brushed groove, and dry close production should reduce anonymous AI-demo feel.
Variable discipline: one primary variable per batch; keep title phrase, language, rights boundary, human anchor lane, and slider baseline fixed.
Rejected magic prompt claims: reject guaranteed-hit tags, celebrity-copy prompts, secret codes, and prompt bundles not tied to blind validation.
Protected-identity safeguard: no artist, band, producer, song, album, or identifiable voice names enter generation-facing fields; references must be neutral style DNA.
Validation metric: blind review must recall the title phrase within 20 seconds and report low AI-flavor red flags.
Drift/rollback condition: if vocals become anonymous, diction twists the title, or the arrangement drifts into EDM/gloss, roll back to style/exclude/slider inputs.
Source freshness: checked 2026-06-25 against local local Suno prompt methodology folder and current project prompt files.
""",
        )
        write(
            project / "02_references" / "rights-and-source-precheck.md",
            """# Rights And Source Precheck

Artist names present: no
Song titles present: no
Allowed action: use neutral style DNA only
Voice identity source: original fictional singer brief
""",
        )
        write(
            project / "02_references" / "reference-rights.md",
            """# Reference Rights

Reference set: no third-party reference, original text-only style DNA
Material type: original prompt design
Owner: Example Test Artist
License / permission: self-owned original writing
Can upload audio: no, text-only
Can use for commercial release?: yes, original prompt text only
Contains third-party lyrics?: no
Contains third-party melody/riff/sample?: no
Contains identifiable voice?: no
Allowed action: text-only neutral style DNA, no reference audio upload
Forbidden use: copied melody, copied lyrics, artist imitation, reference singer voice
""",
        )
        write(
            project / "02_references" / "reference-set.md",
            """# Reference Set

Reference set: no protected artist or song reference; original late-night Mandarin pop coordinates only
Reference A role: tempo and intimate verse space from generic genre convention
Reference B role: none
Do not copy: melody, lyrics, riff, singer identity, arrangement signature, audio recording
""",
        )
        write(
            project / "02_references" / "style-dna-card.md",
            """# Style DNA Card

Reference set: no third-party reference
Rights status: self-owned original text-only style DNA
Tempo / meter: 78 BPM 4/4
Groove: brushed electronic-acoustic hybrid backbeat with warm bass pocket
Form: short intro, verse, pre, chorus, verse 2, bridge, final chorus, outro
Energy timeline: restrained verse to warm final chorus peak
Hook mechanism: title phrase on downbeat with long note on 亮
Vocal delivery: dry close-mic Mandarin lead, controlled mixed chorus
Arrangement palette: piano, muted electric guitar, warm bass, soft drums, bell motif
Production space: narrow dry verse, wider chorus harmonies, short plate
Do-not-copy list: no reference melody, lyrics, riff, voice, artist identity, song title, sample
Original contribution required: original title phrase, lyrics, topline contour, chord pacing, singer brief
Prompt implication: neutral Mandarin pop ballad style DNA only, no artist or song names, no audio upload
Suno tool choice: Custom Mode text-only
Similarity risk: low
""",
        )
        write(
            project / "02_references" / "protected-identity-removal.md",
            """# Protected Identity Removal

Decision: pass
Protected identity removed: yes
Artist identity removed: yes
Song identity removed: yes
Remaining prompt-safe language: neutral style DNA only
""",
        )
        write(
            project / "02_references" / "reference-boundary.md",
            """# Reference Boundary

Reference boundary: use only neutral tempo, groove, form, energy, instrument, production, and vocal-delivery abstractions
Allowed abstraction: tempo, pocket, density curve, dry vocal space, title-hook function
Forbidden use: copied melody, copied lyrics, recognizable riff, artist imitation, reference singer voice, unauthorized audio upload
Original contribution: original title phrase, lyric images, topline map, singer brief, and section structure
Prompt implication: text-only neutral prompt route with no protected names
Suno tool choice: Custom Mode text-only
Similarity risk: low
""",
        )
        write(
            project / "03_writing" / "title-phrase.md",
            """# Title Phrase

Title phrase: 末班车还亮着
Meaning: the confession is still possible but almost missed
Natural spoken stress: 末班车 / 还亮着
Long-note word: 亮
Must-not-distort words: 末班车, 亮
""",
        )
        write(
            project / "03_writing" / "topline-map.md",
            """# Topline Map

Rhythm cell: short-short-long with a breath before the title
Motif contour: small rise into 亮, step down after 着
Target interval: rising fourth on 亮
Start position: chorus title enters on the downbeat
Repeat plan: title repeats twice; second repeat holds 亮 longer
Contrast plan: verse stays low and conversational, chorus jumps to mid-high register
Chorus title landing: long note on 亮 over the chorus arrival chord
Demo file: none
Source: none
Rights: none
""",
        )
        write(
            project / "03_writing" / "melody-contour.md",
            """# Melody Contour

Verse contour: low - low - small rise - fall
Verse rhythm: conversational short phrases
Pre contour: mid - rising - suspended
Pre rhythm: fewer syllables before chorus
Chorus contour: jump up - hold - step down - repeat
Chorus title landing: 亮 is the long-note word
Bridge contrast: lower, narrower, less rhythmic
Final chorus variation: same hook, one restrained lift
""",
        )
        write(
            project / "03_writing" / "harmony-brief.md",
            """# Harmony Brief

Language: zh
Genre: Mandarin pop ballad
Tempo / meter: 78 BPM 4/4
Song emotion: restrained night-bus loneliness to warm confession
Lyric turning point: the message is almost sent before the chorus title
Topline hook status: pass
Key / mode target: minor verse color resolving to bright major chorus lift
Main chord color: warm add9 piano voicings, clear tonic arrival
Tension level: moderate pre-chorus suspension
Bass identity: warm root bass with short melodic pickup
Must avoid: same four-chord loop all song, random key change, muddy bass, bass unrelated to kick, unresolved chorus
Exact harmony required?: no
If exact: n/a
""",
        )
        write(
            project / "03_writing" / "progression-map.md",
            """# Progression Map

[Verse 1]
Progression: vi-IV-I-V, sparse piano
Function: starts unresolved and leaves room for the bus-window narrative
Density: low
Why it fits lyrics: keeps the confession withheld

[Pre-Chorus]
Progression / color: ii-Vsus with stepwise bass climb
Tension device: suspended dominant before the chorus
Target chord: I at chorus downbeat

[Chorus]
Progression: I-V-vi-IV
Arrival point: title phrase lands clearly on I with open voicing
Title phrase chord: I tonic under 亮

[Bridge]
New color: relative minor with reduced bass movement
Reason: admits the hidden feeling before returning

[Final Chorus]
Return / lift: same progression, wider voicing, one restrained borrowed iv before final I
""",
        )
        write(
            project / "03_writing" / "bassline-map.md",
            """# Bassline Map

Primary bass role: warm root anchor with melodic pickup into chorus
Kick relationship: bass follows kick accents, avoids busy fills under the title
Range / sound: warm electric bass, low-mid, not sub-heavy
Verse motion: sparse roots, enters after vocal image
Pre motion: stepwise rising bass toward I
Chorus motion: octave root bass locks the title landing
Bridge motion: reduced pedal bass under relative minor color
Fills / pickups: one short pickup before final chorus
Avoid: muddy bass, bass unrelated to kick
""",
        )
        write(
            project / "03_writing" / "harmonic-rhythm-map.md",
            """# Harmonic Rhythm Map

Verse chord-change rate: one chord per bar, sparse voicing
Pre chord-change rate: slightly faster with suspension into V
Chorus chord-change rate: stable one chord per bar, pause under title word
Bridge chord-change rate: slower, pedal feel
Where harmony should pause: on 亮 in the chorus title
Where harmony should accelerate: pre-chorus second half
""",
        )
        write(
            project / "03_writing" / "cadence-and-bridge-plan.md",
            """# Cadence And Bridge Plan

Chorus arrival: title phrase lands on I with open voicing and octave bass
Pre target: Vsus resolves to I
Bridge contrast: relative minor, reduced bass movement, stripped piano
Final chorus lift: wider harmony, same hook, one restrained borrowed iv before final I
Ending cadence: clean tonic ending after the final title
Do not use: same four-chord loop all song, random key change, unresolved chorus, muddy bass
""",
        )
        write(
            project / "03_writing" / "performance-brief.md",
            """# Performance Brief

Song: Night Bus Confession
Language: zh
Style: Mandarin pop ballad
Tempo / meter: 78 BPM 4/4
Master pocket: laid-back verse, straighter chorus, snare slightly behind
Drum role: soft kick/snare pocket, light ghost notes, no busy fills under vocal
Bass role: follows kick in chorus, sparse muted notes in verse
Guitar role: muted electric guitar answers only between vocal phrases
Keys / synth role: sparse piano comping, short bell synth motif
Vocal-rhythm relationship: title words land on strong beats and drums leave space
Verse feel: intimate, sparse drums, muted bass
Pre-chorus feel: bass rises, snare fill only into chorus
Chorus feel: straighter groove, bass locks with kick, open but not loud-only
Bridge feel: half-time drums, bass drops out first half
Must not sound like: plastic quantized drums, random drum fills, fake live band, constant eighth-note bass, constant pad
Repair priority: rhythm-section pocket before mix polish
""",
        )
        write(
            project / "03_writing" / "drum-realism-map.md",
            """# Drum Realism Map

Kick: soft root pulse, locks with bass on chorus downbeats
Snare: backbeat slightly behind, never flammy
Hats / ride: steady light hats with subtle velocity variation
Ghost notes: very soft, only in pre-chorus lift
Fills: one short snare fill into chorus and final chorus only
Cymbals: mark chorus entry, no constant wash
Velocity shape: hats vary slightly, ghost notes much softer than backbeat
Timing shape: kick stable, snare slightly behind, chorus straighter than verse
Section changes: verse sparse, pre lifts, chorus locks, bridge half-time
Do not: plastic quantized drums, random drum fills
""",
        )
        write(
            project / "03_writing" / "instrument-role-map.md",
            """# Instrument Role Map

Guitar role: muted electric answers between vocal phrases
Guitar playability: simple two-note answer, playable without impossible jumps
Keys / synth role: sparse piano comping and short bell motif
Keys / synth playability: piano leaves left hand out when bass enters
Lead / hook instrument: bell synth mirrors intro only
Vocal space: guitars answer after vocal, keys avoid constant full-range bed
Texture control: pad only in final chorus, not full song
Playable: yes, each part has a realistic hand role
Do not: wall of guitars, constant pad, endless shred
""",
        )
        write(
            project / "03_writing" / "section-performance-map.md",
            """# Section Performance Map

[Verse 1]
Performance: light drums, muted bass, piano leaves vocal space

[Pre-Chorus]
Performance: bass rises, short snare fill into chorus

[Chorus]
Performance: straighter groove, bass locks with kick, open guitar widens after title

[Bridge]
Performance: half-time drums, bass drops out first half

[Final Chorus]
Performance: full band, same pocket, short fill before ending
""",
        )
        write(
            project / "03_writing" / "groove-audit.md",
            """# Groove Audit

Master pocket: laid-back verse, straighter chorus, snare slightly behind
Timing humanization: kick stable, snare slightly behind, chorus straighter than verse
Velocity humanization: hats vary slightly, ghost notes much softer than backbeat
Articulation humanization: muted bass in verse, sustained chorus roots, short guitar answers
Bass articulation: muted bass in verse, sustained chorus roots
Instrument-only reverse caption: restrained ballad band with real rhythm-section pocket
Does the groove match the brief?: yes
""",
        )
        write(
            project / "03_writing" / "structure-brief.md",
            """# Structure Brief

Project: Night Bus Confession
Language: zh
Genre: Mandarin pop ballad
Tempo / meter: 78 BPM 4/4
Target length: 3:20 full single
Use case: demo
Core hook: 末班车还亮着 title phrase
Narrative arc: bus-window restraint to finally admitting the feeling
Emotional arc: intimate verse, rising pre, warm chorus, stripped bridge, full final payoff
Highest energy section: Final Chorus
Highest tension section: Bridge
Must have: clear Verse 2 development, stripped bridge, clean ending
Must avoid: flat energy throughout, same arrangement every section, random genre switch, endless outro, sudden cutoff
Exact structure required?: no
If exact: n/a
""",
        )
        write(
            project / "03_writing" / "energy-map.md",
            """# Energy Map

| Section | Energy 1-9 | Tension 1-9 | Density | Vocal intensity | Width | Low-end |
|---|---:|---:|---|---|---|---|
| Intro | 2 | 2 | sparse motif | low | narrow | none |
| Verse 1 | 3 | 4 | sparse | intimate | narrow | light |
| Pre-Chorus | 5 | 7 | rising | focused | medium | rising |
| Chorus | 7 | 5 | open | mid-high | wide | locked |
| Verse 2 | 4 | 5 | slightly deeper | intimate | medium | muted |
| Chorus 2 | 7 | 5 | added harmony | mid-high | wide | locked |
| Bridge | 4 | 8 | stripped | close | narrow | drop out |
| Final Chorus | 8 | 6 | full band | strongest | widest | locked |
| Outro | 2 | 1 | short tag | soft | narrow | tonic |

Energy rule: verse stays restrained, pre raises tension, chorus releases, bridge lowers density but raises tension, final chorus is the peak.
Where should the listener lean in: pre-chorus breath before title phrase and stripped bridge first line
Where should the listener feel release: chorus title landing and final chorus return
Where should the song breathe: bridge first half and the short outro tag
""",
        )
        write(
            project / "03_writing" / "section-function-map.md",
            """# Section Function Map

Intro:
- musical identity: short bell motif and bus-window space
- lyric/vocal status: no lead vocal
- max length: under 8 seconds

Verse 1:
- information: narrator hides the message while watching neon through the bus window
- vocal posture: close, restrained
- arrangement: sparse piano and light rhythm section

Pre-Chorus:
- tension method: bass climb and fewer words create breath before title
- lyric density: reduced
- melodic direction: rising toward held title word

Chorus:
- title hook: 末班车还亮着
- arrival method: tonic landing with wider band
- repeatable element: title phrase on long note

Verse 2:
- new information: empty seat image suggests the other person might still appear
- new arrangement detail: muted bass answer and subtle guitar counterline
- what stays from Verse 1: intimate vocal and bus imagery

Bridge:
- contrast method: stripped piano, half-time drums, reduced bass
- new perspective: narrator admits the feeling is not just passing by
- return cue: held vocal pickup into final chorus downbeat

Final Chorus:
- what repeats: same title hook and melodic contour
- what develops: wider harmony and one restrained ad-lib
- payoff: confession finally feels possible without burying the vocal

Outro:
- ending logic: short title tag resolves to tonic
- last sound: clean piano/bell cadence
""",
        )
        write(
            project / "03_writing" / "contrast-continuity-matrix.md",
            """# Contrast Continuity Matrix

Keep across song: tempo, singer identity, title hook, night-bus motif, warm piano/bell color
Change by section: lyric information, drum density, bass movement, width, bridge texture, final chorus harmony
Never change: language, title phrase identity, core groove family, vocal intimacy
Allowed surprise: stripped bridge with half-time drums and dry vocal
""",
        )
        write(
            project / "03_writing" / "transition-cue-sheet.md",
            """# Transition Cue Sheet

Intro -> Verse: bell motif decays into first vocal breath
Verse -> Pre: bass starts climbing and hats open slightly
Pre -> Chorus: short snare pickup, one-beat breath, title lands on downbeat
Chorus -> Verse 2: drums drop back, guitar leaves one answer phrase
Verse 2 -> Pre 2: bass climb returns with slightly stronger snare
Chorus 2 -> Bridge: reverb tail and bass dropout
Bridge -> Final Chorus: held vocal pickup and tom fill into full band
Final Chorus -> Outro: band cuts to short title tag and clean cadence

Allowed cues: drum fill, vocal pickup, bass climb, one-bar break, harmonic hold, guitar fill, reverb tail, silence
Forbidden cues: random genre switch, overblown riser, endless outro, sudden cutoff, fake crowd
""",
        )
        write(
            project / "03_writing" / "second-verse-development.md",
            """# Second Verse Development

New information: empty seat and passing stop add a concrete consequence after Verse 1
New arrangement detail: muted bass answer and one subtle guitar counterline
What stays from Verse 1: intimate vocal, restrained drums, bus-window imagery
What must not happen: no full chorus energy before the chorus
""",
        )
        write(
            project / "03_writing" / "bridge-turn-plan.md",
            """# Bridge Turn Plan

Before bridge, listener knows: the narrator has almost confessed but still hides the message
Bridge reveals: the feeling is not temporary and cannot be explained away as a commute
Musical contrast: stripped piano, half-time drums, bass drops out
Lyric contrast: direct admission instead of image-only restraint
Return cue to final chorus: held vocal pickup into full-band downbeat
Do not: third verse disguised as bridge, random key change, genre switch
""",
        )
        write(
            project / "03_writing" / "final-chorus-payoff.md",
            """# Final Chorus Payoff

What repeats exactly: title hook and main contour
What changes: wider harmony and warmer backing vocal
New layer: one restrained guitar/piano lift after the title
Vocal payoff: one controlled ad-lib after the held title word
Mix payoff: wider band without burying lead vocal
Final line: title phrase returns softer
Ending cue: short tag into clean tonic cadence
""",
        )
        write(
            project / "03_writing" / "outro-end-plan.md",
            """# Outro End Plan

Ending logic: short title tag after final chorus resolves the confession
Last sound: clean piano/bell tonic cadence
Outro length: under 10 seconds
Fade / stop / tag: short tag, no long fade
Do not: endless instrumental jam, sudden cutoff, new lyric information
""",
        )
        write(
            project / "03_writing" / "singer-brief.md",
            """# Singer Brief

Song: Night Bus Confession
Language: zh
Narrator: first-person commuter
Vocal role: lead solo fictional singer
Range / tessitura: close mid-low alto, comfortable mixed voice in chorus
Register plan: low intimate verse, controlled mixed voice chorus, straight bridge
Timbre: warm dry close-mic voice with slight breath edge and clear center
Diction: clear Mandarin consonants, stable vowels on title phrase
Breath: audible breath before chorus title, short breath after long phrase
Vibrato / straight tone: straight tone in verse and bridge, restrained vibrato only on title long note
Dynamics: quiet verse, lifted pre-chorus, open but controlled chorus, softer outro
Emotional restraint: no theatrical crying, held-back confession until final chorus
Must not sound like: anonymous vocalist, excessive vocal runs, unclear diction, over-autotuned vocal, fake gasping, same tail every line, choir pad everywhere
Rights source: fictional text-only singer brief, no voice/persona/custom model source used
""",
        )
        write(
            project / "03_writing" / "vocal-performance-map.md",
            """# Vocal Performance Map

[Verse 1]
Performance: close-mic low register, almost spoken, clear consonants

[Pre-Chorus]
Performance: fewer words, audible breath before title, slight intensity rise

[Chorus]
Performance: lead centered, controlled mixed voice, restrained vibrato on 亮 only

[Verse 2]
Performance: same singer identity, slightly more confidence, tighter rhythm

[Bridge]
Performance: stripped straight tone, dry vocal, less reverb, new perspective

[Final Chorus]
Performance: same hook preserved, one restrained ad-lib after title, warm but not overstacked

[Outro]
Performance: soft final title tag, clean consonant ending, short breath tail
""",
        )
        write(
            project / "03_writing" / "vocal-arrangement-map.md",
            """# Vocal Arrangement Map

Lead vocal: fictional lead stays center and carries all title phrases
Doubles: none in verse, light double behind chorus, wider only in final chorus
Harmonies: support the title phrase tail only, never louder than lead
Ad-libs: one restrained ad-lib after final chorus title phrase
Duet / group vocal: none
Lead center: lead remains intelligible over all doubles and harmonies
Do not: choir pad everywhere, excessive vocal runs, lead buried by doubles
""",
        )

        external_method_claim_audit = subprocess.run(
            [
                sys.executable,
                str(EXTERNAL_METHOD_CLAIM_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if external_method_claim_audit.returncode != 0:
            errors.append(f"external method claim audit failed: stdout={external_method_claim_audit.stdout.strip()} stderr={external_method_claim_audit.stderr.strip()}")

        methodology_audit = subprocess.run(
            [
                sys.executable,
                str(METHODOLOGY_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if methodology_audit.returncode != 0:
            errors.append(f"methodology transfer audit failed: stdout={methodology_audit.stdout.strip()} stderr={methodology_audit.stderr.strip()}")

        specificity_audit = subprocess.run(
            [
                sys.executable,
                str(SPECIFICITY_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if specificity_audit.returncode != 0:
            errors.append(f"prompt specificity audit failed: stdout={specificity_audit.stdout.strip()} stderr={specificity_audit.stderr.strip()}")

        genre_lane_audit = subprocess.run(
            [
                sys.executable,
                str(GENRE_LANE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if genre_lane_audit.returncode != 0:
            errors.append(f"genre/lane authenticity audit failed: stdout={genre_lane_audit.stdout.strip()} stderr={genre_lane_audit.stderr.strip()}")

        lyric_narrative_audit = subprocess.run(
            [
                sys.executable,
                str(LYRIC_NARRATIVE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if lyric_narrative_audit.returncode != 0:
            errors.append(f"lyric narrative audit failed: stdout={lyric_narrative_audit.stdout.strip()} stderr={lyric_narrative_audit.stderr.strip()}")

        reference_audit = subprocess.run(
            [
                sys.executable,
                str(REFERENCE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if reference_audit.returncode != 0:
            errors.append(f"reference audit failed: stdout={reference_audit.stdout.strip()} stderr={reference_audit.stderr.strip()}")

        prosody_audit = subprocess.run(
            [
                sys.executable,
                str(PROSODY_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if prosody_audit.returncode != 0:
            errors.append(f"prosody audit failed: stdout={prosody_audit.stdout.strip()} stderr={prosody_audit.stderr.strip()}")

        topline_audit = subprocess.run(
            [
                sys.executable,
                str(TOPLINE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if topline_audit.returncode != 0:
            errors.append(f"topline audit failed: stdout={topline_audit.stdout.strip()} stderr={topline_audit.stderr.strip()}")

        harmony_audit = subprocess.run(
            [
                sys.executable,
                str(HARMONY_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if harmony_audit.returncode != 0:
            errors.append(f"harmony/bass audit failed: stdout={harmony_audit.stdout.strip()} stderr={harmony_audit.stderr.strip()}")

        groove_audit = subprocess.run(
            [
                sys.executable,
                str(GROOVE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if groove_audit.returncode != 0:
            errors.append(f"groove audit failed: stdout={groove_audit.stdout.strip()} stderr={groove_audit.stderr.strip()}")

        structure_audit = subprocess.run(
            [
                sys.executable,
                str(STRUCTURE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if structure_audit.returncode != 0:
            errors.append(f"structure audit failed: stdout={structure_audit.stdout.strip()} stderr={structure_audit.stderr.strip()}")

        vocal_audit = subprocess.run(
            [
                sys.executable,
                str(VOCAL_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if vocal_audit.returncode != 0:
            errors.append(f"vocal audit failed: stdout={vocal_audit.stdout.strip()} stderr={vocal_audit.stderr.strip()}")

        compile_cmd = [
            sys.executable,
            str(COMPILER),
            "--project-root",
            str(project),
            "--write",
            "--allow-overwrite",
            "--strict",
        ]
        compiled = subprocess.run(compile_cmd, cwd=ROOT, text=True, capture_output=True)
        if compiled.returncode != 0:
            errors.append(f"compiler failed: stdout={compiled.stdout.strip()} stderr={compiled.stderr.strip()}")

        package_path = project / "04_prompt" / "prompt-package-v001.md"
        preflight_path = project / "04_prompt" / "prompt-preflight-review.md"
        handoff_path = project / "04_prompt" / "experiment-handoff.md"
        for path in [package_path, preflight_path, handoff_path]:
            if not path.exists():
                errors.append(f"missing compiler output: {path}")

        if package_path.exists():
            package = package_path.read_text(encoding="utf-8")
            for term in [
                "Night Bus Confession",
                "Mandarin pop ballad",
                "clear Mandarin diction",
                "末班车还亮着",
                "awkward translated Mandarin",
                "title phrase on a long note",
                "Human Anchor Lane: text-only",
                "My Taste State: off",
                "Methodology transfer: pass",
                "Prompt specificity: pass",
                "Genre/lane authenticity: pass",
                "Lyric narrative: pass",
                "Reference audit: pass",
                "Prosody audit: pass",
                "Topline audit: pass",
                "Harmony/Bass audit: pass",
                "Groove audit: pass",
                "Structure audit: pass",
                "Vocal audit: pass",
                "Preflight Summary",
                "compile approved",
            ]:
                if term not in package:
                    errors.append(f"compiled package missing term: {term}")

        if preflight_path.exists() and "Decision: compile approved" not in preflight_path.read_text(encoding="utf-8"):
            errors.append("preflight review missing compile approved decision")
        if preflight_path.exists():
            preflight = preflight_path.read_text(encoding="utf-8")
            for term in ["Methodology transfer: pass", "Prompt specificity: pass", "Genre/lane authenticity: pass", "Lyric narrative: pass", "Reference audit: pass", "Prosody audit: pass", "Topline audit: pass", "Harmony/Bass audit: pass", "Groove audit: pass", "Structure audit: pass", "Vocal audit: pass", "Human anchor lane: pass", "Identity routing: pass", "My Taste / boost: pass"]:
                if term not in preflight:
                    errors.append(f"preflight review missing identity term: {term}")
        if handoff_path.exists() and "2-4 candidates" not in handoff_path.read_text(encoding="utf-8"):
            errors.append("experiment handoff missing batch guidance")
        if handoff_path.exists() and "Human anchor lane: text-only" not in handoff_path.read_text(encoding="utf-8"):
            errors.append("experiment handoff missing human anchor lane")

        write(
            project / "04_prompt" / "slider-intent-map.md",
            """# Slider Intent Map

Phase: converge
What this tests: whether the title phrase lands naturally without generic ballad gloss
""",
        )
        missing_slider = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if missing_slider.returncode == 0:
            errors.append("strict compiler should reject missing model/weirdness/style influence")
        missing_slider_text = missing_slider.stdout + "\n" + missing_slider.stderr
        for term in ["model", "weirdness", "style_influence", "sliders", "repair slider intent"]:
            if term not in missing_slider_text:
                errors.append(f"missing-slider compiler output missing term: {term}")

        write(
            project / "04_prompt" / "slider-intent-map.md",
            """# Slider Intent Map

Model: Suno current
Weirdness: 25
Style Influence: 70
Audio Influence: 0
Phase: converge
What this tests: whether the title phrase lands naturally without generic ballad gloss
""",
        )
        write(project / "04_prompt" / "persona-voice-model-routing.md", "# Persona Voice Model Routing\n\nUse identity feature: no\n")
        missing_anchor = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if missing_anchor.returncode == 0:
            errors.append("strict compiler should reject missing Human anchor lane")
        missing_anchor_text = missing_anchor.stdout + "\n" + missing_anchor.stderr
        for term in ["human_anchor_lane", "Human anchor lane", "repair identity routing"]:
            if term not in missing_anchor_text:
                errors.append(f"missing-anchor compiler output missing term: {term}")

        write(
            project / "04_prompt" / "persona-voice-model-routing.md",
            """# Persona Voice Model Routing

Use identity feature: no
Feature type: text-only
Human anchor lane: text-only
Voice identity source: none
Persona source: none
Custom Model source: none
Custom model corpus: none
Voice verification: n/a
My Taste state: off
My Taste summary: n/a
Prompt boost state: off
Boosted style text: n/a
Rights status: no voice/persona/custom model source used
Catalog role: demo exploration
Expected continuity: text prompt only
Risk: no identity feature in this round
Do not use if: a human audio seed, Voice, Persona, Custom Model, or My Taste becomes active without evidence
""",
        )
        write(
            project / "03_writing" / "lyric-narrative-audit.md",
            """# Lyric Narrative Audit

Generated by: tools/audit_music_lyric_narrative.py
Decision: repair before prompt compile

## Lyric Narrative Evidence

Narrator/situation tags: first-person commuter; last bus
Concrete image tags: NEEDS_REPAIR
Title phrase function: the bus light means one last chance
Central metaphor: bus light as held breath
Section information tags: verse 1, chorus
Cliche removal: removed=forever, replacements=NEEDS_REPAIR
Verse 2 development: NEEDS_REPAIR
Bridge perspective: NEEDS_REPAIR
Lyrics rewrite handoff: repair
""",
        )
        failed_lyric_narrative = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_lyric_narrative.returncode == 0:
            errors.append("strict compiler should reject failed lyric narrative audit")
        failed_lyric_text = failed_lyric_narrative.stdout + "\n" + failed_lyric_narrative.stderr
        for term in ["lyric_narrative_audit", "audit_music_lyric_narrative.py", "run audit_music_lyric_narrative.py"]:
            if term not in failed_lyric_text:
                errors.append(f"failed-lyric-narrative compiler output missing term: {term}")

        lyric_narrative_audit = subprocess.run(
            [
                sys.executable,
                str(LYRIC_NARRATIVE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if lyric_narrative_audit.returncode != 0:
            errors.append(f"lyric narrative audit re-run failed: stdout={lyric_narrative_audit.stdout.strip()} stderr={lyric_narrative_audit.stderr.strip()}")

        write(
            project / "03_writing" / "lyrics-prosody-audit.md",
            """# Lyrics Prosody Audit

Generated by: tools/audit_music_lyrics_prosody.py
Decision: repair before prompt compile

## Section Metrics

Lyrics tags: natural Mandarin phrasing
Blind-listening red flags: breathless chorus
""",
        )
        failed_prosody = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_prosody.returncode == 0:
            errors.append("strict compiler should reject failed lyrics prosody audit")
        failed_prosody_text = failed_prosody.stdout + "\n" + failed_prosody.stderr
        for term in ["lyrics_prosody_audit", "audit_music_lyrics_prosody.py", "run audit_music_lyrics_prosody.py"]:
            if term not in failed_prosody_text:
                errors.append(f"failed-prosody compiler output missing term: {term}")

        prosody_audit = subprocess.run(
            [
                sys.executable,
                str(PROSODY_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if prosody_audit.returncode != 0:
            errors.append(f"prosody audit re-run failed: stdout={prosody_audit.stdout.strip()} stderr={prosody_audit.stderr.strip()}")

        write(
            project / "03_writing" / "topline-hook-audit.md",
            """# Topline Hook Audit

Generated by: tools/audit_music_topline_hook.py
Decision: repair before prompt compile

## Hook Design

Topline tags: chorus title enters on the downbeat
Blind hook test: title phrase recall failed
""",
        )
        failed_topline = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_topline.returncode == 0:
            errors.append("strict compiler should reject failed topline hook audit")
        failed_topline_text = failed_topline.stdout + "\n" + failed_topline.stderr
        for term in ["topline_hook_audit", "audit_music_topline_hook.py", "run audit_music_topline_hook.py"]:
            if term not in failed_topline_text:
                errors.append(f"failed-topline compiler output missing term: {term}")

        topline_audit = subprocess.run(
            [
                sys.executable,
                str(TOPLINE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if topline_audit.returncode != 0:
            errors.append(f"topline audit re-run failed: stdout={topline_audit.stdout.strip()} stderr={topline_audit.stderr.strip()}")

        write(
            project / "03_writing" / "harmony-bass-audit.md",
            """# Harmony Bass Audit

Generated by: tools/audit_music_harmony_bass.py
Decision: repair before prompt compile

## Harmony Design

Harmony tags: minor verse color
Bass tags: root bass
Topline/harmony fit: title chord unresolved
""",
        )
        failed_harmony = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_harmony.returncode == 0:
            errors.append("strict compiler should reject failed harmony/bass audit")
        failed_harmony_text = failed_harmony.stdout + "\n" + failed_harmony.stderr
        for term in ["harmony_bass_audit", "audit_music_harmony_bass.py", "run audit_music_harmony_bass.py"]:
            if term not in failed_harmony_text:
                errors.append(f"failed-harmony compiler output missing term: {term}")

        harmony_audit = subprocess.run(
            [
                sys.executable,
                str(HARMONY_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if harmony_audit.returncode != 0:
            errors.append(f"harmony/bass audit re-run failed: stdout={harmony_audit.stdout.strip()} stderr={harmony_audit.stderr.strip()}")

        write(
            project / "03_writing" / "groove-humanization-audit.md",
            """# Groove Humanization Audit

Generated by: tools/audit_music_groove_humanization.py
Decision: repair before prompt compile

## Groove Design

Groove tags: humanized band
Instrument performance tags: realistic instruments
Rhythm-section blind test: failed
""",
        )
        failed_groove = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_groove.returncode == 0:
            errors.append("strict compiler should reject failed groove humanization audit")
        failed_groove_text = failed_groove.stdout + "\n" + failed_groove.stderr
        for term in ["groove_humanization_audit", "audit_music_groove_humanization.py", "run audit_music_groove_humanization.py"]:
            if term not in failed_groove_text:
                errors.append(f"failed-groove compiler output missing term: {term}")

        groove_audit = subprocess.run(
            [
                sys.executable,
                str(GROOVE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if groove_audit.returncode != 0:
            errors.append(f"groove audit re-run failed: stdout={groove_audit.stdout.strip()} stderr={groove_audit.stderr.strip()}")

        write(
            project / "03_writing" / "structure-dynamics-audit.md",
            """# Structure Dynamics Audit

Generated by: tools/audit_music_structure_dynamics.py
Decision: repair before prompt compile

## Structure Design

Structure tags: flat structure
Section tags: weak bridge and final chorus
Structure blind test: failed
""",
        )
        failed_structure = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_structure.returncode == 0:
            errors.append("strict compiler should reject failed structure dynamics audit")
        failed_structure_text = failed_structure.stdout + "\n" + failed_structure.stderr
        for term in ["structure_dynamics_audit", "audit_music_structure_dynamics.py", "run audit_music_structure_dynamics.py"]:
            if term not in failed_structure_text:
                errors.append(f"failed-structure compiler output missing term: {term}")

        structure_audit = subprocess.run(
            [
                sys.executable,
                str(STRUCTURE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if structure_audit.returncode != 0:
            errors.append(f"structure audit re-run failed: stdout={structure_audit.stdout.strip()} stderr={structure_audit.stderr.strip()}")

        write(
            project / "03_writing" / "vocal-identity-audit.md",
            """# Vocal Identity Performance Audit

Generated by: tools/audit_music_vocal_identity.py
Decision: repair before prompt compile

## Vocal Design

Vocal tags: anonymous pop vocal
Vocal performance tags: same intensity all song
Vocal arrangement tags: choir pad everywhere
Vocal blind test: failed
""",
        )
        failed_vocal = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_vocal.returncode == 0:
            errors.append("strict compiler should reject failed vocal identity audit")
        failed_vocal_text = failed_vocal.stdout + "\n" + failed_vocal.stderr
        for term in ["vocal_identity_audit", "audit_music_vocal_identity.py", "run audit_music_vocal_identity.py"]:
            if term not in failed_vocal_text:
                errors.append(f"failed-vocal compiler output missing term: {term}")

        vocal_audit = subprocess.run(
            [
                sys.executable,
                str(VOCAL_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if vocal_audit.returncode != 0:
            errors.append(f"vocal audit re-run failed: stdout={vocal_audit.stdout.strip()} stderr={vocal_audit.stderr.strip()}")

        write(
            project / "02_references" / "reference-dna-audit.md",
            """# Reference DNA Audit

Generated by: tools/audit_music_reference_dna.py
Decision: repair before prompt compile

## Reference Design

Reference tags: unsafe reference
Style DNA tags: thin
Protected identity removal: repair
Similarity blind test: failed
""",
        )
        failed_reference = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if failed_reference.returncode == 0:
            errors.append("strict compiler should reject failed reference DNA audit")
        failed_reference_text = failed_reference.stdout + "\n" + failed_reference.stderr
        for term in ["reference_dna_audit", "audit_music_reference_dna.py", "run audit_music_reference_dna.py"]:
            if term not in failed_reference_text:
                errors.append(f"failed-reference compiler output missing term: {term}")

        reference_audit = subprocess.run(
            [
                sys.executable,
                str(REFERENCE_AUDIT),
                "--project-root",
                str(project),
                "--write",
                "--allow-overwrite",
                "--strict",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if reference_audit.returncode != 0:
            errors.append(f"reference audit re-run failed: stdout={reference_audit.stdout.strip()} stderr={reference_audit.stderr.strip()}")

        write(
            project / "04_prompt" / "slider-intent-map.md",
            """# Slider Intent Map

Model: Suno current
Weirdness: 25
Style Influence: 70
Audio Influence: 0
Phase: converge
What this tests: whether the title phrase lands naturally without generic ballad gloss
""",
        )
        write(
            project / "04_prompt" / "persona-voice-model-routing.md",
            """# Persona Voice Model Routing

Use identity feature: no
Feature type: text-only
Human anchor lane: text-only
Voice identity source: none
Persona source: none
Custom Model source: none
Custom model corpus: none
Voice verification: n/a
My Taste state: off
My Taste summary: n/a
Prompt boost state: off
Boosted style text: n/a
Rights status: no voice/persona/custom model source used
""",
        )
        write(
            project / "04_prompt" / "style-field-map.md",
            """# Style Field Map

genre: Taylor Swift style Mandarin pop ballad, 78 BPM 4/4, warm contemporary arrangement
tempo / meter: 78 BPM 4/4
key / mode: minor verse color resolving to major lift in chorus
vocal: clear Mandarin diction, intimate low verse, controlled chorus lift, restrained vibrato
drums / groove: brushed electronic-acoustic hybrid drums, soft backbeat, no trap hats
bass role: warm bass following kick accents, simple melodic answer before chorus
harmony instruments: close piano voicings, muted electric guitar texture
lead / hook instruments: small bell-like synth motif in intro and outro
production: dry close lead vocal, short plate reverb, centered verse, wider chorus without EDM drop
mood / energy arc: night-bus loneliness to quiet confession, never melodramatic
""",
        )
        protected_identity = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--strict"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if protected_identity.returncode == 0:
            errors.append("strict compiler should reject protected artist names in generation-facing prompt fields")
        protected_identity_text = protected_identity.stdout + "\n" + protected_identity.stderr
        for term in ["protected_identity_in_prompt", "Taylor Swift", "neutral style DNA"]:
            if term not in protected_identity_text:
                errors.append(f"protected-identity compiler output missing term: {term}")

        no_overwrite = subprocess.run(
            [sys.executable, str(COMPILER), "--project-root", str(project), "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if no_overwrite.returncode != 2:
            errors.append("compiler should refuse to overwrite existing outputs without --allow-overwrite")

    prompt_page = WIKI_PROMPT.read_text(encoding="utf-8")
    project_page = WIKI_PROJECT.read_text(encoding="utf-8")
    log_text = LOG.read_text(encoding="utf-8")
    for term in [
        "tools/audit_music_methodology_transfer.py",
        "tools/audit_music_external_method_claims.py",
        "external-method-claim-audit.md",
        "methodology-transfer-audit.md",
        "Methodology transfer",
        "tools/audit_music_prompt_specificity_budget.py",
        "prompt-specificity-budget-audit.md",
        "Prompt specificity",
        "tools/audit_music_genre_lane_authenticity.py",
        "genre-lane-authenticity-audit.md",
        "Genre/lane authenticity",
        "tools/audit_music_lyric_narrative.py",
        "lyric-narrative-audit.md",
        "Lyric narrative",
        "tools/compile_music_prompt_package.py",
        "--project-root",
        "--write",
        "--strict",
        "prompt-package-v001.md",
        "prompt-preflight-review.md",
        "experiment-handoff.md",
        "Model/version",
        "protected_identity_in_prompt",
        "Human anchor lane",
        "My Taste / boost",
        "旧的 `prompt-package-v001.md`",
    ]:
        if term not in prompt_page:
            errors.append(f"prompt workflow missing compiler term: {term}")
    for term in ["tools/audit_music_external_method_claims.py", "external-method-claim-ledger.md", "external-method-claim-audit.md", "tools/audit_music_methodology_transfer.py", "methodology-transfer-plan.md", "methodology-transfer-audit.md", "tools/audit_music_prompt_specificity_budget.py", "field-length-and-specificity-budget.md", "prompt-specificity-budget-audit.md", "tools/audit_music_genre_lane_authenticity.py", "genre-lane-authenticity-audit.md", "tools/audit_music_lyric_narrative.py", "lyric-narrative-audit.md", "tools/compile_music_prompt_package.py", "prompt-package-v001.md", "prompt-preflight-review.md", "Style Influence", "Human Anchor", "persona-voice-model-routing.md", "生成面字段"]:
        if term not in project_page:
            errors.append(f"song project template missing compiler term: {term}")
    for term in ["AI 音乐 External Method Claim 工具闸门", "AI 音乐 Methodology Transfer 工具闸门", "AI 音乐 Prompt Specificity Budget 工具闸门", "AI 音乐 Genre Lane Authenticity 工具闸门", "AI 音乐 Lyric Narrative 工具闸门", "AI 音乐 Prompt Package 编译工具", "AI 音乐 Prompt Preflight 参数与身份硬闸门"]:
        if term not in log_text:
            errors.append(f"wiki log missing prompt compiler entry: {term}")

    if errors:
        print("AI music prompt package compiler verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music prompt package compiler verification passed.")
    print(f"compiler: {COMPILER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
