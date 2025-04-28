import json
import requests
import time
import random
import hashlib
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from bs4 import BeautifulSoup
from trafilatura import extract, fetch_url
from fake_useragent import UserAgent
import os
import logging
from typing import List, Dict, Optional, Tuple

# Import the database functions
from . import database
# Import models for type hinting if desired
from .models import ArticleCreate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__) # Use a logger instance

# Constants
CATEGORIES = ["tech", "business", "sports", "entertainment", "world", "science"] # Added more categories
MAX_ARTICLES_PER_CATEGORY = 5  # Increased slightly
REQUEST_DELAY: Tuple[float, float] = (1.5, 4.0)  # Slightly longer, more polite delay
REQUEST_TIMEOUT = 25 # Timeout for requests in seconds

# Initialize UserAgent only once
try:
    ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
except Exception:
    log.warning("fake_useragent failed to initialize, using fallback.")
    ua = type('obj', (object,), {'random': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})()


def get_user_agent() -> str:
    """Returns a random User-Agent string."""
    return ua.random

def resolve_duckduckgo_url(url: str) -> Optional[str]:
    """Resolves DuckDuckGo redirect URLs to the actual target URL."""
    if not url:
        return None
    try:
        if url.startswith('//duckduckgo.com/l/?uddg='):
            # Add scheme for urlparse
            full_url = 'https:' + url if not url.startswith('http') else url
            parsed_url = urlparse(full_url)
            params = parse_qs(parsed_url.query)
            if 'uddg' in params:
                real_url = unquote(params['uddg'][0])
                # Ensure the URL has a scheme
                if not urlparse(real_url).scheme:
                    return 'https://' + real_url # Assume https if scheme missing
                return real_url
            else:
                 log.warning(f"Could not find 'uddg' param in DDG URL: {url}")
                 return None
        # Handle other potential relative URLs or scheme missing cases if needed
        parsed_original = urlparse(url)
        if not parsed_original.scheme:
             if url.startswith("//"):
                  return 'https:' + url
             else:
                  log.warning(f"URL missing scheme and not starting with //: {url}")
                  return None # Cannot safely resolve without scheme
        # If it looks like a valid URL already
        if parsed_original.scheme in ['http', 'https'] and parsed_original.netloc:
             return url
    except Exception as e:
        log.error(f"Error resolving DDG URL '{url}': {e}")
    return None


def search_latest_news_urls(category: str) -> List[str]:
    """Searches DuckDuckGo HTML version for latest news URLs in a category."""
    # Use a more specific query, maybe region-specific if desired
    # &kl=us-en (US English region) &df=d (past day) might help
    search_query = f"latest {category} news"
    search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(search_query)}&df=d&kl=wt-wt&ia=news"
    headers = {"User-Agent": get_user_agent()}
    resolved_urls = []
    unique_domains = set() # Avoid multiple links to the same site from one search

    log.info(f"Searching for '{category}' news on DuckDuckGo...")
    try:
        # Add delay before search request
        time.sleep(random.uniform(REQUEST_DELAY[0] * 0.5, REQUEST_DELAY[1] * 0.5))
        response = requests.get(search_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find result links more reliably
        links = soup.select('div.result__extras__url > a.result__a') # More specific selector
        if not links:
             links = soup.select('a.result__a') # Fallback

        raw_urls = [a.get('href') for a in links if a.get('href')]
        log.debug(f"Found {len(raw_urls)} raw URLs for {category}.")

        count = 0
        for raw_url in raw_urls:
            if count >= MAX_ARTICLES_PER_CATEGORY:
                break
            resolved = resolve_duckduckgo_url(raw_url)
            if resolved:
                 try:
                     domain = urlparse(resolved).netloc
                     if domain and domain not in unique_domains:
                         resolved_urls.append(resolved)
                         unique_domains.add(domain)
                         count += 1
                     # else: log.debug(f"Skipping duplicate domain: {domain}") # Can be noisy
                 except Exception as e:
                      log.warning(f"Error parsing domain for resolved URL '{resolved}': {e}")
            # else: log.debug(f"Could not resolve or invalid URL: {raw_url}") # Noisy

        log.info(f"Resolved {len(resolved_urls)} unique domain URLs for {category}.")
        return resolved_urls

    except requests.exceptions.Timeout:
        log.error(f"Search request timed out for {category}.")
        return []
    except requests.exceptions.RequestException as e:
        log.error(f"Search request error for {category}: {e}")
        return []
    except Exception as e:
        log.error(f"Error parsing search results for {category}: {e}", exc_info=True)
        return []

# --- Extraction Functions ---

def extract_title(soup: BeautifulSoup) -> str:
    """Extracts the article title using multiple strategies."""
    # Prioritize meta tags
    for prop in ['og:title', 'twitter:title']:
        tag = soup.find('meta', property=prop)
        if tag and tag.get('content'):
            return tag['content'].strip()
    tag = soup.find('meta', attrs={'name': 'title'})
    if tag and tag.get('content'):
        return tag['content'].strip()

    # Fallback to title tag
    if soup.title and soup.title.string:
        title_text = soup.title.string.strip()
        # Clean common site name patterns
        separators = [' | ', ' - ', ' :: ', ' » ']
        for sep in separators:
            if sep in title_text:
                title_text = title_text.split(sep)[0].strip()
                break # Use the first separator found
        return title_text

    # Fallback to first h1
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)

    return "No Title Found"


