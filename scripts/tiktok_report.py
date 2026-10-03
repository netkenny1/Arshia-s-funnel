#!/usr/bin/env python3
"""
TikTok iteration engine for arshia.wav.

What it does
  1. Reads the CSV you export from TikTok Studio (Analytics -> Content -> Download data). Also accepts
     Instagram Reels exports from Meta Business Suite; headers are matched fuzzily.
  2. Joins it with tiktok/content_log.csv, the 60-second-per-video annotation sheet (hook type, format,
     venue, sound, CTA...). The export tells you WHAT happened, the log tells you WHY.
  3. Scores every video, finds which patterns beat the account median, and writes a markdown report
     with a concrete shoot list for next week: 6 slots exploiting winners + 1 slot testing something new.

Usage
  python3 scripts/tiktok_report.py <tiktok_export.csv> [--log tiktok/content_log.csv] [--out tiktok/reports/YYYY-MM-DD.md]

Stdlib only. Nothing leaves your machine.
"""
import csv, sys, re, json, statistics as st, datetime as dt, argparse, random
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]

# ---------- header normalisation ----------
ALIASES = {
    "id":        ["video id", "post id", "id", "media id"],
    "url":       ["video url", "url", "link", "permalink"],
    "caption":   ["video caption", "caption", "title", "description", "video title", "post"],
    "posted":    ["posted date", "post time", "posted", "date", "publish time", "create time", "published", "time posted"],
    "views":     ["video views", "views", "plays", "total views", "reach"],
    "likes":     ["likes", "like count", "total likes"],
    "comments":  ["comments", "comment count"],
    "shares":    ["shares", "share count"],
    "saves":     ["favorites", "favourites", "saves", "saved", "bookmarks", "favorites count"],
    "duration":  ["video duration", "duration", "length", "duration (s)"],
    "watch":     ["average watch time", "avg watch time", "average time watched"],
    "full":      ["watched full video", "full video watch rate", "completion rate", "watched full video (%)"],
    "followers": ["new followers", "followers gained", "follows"],
    "profile":   ["profile views", "profile visits"],
}

def norm(h): return re.sub(r"[^a-z0-9% ()]", "", h.strip().lower())

def map_headers(headers):
    m = {}
    nh = {norm(h): h for h in headers}
    for key, cands in ALIASES.items():
        for c in cands:
            if c in nh and key not in m:
                m[key] = nh[c]; break
        if key not in m:  # substring fallback
            for n, h in nh.items():
                if any(c in n for c in cands) and h not in m.values():
                    m[key] = h; break
    return m

def num(v):
    if v is None: return 0.0
    s = str(v).strip().replace(",", "").replace("%", "")
    if s == "" or s.lower() in ("na", "n/a", "-", "--"): return 0.0
    mult = 1
    if s[-1:].upper() == "K": mult, s = 1000, s[:-1]
    elif s[-1:].upper() == "M": mult, s = 1_000_000, s[:-1]
    try: return float(s) * mult
    except ValueError: return 0.0

def dur_seconds(v):
    s = str(v).strip()
    if ":" in s:
        parts = [num(p) for p in s.split(":")]
        return parts[-1] + 60 * parts[-2] + (3600 * parts[-3] if len(parts) > 2 else 0)
    return num(s)

def parse_date(v):
    s = str(v).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%b %d, %Y %H:%M", "%b %d, %Y", "%d %b %Y %H:%M", "%d %b %Y"):
        try: return dt.datetime.strptime(s[:len(dt.datetime.now().strftime(fmt))] if "%" in fmt else s, fmt)
        except ValueError: pass
    try: return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError: return None

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096); f.seek(0)
        try: dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error: dialect = csv.excel
        rows = list(csv.DictReader(f, dialect=dialect))
    return rows

