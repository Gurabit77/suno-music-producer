#!/usr/bin/env python3
"""Verify the Obsidian music knowledge system for the local task loop task."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

REQUIRED_GUARD_FILES = [
    VAULT / "CLAUDE.md",
    VAULT / "CODEX.md",
    WIKI / "系统" / "自动记录价值闸门.md",
    WIKI / "系统" / "知识新增工作流.md",
    WIKI / "index.md",
]

REQUIRED_STRUCTURE = [
    WIKI / "地图" / "音乐知识地图.md",
    WIKI / "概念" / "音乐" / "index.md",
    WIKI / "分析" / "音乐" / "index.md",
    WIKI / "实体" / "音乐人" / "index.md",
    WIKI / "来源" / "外部资料" / "音乐" / "index.md",
]

THEORY_TOPICS = [
    "乐理基础",
    "音程",
    "音阶",
    "调式",
    "调性",
    "和声功能",
    "级数",
    "流行和声",
    "摇滚和声",
    "节奏",
    "律动",
    "旋律",
    "曲式",
    "编曲",
    "制作",
    "歌词",
]

GENRE_TOPICS = [
    "流行音乐",
    "摇滚音乐",
    "日本流行",
    "华语流行",
    "韩语流行",
    "英语流行",
    "日本摇滚",
    "华语摇滚",
    "韩语摇滚",
    "英语摇滚",
]

ARTISTS = [
    "米津玄师",
    "YOASOBI",
    "Ado",
    "Official髭男dism",
    "King Gnu",
    "宇多田光",
    "Perfume",
    "あいみょん",
    "当山",
    "KOKIA",
    "周杰伦",
    "林俊杰",
    "陈奕迅",
    "邓紫棋",
    "薛之谦",
    "毛不易",
    "蔡徐坤",
    "BTS",
    "BLACKPINK",
    "IU",
    "EXO",
    "Stray Kids",
    "NewJeans",
    "aespa",
    "SEVENTEEN",
    "Taylor Swift",
    "The Weeknd",
    "Billie Eilish",
    "Dua Lipa",
    "Olivia Rodrigo",
    "Harry Styles",
    "Drake",
    "Ed Sheeran",
    "ONE OK ROCK",
    "MY FIRST STORY",
    "RADWIMPS",
    "Mrs. GREEN APPLE",
    "BUMP OF CHICKEN",
    "凛として時雨",
    "ASIAN KUNG-FU GENERATION",
    "Babymetal",
    "五月天",
    "万能青年旅店",
    "草东没有派对",
    "痛仰",
    "告五人",
    "回春丹",
    "DAY6",
    "FTISLAND",
    "CNBLUE",
    "JANNABI",
    "The Rose",
    "N.Flying",
    "Xdinary Heroes",
    "LUCY",
    "Arctic Monkeys",
    "Imagine Dragons",
    "Twenty One Pilots",
    "Foo Fighters",
    "Radiohead",
    "Måneskin",
    "Green Day",
    "The 1975",
]

ENTITY_SECTIONS = [
    "代表作品",
    "逐曲分析",
    "音乐语言",
    "和声",
    "旋律",
    "节奏",
    "编曲",
    "制作",
    "AI音乐",
    "相关来源",
]

GENERIC_ARTIST_PHRASES = [
    "学习重点不是模仿表面音色",
    "初听顺序：先听最大众传播的一首",
    "作品可从五个层次听",
    "可从五个层次听：鼓/打击乐、低音、和声乐器、旋律 hook、人声制作",
    "不要只写",
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", "", text)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def md_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def assert_path_under_vault(path: Path) -> None:
    resolved = path.resolve()
    vault = VAULT.resolve()
    if vault not in [resolved, *resolved.parents]:
        raise AssertionError(f"path is outside vault: {path}")


def frontmatter_ok(text: str, required_type: str | None = None) -> bool:
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end < 0:
        return False
    fm = text[: end + 4]
    required = ["title:", "type:", "tags:", "created:", "updated:"]
    if any(item not in fm for item in required):
        return False
    if required_type and f"type: {required_type}" not in fm:
        return False
    return True


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def page_for_name(files: list[Path], name: str) -> tuple[Path, str] | None:
    needle = normalize(name)
    for path in files:
        text = read(path)
        searchable = normalize(path.stem + "\n" + text[:1200])
        if needle in searchable:
            return path, text
    return None


def main() -> int:
    errors: list[str] = []

    if not VAULT.exists():
        errors.append(f"vault missing: {VAULT}")
    for path in REQUIRED_GUARD_FILES:
        if not path.exists():
            errors.append(f"required guard file missing: {path}")

    for path in REQUIRED_STRUCTURE:
        assert_path_under_vault(path)
        if not path.exists():
            errors.append(f"required music structure missing: {path}")

    concept_dir = WIKI / "概念" / "音乐"
    analysis_dir = WIKI / "分析" / "音乐"
    entity_dir = WIKI / "实体" / "音乐人"
    source_dir = WIKI / "来源" / "外部资料" / "音乐"

    concept_files = [p for p in md_files(concept_dir) if p.name != "index.md"]
    analysis_files = [p for p in md_files(analysis_dir) if p.name != "index.md"]
    entity_files = [p for p in md_files(entity_dir) if p.name != "index.md"]
    source_files = [p for p in md_files(source_dir) if p.name != "index.md"]

    if len(concept_files) < 14:
        errors.append(f"expected at least 14 music concept pages, found {len(concept_files)}")
    if len(analysis_files) < 10:
        errors.append(f"expected at least 10 music analysis pages, found {len(analysis_files)}")
    if len(entity_files) < 58:
        errors.append(f"expected at least 58 artist/band entity pages, found {len(entity_files)}")
    if len(source_files) < 8:
        errors.append(f"expected at least 8 external music source pages, found {len(source_files)}")

    concept_blob = "\n".join(read(p) for p in concept_files)
    missing_theory = [topic for topic in THEORY_TOPICS if topic not in concept_blob]
    if missing_theory:
        errors.append("missing theory topics in concept pages: " + ", ".join(missing_theory))

    analysis_blob = "\n".join(read(p) for p in analysis_files)
    missing_genres = [topic for topic in GENRE_TOPICS if topic not in analysis_blob]
    if missing_genres:
        errors.append("missing genre/language topics in analysis pages: " + ", ".join(missing_genres))

    thin_concepts = []
    for path in concept_files:
        length = compact_len(read(path))
        if length < 1600:
            thin_concepts.append(f"{path.name} ({length})")
    if thin_concepts:
        errors.append("concept pages too thin for professional notes: " + "; ".join(thin_concepts[:20]))

    thin_analyses = []
    for path in analysis_files:
        length = compact_len(read(path))
        if length < 2200:
            thin_analyses.append(f"{path.name} ({length})")
    if thin_analyses:
        errors.append("analysis pages too thin for comparative music study: " + "; ".join(thin_analyses[:20]))

    missing_artists: list[str] = []
    weak_artist_pages: list[str] = []
    bad_frontmatter: list[str] = []
    generic_phrase_hits = {phrase: 0 for phrase in GENERIC_ARTIST_PHRASES}
    for artist in ARTISTS:
        found = page_for_name(entity_files, artist)
        if found is None:
            missing_artists.append(artist)
            continue
        path, text = found
        if not frontmatter_ok(text, "entity"):
            bad_frontmatter.append(str(path))
        body_len = compact_len(text)
        section_hits = sum(1 for section in ENTITY_SECTIONS if section in text)
        work_title_hits = text.count("《")
        song_analysis_markers = text.count("### 《") + text.count("#### 《")
        if body_len < 2800 or section_hits < 7 or work_title_hits < 3 or song_analysis_markers < 3:
            weak_artist_pages.append(f"{artist} -> {path.name}")
        for phrase in GENERIC_ARTIST_PHRASES:
            if phrase in text:
                generic_phrase_hits[phrase] += 1

    if missing_artists:
        errors.append("missing dedicated artist/band pages: " + ", ".join(missing_artists))
    if weak_artist_pages:
        errors.append("artist/band pages too thin or missing core sections: " + "; ".join(weak_artist_pages[:20]))
    if bad_frontmatter:
        errors.append("entity pages missing required frontmatter/type: " + "; ".join(bad_frontmatter[:20]))
    repeated_generic = [
        f"{phrase} ({count})"
        for phrase, count in generic_phrase_hits.items()
        if count > 8
    ]
    if repeated_generic:
        errors.append(
            "artist/band pages are still template-like; repeated generic phrases: "
            + "; ".join(repeated_generic)
        )

    required_index_mentions = [
        "音乐知识地图",
        "音乐",
        "流行音乐",
        "摇滚音乐",
    ]
    for index_path in [WIKI / "index.md", WIKI / "地图" / "index.md"]:
        if index_path.exists():
            index_text = read(index_path)
            missing = [item for item in required_index_mentions if item not in index_text]
            if missing:
                errors.append(f"{index_path} missing mentions: {', '.join(missing)}")

    map_path = WIKI / "地图" / "音乐知识地图.md"
    if map_path.exists():
        map_text = read(map_path)
        map_required = [
            "基础乐理",
            "流行音乐",
            "摇滚音乐",
            "日本",
            "华语",
            "韩语",
            "英语",
            "代表艺人",
            "AI音乐",
        ]
        missing = [item for item in map_required if item not in map_text]
        if missing:
            errors.append("music map missing sections: " + ", ".join(missing))

    if errors:
        print("Music Obsidian verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Music Obsidian verification passed.")
    print(f"- concept pages: {len(concept_files)}")
    print(f"- analysis pages: {len(analysis_files)}")
    print(f"- artist/band entity pages: {len(entity_files)}")
    print(f"- source pages: {len(source_files)}")
    print(f"- vault: {VAULT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
