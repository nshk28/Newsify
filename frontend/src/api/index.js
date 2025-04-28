import axios from 'axios';

// Use environment variable for API base URL, fallback to localhost for dev
// If using CRA proxy, change this to just '/api'
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json', // Explicitly accept JSON
  },
  timeout: 30000, // Set timeout for requests (e.g., 30 seconds)
});

// Helper to format errors consistently
const formatError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    console.error("API Error Response:", error.response.data);
    console.error("Status Code:", error.response.status);
    // Try to get detail message from FastAPI, fallback to generic message
    const message = error.response.data?.detail || error.response.data?.message || `Request failed with status code ${error.response.status}`;
    return new Error(message);
  } else if (error.request) {
    // The request was made but no response was received
    console.error("API No Response:", error.request);
    return new Error('Network error: No response received from server.');
  } else {
    // Something happened in setting up the request that triggered an Error
    console.error('API Request Setup Error:', error.message);
    return new Error(error.message || 'An unexpected error occurred.');
  }
};


export const fetchArticles = async () => {
  try {
    const response = await apiClient.get('/articles');
    // Ensure response data is an array, default to empty array if not
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error("Error fetching articles:", error);
    throw formatError(error); // Re-throw formatted error
  }
};

export const fetchSummary = async (articleId) => {
  if (!articleId) {
    console.error("fetchSummary called with invalid articleId");
    return { summary: null, error: "Invalid article ID provided." };
  }
  try {
    const response = await apiClient.get(`/articles/${articleId}/summary`);
    // Expect response.data to be { summary: "...", error: null } or { summary: null, error: "..." }
    return response.data;
  } catch (error) {
    console.error(`Error fetching summary for article ${articleId}:`, error);
    // Construct error object similar to successful error response from API
    const formattedError = formatError(error);
    return { summary: null, error: formattedError.message };
  }
};

export const triggerScrape = async () => {
  try {
    // Endpoint returns 202 Accepted, response.data might be simple message
    const response = await apiClient.post('/scrape');
    return response.data; // Should contain { message: "..." }
  } catch (error) {
    console.error("Error triggering scrape:", error);
    throw formatError(error);
  }
};

// Optional: Clear data endpoint function
export const clearAllArticles = async () => {
    try {
      // Endpoint returns { message: "...", articles_cleared: num }
      const response = await apiClient.post('/clear');
      return response.data;
    } catch (error) {
      console.error("Error clearing articles:", error);
      throw formatError(error);
    }
  };

export default apiClient; // Export the configured client if needed elsewhere
