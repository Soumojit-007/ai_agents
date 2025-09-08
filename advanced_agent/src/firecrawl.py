import os
import logging
from firecrawl import FirecrawlApp, ScrapeOptions
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.ERROR)

load_dotenv()


class FireCrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY environment variable")
        self.app = FirecrawlApp(api_key=api_key)

    def search(self, query: str, num_results: int = 5):
        """
        General-purpose search with FireCrawl.
        Works for any type of query (company, person, tool, concept).
        Returns markdown-formatted results or [].
        """
        try:
            result = self.app.search(
                query=query,   # ✅ removed "company pricing", now pure query
                limit=num_results,
                scrape_options=ScrapeOptions(formats=["markdown"])
            )

            # Normalize result
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []

        except Exception as e:
            logging.error("Exception during FireCrawl search: %s", e)
            return []

    def scrape(self, url: str):
        """
        Scrape a given page URL using FireCrawl.
        Returns markdown content or [] if failed.
        """
        try:
            result = self.app.scrape_url(url, formats=["markdown"])

            # Normalize result
            if isinstance(result, dict) and "data" in result:
                return result["data"]
            elif isinstance(result, list):
                return result
            else:
                return []

        except Exception as e:
            logging.error("Exception during FireCrawl scrape: %s", e)
            return []
