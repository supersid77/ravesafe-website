# RaveSafe Community website

The new ravesafecommunity.com, rebuilt off WordPress.

## What's where
- `src/pages/` one file per page. Edit the words here.
- `src/layout.html` the header, menu and footer shared by every page.
- `src/styles.css` the one style file. Colours and fonts are at the top.
- `data/images.json` every photo's name and alt text.
- `images-original/` drop full-size photos here, named to match images.json.
- `host/` security headers and redirects for the web host.
- `dist/` the finished site the build makes. Don't edit this by hand.

## Build it
Needs Python 3 and Pillow (`pip install pillow`).

    python build.py

The finished site lands in `dist/`. Photos are shrunk to WebP automatically. Any photo without an original yet shows a labelled placeholder, and the build lists what's still missing.

## Adding a photo
1. Add a line to `data/images.json` with a plain name and alt text.
2. Save the full-size original in `images-original/` with that name.
3. Use it on a page with `{{ photo "the-name" "card" }}` (sizes: hero, wide, card, small).
4. If a crop cuts off the important bit, add `"position": "center 20%"` to that photo in images.json. Lower numbers show more of the top.

## Heads Up

Everything lives in two files in `data/`. The logic is in `headsup.py`.

**Adding a reviewed entry (`data/headsup.json`)**

1. Copy `_template` into the `entries` list and fill it in. Keep `"status": "draft"` while you work on it. Drafts never show on the site.
2. Once a named person has approved it, set `"status": "approved"` and fill in `approved_by` and `approved_at`.
3. Commit to GitHub. Netlify rebuilds and it goes live in a couple of minutes. The newest three also show on the homepage.
4. To take one down, set `"status": "retired"` and add a `retired_reason`. It moves to the archive with its history.

The build stops, and nothing changes on the live site, if an approved or retired entry is missing anything mandatory (source link, testing organisation, location, why we've classified it, approver and so on). The message says what's missing.

Categories are `alert`, `heads-up` and `one-to-watch`. Monitor items are internal and never go in this file.

**Automatic headlines (`data/source-feeds.json`)**

Each source has `"enabled": false` until the SOP wording is approved and that service has agreed. Set it to `true` to show its latest headlines under "Latest from testing services", labelled as not yet reviewed. Only the headline, date, name and link are shown. If a feed is down, the site still builds and says so. Only headlines from the last 30 days show, and the list hides itself if it hasn't updated for 4 days.

The site rebuilds every 3 days to fetch new headlines (`.github/workflows/headsup-rebuild.yml`, using the `NETLIFY_BUILD_HOOK` secret in GitHub). Each Netlify deploy uses 15 of the free plan's 300 monthly credits, so don't make it more frequent without upgrading.

## Free resource PDFs
Put the PDFs in `downloads/` using the clean names the build lists (for example `parents-guide-ketamine.pdf`). Old WordPress PDF links redirect to the new names automatically.

## Forms (Contact, Volunteer, Community Stories)
The forms send through Web3Forms (free, up to 250 messages a month). Each message is emailed to the address on the Web3Forms account, then the miss.k@ forwarder passes it on. The access key is in each form and is safe to be public. After sending, people land on /thank-you/.

## Logo and icons
- Header logo: `images-original/ravesafe-unicorn.png` (the unicorn) next to the RAVESAFE / COMMUNITY text in `src/layout.html`.
- Browser and phone icons: `src/icons/` (favicons 16 to 512px, favicon.ico, apple-touch-icon, pwa-icon-192/512, pwa-maskable-512). The build copies them to the site root and writes `site.webmanifest`.
- Clean master artwork: `brand-original/` (lime and white, stray marks removed, lime matched to #B8F532).
