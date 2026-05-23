#!/usr/bin/env python3
"""Sync SoundMat notes from Obsidian Vault into this Hugo blog."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_VAULT = Path.home() / "Documents/Obsidian Vault"
DEFAULT_IMAGE_MAP = SCRIPT_DIR / "soundmat-image-map.json"

INDEX_DESCRIPTION = "基于触觉传感与音乐的交互装置 · 设计笔记"

# Obsidian filename -> Hugo slug/title/wiki labels. Order is not used for the index;
# index order comes from SoundMat.md in the vault.
ARTICLES: list[dict] = [
    {
        "obsidian": "SoundMat (1)  Idea.md",
        "slug": "soundmat-1-idea",
        "title": "SoundMat (1) Idea",
        "wiki": ["SoundMat (1)  Idea"],
    },
    {
        "obsidian": "SoundMat (2)  Philosophy 产品设计哲学.md",
        "slug": "soundmat-2-philosophy",
        "title": "SoundMat (2) Philosophy 产品设计哲学",
        "wiki": ["SoundMat (2)  Philosophy 产品设计哲学"],
    },
    {
        "obsidian": "SoundMat (3)  外观设计.md",
        "slug": "soundmat-3-exterior-design",
        "title": "SoundMat (3) 外观设计",
        "wiki": ["SoundMat (3)  外观设计"],
        "aliases": ["/soundmat/soundmat-3-waiguan-sheji/"],
    },
    {
        "obsidian": "SoundMat (4)  结构设计.md",
        "slug": "soundmat-4-structural-design",
        "title": "SoundMat (4) 结构设计",
        "wiki": ["SoundMat (4)  结构设计"],
        "aliases": ["/soundmat/soundmat-4-jiegou-sheji/"],
    },
    {
        "obsidian": "SoundMat (?)  传感器原理及设计.md",
        "slug": "soundmat-question-sensor-principles-and-design",
        "title": "SoundMat (?) 传感器原理及设计",
        "wiki": ["SoundMat (?)  传感器原理及设计"],
    },
    {
        "obsidian": "SoundMat (?)  电子系统设计.md",
        "slug": "soundmat-question-electronics-system-design",
        "title": "SoundMat (?) 电子系统设计",
        "wiki": ["SoundMat (?)  电子系统设计"],
    },
    {
        "obsidian": "SoundMat (?)  固件设计.md",
        "slug": "soundmat-question-firmware-design",
        "title": "SoundMat (?) 固件设计",
        "wiki": ["SoundMat (?)  固件设计"],
    },
    {
        "obsidian": None,
        "slug": "soundmat-question-placeholder",
        "title": "SoundMat (?) ",
        "wiki": ["SoundMat (?)  "],
    },
    {
        "obsidian": "SoundMat (?)  交互与声音化设计 Interaction and Sonification.md",
        "slug": "soundmat-question-interaction-and-sonification",
        "title": "SoundMat (?) 交互与声音化设计 Interaction and Sonification",
        "wiki": ["SoundMat (?)  交互与声音化设计 Interaction and Sonification"],
    },
    {
        "obsidian": "SoundMat (?)  结构制造.md",
        "slug": "soundmat-question-structural-manufacturing",
        "title": "SoundMat (?) 结构制造",
        "wiki": ["SoundMat (?)  结构制造"],
    },
    {
        "obsidian": "SoundMat (?)  传感器制造.md",
        "slug": "soundmat-question-sensor-manufacturing",
        "title": "SoundMat (?) 传感器制造",
        "wiki": ["SoundMat (?)  传感器制造"],
    },
    {
        "obsidian": "SoundMat (?)  电子系统制造.md",
        "slug": "soundmat-question-electronics-manufacturing",
        "title": "SoundMat (?) 电子系统制造",
        "wiki": ["SoundMat (?)  电子系统制造"],
    },
    {
        "obsidian": "SoundMat 尾声与总结.md",
        "slug": "soundmat-epilogue-and-summary",
        "title": "SoundMat 尾声与总结",
        "wiki": ["SoundMat 尾声与总结"],
    },
    {
        "obsidian": "SoundMat 时间线.md",
        "slug": "soundmat-timeline",
        "title": "SoundMat 时间线",
        "wiki": ["SoundMat 时间线"],
    },
]

WIKI_LINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
IMAGE_RE = re.compile(r"!\[\[([^\]|]+?)(?:\s*\|\s*\d+)?\s*\]\]\s*$")
NEXT_LINK_RE = re.compile(r"(下一篇：)\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")


@dataclass
class Article:
    obsidian: str | None
    slug: str
    title: str
    wiki: list[str]
    aliases: list[str]


def load_articles() -> list[Article]:
    articles: list[Article] = []
    for item in ARTICLES:
        articles.append(
            Article(
                obsidian=item.get("obsidian"),
                slug=item["slug"],
                title=item["title"],
                wiki=item["wiki"],
                aliases=item.get("aliases", []),
            )
        )
    return articles


def build_wiki_map(articles: list[Article]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for article in articles:
        for target in article.wiki:
            pairs.append((target, article.slug))
    pairs.sort(key=lambda pair: len(pair[0]), reverse=True)
    return pairs


def slugify_filename(name: str) -> str:
    stem = Path(name).name
    stem = re.sub(r"\s+", "-", stem.strip())
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem)
    stem = re.sub(r"-+", "-", stem).strip("-").lower()
    return stem or "image"


def load_image_map(path: Path) -> dict[str, str]:
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def save_image_map(path: Path, image_map: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(dict(sorted(image_map.items())), handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def resolve_image_name(source: str, image_map: dict[str, str]) -> str:
    if source in image_map:
        return image_map[source]

    ext = Path(source).suffix.lower() or ".png"
    base = slugify_filename(source)
    if not base.endswith(ext.lstrip(".")):
        base = f"{base}{ext}"
    candidate = base
    suffix = 1
    used = set(image_map.values())
    while candidate in used:
        candidate = f"{Path(base).stem}-{suffix}{ext}"
        suffix += 1
    image_map[source] = candidate
    return candidate


def should_use_next_line_as_alt(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("#", ">", "|", "[", "!", "下一篇", "---", "$$", "模块链接", "其中")):
        return False
    if stripped.startswith("("):
        return False
    if stripped.startswith(("图 ", "图\t", "效果图")):
        return True
    if stripped.startswith("（") and stripped.endswith("）"):
        return True
    return False


def convert_images(text: str, vault: Path, static_dir: Path, image_map: dict[str, str], dry_run: bool) -> str:
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = IMAGE_RE.match(line.strip())
        if not match:
            out.append(line)
            i += 1
            continue

        source = match.group(1).strip()
        static_name = resolve_image_name(source, image_map)
        alt = ""
        if i + 1 < len(lines) and should_use_next_line_as_alt(lines[i + 1]):
            alt = lines[i + 1].strip()
            i += 1

        src_path = vault / source
        dst_path = static_dir / static_name
        if not src_path.exists():
            print(f"warning: missing image in vault: {source}", file=sys.stderr)
        elif not dry_run:
            static_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)

        out.append(f"![{alt}](/soundmat/{static_name})")
        i += 1

    return "\n".join(out)


def convert_wiki_links(text: str, wiki_map: list[tuple[str, str]]) -> str:
    def repl(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        for wiki_target, slug in wiki_map:
            if target == wiki_target.strip():
                return f"[{target}](/soundmat/{slug}/)"
        return f"[{target}](#)"
    return WIKI_LINK_RE.sub(repl, text)


def convert_next_links(text: str, wiki_map: list[tuple[str, str]]) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1)
        target = match.group(2).strip()
        for wiki_target, slug in wiki_map:
            if target == wiki_target.strip():
                return f"{prefix}[{target}](/soundmat/{slug}/)"
        return match.group(0)
    text = NEXT_LINK_RE.sub(repl, text)
    return re.sub(r"下一篇：\s*$", "", text, flags=re.MULTILINE)


def front_matter(article: Article) -> str:
    lines = ["---", f'title: "{article.title}"', "aliases:"]
    lines.append(f"  - /soundmat/{article.slug}/")
    for alias in article.aliases:
        lines.append(f"  - {alias}")
    lines.append("---")
    return "\n".join(lines)


def normalize_label(label: str) -> str:
    return re.sub(r"\s{2,}", " ", label.strip())


def parse_index_entries(index_text: str, wiki_map: list[tuple[str, str]]) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for match in WIKI_LINK_RE.finditer(index_text):
        label = normalize_label(match.group(1))
        slug = None
        for wiki_target, mapped_slug in wiki_map:
            if label == normalize_label(wiki_target):
                slug = mapped_slug
                break
        if slug is None:
            print(f"warning: index link not mapped: {label}", file=sys.stderr)
            continue
        entries.append((label, slug))
    return entries


def write_index(content_dir: Path, entries: list[tuple[str, str]], dry_run: bool) -> None:
    lines = [
        "---",
        'title: "SoundMat"',
        f'description: "{INDEX_DESCRIPTION}"',
        "---",
        "",
    ]
    for label, slug in entries:
        lines.append(f"- [{label}](/soundmat/{slug}/)")
    lines.append("")
    target = content_dir / "_index.md"
    body = "\n".join(lines)
    if dry_run:
        print(f"would write {target}")
        return
    target.write_text(body, encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


def sync_article(
    article: Article,
    vault: Path,
    content_dir: Path,
    static_dir: Path,
    wiki_map: list[tuple[str, str]],
    image_map: dict[str, str],
    dry_run: bool,
) -> None:
    target = content_dir / f"{article.slug}.md"
    if article.obsidian is None:
        body = ""
    else:
        source = vault / article.obsidian
        if not source.exists():
            print(f"warning: missing note: {article.obsidian}", file=sys.stderr)
            body = ""
        else:
            body = source.read_text(encoding="utf-8").strip()
            body = convert_images(body, vault, static_dir, image_map, dry_run)
            body = convert_wiki_links(body, wiki_map)
            body = convert_next_links(body, wiki_map)

    output = front_matter(article) + "\n\n\n" + body
    if body:
        output += "\n"

    if dry_run:
        print(f"would write {target}")
        return

    content_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(output, encoding="utf-8")
    print(f"wrote {target.relative_to(REPO_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT, help="Obsidian vault path")
    parser.add_argument("--content", type=Path, default=REPO_ROOT / "content/soundmat")
    parser.add_argument("--static", type=Path, default=REPO_ROOT / "static/soundmat")
    parser.add_argument("--image-map", type=Path, default=DEFAULT_IMAGE_MAP)
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    args = parser.parse_args()

    if not args.vault.exists():
        print(f"error: vault not found: {args.vault}", file=sys.stderr)
        return 1

    articles = load_articles()
    wiki_map = build_wiki_map(articles)
    image_map = load_image_map(args.image_map)

    index_path = args.vault / "SoundMat.md"
    if not index_path.exists():
        print(f"error: index note not found: {index_path}", file=sys.stderr)
        return 1

    index_entries = parse_index_entries(index_path.read_text(encoding="utf-8"), wiki_map)
    write_index(args.content, index_entries, args.dry_run)

    for article in articles:
        sync_article(
            article,
            args.vault,
            args.content,
            args.static,
            wiki_map,
            image_map,
            args.dry_run,
        )

    if not args.dry_run:
        save_image_map(args.image_map, image_map)
        print(f"updated {args.image_map.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
