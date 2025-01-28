from .scraper import scrape_site, ContentScraper
import aiohttp
import asyncio

async def scrape_site(base_url, config=None):
    config = config or {}
    
    crawler = SiteCrawler(base_url, config)
    await crawler.crawl()
    
    scraper = ContentScraper(config)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in crawler.discovered_links:
            tasks.append(scraper.process_url(session, url))
        
        results = await asyncio.gather(*tasks)
        scraper.results = [r for r in results if r is not None]
    
    await scraper.save_results()
    return scraper.results