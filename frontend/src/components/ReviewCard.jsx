import React from "react";

export default function ReviewCard({ review }) {
  return (
    <div className="review-card">
      <div className="review-header">
        <strong className="review-username">{review.username || "Anonymous"}</strong>
        <div className="review-date">{new Date(review.created_at).toLocaleString()}</div>
      </div>

      <div className="review-content">
        <div className="review-rating-display">
          <span className="stars">{"⭐".repeat(review.rating || 5)}</span>
          <span className="rating-text">{review.rating || 5}/5</span>
        </div>
        <div className="review-comment">{review.comment || ""}</div>
      </div>
    </div>
  );
}
