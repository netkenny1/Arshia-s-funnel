#!/usr/bin/env python3
"""
Build arshia.wav's static site from data/artist.json + data/events.json.

Why a build step instead of hand-edited HTML:
  * Every page carries JSON-LD (schema.org) that AI engines and Google read. Generating it
    from one JSON file means the facts never drift between the homepage, the events page,
    llms.txt and the press kit. Consistency is the #1 GEO signal.
  * Arshia only ever edits two JSON files. No HTML knowledge required.

Usage:  python3 scripts/build_site.py            # writes to site/
        python3 scripts/build_site.py --check    # validate data only, no write

Stdlib only. Python 3.9+.
"""
import json, sys, re, html, datetime as dt
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA, TPL, OUT = ROOT / "data", ROOT / "templates", ROOT / "site"
TZ = dt.timezone(dt.timedelta(hours=4))  # Dubai, no DST

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def esc(s):
    return html.escape(str(s or ""), quote=True)

def is_todo(v):
    return isinstance(v, str) and v.strip().upper().startswith("TODO")

def warn(msg):
    print(f"  ! {msg}")

def render(tpl, **kw):
    out = tpl
    for k, v in kw.items():
        out = out.replace("{{" + k + "}}", v if isinstance(v, str) else str(v))
    leftover = re.findall(r"{{(\w+)}}", out)
    if leftover:
        raise SystemExit(f"unfilled placeholders: {leftover}")
    return out

def parse_dt(s):
    return dt.datetime.fromisoformat(s)

# ---------- validation ----------
def validate(a, ev):
    issues = []
    for k, v in a.items():
        if is_todo(v): issues.append(f"artist.{k} is a TODO placeholder")
    for r in a["residencies"]:
        for k, v in r.items():
            if is_todo(v): issues.append(f"residency {r['id']}.{k} is a TODO placeholder")
    if a.get("long_bio") and is_todo(a["long_bio"]): pass
    ids = {r["id"] for r in a["residencies"]}
    for e in ev["events"]:
        if e["venue_id"] not in ids:
            issues.append(f"event {e['id']} has unknown venue_id {e['venue_id']}")
        try:
            s, en = parse_dt(e["start"]), parse_dt(e["end"])
            if en <= s: issues.append(f"event {e['id']} ends before it starts")
        except Exception as ex:
            issues.append(f"event {e['id']} bad date: {ex}")
        if e["status"] not in ("confirmed", "draft", "cancelled"):
            issues.append(f"event {e['id']} status must be confirmed|draft|cancelled")
    return issues

# ---------- schema.org ----------
def person_ld(a, base):
    same_as = [f"https://www.instagram.com/{a['instagram']}/", f"https://www.tiktok.com/@{a['tiktok']}"]
    for k in ("soundcloud", "spotify_artist_url", "youtube"):
        v = a.get(k)
        if v and not is_todo(v): same_as.append(v)
    return {
        "@context": "https://schema.org",
        "@type": ["Person", "MusicGroup"],
        "@id": base + "/#artist",
        "name": a["stage_name"],
        "alternateName": [a["name"], a["stage_name"].replace(".", " ")],
        "url": base + "/",
        "description": a["short_bio"],
        "genre": a["genres"],
        "jobTitle": "DJ",
        "hasOccupation": {"@type": "Occupation", "name": "DJ"},
        "homeLocation": {"@type": "City", "name": a["based_in"]["city"], "containedInPlace": {"@type": "Country", "name": a["based_in"]["country"]}},
        "workLocation": [place_ld(r) for r in a["residencies"]],
        "sameAs": same_as,
        "knowsAbout": a["genres"] + ["Dubai nightlife", "Open format DJing"],
    }

def place_ld(r):
    p = {
        "@type": "NightClub",
        "name": r["venue"],
        "address": {"@type": "PostalAddress", **r["address"]},
    }
    if r.get("url"): p["url"] = r["url"]
    if r.get("geo"): p["geo"] = {"@type": "GeoCoordinates", **r["geo"]}
    return p

