import requests
from bs4 import BeautifulSoup
import time
import re
import sys

# Ensure proper UTF-8 output
if sys.stdout.encoding != "utf-8":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)


def is_real_news_article(url):
    """Heuristic: Only accept URLs that look like real news (not about, forum, frequencies, etc.)"""
    bad_keywords = [
        "about",
        "frequencies",
        "listener-forum",
        "people",
        "profiles",
        "contact",
    ]
    for kw in bad_keywords:
        if kw in url:
            return False
    # Must have /khmer/ and end with .html and contain a date-like number (e.g., 12232025)
    if "/khmer/" in url and url.endswith(".html") and re.search(r"\d{6,8}", url):
        return True
    return False


def scrape_rfa_khmer_article_links():
    url = "https://www.rfa.org/khmer"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch homepage: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    # Find all candidate links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = href if href.startswith("http") else "https://www.rfa.org" + href
        if is_real_news_article(full_url):
            title = a.get_text(strip=True)
            if title and len(title) > 15:
                links.append({"title": title, "url": full_url})

    # Remove duplicates
    seen = set()
    unique = []
    for item in links:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique[:15]  # Get up to 15 articles


def scrape_article_content(article_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {article_url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # RFA main content selector
    content = soup.select_one("div.content, div.contentblock")
    if not content:
        content = soup.find("article")

    if content:
        # Remove noise
        for bad in content.select(
            "script, style, .share, .tags, .byline, .date, .related, nav, footer, iframe, img, .audio"
        ):
            bad.decompose()
        paragraphs = [
            p.get_text(strip=True)
            for p in content.find_all("p")
            if p.get_text(strip=True)
        ]
        full_text = "\n".join(paragraphs)
        return full_text if len(full_text) > 200 else ""  # Only keep if substantial

    return ""


# Main execution
if __name__ == "__main__":
    print("📡 Fetching real Khmer news articles from RFA (for stop-word corpus)...\n")
    articles = scrape_rfa_khmer_article_links()

    if not articles:
        print("⚠️ No valid news articles found.")
        sys.exit(1)

    all_text = []
    saved_count = 0

    for i, art in enumerate(articles, 1):
        print(f"{i}. {art['title']}")
        print(f"   🔗 {art['url']}")

        content = scrape_article_content(art["url"])
        if content and len(content) > 300:  # Only use long articles
            all_text.append(content)
            saved_count += 1
            print(f"   ✅ {len(content)} characters extracted.")
        else:
            print("   ❌ Skipped (too short or no content).")

        time.sleep(1.5)  # Be respectful

    # Save full corpus
    if all_text:
        corpus = "\n\n" + ("=" * 80 + "\n\n").join(all_text)
        filename = "khmer_news_corpus.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(corpus)
        print(
            f"\n🎉 Success! Saved {saved_count} articles ({len(corpus):,} characters) to '{filename}'"
        )
    else:
        print("\n⚠️ No valid content collected.")
