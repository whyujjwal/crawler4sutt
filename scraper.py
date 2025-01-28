import fitz
import json
import aiofiles
from datetime import datetime
from bs4 import BeautifulSoup
from scrapekit.utils import clean_text  
from scrapekit.config import DEFAULT_CONFIG  
import aiohttp
import logging

logger = logging.getLogger(__name__)

class ContentScraper:
    def __init__(self, config=None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.results = []
    
    async def process_content(self, url, content_type, content):
        if content_type == 'pdf':
            return await self.process_pdf(url, content)
        else:
            return await self.process_html(url, content)

    async def process_pdf(self, url, content):
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            return {
                'url': url,
                'content': clean_text(text),
                'type': 'pdf',
                'metadata': doc.metadata
            }
        except Exception as e:
            return None

    async def process_html(self, url, content):
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            for tag in self.config['excluded_tags']:
                for element in soup(tag):
                    element.decompose()
            
            for selector in self.config['clean_selectors']:
                for element in soup.select(selector):
                    element.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            return {
                'url': url,
                'content': clean_text(text),
                'type': 'html',
                'title': soup.title.text.strip() if soup.title else ''
            }
        except Exception as e:
            return None

    async def save_results(self):
        async with aiofiles.open(self.config['output_file'], 'w') as f:
            await f.write(json.dumps({
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'source': self.config.get('source', 'website'),
                    'stats': {
                        'total_pages': len(self.results),
                        'pdf_count': sum(1 for r in self.results if r['type'] == 'pdf'),
                        'html_count': sum(1 for r in self.results if r['type'] == 'html')
                    }
                },
                'data': self.results
            }, indent=2, ensure_ascii=False))

async def scrape_site(url: str, config: dict) -> None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=config['timeout'], headers=config.get('headers', {})) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Remove excluded tags
                    for tag in config['excluded_tags']:
                        for element in soup.find_all(tag):
                            element.decompose()
                    
                    # Remove elements by CSS selectors
                    if 'clean_selectors' in config:
                        for selector in config['clean_selectors']:
                            for element in soup.select(selector):
                                element.decompose()
                    
                    # Extract and clean main content
                    main_content = soup.find('main') or soup.find('article') or soup.find('div', {'id': 'mw-content-text'})
                    raw_content = main_content.get_text(' ', strip=True) if main_content else soup.get_text(' ', strip=True)
                    cleaned_content = clean_text(raw_content)
                    
                    data = {
                        "metadata": {
                            "created_at": datetime.now().isoformat(),
                            "source": url,
                            "stats": {
                                "total_pages": 1,
                                "pdf_count": len(soup.find_all('a', href=lambda x: x and x.endswith('.pdf'))),
                                "html_count": 1
                            }
                        },
                        "data": [{
                            "url": url,
                            "title": clean_text(soup.title.string) if soup.title else "",
                            "content": cleaned_content,
                            "links": [
                                a.get('href') for a in soup.find_all('a', href=True)
                                if not a.get('href').startswith('#')
                            ]
                        }]
                    }
                    
                    with open(config['output_file'], 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    logger.info(f"Data saved to {config['output_file']}")
                else:
                    raise Exception(f"Failed to fetch {url}, status: {response.status}")
        except Exception as e:
            logger.error(f"Error while scraping {url}: {str(e)}")
            raise