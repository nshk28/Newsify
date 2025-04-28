# backend/app/main.py

import logging
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sqlite3
from typing import List, Optional

# Import our modules
from . import database, scraper, summarizer
# Import models for response validation and OpenAPI documentation
from .models import (
    ArticlePublic,
    ArticleSummaryResponse, # Response now includes summary & explanation
    ScrapeStatusResponse,
    HealthResponse,
    ClearResponse
)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__) # Get logger for this module

# --- App Lifecycle (Database Init) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown events."""
    log.info("Newsify Backend starting up...")
    try:
        # Initialize database and create tables if needed on startup
        database.init_db()
        log.info("Database initialized successfully.")
    except Exception as e:
        log.fatal(f"CRITICAL: Database initialization failed on startup: {e}", exc_info=True)
        # Stop the application from starting if DB init fails
        raise RuntimeError("Failed to initialize database connection.") from e
    yield
    # Code to run on shutdown (e.g., close DB pool if using one)
    log.info("Newsify Backend shutting down...")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Newsify API",
    description="API for scraping, storing (SQLite), summarizing/explaining news articles with caching and deduplication.",
    version="1.2.0", # Incremented version for new features
    lifespan=lifespan # Use the lifespan context manager
)

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Background Scraper Task ---
is_scraping_active = False # Simple flag to prevent concurrent scrapes

async def run_background_scrape():
    """Runs scraper, gets *new* articles, and adds them to the DB."""
    global is_scraping_active
    if is_scraping_active:
        log.warning("Scrape task requested but another is already active. Skipping.")
        return

    is_scraping_active = True
    log.info("Starting background scrape task...")
    start_time = asyncio.get_event_loop().time()
    try:
        # Run synchronous scraper code in a thread pool
        loop = asyncio.get_running_loop()
        new_articles = await loop.run_in_executor(None, scraper.run_scraper)

        if new_articles:
            added_count = database.add_articles(new_articles)
            log.info(f"Background scrape completed. Added {added_count} new articles to the database.")
        else:
            log.info("Background scrape completed. No new articles found to add.")
    except Exception as e:
        log.error(f"Error during background scrape execution: {e}", exc_info=True)
    finally:
        end_time = asyncio.get_event_loop().time()
        log.info(f"Background scrape task finished in {end_time - start_time:.2f} seconds.")
        is_scraping_active = False # Release the lock

# --- API Endpoints ---

@app.get("/api/health", response_model=HealthResponse, tags=["Status"])
async def health_check():
    """Performs a basic health check, including database connectivity."""
    db_status = "error"
    try:
        conn = database.get_db_connection()
        conn.close()
        db_status = "ok"
    except Exception as e:
        log.error(f"Health check DB connection failed: {e}")
    return {"status": "ok", "database_status": db_status}


@app.get("/api/articles", response_model=List[ArticlePublic], tags=["Articles"])
async def get_articles():
    """
    Retrieves all stored articles from SQLite, sorted by impact score (desc).
    Returns a list of articles excluding the full content for brevity.
    """
    log.info("Request received for /api/articles")
    try:
        articles_from_db = database.get_all_articles(sort_by="impact_score", ascending=False)
        # Use Pydantic's from_attributes (formerly from_orm) to map DB rows to the response model
        # model_validate replaces __init__ and from_orm in Pydantic v2
        public_articles = [ArticlePublic.model_validate(article, from_attributes=True) for article in articles_from_db if article]
        log.info(f"Returning {len(public_articles)} articles.")
        return public_articles
    except Exception as e:
        log.error(f"Error fetching articles from DB in API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not retrieve articles from database.")


