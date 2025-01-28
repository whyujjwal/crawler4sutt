import asyncio
import logging
from crawler import WebCrawler
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    config = {
        'max_pages': 50,  # Maximum pages to crawl
        'output_file': 'augsd_full.json',
        'excluded_tags': ['nav', 'footer', 'header', 'script', 'style'],
        'headers': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
    }

    try:
        crawler = WebCrawler(config)
        results = await crawler.crawl('https://www.youtube.com/') # link
        
        with open(config['output_file'], 'w', encoding='utf-8') as f:
            json.dump({
                'pages': results,
                'stats': {
                    'total_pages': len(results),
                    'urls_visited': len(crawler.visited_urls)
                }
            }, f, indent=2)
            
        logger.info(f"Crawling completed. Processed {len(results)} pages")
        
    except Exception as e:
        logger.error(f"Crawling failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
