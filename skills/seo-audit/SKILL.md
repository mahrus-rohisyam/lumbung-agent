---
name: seo-audit
description: Perform SEO strategy and technical/on-page SEO checking for websites, web apps, and content. Use when auditing a site or page for search visibility, reviewing HTML/metadata/structured data, planning keywords and internal links, or checking SEO regressions before launch.
---

# SEO & SEO checking

Optimize pages for search intent and crawlability, and verify implementation directly against rendered HTML, headers, and codebase files.

## 1. Technical SEO checks

Inspect live URLs (when accessible) or built/source templates for:

- **Crawlability & indexing:**
  - `robots.txt` allows important routes and points to `Sitemap:`.
  - XML `sitemap.xml` is valid, returns `200`, and lists canonical indexable URLs only.
  - No unintended `noindex`, `X-Robots-Tag: noindex`, or `Disallow: /` on production pages.
- **Status codes & redirects:**
  - Key pages return `200` directly (avoid redirect chains `301 -> 301 -> 200` and soft 404s).
  - Trailing slash and `http` → `https` / `www` canonicalization are consistent.
- **Canonicalization:**
  - Every indexable page has a self-referencing `<link rel="canonical" href="...">` with an absolute URL.
  - Paginated, filtered, or UTM-tagged URLs do not create duplicate indexable pages.
- **Performance & mobile:**
  - Responsive viewport `<meta name="viewport" content="width=device-width, initial-scale=1">`.
  - Images have explicit `width`/`height` (prevent CLS), modern formats, and lazy-loading below the fold (not on the LCP hero image).
  - Minimal render-blocking scripts/CSS.

Quick CLI checks (when checking a live URL or local dev server):

```sh
curl -sI https://example.com/ | grep -iE "^(http/|location:|x-robots-tag:|cache-control:)"
curl -s https://example.com/robots.txt
curl -s https://example.com/ | grep -iE "<title|<meta[^>]+(description|robots)|rel=\"canonical\"|<h1|application/ld\+json"
```

## 2. On-page & content SEO checks

- **Search intent & keyword focus:** One primary topic/intent per page; avoid multiple pages competing for the same query (cannibalization).
- **Title tag (`<title>`):** ~50–60 characters, primary keyword near the front, unique per page, compelling CTR.
- **Meta description:** ~140–160 characters, summarizes value and encourages clicks, unique per page.
- **Headings (`H1`–`H3`):** Exactly one clear `H1` matching page intent; logical `H2`/`H3` hierarchy without skipping levels for styling.
- **URL slug:** Short, lowercase, hyphenated, descriptive, no unnecessary parameters or dates unless news.
- **Media:** Descriptive `alt` text on meaningful images; descriptive filenames.
- **Internal linking:** Key pages linked from navigation or related content with descriptive anchor text (avoid "click here").

## 3. Structured data & social metadata

- **JSON-LD Schema:** Valid `application/ld+json` matching visible page content (`Organization`, `WebSite`, `Article`, `Product`, `FAQPage`, `BreadcrumbList` as appropriate).
- **Open Graph & Twitter/X cards:** `og:title`, `og:description`, `og:image` (absolute URL, `1200x630`), `og:url`, `og:type`, `twitter:card`.

## 4. Audit output format

Group findings by severity so the team can fix high-impact issues first:

1. **Critical (indexing/ranking blockers):** e.g., accidental `noindex`, broken canonicals, `5xx`/`404` on key pages.
2. **High (on-page & structure):** missing/duplicate titles, missing `H1`, redirect chains, missing sitemap/schema.
3. **Medium / Opportunities:** thin content, weak internal linking, missing OG tags, image optimization.
4. **Verified passing:** list what was checked and passed.

Include `file:line` or `URL`, the exact issue observed, and the concrete fix for every finding.