# ---------- load + join ----------
def load_videos(export_path, log_path):
    raw = read_csv(export_path)
    if not raw: raise SystemExit("export is empty")
    m = map_headers(raw[0].keys())
    missing = [k for k in ("views",) if k not in m]
    if missing: raise SystemExit(f"could not find columns for {missing}; headers were {list(raw[0].keys())}")
    log = {}
    if log_path and Path(log_path).exists():
        for r in read_csv(log_path):
            key = (r.get("video_id") or r.get("url") or "").strip()
            if key: log[key.lower()] = {k.strip().lower(): (v or "").strip() for k, v in r.items()}
    vids = []
    for r in raw:
        v = {
            "id": (r.get(m.get("id"), "") or "").strip(),
            "url": (r.get(m.get("url"), "") or "").strip(),
            "caption": (r.get(m.get("caption"), "") or "").strip(),
            "posted": parse_date(r.get(m.get("posted"), "")) if "posted" in m else None,
            "views": num(r.get(m.get("views"))),
            "likes": num(r.get(m.get("likes"))) if "likes" in m else 0,
            "comments": num(r.get(m.get("comments"))) if "comments" in m else 0,
            "shares": num(r.get(m.get("shares"))) if "shares" in m else 0,
            "saves": num(r.get(m.get("saves"))) if "saves" in m else 0,
            "duration": dur_seconds(r.get(m.get("duration"))) if "duration" in m else 0,
            "watch": dur_seconds(r.get(m.get("watch"))) if "watch" in m else 0,
            "full": num(r.get(m.get("full"))) if "full" in m else 0,
            "followers": num(r.get(m.get("followers"))) if "followers" in m else 0,
        }
        if v["views"] <= 0: continue
        # derived
        v["eng_rate"] = (v["likes"] + v["comments"] + v["shares"] + v["saves"]) / v["views"]
        v["share_rate"] = v["shares"] / v["views"]
        v["save_rate"] = v["saves"] / v["views"]
        v["viral_rate"] = (v["shares"] + v["saves"]) / v["views"]  # sends + saves = the two signals the FYP weights most
        v["hashtags"] = [h.lower() for h in re.findall(r"#(\w+)", v["caption"])]
        v["dow"] = v["posted"].strftime("%a") if v["posted"] else "?"
        v["hour"] = hour_bucket(v["posted"].hour) if v["posted"] else "?"
        v["dur_bucket"] = dur_bucket(v["duration"])
        ann = log.get(v["id"].lower()) or log.get(v["url"].lower()) or {}
        for k in ("hook_type", "format", "venue", "sound", "cta", "on_screen_text", "face_first_2s", "notes"):
            v[k] = ann.get(k, "") or "?"
        v["annotated"] = bool(ann)
        vids.append(v)
    return vids, m

def hour_bucket(h):
    if 6 <= h < 11: return "morning 6-11"
    if 11 <= h < 15: return "midday 11-15"
    if 15 <= h < 19: return "afternoon 15-19"
    if 19 <= h < 23: return "evening 19-23"
    return "late 23-6"

def dur_bucket(s):
    if s <= 0: return "?"
    if s < 8: return "<8s"
    if s < 15: return "8-15s"
    if s < 30: return "15-30s"
    if s < 60: return "30-60s"
    return "60s+"

# ---------- analysis ----------
DIMS = [("hook_type", "Hook type"), ("format", "Format"), ("venue", "Venue / setting"), ("sound", "Sound"),
        ("cta", "Call to action"), ("on_screen_text", "On-screen text"), ("face_first_2s", "Face in first 2s"),
        ("dow", "Day posted"), ("hour", "Hour posted (your local time)"), ("dur_bucket", "Length")]

def median(xs): return st.median(xs) if xs else 0

