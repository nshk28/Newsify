# newsify/backend/app/database.py
# Database module for Newsify
import sqlite3
import logging
import os
from typing import Dict, List, Optional, Any
import time

# Determine the absolute path for the database file
# Place it in the 'backend' directory, one level up from 'app'
DATABASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(DATABASE_DIR, "newsify.db")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__) # Use a logger instance

log.info(f"Database path set to: {DATABASE_PATH}")

def get_db_connection() -> sqlite3.Connection:
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10) # Added timeout
        conn.row_factory = sqlite3.Row # Access columns by name
        log.debug("Database connection established.")
        return conn
    except sqlite3.Error as e:
        log.error(f"Error connecting to database: {e}", exc_info=True)
        raise

def init_db():
    """Initializes the database and creates the articles table if it doesn't exist."""
    log.info(f"Initializing database at {DATABASE_PATH}...")
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,          -- Unique hash ID
                    title TEXT NOT NULL,
                    author TEXT,
                    source_url TEXT UNIQUE NOT NULL, -- Unique URL for deduplication
                    content TEXT,
                    published_time TEXT,          -- Store as TEXT, parsing handled elsewhere
                    image_url TEXT,
                    category TEXT NOT NULL,
                    scraped_at TEXT NOT NULL,     -- Store as ISO8601 string TEXT
                    summary TEXT,                 -- For caching summaries
                    explanation TEXT,
                    impact_score INTEGER DEFAULT 50 -- Store impact score
                );
            """)
            # Add indexes for faster lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON articles (category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_impact_score ON articles (impact_score);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_at ON articles (scraped_at);")
            conn.commit()
            log.info("Database initialized successfully. 'articles' table verified/created.")
    except sqlite3.Error as e:
        log.error(f"Database initialization failed: {e}", exc_info=True)
        raise
    except OSError as e:
        log.error(f"Failed to create database directory {os.path.dirname(DATABASE_PATH)}: {e}", exc_info=True)
        raise

def dict_from_row(row: sqlite3.Row) -> Optional[Dict[str, Any]]:
    """Converts a sqlite3.Row object to a dictionary."""
    if row is None:
        return None
    return dict(row)

def add_articles(articles: List[Dict]) -> int:
    """
    Adds multiple articles to the database.
    Uses INSERT OR IGNORE to handle potential duplicate IDs/URLs gracefully.
    Returns the number of articles successfully added.
    """
    if not articles:
        return 0

    added_count = 0
    sql = """
        INSERT OR IGNORE INTO articles
        (id, title, author, source_url, content, published_time, image_url, category, scraped_at, summary,explanation, impact_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    # Prepare data tuples, ensuring all keys exist with None/defaults
    data_to_insert = []
    for article in articles:
         # Ensure required fields have values
         article_id = article.get("id")
         source_url = article.get("source_url")
         category = article.get("category")
         title = article.get("title", "Untitled Article") # Provide default title

         if not all([article_id, source_url, category]):
             log.warning(f"Skipping article due to missing required fields (id, url, category): Title='{title}', URL='{source_url}'")
             continue

         data_tuple = (
              article_id,
              title,
              article.get("author"),
              source_url,
              article.get("content"),
              article.get("published_time"),
              article.get("image_url"),
              category,
              article.get("scraped_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
              article.get("summary"), # Initially None
              article.get("explanation"),
              article.get("impact_score", 50)
         )
         data_to_insert.append(data_tuple)

    if not data_to_insert:
         log.warning("No valid articles provided to add_articles after validation.")
         return 0

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, data_to_insert)
            added_count = cursor.rowcount # Number of rows actually inserted
            conn.commit()
            if added_count > 0:
                log.info(f"Successfully added {added_count} new articles to the database.")
            else:
                 log.info("No new articles were added (they might have existed already).")
    except sqlite3.Error as e:
        log.error(f"Error adding articles to database: {e}", exc_info=True)
    return added_count


def get_all_articles(sort_by: str = "impact_score", ascending: bool = False) -> List[Dict]:
    """Retrieves all articles from the database, sorted."""
    allowed_sort_columns = ["impact_score", "scraped_at", "published_time", "title", "category"]
    sort_column = sort_by if sort_by in allowed_sort_columns else "impact_score"
    order = "ASC" if ascending else "DESC"

    # Ensure scraped_at is sorted correctly (lexicographical sort works for ISO8601)
    sql = f"SELECT * FROM articles ORDER BY {sort_column} {order}"

    articles = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            articles = [dict_from_row(row) for row in rows if row] # Filter out None if any rows fail dict conversion
            log.debug(f"Retrieved {len(articles)} articles from database.")
    except sqlite3.Error as e:
        log.error(f"Error retrieving articles from database: {e}", exc_info=True)
        # In case of error, return empty list or re-raise
        return []
    return articles

def get_article_by_id(article_id: str) -> Optional[Dict]:
    """Retrieves a single article by its ID."""
    sql = "SELECT * FROM articles WHERE id = ?"
    article = None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (article_id,))
            row = cursor.fetchone()
            article = dict_from_row(row)
            # log.debug(f"Retrieved article by ID: {article_id}" if article else f"Article not found by ID: {article_id}")
    except sqlite3.Error as e:
        log.error(f"Error retrieving article by ID {article_id}: {e}", exc_info=True)
    return article

