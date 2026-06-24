# GEO / AI Optimization Checklist — Script Master Labs LLC

Run this checklist every time you ship a new product, page, or MCP endpoint.

---

## 1. llms.txt (AI Agent Directory)
- [ ] Add new product row to the Products table with accurate name, description, endpoint
- [ ] Verify pricing is exact (not "contact us" vague — state the model: per-call, invite-only, free tier)
- [ ] Update payment addresses if changed
- [ ] Deploy to: `https://www.scriptmasterlabs.com/llms.txt`

## 2. Schema Markup (JSON-LD)
- [ ] Add a `SoftwareApplication` or `Product` block in `seo/schema.json` for every new product
- [ ] Embed updated `<script type="application/ld+json">` blocks in `<head>` of relevant pages
- [ ] Test at: https://search.google.com/test/rich-results

## 3. Sitemap
- [ ] Add new URL to `seo/sitemap_template.xml`
- [ ] Upload to: `https://www.scriptmasterlabs.com/sitemap.xml`
- [ ] Re-submit in Google Search Console → Sitemaps

## 4. robots.txt
- [ ] Confirm all AI crawlers remain in the Allow list (no accidental blocks)
- [ ] Verify `Sitemap:` line points to current sitemap URL

## 5. Page-Level GEO (for each new product page)
- [ ] H1 = exact product name (e.g., "MCP-x402 — x402 Protocol MCP Server")
- [ ] First paragraph: declarative fact sentence answering "what is this / what does it cost"
  - BAD: "Revolutionize your agent workflow"
  - GOOD: "MCP-x402 is a 51-tool MCP server. Agents pay per call using the x402 protocol on XRPL or Base. No subscription required."
- [ ] Pricing in a `<table>` (not CSS-styled divs) so AI crawlers read the relationship correctly
- [ ] Use `<h2>` / `<h3>` subheadings — not bold divs — for Features, Pricing, How It Works
- [ ] Add one canonical `<link rel="canonical" href="...">` per page

## 6. MCP / Agent Direct Integration
- [ ] Verify MCP endpoint is live: `curl https://mcp-x402.onrender.com/mcp/health`
- [ ] Confirm tool schemas are Zod-validated (not raw object schemas — Zod required by MCP SDK)
- [ ] Add endpoint to llms.txt MCP Integration section

## 7. GitHub Repos (awesome-lists / backlinks)
- [ ] Open PR to relevant awesome-list when new product ships
  - punkpeye/awesome-mcp-servers (MCP products)
  - xpaysh/awesome-x402 (x402 products)
  - wojake/awesome-xrpl (XRPL products)
- [ ] Ensure README has: description, live endpoint, payment model, SDVOSB badge

## 8. Google Search Console
- [ ] Inspect URL after any page change
- [ ] Request re-indexing if content changed materially
- [ ] Check Coverage report monthly for any crawl errors on AI-critical pages
