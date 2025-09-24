// src/components/SummaryCards.js
import React from "react";

/**
 * Displays summary cards for key metrics (Total Patients, AI Predictions, Accuracy Rate, Flagged Cases).
 * Accepts a `summary` object with numeric/stat fields.
 */
function SummaryCards({ summary }) {
  if (!summary) return null;
  return (
    <div className="row mb-4">
      <div className="col-md-3 col-6 mb-3">
        <div className="card text-center shadow-sm">
          <div className="card-body">
            <h6 className="card-title">Total Patients</h6>
            <p className="h4 mb-0">{summary.totalPatients}</p>
          </div>
        </div>
      </div>
      <div className="col-md-3 col-6 mb-3">
        <div className="card text-center shadow-sm">
          <div className="card-body">
            <h6 className="card-title">AI Predictions</h6>
            <p className="h4 mb-0">{summary.aiPredictions}</p>
          </div>
        </div>
      </div>
      <div className="col-md-3 col-6 mb-3">
        <div className="card text-center shadow-sm">
          <div className="card-body">
            <h6 className="card-title">Accuracy Rate</h6>
            <p className="h4 mb-0">{summary.accuracyRate}%</p>
          </div>
        </div>
      </div>
      <div className="col-md-3 col-6 mb-3">
        <div className="card text-center shadow-sm">
          <div className="card-body">
            <h6 className="card-title">Flagged Cases</h6>
            <p className="h4 mb-0">{summary.flaggedCases}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SummaryCards;
