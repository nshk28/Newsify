import React from 'react';
import PropTypes from 'prop-types';
import ArticleItem from './ArticleItem';

// Helper function to group articles by category
const groupArticlesByCategory = (articles) => {
  if (!Array.isArray(articles) || articles.length === 0) {
    return {};
  }
  // Ensure articles are sorted by impact score descending *before* grouping
  // The backend already sorts, but this ensures it if the prop changes unexpectedly
  const sortedArticles = [...articles].sort((a, b) => (b.impact_score ?? 0) - (a.impact_score ?? 0));

  return sortedArticles.reduce((acc, article) => {
    const category = article.category || 'Uncategorized'; // Fallback category
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(article);
    return acc;
  }, {});
};

// Define a preferred order for categories for consistent display
const CATEGORY_ORDER = ["business", "world", "tech", "science", "entertainment", "sports", "Uncategorized"];

function ArticleList({ articles, onGetSummary, isLoading, error }) {

  // Loading state display
  if (isLoading) {
    // Provide a more visually engaging loader if desired (e.g., spinner component)
    return <div className="loading-indicator">Fetching articles... Please wait.</div>;
  }

  // Error state display
  if (error) {
    return <div className="error-message">Error loading articles: {error.message || 'Could not fetch data from the server.'} Please try again later.</div>;
  }

  // Group articles after loading and no error
  const groupedArticles = groupArticlesByCategory(articles);
  const categories = Object.keys(groupedArticles).sort((a, b) => {
      // Sort categories based on predefined order, put unknown ones last alphabetically
      const indexA = CATEGORY_ORDER.indexOf(a.toLowerCase());
      const indexB = CATEGORY_ORDER.indexOf(b.toLowerCase());

      if (indexA === -1 && indexB === -1) return a.localeCompare(b); // Both unknown, sort alphabetically
      if (indexA === -1) return 1; // Put unknown 'a' after known 'b'
      if (indexB === -1) return -1; // Put unknown 'b' after known 'a'
      return indexA - indexB; // Sort by predefined index
  });

  // Empty state display (after loading, no error, but no articles)
  if (categories.length === 0) {
    return <div className="loading-indicator">No articles found. Try the "Fetch Latest News" button to populate the list.</div>;
  }

  // Render grouped articles
  return (
    <div className="articles-container">
      {categories.map((category) => (
        <section key={category} className="category-section" aria-labelledby={`category-heading-${category}`}>
          {/* Accessible heading for the category section */}
          <h2 id={`category-heading-${category}`} className="category-heading">
            {category.charAt(0).toUpperCase() + category.slice(1)} News
          </h2>
          <div className="article-list">
            {/* Render articles within this category */}
            {groupedArticles[category].map((article) => (
              <ArticleItem
                 key={article.id} // Use unique article ID as key
                 article={article}
                 onGetSummary={onGetSummary}
               />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

ArticleList.propTypes = {
  articles: PropTypes.arrayOf(PropTypes.object).isRequired, // Expect an array of article objects
  onGetSummary: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
  error: PropTypes.instanceOf(Error), // Expect null or an Error object
};

export default ArticleList;
