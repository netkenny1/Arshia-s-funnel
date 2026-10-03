# 03 — Reach: ads through Claude, the pixel, and the list

Playbook 04 says *who*. This is the *how*.

## 1. The pixel comes first

Without it there is no retargeting and no lookalike, and ads are just paying for strangers.
- Meta Events Manager → create a Pixel → copy the ID into `data/artist.json → tracking.meta_pixel_id`. Push. The site loads it and fires `PageView`; the form fires `Lead` on success.
- Same for TikTok (`tracking.tiktok_pixel_id`) once TikTok ads start.
- Verify with the Meta Pixel Helper extension on the live site.

## 2. Meta Ads MCP in Claude

Meta's official hosted connector: `https://mcp.facebook.com/ads` (open beta since 29 April 2026, Business login, no developer app). Add it in Claude → Settings → Connectors → custom connector. Then the weekly conversation is literally:

> "Create a campaign 'arshia list — week 41', objective leads, Dubai only, 23–38, interests Keinemusik, Black Coffee, Solomun, Peggy Gou, Soho Garden, Terra Solis, Blu Dubai, exclude interests nightlife/ladies night. Daily budget AED 50. Use the video from this URL. Destination https://…/#list?utm_source=ig&utm_medium=paid&utm_campaign=w41."

> "Pull last 7 days by ad set: spend, link clicks, leads, cost per lead. Pause anything above AED 10 per lead."

> "Create a Custom Audience from this CSV of phone numbers (the sheet export) and a 1% UAE lookalike."

Rules of thumb:
- One campaign, three ad sets (seed / warm / lookalike, playbook 04). Don't fragment further until spend is over AED 150/day.
- Creative is the lever. Swap in the week's winning clip from the TikTok report every Monday.
- Optimise for Leads. Followers and video views as objectives attract the cheap, wrong audience.
- Advantage+ audience: off at the start. It will "expand" straight into generic nightlife. Turn it on only for the lookalike set after 50+ leads.

## 3. Free reach that compounds

In order of leverage for the house crowd:
1. Venue collab posts on every set (ask once, then it's routine).
2. RA artist page + venue RA listings.
3. Other residents: b2b, reposts, tags.
4. Track ID comments on Keinemusik/Afterlife/Soho Garden posts (be useful, not promotional).
5. Platinumlist listing of his nights.
6. One honest Reddit r/dubai answer a week in "where to go" threads.

## 4. The list itself

- Sheet → WhatsApp broadcast lists (not groups). Tuesday message: the nights. Day-of: "tonight, list closes 9". Next morning: photos, "tag yourself".
- Sheet → Telegram door channel (automatic, see Apps Script) so the host sees names live.
- Sheet phone column → Meta Custom Audience monthly → lookalike refresh.
- Reply to every "ID?" DM. That person is the audience.

## 5. Permit and creative rules

UAE Advertiser Permit (Media Council), mandatory since 1 Feb 2026 for paid and unpaid promotion from inside the UAE; free for residents for 3 years. Apply before boosting. No alcohol in creatives. No "free entry" in copy: it's against the targeting logic, and venues don't want it on record.

## Budget

| Month 1 | AED |
|---|---|
| Meta ads (AED 40–75/day) | 1,200–2,200 |
| TikTok Promote on winners | 300 |
| Domain | 50 |
| Everything else in this repo | 0 |
