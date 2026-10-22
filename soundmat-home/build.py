# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["jinja2>=3.1", "pillow>=10", "fonttools>=4.50", "brotli>=1.1"]
# ///
"""Build the SoundMat homepage into the Hugo static folder.

    uv run soundmat-home/build.py

Sources (this folder): content.toml (copy), page.html (structure), style.css,
main.js, img/ (photos), fonts/ (full font files, fetched on first run).

Output (served by Hugo as-is):
    static/soundmat/index.html      Chinese page, /soundmat/
    static/soundmat/en/index.html   English page, /soundmat/en/
    static/soundmat/home/           fingerprinted CSS, JS, fonts, images
"""

from __future__ import annotations

import hashlib
import html
import re
import sys
import tomllib
import urllib.request
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DOCS = REPO / "content/soundmat/docs"
OUT = REPO / "static/soundmat"
ASSETS = OUT / "home"
ASSET_URL = "/soundmat/home/"
SITE = "https://mukii.space"
LANGS = ("zh", "en")
URLS = {"zh": "/soundmat/", "en": "/soundmat/en/"}
DOCS_URLS = {"zh": "/soundmat/docs/", "en": "/soundmat/docs/en/"}

# Image widths to generate; a width larger than the source is skipped.
BLEED_WIDTHS = (800, 1280, 1920, 2400)
STRIP_WIDTHS = (480, 800, 1200)
STRIP_SIZES = "(max-width: 560px) 82vw, (max-width: 789px) 300px, (max-width: 1473px) 38vw, 560px"

GOOGLE_FONTS = "https://github.com/google/fonts/raw/main/ofl/"
FONTS = [
    # family, css weight, source file, download path, variable axis limits
    ("IBM Plex Sans", "300 500", "IBMPlexSans[wdth,wght].ttf", "ibmplexsans/IBMPlexSans%5Bwdth,wght%5D.ttf",
     {"wght": (300, 500), "wdth": 100}),
    ("IBM Plex Mono", "400", "IBMPlexMono-Regular.ttf", "ibmplexmono/IBMPlexMono-Regular.ttf", None),
    ("IBM Plex Mono", "500", "IBMPlexMono-Medium.ttf", "ibmplexmono/IBMPlexMono-Medium.ttf", None),
    ("Noto Sans SC", "300 500", "NotoSansSC[wght].ttf", "notosanssc/NotoSansSC%5Bwght%5D.ttf",
     {"wght": (300, 500)}),
]


class BuildError(Exception):
    pass


def short_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:10]


# ---------------------------------------------------------------- content

def resolve(value, lang: str, path: str = ""):
    """Pick one language out of {zh, en} pairs, recursively."""
    if isinstance(value, dict):
        keys = set(value)
        if keys & set(LANGS):
            missing = set(LANGS) - keys
            if missing or keys - set(LANGS):
                raise BuildError(f"{path}: needs exactly zh and en, has {sorted(keys)}")
            return value[lang]
        return {k: resolve(v, lang, f"{path}.{k}" if path else k) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v, lang, f"{path}[{i}]") for i, v in enumerate(value)]
    return value


def doc_titles() -> dict[str, dict[str, str]]:
    titles: dict[str, dict[str, str]] = {"zh": {}, "en": {}}
    for lang, folder in (("zh", DOCS), ("en", DOCS / "en")):
        for md in folder.glob("*.md"):
            m = re.search(r'^title:\s*"(.*)"\s*$', md.read_text(encoding="utf-8"), re.M)
            if m and md.stem != "_index":
                titles[lang][md.stem] = m.group(1)
    return titles


# ---------------------------------------------------------------- text markup

TRIGGER_RE = re.compile(r"\[([^\]]+)\]\^([a-z0-9-]+)([.,;:!?。，、；：！？）」』”’)]*)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
ITALIC_RE = re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])")
BARE_AMP_RE = re.compile(r"&(?!#?\w+;)")


