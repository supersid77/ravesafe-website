"""RaveSafe Heads Up: turns data/headsup.json and data/source-feeds.json into page sections.

The approval gate lives here. Only entries with status "approved" AND an approver name
and time are shown. Drafts never appear. Retired entries go to the archive.
If an approved entry is missing something the SOP says is mandatory, the build stops
with a clear message rather than publishing a half-finished alert.
"""
import html, json, re, sys
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
esc = html.escape

CATS = {
    "alert": ("Alert", "hu--alert",
              '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17v.01"/>'),
    "heads-up": ("Heads Up", "hu--headsup",
                 '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.01"/>'),
    "one-to-watch": ("One to Watch", "hu--watch",
                     '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/>'),
}
LOCATIONS = {"Local", "Regional UK", "UK-wide", "European", "International", "Location unknown"}
MUST_HAVE = ["id", "classification", "title", "summary", "testing_org", "source_url", "source_date",
             "location_label", "evidence_type", "why_classified", "advice", "reviewed_date",
             "approved_by", "approved_at"]

HOLDING = ('<div class="panel alert-empty"><span class="tag tag--cyan">Nothing to flag right now</span>'
           '<h3>No current RaveSafe Heads Up</h3>'
           '<p>We review warnings from UK and European drug checking services and public health bodies every few days. '
           'When something meets our threshold, it goes here with a link to the original source.</p>'
           '<p>Until then, check these before you go:</p>'
           '<ul class="ticks">'
           '<li><a href="https://www.wearetheloop.org/drug-alerts" rel="noopener">The Loop drug alerts</a></li>'
           '<li><a href="https://www.wedinos.wales/" rel="noopener">WEDINOS sample results</a></li>'
           '</ul></div>')


def _fail(msg):
    print(f"\nHEADS UP BUILD STOPPED: {msg}\nNothing has been published. Fix data/headsup.json and build again.\n")
    sys.exit(1)


def _iso(d):
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        return None


def nice(d):
    when = _iso(d)
    if not when:
        return esc(str(d))
    return f'<time datetime="{when.isoformat()}">{when.day} {when.strftime("%B %Y")}</time>'


def _safe_url(u):
    u = str(u or "").strip()
    return u if re.match(r"^https?://", u) else ""


def load_entries():
    data = json.loads((ROOT / "data/headsup.json").read_text())
    current, archive, seen = [], [], set()
    for e in data.get("entries", []):
        status = e.get("status", "draft")
        if status not in ("approved", "retired"):
            continue  # drafts and anything else never reach the website
        name = e.get("id") or e.get("title") or "an entry"
        missing = [k for k in MUST_HAVE if not e.get(k)]
        if missing:
            _fail(f'{name} is marked {status} but is missing: {", ".join(missing)}.')
        if e["classification"] not in CATS:
            _fail(f'{name} has classification "{e["classification"]}". Use alert, heads-up or one-to-watch. Monitor items are internal only.')
        if e["location_label"] not in LOCATIONS:
            _fail(f'{name} has location_label "{e["location_label"]}". Use one of: {", ".join(sorted(LOCATIONS))}.')
        if not _safe_url(e["source_url"]):
            _fail(f"{name} needs a full source_url starting with https://")
        if not re.match(r"^[A-Za-z0-9-]+$", e["id"]) or e["id"] in seen:
            _fail(f"{name} needs a unique id using only letters, numbers and dashes.")
        if status == "retired" and not e.get("retired_reason"):
            _fail(f"{name} is retired but has no retired_reason.")
        seen.add(e["id"])
        (current if status == "approved" else archive).append(e)
    key = lambda e: (str(e.get("source_date", "")), str(e.get("approved_at", "")))
    current.sort(key=key, reverse=True)
    archive.sort(key=key, reverse=True)
    return current, archive


def tag(cls_key):
    label, cls, icon = CATS[cls_key]
    return (f'<span class="hu-tag {cls}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{icon}</svg>{label}</span>')