def extract_author(soup: BeautifulSoup) -> str:
    """Extracts the article author using multiple strategies."""
    # Prioritize specific meta tags
    meta_selectors = [
        {'name': 'author'},
        {'property': 'article:author'},
        {'name': 'twitter:creator'},
        {'property': 'og:article:author'}
    ]
    for attrs in meta_selectors:
        tag = soup.find('meta', attrs=attrs)
        if tag and tag.get('content'):
            return tag['content'].strip()

    # Look for common class names or attributes
    selectors = [
        '[rel="author"]', '.author-name', '.author', '.byline a', '.byline', '.byline__author', '.article__author',
        '.author-info .name', '.c-byline__item a', '.AssetSource', '.o-byline__item',
        '.contributor-name', 'a[href*="/author/"]', '.posted-by .fn', 'span.author'
    ]
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            author_text = tag.get_text(strip=True)
            # Clean up common prefixes/junk
            if author_text.lower().startswith("by "):
                author_text = author_text[3:].strip()
            if author_text and len(author_text) < 100: # Basic sanity check for length
                return author_text

    # Check for JSON-LD schema
    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        for script_tag in script_tags:
            if not script_tag.string: continue
            json_data = json.loads(script_tag.string)
            items = json_data if isinstance(json_data, list) else [json_data] # Handle list or single object

            for item in items:
                 if not isinstance(item, dict): continue
                 if item.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']:
                     author_info = item.get('author')
                     if author_info:
                         if isinstance(author_info, list): # Can be a list of authors
                             names = [a.get('name') for a in author_info if isinstance(a, dict) and a.get('name')]
                             if names: return ', '.join(names)
                         elif isinstance(author_info, dict) and author_info.get('name'):
                             return author_info['name']
                         elif isinstance(author_info, str): # Sometimes just a string name
                             return author_info
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as e:
        log.debug(f"Error parsing JSON-LD for author: {e}") # Debug level as it's common

    return "Unknown Author"


