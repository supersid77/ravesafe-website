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

## Posting a Head's Up alert
1. Open `data/alerts.json`.
2. Copy the `_example` block into the `alerts` list, newest at the top.
3. Change the words. `level` is `red`, `caution` or `plan`. `date` is like `2026-10-25`.
4. Run `python build.py`. It shows on Head's Up and the latest three show on the homepage.

## Free resource PDFs
Put the PDFs in `downloads/` using the clean names the build lists (for example `parents-guide-ketamine.pdf`). Old WordPress PDF links redirect to the new names automatically.

## Forms (Contact, Volunteer, Community Stories)
The forms send through Web3Forms (free, up to 250 messages a month). Each message is emailed to the address on the Web3Forms account, then the miss.k@ forwarder passes it on. The access key is in each form and is safe to be public. After sending, people land on /thank-you/.

## Logo and icons
- Header logo: `images-original/ravesafe-unicorn.png` (the unicorn) next to the RAVESAFE / COMMUNITY text in `src/layout.html`.
- Browser and phone icons: `src/icons/` (favicons 16 to 512px, favicon.ico, apple-touch-icon, pwa-icon-192/512, pwa-maskable-512). The build copies them to the site root and writes `site.webmanifest`.
- Clean master artwork: `brand-original/` (lime and white, stray marks removed, lime matched to #B8F532).
