#!/usr/bin/env python3
"""Verify the desktop Suno Music Producer optimization plan document.

This verifier is intentionally offline. It does not open Chrome, contact Suno,
upload audio, spend credits, or inspect account state. It only checks that the
desktop plan document contains the execution-ready structure requested for the
Suno Music Producer optimization loop.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


PLAN = Path("/path/to/private-product-plan.md")


REQUIRED_TERMS = {
    "real_run_postmortem": [
        "v002-v007",
        "青は終わらない",
        "连续围绕曲风词修改",
        "副歌",
        "破音",
        "电流音",
    ],
    "p0_modules": [
        "ArtifactRootCauseClassifier",
        "ChorusPressureAudit",
        "ReferenceRouteReset",
        "SunoPagePreflight",
        "CreateTransaction",
    ],
    "page_safety": [
        "Audio/Sample",
        "Audio Influence = 0",
        "CAPTCHA",
        "付款",
        "额度",
        "Voice/Persona",
    ],
    "transaction_control": [
        "snapshot_before",
        "click_create_once",
        "expected_new_takes",
        "actual_new_takes",
        "duplicate_click_blocked",
    ],
    "payload_layering": [
        "Rich Prompt Package",
        "Suno Page Payload",
        "用户可见",
        "内部证据包",
    ],
    "loop_package": [
        "无人值守 Loop 执行包",
        "Loop Goal",
        "Acceptance Criteria",
        "Loop Stop Conditions",
    ],
    "data_contracts": [
        "RootCauseReport",
        "ChorusPressureReport",
        "ReferenceResetRecord",
        "SunoPagePreflightReport",
        "CreateTransactionRecord",
    ],
    "implementation_tasks": [
        "实施任务拆分",
        "T1",
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
        "T7",
    ],
    "completion_definition": [
        "完成定义",
        "verifier",
        "可执行",
        "可验收",
    ],
}


REQUIRED_HEADINGS = [
    "## 0. 一句话结论",
    "## 2. 真实运行复盘",
    "## 5. P0 必须优先落地的解决方案",
    "## 8. 本地项目与 Suno Music Producer 的融合方案",
    "## 9. Chrome/Suno 自动化详细方案",
    "## 11. 生成前闸门清单",
    "## 14. 分阶段落地路线",
    "## 15. 优先级任务清单",
    "## 16. 验收指标",
    "## 20. 无人值守 Loop 执行包",
    "## 21. 模块级数据契约",
    "## 22. 实施任务拆分",
    "## 23. Verifier 设计",
    "## 24. 完成定义",
]


def fail(errors: list[str]) -> int:
    print("Suno Music Producer plan document verification failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []
    if not PLAN.exists():
        return fail([f"plan document missing: {PLAN}"])

    text = PLAN.read_text(encoding="utf-8")
    compact = re.sub(r"\s+", " ", text).casefold()

    if len(text) < 25_000:
        errors.append(f"plan is too short for optimized execution-ready version: {len(text)} chars")

    line_count = text.count("\n") + 1
    if line_count < 1_500:
        errors.append(f"plan should contain expanded loop-ready detail; only {line_count} lines")

    for heading in REQUIRED_HEADINGS:
        if heading.casefold() not in compact:
            errors.append(f"missing heading: {heading}")

    for group, terms in REQUIRED_TERMS.items():
        missing = [term for term in terms if term.casefold() not in compact]
        if missing:
            errors.append(f"{group} missing terms: {', '.join(missing)}")

    code_blocks = text.count("```")
    if code_blocks < 20:
        errors.append(f"expected rich executable examples/data contracts; only {code_blocks} code fences")

    if "不应该追求“把 Suno 点得更快”" not in text:
        errors.append("missing first-principles conclusion against click-only automation")

    if "真实打开 Chrome" not in text or "真实点击 Suno Create" not in text:
        errors.append("missing human-gate language for real Chrome/Suno actions")

    if errors:
        return fail(errors)

    print(f"Verified Suno Music Producer plan document: {PLAN}")
    print(f"- chars: {len(text)}")
    print(f"- lines: {line_count}")
    print(f"- code_fences: {code_blocks}")
    print("- decision: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
