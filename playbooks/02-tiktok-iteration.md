# 02 — TikTok (and Reels) as a weekly experiment

Full mechanics in `tiktok/README.md`. This is the strategy layer.

## Cadence: 3-2-1 per week, 7 shot in one night

- **3 track-ID clips** from the night (the record, the moment, the ID in the caption). This is what house people save and share.
- **2 transitions** (15s, the mix point, no talking).
- **1 short talking clip** (what he's digging this week, or "the list is open"). Builds the person, not just the set.
- **+1 explore slot** the report assigns: a hook type he hasn't tried.

Shoot all seven in one night with a phone on a small tripod behind the decks and a friend doing crowd pans. Posting is spread Mon–Sun.

## Hook rules (first 2 seconds decide everything)

1. On-screen text in frame one, 3–8 words, says what the record or the mix is. No hype words.
2. Movement in frame one: hands on the mixer, the room, lights. Never a static logo.
3. Venue name spoken or written in the first 3 seconds. TikTok's search index reads on-screen text and audio.
4. The payoff lands by second 6. Loop the ending back to the start for completion rate.

Hook bank in `content/hooks.md`, grouped by the `hook_type` labels the report uses.

## TikTok search optimisation (this is "SEO" inside TikTok)

Caption formula: `[hook sentence]. [venue] [city]. [1-2 genre words]` + 3–5 hashtags max.
Always include: `Dubai`, the venue name, and a genre. Rotate: `#dubainightlife #dubai #dxb #moesonthe5th #sohogardendxb #afrohouse #housemusic`.
Say "Dubai" out loud in talking-head videos. Pin a comment with "guest list link in bio" and the date.

## Geo: making the For You feed think he's a Dubai account

TikTok decides location relevance from (a) where the account is used, (b) where the first 300 viewers are, (c) text signals. So:

- Post from Dubai, on Dubai IP, at Dubai prime times (TikTok Studio → Viewers → Most active times; typically 8–11pm GST).
- First hour: send each video to the WhatsApp guest list group and ask for a share, not a like. Shares from Dubai phones = Dubai distribution.
- Don't use a VPN for posting. Don't post while travelling without checking the territory split afterward.
- TikTok Studio → Analytics → Viewers → Territories: the UAE share should climb above 70%. If it drops, the last few hooks were too generic.

## Promote: AED 40/day on winners only

TikTok Promote (in-app) is boosting, not an ad campaign. Use it only on videos the report flagged as WINNER, goal "website visits" → the site, location Dubai, age 23–38, 3 days. Watch cost per site visit; under AED 1.50 is good for nightlife. Kill at day 2 if it's over AED 3.

## Instagram

Reels: same videos, same day, trimmed to 15s if longer. Instagram's recommendation now weights sends-per-reach like TikTok. Cover frame = the on-screen hook text.
Stories: link sticker to the site on the day. Reshare every tagged story the next morning.
Collab posts with the venue account for every set. Doubles reach, zero cost, and co-occurrence of names feeds the GEO side.

## Weekly loop (15 min)

Export → annotate → run `scripts/tiktok_report.py` → shoot the 7 → repeat. Four loops and the winners are obvious. Twelve loops and the account has a recognisable format people search for.
