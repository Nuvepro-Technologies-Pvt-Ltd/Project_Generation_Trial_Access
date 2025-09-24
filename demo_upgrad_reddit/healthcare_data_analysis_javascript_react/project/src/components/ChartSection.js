// src/components/ChartSection.js
import React from "react";

/**
 * Renders simple Bootstrap progress bar charts for visualizing analytics.
 * Accepts an array of chart data objects ({ id, label, percentage }).
 */
function ChartSection({ charts }) {
  if (!charts) return null;
  return (
    <div className="row mb-4">
      {charts.map((chart) => (
        <div className="col-md-6 mb-3" key={chart.id}>
          <div className="card shadow-sm">
            <div className="card-body">
              <h6 className="card-title">{chart.label}</h6>
              <div className="progress">
                <div
                  className="progress-bar"
                  role="progressbar"
                  style={{ width: `${chart.percentage}%` }}
                  aria-valuenow={chart.percentage}
                  aria-valuemin="0"
                  aria-valuemax="100"
                >
                  {chart.percentage}%
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ChartSection;
