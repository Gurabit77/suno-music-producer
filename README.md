# Suno Music Producer

## 中文介绍

Suno Music Producer 是一个面向 Suno 和其他 AI 音乐生成流程的本地工具箱。它不是一键生成歌曲的机器人，而是帮助创作者把一个模糊想法整理成可复用、可审查、可迭代的音乐制作包。

它关注四件事：

- 把创作想法整理成歌词、曲风、排除项、批次计划和评审标准。
- 在使用参考曲、音频种子、和弦骨架之前做版权和相似性边界检查。
- 记录每一版 prompt、生成批次、听感评审和下一步修改变量。
- 为后续 DAW 处理、发行前检查、项目归档提供结构化文件和验证脚本。

这个仓库适合：

- 想用 Suno 做更稳定、更像真实制作流程的音乐创作者。
- 想把 AI 音乐 prompt、版本迭代、听感评审流程沉淀成本地文件的人。
- 想研究 AI 音乐工作流、提示词审查、参考曲合法转译和发行前检查的人。

这个仓库不包含：

- 已生成歌曲、历史单曲项目或私人听感记录。
- Suno 账号数据、浏览器状态、cookies、API keys 或任何密钥。
- 私人知识库内容、本机绝对路径或个人项目日志。

### 快速开始

```bash
python3 tools/create_music_song_project.py --help
python3 tools/plan_music_generation_route.py --brief "一首适合夜晚开车听的华语流行歌，温暖吉他和克制鼓组"
python3 tools/prepare_music_effect_first_suno_run.py --brief "一首适合短视频的明亮 city-pop demo"
```

创建一个本地单曲项目：

```bash
python3 tools/create_music_song_project.py --project-root song-projects/example-song
```

建议把生成结果、单曲项目、导出文件放在被 `.gitignore` 忽略的本地目录，例如 `song-projects/`、`outputs/` 或其他私有工作目录。

### 安全边界

这个工具箱只做离线准备、审查和记录。它不应该：

- 未经明确人工确认就上传音频。
- 自动点击 Generate/Create/Cover 或消耗账号额度。
- 使用非官方 Suno API、cookies、session 提取、验证码绕过或账号 token 抓取。
- 复制具名艺人、在世歌手声音、旋律、歌词、stem、采样或第三方歌曲。

## English Overview

Suno Music Producer is a local toolkit for planning, auditing, and preparing Suno and AI music generation workflows. It is not a one-click song generator. It helps creators turn a rough idea into a reusable, reviewable, and iterable production package.

It focuses on four jobs:

- Turn a creative brief into lyrics, style text, exclude terms, batch plans, and review criteria.
- Check rights and similarity boundaries before using references, audio seeds, or chord skeletons.
- Track prompt versions, generation batches, listening reviews, and the next changed variable.
- Provide structured files and verifier scripts for DAW handoff, release checks, and project archiving.

This repository is useful for:

- Creators who want a steadier, more production-like Suno workflow.
- People who want to keep AI music prompts, iterations, and listening reviews in local files.
- Researchers or builders studying AI music workflows, prompt audits, reference translation, and release readiness.

This repository does not include:

- Generated songs, historical song projects, or private listening notes.
- Suno account data, browser state, cookies, API keys, or credentials.
- Private knowledge-base content, local machine paths, or personal project logs.

### Quick Start

```bash
python3 tools/create_music_song_project.py --help
python3 tools/plan_music_generation_route.py --brief "A late-night Mandarin pop ballad with warm guitar and restrained drums"
python3 tools/prepare_music_effect_first_suno_run.py --brief "A hopeful city-pop demo for a short video"
```

Create a local song project:

```bash
python3 tools/create_music_song_project.py --project-root song-projects/example-song
```

Keep generated outputs, song projects, and exports in ignored local folders such as `song-projects/`, `outputs/`, or another private workspace outside this repository.

### Optional Local Paths

Some verifier scripts can be adapted to a private Obsidian vault or a local prompt-methodology folder. Keep those paths out of Git and pass them through environment variables or command-line arguments when you customize the toolkit.

Suggested private environment variables:

```bash
export OBSIDIAN_VAULT="/path/to/your/obsidian-vault"
export SUNO_PROMPT_METHODOLOGY="/path/to/your/suno-prompt-methodology"
export SUNO_MUSIC_PRODUCER_ROOT="$PWD"
```

Do not commit `.env` files or private vault exports.

### Safety Boundaries

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
