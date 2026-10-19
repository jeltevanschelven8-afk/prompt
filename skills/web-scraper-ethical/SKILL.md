---
name: web-scraper-ethical
description: >-
  Collect data from public web pages responsibly and turn it into clean structured output (CSV or
  JSON). Checks for an official API or data export first, reads robots.txt and the site terms,
  throttles requests, caches pages, and identifies itself honestly. Use this skill whenever the
  user wants to scrape a website, extract a table or list from pages, monitor prices or listings,
  build a crawler, or says "haal deze gegevens van de site", "scrape deze pagina" or "data van een
  website verzamelen", even if they only paste a URL and ask for the data in a spreadsheet.
license: "MIT"
metadata:
  author: "prompt"
  category: "automation"
  tags: "scraping, crawler, robots.txt, rate limit, data, csv, webdata, verzamelen"
  version: "1.0.0"
  summary_nl: "Verzamel gegevens van openbare webpagina's op een nette manier: eerst API, robots.txt respecteren, rustig tempo, nette CSV."
---

# Ethical web scraper

Scraping works best when it is boring for the site owner: few requests, clearly identified, nothing
they asked you not to take. That also makes the scraper more reliable, because polite scrapers get
blocked less and break less. This skill builds that kind of scraper.

## Workflow

1. **Clarify the target.** Which pages, which fields, how many records, one-off or recurring? Write
   down the output columns before writing code; it keeps the scraper small.
2. **Look for a better source first.** Check for a public API, an RSS feed, a sitemap, a "download
   CSV" link, or an open-data portal. Many sites load their data from a JSON endpoint you can see in
   the browser's Network tab. These are faster, more stable and usually what the owner prefers.
3. **Check permission signals.**
   - Fetch `https://example.com/robots.txt` and check the paths you need against the `Disallow`
     rules for `*` and any named agent. Respect `Crawl-delay` if present.
   - Skim the terms of use for clauses on automated access or reuse of the data.
   - Pages behind a login, paywall or CAPTCHA are off limits for this skill; tell the user why.
4. **Prototype on one page.** Fetch a single page, save it to disk, and write the parser against the
   saved copy. That way you iterate on selectors without hitting the site again.
5. **Scale up politely.** Add throttling, caching and a clear User-Agent, then run on a small batch
   (10 pages), inspect the output, and only then do the full run.
6. **Deliver structured output** and a short report of what was collected and what was skipped.

## Reference implementation (Python)

```python
import csv, time, pathlib, hashlib
from urllib import robotparser
import requests
from bs4 import BeautifulSoup

BASE = "https://example.com"
UA = "PromptResearchBot/1.0 (contact: you@example.com)"
CACHE = pathlib.Path(".cache"); CACHE.mkdir(exist_ok=True)

rp = robotparser.RobotFileParser(BASE + "/robots.txt"); rp.read()
delay = rp.crawl_delay(UA) or 2.0
session = requests.Session(); session.headers["User-Agent"] = UA

def get(url):
    if not rp.can_fetch(UA, url):
        print("skip (robots.txt):", url); return None
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if f.exists():
        return f.read_text(encoding="utf-8")
    r = session.get(url, timeout=20)
    if r.status_code == 429:
        time.sleep(60); r = session.get(url, timeout=20)
    r.raise_for_status()
    f.write_text(r.text, encoding="utf-8")
    time.sleep(delay)
    return r.text

rows = []
for page in range(1, 4):
    html = get(f"{BASE}/products?page={page}")
    if not html: continue
    for card in BeautifulSoup(html, "html.parser").select(".product"):
        rows.append({
            "name": card.select_one(".title").get_text(strip=True),
            "price": card.select_one(".price").get_text(strip=True),
            "url": BASE + card.select_one("a")["href"],
        })

with open("products.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["name", "price", "url"]); w.writeheader(); w.writerows(rows)
```

Why each piece is there: the cache means reruns cost the site nothing; the delay keeps load low; the
named User-Agent lets the owner contact you instead of blocking you; the 429 handling backs off when
the site says it is busy. For pages rendered by JavaScript, first look for the JSON request behind
them; use Playwright only if there is none.

## What the user receives

```markdown
**Source:** example.com/products (pages 1-3), no public API found
**robots.txt:** /products allowed, crawl-delay 2s respected
**Collected:** 72 rows -> products.csv (name, price, url)
**Skipped:** 3 cards without a price; 0 pages blocked by robots.txt
**Rerun:** python scrape.py (uses .cache/, delete it to refetch)
**Notes:** prices are text as shown ("EUR 12,95"); say if you want them as numbers
```

Show the first five rows inline so the user can check the fields are right.

## Pitfalls and when to stop

- robots.txt disallows the path, or the terms forbid automated collection: stop and tell the user,
  and suggest asking the site owner or using an official source.
- Personal data (names, emails, profiles of private people): ask what it is for; collecting and
  storing it may fall under privacy law such as the GDPR/AVG.
- Rate limiting, CAPTCHAs or blocks are a signal to slow down or stop, not something to work around.
- Selectors break when the site changes; validate that each required field is present and report
  missing ones instead of writing empty cells silently.
- Never fill gaps with guessed values. If a field could not be read, leave it empty and count it.

## Scope

For public pages and modest volumes. Not for bypassing logins, paywalls or bot protection, mass
crawling of whole domains, or reproducing copyrighted content in bulk.
