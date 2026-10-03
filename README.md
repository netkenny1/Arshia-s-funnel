# arshia.wav — growth funnel

Everything needed to push **arshia.wav** (DJ, Dubai · Moe's on the 5th · Soho Garden) from zero web presence to a name AI engines, Google, TikTok and a WhatsApp list all agree on.

Start with [`playbooks/00-strategy.md`](playbooks/00-strategy.md). Do [`playbooks/05-week-1-checklist.md`](playbooks/05-week-1-checklist.md).

## What's here

| Piece | Where | Status |
|---|---|---|
| Entity hub site with schema.org JSON-LD, FAQ, events, guest list form, press kit, `llms.txt`, sitemap | `site/` (built from `data/` + `templates/` by `scripts/build_site.py`) | built, tested |
| Free guest-list backend (Google Sheet + attribution + de-dupe) | `scripts/guestlist_apps_script.gs` | built, 5-min setup |
| TikTok/Reels iteration engine: export CSV + annotation log → winners/kills + next 7-video shoot list | `scripts/tiktok_report.py`, `tiktok/` | built, sample run in `tiktok/samples/report_sample.md` |
| GitHub Pages deploy + nightly rebuild, PR checks | `.github/workflows/` | built |
| Playbooks: GEO/AI SEO, TikTok loop, Dubai geo-targeting + automations, crowd curation, week 1 | `playbooks/` | written |
| Hook bank, WhatsApp/DM scripts, outreach templates, creative brief | `content/` | written |

## Run it

```bash
python3 scripts/build_site.py            # data/*.json -> site/   (warns on every TODO left)
python3 scripts/check_schema.py          # every JSON-LD block parses + has required keys
python3 scripts/tiktok_report.py tiktok/exports/<date>.csv   # weekly report -> tiktok/reports/
```

Local preview (the site is built for the `/Arshia-s-funnel/` path GitHub Pages uses):

```bash
mkdir -p /tmp/www && ln -sfn "$PWD/site" /tmp/www/Arshia-s-funnel && (cd /tmp/www && python3 -m http.server 8765)
# open http://localhost:8765/Arshia-s-funnel/
```

## Deploy

1. GitHub → Settings → Pages → Source: **GitHub Actions**.
2. Merge to `master`. The workflow validates, builds and deploys to `https://netkenny1.github.io/Arshia-s-funnel/`.
3. Custom domain later: set `site_url` in `data/artist.json`, add `site/CNAME`, set the domain in Pages settings.

## Arshia's two files

- `data/artist.json` — who he is, where he plays, FAQ, links, WhatsApp, guest list endpoint. Every `TODO` shows up as a build warning.
- `data/events.json` — gigs. `status: confirmed` publishes with `MusicEvent` schema; `draft` stays hidden; `cancelled` emits `EventCancelled`.
