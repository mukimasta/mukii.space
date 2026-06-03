#!/usr/bin/env python3
"""Scaffold English SoundMat section (no body translation)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZH_DIR = ROOT / "content" / "soundmat"
EN_DIR = ZH_DIR / "en"

ARTICLES = [
    ("soundmat-1-idea.md", "SoundMat (1) Idea", "SoundMat (1) Idea"),
    ("soundmat-2-philosophy.md", "SoundMat (2) Philosophy 产品设计哲学", "SoundMat (2) Product Design Philosophy"),
    ("soundmat-3-exterior-design.md", "SoundMat (3) 外观设计", "SoundMat (3) Exterior Design"),
    ("soundmat-4-structural-design.md", "SoundMat (4) 结构设计", "SoundMat (4) Structural Design"),
    ("soundmat-5-sensor-principles-and-design.md", "SoundMat (5) 传感器原理及设计", "SoundMat (5) Sensor Principles and Design"),
    ("soundmat-6-electronics-system-design.md", "SoundMat (6) 电子系统设计", "SoundMat (6) Electronics System Design"),
    ("soundmat-7-firmware-design.md", "SoundMat (7) 固件设计", "SoundMat (7) Firmware Design"),
    (
        "soundmat-8-interaction-and-sonification.md",
        "SoundMat (8) 交互与声音化设计 Interaction and Sonification",
        "SoundMat (8) Interaction and Sonification Design",
    ),
    ("soundmat-9-structural-manufacturing.md", "SoundMat (9) 结构制造", "SoundMat (9) Structural Manufacturing"),
    ("soundmat-10-sensor-manufacturing.md", "SoundMat (10) 传感器制造", "SoundMat (10) Sensor Manufacturing"),
    ("soundmat-11-electronics-manufacturing.md", "SoundMat (11) 电子系统制造", "SoundMat (11) Electronics Manufacturing"),
    (
        "soundmat-12-software-design-and-development.md",
        "SoundMat (12) 软件设计与开发",
        "SoundMat (12) Software Design and Development",
    ),
    ("soundmat-13-epilogue-and-summary.md", "SoundMat (13) 尾声与总结", "SoundMat (13) Epilogue and Summary"),
    ("soundmat-14-timeline.md", "SoundMat (14) 时间线", "SoundMat (14) Timeline"),
    ("soundmat-15-network-solution.md", "SoundMat (15) 网络解决方案", "SoundMat (15) Network Solution"),
    (
        "soundmat-16-software-deployment-performance.md",
        "SoundMat (16) 软件部署性能优化",
        "SoundMat (16) Software Deployment Performance Optimization",
    ),
    ("soundmat-presentation.md", "SoundMat Presentation", "SoundMat Presentation"),
]

PLACEHOLDER = "*English translation in progress.*\n"


def slug(filename: str) -> str:
    return filename.removesuffix(".md")


def split_frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = text[m.end() :]
    meta: dict[str, str | list[str]] = {}
    key: str | None = None
    for line in fm_raw.splitlines():
        if line.startswith("  - "):
            if key == "aliases":
                meta.setdefault("aliases", [])
                assert isinstance(meta["aliases"], list)
                meta["aliases"].append(line[4:].strip())
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        v = v.strip().strip('"')
        if key == "aliases":
            meta[key] = []
        else:
            meta[key] = v
    return meta, body


def build_fm(
    title: str,
    lang: str,
    key: str,
    *,
    description: str | None = None,
    aliases: list[str] | None = None,
) -> str:
    lines = [
        f'title: "{title}"',
        f"docLang: {lang}",
        f"translationKey: {key}",
        "alternates:",
        f"  zh: /soundmat/{key}/",
        f"  en: /soundmat/en/{key}/",
    ]
    if description:
        lines.append(f'description: "{description}"')
    if aliases:
        lines.append("aliases:")
        for a in aliases:
            lines.append(f"  - {a}")
    return "\n".join(lines)


def write_page(path: Path, fm: str, body: str) -> None:
    path.write_text(f"---\n{fm}\n---\n\n{body}", encoding="utf-8")


def update_zh(path: Path, title: str) -> None:
    key = slug(path.name)
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    desc = meta.get("description")
    aliases = meta.get("aliases")
    alias_list = aliases if isinstance(aliases, list) else None
    desc_str = desc if isinstance(desc, str) else None
    fm = build_fm(title, "zh", key, description=desc_str, aliases=alias_list)
    write_page(path, fm, body)


def create_en(path: Path, title: str) -> None:
    key = slug(path.name)
    fm = build_fm(title, "en", key, aliases=[f"/soundmat/en/{key}/"])
    write_page(path, fm, PLACEHOLDER)


def write_index_files() -> None:
    write_page(
        ZH_DIR / "_index.md",
        build_fm(
            "SoundMat",
            "zh",
            "soundmat-index",
            description="基于触觉传感与音乐的交互装置 · 设计笔记",
        ).replace(
            "  zh: /soundmat/soundmat-index/",
            "  zh: /soundmat/",
        ).replace(
            "  en: /soundmat/en/soundmat-index/",
            "  en: /soundmat/en/",
        ),
        """- [SoundMat (1) Idea](/soundmat/soundmat-1-idea/)
