# Publication Cleanup Report

This directory is a sanitized public copy.

Removed from the public copy:

- Original Git history.
- Local task-runner records and attempt logs.
- Generated song projects and previous outputs.
- macOS metadata files.
- Private loop prompts tied to a local workspace.

Sanitized in the public copy:

- Local absolute paths were replaced with generic placeholders.
- Private Obsidian vault references were changed to generic local-vault wording.
- Secret-like token patterns were scanned after cleanup.

Before publishing, run:

```bash
rg -n -uu --hidden '(/User[s]/|sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|DSA|EC|OPENSSH|PRIVATE) KEY-----|Bearer[[:space:]]+[A-Za-z0-9._-]+)' .
python3 -m py_compile tools/*.py
git status --short
```

Validation performed for this sanitized copy:

- Personal path/name scan: 0 matches.
- High-confidence token/key pattern scan: 0 matches.
- Private directory and local database scan: 0 matches.
- Python syntax check: passed for `tools/*.py`.