def extract_publish_date(soup: BeautifulSoup) -> str:
    """Extracts the publication date using multiple strategies."""
    # Prioritize specific meta tags
    meta_attrs = [
        {'property': 'article:published_time'},
        {'property': 'og:article:published_time'},
        {'name': 'article:published_date'},
        {'name': 'cXenseParse:recs:publishtime'},
        {'name': 'sailthru.date'},
        {'name': 'datePublished'},
        {'itemprop': 'datePublished'},
        {'name': 'dc.date.issued'}
    ]
    for attrs in meta_attrs:
        tag = soup.find('meta', attrs=attrs)
        if tag and tag.get('content'):
            return tag['content'].strip()

    # Look for time tags with datetime attribute
    time_tags = soup.find_all('time', {'datetime': True})
    if time_tags:
        # Prefer time tags with specific classes/attributes indicating publication
        preferred_time = soup.select_one('.entry-date[datetime], .published[datetime], time[itemprop="datePublished"]')
        if preferred_time and preferred_time.get('datetime'):
             return preferred_time['datetime'].strip()
        # Otherwise, take the first one found
        return time_tags[0]['datetime'].strip()

    # Check for specific class names/attributes commonly used for dates
    selectors = [
        '.date-published', '.published-date', '.entry-date', '.article__date',
        '.timestamp', '.post-meta time', '.c-timestamp', '.AssetPublishDate',
        '.o-timestamp time', '.article-dateline time', 'span.date', '.posted-on time',
        '.article-meta time', '[itemprop="datePublished"]' # itemprop can be on span too
    ]
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            date_text = tag.get_text(strip=True) or tag.get('datetime') or tag.get('title')
            if date_text:
                 # Basic cleaning, might need more sophisticated date parsing later
                 date_text = date_text.replace('Published:', '').replace('Updated:', '').strip()
                 # Add more cleaning rules if needed
                 if len(date_text) > 5 and len(date_text) < 50: # Basic sanity check
                    return date_text

    # Check for JSON-LD schema (again, as date might be elsewhere)
    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        for script_tag in script_tags:
            if not script_tag.string: continue
            json_data = json.loads(script_tag.string)
            items = json_data if isinstance(json_data, list) else [json_data]

            for item in items:
                 if not isinstance(item, dict): continue
                 if item.get('@type') in ['NewsArticle', 'Article', 'WebPage', 'BlogPosting']:
                     pub_date = item.get('datePublished')
                     if pub_date and isinstance(pub_date, str): return pub_date
                     mod_date = item.get('dateModified') # Fallback to modified date
                     if mod_date and isinstance(mod_date, str): return mod_date
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as e:
         log.debug(f"Error parsing JSON-LD for date: {e}")

    return "Date Not Available"


