# Make arshia.wav known in Dubai — the system

**Goal:** his name known across the Dubai house scene, and a list of people from that scene he can message directly before every night.

**Not the goal:** follower count, viral randoms, people who come for "free entry" and kill the room.

**Starting point (3 Oct 2026):** zero web footprint. No RA, SoundCloud, Spotify or press. Instagram follower count unknown (rate-limited). Nothing to fix, nothing to inherit.

## How it works

```
  set clips + track IDs (IG / TikTok)  ──►  people who watch them to the end  ──►  retarget only them
                                                                                        │
  Meta ads aimed at the house crowd (artists + venues they follow, Dubai only)  ────────┤
                                                                                        ▼
                                                              arshiawav site: one page, "the list"
                                                                                        │
                                                   Google Sheet (names, IG, WhatsApp)  ──►  WhatsApp before every night
                                                                                        │
                                                    lookalike audience from the sheet  ──►  more of the same people
```

The filter for "the right people" is built in at three points, none of which judge individuals:
1. **Content**: real house sets, transitions, track IDs. People who don't like house don't watch to the end.
2. **Targeting seed**: interests = house artists and the Dubai venues that book them. Not "nightlife".
3. **Lookalike**: Meta finds people who resemble the ones already on the list. The list is self-selected by 1 and 2.

If 1 and 2 are done honestly, the lookalike compounds in the right direction. If the seed is "free entry Dubai", it compounds the wrong way and no amount of door policy fixes it. That's why the site says "the list", not "free entry", anywhere.

## The four pieces (all in this repo)

| Piece | Why it exists | Where |
|---|---|---|
| One-page site | Something to send people to that isn't an Instagram profile. Collects the list. Carries structured data so Google and AI answer engines know who he is. | `web/`, built from `data/artist.json` |
| The list backend | Google Sheet = the asset. Names, IG, WhatsApp, and which post sent them. Relays to a private Telegram channel so he sees sign-ups live. | `scripts/guestlist_apps_script.gs` |
| Content loop | Weekly: export TikTok/IG numbers, annotate, see which clips the house crowd actually finishes and shares, make more of those. | `scripts/tiktok_report.py`, `tiktok/` |
| Reach | Meta ads through Claude (official Meta Ads MCP), seeded to the house scene, Dubai only; retargeting; lookalikes. Plus the free stuff: RA, venue tags, the right communities. | `playbooks/03`, `04` |

## Weekly rhythm (about 2 hours total)

- **Mon**: export numbers, run the report, pick 5 clips to cut from last weekend's set.
- **Tue**: post 1, WhatsApp the list the week's nights.
- **Wed–Sat**: post 1 a day. Boost the one that's winning (Dubai, house interests only).
- **Night of**: shoot the set from the booth + one crowd angle. Photographer or a friend.
- **Sun**: pull ad results through Claude, kill the losers, note who signed up from where.

## KPIs

| | Now | 90 days |
|---|---|---|
| People on the list from Dubai | 0 | 500 |
| Cost per sign-up (Meta) | — | under AED 8 |
| % of clip viewers who watch to the end | baseline | +50% |
| Dubai share of audience (TikTok Studio → Territories) | baseline | 70%+ |
| Venue, promoter and other-DJ tags per month | 0 | 10 |
| AI mention test (10 prompts, playbook 01) | 0/10 | 3/10 |
