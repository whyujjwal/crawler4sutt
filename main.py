import asyncio
import logging
from scraper import scrape_site  # Changed back to relative import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        await scrape_site(
            'https://en.wikipedia.org/wiki/Python_(programming_language)',
            config={
                'max_depth': 10,
                'output_file': 'wikipedia_ex.json',
                'excluded_tags': ['nav', 'footer', 'header', 'script', 'style'],
                'clean_selectors': ['.mw-editsection', '.reference', '.toc'],
                'timeout': 30,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
        )
        logger.info("Scraping completed successfully")
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