def _fact(label, value):
    return f"<div><dt>{label}</dt><dd>{value}</dd></div>" if value else ""


def card(e, full=True, retired=False):
    _, cls, _ = CATS[e["classification"]]
    top = (f'<div class="alert__top">{tag(e["classification"])}'
           f'<span class="alert__cat">{esc(e["location_label"])}</span>{nice(e["source_date"])}</div>')
    if not full:
        return (f'<article class="panel alert {cls}">{top}<h3>{esc(e["title"])}</h3>'
                f'<p>{esc(e["summary"])}</p>'
                f'<a class="alert__more" href="/heads-up/#{e["id"]}">Read the full Heads Up</a></article>')
    src = _safe_url(e["source_url"])
    tested = f'<a href="{esc(src)}" rel="noopener">{esc(e["testing_org"])}</a>'
    found = ", ".join(esc(x) for x in e.get("detected", []))
    place = esc(e["location_label"]) + (f'. {esc(e["location_detail"])}' if e.get("location_detail") else "")
    facts = "".join([
        _fact("Sold as", esc(e.get("sold_as", ""))),
        _fact("What was found", found),
        _fact("Tested by", tested),
        _fact("Warning issued by", esc(e.get("issuing_org", "")) if e.get("issuing_org") and e.get("issuing_org") != e["testing_org"] else ""),
        _fact("Reference", esc(e.get("sample_ref", ""))),
        _fact("Evidence", esc(e["evidence_type"])),
        _fact("Where", place),
        _fact("Their warning level", esc(e.get("original_warning_level", ""))),
        _fact("Pattern so far", esc(e.get("trend_status", ""))),
    ])
    advice = "".join(f"<li>{esc(a)}</li>" for a in e["advice"])
    unknown = (f'<div><p class="list-title list-title--dont">What\'s still unknown</p><p>{esc(e["uncertainty"])}</p></div>'
               if e.get("uncertainty") else "")
    hist = e.get("history") or []
    history = ""
    if hist:
        rows = "".join(f'<li>{nice(h.get("date", ""))}: {esc(h.get("change", ""))}</li>' for h in hist)
        history = f'<details class="hu-history"><summary>Changes to this entry</summary><ul>{rows}</ul></details>'
    banner = ""
    if retired:
        banner = (f'<p class="hu-retired"><strong>Archived.</strong> This is no longer a current Heads Up. '
                  f'{esc(e["retired_reason"])}</p>')
    return (f'<article class="alert alert--full {cls}{" alert--retired" if retired else ""}" id="{e["id"]}">{banner}{top}'
            f'<h3>{esc(e["title"])}</h3><p class="alert__summary">{esc(e["summary"])}</p>'
            f'<dl class="hu-facts">{facts}</dl>'
            f'<div class="alert__cols">'
            f'<div><p class="list-title list-title--do">Why we\'ve classified this</p><p>{esc(e["why_classified"])}</p></div>'
            f'{unknown}'
            f'<div class="alert__action"><p class="list-title list-title--do">What you can do</p><ul class="ticks">{advice}</ul></div>'
            f'</div>'
            f'<p class="hu-meta">Published by {esc(e["testing_org"])} on {nice(e["source_date"])}. '
            f'Reviewed by RaveSafe on {nice(e["reviewed_date"])}. '
            f'<a href="{esc(src)}" rel="noopener">Read the original from {esc(e["testing_org"])}</a></p>'
            f'{history}</article>')


# ---------- Lane 1: headlines straight from testing services (off until approved) ----------
def _text(el, *names):
    for n in names:
        found = el.find(n)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
    return ""


UA = {"User-Agent": "RaveSafe-site-build (+https://ravesafecommunity.com)"}


def _get(url):
    with urlopen(Request(url, headers=UA), timeout=15) as r:
        return r.read()


