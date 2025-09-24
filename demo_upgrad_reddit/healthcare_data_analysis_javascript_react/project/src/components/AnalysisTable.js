// src/components/AnalysisTable.js
import React from "react";

/**
 * Displays a table with patient-level and aggregate analytics.
 * Expects `tableData` array [{ id, patientName, predictedCondition, confidence, status }, ...].
 */
function AnalysisTable({ tableData }) {
  if (!tableData || !Array.isArray(tableData) || tableData.length === 0) {
    return (
      <div className="alert alert-info">No detailed results available.</div>
    );
  }
  return (
    <div className="card mb-4 shadow-sm">
      <div className="card-body">
        <h6 className="card-title mb-3">Detailed Analysis Results</h6>
        <div className="table-responsive">
          <table className="table table-bordered">
            <thead className="table-light">
              <tr>
                <th scope="col">Case ID</th>
                <th scope="col">Patient Name</th>
                <th scope="col">Predicted Condition</th>
                <th scope="col">Confidence (%)</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.patientName}</td>
                  <td>{row.predictedCondition}</td>
                  <td>{row.confidence}%</td>
                  <td>
                    <span className={`badge ${row.status === "Flagged" ? "bg-danger" : "bg-success"}`}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AnalysisTable;