class Markup:
    """Tiny text markup for content.toml; see the header of that file."""

    def __init__(self, notes: dict, sources_label: str, doc_url, used_notes: set):
        self.notes, self.sources_label, self.doc_url, self.used_notes = notes, sources_label, doc_url, used_notes

    def inline(self, text: str, newtab: bool = False, triggers: list | None = None) -> str:
        text = BARE_AMP_RE.sub("&amp;", text.strip())

        def link(m):
            label, url = m.group(1), m.group(2)
            if url.startswith("doc:"):
                url = self.doc_url(url[4:])
            extra = ' target="_blank" rel="noopener"' if newtab else ""
            return f'<a href="{html.escape(url)}"{extra}>{label}</a>'

        def trigger(m):
            label, note, punct = m.groups()
            if note not in self.notes:
                raise BuildError(f"footnote [{label}]^{note}: no [notes.{note}] in content.toml")
            if triggers is None:
                raise BuildError(f"footnote [{label}]^{note} is not allowed here")
            triggers.append(note)
            self.used_notes.add(note)
            button = f'<button class="tn" aria-expanded="false" aria-controls="n-{note}">{label}</button>'
            return f'<span class="nb">{button}{punct}</span>' if punct else button

        text = TRIGGER_RE.sub(trigger, text)
        text = LINK_RE.sub(link, text)
        return ITALIC_RE.sub(r"<i>\1</i>", text)

    def note_card(self, note_id: str) -> str:
        note = self.notes[note_id]
        out = f'<div class="note-card" id="n-{note_id}" hidden><b>{self.inline(note["title"])}</b>'
        out += f'<p>{self.inline(note["body"])}</p>'
        if note.get("sources"):
            out += f'<span class="src">{self.sources_label}{self.inline(note["sources"], newtab=True)}</span>'
        return out + "</div>"

    def block(self, text: str) -> str:
        out = []
        for chunk in re.split(r"\n\s*\n", text.strip()):
            lines = [l.strip() for l in chunk.splitlines() if l.strip()]
            if all(re.match(r"1\.\s", l) for l in lines):
                items = "".join(f"<li>{self.inline(l[2:])}</li>" for l in lines)
                out.append(f"<ol>{items}</ol>")
                continue
            triggers: list[str] = []
            out.append(f"<p>{self.inline(' '.join(lines), triggers=triggers)}</p>")
            out.extend(self.note_card(n) for n in triggers)
        return "\n".join(out)


# ---------------------------------------------------------------- images

class Images:
    def __init__(self):
        self.made: set[Path] = set()
        self.cache: dict[tuple, dict] = {}

    def variants(self, name: str, widths) -> dict:
        key = (name, tuple(widths))
        if key in self.cache:
            return self.cache[key]
        src = HERE / "img" / name
        if not src.exists():
            raise BuildError(f"image not found: img/{name}")
        data = src.read_bytes()
        stem = name.rsplit(".", 1)[0].replace("/", "-")
        tag = short_hash(data)
        with Image.open(BytesIO(data)) as im:
            im = im.convert("RGB")
            w0, h0 = im.size
            sizes = [w for w in widths if w < w0] + [min(w0, max(widths))]
            files = []
            for w in sorted(set(sizes)):
                out = ASSETS / "img" / f"{stem}.{tag}-{w}.webp"
                if not out.exists():
                    out.parent.mkdir(parents=True, exist_ok=True)
                    im.resize((w, round(h0 * w / w0)), Image.LANCZOS).save(out, "WEBP", quality=80, method=6)
                self.made.add(out)
                files.append((w, ASSET_URL + "img/" + out.name))
        result = {"files": files, "width": w0, "height": h0}
        self.cache[key] = result
        return result

    def jpeg(self, name: str, width: int) -> str:
        src = HERE / "img" / name
        data = src.read_bytes()
        out = ASSETS / "img" / f"{name.rsplit('.', 1)[0].replace('/', '-')}.{short_hash(data)}-{width}.jpg"
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(BytesIO(data)) as im:
                im = im.convert("RGB")
                im.resize((width, round(im.height * width / im.width)), Image.LANCZOS).save(
                    out, "JPEG", quality=82, optimize=True, progressive=True)
        self.made.add(out)
        return ASSET_URL + "img/" + out.name

    def tag(self, name, alt, sizes, position=None, eager=False) -> str:
        widths = STRIP_WIDTHS if sizes != "100vw" else BLEED_WIDTHS
        v = self.variants(name, widths)
        srcset = ", ".join(f"{url} {w}w" for w, url in v["files"])
        default = v["files"][min(1, len(v["files"]) - 1)][1]
        attrs = [f'src="{default}"', f'srcset="{srcset}"', f'sizes="{sizes}"',
                 f'width="{v["width"]}"', f'height="{v["height"]}"', f'alt="{html.escape(alt)}"']
        attrs += ['fetchpriority="high"'] if eager else ['loading="lazy"', 'decoding="async"']
        if position:
            attrs.append(f'style="object-position:{position}"')
        return f"<img {' '.join(attrs)}>"


# ---------------------------------------------------------------- fonts

def visible_text(page: str) -> str:
    page = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S)
    attrs = " ".join(re.findall(r'(?:alt|aria-label|content)="([^"]*)"', page))
    return html.unescape(re.sub(r"<[^>]+>", " ", page) + " " + attrs)


