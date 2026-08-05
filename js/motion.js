/* AK — motion, navigation, and preview behavior.
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
  // Everything outside the dialog is made inert while it is open, so keyboard
  // and screen-reader users cannot reach the page behind the overlay.
  const background = [
    document.querySelector(".site-nav"),
    document.getElementById("main"),
    document.querySelector(".site-footer"),
  ].filter(Boolean);

  const FOCUSABLE =
    'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';

  const setBackgroundInert = (inert) => {
    background.forEach((el) => {
      if ("inert" in HTMLElement.prototype) el.inert = inert;
      if (inert) el.setAttribute("aria-hidden", "true");
      else el.removeAttribute("aria-hidden");
    });
    // The toggle lives inside the (now inert) header, so keep it usable.
    if ("inert" in HTMLElement.prototype) toggle.inert = false;
    if (inert) toggle.removeAttribute("aria-hidden");
  };

  const setOpen = (open) => {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    overlay.hidden = !open;
    document.body.classList.toggle("menu-open", open);
    setBackgroundInert(open);
    if (open) {
      const first = overlay.querySelector(FOCUSABLE);
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
    if (overlay.hidden) return;

    if (e.key === "Escape") {
      setOpen(false);
      toggle.focus();
      return;
    }

    // Cycle focus between the overlay's links and the close button.
    if (e.key === "Tab") {
      const stops = [...overlay.querySelectorAll(FOCUSABLE), toggle];
      if (!stops.length) return;
      const first = stops[0];
      const last = stops[stops.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  // Reset state if the viewport grows past the mobile breakpoint.
  const desktop = window.matchMedia("(min-width: 861px)");
  const onBreakpoint = (e) => {
    if (e.matches && !overlay.hidden) setOpen(false);
  };
  if (desktop.addEventListener) desktop.addEventListener("change", onBreakpoint);
  else if (desktop.addListener) desktop.addListener(onBreakpoint); // Safari < 14
}

/* --- Case-study live previews --------------------------------------------
   Previews load on request rather than automatically: no third-party
   requests, cookies, or extra tab stops until the visitor asks for them,
   and a site that refuses to be framed degrades to its "open in a new tab"
   link instead of an empty rectangle. */

document.querySelectorAll("[data-preview-launch]").forEach((button) => {
  button.addEventListener("click", () => {
    const stage = button.closest(".site-preview-stage");
    if (!stage) return;
    const frame = stage.querySelector("iframe[data-preview-src]");
    const facade = stage.querySelector(".preview-facade");
    if (!frame) return;

    frame.src = frame.dataset.previewSrc;
    frame.hidden = false;
    if (facade) facade.hidden = true;
    stage.classList.add("is-loaded");

    // The fallback line sits beside .site-preview, not inside it.
    const scope = stage.closest(".case-preview-section") || document;
    const fallback = scope.querySelector(".preview-fallback");
    if (fallback) fallback.hidden = false;

    frame.focus({ preventScroll: true });
  });
});
