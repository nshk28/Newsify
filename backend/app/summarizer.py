# import os
# import logging
# from groq import Groq, GroqError
# from dotenv import load_dotenv
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
# from typing import Optional

# # Load environment variables from .env file in the backend directory
# dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
# load_dotenv(dotenv_path=dotenv_path)

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# log = logging.getLogger(__name__) # Use a logger instance

# api_key = os.environ.get("GROQ_API_KEY")
# if not api_key:
#     log.error("GROQ_API_KEY not found in environment variables.")
#     # Application might fail later if summarization is attempted.
#     # Consider raising an error during startup in main.py if key is mandatory.
#     client = None # No client if key is missing
# else:
#      try:
#           client = Groq(api_key=api_key)
#           log.info("Groq client initialized.")
#      except Exception as e:
#           log.error(f"Failed to initialize Groq client: {e}", exc_info=True)
#           client = None


# MODEL = "mixtral-8x7b-32768" # Recommended model on Groq
# # MODEL = "llama3-70b-8192" # Alternative
# # MODEL = "deepseek-r1-distill-llama-70b" # If you have access and prefer it
# MAX_TOKENS_SUMMARY = 512  # Limit summary length (~100-150 words typically)
# TEMPERATURE = 0.5
# TOP_P = 0.9

# # Configure retry mechanism for Groq API calls
# @retry(
#     stop=stop_after_attempt(3), # Retry up to 3 times (initial try + 2 retries)
#     wait=wait_exponential(multiplier=1, min=2, max=10), # Exponential backoff (2s, 4s, ...)
#     retry=(retry_if_exception_type((GroqError, ConnectionError, TimeoutError))), # Retry on specific errors
#     reraise=True # Reraise the exception if all retries fail
# )
# async def generate_summary(title: str, content: str) -> Optional[str]:
#     """
#     Generates a concise summary using the Groq API with retry logic.
#     Returns the summary string on success, None or an error string on failure.
#     """
#     if not client:
#         log.error("Cannot generate summary: Groq client is not initialized (check API key).")
#         return "Error: Summarizer service not configured."

#     if not content:
#         log.warning(f"Cannot generate summary for '{title}': Content is empty.")
#         return None # Return None if content is missing, API shouldn't be called

#     # Prepare the prompt - keep it concise and clear
#     # Limit input content length significantly to avoid hitting Groq context limits and reduce cost/latency
#     max_content_length = 6000 # Adjust based on model context window and typical article size
#     truncated_content = content[:max_content_length]
#     if len(content) > max_content_length:
#         log.warning(f"Content for '{title}' truncated to {max_content_length} chars for summarization.")

#     prompt = f"""
#     Please provide a concise, neutral summary (around 3-5 sentences, maximum 150 words) of the following news article.
#     Focus strictly on the main facts and key information presented in the text.
#     Do not add any introductory phrases like "Here is the summary:" or "The article discusses...".
#     Do not include opinions or analysis not present in the original text.

#     Article Title: {title}

#     Article Content:
#     {truncated_content}

#     Concise Summary:"""

#     log.info(f"Requesting summary generation for: {title[:50]}...")
#     try:
#         chat_completion = await client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt,
#                 }
#             ],
#             model=MODEL,
#             temperature=TEMPERATURE,
#             max_tokens=MAX_TOKENS_SUMMARY,
#             top_p=TOP_P,
#             stop=None,  # Let the model decide based on prompt/content
#             stream=False, # Get the full response at once
#         )

#         summary = chat_completion.choices[0].message.content.strip()

#         # Basic validation of the summary
#         if not summary or len(summary) < 20:
#             log.warning(f"Generated summary for '{title}' seems too short or empty.")
#             # Decide whether to return it or consider it a failure
#             return None # Or return "Error: Generated summary was empty."
#         elif len(summary) > MAX_TOKENS_SUMMARY * 6: # Heuristic check for overly long summary
#             log.warning(f"Generated summary for '{title}' seems too long, possibly failed instruction following.")
#             # Truncate or return error? Let's return truncated for now.
#             summary = summary[:MAX_TOKENS_SUMMARY * 6] + "..."

#         log.info(f"Summary generated successfully for: {title[:50]}...")
#         return summary

#     except RetryError as e:
#         # This catches the error after all retries have failed
#         log.error(f"Groq API error after retries for '{title}': {e}", exc_info=True)
#         # Extract underlying error type if needed
#         original_exception = e.cause
#         return f"Error: Summary service unavailable after multiple attempts ({type(original_exception).__name__})."

#     except GroqError as e:
#         # Catch specific Groq errors not covered by retry or if retry is disabled
#         log.error(f"Groq API error generating summary for '{title}': {e}", exc_info=True)
#         return f"Error: Summary service API error ({e.status_code})."

#     except Exception as e:
#         # Catch any other unexpected errors during the API call or processing
#         log.error(f"Unexpected error generating summary for '{title}': {e}", exc_info=True)
#         return f"Error: An unexpected error occurred during summary generation."

import os
import logging
from groq import Groq, GroqError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from typing import Optional