def build_fonts(pages: dict[str, str], made: set[Path]) -> tuple[str, list[str]]:
    """Subset each font to the characters the pages use; return @font-face CSS."""
    all_text = "".join(pages.values())
    latin = "".join(sorted({c for c in all_text if ord(c) < 0x2E80})) + "‘’“”–—…·"
    cjk = "".join(sorted(set(visible_text(pages["zh"])))) + "“”‘’"
    css, preload = [], []
    for family, weight, filename, remote, axes in FONTS:
        src = HERE / "fonts" / filename
        if not src.exists():
            print(f"fetching {filename}", file=sys.stderr)
            src.parent.mkdir(exist_ok=True)
            urllib.request.urlretrieve(GOOGLE_FONTS + remote, src)
        chars = cjk if family == "Noto Sans SC" else latin
        key = short_hash(src.read_bytes()[:4096] + str(src.stat().st_size).encode() + chars.encode() + repr(axes).encode())
        out = ASSETS / "fonts" / f"{filename.split('[')[0].split('.')[0]}.{key}.woff2"
        if not out.exists():
            out.parent.mkdir(parents=True, exist_ok=True)
            font = TTFont(src)
            options = subset.Options()
            options.flavor = None
            options.layout_features = ["*"]
            options.name_IDs = ["*"]
            sub = subset.Subsetter(options)
            sub.populate(text=chars)
            sub.subset(font)
            if axes:
                font = instancer.instantiateVariableFont(font, axes)
            font.flavor = "woff2"
            font.save(out)
        made.add(out)
        url = ASSET_URL + "fonts/" + out.name
        css.append(f'@font-face{{font-family:"{family}";font-style:normal;font-weight:{weight};'
                   f'font-display:swap;src:url({url}) format("woff2")}}')
        if family in ("IBM Plex Sans", "Noto Sans SC"):
            preload.append(url)
    return "\n".join(css) + "\n", preload


# ---------------------------------------------------------------- build

def write_hashed(name: str, ext: str, data: str, made: set[Path]) -> str:
    out = ASSETS / f"{name}.{short_hash(data.encode())}.{ext}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(data, encoding="utf-8")
    made.add(out)
    return ASSET_URL + out.name


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.sub(r"\n\s*\n+", "\n", css).strip() + "\n"


def render(content: dict, titles, images: Images, env: Environment, assets: dict) -> dict[str, str]:
    pages, used_notes = {}, set()
    for lang in LANGS:
        t = resolve(content, lang)

        def doc_url(slug, lang=lang):
            if slug not in titles[lang]:
                raise BuildError(f"doc '{slug}' not found in content/soundmat/docs ({lang})")
            return f"{DOCS_URLS[lang]}{slug}/"

        markup = Markup(t.get("notes", {}), t["ui"]["sources"], doc_url, used_notes)
        film_poster = None
        if t["film"].get("src") and t["film"].get("poster"):
            film_poster = images.variants(t["film"]["poster"], (1920,))["files"][-1][1]
        pages[lang] = env.get_template("page.html").render(
            t=t, lang=lang, html_lang="zh-CN" if lang == "zh" else "en", site=SITE, urls=URLS,
            docs_url=DOCS_URLS[lang], md=markup.block, inline=markup.inline, img=images.tag,
            doc_url=doc_url, doc_title=lambda slug, lang=lang: (doc_url(slug), titles[lang][slug])[1],
            strip_sizes=STRIP_SIZES, film_poster=film_poster, **assets)
    unused = set(content.get("notes", {})) - used_notes
    if unused:
        raise BuildError(f"notes never referenced: {sorted(unused)}")
    return pages


def main() -> int:
    content = tomllib.loads((HERE / "content.toml").read_text(encoding="utf-8"))
    titles = doc_titles()
    env = Environment(loader=FileSystemLoader(HERE), undefined=StrictUndefined, autoescape=False,
                      trim_blocks=False, lstrip_blocks=False)
    images = Images()
    made = images.made

    og_image = images.jpeg(content["figures"]["hero"]["img"], 1200)
    js = write_hashed("main", "js", (HERE / "main.js").read_text(encoding="utf-8"), made)
    # First pass with placeholder asset names, only to learn which characters the pages use.
    draft = render(content, titles, images, env,
                   dict(css="", js=js, og_image=og_image, preload_fonts=[]))
    font_css, preload = build_fonts(draft, made)
    css = write_hashed("style", "css", minify_css(font_css + (HERE / "style.css").read_text(encoding="utf-8")), made)
    pages = render(content, titles, images, env,
                   dict(css=css, js=js, og_image=og_image, preload_fonts=preload))

    for lang, page in pages.items():
        out = OUT / URLS[lang].removeprefix("/soundmat/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print(f"wrote {out.relative_to(REPO)}")

    stale = [p for p in ASSETS.rglob("*") if p.is_file() and p not in made]
    for p in stale:
        p.unlink()
    total = sum(p.stat().st_size for p in made)
    print(f"{len(made)} assets in {ASSETS.relative_to(REPO)} ({total / 1e6:.1f} MB), removed {len(stale)} stale")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as e:
        print(f"build failed: {e}", file=sys.stderr)
        sys.exit(1)
