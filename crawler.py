import asyncio
import aiohttp
from urllib.parse import urlparse
from .utils import normalize_url, is_valid_url
from .config import DEFAULT_CONFIG

class SiteCrawler:
    def __init__(self, base_url, config=None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.base_url = base_url
        self.root_domain = urlparse(base_url).netloc
        self.visited = set()
        self.discovered_links = set()

    async def fetch_links(self, session, url):
        try:
            async with session.get(url, timeout=self.config['timeout']) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.extract_links(html, url)
                return []
        except Exception as e:
            return []

    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, 'lxml')
        links = set()
        for link in soup.find_all('a', href=True):
            full_url = normalize_url(base_url, link['href'])
            if is_valid_url(self.root_domain, full_url, self.config):
                links.add(full_url)
        return links

    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            queue = [self.base_url]
            while queue:
                tasks = []
                current_batch = queue[:self.config['max_concurrent']]
                queue = queue[self.config['max_concurrent']:]
                
                for url in current_batch:
                    if url not in self.visited:
                        tasks.append(self.fetch_links(session, url))
                        self.visited.add(url)
                
                results = await asyncio.gather(*tasks)
                for links in results:
                    for link in links:
                        if link not in self.discovered_links:
                            self.discovered_links.add(link)
                            queue.append(link)