# backend/app/database.py (Add this new function)
def update_article_explanation(article_id: str, explanation: str) -> bool:
    """Updates the explanation for a specific article."""
    sql = "UPDATE articles SET explanation = ? WHERE id = ?"
    success = False
    if not article_id or explanation is None:
         log.warning(f"Invalid input for updating explanation: ID='{article_id}', Explanation='{explanation}'")
         return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (explanation, article_id))
            conn.commit()
            if cursor.rowcount > 0:
                log.info(f"Successfully updated explanation for article ID: {article_id}")
                success = True
            else:
                 log.warning(f"Attempted to update explanation, but article ID not found or explanation unchanged: {article_id}")
    except sqlite3.Error as e:
        log.error(f"Error updating explanation for article ID {article_id}: {e}", exc_info=True)
    return success

def url_exists(source_url: str) -> bool:
    """Checks if an article with the given source_url already exists."""
    sql = "SELECT EXISTS(SELECT 1 FROM articles WHERE source_url = ? LIMIT 1)"
    exists = False
    if not source_url: # Avoid checking empty URLs
        return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (source_url,))
            result = cursor.fetchone()
            exists = result[0] == 1 if result else False
            # log.debug(f"URL exists check for {source_url}: {exists}")
    except sqlite3.Error as e:
        log.error(f"Error checking URL existence for {source_url}: {e}", exc_info=True)
        # Assume it doesn't exist on error to potentially allow scrape? Or return True to prevent? Let's return False.
        exists = False
    return exists


def update_article_summary(article_id: str, summary: str) -> bool:
    """Updates the summary for a specific article."""
    sql = "UPDATE articles SET summary = ? WHERE id = ?"
    success = False
    if not article_id or summary is None: # Basic validation
         log.warning(f"Invalid input for updating summary: ID='{article_id}', Summary='{summary}'")
         return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (summary, article_id))
            conn.commit()
            if cursor.rowcount > 0:
                log.info(f"Successfully updated summary for article ID: {article_id}")
                success = True
            else:
                 log.warning(f"Attempted to update summary, but article ID not found or summary unchanged: {article_id}")
    except sqlite3.Error as e:
        log.error(f"Error updating summary for article ID {article_id}: {e}", exc_info=True)
    return success

def clear_articles() -> int:
    """Deletes all articles from the database. Returns number of rows deleted."""
    sql = "DELETE FROM articles"
    deleted_count = 0
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            deleted_count = cursor.rowcount
            conn.commit()
            log.info(f"Cleared {deleted_count} articles from the database.")
    except sqlite3.Error as e:
        log.error(f"Error clearing articles from database: {e}", exc_info=True)
    return deleted_count
