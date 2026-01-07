import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
import random


class WorkingKhmerScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.khmer_pattern = re.compile(r"[\u1780-\u17FF\s]+")

    def scrape_khmer_news(self, url, max_articles=50):
        """Scrape Khmer news from a single website"""
        articles = []
        page = 1

        print(f"Starting to scrape: {url}")

        while len(articles) < max_articles:
            try:
                # For pagination
                if page > 1:
                    if "rasmeinews" in url:
                        current_url = f"{url}page/{page}/"
                    else:
                        current_url = f"{url}?page={page}"
                else:
                    current_url = url

                print(f"Page {page}: {current_url}")

                response = self.session.get(current_url, timeout=15)
                response.encoding = "utf-8"

                if response.status_code != 200:
                    print(f"  Failed to load page {page}")
                    break

                soup = BeautifulSoup(response.content, "html.parser")

                # Different strategies to find articles
                article_links = self.find_article_links(soup, url)

                if not article_links:
                    print(f"  No article links found on page {page}")
                    # Try alternative method
                    article_links = self.find_links_by_pattern(soup, url)

                print(f"  Found {len(article_links)} potential articles")

                # Scrape each article
                for i, article_url in enumerate(
                    article_links[:10]
                ):  # Limit to 10 per page
                    if len(articles) >= max_articles:
                        break

                    print(
                        f"    Processing article {i+1}/{len(article_links[:10])}: {article_url}"
                    )
                    article_data = self.scrape_article_content(article_url)

                    if article_data and len(article_data.get("content", "")) > 200:
                        articles.append(article_data)
                        print(f"      ✓ Added article {len(articles)}")

                    # Random delay to avoid being blocked
                    time.sleep(random.uniform(1, 3))

                # Check if we should continue to next page
                if not article_links or len(articles) >= max_articles:
                    break

                page += 1
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Error on page {page}: {str(e)}")
                break

        return articles

    def find_article_links(self, soup, base_url):
        """Find article links using multiple strategies"""
        links = set()

        # Strategy 1: Look for common article link patterns
        patterns = [
            'a[href*="/article/"]',
            'a[href*="/news/"]',
            'a[href*="/post/"]',
            'a[href*="/blog/"]',
            'a[href*="/story/"]',
            'a[href*="/202"]',  # Links containing year (for news)
            "article a",  # Links inside article tags
            ".post a",
            ".news-item a",
            ".entry-title a",
            ".title a",
            "h2 a",
            "h3 a",
        ]

        for pattern in patterns:
            elements = soup.select(pattern)
            for elem in elements:
                href = elem.get("href", "")
                if href:
                    full_url = urljoin(base_url, href)
                    if self.is_valid_article_url(full_url):
                        links.add(full_url)

        # Strategy 2: Look for links with Khmer text
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            text = link.get_text(strip=True)
            # Check if link text contains Khmer characters
            if any("\u1780" <= char <= "\u17ff" for char in text):
                href = link.get("href")
                full_url = urljoin(base_url, href)
                if self.is_valid_article_url(full_url):
                    links.add(full_url)

        return list(links)

    def find_links_by_pattern(self, soup, base_url):
        """Alternative method to find links"""
        links = set()

        # Look for links with common news URL patterns
        for link in soup.find_all("a", href=True):
            href = link["href"]

            # Check for common news URL patterns
            url_patterns = [
                "/article/",
                "/news/",
                "/post/",
                "/blog/",
                "/story/",
                "/archives/",
                "/entry/",
                "/content/",
                "/detail/",
            ]

            if any(pattern in href.lower() for pattern in url_patterns):
                full_url = urljoin(base_url, href)
                if self.is_valid_article_url(full_url):
                    links.add(full_url)

            # Also check for numeric IDs (common in CMS)
            if re.search(r"/\d+/", href):
                full_url = urljoin(base_url, href)
                if self.is_valid_article_url(full_url):
                    links.add(full_url)

        return list(links)

    def is_valid_article_url(self, url):
        """Check if URL looks like an article URL"""
        # Exclude common non-article pages
        exclude_patterns = [
            "/category/",
            "/tag/",
            "/author/",
            "/page/",
            "/feed/",
            "/search/",
            "/wp-admin/",
            "/login",
            "/register",
            "/comment",
            "/#",
            "?replytocom",
            ".jpg",
            ".png",
            ".gif",
            ".pdf",
            ".zip",
        ]

        # Check if URL should be excluded
        if any(pattern in url.lower() for pattern in exclude_patterns):
            return False

        # URL should have some path segments
        if url.count("/") < 3:
            return False

        return True

    def scrape_article_content(self, url):
        """Scrape content from a single article"""
        try:
            print(f"      Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.encoding = "utf-8"

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = self.extract_title(soup)

            # Extract content
            content = self.extract_content(soup)

            # Clean and filter Khmer text
            if content:
                khmer_content = self.extract_khmer_text(content)

                if len(khmer_content) > 200:  # Minimum length
                    return {
                        "url": url,
                        "title": title,
                        "content": khmer_content,
                        "length": len(khmer_content),
                        "source": url,
                    }

            return None

        except Exception as e:
            print(f"      Error scraping article: {str(e)}")
            return None

    def extract_title(self, soup):
        """Extract article title"""
        # Try different selectors for title
        title_selectors = [
            "h1.entry-title",
            "h1.title",
            "h1.post-title",
            "h1.article-title",
            "h1.headline",
            "h1",
            ".post h1",
            ".article h1",
            "header h1",
            "title",
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 10:
                    return title

        # Fallback: use page title
        if soup.title:
            return soup.title.get_text(strip=True)

        return ""

    def extract_content(self, soup):
        """Extract article content"""
        # Remove unwanted elements
        for element in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "button",
                "iframe",
                ".ads",
                ".advertisement",
                ".sidebar",
                ".comments",
                ".share-buttons",
            ]
        ):
            element.decompose()

        # Try different content selectors
        content_selectors = [
            "article .entry-content",
            "article .post-content",
            "div.entry-content",
            "div.post-content",
            "div.article-content",
            "div.content",
            "div.story-content",
            "article",
            "main",
            "div.main-content",
            ".post",
            ".article-body",
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator=" ", strip=True)
                if len(text) > 300:  # Minimum content length
                    return text

        # If no specific content area found, get all text
        body = soup.find("body")
        if body:
            return body.get_text(separator=" ", strip=True)

        return ""

    def extract_khmer_text(self, text):
        """Extract and clean Khmer text"""
        # Extract Khmer characters and spaces
        khmer_text = "".join(self.khmer_pattern.findall(text))

        # Clean up
        khmer_text = re.sub(r"\s+", " ", khmer_text)  # Remove extra spaces
        khmer_text = khmer_text.strip()

        return khmer_text

    def save_articles(self, articles, filename):
        """Save articles to JSON file"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        total_chars = sum(article["length"] for article in articles)
        print(f"\n✅ Saved {len(articles)} articles to {filename}")
        print(f"📊 Total characters: {total_chars:,}")

        # Print sample
        if articles:
            print(f"\n📝 Sample article:")
            print(f"Title: {articles[0]['title'][:100]}...")
            print(f"Content preview: {articles[0]['content'][:200]}...")

    def export_text_only(self, articles, filename):
        """Export only the text content for NLP processing"""
        with open(filename, "w", encoding="utf-8") as f:
            for article in articles:
                f.write(article["content"] + "\n\n")
        print(f"Exported text to {filename}")


def main():
    """Main function to run the scraper"""

    # List of Khmer websites to scrape
    khmer_sites = [
        "https://www.khmerload.com/",
        "https://www.sabay.com.kh/",
        "https://www.cambodiadaily.com/kh/",  # Cambodian news in Khmer
    ]

    # Choose a site to start with
    target_site = khmer_sites[0]

    # Initialize scraper
    scraper = WorkingKhmerScraper()

    # Scrape articles
    print(f"🚀 Starting scraper for: {target_site}")
    print("=" * 60)

    articles = scraper.scrape_khmer_news(target_site, max_articles=20)

    if articles:
        # Save results
        scraper.save_articles(articles, "khmer_articles.json")

        # Export for your stop-word project
        scraper.export_text_only(articles, "khmer_corpus.txt")

        print("\n" + "=" * 60)
        print("🎉 Scraping completed successfully!")
        print(f"📚 Collected {len(articles)} articles for your stop-word project")

        # Show statistics
        word_count = sum(len(article["content"].split()) for article in articles)
        print(f"📊 Total words: {word_count:,}")

    else:
        print("\n❌ No articles were collected.")
        print("Possible reasons:")
        print("1. Website structure has changed")
        print("2. Anti-bot protection is active")
        print("3. Network issues")
        print("\nTry a different website or check the URL.")


if __name__ == "__main__":
    main()
