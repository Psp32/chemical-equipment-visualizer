import React from 'react';
import './SummaryStats.css';

function SummaryStats({ summary }) {
  if (!summary) return null;

  return (
    <div className="summary-stats">
      <h2>Summary Statistics</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Equipment</div>
          <div className="stat-value">{summary.total_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Flowrate</div>
          <div className="stat-value">{summary.avg_flowrate.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Pressure</div>
          <div className="stat-value">{summary.avg_pressure.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Temperature</div>
          <div className="stat-value">{summary.avg_temperature.toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
}

export default SummaryStats;
