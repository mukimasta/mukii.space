#!/usr/bin/env python3
"""One-off: migrate SoundMat docs from Obsidian vault to Hugo content/soundmat."""

import re
from pathlib import Path

VAULT = Path("/Users/mukii/Documents/Obsidian Vault")
CONTENT = Path(__file__).resolve().parent.parent / "content" / "soundmat"

ARTICLES = [
    ("SoundMat (1)  Idea.md", "soundmat-1-idea.md", "SoundMat (1) Idea"),
    ("SoundMat (2)  Philosophy 产品设计哲学.md", "soundmat-2-philosophy.md", "SoundMat (2) Philosophy 产品设计哲学"),
    ("SoundMat (3)  外观设计.md", "soundmat-3-exterior-design.md", "SoundMat (3) 外观设计"),
    ("SoundMat (4)  结构设计.md", "soundmat-4-structural-design.md", "SoundMat (4) 结构设计"),
    ("SoundMat (5)  传感器原理及设计.md", "soundmat-5-sensor-principles-and-design.md", "SoundMat (5) 传感器原理及设计"),
    ("SoundMat (6)  电子系统设计.md", "soundmat-6-electronics-system-design.md", "SoundMat (6) 电子系统设计"),
    ("SoundMat (7)  固件设计.md", "soundmat-7-firmware-design.md", "SoundMat (7) 固件设计"),
    ("SoundMat (8)  交互与声音化设计 Interaction and Sonification.md", "soundmat-8-interaction-and-sonification.md", "SoundMat (8) 交互与声音化设计 Interaction and Sonification"),
    ("SoundMat (9)  结构制造.md", "soundmat-9-structural-manufacturing.md", "SoundMat (9) 结构制造"),
    ("SoundMat (10)  传感器制造.md", "soundmat-10-sensor-manufacturing.md", "SoundMat (10) 传感器制造"),
    ("SoundMat (11)  电子系统制造.md", "soundmat-11-electronics-manufacturing.md", "SoundMat (11) 电子系统制造"),
    ("SoundMat (12)  软件设计与开发.md", "soundmat-12-software-design-and-development.md", "SoundMat (12) 软件设计与开发"),
    ("SoundMat (13)  尾声与总结.md", "soundmat-13-epilogue-and-summary.md", "SoundMat (13) 尾声与总结"),
    ("SoundMat (14)  时间线.md", "soundmat-14-timeline.md", "SoundMat (14) 时间线"),
    ("SoundMat (15)  网络解决方案.md", "soundmat-15-network-solution.md", "SoundMat (15) 网络解决方案"),
    ("SoundMat (16)  软件部署性能优化.md", "soundmat-16-software-deployment-performance.md", "SoundMat (16) 软件部署性能优化"),
    ("SoundMat Presentation.md", "soundmat-presentation.md", "SoundMat Presentation"),
]

OLD_ALIASES = {
    "soundmat-5-sensor-principles-and-design.md": ["/soundmat/soundmat-question-sensor-principles-and-design/"],
    "soundmat-6-electronics-system-design.md": ["/soundmat/soundmat-question-electronics-system-design/"],
    "soundmat-7-firmware-design.md": ["/soundmat/soundmat-question-firmware-design/"],
    "soundmat-8-interaction-and-sonification.md": ["/soundmat/soundmat-question-interaction-and-sonification/"],
    "soundmat-9-structural-manufacturing.md": ["/soundmat/soundmat-question-structural-manufacturing/"],
    "soundmat-10-sensor-manufacturing.md": ["/soundmat/soundmat-question-sensor-manufacturing/"],
    "soundmat-11-electronics-manufacturing.md": ["/soundmat/soundmat-question-electronics-manufacturing/"],
    "soundmat-13-epilogue-and-summary.md": ["/soundmat/soundmat-epilogue-and-summary/"],
    "soundmat-14-timeline.md": ["/soundmat/soundmat-timeline/"],
    "soundmat-4-structural-design.md": ["/soundmat/soundmat-4-jiegou-sheji/"],
}

