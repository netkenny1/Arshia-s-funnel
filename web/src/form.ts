/**
 * The list. Posts to the Apps Script endpoint when configured; otherwise opens WhatsApp pre-filled
 * so it works before any backend exists. Captures UTM + referrer so the sheet shows which post sent them.
 */
import type { Artist, Event } from "../plugins/arshia-data";

type Data = { artist: Artist; upcoming: Event[]; base: string };

export function form({ artist: a }: Data) {
  const f = document.getElementById("list-form") as HTMLFormElement | null;
  const status = document.getElementById("status")!;
  if (!f) return;
  const p = new URLSearchParams(location.search);
  const attribution = { utm_source: p.get("utm_source") ?? "", utm_medium: p.get("utm_medium") ?? "", utm_campaign: p.get("utm_campaign") ?? "", utm_content: p.get("utm_content") ?? "", referrer: document.referrer, landing: location.pathname };
  try { if (!localStorage.getItem("first_touch")) localStorage.setItem("first_touch", JSON.stringify(attribution)); } catch {}

  const wa = (text: string) => `https://wa.me/${a.whatsapp_e164.replace(/\D/g, "")}?text=${encodeURIComponent(text)}`;

  f.addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(f);
    if (fd.get("_hp")) return;
    const d = {
      name: String(fd.get("name") ?? "").trim(),
      instagram: String(fd.get("instagram") ?? "").trim().replace(/^@/, ""),
      phone: String(fd.get("phone") ?? "").trim(),
      event: "list", party_size: "", consent: true,
      submitted_at: new Date().toISOString(), attribution,
    };
    if (!d.name || !d.instagram || !d.phone) { set("Name, Instagram and WhatsApp.", "err"); return; }
    const msg = `Put me on the list.\nName: ${d.name}\nIG: @${d.instagram}`;
    if (!a.guestlist_endpoint) {
      if (!a.whatsapp_e164) { set("List opens soon. Follow @" + a.instagram + " for now.", "ok"); return; }
      set("Opening WhatsApp…", "ok"); window.open(wa(msg), "_blank"); return;
    }
    set("…");
    try {
      await fetch(a.guestlist_endpoint, { method: "POST", mode: "no-cors", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(d) });
      set("You're on. We'll message you before the next one.", "ok"); f.reset();
      (window as any).fbq?.("track", "Lead"); (window as any).ttq?.track?.("SubmitForm");
    } catch { set("Didn't go through. Try WhatsApp.", "err"); if (a.whatsapp_e164) window.open(wa(msg), "_blank"); }
  });
  function set(t: string, cls = "") { status.textContent = t; status.className = "status " + cls; }
}
