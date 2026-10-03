# TikTok iteration loop

**The idea:** TikTok Studio tells you what happened. It cannot tell you *why*. The `content_log.csv` is where you spend 60 seconds per video writing down the creative decisions, so the script can correlate decisions with results.

## Weekly routine (15 minutes)

1. **Export**: studio.tiktok.com → Analytics → Content → Download data (CSV). Save it as `tiktok/exports/YYYY-MM-DD.csv`.
2. **Annotate**: open `tiktok/content_log.csv`, add one row per new video. Columns:
   - `video_id` (or `url`) — copy from the export so the rows join
   - `hook_type` — one of: `crowd_reaction`, `pov_dj_booth`, `transition_reveal`, `dubai_hook`, `guestlist_cta`, `song_id`, `day_in_life`, `controversy` (add your own, just be consistent)
   - `format` — e.g. `crowd pan from booth`, `tripod behind decks`, `split screen`, `talking head`, `photo dump`
   - `venue` — `Moe's`, `Soho`, `studio`, `car`, `home`
   - `sound` — `set audio`, `trending sound`, `own edit`, `voiceover`
   - `cta` — `guest list`, `follow`, `comment song`, `none`
   - `on_screen_text` — `y` / `n`
   - `face_first_2s` — `y` / `n`
3. **Run**:
   ```
   python3 scripts/tiktok_report.py tiktok/exports/2026-10-10.csv
   ```
4. **Read** `tiktok/reports/<date>.md`. Shoot the 7 videos it lists. Repeat.

Instagram Reels: Meta Business Suite → Insights → Content → Export. Same script, same log.

## Why shares + saves, not likes

TikTok's recommender weights "sends" (shares to DMs) and completion far above likes. For a nightlife account, a share is literally someone sending the clip to a friend saying "we're going here." That is the exact behaviour that fills a guest list, so `viral_rate` is the number the report optimises for.