# Endpoint to get both summary and explanation
@app.get("/api/articles/{article_id}/summary", response_model=ArticleSummaryResponse, tags=["Articles"])
async def get_article_details(article_id: str):
    """
    Retrieves an article's summary and explanation.
    Generates and caches them using Groq if not present. Runs generation in parallel.
    """
    log.info(f"Request received for details (summary/explanation) of article ID: {article_id}")
    try:
        article = database.get_article_by_id(article_id)
    except Exception as e:
         log.error(f"Database error retrieving article {article_id} for details: {e}", exc_info=True)
         raise HTTPException(status_code=500, detail="Database error retrieving article.")

    if not article:
        log.warning(f"Article not found for details request: {article_id}")
        raise HTTPException(status_code=404, detail="Article not found")

    # Get existing cached data (will be None if not cached)
    cached_summary = article.get("summary")
    cached_explanation = article.get("explanation")
    combined_error_message = None # To accumulate errors from parallel tasks

    # Check if content exists - essential for generation
    article_content = article.get("content")
    article_title = article.get("title", "Untitled Article")
    if not article_content:
         log.error(f"Cannot generate details for {article_id}: Article content is missing in DB.")
         return {"summary": None, "explanation": None, "error": "Article content is missing, cannot generate details."}

    # --- Prepare tasks for summary and explanation ---
    tasks_to_run = []
    summary_task_needed = False
    explanation_task_needed = False

    # Task for Summary
    if not cached_summary:
        log.info(f"Summary not cached for {article_id}. Scheduling generation.")
        tasks_to_run.append(summarizer.generate_summary(article_title, article_content))
        summary_task_needed = True
    else:
        tasks_to_run.append(asyncio.sleep(0, result=cached_summary)) # Dummy task returning cached data

    # Task for Explanation
    if not cached_explanation:
        log.info(f"Explanation not cached for {article_id}. Scheduling generation.")
        tasks_to_run.append(summarizer.generate_explanation(article_title, article_content))
        explanation_task_needed = True
    else:
        tasks_to_run.append(asyncio.sleep(0, result=cached_explanation)) # Dummy task

    # --- Execute tasks concurrently ---
    final_summary = cached_summary # Start with cached values
    final_explanation = cached_explanation

    if summary_task_needed or explanation_task_needed:
        log.info(f"Running generation tasks for {article_id}...")
        try:
            # Execute tasks and capture results or exceptions
            results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

            summary_result = results[0]
            explanation_result = results[1]

            # --- Process Summary Result ---
            if summary_task_needed: # Only process if we actually ran the task
                if isinstance(summary_result, Exception):
                    log.error(f"Error during summary generation task for {article_id}: {summary_result}")
                    error_msg = f"Summary generation failed: {type(summary_result).__name__}."
                    combined_error_message = error_msg if not combined_error_message else combined_error_message + f" {error_msg}"
                    final_summary = None # Ensure summary is None on error
                elif isinstance(summary_result, str) and summary_result.startswith("Error:"):
                    log.warning(f"Summary generation returned an error message for {article_id}: {summary_result}")
                    error_msg = summary_result # Use the error message from the summarizer
                    combined_error_message = error_msg if not combined_error_message else combined_error_message + f" {error_msg}"
                    final_summary = None
                elif isinstance(summary_result, str):
                    log.info(f"Summary generated successfully for {article_id}. Caching...")
                    final_summary = summary_result
                    # Try caching, but don't let cache failure stop the response
                    try:
                        database.update_article_summary(article_id, final_summary)
                    except Exception as cache_err:
                        log.error(f"Failed to cache summary for {article_id}: {cache_err}")
                else: # Handle unexpected None from generator
                    log.warning(f"Summary generation task yielded unexpected result type for {article_id}: {type(summary_result)}. Keeping cached value if exists.")
                    final_summary = cached_summary # Fallback to original cache

            # --- Process Explanation Result ---
            if explanation_task_needed: # Only process if we actually ran the task
                if isinstance(explanation_result, Exception):
                    log.error(f"Error during explanation generation task for {article_id}: {explanation_result}")
                    error_msg = f"Explanation generation failed: {type(explanation_result).__name__}."
                    combined_error_message = error_msg if not combined_error_message else combined_error_message + f" {error_msg}"
                    final_explanation = None # Ensure explanation is None on error
                elif isinstance(explanation_result, str) and explanation_result.startswith("Error:"):
                    log.warning(f"Explanation generation returned an error message for {article_id}: {explanation_result}")
                    error_msg = explanation_result # Use the error message from the generator
                    combined_error_message = error_msg if not combined_error_message else combined_error_message + f" {error_msg}"
                    final_explanation = None
                elif isinstance(explanation_result, str):
                    log.info(f"Explanation generated successfully for {article_id}. Caching...")
                    final_explanation = explanation_result
                    # Try caching, but don't let cache failure stop the response
                    try:
                        database.update_article_explanation(article_id, final_explanation)
                    except Exception as cache_err:
                         log.error(f"Failed to cache explanation for {article_id}: {cache_err}")
                else: # Handle unexpected None from generator
                    log.warning(f"Explanation generation task yielded unexpected result type for {article_id}: {type(explanation_result)}. Keeping cached value if exists.")
                    final_explanation = cached_explanation # Fallback to original cache

        except Exception as e:
            # Catch unexpected errors during asyncio.gather or result processing
            log.error(f"Unexpected error handling generation tasks for {article_id}: {e}", exc_info=True)
            # Set a general error message if specific ones weren't caught
            if not combined_error_message:
                combined_error_message = "Internal server error during detail generation."
            # Keep potentially cached values if available, despite the error
            final_summary = cached_summary
            final_explanation = cached_explanation
    else:
        log.info(f"Both summary and explanation already cached for {article_id}.")
        # Values already assigned from cache at the start

    # Return final results including any accumulated errors
    return {
        "summary": final_summary,
        "explanation": final_explanation,
        "error": combined_error_message
    }


@app.post("/api/scrape", response_model=ScrapeStatusResponse, status_code=202, tags=["Scraping"])
async def trigger_scrape(background_tasks: BackgroundTasks):
    """
    Triggers the news scraping process (with deduplication) to run in the background.
    Returns immediately with status code 202 (Accepted).
    """
    global is_scraping_active
    log.info("Request received to trigger background scrape.")
    if is_scraping_active:
        log.warning("Scrape trigger request ignored: A scrape task is already running.")
        raise HTTPException(status_code=409, detail="Scraping process is already active.")

    background_tasks.add_task(run_background_scrape)
    log.info("Background scrape task added.")
    return {"message": "Scraping process started in the background. Checking for new articles."}


@app.post("/api/clear", response_model=ClearResponse, tags=["Admin"])
async def clear_data():
    """
    Clears all articles from the SQLite database. Use with extreme caution!
    """
    log.warning("Received request to clear ALL articles from the database.")
    try:
        deleted_count = database.clear_articles()
        log.info(f"Successfully cleared {deleted_count} articles via API.")
        return {"message": "All articles cleared from the database.", "articles_cleared": deleted_count}
    except Exception as e:
        log.error(f"Error clearing database via API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not clear database due to an internal error.")

# Optional: Add root path message
@app.get("/", include_in_schema=False) # Hide from OpenAPI docs if desired
async def read_root():
    return {"message": "Welcome to the Newsify API! Visit /docs for interactive documentation."}