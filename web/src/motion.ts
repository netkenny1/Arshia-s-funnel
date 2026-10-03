/**
 * Restrained motion: smooth scroll (Lenis), a word-by-word hero reveal, and a soft reveal on scroll
 * for everything else. Nothing decorative. Fully off under prefers-reduced-motion.
 */
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function motion() {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) { document.documentElement.classList.add("no-motion"); return; }
  gsap.registerPlugin(ScrollTrigger);

  const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add(t => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
  document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach(a => a.addEventListener("click", e => {
    const t = document.querySelector(a.getAttribute("href")!); if (!t) return; e.preventDefault(); lenis.scrollTo(t as HTMLElement, { offset: -8 });
  }));

  // hero: split into words, stagger up
  const h = document.querySelector<HTMLElement>("[data-split]");
  if (h) {
    const words = h.textContent!.trim().split(/\s+/);
    h.innerHTML = words.map(w => `<span class="w">${w}</span>`).join(" ");
    gsap.fromTo(h.querySelectorAll(".w"), { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 1.1, ease: "expo.out", stagger: 0.08, delay: 0.15 });
  }
  gsap.fromTo("[data-word]", { opacity: 0 }, { opacity: 1, duration: 0.8, delay: 0.3 });

  // everything else: reveal once as it enters
  gsap.utils.toArray<HTMLElement>("[data-reveal]").forEach(n => {
    gsap.fromTo(n, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.9, ease: "power3.out", scrollTrigger: { trigger: n, start: "top 88%", once: true } });
  });
  // list rows: stagger in per section
  gsap.utils.toArray<HTMLElement>(".venues, .events").forEach(ul => {
    gsap.fromTo(ul.children, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out", stagger: 0.08, scrollTrigger: { trigger: ul, start: "top 85%", once: true } });
  });
  // hero line drifts up slightly as you leave it
  gsap.to(".hero", { yPercent: -8, ease: "none", scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true } });
}
