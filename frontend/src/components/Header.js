import React from 'react';
import PropTypes from 'prop-types';

function Header({ isDarkMode, toggleDarkMode, onScrape, isScraping, onClear }) {
  return (
    <header className="header">
      <h1>Newsify ✨</h1>
      <div className="header-controls">
        <button
          onClick={onScrape}
          disabled={isScraping}
          title={isScraping ? "Scraping in progress..." : "Fetch latest articles from the web"}
        >
          {isScraping ? 'Scraping...' : 'Fetch Latest News'}
        </button>
        <button
            onClick={toggleDarkMode}
            title={`Switch to ${isDarkMode ? 'Light' : 'Dark'} Mode`}
         >
          {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
         {/* Optional Clear Button - Use with Caution! */}
         {onClear && ( // Only render if onClear prop is provided
            <button
                onClick={onClear}
                disabled={isScraping} // Disable if scraping
                style={{ backgroundColor: 'var(--error-color)', marginLeft: '10px' }}
                title="Permanently delete all stored articles"
            >
               Clear All Data
            </button>
         )}
      </div>
    </header>
  );
}

Header.propTypes = {
  isDarkMode: PropTypes.bool.isRequired,
  toggleDarkMode: PropTypes.func.isRequired,
  onScrape: PropTypes.func.isRequired,
  isScraping: PropTypes.bool.isRequired,
  onClear: PropTypes.func, // Make onClear optional
};


export default Header;
