from urllib.parse import urlparse, urljoin
import re

def normalize_url(base_url, url):
    normalized = urljoin(base_url, url)
    return normalized.split('#')[0].rstrip('/')

def is_valid_url(base_domain, url, config):
    parsed = urlparse(url)
    if parsed.netloc != base_domain or parsed.scheme not in ('http', 'https'):
        return False
    
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in config['bad_extensions']):
        return False
    
    return True

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and newlines"""
    if not text:
        return ""
    
    # Replace multiple spaces and newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove spaces around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    # Remove leading/trailing whitespace
    return text.strip()