# arshia.wav growth system — the strategy

**Goal:** make arshia.wav the name people in Dubai associate with a good night at Moe's on the 5th and Soho Garden, and turn that attention into a guest list the door team is happy to see.

**Starting point (checked 3 Oct 2026):** zero search footprint. No Resident Advisor page, no SoundCloud, no Spotify, no press mention, nothing for "arshia.wav" on Google. Instagram returned a rate-limit so follower count is unknown. This is good news: there is no wrong information to fix, and the first thing we publish becomes the canonical source every AI engine reads.

## The thesis

Most Dubai DJs grow through promoters and Instagram stories. That works but it is slow and it is what everyone does. Three channels are under-used by local DJs right now:

1. **AI answer engines (GEO).** When someone asks ChatGPT, Perplexity or Google's AI mode "where should I go out in Dubai on Saturday" or "who's playing at Soho Garden this weekend", the answer is assembled from whatever structured, consistent, recently-updated pages exist. Nobody at his level has those pages. We build them (done: `site/`).
2. **TikTok as a search engine with a feedback loop.** Dubai has ~11M TikTok users for ~10M people. TikTok search ("Dubai nightlife", "Moe's on the 5th") is the second biggest discovery surface after the For You feed. We treat videos as experiments, not posts: annotate every one, measure shares and saves, double down weekly (done: `scripts/tiktok_report.py`).
3. **Geo-fenced distribution.** Meta and TikTok Promote both let you target a 1-mile radius. Snapchat has 45% penetration in the UAE and lets you buy a geo-filter at the venue itself. Guest list sign-ups become a lookalike seed. Every dirham goes to people physically in Dubai who already go out.

## The funnel

```
   TikTok / Reels (discovery, Dubai-targeted)            AI engines + Google (intent: "where to go tonight")
                 │                                                       │
                 ▼                                                       ▼
        Instagram @arshia.wav  ◄──────────────────────────────  arshiawav site (entity hub)
                 │                                                       │
                 └──────────────► Guest list page (name · IG · WhatsApp · date) ◄──┘
                                                 │
                                   Google Sheet + WhatsApp confirmation
                                                 │
                                   Door list → night → photos → tagged posts → back to top
```

Every arrow is measurable. The guest list form carries UTM tags, so the sheet shows which TikTok filled the list.

## What "the right crowd" means operationally

You said attractive people who actually club. The honest version of that is: people who already go out in Dubai, dress for it, and bring friends. You can't filter for that with a tool, and trying to score individuals is a dead end (and in the UAE, a legal one: personal data law applies). What you *can* do is control who the content and the offer are built for, and let the venue's door do what it already does. That's playbook 04.

## KPIs (weekly, one line each in a notes app)

| KPI | Week 1 target | Month 3 target |
|---|---|---|
| Guest list sign-ups per night | 15 | 60 |
| Show-up rate (door count ÷ list) | 40% | 60% |
| TikTok median views | baseline | 3× baseline |
| Viral rate (shares+saves ÷ views) | baseline | 1.5%+ |
| Dubai share of audience (TikTok Studio → Viewers → Territories) | baseline | 70%+ |
| AI mention test (playbook 01, 10 prompts) | 0/10 | 4/10 |
| Instagram follows per night played | baseline | 100+ |

## 90-day plan

**Weeks 1–2: foundation.** Fill `data/artist.json`, deploy the site, point IG bio to `/guestlist/`, create SoundCloud + RA + Bandsintown, upload one 30-minute mix, start the content log. Shoot 7 videos in one night.

**Weeks 3–6: iteration.** Weekly export → report → shoot list. Start TikTok Promote at AED 40/day on the top video, Dubai only. First Snapchat geo-filter night. Photographer at every night.

**Weeks 7–12: compounding.** Pitch Time Out Dubai / What's On / Lovin Dubai with the press page. Guest list lookalike audience on Meta. Creator seeding with 10 Dubai micro-creators. Monthly AI prompt test. Push for a named night ("arshia.wav presents") at Moe's.

## Files in this repo

| Path | What |
|---|---|
| `data/artist.json`, `data/events.json` | The only files Arshia edits. Facts + gigs. |
| `scripts/build_site.py` | Turns data into the site with schema.org JSON-LD, llms.txt, sitemap. |
| `site/` | The built site. Deployed to GitHub Pages by `.github/workflows/pages.yml`. |
| `scripts/guestlist_apps_script.gs` | Free Google Sheets backend for the guest list form. |
| `scripts/tiktok_report.py`, `tiktok/` | The TikTok iteration engine. |
| `playbooks/` | This folder. 01 GEO, 02 TikTok, 03 Dubai targeting + automations, 04 crowd, 05 week-1 checklist. |
| `content/` | Hook bank, DM/WhatsApp scripts, outreach templates. |
