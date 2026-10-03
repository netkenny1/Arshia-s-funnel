# arshia.wav — the system

Goal: make **arshia.wav** (DJ, Dubai · Moe's on the 5th · Soho Garden) known across the Dubai house scene, and build a list of those people he can message before every night.

Read [`playbooks/00-strategy.md`](playbooks/00-strategy.md) first. Then [`playbooks/04-right-audience.md`](playbooks/04-right-audience.md). Then do [`playbooks/05-week-1-checklist.md`](playbooks/05-week-1-checklist.md).

## Pieces

| | Where | Status |
|---|---|---|
| One-page site: name, where, listen, the list. Structured data (schema.org) and `llms.txt` underneath so Google and AI engines know who he is. Restrained motion. | `web/` (Vite + TypeScript + GSAP + Lenis), content from `data/artist.json` | built, QA'd |
| The list: Google Sheet backend with source attribution, de-dupe, Telegram door-channel relay | `scripts/guestlist_apps_script.gs` | built, 5-min setup |
| Content loop: TikTok/IG export + annotation log → what the house crowd finishes and shares → next 7 clips | `scripts/tiktok_report.py`, `tiktok/` | built, sample in `tiktok/samples/` |
| Reach: Meta Ads through Claude (official Meta Ads MCP), pixel, retargeting, lookalikes, free scene channels, UAE permit | `playbooks/03-reach.md`, `04-right-audience.md` | written |
| Deploy: GitHub Pages, nightly rebuild, PR checks | `.github/workflows/` | built |

## Run

```bash
cd web && npm ci && npm run build        # typecheck + build -> web/dist (reads ../data/*.json)
python3 scripts/check_schema.py web/dist # every JSON-LD block valid
cd web && npm run dev                    # local, http://localhost:5173
python3 scripts/tiktok_report.py tiktok/exports/<date>.csv
```

## Deploy

1. GitHub → Settings → Pages → Source: **GitHub Actions**. Merge to `master`.
2. Live at `https://netkenny1.github.io/Arshia-s-funnel/`. Custom domain: set `site_url` in `data/artist.json`, add `web/public/CNAME`, set it in Pages settings.

## The one file Arshia edits

`data/artist.json`: bio, genres, links, WhatsApp, pixel IDs, channel links, the list endpoint. Empty string = not shown. `data/events.json` is optional; add a date only when it's confirmed.
