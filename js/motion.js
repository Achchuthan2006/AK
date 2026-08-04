/* AK — motion & navigation behavior.
   Everything degrades: without JS the site is fully readable (see
   html:not(.has-js) rules in global.css), and prefers-reduced-motion
   disables transitions at the CSS layer. */

document.documentElement.classList.add("has-js");

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* --- Scroll reveals ----------------------------------------------------- */

const revealTargets = document.querySelectorAll("[data-reveal], .rule-anim");

if (reduceMotion || !("IntersectionObserver" in window)) {
  revealTargets.forEach((el) => el.classList.add("is-in"));
} else {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
  );
  revealTargets.forEach((el) => io.observe(el));
}

/* --- Sticky nav state ---------------------------------------------------- */

const nav = document.querySelector(".site-nav");
if (nav) {
  const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 8);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
}

/* --- Mobile menu ---------------------------------------------------------- */

const toggle = document.querySelector(".nav-toggle");
const overlay = document.getElementById("menu");

if (toggle && overlay) {
  const setOpen = (open) => {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    overlay.hidden = !open;
    document.body.classList.toggle("menu-open", open);
    if (open) {
      const first = overlay.querySelector("a");
      if (first) first.focus();
    }
  };

  toggle.addEventListener("click", () => {
    setOpen(toggle.getAttribute("aria-expanded") !== "true");
  });

  overlay.addEventListener("click", (e) => {
    if (e.target.closest("a")) setOpen(false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !overlay.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });

  // Reset state if the viewport grows past the mobile breakpoint
  window.matchMedia("(min-width: 861px)").addEventListener("change", (e) => {
    if (e.matches) setOpen(false);
  });
}
