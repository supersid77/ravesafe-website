#!/usr/bin/env python3
"""
RaveSafe Community site builder.

  python3 build.py            build the live site into dist/
  python3 build.py --preview  build with relative links, for previewing without a server

What it does:
  - wraps every page in src/pages/ with the shared layout (header, footer)
  - swaps {{ photo "name" "size" }} for a shrunk WebP image if the original is in
    images-original/, or a labelled placeholder if it isn't yet
  - takes alt text from data/images.json, so it lives in one place
  - writes a sitemap, robots.txt, security headers and redirects

Needs Python 3 and Pillow (pip install pillow).
"""
import json, re, shutil, sys, html, os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
SRC, DIST = ROOT / "src", ROOT / "dist"
ORIG = ROOT / "images-original"
DL_ORIG = ROOT / "downloads"
missing_downloads = set()
SITE_URL = "https://ravesafecommunity.com"
PREVIEW = "--preview" in sys.argv

IMAGES = {k: v for k, v in json.loads((ROOT / "data/images.json").read_text()).items() if not k.startswith("_")}
SIZES = {
    "hero": ([800, 1200, 1600], "(min-width: 1240px) 600px, 100vw"),
    "wide": ([800, 1200, 1600], "(min-width: 1240px) 1200px, 100vw"),
    "card": ([400, 800], "(min-width: 1000px) 400px, (min-width: 640px) 50vw, 100vw"),
    "small": ([200, 400], "200px"),
    "logo": ([120, 240], "60px"),
}
EXTS = [".jpg", ".jpeg", ".png", ".webp"]
done_images = {}


def find_original(name):
    for ext in EXTS:
        p = ORIG / f"{name}{ext}"
        if p.exists():
            return p
    return None


def make_webp(name, widths):
    """Resize the original to each width (never upscaling) and save as WebP."""
    key = (name, tuple(widths))
    if key in done_images:
        return done_images[key]
    src = find_original(name)
    if not src:
        done_images[key] = None
        return None
    out_dir = DIST / "img"
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    pad = IMAGES.get(name, {}).get("pad")
    if pad:
        # Show the whole photo: fit it into the frame and fill the sides with a soft blurred copy
        from PIL import ImageFilter, ImageEnhance
        rw, rh = (int(x) for x in pad.split(":"))
        H = im.height; W = round(H * rw / rh)
        if W > im.width:
            bg = im.convert("RGB").resize((W, round(im.height * W / im.width)), Image.LANCZOS)
            top = (bg.height - H) // 2
            bg = bg.crop((0, top, W, top + H)).filter(ImageFilter.GaussianBlur(40))
            bg = ImageEnhance.Brightness(bg).enhance(0.55)
            bg.paste(im.convert("RGB"), ((W - im.width) // 2, 0))
            im = bg
    made = []
    for w in widths:
        w = min(w, im.width)
        h = round(im.height * w / im.width)
        fn = f"{name}-{w}.webp"
        if not any(m[1] == w for m in made):
            im.resize((w, h), Image.LANCZOS).save(out_dir / fn, "WEBP", quality=76, method=6)
            made.append((f"/img/{fn}", w, h))
    done_images[key] = made
    return made


def photo(name, size="card", cls=""):
    info = IMAGES.get(name)
    if info is None:
        raise SystemExit(f"Photo '{name}' is not listed in data/images.json")
    alt = info.get("alt", "")
    widths, sizes = SIZES[size]
    made = make_webp(name, widths)
    cls_attr = f' class="{cls}"' if cls else ""
    if made:
        srcset = ", ".join(f"{u} {w}w" for u, w, _ in made)
        u, w, h = made[-1]
        loading = {"hero": 'fetchpriority="high"', "logo": 'loading="eager"'}.get(size, 'loading="lazy"')
        pos = f' style="object-position: {info["position"]}"' if info.get("position") else ""
        return (f'<img{cls_attr} src="{u}" srcset="{srcset}" sizes="{sizes}" '
                f'width="{w}" height="{h}" alt="{html.escape(alt)}"{pos} {loading} decoding="async">')
    # Placeholder until the original arrives
    label = html.escape(alt) if alt else "Background photo"
    a11y = f'role="img" aria-label="{html.escape(alt)}"' if alt else 'aria-hidden="true"'
    return (f'<div class="ph {cls}" {a11y}><span class="ph__inner">'
            f'<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">'
            f'<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 17-5-5-9 7"/></svg>'
            f'<span class="ph__label">{label}</span><span class="ph__file">{name}</span></span></div>')


PHOTO_RE = re.compile(r'\{\{\s*photo\s+"([^"]+)"(?:\s+"([^"]*)")?(?:\s+"([^"]*)")?\s*\}\}')


# ---------- Heads Up (see headsup.py for the approval gate) ----------
import headsup


DISCLAIMER = ('<aside class="disclaimer" aria-label="Medical disclaimer"><div class="wrap disclaimer__inner">'
              '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
              '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16.5v.01"/></svg>'
              '<p><strong>We\'re not medically trained.</strong> Everything here is for informational purposes only and isn\'t medical advice. '
              'It doesn\'t replace a doctor, paramedic or proper first aid training. If someone is unwell, get help from on-site medics or welfare, '
              'or call <a href="tel:999">999</a>.</p></div></aside>')


def read_page(p):
    text = p.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if ": " in line)
    return meta, text[m.end():]


def relativise(page_html, depth):
    """For preview builds: turn /root links into relative ones that work without a server."""
    up = "../" * depth if depth else "./"

    def fix(url):
        if not url.startswith("/") or url.startswith("//"):
            return url
        url = url[1:]
        if url == "" or url.endswith("/"):
            url += "index.html"
        elif "#" in url and url.split("#")[0].endswith("/"):
            a, b = url.split("#", 1)
            url = a + "index.html#" + b
        return up + url

    page_html = re.sub(r'(href|src)="([^"]*)"', lambda m: f'{m.group(1)}="{fix(m.group(2))}"', page_html)
    page_html = re.sub(r'srcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(
        " ".join([fix(part.split()[0])] + part.split()[1:]) for part in m.group(1).split(", ")) + '"', page_html)
    return page_html


