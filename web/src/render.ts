/** Fills the static shell from the data module. No framework: the page is one screen of content. */
import type { Artist, Event } from "../plugins/arshia-data";

type Data = { artist: Artist; upcoming: Event[]; base: string; built: string };
const $ = <T extends Element = HTMLElement>(sel: string) => document.querySelector(sel) as T | null;
const has = (s?: string) => !!s && s.trim() !== "";
const el = (tag: string, attrs: Record<string, string> = {}, html = "") => { const n = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v); n.innerHTML = html; return n; };
const esc = (s: string) => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]!));
const DXB = "Asia/Dubai";

export function mount({ artist: a, upcoming }: Data) {
  $("[data-text=one_liner]")!.textContent = a.one_liner;
  $("[data-text=sub]")!.textContent = `${a.stage_name} — ${a.role}, ${a.city}. ${a.venues.map(v => v.name).join(" · ")}.`;

  const venues = $("[data-venues]")!;
  for (const v of a.venues) venues.append(el("li", {}, `<a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.name)}</a><small>${esc(v.address.streetAddress.split(",").slice(-1)[0].trim())}</small>`));

  if (upcoming.length) {
    show("next");
    const ul = $("[data-events]")!;
    for (const e of upcoming) {
      const v = a.venues.find(x => x.id === e.venue_id);
      const d = new Date(e.start);
      const when = d.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", timeZone: DXB });
      ul.append(el("li", { id: e.id }, `<div><a href="#list">${esc(v?.name ?? e.name)}</a><time datetime="${esc(e.start)}">${when}${e.description ? " · " + esc(e.description) : ""}</time></div><small>${e.guestlist_open ? "list open" : ""}</small>`));
    }
  }

  if (has(a.soundcloud_embed_track_url)) {
    show("listen");
    const src = `https://w.soundcloud.com/player/?url=${encodeURIComponent(a.soundcloud_embed_track_url)}&color=%23ffffff&auto_play=false&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false&visual=false`;
    $("[data-embed]")!.append(el("iframe", { src, title: `${a.stage_name} on SoundCloud`, loading: "lazy", allow: "autoplay" }));
  }

  const ch = $("[data-channels]")!;
  const chans: [string, string][] = [["WhatsApp channel", a.channels?.whatsapp_channel_url], ["Instagram broadcast", a.channels?.instagram_broadcast_url], ["Telegram", a.channels?.telegram_channel_url]];
  const live = chans.filter(([, u]) => has(u));
  if (live.length) { ch.append(el("li", {}, "Or follow the list:")); for (const [n, u] of live) ch.append(el("li", {}, `<a href="${esc(u)}" target="_blank" rel="noopener">${n}</a>`)); }

  const links = $("[data-links]")!;
  const L: [string, string][] = [["Instagram", `https://www.instagram.com/${a.instagram}/`], ["TikTok", `https://www.tiktok.com/@${a.tiktok}`], ["SoundCloud", a.soundcloud_url], ["RA", a.resident_advisor_url], ["Spotify", a.spotify_artist_url]];
  for (const [n, u] of L) if (has(u)) links.append(el("li", {}, `<a href="${esc(u)}" target="_blank" rel="me noopener">${n}</a>`));
  if (has(a.email_bookings)) links.append(el("li", {}, `<a href="mailto:${esc(a.email_bookings)}">Bookings</a>`));
  $("[data-footer]")!.textContent = `${a.stage_name} · ${a.city}`;
}

function show(id: string) { document.querySelectorAll(`[data-if="${id}"]`).forEach(n => ((n as HTMLElement).style.display = n.tagName === "A" ? "inline" : "block")); }
