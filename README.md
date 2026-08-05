# AK — Portfolio & Studio Site

Personal portfolio and freelance studio site for **Achchuthan Kumaranantha** — full-stack product engineer, GTA.

## Architecture

Zero-build static HTML/CSS/JS. No toolchain, no framework, no install step.

```
index.html            Home
work/                 Work index + case studies (one folder per project)
services/             Freelance services
about/                Story, skills, experience, education
contact/              Inquiry composer (mailto-based, no backend)
resume/               Print-friendly resume (print -> save as PDF)
styles/tokens.css     Design tokens (color, type, spacing, motion)
styles/global.css     Component system
js/motion.js          Reveals, nav behavior, mobile menu, preview loading
tools/verify.py       Pre-release checks (run before every deploy)
tools/make-og-image.py Regenerates assets/og-image.png
vercel.json           Security headers + cache policy
404.html, robots.txt, sitemap.xml
```

Internal links are **relative**, so the site works from any base path and from `file://`. Absolute URLs appear only in canonicals, Open Graph tags, JSON-LD, `sitemap.xml`, and `404.html`.

## Local development

```bash
python -m http.server 8123
```

Then open http://localhost:8123.

## Verify before deploying

```bash
python tools/verify.py
```

Checks internal links, duplicate IDs, required metadata, canonical correctness, stale hostnames, iframe titles and sandboxing, and sitemap coverage. Exits non-zero on any problem.

## Deployment

Production is **Vercel** at **https://ak-hazel.vercel.app**, deploying from `main`.

Release procedure:

```bash
git switch main
git pull origin main
git merge --no-ff feat/portfolio-premium-rebuild
git push origin main
```

Vercel redeploys automatically on push.

### Cache versioning — important

`styles/*.css` and `js/motion.js` are referenced with a version query (`?v=N`) because the filenames are not content-hashed and `vercel.json` sets a cache lifetime on them. **When you edit a CSS or JS file, bump that number in every HTML page**, or returning visitors will run the old asset:

```bash
grep -rl 'motion.js?v=' . --include='*.html' | xargs sed -i 's/motion\.js?v=3/motion.js?v=4/g'
```

### External dependency: case-study previews

Case studies embed a live preview of each project, loaded only when the visitor clicks **Launch interactive preview**. A site that refuses to be framed degrades to a visible "open in a new tab" link rather than an empty rectangle — but two projects currently refuse to be framed by production:

| Project | Current `frame-ancestors` | Needs |
|---|---|---|
| PrintMe (`printme-design-website.vercel.app`) | `'self' https://achchuthan2006.github.io http://127.0.0.1:* http://localhost:*` | add `https://ak-hazel.vercel.app` |
| Arun Bakery (`arun-bakery-smoky.vercel.app`) | same as above | add `https://ak-hazel.vercel.app` |

Fix in each of those projects' own CSP header (their `vercel.json` or middleware), not here. Never widen it to `frame-ancestors *`. If a custom domain is added later, allow that origin too.

## Editing

- Colors, fonts, spacing: edit `styles/tokens.css` — every component derives from it.
- New case study: copy any `work/<slug>/index.html`, update content + metadata, then add it to `work/index.html`, the homepage grid, and `sitemap.xml`. `tools/verify.py` will catch anything missed.
- Social image: edit and re-run `python tools/make-og-image.py` (requires Pillow).
- The contact form has **no backend** by design: it composes a message in the visitor's own mail app and states so on the page. To move to a hosted form service, replace the submit handler in `contact/index.html`.

## Known follow-ups

- LinkedIn URL is not published anywhere yet (hero, footer, contact, and JSON-LD `sameAs` all await it).
- Project screenshots are not stored locally; case studies rely on live previews plus links.
- Contact form is mailto-only; a real backend + spam protection is a future upgrade.
- If a custom domain replaces `ak-hazel.vercel.app`, find-and-replace it across the repo and re-run `tools/verify.py`.
