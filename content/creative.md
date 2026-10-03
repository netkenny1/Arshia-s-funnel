# Creative

## Brand kit (first pass)
- Wordmark: `arshia.wav` lowercase, the `.wav` in acid yellow `#E9FF3F` on near-black `#0B0B0F`. Same as the site.
- Secondary: white, 1px hairlines, no gradients.
- Type: Inter (free) or the system sans. Big, tight, lowercase.
- Photo treatment: real crowd, high contrast, slight grain. No stock, no renders.

## Templates to make in Canva (1080×1920 story, 1080×1350 feed)
1. **Guest list open** — venue, day, time, "link in bio", QR to `/guestlist/`.
2. **Tonight** — one crowd photo, venue, "list closes 9pm".
3. **Photo dump cover** — "last night at Moe's", date.
4. **Monthly dates** — grid of the month's nights (from `events.json`).

Ask Claude (with the Canva connector) to generate these from the brand kit above and the dates in `data/events.json`; `canva/` in this repo holds the exported drafts when that's done.

## OG image
`site/assets/og.jpg`, 1200×630: wordmark + "DJ · Dubai · Moe's on the 5th · Soho Garden" + one crowd photo. This is what WhatsApp shows when the guest list link is shared.