def _item(src, title, link, when):
    return {"title": title, "link": link, "date": when, "source": src["name"], "lang": src.get("lang_code", "en"),
            "language": src.get("language", "")}


def fetch_rss(src, limit):
    root = ET.fromstring(_get(src["feed_url"]))
    items = []
    for it in root.iter("item"):
        title, link = _text(it, "title"), _safe_url(_text(it, "link"))
        if not title or not link:
            continue
        when = None
        try:
            when = parsedate_to_datetime(_text(it, "pubDate")).date()
        except (TypeError, ValueError):
            pass
        items.append(_item(src, title, link, when))
        if len(items) >= limit:
            break
    return items


DE_MONTHS = {m: i for i, m in enumerate(["januar", "februar", "märz", "april", "mai", "juni", "juli", "august",
                                         "september", "oktober", "november", "dezember"], 1)}
CHECKIT_RE = re.compile(r'class="t-entry-date">\s*(\d{1,2})\.\s*([^\s<]+)\s+(\d{4})\s*</span>.*?'
                        r'<h3[^>]*t-entry-title[^>]*>\s*<a href="([^"]+)"[^>]*>(.*?)</a>', re.S)


def fetch_checkit(src, limit):
    """checkit! (Vienna) has no feed, so read the dated warnings list on its results page."""
    page = _get(src["feed_url"]).decode("utf-8", "replace")
    items = []
    for d, mon, y, link, title in CHECKIT_RE.findall(page):
        m = DE_MONTHS.get(mon.lower())
        link = _safe_url(html.unescape(link))
        title = re.sub(r"<[^>]+>", "", html.unescape(title)).strip()
        if not (m and link and title):
            continue
        try:
            when = date(int(y), m, int(d))
        except ValueError:
            continue
        items.append(_item(src, title, link, when))
        if len(items) >= limit:
            break
    return items


FETCHERS = {"rss": fetch_rss, "checkit": fetch_checkit}


def fetch_feed(src, limit):
    return FETCHERS[src.get("type", "rss")](src, limit)


