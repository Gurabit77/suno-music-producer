# Suno Music Producer

Suno Music Producer is a local, file-based toolkit for planning, auditing, and preparing AI music generation workflows. It focuses on reusable prompt packages, rights-aware reference handling, structured take review, and release-readiness checks.

This repository does not include generated songs, private listening notes, account data, browser state, API keys, or personal project archives.

## What This Includes

- Project scaffolding for song production evidence packages.
- Prompt package compilation and preflight checks.
- Reference DNA and chord-skeleton safety audits.
- Take review, repair routing, DAW handoff, and release-readiness utilities.
- Verifier scripts for local development and workflow regression checks.

## What This Excludes

- Generated music and previous song projects.
- Local task-runner logs and attempt history.
- Obsidian vault content or private knowledge-base notes.
- Browser cookies, Suno account data, API keys, and secrets.
- Local machine paths from the original private workspace.

## Quick Start

```bash
python3 tools/create_music_song_project.py --help
python3 tools/plan_music_generation_route.py --brief "A late-night Mandarin pop ballad with warm guitar and restrained drums"
python3 tools/prepare_music_effect_first_suno_run.py --brief "A hopeful city-pop demo for a short video"
```

Create a local song project:

```bash
python3 tools/create_music_song_project.py --project-root song-projects/example-song
```

Project outputs should stay in ignored local folders such as `song-projects/`, `outputs/`, or another private workspace outside this repository.

## Optional Local Paths

Some verifier scripts can be adapted to a private Obsidian vault or a local prompt-methodology folder. Keep those paths out of Git and pass them through environment variables or command-line arguments when you customize the toolkit.

Suggested private environment variables:

```bash
export OBSIDIAN_VAULT="/path/to/your/obsidian-vault"
export SUNO_PROMPT_METHODOLOGY="/path/to/your/suno-prompt-methodology"
export SUNO_MUSIC_PRODUCER_ROOT="$PWD"
```

Do not commit `.env` files or private vault exports.

## Safety Boundaries

The toolkit is designed for offline preparation and review. It should not:

- Upload audio without explicit human approval.
- Click Generate/Create/Cover or spend account credits.
- Use unofficial Suno APIs, cookies, session extraction, CAPTCHA bypasses, or account-token scraping.
- Copy named artists, living voices, melodies, lyrics, stems, samples, or third-party songs.

## Verification

Basic syntax check:

```bash
python3 -m py_compile tools/*.py
```

Run individual verifiers as needed:

```bash
python3 tools/verify_music_system_health.py
```

Some verifiers are workflow fixtures and may require local private references that are intentionally not included in this public repository.