def extract_image_url(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Extracts a relevant main image URL using multiple strategies."""
    # Prioritize specific meta tags
    meta_attrs = [
        {'property': 'og:image'},
        {'property': 'twitter:image'},
        {'name': 'twitter:image:src'},
        {'itemprop': 'image'} # Can be meta or link tag
    ]
    for attrs in meta_attrs:
        tag = soup.find(['meta', 'link'], attrs=attrs) # Check both meta and link tags
        if tag and tag.get('content'): # Meta tag
            url = tag['content'].strip()
            return urljoin(base_url, url)
        if tag and tag.get('href'): # Link tag (e.g. itemprop="image")
            url = tag['href'].strip()
            return urljoin(base_url, url)

    # Check JSON-LD schema
    try:
        script_tags = soup.find_all('script', type='application/ld+json')
        for script_tag in script_tags:
            if not script_tag.string: continue
            json_data = json.loads(script_tag.string)
            items = json_data if isinstance(json_data, list) else [json_data]

            for item in items:
                 if not isinstance(item, dict): continue
                 if item.get('@type') in ['NewsArticle', 'Article', 'WebPage', 'BlogPosting']:
                     image_info = item.get('image')
                     if image_info:
                         # Handle various JSON-LD image structures
                         if isinstance(image_info, list):
                             image_info = image_info[0] # Take the first one if it's a list
                         if isinstance(image_info, str):
                             return urljoin(base_url, image_info)
                         if isinstance(image_info, dict):
                              img_url = image_info.get('url') or image_info.get('contentUrl')
                              if img_url and isinstance(img_url, str):
                                   return urljoin(base_url, img_url)
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as e:
        log.debug(f"Error parsing JSON-LD for image: {e}")

    # Look within common article structures for plausible images
    content_selectors = [
        'article img', '.article-content img', '.entry-content img', '.post-content img',
        'figure img', '.featured-image img', '.main-image img', '.story-image img',
        '.article__featured-image img', '.c-picture img', '.js-lazy-image', 'header img'
    ]
    # Exclude common small/irrelevant image patterns
    exclude_patterns = ['logo', 'icon', 'avatar', 'profile', 'spinner', 'loading', 'badge', 'sprite']
    exclude_selectors = ', '.join([f'img[src*="{p}"], img[class*="{p}"]' for p in exclude_patterns])


    for selector in content_selectors:
        # Find all potential images in the area, excluding common noise
        images = soup.select(f'{selector}', limit=5) # Limit to first few found
        for tag in images:
            # Skip if it matches exclusion patterns based on class or src
             if tag.matches(exclude_selectors): continue

             # Prioritize 'src', fallback to 'data-src' etc. for lazy loading
             src = tag.get('src') or tag.get('data-src') or tag.get('data-lazy-src') or tag.get('data-original')
             if src and not src.startswith('data:image') and not src.startswith('about:blank'):
                 src = src.strip()
                 # Basic dimension check (heuristic) - very small images are often icons
                 width = tag.get('width') or tag.get('data-width')
                 height = tag.get('height') or tag.get('data-height')
                 is_small = False
                 try:
                     # Consider images > 200px wide or high more likely main images
                     if (width and int(width) < 150) or (height and int(height) < 150):
                         is_small = True
                     # If dimensions available and look like a square icon, skip
                     if width and height and abs(int(width) - int(height)) < 10 and int(width) < 100:
                          is_small = True
                 except (ValueError, TypeError):
                     pass # Ignore if width/height aren't valid numbers

                 if not is_small:
                     return urljoin(base_url, src) # Resolve relative URLs

    log.debug(f"No suitable main image found for {base_url}")
    return None # No suitable image found


def fallback_content_extraction(html_content: str) -> Optional[str]:
    """More robust fallback using common article selectors if Trafilatura fails."""
    if not html_content: return None
    soup = BeautifulSoup(html_content, 'html.parser')
    # Try common article container selectors first
    selectors = [
        'article', '.article-body', '.article-content', '.entry-content',
        '.story-content', '.post-content', '.main-content', '.body-copy',
        'div[itemprop="articleBody"]', '.articletext', '#story' # Added more
    ]
    content_parts = []
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            log.debug(f"Using fallback selector '{selector}' for content extraction.")
            # Remove common noise like script/style tags, ads, related links sections, footers, headers
            for unwanted_selector in ['script', 'style', '.ad-container', '.related-links', '.sidebar', 'figure', '.caption', 'footer', 'header', '.metadata', '.social-share', '.comments']:
                for unwanted_tag in element.select(unwanted_selector):
                    unwanted_tag.decompose()

            # Extract text primarily from paragraph tags within the container
            paragraphs = element.find_all('p', recursive=True) # Find all <p> descendents
            if paragraphs:
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 10: # Avoid empty or very short paragraphs
                        content_parts.append(text)

            # If enough content found, return it
            if content_parts:
                 full_content = ' '.join(content_parts)
                 if len(full_content) > 200: # Check if we got substantial content
                     log.info(f"Fallback extraction found {len(full_content)} chars using selector '{selector}'.")
                     return full_content
                 else:
                      content_parts = [] # Reset if content was too short

    # If specific containers fail, fallback to joining all paragraphs on page (less reliable)
    log.warning("Fallback selectors failed. Trying to join all paragraphs on page.")
    all_paragraphs = soup.find_all('p')
    content_parts = [p.get_text(strip=True) for p in all_paragraphs if p.get_text(strip=True) and len(p.get_text(strip=True)) > 10]
    if content_parts:
         full_content = ' '.join(content_parts)
         if len(full_content) > 200:
              log.info(f"Fallback extracted {len(full_content)} chars from all paragraphs.")
              return full_content

    log.error("Fallback content extraction failed to find sufficient content.")
    return None


def calculate_impact_score(article: Dict) -> int:
    """
    Calculates a heuristic impact score for an article.
    This is a basic placeholder and can be significantly improved.
    """
    score = 50 # Base score

    # Category weighting (adjust as needed)
    category_weights = {
        "business": 20,
        "tech": 15,
        "world": 18,
        "science": 12,
        "sports": -5, # Lower impact?
        "entertainment": -10 # Lower impact?
    }
    score += category_weights.get(article.get("category", "").lower(), 0)

    # Content length (longer might imply more depth, but not always impact)
    content_length = len(article.get("content", "") or "")
    if content_length > 3000: score += 15
    elif content_length > 1500: score += 10
    elif content_length > 500: score += 5

    # Recency (placeholder - needs proper date parsing)
    # For now, give small bonus if date found and doesn't look like "Not Available"
    pub_time = article.get("published_time", "Date Not Available")
    if pub_time != "Date Not Available" and len(pub_time) > 4:
         score += 5
         # TODO: Could add more points if date is very recent (e.g., within last 24h)
         # Requires parsing 'pub_time' string into a datetime object.

    # Keyword check (simple example)
    title_lower = article.get("title", "").lower()
    # Check first 500 chars of content for keywords
    content_lower_preview = (article.get("content", "") or "")[:500].lower()
    impact_keywords = ["breaking", "major", "alert", "crisis", "exclusive", "significant", "urgent", "warning"]
    keyword_bonus = 0
    for keyword in impact_keywords:
         if keyword in title_lower or keyword in content_lower_preview:
             keyword_bonus = 15 # Add significant bonus for strong keywords
             break
    score += keyword_bonus

    # Author/Source reputation (very basic placeholder)
    # Could maintain a list of reputable sources vs less reputable ones
    # author = article.get("author", "Unknown Author").lower()
    # if "reuters" in author or "ap" in author or "associated press" in author:
    #      score += 5

    # Clamp score between 0 and 100
    final_score = max(0, min(100, score))
    log.debug(f"Calculated impact score {final_score} for: {article.get('title', 'N/A')[:50]}...")
    return final_score


def scrape_article(url: str, category: str) -> Optional[Dict]:
    """
    Scrapes a single article URL. Assumes the URL has passed the initial DB check.
    Returns a dictionary suitable for ArticleCreate model or None on failure.
    """
    headers = {"User-Agent": get_user_agent()}
    html_content = None
    response = None

    log.info(f"Attempting to scrape URL: {url}")
    try:
        # Add delay before each scrape request
        time.sleep(random.uniform(*REQUEST_DELAY))

        # Use requests directly for more control over redirects and final URL
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        html_content = response.text
        final_url = response.url # Get URL after potential redirects

        # Check if the final URL (after redirects) already exists in DB
        # This is a secondary check, main check happens before scraping
        if final_url != url and database.url_exists(final_url):
             log.info(f"Skipping article, final URL {final_url} already exists in DB (redirect from {url}).")
             return None

        # Use Trafilatura first for main content extraction
        # Setting favour_precision=True might yield less but more relevant text
        content = extract(html_content, include_comments=False, include_tables=False, favor_precision=True)

        soup = BeautifulSoup(html_content, 'html.parser')

        # If Trafilatura fails or gets very little, try fallback
        if not content or len(content) < 250: # Increased minimum length
            log.warning(f"Trafilatura extracted minimal content ({len(content or '')} chars) for {final_url}. Trying fallback.")
            content = fallback_content_extraction(html_content)

        if not content:
             log.error(f"Failed to extract sufficient content for {final_url} even with fallback.")
             return None # Cannot proceed without content

        title = extract_title(soup)
        if title == "No Title Found":
            log.warning(f"Failed to extract title for {final_url}. Using fallback title.")
            # Use domain name as a fallback title if absolutely necessary
            parsed_uri = urlparse(final_url)
            title = f"Article from {parsed_uri.netloc}" if parsed_uri.netloc else "Untitled Article"

        # Generate unique ID using a hash of the *final* URL and title
        hash_input = (final_url + title).encode('utf-8')
        article_id = hashlib.md5(hash_input).hexdigest()

        article_data = {
            "id": article_id,
            "title": title,
            "author": extract_author(soup),
            "source_url": final_url, # Store the final URL
            "content": content.strip(),
            "published_time": extract_publish_date(soup),
            "image_url": extract_image_url(soup, final_url), # Pass base URL
            "category": category,
            "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "summary": None, # Summary is initially null
            # Impact score calculated after dict creation
        }

        # Calculate impact score and add it
        article_data["impact_score"] = calculate_impact_score(article_data)

        log.info(f"Successfully processed: {article_data['title'][:60]}... (ID: {article_id}, Score: {article_data['impact_score']})")
        # Validate with Pydantic model before returning (optional but good practice)
        # try:
        #     ArticleCreate(**article_data)
        # except ValidationError as e:
        #      log.error(f"Validation error for scraped data from {final_url}: {e}")
        #      return None
        return article_data

    except requests.exceptions.Timeout:
        log.error(f"Timeout error scraping {url}")
        return None
    except requests.exceptions.HTTPError as e:
        # Log differently based on status code
        if e.response.status_code == 404:
            log.warning(f"HTTP 404 Not Found for {url}. Skipping.")
        elif e.response.status_code == 403:
             log.warning(f"HTTP 403 Forbidden for {url}. Access denied.")
        elif e.response.status_code >= 500:
             log.error(f"HTTP Server Error {e.response.status_code} for {url}.")
        else:
             log.error(f"HTTP error scraping {url}: {e.response.status_code} {e.response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        log.error(f"Request error scraping {url}: {e}")
        return None
    except Exception as e:
        # Catch broad exception for unexpected errors during parsing/processing
        log.error(f"Unexpected error processing URL {url}: {e}", exc_info=True) # Log traceback
        return None


def run_scraper() -> List[Dict]:
    """
    Runs the scraper for all categories, performing database deduplication before scraping.
    Returns only the *newly* scraped articles (as dicts ready for DB insertion).
    """
    newly_scraped_articles: List[Dict] = []
    # Use a set to track URLs processed *within this specific run* to handle duplicates from search results
    processed_urls_in_this_run: set[str] = set()

    log.info("Starting scraper run...")
    for category in CATEGORIES:
        log.info(f"--- Processing category: {category} ---")
        # 1. Search for candidate URLs
        candidate_urls = search_latest_news_urls(category)

        if not candidate_urls:
            log.warning(f"No candidate URLs found for category: {category}")
            continue

        articles_added_this_category = 0
        # 2. Iterate through candidates
        for url in candidate_urls:
            if not url or url in processed_urls_in_this_run:
                # log.debug(f"Skipping already processed URL in this run: {url}")
                continue
            processed_urls_in_this_run.add(url) # Mark as seen in this run

            # 3. Check if URL (or its potential final redirected version) exists in DB
            try:
                 if database.url_exists(url):
                     log.info(f"Skipping existing URL (found in DB): {url}")
                     continue
                 # Optional: Add check for common variations (http vs https, www vs non-www) if needed
                 # else: log.debug(f"URL {url} not found in DB, proceeding to scrape.")
            except Exception as e:
                 # Log error but proceed cautiously - might lead to duplicates if DB check fails
                 log.error(f"Database check failed for URL {url}: {e}. Attempting scrape anyway.")

            # 4. If checks pass, attempt to scrape the article
            scraped_article_data = scrape_article(url, category)

            # 5. Process the result
            if scraped_article_data and scraped_article_data.get('source_url'):
                final_url = scraped_article_data['source_url']
                # Add final URL to processed set for this run as well
                processed_urls_in_this_run.add(final_url)

                # One final check: ensure the *final* url didn't already exist if it redirected
                # This is redundant if scrape_article handles it, but adds safety
                if final_url != url and database.url_exists(final_url):
                     log.info(f"Skipping article post-scrape, final URL {final_url} exists in DB (redirect from {url}).")
                     continue

                # If truly new, add to the list for DB insertion
                newly_scraped_articles.append(scraped_article_data)
                articles_added_this_category += 1
                # Optional: Break early if enough articles found for category?
                # if articles_added_this_category >= MAX_ARTICLES_PER_CATEGORY: break

            # If scraping failed, the URL is already marked in processed_urls_in_this_run
            # No need to explicitly handle failed scrapes here unless specific action needed

        log.info(f"Finished category '{category}'. Added {articles_added_this_category} new articles.")

    total_new = len(newly_scraped_articles)
    log.info(f"--- Scraper run complete. Found {total_new} total new articles to add. ---")
    return newly_scraped_articles


# Allow running scraper directly for testing/debugging
if __name__ == "__main__":
    print("[Standalone Scraper Run]")
    # Ensure DB is initialized when run directly
    try:
        print("Initializing database...")
        database.init_db()
    except Exception as e:
        print(f"FATAL: Could not initialize database: {e}")
        exit(1)

    print("\nStarting scraper process...")
    start_time = time.time()
    new_articles = run_scraper()
    end_time = time.time()
    print(f"\nScraper process finished in {end_time - start_time:.2f} seconds.")

    if new_articles:
         print(f"\nFound {len(new_articles)} new articles. Attempting to add to database...")
         try:
             added_count = database.add_articles(new_articles)
             print(f"Successfully added {added_count} new articles to the database.")
         except Exception as e:
              print(f"Error adding articles to database: {e}")
    else:
         print("\nNo new articles were found during this run.")

    print("\nStandalone run finished.")