def render_feed(fetch=fetch_feed):
    cfg = json.loads((ROOT / "data/source-feeds.json").read_text())
    on = [s for s in cfg.get("sources", []) if s.get("enabled")]
    if not on:
        return ""  # lane switched off: nothing shows
    limit = int(cfg.get("show_max", 8))
    items, failed = [], []
    for s in on:
        try:
            items += fetch(s, 50)
        except Exception as err:  # a broken feed must never break the site
            print(f"  feed skipped: {s['name']} ({err})")
            failed.append(s)
    # Only recent headlines. Undated ones are dropped as we can't tell how old they are.
    max_age = int(cfg.get("max_age_days", 30))
    cutoff = date.today().toordinal() - max_age
    items = [i for i in items if i["date"] and i["date"].toordinal() >= cutoff]
    items.sort(key=lambda i: i["date"], reverse=True)
    def row(i):
        lang = i["lang"] if re.match(r"^[a-z]{2}$", i["lang"]) else "en"
        tag = f' · in {esc(i["language"])}' if lang != "en" and i["language"] else ""
        return (f'<li data-date="{i["date"].isoformat()}"><a href="{esc(i["link"])}" rel="noopener" lang="{lang}">{esc(i["title"])}</a>'
                f'<span>{esc(i["source"])}{tag} · {nice(i["date"].isoformat())}</span></li>')
    rows = "".join(row(i) for i in items[:limit])
    names = ", ".join(f'<a href="{esc(_safe_url(s.get("home_url")) or _safe_url(s["feed_url"]))}" rel="noopener">{esc(s["name"])}</a>' for s in on)
    if not rows and len(failed) == len(on):
        rows = f'<li class="hu-feed__empty">Couldn\'t load the latest headlines just now. Check {names} directly.</li>'
    elif not rows:
        rows = (f'<li class="hu-feed__empty">No new headlines in the last {max_age} days. '
                f'Check {names} directly for older warnings.</li>')
    sources = "".join(
        f'<li><a href="{esc(_safe_url(x.get("home_url")) or _safe_url(x["feed_url"]))}" rel="noopener">{esc(x["name"])}</a>'
        f'{", " + esc(x["country"]) if x.get("country") else ""}'
        f'{". Headlines in " + esc(x["language"]) if x.get("language") and x.get("lang_code", "en") != "en" else ""}</li>'
        for x in on)
    europe = any(x.get("country", "UK") != "UK" for x in on)
    where = "the UK and Europe" if europe else "the UK"
    early = ('<p class="muted">Dangerous batches are often spotted in Europe before they reach the UK, '
             'so these can be an early warning of what\'s coming.</p>') if europe else ""
    try:
        now, zone = datetime.now(ZoneInfo("Europe/London")), "UK time"
    except Exception:
        now, zone = datetime.utcnow(), "GMT"
    stamp = f"{now.day} {now:%B %Y at %H:%M} ({zone})"
    return (f'<section class="section section--alt" id="from-testing" aria-labelledby="feed-title" style="scroll-margin-top: 90px">'
            f'<div class="wrap stack"><div class="section-head" style="margin-bottom:0"><div>'
            f'<p class="kicker">Straight from the testing services</p>'
            f'<h2 id="feed-title" class="display h-lg">Latest from testing services</h2>'
            f'<p class="muted"><span class="tag tag--cyan">Not yet reviewed by RaveSafe</span></p>'
            f'<p class="muted">These are the last {max_age} days of headlines from drug checking services in {where}, shown as they are. '
            f'We haven\'t checked or classified them yet.{" Some are in the service\'s own language." if europe else ""} Tap through to read the full warning on their site.</p>'
            f'{early}</div></div>'
            f'<div data-feed-checked="{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}" data-feed-max-hours="96" data-feed-max-days="{max_age}">'
            f'<ul class="hu-feed">{rows}</ul>'
            f'<p class="hu-feed__stale panel" hidden>These headlines haven\'t updated for over 4 days, so we\'ve hidden them in case they\'re out of date. '
            f'Check {names} directly for their latest warnings.</p>'
            f'<p class="note">Last checked {stamp}. All credit to the services who do the testing.</p></div>'
            f'<details class="hu-sources"><summary>Where these headlines come from</summary><ul class="ticks">{sources}</ul></details>'
            f'</div></section>')


# ---------- Shortcodes ----------
SHORTCODE = re.compile(r'\{\{\s*headsup\s+"(current|latest|archive|feed)"(?:\s+(\d+))?\s*\}\}')


def renderer():
    current, archive = load_entries()
    feed_html = None

    def render(m):
        nonlocal feed_html
        kind, n = m.group(1), m.group(2)
        if kind == "feed":
            if feed_html is None:
                feed_html = render_feed()
            return feed_html
        if kind == "archive":
            if not archive:
                return ""
            cards = "\n".join(card(e, True, retired=True) for e in archive)
            return (f'<section class="section" id="archive" aria-labelledby="archive-title" style="scroll-margin-top: 90px">'
                    f'<div class="wrap stack"><div class="section-head" style="margin-bottom:0"><div>'
                    f'<p class="kicker">For the record</p><h2 id="archive-title" class="display h-lg">Archive</h2>'
                    f'<p class="muted">Past entries that are no longer current, kept with their original dates and any changes.</p>'
                    f'</div></div><details class="hu-archive"><summary>Show {len(archive)} archived '
                    f'{"entry" if len(archive) == 1 else "entries"}</summary><div class="alerts">{cards}</div></details></div></section>')
        if not current:
            return HOLDING
        if kind == "latest":
            return "\n".join(card(e, False) for e in current[: int(n or 3)])
        return "\n".join(card(e, True) for e in current)

    return render, len(current), len(archive)