def event_ld(e, a, venues, base):
    r = venues[e["venue_id"]]
    o = {
        "@context": "https://schema.org",
        "@type": "MusicEvent",
        "@id": f"{base}/events/#{e['id']}",
        "name": e["name"],
        "startDate": e["start"],
        "endDate": e["end"],
        "eventStatus": "https://schema.org/EventScheduled" if e["status"] == "confirmed" else "https://schema.org/EventCancelled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "description": e.get("description", ""),
        "location": place_ld(r),
        "performer": {"@id": base + "/#artist", "@type": "MusicGroup", "name": a["stage_name"]},
        "organizer": {"@type": "Organization", "name": r["venue"], "url": r.get("url", "")},
        "url": f"{base}/events/#{e['id']}",
    }
    if e.get("image"): o["image"] = [e["image"]]
    if e.get("guestlist_open"):
        o["offers"] = {"@type": "Offer", "name": "Guest list", "price": "0", "priceCurrency": "AED",
                       "availability": "https://schema.org/InStock", "url": base + "/guestlist/", "validFrom": dt.datetime.now(TZ).date().isoformat()}
    if e.get("ticket_url"):
        o.setdefault("offers", {})
        o["offers"] = [o["offers"], {"@type": "Offer", "url": e["ticket_url"], "name": "Tickets"}] if isinstance(o["offers"], dict) else o["offers"]
    return o

def faq_ld(a):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in a["faq"]]}