def pattern_table(vids, key, overall_med_views, overall_viral):
    groups = defaultdict(list)
    for v in vids:
        if v[key] not in ("?", ""): groups[v[key]].append(v)
    rows = []
    for g, vs in groups.items():
        mv = median([v["views"] for v in vs]); vr = median([v["viral_rate"] for v in vs])
        lift = (mv / overall_med_views - 1) if overall_med_views else 0
        rows.append({"value": g, "n": len(vs), "med_views": mv, "viral": vr, "lift": lift,
                     "verdict": verdict(len(vs), lift, vr, overall_viral)})
    rows.sort(key=lambda r: (-r["lift"] if r["n"] >= 2 else 0, -r["n"]))
    return rows

def verdict(n, lift, vr, overall_viral):
    if n < 2: return "too few to call"
    if lift >= 0.5 and vr >= overall_viral: return "WINNER"
    if lift >= 0.25: return "promising"
    if lift <= -0.4: return "kill"
    return "neutral"

def fmt_int(x): return f"{int(round(x)):,}"
def pct(x): return f"{100*x:.1f}%"

def hashtag_table(vids, overall_med):
    groups = defaultdict(list)
    for v in vids:
        for h in set(v["hashtags"]): groups[h].append(v["views"])
    rows = [{"tag": "#" + h, "n": len(x), "med": median(x), "lift": median(x) / overall_med - 1 if overall_med else 0} for h, x in groups.items() if len(x) >= 2]
    return sorted(rows, key=lambda r: -r["lift"])[:12]

HOOK_BANK = {
    "crowd_reaction": ["POV: the drop hits at Moe's at 1am", "the moment the whole rooftop lost it", "nobody expected this transition"],
    "pov_dj_booth": ["POV: you're in the booth with me at Soho Garden", "what I see from the decks at midnight", "booth cam: last 30 seconds of my set"],
    "transition_reveal": ["wait for the transition", "I mixed [song A] into [song B] and it shouldn't work", "the edit everyone keeps asking for"],
    "dubai_hook": ["if you're in Dubai this weekend, this is where to be", "the best rooftop sound on Sheikh Zayed Road rn", "Dubai Saturday > any other Saturday"],
    "guestlist_cta": ["I put 20 people on the list every week, here's how", "guest list is open for Friday, link in bio", "free entry on my list this Thursday"],
    "song_id": ["this song ID is the most requested of the month", "ID: the afro house track from Saturday", "the song you Shazamed at 1:12am"],
    "day_in_life": ["a Thursday as a Dubai DJ, from crate digging to 2am", "what a resident DJ actually does before doors", "soundcheck to last song in 20 seconds"],
    "controversy": ["unpopular opinion: Dubai crowds are better than Ibiza for this reason", "things promoters won't tell you about guest list", "DJs who play the same 10 songs, this is for you"],
}
FORMATS = ["crowd pan from booth", "phone on tripod behind decks", "split: hands on decks / crowd", "photo dump with set audio", "talking head then set clip", "slow-mo crowd + text overlay"]

def winners_for(key, tables):
    return [r["value"] for r in tables.get(key, []) if r["verdict"] in ("WINNER", "promising")]

def build_plan(tables, vids):
    hooks = winners_for("hook_type", tables) or list(HOOK_BANK.keys())[:3]
    formats = winners_for("format", tables) or FORMATS[:3]
    venues = winners_for("venue", tables) or ["Moe's on the 5th", "Soho Garden"]
    days = winners_for("dow", tables) or ["Thu", "Fri", "Sat"]
    hours = winners_for("hour", tables) or ["evening 19-23"]
    durs = winners_for("dur_bucket", tables) or ["8-15s"]
    sounds = winners_for("sound", tables) or ["set audio (original)"]
    ctas = winners_for("cta", tables) or ["guest list link in bio"]
    tested_hooks = {v["hook_type"] for v in vids if v["hook_type"] != "?"}
    untested = [h for h in HOOK_BANK if h not in tested_hooks]
    plan = []
    rnd = random.Random(len(vids))
    for i in range(6):
        h = hooks[i % len(hooks)]
        plan.append({"slot": i + 1, "type": "exploit", "hook_type": h, "hook_line": rnd.choice(HOOK_BANK.get(h, ["[write a hook that states the payoff in 6 words]"])),
                     "format": formats[i % len(formats)], "venue": venues[i % len(venues)], "post": f"{days[i % len(days)]} · {hours[i % len(hours)]}",
                     "length": durs[0], "sound": sounds[0], "cta": ctas[0]})
    if untested:
        h = untested[0]
        plan.append({"slot": 7, "type": "explore", "hook_type": h, "hook_line": HOOK_BANK[h][0], "format": rnd.choice(FORMATS), "venue": venues[0],
                     "post": f"{days[0]} · {hours[0]}", "length": durs[0], "sound": sounds[0], "cta": ctas[0]})
    return plan

