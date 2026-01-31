import React from 'react';
import './History.css';

function History({ history, onSelectDataset, onGeneratePDF, getAuthHeaders }) {
  if (!history || history.length === 0) {
    return (
      <div className="history-container">
        <h2>Upload History</h2>
        <p>No upload history available.</p>
      </div>
    );
  }

  return (
    <div className="history-container">
      <h2>Upload History (Last 5 Datasets)</h2>
      <div className="history-list">
        {history.map((dataset) => (
          <div key={dataset.id} className="history-item">
            <div className="history-info">
              <h3>{dataset.filename}</h3>
              <p className="history-date">
                Uploaded: {new Date(dataset.uploaded_at).toLocaleString()}
              </p>
              <div className="history-stats">
                <span>Count: {dataset.total_count}</span>
                <span>Avg Flowrate: {dataset.avg_flowrate.toFixed(2)}</span>
                <span>Avg Pressure: {dataset.avg_pressure.toFixed(2)}</span>
                <span>Avg Temperature: {dataset.avg_temperature.toFixed(2)}</span>
              </div>
            </div>
            <div className="history-actions">
              <button
                onClick={() => onSelectDataset(dataset.id)}
                className="history-btn view-btn"
              >
                View
              </button>
              <button
                onClick={() => onGeneratePDF(dataset.id)}
                className="history-btn pdf-btn"
              >
                PDF
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default History;
