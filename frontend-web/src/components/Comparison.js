import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie, Radar } from 'react-chartjs-2';
import './Comparison.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  RadialLinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function Comparison({ history, getAuthHeaders }) {
  const [selectedDatasets, setSelectedDatasets] = useState({ dataset1: null, dataset2: null });
  const [comparisonData, setComparisonData] = useState({ data1: null, data2: null, summary1: null, summary2: null });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
      ? 'http://localhost:8000/api' 
      : 'https://chemical-equipment-visualizer-vcel.onrender.com/api');

  const loadDatasetData = async (datasetId, datasetNumber) => {
    try {
      const res = await fetch(`${API_BASE_URL}/data/${datasetId}/`, { headers: getAuthHeaders() });
      const summaryRes = await fetch(`${API_BASE_URL}/summary/${datasetId}/`, { headers: getAuthHeaders() });
      
      if (res.ok && summaryRes.ok) {
        const data = await res.json();
        const summary = await summaryRes.json();
        
        setComparisonData(prev => ({
          ...prev,
          [`data${datasetNumber}`]: data,
          [`summary${datasetNumber}`]: summary
        }));
      }
    } catch (err) {
      console.error(`Failed to load dataset ${datasetNumber}:`, err);
      setError(`Failed to load dataset ${datasetNumber}`);
    }
  };

  const handleDatasetSelect = async (datasetId, datasetNumber) => {
    setLoading(true);
    setError(null);
    
    setSelectedDatasets(prev => ({ ...prev, [`dataset${datasetNumber}`]: datasetId }));
    await loadDatasetData(datasetId, datasetNumber);
    
    setLoading(false);
  };

  const clearSelection = (datasetNumber) => {
    setSelectedDatasets(prev => ({ ...prev, [`dataset${datasetNumber}`]: null }));
    setComparisonData(prev => ({
      ...prev,
      [`data${datasetNumber}`]: null,
      [`summary${datasetNumber}`]: null
    }));
  };

  const canCompare = comparisonData.data1 && comparisonData.data2 && 
                   comparisonData.summary1 && comparisonData.summary2;

  const getAdvancedMetrics = () => {
    if (!canCompare) return null;

    const { summary1, summary2, data1, data2 } = comparisonData;
    
    const calculateStdDev = (data, field) => {
      const values = data.map(item => item[field]);
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
      return Math.sqrt(variance);
    };

    const stdDev1 = {
      flowrate: calculateStdDev(data1, 'flowrate'),
      pressure: calculateStdDev(data1, 'pressure'),
      temperature: calculateStdDev(data1, 'temperature'),
    };

    const stdDev2 = {
      flowrate: calculateStdDev(data2, 'flowrate'),
      pressure: calculateStdDev(data2, 'pressure'),
      temperature: calculateStdDev(data2, 'temperature'),
    };

    const getRange = (data, field) => {
      const values = data.map(item => item[field]);
      return { min: Math.min(...values), max: Math.max(...values) };
    };

    const range1 = {
      flowrate: getRange(data1, 'flowrate'),
      pressure: getRange(data1, 'pressure'),
      temperature: getRange(data1, 'temperature'),
    };

    const range2 = {
      flowrate: getRange(data2, 'flowrate'),
      pressure: getRange(data2, 'pressure'),
      temperature: getRange(data2, 'temperature'),
    };

    const calculatePerformanceScore = (summary) => {
      const flowScore = Math.min(summary.avg_flowrate / 5, 1) * 100;
      const pressureScore = Math.min(summary.avg_pressure / 50, 1) * 100;
      const tempScore = Math.min(summary.avg_temperature / 200, 1) * 100;
      return (flowScore + pressureScore + tempScore) / 3;
    };

    return {
      flowrateDiff: summary1.avg_flowrate - summary2.avg_flowrate,
      pressureDiff: summary1.avg_pressure - summary2.avg_pressure,
      temperatureDiff: summary1.avg_temperature - summary2.avg_temperature,
      countDiff: summary1.total_count - summary2.total_count,
      flowratePercentChange: ((summary1.avg_flowrate - summary2.avg_flowrate) / summary2.avg_flowrate * 100).toFixed(2),
      pressurePercentChange: ((summary1.avg_pressure - summary2.avg_pressure) / summary2.avg_pressure * 100).toFixed(2),
      temperaturePercentChange: ((summary1.avg_temperature - summary2.avg_temperature) / summary2.avg_temperature * 100).toFixed(2),
      stdDev1, stdDev2, range1, range2,
      performanceScore1: calculatePerformanceScore(summary1),
      performanceScore2: calculatePerformanceScore(summary2),
      efficiency1: (summary1.avg_flowrate / summary1.avg_pressure).toFixed(2),
      efficiency2: (summary2.avg_flowrate / summary2.avg_pressure).toFixed(2),
    };
  };

  const metrics = getAdvancedMetrics();

  const getComparisonChartData = () => {
    if (!canCompare) return null;

    const { data1, data2, summary1, summary2 } = comparisonData;
    
    const types1 = Object.keys(summary1.equipment_type_distribution);
    const types2 = Object.keys(summary2.equipment_type_distribution);
    const commonTypes = [...new Set([...types1, ...types2])];

    const typeComparisonData = {
      labels: commonTypes,
      datasets: [
        {
          label: 'Dataset 1',
          data: commonTypes.map(type => summary1.equipment_type_distribution[type] || 0),
          backgroundColor: 'rgba(46, 107, 240, 0.8)',
          borderColor: '#2E6BF0',
          borderWidth: 2,
        },
        {
          label: 'Dataset 2',
          data: commonTypes.map(type => summary2.equipment_type_distribution[type] || 0),
          backgroundColor: 'rgba(96, 165, 250, 0.8)',
          borderColor: '#60a5fa',
          borderWidth: 2,
        },
      ],
    };

    const parametersData = {
      labels: ['Avg Flowrate', 'Avg Pressure', 'Avg Temperature'],
      datasets: [
        {
          label: 'Dataset 1',
          data: [summary1.avg_flowrate, summary1.avg_pressure, summary1.avg_temperature],
          backgroundColor: 'rgba(46, 107, 240, 0.8)',
          borderColor: '#2E6BF0',
          borderWidth: 2,
        },
        {
          label: 'Dataset 2',
          data: [summary2.avg_flowrate, summary2.avg_pressure, summary2.avg_temperature],
          backgroundColor: 'rgba(96, 165, 250, 0.8)',
          borderColor: '#60a5fa',
          borderWidth: 2,
        },
      ],
    };

    const radarData = {
      labels: ['Flowrate', 'Pressure', 'Temperature', 'Equipment Count', 'Efficiency'],
      datasets: [
        {
          label: 'Dataset 1',
          data: [
            (summary1.avg_flowrate / 500) * 100,
            (summary1.avg_pressure / 50) * 100,
            (summary1.avg_temperature / 200) * 100,
            (summary1.total_count / 25) * 100,
            (metrics.efficiency1 / 10) * 100,
          ],
          backgroundColor: 'rgba(46, 107, 240, 0.2)',
          borderColor: '#2E6BF0',
          borderWidth: 2,
          pointBackgroundColor: '#2E6BF0',
        },
        {
          label: 'Dataset 2',
          data: [
            (summary2.avg_flowrate / 500) * 100,
            (summary2.avg_pressure / 50) * 100,
            (summary2.avg_temperature / 200) * 100,
            (summary2.total_count / 25) * 100,
            (metrics.efficiency2 / 10) * 100,
          ],
          backgroundColor: 'rgba(96, 165, 250, 0.2)',
          borderColor: '#60a5fa',
          borderWidth: 2,
          pointBackgroundColor: '#60a5fa',
        },
      ],
    };

    const stdDevData = {
      labels: ['Flowrate', 'Pressure', 'Temperature'],
      datasets: [
        {
          label: 'Dataset 1 Std Dev',
          data: [metrics.stdDev1.flowrate, metrics.stdDev1.pressure, metrics.stdDev1.temperature],
          backgroundColor: 'rgba(46, 107, 240, 0.8)',
          borderColor: '#2E6BF0',
          borderWidth: 2,
        },
        {
          label: 'Dataset 2 Std Dev',
          data: [metrics.stdDev2.flowrate, metrics.stdDev2.pressure, metrics.stdDev2.temperature],
          backgroundColor: 'rgba(96, 165, 250, 0.8)',
          borderColor: '#60a5fa',
          borderWidth: 2,
        },
      ],
    };

    const pieData1 = {
      labels: types1,
      datasets: [{
        data: types1.map(type => summary1.equipment_type_distribution[type]),
        backgroundColor: [
          '#2E6BF0', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe',
          '#1e40af', '#1d4ed8', '#2563eb', '#3b82f6'
        ],
        borderWidth: 2,
        borderColor: '#fff',
      }],
    };

    const pieData2 = {
      labels: types2,
      datasets: [{
        data: types2.map(type => summary2.equipment_type_distribution[type]),
        backgroundColor: [
          '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#f0f9ff',
          '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd'
        ],
        borderWidth: 2,
        borderColor: '#fff',
      }],
    };

    return { 
      typeComparisonData, 
      parametersData, 
      radarData, 
      stdDevData, 
      pieData1, 
      pieData2 
    };
  };

  const chartData = getComparisonChartData();

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: { size: 12 },
          padding: 15,
        },
      },
      title: {
        display: true,
        font: { size: 16, weight: 'bold' },
        padding: 15,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
      },
      x: {
        grid: { display: false },
      },
    },
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: {
        display: true,
        text: 'Performance Comparison',
        font: { size: 16, weight: 'bold' },
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        grid: { color: 'rgba(0, 0, 0, 0.05)' },
      },
    },
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      title: {
        display: true,
        font: { size: 14, weight: 'bold' },
      },
    },
  };

  if (!history || history.length < 2) {
    return (
      <div className="comparison-container">
        <div className="comparison-header">
          <h2>Advanced Dataset Comparison</h2>
          <p>Compare two datasets with detailed metrics and visualizations</p>
        </div>
        <div className="no-data">
          <div className="no-data-icon">📊</div>
          <h3>Need More Data</h3>
          <p>At least two datasets are required for comparison. Upload more CSV files to see detailed analysis.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="comparison-container">
      <div className="comparison-header">
        <h2>Advanced Dataset Comparison</h2>
        <p>Compare two datasets with detailed metrics and visualizations</p>
      </div>
      
      <div className="selection-section">
        <div className="dataset-selector">
          <div className="selector-header">
            <h3>Dataset 1</h3>
            <div className="dataset-badge primary">Primary</div>
          </div>
          <div className="selector-content">
            {selectedDatasets.dataset1 ? (
              <div className="selected-dataset">
                <div className="dataset-info">
                  <span className="dataset-name">{history.find(h => h.id === selectedDatasets.dataset1)?.filename}</span>
                  <span className="dataset-date">{new Date(history.find(h => h.id === selectedDatasets.dataset1)?.uploaded_at).toLocaleDateString()}</span>
                </div>
                <button onClick={() => clearSelection(1)} className="clear-btn">✕</button>
              </div>
            ) : (
              <select 
                onChange={(e) => e.target.value && handleDatasetSelect(parseInt(e.target.value), 1)}
                value=""
                className="dataset-select"
              >
                <option value="">Select first dataset...</option>
                {history.filter(h => h.id !== selectedDatasets.dataset2).map(dataset => (
                  <option key={dataset.id} value={dataset.id}>
                    {dataset.filename} ({new Date(dataset.uploaded_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        <div className="vs-divider">
          <span>VS</span>
        </div>

        <div className="dataset-selector">
          <div className="selector-header">
            <h3>Dataset 2</h3>
            <div className="dataset-badge secondary">Secondary</div>
          </div>
          <div className="selector-content">
            {selectedDatasets.dataset2 ? (
              <div className="selected-dataset">
                <div className="dataset-info">
                  <span className="dataset-name">{history.find(h => h.id === selectedDatasets.dataset2)?.filename}</span>
                  <span className="dataset-date">{new Date(history.find(h => h.id === selectedDatasets.dataset2)?.uploaded_at).toLocaleDateString()}</span>
                </div>
                <button onClick={() => clearSelection(2)} className="clear-btn">✕</button>
              </div>
            ) : (
              <select 
                onChange={(e) => e.target.value && handleDatasetSelect(parseInt(e.target.value), 2)}
                value=""
                className="dataset-select"
              >
                <option value="">Select second dataset...</option>
                {history.filter(h => h.id !== selectedDatasets.dataset1).map(dataset => (
                  <option key={dataset.id} value={dataset.id}>
                    {dataset.filename} ({new Date(dataset.uploaded_at).toLocaleDateString()})
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Analyzing datasets...</p>
        </div>
      )}
      {error && <div className="error-message">{error}</div>}

      {canCompare && metrics && (
        <>
          <div className="metrics-overview">
            <h3>Performance Overview</h3>
            <div className="overview-cards">
              <div className="overview-card">
                <div className="card-header">
                  <h4>Dataset 1</h4>
                  <div className="performance-score" style={{ color: '#2E6BF0' }}>
                    {metrics.performanceScore1.toFixed(1)}%
                  </div>
                </div>
                <div className="card-metrics">
                  <div className="metric">
                    <span>Efficiency</span>
                    <strong>{metrics.efficiency1}</strong>
                  </div>
                  <div className="metric">
                    <span>Equipment</span>
                    <strong>{comparisonData.summary1.total_count}</strong>
                  </div>
                </div>
              </div>

              <div className="overview-card">
                <div className="card-header">
                  <h4>Dataset 2</h4>
                  <div className="performance-score" style={{ color: '#60a5fa' }}>
                    {metrics.performanceScore2.toFixed(1)}%
                  </div>
                </div>
                <div className="card-metrics">
                  <div className="metric">
                    <span>Efficiency</span>
                    <strong>{metrics.efficiency2}</strong>
                  </div>
                  <div className="metric">
                    <span>Equipment</span>
                    <strong>{comparisonData.summary2.total_count}</strong>
                  </div>
                </div>
              </div>

              <div className="overview-card winner">
                <div className="card-header">
                  <h4>Winner</h4>
                  <div className="winner-badge">
                    {metrics.performanceScore1 > metrics.performanceScore2 ? 'Dataset 1' : 'Dataset 2'}
                  </div>
                </div>
                <div className="improvement">
                  <span>Performance Gap</span>
                  <strong>{Math.abs(metrics.performanceScore1 - metrics.performanceScore2).toFixed(1)}%</strong>
                </div>
              </div>
            </div>
          </div>

          <div className="detailed-metrics">
            <h3>Detailed Analysis</h3>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-header">
                  <h4>Flowrate Analysis</h4>
                  <div className={`metric-diff ${metrics.flowrateDiff >= 0 ? 'positive' : 'negative'}`}>
                    {metrics.flowrateDiff >= 0 ? '↑' : '↓'} {Math.abs(metrics.flowratePercentChange)}%
                  </div>
                </div>
                <div className="metric-values">
                  <div className="value-group">
                    <span className="label">Dataset 1</span>
                    <span className="value primary">{comparisonData.summary1.avg_flowrate.toFixed(2)}</span>
                  </div>
                  <div className="value-group">
                    <span className="label">Dataset 2</span>
                    <span className="value secondary">{comparisonData.summary2.avg_flowrate.toFixed(2)}</span>
                  </div>
                </div>
                <div className="metric-details">
                  <div className="detail-item">
                    <span>Std Dev</span>
                    <span>{metrics.stdDev1.flowrate.toFixed(2)} vs {metrics.stdDev2.flowrate.toFixed(2)}</span>
                  </div>
                  <div className="detail-item">
                    <span>Range</span>
                    <span>{metrics.range1.flowrate.min.toFixed(1)}-{metrics.range1.flowrate.max.toFixed(1)}</span>
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <h4>Pressure Analysis</h4>
                  <div className={`metric-diff ${metrics.pressureDiff >= 0 ? 'positive' : 'negative'}`}>
                    {metrics.pressureDiff >= 0 ? '↑' : '↓'} {Math.abs(metrics.pressurePercentChange)}%
                  </div>
                </div>
                <div className="metric-values">
                  <div className="value-group">
                    <span className="label">Dataset 1</span>
                    <span className="value primary">{comparisonData.summary1.avg_pressure.toFixed(2)}</span>
                  </div>
                  <div className="value-group">
                    <span className="label">Dataset 2</span>
                    <span className="value secondary">{comparisonData.summary2.avg_pressure.toFixed(2)}</span>
                  </div>
                </div>
                <div className="metric-details">
                  <div className="detail-item">
                    <span>Std Dev</span>
                    <span>{metrics.stdDev1.pressure.toFixed(2)} vs {metrics.stdDev2.pressure.toFixed(2)}</span>
                  </div>
                  <div className="detail-item">
                    <span>Range</span>
                    <span>{metrics.range1.pressure.min.toFixed(1)}-{metrics.range1.pressure.max.toFixed(1)}</span>
                  </div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <h4>Temperature Analysis</h4>
                  <div className={`metric-diff ${metrics.temperatureDiff >= 0 ? 'positive' : 'negative'}`}>
                    {metrics.temperatureDiff >= 0 ? '↑' : '↓'} {Math.abs(metrics.temperaturePercentChange)}%
                  </div>
                </div>
                <div className="metric-values">
                  <div className="value-group">
                    <span className="label">Dataset 1</span>
                    <span className="value primary">{comparisonData.summary1.avg_temperature.toFixed(2)}</span>
                  </div>
                  <div className="value-group">
                    <span className="label">Dataset 2</span>
                    <span className="value secondary">{comparisonData.summary2.avg_temperature.toFixed(2)}</span>
                  </div>
                </div>
                <div className="metric-details">
                  <div className="detail-item">
                    <span>Std Dev</span>
                    <span>{metrics.stdDev1.temperature.toFixed(2)} vs {metrics.stdDev2.temperature.toFixed(2)}</span>
                  </div>
                  <div className="detail-item">
                    <span>Range</span>
                    <span>{metrics.range1.temperature.min.toFixed(1)}-{metrics.range1.temperature.max.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {chartData && (
            <div className="enhanced-charts">
              <h3>Visual Analysis</h3>
              
              <div className="chart-row">
                <div className="chart-card large">
                  <h4>Performance Radar</h4>
                  <div className="chart-wrapper">
                    <Radar data={chartData.radarData} options={radarOptions} />
                  </div>
                </div>
              </div>

              <div className="chart-row">
                <div className="chart-card">
                  <h4>Equipment Type Distribution</h4>
                  <div className="chart-wrapper">
                    <Bar data={chartData.typeComparisonData} options={chartOptions} />
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Parameters Comparison</h4>
                  <div className="chart-wrapper">
                    <Bar data={chartData.parametersData} options={chartOptions} />
                  </div>
                </div>
              </div>

              <div className="chart-row">
                <div className="chart-card">
                  <h4>Data Variability (Std Dev)</h4>
                  <div className="chart-wrapper">
                    <Bar data={chartData.stdDevData} options={chartOptions} />
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Dataset 1 Distribution</h4>
                  <div className="chart-wrapper">
                    <Pie data={chartData.pieData1} options={pieOptions} />
                  </div>
                </div>
                <div className="chart-card">
                  <h4>Dataset 2 Distribution</h4>
                  <div className="chart-wrapper">
                    <Pie data={chartData.pieData2} options={pieOptions} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Comparison;
