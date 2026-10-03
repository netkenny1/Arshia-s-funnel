# 03 — Reaching people who are physically in Dubai (paid + automation)

UAE numbers that matter (DataReportal / Napoleon Cat, 2026): ~99% social media penetration, Instagram ~9.8M users, TikTok ~11M adults, Snapchat ~5M (about 45% of the population, skewing 18–30, heavier among Emiratis and Gulf nationals). WhatsApp is the operating system of Dubai nightlife; every promoter runs on broadcast lists.

## Tier 0 (free): WhatsApp

- **Broadcast list, not a group.** Groups leak numbers and die. Broadcast lists send 1:1 messages to up to 256 people each; make several ("Moe's list", "Soho list").
- Guest list sign-ups go into the Google Sheet; add every number to the broadcast list the same day.
- Message cadence: Tuesday ("this week: Thu Moe's, Sat Soho, reply with names"), day-of 4pm confirmation with the cut-off time, next-morning photo dump + "tag yourself".
- **WhatsApp Channel** (public, one-to-many, followable from a link): put the link in bios. Good for people who won't give a number yet.
- Scripts in `content/scripts.md`.

## Tier 1 (AED 500–1,500/month): geo-fenced boosts

### TikTok Promote
Covered in playbook 02. Dubai-only, winners-only, website-visits objective.

### Meta (Instagram) ads, Advantage+ off, manual placements
- **Location:** drop pins with 1-mile radius on: Sheraton Grand SZR (Moe's), Meydan (Soho Garden), DIFC, Dubai Marina / JBR, Business Bay, Palm Jumeirah, City Walk, Downtown. "People living in or recently in this location".
- **Age 21–34.** Interests: nightlife, house music, afro house, Soho Garden, White Dubai, Blu Dubai, Ushuaïa, Hï Ibiza (cross-venue interest is the strongest signal that someone actually clubs).
- **Creative:** the winning TikTok, vertical, 9:16, native-looking. No logo intro.
- **Objective:** traffic to `/guestlist/?utm_source=ig&utm_medium=paid&utm_campaign=<night>`. Later: conversions, once the pixel is on the site (add the Meta pixel snippet to `templates/layout.html`).
- **Lookalike:** export the sheet's phone column, upload as a Custom Audience (Meta hashes it), build a 1% UAE lookalike. From 100 numbers it starts working; from 500 it's the best audience you'll have.
- **Retargeting:** everyone who hit the site but didn't submit, 7-day window, one ad: "Friday list closes at 9pm".

### Snapchat
- **Geofilter at the venue** (Snapchat Ads Manager → Filters → Community/On-demand). Draw the fence around the venue for the hours of the set. People at the night use it, their friends see the venue + his name. This is the single cheapest "the right crowd tells their friends" mechanic in Dubai, and almost no DJ at his level does it.
- Snap Map public stories: tag the venue location on his own Snaps during the set.

## Tier 2: partners instead of ads

- **Venue co-marketing.** Ask for: collab posts, his name on the venue's weekly flyer, a Platinumlist listing (free entry "guest list" ticket) which also gets Platinumlist's own SEO and email list behind the night.
- **Table-heavy nights.** Guest list people fill the floor; tables pay the bills. Offer the venue a "bring 6, get a table hold" deal through his list and he becomes a revenue line, not a cost. That's how residencies get extended.
- **Creator seeding (10 people).** Dubai lifestyle/fashion micro-creators, 5k–50k followers, who post nightlife already. Invite them with a +3, a table hold, a photographer. No payment, just a great night and a tag. The report will show the "creator night" spike within a week.
- **Lifestyle partnerships.** Barbers, gyms, fashion boutiques, car rental, padel clubs in Marina/JVC: they have the exact audience and love being "the official pre-game of". Trade: their logo on one video + a guest list code per partner (`?utm_source=<partner>` so you can see who delivers).

## Automations you can run from this repo and the connected tools

| What | How | Status |
|---|---|---|
| Nightly site rebuild so past events roll off | `.github/workflows/pages.yml` cron | built |
| Weekly TikTok report | Run `scripts/tiktok_report.py` on the new export. Can be scheduled as a Claude Code routine that reads the export from a Drive folder and posts the shoot list to WhatsApp/email. | script built; schedule it once exports exist |
| Guest list → Google Sheet → WhatsApp confirm | `scripts/guestlist_apps_script.gs`; set `WHATSAPP_WEBHOOK` to a WhatsApp Cloud API or Make.com webhook for auto-confirmation | built; needs 5-min setup |
| Weekly source report (which video filled the list) | `weeklySourceReport()` in the Apps Script | built |
| Gig → calendar invites for the crew/photographer | Google Calendar MCP from `events.json` (ask Claude: "put this month's events in my calendar") | available |
| Press / venue outreach drafts | Gmail MCP: draft (not send) from `content/outreach.md` templates | available |
| Weekly story/flyer design | Canva MCP: generate from a brand template with the date + venue text | available (see `content/creative.md`) |
| Partner / venue / creator-agency list | Vibe Prospecting MCP for *businesses* in Dubai (venues, agencies, lifestyle brands) for the Tier 2 outreach | available; businesses only, see note |

**Note on data tools.** I did not and will not use prospecting/enrichment tools to build lists of individual people by looks, gender or anything similar. It is illegal under UAE PDPL to process personal data that way without consent, Meta and TikTok ban it, and it is not how the crowd gets built. The tools are fine for finding *businesses* to partner with.

## Budget sketch (month 1)

| Item | AED |
|---|---|
| Domain + nothing else for the site | 50 |
| TikTok Promote, 3 winners × 3 days × AED 40 | 360 |
| Meta geo campaign | 600 |
| Snapchat geofilter, 2 nights | 150 |
| Photographer, 4 nights (or a friend with a good phone) | 0–800 |
| **Total** | **~1,200–2,000** |
