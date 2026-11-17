#!/usr/bin/env python3
"""Subset the site fonts to the characters the site actually uses.

Inter (Latin) and Noto Sans SC (Chinese) are downloaded from google/fonts
into .fontcache/ the first time, then cut down to the characters found in
content/, layouts/, themes/mukii/layouts/ and hugo.toml, and written as
woff2 into themes/mukii/static/fonts/.

Run from the repository root:  python3 scripts/build_fonts.py
build.sh runs it before Hugo; the generated files are also committed, so a
failed run (no network, no fonttools) still leaves working fonts.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".fontcache"
OUT = ROOT / "themes" / "mukii" / "static" / "fonts"
GOOGLE_FONTS = "https://github.com/google/fonts/raw/main/ofl/"

# output name, source file, download path, axis limits (None: keep all;
# the old fonttools on Jetson cannot cut Noto's weight range, its default is 100)
FONTS = [
    ("inter", "Inter[opsz,wght].ttf", "inter/Inter%5Bopsz,wght%5D.ttf", {"wght": (400, 600), "opsz": 14}),
    ("noto-sans-sc", "NotoSansSC[wght].ttf", "notosanssc/NotoSansSC%5Bwght%5D.ttf", None),
]
SOURCES = ["content", "layouts", "themes/mukii/layouts", "hugo.toml"]
TEXT_SUFFIXES = {".md", ".html", ".toml"}
# always keep: ASCII, Latin-1, common typography, CJK punctuation
ALWAYS = "".join(chr(c) for c in range(0x20, 0x250)) + "‘’“”–—…·•←→↑↓↗◇©™€" + "，。、；：？！（）《》「」『』【】〈〉…—～·"


def site_text() -> str:
    parts = []
    for name in SOURCES:
        p = ROOT / name
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.suffix in TEXT_SUFFIXES]
        for f in files:
            parts.append(f.read_text(encoding="utf-8", errors="ignore"))
    return "".join(parts)


def fetch(filename: str, remote: str) -> Path:
    src = CACHE / filename
    if not src.exists():
        print(f"fetching {filename}", file=sys.stderr)
        CACHE.mkdir(exist_ok=True)
        urllib.request.urlretrieve(GOOGLE_FONTS + remote, src)
    return src


def build(name: str, src: Path, axes: dict, chars: str) -> Path:
    font = TTFont(src)
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.flavor = "woff2"
    sub = subset.Subsetter(options)
    sub.populate(text=chars)
    sub.subset(font)
    if axes:
        font = instancer.instantiateVariableFont(font, axes)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{name}.woff2"
    font.flavor = "woff2"
    font.save(out)
    return out


def main() -> int:
    text = site_text()
    latin = "".join(sorted({c for c in text if ord(c) < 0x2E80} | set(ALWAYS)))
    cjk = "".join(sorted({c for c in text if ord(c) >= 0x2E80} | set(ALWAYS)))
    for name, filename, remote, axes in FONTS:
        chars = latin if name == "inter" else cjk
        out = build(name, fetch(filename, remote), axes, chars)
        print(f"{out.relative_to(ROOT)}: {len(chars)} chars, {out.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