# ---------- report ----------
def report(vids, mapping, out_path, export_name):
    vids_sorted = sorted(vids, key=lambda v: -v["views"])
    n = len(vids); views = [v["views"] for v in vids]
    med_v = median(views); mean_v = sum(views) / n
    overall_viral = median([v["viral_rate"] for v in vids])
    eng = median([v["eng_rate"] for v in vids])
    annotated = sum(v["annotated"] for v in vids)
    tables = {k: pattern_table(vids, k, med_v, overall_viral) for k, _ in DIMS}
    plan = build_plan(tables, vids)
    top = vids_sorted[:5]; bottom = vids_sorted[-5:][::-1]
    span = ""
    dates = [v["posted"] for v in vids if v["posted"]]
    if dates: span = f"{min(dates):%d %b %Y} → {max(dates):%d %b %Y}"

    L = []
    L.append(f"# arshia.wav content report — {dt.date.today():%d %b %Y}\n")
    L.append(f"Source: `{export_name}` · {n} videos · {span}  ")
    L.append(f"Annotated in content_log: {annotated}/{n}" + ("" if annotated == n else "  ← annotate the rest, patterns below get sharper with every row"))
    L.append("")
    L.append("## Scoreboard\n")
    L.append("| Metric | Value | What it means |")
    L.append("|---|---|---|")
    L.append(f"| Median views | {fmt_int(med_v)} | Your 'normal' video. Beat this and the pattern is real. |")
    L.append(f"| Mean views | {fmt_int(mean_v)} | {'Mean >> median: a few videos carry the account. Study them.' if mean_v > 1.8 * med_v else 'Flat distribution: no breakout yet, keep testing hooks.'} |")
    L.append(f"| Median engagement rate | {pct(eng)} | likes+comments+shares+saves ÷ views. 5%+ is strong for nightlife. |")
    L.append(f"| Median viral rate (shares+saves) | {pct(overall_viral)} | The FYP's favourite signal. 1%+ means the algorithm keeps pushing. |")
    L.append(f"| Total views | {fmt_int(sum(views))} | |")
    if any(v["followers"] for v in vids):
        L.append(f"| New followers | {fmt_int(sum(v['followers'] for v in vids))} | Follower conversion = {pct(sum(v['followers'] for v in vids)/sum(views))} of views |")
    L.append("")

    L.append("## Top 5\n")
    L.append("| Views | Viral rate | Hook type | Format | Caption |")
    L.append("|---|---|---|---|---|")
    for v in top: L.append(f"| {fmt_int(v['views'])} | {pct(v['viral_rate'])} | {v['hook_type']} | {v['format']} | {v['caption'][:70].replace('|','/')} |")
    L.append("\n## Bottom 5\n")
    L.append("| Views | Viral rate | Hook type | Format | Caption |")
    L.append("|---|---|---|---|---|")
    for v in bottom: L.append(f"| {fmt_int(v['views'])} | {pct(v['viral_rate'])} | {v['hook_type']} | {v['format']} | {v['caption'][:70].replace('|','/')} |")

    L.append("\n## Patterns (lift = median views of this group vs account median)\n")
    L.append("Rules: a pattern needs 2+ videos to count. WINNER = +50% views AND viral rate at/above account median. Kill = −40% or worse.\n")
    for key, label in DIMS:
        rows = tables[key]
        if not rows: continue
        L.append(f"### {label}\n")
        L.append("| Value | n | Median views | Viral rate | Lift | Verdict |")
        L.append("|---|---|---|---|---|---|")
        for r in rows:
            L.append(f"| {r['value']} | {r['n']} | {fmt_int(r['med_views'])} | {pct(r['viral'])} | {'+' if r['lift']>=0 else ''}{100*r['lift']:.0f}% | {r['verdict']} |")
        L.append("")
    ht = hashtag_table(vids, med_v)
    if ht:
        L.append("### Hashtags (2+ uses)\n")
        L.append("| Tag | n | Median views | Lift |")
        L.append("|---|---|---|---|")
        for r in ht: L.append(f"| {r['tag']} | {r['n']} | {fmt_int(r['med'])} | {'+' if r['lift']>=0 else ''}{100*r['lift']:.0f}% |")
        L.append("")

    winners = [(label, r["value"]) for key, label in DIMS for r in tables[key] if r["verdict"] == "WINNER"]
    kills = [(label, r["value"]) for key, label in DIMS for r in tables[key] if r["verdict"] == "kill"]
    L.append("## Read this part\n")
    L.append("**Double down on:** " + (", ".join(f"{l} = {v}" for l, v in winners) if winners else "nothing is a clear winner yet. Post 7 more with distinct hook types and re-run.") + "  ")
    L.append("**Stop doing:** " + (", ".join(f"{l} = {v}" for l, v in kills) if kills else "nothing is clearly dead yet.") + "  ")
    L.append("")

    L.append("## Next 7 videos (shoot list)\n")
    L.append("Six exploit what's working, one explores an untested hook. Shoot all seven in one night at the venue; posting is spread across the week.\n")
    L.append("| # | Type | Hook (first 2 seconds) | Format | Venue | Post | Length | Sound | CTA |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in plan:
        L.append(f"| {p['slot']} | {p['type']} | *{p['hook_line']}* ({p['hook_type']}) | {p['format']} | {p['venue']} | {p['post']} | {p['length']} | {p['sound']} | {p['cta']} |")
    L.append("")
    L.append("Every video: on-screen text in the first frame, caption with 'Dubai' + venue name (TikTok search is now the second-biggest discovery surface), ")
    L.append("link in bio to the guest list page with `?utm_source=tiktok&utm_content=<video-slug>` so the sheet shows which video filled the list.")
    L.append("")
    L.append("## Loop\n")
    L.append("1. Post the 7. 2. After 72h, export again from TikTok Studio. 3. Add the 7 rows to content_log.csv (60 seconds). 4. Re-run this script. 5. Repeat. Four cycles = a month, and by then the winners are obvious.")
    out = "\n".join(L)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(out, encoding="utf-8")
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export")
    ap.add_argument("--log", default=str(ROOT / "tiktok" / "content_log.csv"))
    ap.add_argument("--out", default=str(ROOT / "tiktok" / "reports" / f"{dt.date.today()}.md"))
    ap.add_argument("--json", help="also dump the per-video table as JSON")
    a = ap.parse_args()
    vids, mapping = load_videos(a.export, a.log)
    print(f"Mapped columns: {json.dumps(mapping)}")
    print(f"Loaded {len(vids)} videos ({sum(v['annotated'] for v in vids)} annotated)")
    out = report(vids, mapping, a.out, Path(a.export).name)
    if a.json:
        Path(a.json).write_text(json.dumps([{k: (v.isoformat() if isinstance(v, dt.datetime) else v) for k, v in vid.items()} for vid in vids], indent=2), encoding="utf-8")
    print(f"Report -> {a.out}")

if __name__ == "__main__":
    main()