WIKI_TO_SLUG = {
    r"SoundMat \(1\)\s+Idea": "soundmat-1-idea",
    r"SoundMat \(2\)\s+Philosophy 产品设计哲学": "soundmat-2-philosophy",
    r"SoundMat \(3\)\s+外观设计": "soundmat-3-exterior-design",
    r"SoundMat \(4\)\s+结构设计": "soundmat-4-structural-design",
    r"SoundMat \(5\)\s+传感器原理及设计": "soundmat-5-sensor-principles-and-design",
    r"SoundMat \(6\)\s+电子系统设计": "soundmat-6-electronics-system-design",
    r"SoundMat \(7\)\s+固件设计": "soundmat-7-firmware-design",
    r"SoundMat \(8\)\s+交互与声音化设计 Interaction and Sonification": "soundmat-8-interaction-and-sonification",
    r"SoundMat \(9\)\s+结构制造": "soundmat-9-structural-manufacturing",
    r"SoundMat \(10\)\s+传感器制造": "soundmat-10-sensor-manufacturing",
    r"SoundMat \(11\)\s+电子系统制造": "soundmat-11-electronics-manufacturing",
    r"SoundMat \(12\)\s+软件设计与开发": "soundmat-12-software-design-and-development",
    r"SoundMat \(13\)\s+尾声与总结": "soundmat-13-epilogue-and-summary",
    r"SoundMat \(14\)\s+时间线": "soundmat-14-timeline",
    r"SoundMat \(15\)\s+网络解决方案": "soundmat-15-network-solution",
    r"SoundMat \(16\)\s+软件部署性能优化": "soundmat-16-software-deployment-performance",
    r"SoundMat Presentation": "soundmat-presentation",
}

IMAGE_MAP = {
    "Pasted image 20260415014755.png": "sensor-velostat-principle.png",
    "Pasted image 20260415013507.png": "sensor-divider-circuit.png",
    "Pasted image 20260415015646.png": "sensor-sandwich-structure.png",
    "Pasted image 20260503025912.png": "sensor-scanning-circuit.png",
    "Pasted image 20260503032130.png": "sensor-polar-array.png",
    "stitched-side-by-side.png": "sensor-final-design.png",
    "Pasted image 20260412023153.png": "exterior-render-no-light.png",
    "Pasted image 20260412023216.png": "exterior-render-with-light.png",
    "ChatGPT Image Apr 16, 2026, 07_32_25 PM.png": "exterior-render-chatgpt.png",
    "Pasted image 20260416001838.png": "structural-planter-bowl.png",
    "Pasted image 20260509155554.png": "electronics-architecture.png",
    "Pasted image 20260509155609.png": "electronics-architecture-design.png",
    "Pasted image 20260511024040.png": "electronics-power-module.png",
    "Pasted image 20260511024053.png": "electronics-compute-module.png",
    "Pasted image 20260511024112.png": "electronics-sensor-module.png",
    "esp32_dual_cd4067_mux_with_rings_v3 1.svg": "esp32-dual-cd4067-mux-with-rings-v3.svg",
    "Pasted image 20260511024125.png": "electronics-led-module.png",
    "bom.png": "electronics-bom.png",
    "Pasted image 20260516015119.png": "manufacturing-perfboard-layout-1.png",
    "Pasted image 20260516015053.png": "manufacturing-perfboard-layout-2.png",
    "FF06531F-3670-4B29-BBBE-F53C8D428439_1_105_c.jpeg": "manufacturing-buck-converter-1.jpeg",
    "19F53ACB-4C88-4019-B97E-1F0AAED3593F_1_105_c.jpeg": "manufacturing-buck-converter-2.jpeg",
    "948ED307-C543-45EB-B3D2-FBA04DA7BBD0_1_105_c.jpeg": "manufacturing-buck-converter-3.jpeg",
    "Pasted image 20260516015206.png": "manufacturing-led-power-board.png",
}

