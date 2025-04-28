// frontend/src/App.js

import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import ArticleList from './components/ArticleList';
import SummaryModal from './components/SummaryModal'; // Name kept for now
import { fetchArticles, fetchSummary, triggerScrape, clearAllArticles } from './api';
import './styles/App.css';
import './styles/dark-mode.css';

// --- Notification Component ---
function Notification({ message, type, show }) {
    // Simple fade-in/out might need more complex animation library for slide
    const style = {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: show ? 'translateX(-50%) translateY(0)' : 'translateX(-50%) translateY(100px)',
        padding: '12px 25px',
        borderRadius: '6px',
        color: 'var(--button-text)',
        fontWeight: 500,
        zIndex: 1100,
        boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)',
        opacity: show ? 1 : 0,
        transition: 'opacity 0.4s ease, transform 0.4s ease',
        backgroundColor: type === 'success' ? 'var(--success-color)' :
                         type === 'error' ? 'var(--error-color)' :
                         'var(--button-background)' // Default to info blue
    };
    if (!message) return null; // Don't render empty message
    return <div style={style}>{message}</div>;
}


function App() {
  // --- State ---
  const [articles, setArticles] = useState([]);
  const [isLoadingArticles, setIsLoadingArticles] = useState(true);
  const [articlesError, setArticlesError] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isScraping, setIsScraping] = useState(false);

  // State for detail modal (summary + explanation)
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [detailData, setDetailData] = useState(null); // Holds { summary, explanation, error }
  const [isDetailLoading, setIsDetailLoading] = useState(false);

  // State for notifications
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });
  const notificationTimer = React.useRef(null); // Ref to manage notification timeout

  // --- Effects ---

  // Load dark mode preference on initial mount
  useEffect(() => {
    const savedMode = localStorage.getItem('darkMode') === 'true';
    setIsDarkMode(savedMode);
    document.body.classList.toggle('dark-mode', savedMode); // Use toggle for cleaner logic
  }, []);

  // Function to show notifications
  const showNotification = useCallback((message, type = 'info', duration = 4000) => {
    // Clear existing timer if a new notification comes quickly
    if (notificationTimer.current) {
      clearTimeout(notificationTimer.current);
    }
    setNotification({ show: true, message, type });
    // Set new timer to hide the notification
    notificationTimer.current = setTimeout(() => {
      setNotification({ show: false, message: '', type: '' });
      notificationTimer.current = null;
    }, duration);
  }, []); // showNotification is stable


  // Function to load articles
  const loadArticles = useCallback(async (showSuccessNotification = false) => {
    console.log("Attempting to load articles...");
    setIsLoadingArticles(true);
    setArticlesError(null);
    try {
      const data = await fetchArticles();
      setArticles(data || []);
      console.log(`Loaded ${data?.length ?? 0} articles.`);
      if (showSuccessNotification && data?.length > 0) {
          showNotification("Articles refreshed successfully.", "success");
      } else if (showSuccessNotification && data?.length === 0) {
           showNotification("Article list is empty.", "info");
      }
    } catch (err) {
      console.error("Failed to load articles:", err);
      setArticlesError(err);
      setArticles([]);
      showNotification(`Error loading articles: ${err.message}`, "error", 5000);
    } finally {
      setIsLoadingArticles(false);
    }
  }, [showNotification]); // Depend on showNotification

  // Load articles on initial mount
  useEffect(() => {
    loadArticles(false); // Don't show success on initial load
     // Cleanup notification timer on unmount
    return () => {
        if (notificationTimer.current) {
            clearTimeout(notificationTimer.current);
        }
    };
  }, [loadArticles]);

  // --- Event Handlers ---

  const toggleDarkMode = () => {
    setIsDarkMode(prevMode => {
      const newMode = !prevMode;
      document.body.classList.toggle('dark-mode', newMode);
      localStorage.setItem('darkMode', String(newMode)); // Store as string 'true'/'false'
      return newMode;
    });
  };

  const handleScrape = async () => {
    if (isScraping) return;

    setIsScraping(true);
    setArticlesError(null);
    showNotification("Scraping process started in background...", "info", 5000); // Show longer
    try {
      await triggerScrape();
      // Schedule a delayed refresh to check for new articles
      setTimeout(() => {
        showNotification("Checking for new articles...", "info", 2000);
        loadArticles(true); // Show success notification if articles are loaded
      }, 9000); // Increase delay slightly to allow more time for scraping

    } catch (err) {
      console.error("Scraping trigger failed:", err);
      // Error might be 409 Conflict if already scraping
      const message = err.message.includes('409') ? "Scraping is already in progress." : `Scraping trigger failed: ${err.message}`;
      showNotification(message, "error", 5000);
    } finally {
      setIsScraping(false); // Set back to false once trigger API call returns
    }
  };

  // Handler when an article card is clicked
  const handleShowDetails = useCallback(async (articleId) => {
    const article = articles.find(a => a.id === articleId);
    if (!article || isDetailLoading) return; // Prevent opening if already loading

    setSelectedArticle(article);
    setIsDetailLoading(true);
    setDetailData(null); // Reset previous details

    console.log(`Fetching details for article: ${article.title}`);
    // The API endpoint URL is still /summary, but fetches both summary and explanation
    const result = await fetchSummary(articleId); // result = { summary, explanation, error }
    console.log("Detail result:", result);

    // Check result structure before setting state
    if (result && (result.summary !== undefined || result.explanation !== undefined || result.error !== undefined)) {
        setDetailData(result);
    } else {
        // Handle unexpected API response structure
        console.error("Unexpected API response structure for details:", result);
        setDetailData({ summary: null, explanation: null, error: "Invalid response from server." });
        showNotification("Received an invalid response while fetching details.", "error", 5000);
    }

    setIsDetailLoading(false);

    // Optionally show notification only if there was an error reported by the backend
    if (result?.error) {
        showNotification(`Error fetching details: ${result.error}`, "error", 5000);
    }
  }, [articles, isDetailLoading, showNotification]); // Add isDetailLoading dependency


  const handleCloseModal = () => {
    setSelectedArticle(null);
    setDetailData(null);
  };

  // Handler for clearing data
  const handleClearData = async () => {
      if (window.confirm("Are you sure you want to permanently delete ALL stored articles? This action cannot be undone.")) {
          console.warn("Attempting to clear all article data...");
          try {
              const response = await clearAllArticles();
              showNotification(`Successfully cleared ${response.articles_cleared} articles.`, "success");
              loadArticles(false); // Refresh the list (should be empty), no success message needed
          } catch (err) {
              console.error("Failed to clear articles:", err);
              showNotification(`Failed to clear articles: ${err.message}`, "error", 5000);
          }
      }
  };

  // --- Render Logic ---
  return (
    <div className={`app ${isDarkMode ? 'dark-mode' : ''}`}>
      <Header
        isDarkMode={isDarkMode}
        toggleDarkMode={toggleDarkMode}
        onScrape={handleScrape}
        isScraping={isScraping}
        onClear={handleClearData}
      />
      <main>
        <ArticleList
           articles={articles}
           onGetSummary={handleShowDetails} // Pass the correct handler for card clicks
           isLoading={isLoadingArticles}
           error={articlesError}
        />
      </main>

      {/* Render Detail Modal (previously SummaryModal) */}
      {selectedArticle && (
          <SummaryModal
            show={selectedArticle !== null}
            onClose={handleCloseModal}
            detailData={detailData} // Pass the object with { summary, explanation, error }
            isLoading={isDetailLoading}
            articleTitle={selectedArticle.title}
          />
      )}

      <Notification
            message={notification.message}
            type={notification.type}
            show={notification.show}
       />

       {/* Optional Simple Footer */}
       <footer style={{ textAlign: 'center', padding: '20px', marginTop: 'auto', fontSize: '0.9em', opacity: 0.6 }}>
           Newsify Demo © {new Date().getFullYear()}
       </footer>
    </div>
  );
}

export default App;