# Load environment variables from .env file in the backend directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__) # Use a logger instance

api_key = os.environ.get("GROQ_API_KEY")
client = None
if not api_key:
    log.error("GROQ_API_KEY not found in environment variables.")
else:
     try:
          client = Groq(api_key=api_key)
          log.info("Groq client initialized.")
     except Exception as e:
          log.error(f"Failed to initialize Groq client: {e}", exc_info=True)

# --- CHANGE MODEL NAME ---
MODEL_SUMMARY = "llama3-8b-8192" # Use a known available model for summary
MODEL_EXPLANATION = "llama3-8b-8192" # Can be the same or different
# --- ADJUST MAX TOKENS / CONTENT LENGTH ---
MAX_TOKENS_SUMMARY = 300 # Slightly less restrictive for summary
MAX_TOKENS_EXPLANATION = 800 # Allow more tokens for explanation
MAX_CONTENT_LENGTH_INPUT = 4000 # Reduce input length further

TEMPERATURE = 0.6 # Adjusted temperature slightly
TOP_P = 0.9

# --- Function to generate concise summary ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=(retry_if_exception_type((GroqError, ConnectionError, TimeoutError))),
    reraise=True
)
async def generate_summary(title: str, content: str) -> Optional[str]:
    """Generates a concise summary using the Groq API."""
    if not client: return "Error: Summarizer service not configured."
    if not content: return None

    truncated_content = content[:MAX_CONTENT_LENGTH_INPUT]
    if len(content) > MAX_CONTENT_LENGTH_INPUT:
        log.warning(f"Summary Input: Content for '{title}' truncated to {MAX_CONTENT_LENGTH_INPUT} chars.")

    prompt = f"""Please provide a concise, neutral summary (around 3-5 sentences, maximum 100 words) of the following news article. Focus strictly on the main facts. Do not add introductory phrases.

Article Title: {title}
Article Content:
{truncated_content}

Concise Summary:"""

    log.info(f"Requesting CONCISE SUMMARY for: {title[:50]}... using model {MODEL_SUMMARY}")
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_SUMMARY,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS_SUMMARY,
            top_p=TOP_P,
            stream=False,
        )
        summary = chat_completion.choices[0].message.content.strip()
        log.info(f"Concise summary generated successfully for: {title[:50]}...")
        # Add basic validation if needed
        return summary if summary and len(summary) > 10 else None
    except RetryError as e:
        log.error(f"CONCISE SUMMARY: Groq API error after retries for '{title}': {e}", exc_info=True)
        return f"Error: Summary service unavailable ({type(e.cause).__name__})."
    except GroqError as e:
        log.error(f"CONCISE SUMMARY: Groq API error for '{title}': Status={e.status_code}, Body={e.response.text}", exc_info=True) # Log body
        return f"Error: Summary service API error ({e.status_code})."
    except Exception as e:
        log.error(f"CONCISE SUMMARY: Unexpected error for '{title}': {e}", exc_info=True)
        return f"Error: An unexpected error occurred."

# --- NEW Function to generate in-depth explanation ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=(retry_if_exception_type((GroqError, ConnectionError, TimeoutError))),
    reraise=True
)
async def generate_explanation(title: str, content: str) -> Optional[str]:
    """Generates an in-depth explanation using the Groq API."""
    if not client: return "Error: Explanation service not configured."
    if not content: return None

    truncated_content = content[:MAX_CONTENT_LENGTH_INPUT] # Use same truncation for consistency
    if len(content) > MAX_CONTENT_LENGTH_INPUT:
        log.warning(f"Explanation Input: Content for '{title}' truncated to {MAX_CONTENT_LENGTH_INPUT} chars.")

    prompt = f"""Please provide an in-depth explanation (around 3-4 paragraphs, 200-300 words) of the key points, context, and potential implications of the following news article. Analyze the main arguments or events described. Do not just repeat the article.

Article Title: {title}
Article Content:
{truncated_content}

In-depth Explanation:"""

    log.info(f"Requesting IN-DEPTH EXPLANATION for: {title[:50]}... using model {MODEL_EXPLANATION}")
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL_EXPLANATION,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS_EXPLANATION,
            top_p=TOP_P,
            stream=False,
        )
        explanation = chat_completion.choices[0].message.content.strip()
        log.info(f"In-depth explanation generated successfully for: {title[:50]}...")
        return explanation if explanation and len(explanation) > 20 else None
    except RetryError as e:
        log.error(f"IN-DEPTH EXPLANATION: Groq API error after retries for '{title}': {e}", exc_info=True)
        return f"Error: Explanation service unavailable ({type(e.cause).__name__})."
    except GroqError as e:
        log.error(f"IN-DEPTH EXPLANATION: Groq API error for '{title}': Status={e.status_code}, Body={e.response.text}", exc_info=True) # Log body
        return f"Error: Explanation service API error ({e.status_code})."
    except Exception as e:
        log.error(f"IN-DEPTH EXPLANATION: Unexpected error for '{title}': {e}", exc_info=True)
        return f"Error: An unexpected error occurred."