WIKI_PATTERN = re.compile(
    r"\[\[(" + "|".join(WIKI_TO_SLUG.keys()) + r")(?:#([^\]|]+))?(?:\s*\|\s*[^\]]+)?\]\]"
)

IMG_PATTERN = re.compile(r"!\[\[([^\]|]+?)(?:\s*\|\s*(\d+))?\]\]")


def anchor_slug(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def replace_wikilink(match: re.Match) -> str:
    title_key = None
    header = match.group(2)
    full = match.group(0)
    inner = full[2:-2].split("#")[0].split("|")[0].strip()
    for pattern, slug in WIKI_TO_SLUG.items():
        if re.fullmatch(pattern, inner):
            title_key = slug
            break
    if not title_key:
        return full
    url = f"/soundmat/{title_key}/"
    if header:
        url += f"#{anchor_slug(header)}"
    return f"[{inner}]({url})"


def replace_image(match: re.Match) -> str:
    name = match.group(1).strip()
    static = IMAGE_MAP.get(name)
    if not static:
        raise ValueError(f"Unknown image: {name!r}")
    return f"![](/soundmat/{static})"


def convert_body(text: str) -> str:
    text = IMG_PATTERN.sub(replace_image, text)
    text = WIKI_PATTERN.sub(replace_wikilink, text)
    # Fix any remaining wikilinks with flexible spacing
    for pattern, slug in WIKI_TO_SLUG.items():
        rx = re.compile(
            rf"\[\[{pattern}(?:#([^\]|]+))?(?:\s*\|\s*[^\]]+)?\]\]"
        )

        def repl(m, slug=slug):
            inner = m.group(0)[2:-2].split("#")[0].split("|")[0].strip()
            url = f"/soundmat/{slug}/"
            if m.group(1):
                url += f"#{anchor_slug(m.group(1))}"
            return f"[{inner}]({url})"

        text = rx.sub(repl, text)
    return text.strip() + "\n"


def strip_leading_h1(text: str, title: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        h1 = lines[0][2:].strip()
        if h1 in title or title in h1 or "SoundMat" in h1:
            return "\n".join(lines[1:]).lstrip("\n")
    return text


def frontmatter(title: str, slug: str, extra_aliases: list[str]) -> str:
    aliases = [f"/soundmat/{slug}/"] + extra_aliases
    lines = ["---", f'title: "{title}"', "aliases:"]
    for a in aliases:
        lines.append(f"  - {a}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def write_index():
    body = """---
title: "SoundMat"
description: "基于触觉传感与音乐的交互装置 · 设计笔记"
---

- [SoundMat (1) Idea](/soundmat/soundmat-1-idea/)
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
"""
    (CONTENT / "_index.md").write_text(body, encoding="utf-8")


def main():
    CONTENT.mkdir(parents=True, exist_ok=True)
    new_files = {out for _, out, _ in ARTICLES}

    for src_name, out_name, title in ARTICLES:
        src = VAULT / src_name
        if not src.exists():
            raise FileNotFoundError(src)
        raw = src.read_text(encoding="utf-8")
        raw = strip_leading_h1(raw, title)
        body = convert_body(raw)
        slug = out_name.removesuffix(".md")
        extra = OLD_ALIASES.get(out_name, [])
        out = frontmatter(title, slug, extra) + "\n" + body
        (CONTENT / out_name).write_text(out, encoding="utf-8")
        print(f"Wrote {out_name}")

    write_index()
    print("Wrote _index.md")

    for old in CONTENT.glob("*.md"):
        if old.name == "_index.md":
            continue
        if old.name not in new_files:
            old.unlink()
            print(f"Removed {old.name}")


if __name__ == "__main__":
    main()
