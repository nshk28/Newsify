
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
import time

# Helper function to generate current time in ISO format
def current_time_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class ArticleBase(BaseModel):
    """ Base model for article data points """
    title: str = Field(..., min_length=1)
    author: Optional[str] = "Unknown Author"
    source_url: HttpUrl
    published_time: Optional[str] = "Date Not Available"
    image_url: Optional[HttpUrl] = None
    category: str = Field(..., min_length=1)
    impact_score: int = Field(default=50, ge=0, le=100)

class ArticleCreate(ArticleBase):
    """ Model for creating an article (used internally by scraper) """
    id: str = Field(..., min_length=32, max_length=32) # MD5 hash length
    content: Optional[str] = None
    scraped_at: str = Field(default_factory=current_time_iso)
    summary: Optional[str] = None # Summary is added later
    explanation: Optional[str] = None # <<<--- Add explanation

class ArticleInDB(ArticleCreate):
    """ Model representing article structure as stored in DB (includes all fields) """
    pass # Inherits all fields from ArticleCreate

class ArticlePublic(ArticleBase):
    """ Model for public API responses (excluding raw content) """
    id: str
    scraped_at: str # Use string from DB directly
    summary: Optional[str] = None # Include summary if available
    explanation: Optional[str] = None # <<<--- Add explanation

    model_config = {
        "from_attributes": True  # Use this instead of orm_mode
    }

class ArticleSummaryResponse(BaseModel):
    """ Response model for the summary/explanation endpoint """
    summary: Optional[str] = None
    explanation: Optional[str] = None 
    error: Optional[str] = None

class ScrapeStatusResponse(BaseModel):
    """ Response model for the scrape trigger endpoint """
    message: str
    # Optional: could add articles_added if scrape ran synchronously
    # articles_added: Optional[int] = None

class HealthResponse(BaseModel):
     status: str
     database_status: str

class ClearResponse(BaseModel):
     message: str
     articles_cleared: int