DEFAULT_CONFIG = {
    'max_depth': 3,
    'max_concurrent': 20,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Mozilla/5.0 (X11; Linux x86_64)'
    ],
    'timeout': 30,
    'max_retries': 2,
    'output_file': 'scraped_data.json',
    'pdf_dir': 'pdfs',
    'excluded_tags': ['script', 'style', 'nav', 'footer', 'header', 'iframe'],
    'clean_selectors': ['.ads', '.cookie-banner'],
    'allowed_extensions': ['.html', '.htm', '.pdf']
}