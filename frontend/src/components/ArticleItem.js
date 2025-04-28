import React from 'react';
import PropTypes from 'prop-types';

// Simple placeholder image SVG (better than text for layout)
const PLACEHOLDER_IMAGE_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 9'%3E%3Crect width='16' height='9' fill='%23cccccc'/%3E%3Ctext x='8' y='5' text-anchor='middle' dy='.3em' font-family='sans-serif' font-size='1' fill='%23555555'%3ENo Image%3C/text%3E%3C/svg%3E";

// Helper to get impact score CSS class
function getImpactClass(score) {
    if (score >= 75) return 'impact-high';
    if (score >= 45) return 'impact-medium'; // Adjusted threshold
    return 'impact-low';
}

// Helper to safely parse URL hostname
function getHostname(urlString) {
    try {
        if (!urlString) return 'N/A';
        const url = new URL(urlString);
        // Remove 'www.' if present for cleaner display
        return url.hostname.replace(/^www\./, '');
    } catch (e) {
        console.warn(`Invalid URL for hostname extraction: ${urlString}`);
        return 'Invalid Source';
    }
}

function ArticleItem({ article, onGetSummary }) {

  // Handle image loading errors by replacing with placeholder
  const handleImageError = (e) => {
      if (e.target.src !== PLACEHOLDER_IMAGE_SVG) {
          e.target.onerror = null; // Prevent potential infinite loop
          e.target.src = PLACEHOLDER_IMAGE_SVG;
          e.target.classList.add('placeholder-image'); // Add class for specific styling if needed
      }
  };

  // Format date string for display (very basic)
  const formatDate = (dateString) => {
      if (!dateString || dateString === "Date Not Available") {
          return "N/A";
      }
      try {
          // Attempt to create a date object - handles ISO 8601 well
          const date = new Date(dateString);
          // Check if the date is valid
          if (isNaN(date.getTime())) {
              // If invalid, return the original string (might be 'YYYY-MM-DD' or other formats)
              return dateString;
          }
          // Format to locale date string (e.g., "1/25/2024")
          return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
      } catch (e) {
          // If any error during parsing, return original string
          console.warn(`Could not parse date: ${dateString}`);
          return dateString;
      }
  };

  const hostname = getHostname(article.source_url);

  return (
    <div className="article-item">
       <img
            src={article.image_url || PLACEHOLDER_IMAGE_SVG}
            alt={`Image for ${article.title || 'article'}`}
            className="article-image" // Placeholder class added dynamically by onError
            onError={handleImageError}
            loading="lazy" // Add lazy loading for images below the fold
         />
      <div className="article-content-wrapper">
        <h3>{article.title || 'No Title Provided'}</h3>
        <div className="article-meta">
           <span title={article.author}><span className="label">Author:</span> {article.author || 'Unknown'}</span>
           {/* Link the source hostname */}
           <span title={article.source_url}>
                <span className="label">Source:</span>
                <a href={article.source_url} target="_blank" rel="noopener noreferrer">{hostname}</a>
            </span>
           <span><span className="label">Published:</span> {formatDate(article.published_time)}</span>
           <span><span className="label">Category:</span> {article.category || 'N/A'}</span>
        </div>
        <span className={`impact-score ${getImpactClass(article.impact_score)}`}>
            Impact: {article.impact_score}
        </span>
      </div>
      <div className="article-actions">
        <button onClick={() => onGetSummary(article.id)} title={`Get AI summary for ${article.title}`}>
           View Summary
        </button>
      </div>
    </div>
  );
}

ArticleItem.propTypes = {
  article: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string,
    author: PropTypes.string,
    source_url: PropTypes.string.isRequired,
    published_time: PropTypes.string,
    image_url: PropTypes.string,
    category: PropTypes.string,
    impact_score: PropTypes.number.isRequired,
    // Note: content and summary are not needed directly in the item display
  }).isRequired,
  onGetSummary: PropTypes.func.isRequired,
};

export default ArticleItem;