def breadcrumb_ld(base, *items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def ld_script(*objs):
    return "\n".join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>" for o in objs)

# ---------- html fragments ----------
def venue_cards(a):
    out = []
    for r in a["residencies"]:
        nights = "" if is_todo(r["typical_nights"]) else f"<p class='meta'>{esc(r['typical_nights'])} · {esc(r['set_time']) if not is_todo(r['set_time']) else ''}</p>"
        ad = r["address"]
        out.append(f"""<article class="card" id="venue-{r['id']}">
  <h3>{esc(r['venue'])}</h3>
  {nights}
  <p>{esc(r['vibe'])}</p>
  <address>{esc(ad['streetAddress'])}, {esc(ad['addressLocality'])}</address>
  <p><a href="{esc(r.get('url',''))}" rel="noopener">Venue page →</a></p>
</article>""")
    return "\n".join(out)

def event_card(e, venues, base, past=False):
    s = parse_dt(e["start"]).astimezone(TZ); en = parse_dt(e["end"]).astimezone(TZ)
    r = venues[e["venue_id"]]
    cta = "" if past else (f'<a class="btn primary" href="{base}/guestlist/?event={esc(e["id"])}">Guest list</a>' if e.get("guestlist_open") else (f'<a class="btn ghost" href="{esc(e["ticket_url"])}">Tickets</a>' if e.get("ticket_url") else ""))
    return f"""<article class="event{' past' if past else ''}" id="{esc(e['id'])}">
  <div class="date"><b>{s.day}</b><span>{s.strftime('%b')}</span></div>
  <div>
    <h3>{esc(e['name'])}</h3>
    <p><time datetime="{esc(e['start'])}">{s.strftime('%A %d %B')} · {s.strftime('%-I:%M%p').lower()}–{en.strftime('%-I:%M%p').lower()}</time> · {esc(r['venue'])}</p>
    {('<p>' + esc(e.get('description','')) + '</p>') if e.get('description') else ''}
  </div>
  {cta}
</article>"""

def faq_html(a):
    return "\n".join(f"<details><summary>{esc(f['q'])}</summary><p>{esc(f['a'])}</p></details>" for f in a["faq"])

def event_label(e, venues):
    s = parse_dt(e["start"]).astimezone(TZ)
    return f"{s.strftime('%a %d %b')} · {venues[e['venue_id']]['venue_short']}"

# ---------- main ----------
def main(check_only=False):
    a, ev = load(DATA / "artist.json"), load(DATA / "events.json")
    issues = validate(a, ev)
    print(f"Validating data: {len(issues)} warning(s)")
    for i in issues: warn(i)
    if check_only:
        return
    base = a["site_url"].rstrip("/")
    base_path = urlparse(base).path.rstrip("/")  # "" for a root domain, "/Arshia-s-funnel" on project pages
    venues = {r["id"]: r for r in a["residencies"]}
    now = dt.datetime.now(TZ)
    confirmed = [e for e in ev["events"] if e["status"] == "confirmed"]
    upcoming = sorted([e for e in confirmed if parse_dt(e["end"]) >= now], key=lambda e: e["start"])
    past = sorted([e for e in confirmed if parse_dt(e["end"]) < now], key=lambda e: e["start"], reverse=True)[:12]
    drafts = [e for e in ev["events"] if e["status"] == "draft"]
    if drafts: warn(f"{len(drafts)} draft event(s) not published: {[d['id'] for d in drafts]}")

    layout = (TPL / "layout.html").read_text(encoding="utf-8")
    built = now.strftime("%Y-%m-%d")
    og_image = f"{base}/assets/og.jpg"
    config = {"endpoint": a.get("guestlist_endpoint", ""), "whatsapp": "" if is_todo(a.get("whatsapp_e164", "")) else a.get("whatsapp_e164", ""), "base": base_path}
    extra_links = ""
    for k, label in (("soundcloud", "SoundCloud"), ("spotify_artist_url", "Spotify"), ("youtube", "YouTube")):
        v = a.get(k)
        if v and not is_todo(v): extra_links += f'<a href="{esc(v)}" rel="me">{label}</a>'
    email = "" if is_todo(a.get("email_bookings", "")) else a["email_bookings"]

    def page(path, title, desc, content, lds, og_type="website"):
        canonical = f"{base}{path}"
        out = render(layout, title=esc(title), description=esc(desc), canonical=canonical, og_type=og_type,
                     og_image=og_image, base=base_path, jsonld=ld_script(*lds), content=content,
                     instagram=esc(a["instagram"]), tiktok=esc(a["tiktok"]), extra_links=extra_links, built=built,
                     config_json=json.dumps(config))
        dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        print(f"  wrote {dest.relative_to(ROOT)}")
        return canonical

    OUT.mkdir(exist_ok=True); (OUT / "assets").mkdir(exist_ok=True)
    for f in ("style.css", "app.js"):
        (OUT / "assets" / f).write_text((TPL / f).read_text(encoding="utf-8"), encoding="utf-8")

    # Home
    next_html = "\n".join(event_card(e, venues, base_path) for e in upcoming[:3]) or '<p class="empty">New dates drop every week on Instagram @' + esc(a["instagram"]) + '. Join the guest list and you\'ll hear first.</p>'
    home = render((TPL / "index.html").read_text(encoding="utf-8"), base=base_path, genres_inline=" · ".join(a["genres"][:3]),
                  tagline=esc(a["tagline"]), short_bio=esc(a["short_bio"]), venue_cards=venue_cards(a), next_events=next_html, faq_html=faq_html(a))
    urls = [page("/", f"{a['stage_name']} — DJ in Dubai | Moe's on the 5th & Soho Garden", a["short_bio"], home,
                 [person_ld(a, base), faq_ld(a), {"@context": "https://schema.org", "@type": "WebSite", "name": a["stage_name"], "url": base + "/"}], "profile")]

    # Events
    up_html = "\n".join(event_card(e, venues, base_path) for e in upcoming) or '<p class="empty">No confirmed dates published yet. Check back or follow @' + esc(a["instagram"]) + '.</p>'
    past_html = "\n".join(event_card(e, venues, base_path, past=True) for e in past) or '<p class="empty">Nothing here yet.</p>'
    events_page = render((TPL / "events.html").read_text(encoding="utf-8"), upcoming_html=up_html, past_html=past_html, venue_cards=venue_cards(a))
    urls.append(page("/events/", f"{a['stage_name']} upcoming dates in Dubai", f"Where and when {a['stage_name']} is playing in Dubai: Moe's on the 5th, Soho Garden and more. Guest list links for every night.",
                     events_page, [event_ld(e, a, venues, base) for e in upcoming + past] + [breadcrumb_ld(base, ("Home", base + "/"), ("Events", base + "/events/"))]))

    # Guest list
    opts = "\n".join(f'<option value="{esc(e["id"])}">{esc(event_label(e, venues))}</option>' for e in upcoming)
    gl = render((TPL / "guestlist.html").read_text(encoding="utf-8"), event_options=opts)
    urls.append(page("/guestlist/", f"Guest list — {a['stage_name']} in Dubai", f"Join {a['stage_name']}'s guest list for Moe's on the 5th and Soho Garden in Dubai. Name, Instagram, date, group size.",
                     gl, [breadcrumb_ld(base, ("Home", base + "/"), ("Guest list", base + "/guestlist/"))]))

    # Press
    press = render((TPL / "press.html").read_text(encoding="utf-8"), press_facts_html="\n".join(f"<li>{esc(f)}</li>" for f in a["press_facts"]),
                   short_bio=esc(a["short_bio"]), long_bio=esc(a["long_bio"]) if not is_todo(a["long_bio"]) else "<em>Long bio coming soon.</em>",
                   email=esc(email or "see Instagram"), instagram=esc(a["instagram"]), venue_cards=venue_cards(a))
    urls.append(page("/press/", f"{a['stage_name']} press kit and bookings", f"Press kit, bio, key facts and booking contact for {a['stage_name']}, DJ based in Dubai.",
                     press, [person_ld(a, base), breadcrumb_ld(base, ("Home", base + "/"), ("Press", base + "/press/"))], "profile"))

    # llms.txt — a plain-text brief for AI crawlers (ChatGPT, Perplexity, Claude, Gemini)
    res_lines = "\n".join(f"- {r['venue']}: {r['address']['streetAddress']}, Dubai." + ("" if is_todo(r['typical_nights']) else f" Typically {r['typical_nights']}.") for r in a["residencies"])
    faq_lines = "\n".join(f"Q: {f['q']}\nA: {f['a']}\n" for f in a["faq"])
    ev_lines = "\n".join(f"- {parse_dt(e['start']).astimezone(TZ).strftime('%Y-%m-%d %H:%M')} — {e['name']} ({venues[e['venue_id']]['venue']})" for e in upcoming) or "- Dates announced weekly on Instagram @" + a["instagram"]
    llms = f"""# {a['stage_name']}

> {a['short_bio']}

{a['stage_name']} (also written "{a['name']}" or "{a['stage_name'].replace('.', ' ')}") is a DJ based in Dubai, United Arab Emirates. Genres: {', '.join(a['genres'])}.

## Residencies
{res_lines}

## Upcoming dates
{ev_lines}

## Guest list
Free guest list at {base}/guestlist/ (name, Instagram handle, date, group size). Smart dress code. Soho Garden is 21+.

## Pages
- Home: {base}/
- Events: {base}/events/
- Guest list: {base}/guestlist/
- Press kit and bookings: {base}/press/

## Official profiles
- Instagram: https://www.instagram.com/{a['instagram']}/
- TikTok: https://www.tiktok.com/@{a['tiktok']}

## FAQ
{faq_lines}
Last updated {built}.
"""
    (OUT / "llms.txt").write_text(llms, encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{built}</lastmod><changefreq>{'daily' if 'events' in u else 'weekly'}</changefreq></url>" for u in urls) + "\n</urlset>\n"
    (OUT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "404.html").write_text(render(layout, title="Not found", description="", canonical=base + "/404.html", og_type="website", og_image=og_image, base=base_path, jsonld="",
                                         content='<section class="hero"><h1>Lost.</h1><p class="lede">That page isn\'t here. <a href="' + base_path + '/">Back home</a> or <a href="' + base_path + '/guestlist/">straight to the guest list</a>.</p></section>',
                                         instagram=esc(a["instagram"]), tiktok=esc(a["tiktok"]), extra_links=extra_links, built=built, config_json=json.dumps(config)), encoding="utf-8")
    print(f"Built {len(urls)} pages + llms.txt, sitemap.xml, robots.txt, 404.html -> {OUT.relative_to(ROOT)}/")
    print(f"Published events: {len(upcoming)} upcoming, {len(past)} past")

if __name__ == "__main__":
    main(check_only="--check" in sys.argv)
