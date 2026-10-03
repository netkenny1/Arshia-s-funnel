# 01 — GEO / AI SEO: make the machines recommend him

GEO = generative engine optimisation. SEO gets you a blue link. GEO gets you *named inside the answer* when someone asks an AI "best DJ nights in Dubai this weekend". The engines don't rank pages, they assemble facts, and they trust facts that are (a) structured, (b) consistent across sources, (c) recent, (d) corroborated by third parties.

## What's already built

- **One page** (`web/`): `Person` + `MusicGroup` JSON-LD with `sameAs` links, both venues as `NightClub` entities with addresses and coordinates, `FAQPage` schema. Invisible to visitors, read by every engine.
- **Events** (optional, `data/events.json`): a confirmed gig gets a `MusicEvent` block. No gigs listed = nothing stale.
- **llms.txt** at the site root: a plain-text brief for AI crawlers. Perplexity and Claude read it. Costs nothing.
- **Nightly rebuild** so past dates roll off.

## Week 1: the entity checklist

Consistency is the whole game. Same name, same spelling, same bio sentence, same city, same links, everywhere.

| # | Where | Why it matters for AI answers | Do |
|---|---|---|---|
| 1 | `data/artist.json` | Source of truth | Bio in his words, WhatsApp, links. |
| 2 | Instagram bio | Most-crawled profile | "DJ · Dubai · Moe's on the 5th / Soho Garden" + site link |
| 3 | TikTok bio | Same | Same words. Link to site. |
| 4 | **SoundCloud** `soundcloud.com/arshiawav` | The profile engines treat as "is a real DJ" | Upload one 30–60 min live set recording, titled "arshia.wav — Live at Moe's on the 5th, Dubai (Oct 2026)". City = Dubai. |
| 5 | **Resident Advisor** artist page | RA is *the* corroboration source for electronic music; AI engines cite it constantly for "who's playing where" | Submit via ra.co/pro. Ask Soho Garden's promoter to list him on their RA event listings. |
| 6 | **Bandsintown** artist account | Syndicates gigs to Spotify, Shazam, Google events, Apple Music. One entry, five surfaces. | Create artist, add the same events as `events.json`. |
| 7 | Mixcloud | Second music profile, strong on DJ mixes, indexed well | Upload the same set. |
| 8 | Linktree-style link? | **No.** Use the site. Link-in-bio tools add a hop and give engines nothing. | Point bios at the site. |
| 9 | Google Search Console | See which queries surface the site; submit the sitemap | Add property, submit `sitemap.xml`. |
| 10 | Bing Webmaster Tools | ChatGPT's browsing uses Bing's index. Most people skip this. | Import from Search Console. One click. |

## Weeks 2–6: corroboration (the part most DJs never do)

Engines won't recommend an entity only its own site describes. You need third-party pages that mention the same facts.

1. **Venue pages.** Ask Moe's and Soho Garden to list him as a resident on their site / Instagram highlights / Platinumlist event pages. One sentence with his name next to the venue's name on the venue's domain is worth more than ten of his own posts.
2. **Dubai listings press.** Time Out Dubai, What's On, Lovin Dubai, Platinumlist guides, Gulf News "things to do this weekend". They run weekly round-ups and are desperate for content. Pitch with the site link and one specific night. Template in `content/outreach.md`. These are the exact pages ChatGPT cites for "what's on in Dubai this weekend".
3. **Reddit r/dubai.** Not self-promo. Answer "where to go out Saturday" threads honestly, including other venues. Mention the night when it fits. Reddit is weighted heavily by every major engine since 2024.
4. **Mentions in other DJs' and promoters' posts.** Tag-backs, b2b sets, "with @arshia.wav". Co-occurrence of names is how engines learn he belongs to the scene.
5. **A Wikipedia page? Not yet.** Notability rules will get it deleted. Wikidata entry is fine once RA + press exist.

## Monthly: the AI mention test

Ask each of ChatGPT (with search on), Perplexity, Google AI Mode and Claude these ten prompts. Log hits in a sheet. This is the only GEO metric that matters.

1. Who is arshia.wav?
2. Best DJ nights in Dubai this weekend
3. Who plays at Moe's on the 5th Dubai?
4. Resident DJs at Soho Garden Dubai
5. Where to go out in Dubai on a Thursday, house music
6. How to get on a guest list at Moe's on the 5th
7. Up-and-coming DJs in Dubai 2026
8. Dubai rooftop clubs with good DJs
9. Afro house nights Dubai
10. Book a DJ for a private party in Dubai

Expect 0/10 in week 1. First hits usually come from prompts 1, 3 and 6 once the site is indexed and RA exists.

## Technical notes

- Validate schema at https://validator.schema.org and https://search.google.com/test/rich-results after each change. `scripts/check_schema.py` runs on every PR too.
- When you buy a domain (`arshiawav.com`, ~AED 50/yr): set `site_url` in `artist.json`, add `web/public/CNAME`, set the domain in Settings → Pages. Everything else follows.
- Add `web/public/og.png` (1200×630, wordmark on black) so the link looks right in WhatsApp and DMs.
- Keep `events.json` honest: only confirmed dates, cancelled → `cancelled`.