def build_icons():
    """Favicons, Apple and Android icons go at the site root, plus a small manifest so Android knows which icon to use."""
    for f in (SRC / "icons").iterdir():
        shutil.copy(f, DIST / f.name)
    manifest = {
        "name": "RaveSafe Community",
        "short_name": "RaveSafe",
        "start_url": "/",
        "display": "browser",
        "background_color": "#070B12",
        "theme_color": "#070B12",
        "icons": [
            {"src": "/pwa-icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/pwa-icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/pwa-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (DIST / "site.webmanifest").write_text(json.dumps(manifest, indent=2))


def build_audio():
    """Shrink every track in audio-original/ to a phone-friendly 96kbps MP3 (needs ffmpeg, else copies as is)."""
    src_dir = ROOT / "audio-original"
    if not src_dir.exists():
        return
    out_dir = DIST / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    have_ffmpeg = shutil.which("ffmpeg") is not None
    for f in sorted(src_dir.glob("*.mp3")):
        out = out_dir / f.name
        if have_ffmpeg and f.stat().st_size > 4_000_000:
            os.system(f'ffmpeg -v error -y -i "{f}" -vn -ac 2 -b:a 96k "{out}"')
        else:
            shutil.copy(f, out)
        print(f"  audio {f.name}: {f.stat().st_size // 1024}kB -> {out.stat().st_size // 1024}kB")


def build():
    # Check Heads Up first, so a bad entry stops the build before anything is touched
    hu_render, hu_live, hu_old = headsup.renderer()
    print(f"Heads Up: {hu_live} approved, {hu_old} archived (drafts are never shown)")
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    layout = (SRC / "layout.html").read_text()
    shutil.copy(SRC / "styles.css", DIST / "styles.css")
    shutil.copy(SRC / "site.js", DIST / "site.js")
    shutil.copytree(SRC / "fonts", DIST / "fonts")
    logo = photo("ravesafe-unicorn", "logo", "brand__logo")
    misk_photo = re.sub(r'alt="[^"]*"', 'alt=""', photo("miss-k", "small", "misk-chat__img"))
    build_icons()
    build_audio()
    if DL_ORIG.exists():
        shutil.copytree(DL_ORIG, DIST / "downloads", ignore=shutil.ignore_patterns("*.txt"))

    urls = []
    for p in sorted((SRC / "pages").glob("*.html")):
        meta, body = read_page(p)
        path = meta["path"]
        if "{{ disclaimer }}" in body:  # medical disclaimer box goes at the bottom of the page, above the footer
            body = body.replace("{{ disclaimer }}", "").rstrip() + "\n" + DISCLAIMER + "\n"
        body = headsup.SHORTCODE.sub(hu_render, body)
        body = PHOTO_RE.sub(lambda m: photo(m.group(1), m.group(2) or "card", m.group(3) or ""), body)
        page = (layout.replace("{{ content }}", body)
                .replace("{{ title }}", html.escape(meta["title"]))
                .replace("{{ description }}", html.escape(meta["description"]))
                .replace("{{ canonical }}", SITE_URL + path)
                .replace("{{ logo }}", logo)
                .replace("{{ misk_photo }}", misk_photo)
                .replace("{{ robots }}", '<meta name="robots" content="noindex">\n' if meta.get("robots") == "noindex" else ""))
        # Mark the current page in the menu
        page = page.replace(f'data-nav href="{path}"', f'data-nav href="{path}" aria-current="page"')
        out = DIST / "404.html" if path == "/404/" else (DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        depth = len([s for s in path.strip("/").split("/") if s])
        if PREVIEW:
            page = relativise(page, depth)
            if path == "/":
                # The preview host wraps its main page in its own skeleton: keep only head bits + body
                head = re.search(r"<head>(.*?)</head>", page, re.S).group(1)
                head = re.sub(r'<meta (charset|name="viewport")[^>]*>\n?', "", head)
                body = re.search(r"<body>(.*)</body>", page, re.S).group(1)
                page = head.replace("<title>", '<meta name="claude:viewport-fit-sides" content="cover">\n<title>', 1) + body
        out.write_text(page)
        if meta.get("robots") != "noindex":
            urls.append(path)
        for f in re.findall(r'href="/downloads/([^"#?]+)"', body):
            if not (DL_ORIG / f).exists():
                missing_downloads.add(f)
        print(f"  built {path}")

    # Sitemap, robots, host settings (Netlify and Cloudflare Pages both read these)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    shutil.copy(ROOT / "host" / "_headers", DIST / "_headers")
    if headsup.is_preview():
        # Test site (netlify.app or a local build): keep it out of search engines
        (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
        with open(DIST / "_headers", "a") as h:
            h.write("\n# Test site only: keep out of search results\n/*\n  X-Robots-Tag: noindex, nofollow\n")
        print("Test site build: search engines blocked, preview-only sources shown")
    else:
        (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    shutil.copy(ROOT / "host" / "_redirects", DIST / "_redirects")

    if missing_downloads:
        print("\nWaiting for PDFs (put them in downloads/ with these names):")
        for f in sorted(missing_downloads):
            print(f"  - {f}")
    missing = [n for (n, _), v in done_images.items() if v is None]
    if missing:
        print("\nWaiting for originals (showing placeholders):")
        for n in sorted(set(missing)):
            print(f"  - {n}")


if __name__ == "__main__":
    build()
