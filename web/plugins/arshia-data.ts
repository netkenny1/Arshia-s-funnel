/**
 * Vite plugin: turns ../data/artist.json + ../data/events.json into
 *   - a virtual module `virtual:arshia` the app imports (typed, tree-shaken)
 *   - <head> injections: title, meta, canonical, OG, JSON-LD (Person/MusicGroup, MusicEvent, FAQPage), pixels
 *   - build outputs: llms.txt, sitemap.xml, robots.txt, 404.html, .nojekyll
 * One source of truth, no drift between what people see and what machines read.
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import type { Plugin, ResolvedConfig } from "vite";

export interface Venue { id: string; name: string; url: string; address: Record<string, string>; geo?: { latitude: number; longitude: number } }
export interface Event { id: string; status: "confirmed" | "draft" | "cancelled"; name: string; venue_id: string; start: string; end: string; description?: string; guestlist_open?: boolean; ticket_url?: string }
export interface Artist {
  stage_name: string; name: string; role: string; city: string; country: string; country_code: string;
  one_liner: string; bio: string; genres: string[]; instagram: string; tiktok: string;
  soundcloud_url: string; soundcloud_embed_track_url: string; resident_advisor_url: string; spotify_artist_url: string;
  email_bookings: string; whatsapp_e164: string; site_url: string; guestlist_endpoint: string;
  channels: { whatsapp_channel_url: string; instagram_broadcast_url: string; telegram_channel_url: string };
  tracking: { meta_pixel_id: string; tiktok_pixel_id: string };
  venues: Venue[]; faq: { q: string; a: string }[];
}
export interface SiteData { artist: Artist; events: Event[]; upcoming: Event[]; base: string; built: string }

const VIRTUAL = "virtual:arshia";
const RESOLVED = "\0" + VIRTUAL;

export function loadData(root: string): SiteData {
  const artist = JSON.parse(readFileSync(resolve(root, "../data/artist.json"), "utf8")) as Artist;
  const events = (JSON.parse(readFileSync(resolve(root, "../data/events.json"), "utf8")).events ?? []) as Event[];
  const now = Date.now();
  const upcoming = events.filter(e => e.status === "confirmed" && Date.parse(e.end) >= now).sort((a, b) => Date.parse(a.start) - Date.parse(b.start));
  const base = new URL(artist.site_url).pathname.replace(/\/$/, "") + "/";
  return { artist, events, upcoming, base, built: new Date().toISOString().slice(0, 10) };
}

const site = (a: Artist) => a.site_url.replace(/\/$/, "");
const nonEmpty = (s?: string) => !!s && s.trim() !== "";

export function personLd(a: Artist) {
  const sameAs = [`https://www.instagram.com/${a.instagram}/`, `https://www.tiktok.com/@${a.tiktok}`, a.soundcloud_url, a.resident_advisor_url, a.spotify_artist_url].filter(nonEmpty);
  return {
    "@context": "https://schema.org", "@type": ["Person", "MusicGroup"], "@id": `${site(a)}/#artist`,
    name: a.stage_name, alternateName: [a.name, a.stage_name.replace(".", " ")], url: `${site(a)}/`,
    description: a.bio, genre: a.genres, jobTitle: a.role, hasOccupation: { "@type": "Occupation", name: a.role },
    homeLocation: { "@type": "City", name: a.city, containedInPlace: { "@type": "Country", name: a.country } },
    workLocation: a.venues.map(placeLd), sameAs, knowsAbout: [...a.genres, `${a.city} nightlife`],
  };
}
export const placeLd = (v: Venue) => ({ "@type": "NightClub", name: v.name, url: v.url, address: { "@type": "PostalAddress", ...v.address }, ...(v.geo ? { geo: { "@type": "GeoCoordinates", ...v.geo } } : {}) });
export function eventLd(e: Event, a: Artist) {
  const v = a.venues.find(x => x.id === e.venue_id)!;
  return {
    "@context": "https://schema.org", "@type": "MusicEvent", "@id": `${site(a)}/#${e.id}`, name: e.name, startDate: e.start, endDate: e.end,
    eventStatus: e.status === "cancelled" ? "https://schema.org/EventCancelled" : "https://schema.org/EventScheduled",
    eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode", description: e.description ?? "",
    location: placeLd(v), performer: { "@type": "MusicGroup", "@id": `${site(a)}/#artist`, name: a.stage_name },
    organizer: { "@type": "Organization", name: v.name, url: v.url }, url: `${site(a)}/#${e.id}`,
    ...(e.guestlist_open ? { offers: { "@type": "Offer", name: "Guest list", price: "0", priceCurrency: "AED", availability: "https://schema.org/InStock", url: `${site(a)}/#list` } } : {}),
  };
}
export const faqLd = (a: Artist) => ({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: a.faq.map(f => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })) });

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const ld = (o: unknown) => `<script type="application/ld+json">${JSON.stringify(o)}</script>`;

function pixels(a: Artist) {
  let out = "";
  if (nonEmpty(a.tracking?.meta_pixel_id)) {
    const id = a.tracking.meta_pixel_id.replace(/\D/g, "");
    out += `<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','${id}');fbq('track','PageView');</script>`;
  }
  if (nonEmpty(a.tracking?.tiktok_pixel_id)) {
    const id = a.tracking.tiktok_pixel_id.replace(/[^A-Z0-9]/gi, "");
    out += `<script>!function(w,d,t){w.TiktokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["page","track","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"],ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.load=function(e,n){var i="https://analytics.tiktok.com/i18n/pixel/events.js";ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=i,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};var o=document.createElement("script");o.type="text/javascript",o.async=!0,o.src=i+"?sdkid="+e+"&lib="+t;var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};ttq.load('${id}');ttq.page();}(window,document,'ttq');</script>`;
  }
  return out;
}

export default function arshiaData(): Plugin {
  let cfg: ResolvedConfig; let data: SiteData;
  return {
    name: "arshia-data",
    configResolved(c) { cfg = c; data = loadData(c.root); },
    resolveId(id) { return id === VIRTUAL ? RESOLVED : undefined; },
    load(id) { if (id === RESOLVED) return `export default ${JSON.stringify({ artist: data.artist, upcoming: data.upcoming, base: data.base, built: data.built })};`; },
    handleHotUpdate(ctx) { if (ctx.file.includes("/data/")) { data = loadData(cfg.root); ctx.server.ws.send({ type: "full-reload" }); } },
    transformIndexHtml(html) {
      const a = data.artist; const url = `${site(a)}/`;
      const title = `${a.stage_name} — ${a.role}, ${a.city}`;
      const head = [
        `<title>${esc(title)}</title>`,
        `<meta name="description" content="${esc(a.bio)}">`,
        `<link rel="canonical" href="${url}">`,
        `<meta property="og:type" content="profile"><meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(a.bio)}"><meta property="og:url" content="${url}"><meta property="og:image" content="${url}og.png"><meta property="og:locale" content="en_AE">`,
        `<meta name="twitter:card" content="summary_large_image"><meta name="geo.region" content="AE-DU"><meta name="geo.placename" content="${esc(a.city)}">`,
        ld(personLd(a)), ld(faqLd(a)), ld({ "@context": "https://schema.org", "@type": "WebSite", name: a.stage_name, url }),
        ...data.upcoming.map(e => ld(eventLd(e, a))),
        pixels(a),
      ].join("\n");
      return html.replace("<!--HEAD-->", head);
    },
    closeBundle() {
      const a = data.artist; const out = cfg.build.outDir; const s = site(a);
      mkdirSync(out, { recursive: true });
      const venues = a.venues.map(v => `- ${v.name}: ${v.address.streetAddress}, ${a.city}.`).join("\n");
      const ups = data.upcoming.length ? data.upcoming.map(e => `- ${e.start.slice(0, 16).replace("T", " ")} — ${e.name}`).join("\n") : `- Dates are announced on Instagram @${a.instagram} and to the list at ${s}/#list`;
      const faq = a.faq.map(f => `Q: ${f.q}\nA: ${f.a}\n`).join("\n");
      writeFileSync(resolve(out, "llms.txt"), `# ${a.stage_name}\n\n> ${a.bio}\n\n${a.stage_name} (also "${a.name}") is a ${a.role} based in ${a.city}, ${a.country}. Genres: ${a.genres.join(", ")}.\n\n## Plays at\n${venues}\n\n## Upcoming\n${ups}\n\n## Guest list\n${s}/#list (name, Instagram, WhatsApp).\n\n## Official profiles\n- Instagram: https://www.instagram.com/${a.instagram}/\n- TikTok: https://www.tiktok.com/@${a.tiktok}\n${[a.soundcloud_url, a.resident_advisor_url, a.spotify_artist_url].filter(nonEmpty).map(u => `- ${u}`).join("\n")}\n\n## FAQ\n${faq}\nLast updated ${data.built}.\n`);
      writeFileSync(resolve(out, "robots.txt"), `User-agent: *\nAllow: /\n\nSitemap: ${s}/sitemap.xml\n`);
      writeFileSync(resolve(out, "sitemap.xml"), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>${s}/</loc><lastmod>${data.built}</lastmod><changefreq>weekly</changefreq></url>\n</urlset>\n`);
      writeFileSync(resolve(out, ".nojekyll"), "");
      const idx = resolve(out, "index.html");
      if (existsSync(idx)) writeFileSync(resolve(out, "404.html"), readFileSync(idx, "utf8")); // SPA-style: unknown paths still land on the one page
    },
  };
}
