// frontend/src/components/SummaryModal.js

import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';

// Component now expects detailData = { summary, explanation, error }
function SummaryModal({ show, onClose, detailData, isLoading, articleTitle }) {
  const modalRef = useRef(null);

  // Effect for Escape key and focus management
  useEffect(() => {
    const handleEsc = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    if (show) {
      document.addEventListener('keydown', handleEsc);
      setTimeout(() => modalRef.current?.focus(), 0); // Focus modal on open
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
    };
  }, [show, onClose]);

  if (!show) return null; // Don't render if not visible

  // Extract data for easier access, provide defaults
  const { summary = null, explanation = null, error = null } = detailData || {};

  return (
    <div
        className="modal-overlay"
        onClick={onClose}
        role="dialog"
        aria-modal="true"
        aria-labelledby="summary-modal-title"
     >
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        ref={modalRef}
        tabIndex="-1" // Make modal focusable
      >
        <button
          className="modal-close-button"
          onClick={onClose}
          aria-label="Close article details"
        >
          ×
        </button>

        {/* Modal Title */}
        <h2 id="summary-modal-title">
          Details: {articleTitle || 'Article'}
        </h2>

        {/* Loading State */}
        {isLoading && (
            <div className="loading-indicator">Generating details from AI... Please wait.</div>
        )}

        {/* Error State (display first if present) */}
        {!isLoading && error && (
            <div className="error-message">
                <strong>Error retrieving details:</strong><br />
                {error}
            </div>
        )}

        {/* Content Display (only if not loading and no critical error preventing display) */}
        {!isLoading && !error && (
            <>
                {/* Concise Summary Section */}
                {summary ? (
                    <>
                        <h3 style={{ marginTop: '20px', marginBottom: '10px', borderBottom: '1px solid var(--card-border)', paddingBottom: '5px' }}>Concise Summary</h3>
                        <p className="summary-text">{summary}</p>
                    </>
                ) : (
                    <p style={{ fontStyle: 'italic', opacity: 0.7, marginTop: '20px' }}>Concise summary could not be generated or is unavailable.</p>
                )}

                {/* In-Depth Explanation Section */}
                {explanation ? (
                     <>
                        <h3 style={{ marginTop: '25px', marginBottom: '10px', borderBottom: '1px solid var(--card-border)', paddingBottom: '5px' }}>In-Depth Explanation</h3>
                        <p className="summary-text">{explanation}</p> {/* Can reuse styling */}
                    </>
                ) : (
                     <p style={{ fontStyle: 'italic', opacity: 0.7, marginTop: '25px' }}>In-depth explanation could not be generated or is unavailable.</p>
                )}
            </>
        )}

        {/* Fallback if not loading, no error, but somehow no content */}
         {!isLoading && !error && !summary && !explanation && (
              <p>Details are currently unavailable for this article.</p>
         )}

      </div>
    </div>
  );
}

SummaryModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  // Updated prop type: expects an object or null
  detailData: PropTypes.shape({
    summary: PropTypes.string,
    explanation: PropTypes.string,
    error: PropTypes.string,
  }),
  isLoading: PropTypes.bool.isRequired,
  articleTitle: PropTypes.string,
};

SummaryModal.defaultProps = {
  detailData: null, // Default to null
  articleTitle: 'Article',
};

export default SummaryModal;