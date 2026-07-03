#!/usr/bin/env python3
"""Aggregate all music verifiers into a single health check."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
SELF_NAME = "verify_music_system_health.py"


def discover_verifiers() -> list[Path]:
    return sorted(
        p for p in TOOLS_DIR.glob("verify_music_*.py")
        if p.name != SELF_NAME
    )


def run_verifier(path: Path) -> tuple[str, int, str]:
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = (result.stdout + result.stderr).strip()
        return path.name, result.returncode, output
    except subprocess.TimeoutExpired:
        return path.name, 1, "TIMEOUT after 60s"
    except Exception as exc:
        return path.name, 1, str(exc)


def main() -> int:
    print("AI Music System Health Check")
    print("=" * 50)

    python_files = sorted(TOOLS_DIR.glob("*.py"))
    syntax_result = subprocess.run(
        [sys.executable, "-m", "py_compile", *[str(path) for path in python_files]],
        capture_output=True,
        text=True,
    )
    if syntax_result.returncode != 0:
        print(f"\nSYNTAX CHECK FAILED:\n{syntax_result.stderr}")
        return 1
    print("Syntax check: PASSED")

    verifiers = discover_verifiers()
    print(f"Found {len(verifiers)} verifiers\n")

    passed = 0
    failed = 0
    first_failed_name = None
    first_failed_output = None

    for verifier in verifiers:
        name, code, output = run_verifier(verifier)
        if code == 0:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            if first_failed_name is None:
                first_failed_name = name
                first_failed_output = output
            print(f"  FAIL  {name}")

    print(f"\n{'=' * 50}")
    print(f"Total: {len(verifiers)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print(f"\nFirst failed: {first_failed_name}")
        print(f"Suggested next: python3 tools/{first_failed_name}")
        if first_failed_output:
            print(f"\nFailure output:\n{first_failed_output[:2000]}")
        return 1

    print("\nAI music system health verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
