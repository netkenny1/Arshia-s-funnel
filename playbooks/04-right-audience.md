# 04 — Reaching the house crowd, not the randoms

The whole thing hinges on this. Here's who they are, where they already are, and how every tool in this repo is pointed at them.

## Who they are (Dubai, 2026)

People who already go to house nights. In Dubai that means they follow some of: Keinemusik (&ME, Rampa, Adam Port), Black Coffee, Solomun, Peggy Gou, Jamie Jones, Dixon, Âme, Adriatique, Mind Against, Tale of Us / Anyma, ARTBAT, Charlotte de Witte, Francis Mercier, Kas:st, Mathame, Marco Carola, Loco Dice, Dennis Cruz, Vintage Culture, Carlita, Themba, Shimza, Enoo Napa, Caiiro, Culoe De Song. And the Dubai rooms and brands that book them: Soho Garden, Terra Solis, Blu, Bohemia, Pacha ICONS, Ushuaïa Dubai, Analog Room, Soho Beach, Playa Pacha, Afterlife Dubai, Keinemusik Dubai, White Dubai (for the crossover), Nikki Beach, Zero Gravity (daytime).

They are 23–38, a mix of residents and long-stay visitors, concentrated in Marina/JBR, Downtown/Business Bay, DIFC, City Walk, Palm, JVC. Many are Lebanese, European, Russian/CIS, Indian, South African. They plan Thursday to Saturday, book tables in groups, follow lineups on RA and Platinumlist, and discover new DJs through track IDs and set clips, not through "free entry" posts.

## Where the content meets them

1. **Set clips with a track ID in the caption.** This is the single highest-signal format for house people. "ID: Keinemusik edit I played at 1am" gets saved and shared by exactly the people we want and ignored by everyone else. Cut 3–5 per night.
2. **Transitions.** 15 seconds, the mix point, no talking. House people judge DJs on this.
3. **Tag the scene.** Every clip tags the venue and, where honest, the label or artist of the track. Co-occurrence with those names is how both the algorithms and the humans file him.
4. **No crowd-hype hooks** ("the rooftop lost it 🔥"). They pull the wrong audience. Keep crowd shots as B-roll under a track ID, not as the hook.

Hook bank is in `content/hooks.md`, rewritten for this.

## Targeting (Meta, Dubai only)

Run through Claude with the official **Meta Ads MCP** (hosted at mcp.facebook.com/ads, launched 29 April 2026; add it as a custom connector in Claude and sign in with the Business account). Campaign structure:

| Ad set | Audience | Creative | Goal |
|---|---|---|---|
| A. Scene seed | Dubai, 23–38, interests: 6–10 of the artists above + Soho Garden, Terra Solis, Blu, Analog Room, Pacha ICONS. **Exclude** "clubbing", "ladies night", "free entry". | best set clip + track ID | site visits / leads |
| B. Warm | people who watched 75%+ of his clips in the last 30 days, or visited the site, minus those who joined the list | transition clip, "next one is Thursday" | leads |
| C. Lookalike | 1% UAE lookalike of the list's phone numbers (works from ~100 rows) | best clip from A | leads |

Budget AED 40–75/day total to start. Review Sundays: kill anything over AED 10 per sign-up, move budget to B and C as they come online. Optimise for leads (the form) never for followers.

The Meta Pixel ID goes in `data/artist.json → tracking.meta_pixel_id`; the form fires a `Lead` event on success. Without the pixel, B and C don't exist.

Same structure on TikTok via the TikTok for Business connector (also available in Claude's registry) when the TikTok side has 10+ clips of data.

## The free channels that matter more than ads

- **Resident Advisor.** Artist profile + get listed on the venue's RA events. The house crowd checks RA before anywhere else.
- **Venue tags and collab posts.** Every set, every time. Ask both venues.
- **Other DJs.** B2B sets, reposts, "with @". Three Dubai residents tagging him beats any ad.
- **Analog Room, Eurostar-type communities, record shops, DJ schools.** Be a regular, not a promoter.
- **Track IDs in comments on bigger accounts.** Being the person who knows the ID in a Keinemusik Dubai comment section is free, honest, and reaches exactly these people.
- **Platinumlist listing** for his nights; their newsletter reaches the table-booking segment.

## Channel for the list

Primary: **WhatsApp broadcast lists** (from the sheet; 256 per list, make several). Dubai runs on WhatsApp.
Public follow option: **WhatsApp Channel** link on the site (people who won't give a number yet). Instagram broadcast channel second. Telegram only if the CIS crowd becomes a real share, which the sheet will show.
Door: a private Telegram channel the Apps Script posts every sign-up into, so he and the host see the list live. Setup at the top of `scripts/guestlist_apps_script.gs`.

## What this deliberately doesn't do

No tooling that profiles or rates individuals. Not needed, not legal under UAE data law, and it doesn't work. The seed and the lookalike do the filtering.

## Legal: UAE Advertiser Permit

Since 1 February 2026 anyone promoting from inside the UAE, paid or unpaid, needs a UAE Media Council Advertiser Permit. Free for residents for three years, valid one year. He should apply before the first boosted post. Keep alcohol out of ad creatives.