- [SoundMat (2) Philosophy 产品设计哲学](/soundmat/soundmat-2-philosophy/)
- [SoundMat (3) 外观设计](/soundmat/soundmat-3-exterior-design/)
- [SoundMat (4) 结构设计](/soundmat/soundmat-4-structural-design/)
- [SoundMat (5) 传感器原理及设计](/soundmat/soundmat-5-sensor-principles-and-design/)
- [SoundMat (6) 电子系统设计](/soundmat/soundmat-6-electronics-system-design/)
- [SoundMat (7) 固件设计](/soundmat/soundmat-7-firmware-design/)
- [SoundMat (8) 交互与声音化设计 Interaction and Sonification](/soundmat/soundmat-8-interaction-and-sonification/)
- [SoundMat (9) 结构制造](/soundmat/soundmat-9-structural-manufacturing/)
- [SoundMat (10) 传感器制造](/soundmat/soundmat-10-sensor-manufacturing/)
- [SoundMat (11) 电子系统制造](/soundmat/soundmat-11-electronics-manufacturing/)
- [SoundMat (12) 软件设计与开发](/soundmat/soundmat-12-software-design-and-development/)
- [SoundMat (13) 尾声与总结](/soundmat/soundmat-13-epilogue-and-summary/)

附录

- [SoundMat (14) 时间线](/soundmat/soundmat-14-timeline/)
- [SoundMat (15) 网络解决方案](/soundmat/soundmat-15-network-solution/)
- [SoundMat (16) 软件部署性能优化](/soundmat/soundmat-16-software-deployment-performance/)

其他相关文档

- [SoundMat Presentation](/soundmat/soundmat-presentation/)
""",
    )
    EN_DIR.mkdir(parents=True, exist_ok=True)
    write_page(
        EN_DIR / "_index.md",
        build_fm(
            "SoundMat",
            "en",
            "soundmat-index",
            description="Interactive installation · tactile sensing and music · design notes",
        ).replace(
            "  zh: /soundmat/soundmat-index/",
            "  zh: /soundmat/",
        ).replace(
            "  en: /soundmat/en/soundmat-index/",
            "  en: /soundmat/en/",
        ),
        """- [SoundMat (1) Idea](/soundmat/en/soundmat-1-idea/)
- [SoundMat (2) Product Design Philosophy](/soundmat/en/soundmat-2-philosophy/)
- [SoundMat (3) Exterior Design](/soundmat/en/soundmat-3-exterior-design/)
- [SoundMat (4) Structural Design](/soundmat/en/soundmat-4-structural-design/)
- [SoundMat (5) Sensor Principles and Design](/soundmat/en/soundmat-5-sensor-principles-and-design/)
- [SoundMat (6) Electronics System Design](/soundmat/en/soundmat-6-electronics-system-design/)
- [SoundMat (7) Firmware Design](/soundmat/en/soundmat-7-firmware-design/)
- [SoundMat (8) Interaction and Sonification Design](/soundmat/en/soundmat-8-interaction-and-sonification/)
- [SoundMat (9) Structural Manufacturing](/soundmat/en/soundmat-9-structural-manufacturing/)
- [SoundMat (10) Sensor Manufacturing](/soundmat/en/soundmat-10-sensor-manufacturing/)
- [SoundMat (11) Electronics Manufacturing](/soundmat/en/soundmat-11-electronics-manufacturing/)
- [SoundMat (12) Software Design and Development](/soundmat/en/soundmat-12-software-design-and-development/)
- [SoundMat (13) Epilogue and Summary](/soundmat/en/soundmat-13-epilogue-and-summary/)

Appendix

- [SoundMat (14) Timeline](/soundmat/en/soundmat-14-timeline/)
- [SoundMat (15) Network Solution](/soundmat/en/soundmat-15-network-solution/)
- [SoundMat (16) Software Deployment Performance Optimization](/soundmat/en/soundmat-16-software-deployment-performance/)

Related Documents

- [SoundMat Presentation](/soundmat/en/soundmat-presentation/)
""",
    )


def main() -> None:
    EN_DIR.mkdir(parents=True, exist_ok=True)
    for filename, zh_title, en_title in ARTICLES:
        update_zh(ZH_DIR / filename, zh_title)
        create_en(EN_DIR / filename, en_title)
        print(filename)
    write_index_files()
    print("index files written")


if __name__ == "__main__":
    main()
