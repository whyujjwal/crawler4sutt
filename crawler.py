import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, config=None):
        self.config = config or {}
        self.visited_urls = set()
        self.urls_to_visit = set()
        self.results = []
        self.domain = None

    def is_valid_url(self, url):
        """Check if URL belongs to same domain and is not already processed"""
        if not url:
            return False
        parsed = urlparse(url)
        return (
            parsed.netloc == self.domain and
            not url.endswith(('.pdf', '.jpg', '.png', '.gif')) and
            url not in self.visited_urls
        )

    def normalize_url(self, base_url, url):
        """Convert relative URLs to absolute"""
        return urljoin(base_url, url).split('#')[0]

    async def crawl(self, start_url):
        self.domain = urlparse(start_url).netloc
        self.urls_to_visit.add(start_url)
        
        async with aiohttp.ClientSession() as session:
            while self.urls_to_visit and len(self.visited_urls) < self.config.get('max_pages', 100):
                batch = list(self.urls_to_visit)[:10]
                self.urls_to_visit.difference_update(batch)
                
                tasks = [self.process_url(session, url) for url in batch]
                await asyncio.gather(*tasks)
                
        return self.results

    async def process_url(self, session, url):
        if url in self.visited_urls:
            return

        try:
            async with session.get(url, headers=self.config.get('headers', {})) as response:
                if response.status != 200:
                    return

                html = await response.text()
                self.visited_urls.add(url)
                
                soup = BeautifulSoup(html, 'html.parser')
                content = self.extract_content(soup)
                self.results.append({
                    'url': url,
                    'title': soup.title.string if soup.title else '',
                    'content': content
                })
                
                links = self.extract_links(soup, url)
                self.urls_to_visit.update(
                    link for link in links 
                    if self.is_valid_url(link)
                )
                
                logger.info(f"Processed {url}, found {len(links)} links")
                
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")

    def extract_content(self, soup):
        # Remove unwanted elements
        for tag in self.config.get('excluded_tags', []):
            for element in soup.find_all(tag):
                element.decompose()

        return soup.get_text(separator=' ', strip=True)

    def extract_links(self, soup, base_url):
        links = set()
        for a in soup.find_all('a', href=True):
            url = self.normalize_url(base_url, a['href'])
            links.add(url)
        return links