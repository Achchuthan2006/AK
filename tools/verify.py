"""Pre-release checks for the static site.

    python tools/verify.py

Exits non-zero and prints every problem it finds. Checks:
  * internal links and asset paths resolve on disk
  * no duplicate element IDs within a page
  * required metadata (title, description, canonical, viewport, lang, OG tags)
  * canonical URL matches the page's own path
  * no stale hostnames (old GitHub Pages URL, localhost, 127.0.0.1)
  * every iframe has a title and a non-embedded fallback link
  * sitemap.xml covers exactly the public pages
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ak-hazel.vercel.app"
STALE = ("achchuthan2006.github.io", "localhost", "127.0.0.1")
NOINDEX = {"404.html"}

problems: list[str] = []


def fail(page: Path, message: str) -> None:
    problems.append(f"{page.relative_to(ROOT).as_posix()}: {message}")


pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
if not pages:
    sys.exit("no HTML pages found")

REF = re.compile(r'(?:href|src)="([^"]+)"')
ID = re.compile(r'\sid="([^"]+)"')
IFRAME = re.compile(r"<iframe\b[^>]*>", re.IGNORECASE)

for page in pages:
    html = page.read_text(encoding="utf-8")
    rel = page.relative_to(ROOT).as_posix()
    indexable = rel not in NOINDEX

    # --- links and assets ---
    for ref in REF.findall(html):
        if ref.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
            continue
        path = unquote(urlparse(ref).path)
        if not path:
            continue
        target = (ROOT / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
        target = target.resolve()
        if target.is_dir() or path.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            fail(page, f'broken reference "{ref}"')

    # --- duplicate IDs ---
    ids = ID.findall(html)
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        fail(page, f'duplicate id "{dup}"')

    # --- stale hostnames ---
    for host in STALE:
        if host in html:
            fail(page, f'stale hostname "{host}"')

    # --- iframes ---
    for tag in IFRAME.findall(html):
        if "title=" not in tag:
            fail(page, "iframe without a title attribute")
        if "data-preview-src" in tag and "sandbox=" not in tag:
            fail(page, "preview iframe without sandbox")
    if "<iframe" in html and "preview-fallback" not in html:
        fail(page, "iframe present but no non-embedded fallback link")

    # --- metadata ---
    if '<html lang="en">' not in html:
        fail(page, "missing lang on <html>")
    if 'name="viewport"' not in html:
        fail(page, "missing viewport")
    if "<title>" not in html:
        fail(page, "missing <title>")

    if indexable:
        for needle, label in (
            ('name="description"', "meta description"),
            ('rel="canonical"', "canonical"),
            ('property="og:title"', "og:title"),
            ('property="og:description"', "og:description"),
            ('property="og:url"', "og:url"),
            ('property="og:image"', "og:image"),
        ):
            if needle not in html:
                fail(page, f"missing {label}")

        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', html)
        if canonical:
            want = SITE + "/" + ("" if rel == "index.html" else rel[: -len("index.html")])
            if canonical.group(1) != want:
                fail(page, f"canonical is {canonical.group(1)}, expected {want}")

# --- sitemap coverage ---
sitemap = ROOT / "sitemap.xml"
if not sitemap.exists():
    problems.append("sitemap.xml: missing")
else:
    listed = set(re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8")))
    expected = {
        SITE + "/" + ("" if p.relative_to(ROOT).as_posix() == "index.html"
                      else p.relative_to(ROOT).as_posix()[: -len("index.html")])
        for p in pages
        if p.relative_to(ROOT).as_posix() not in NOINDEX
    }
    for missing in sorted(expected - listed):
        problems.append(f"sitemap.xml: missing {missing}")
    for extra in sorted(listed - expected):
        problems.append(f"sitemap.xml: lists nonexistent {extra}")

print(f"checked {len(pages)} pages")
if problems:
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("all checks passed")
