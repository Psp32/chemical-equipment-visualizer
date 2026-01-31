import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import './Charts.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function Charts({ data, summary }) {
  if (!data || data.length === 0 || !summary) return null;

  // Prepare data for charts
  const equipmentTypes = Object.keys(summary.equipment_type_distribution);
  const typeCounts = Object.values(summary.equipment_type_distribution);

  // Flowrate by equipment
  const flowrateData = data.map(item => ({
    label: item.equipment_name,
    value: item.flowrate,
  })).slice(0, 10); // Show top 10

  // Pressure by equipment
  const pressureData = data.map(item => ({
    label: item.equipment_name,
    value: item.pressure,
  })).slice(0, 10);

  // Temperature by equipment
  const temperatureData = data.map(item => ({
    label: item.equipment_name,
    value: item.temperature,
  })).slice(0, 10);

  // Pie chart data for equipment type distribution
  const pieData = {
    labels: equipmentTypes,
    datasets: [
      {
        label: 'Equipment Count',
        data: typeCounts,
        backgroundColor: [
          '#2E6BF0',
          '#2563eb',
          '#3b82f6',
          '#60a5fa',
          '#93c5fd',
          '#bfdbfe',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  // Bar chart for flowrate
  const flowrateBarData = {
    labels: flowrateData.map(item => item.label),
    datasets: [
      {
        label: 'Flowrate',
        data: flowrateData.map(item => item.value),
        backgroundColor: 'rgba(46, 107, 240, 0.8)',
        borderColor: '#2E6BF0',
        borderWidth: 1,
      },
    ],
  };

  // Line chart for pressure
  const pressureLineData = {
    labels: pressureData.map(item => item.label),
    datasets: [
      {
        label: 'Pressure',
        data: pressureData.map(item => item.value),
        borderColor: '#2E6BF0',
        backgroundColor: 'rgba(46, 107, 240, 0.1)',
        borderWidth: 2,
        fill: true,
      },
    ],
  };

  // Line chart for temperature
  const temperatureLineData = {
    labels: temperatureData.map(item => item.label),
    datasets: [
      {
        label: 'Temperature',
        data: temperatureData.map(item => item.value),
        borderColor: '#60a5fa',
        backgroundColor: 'rgba(96, 165, 250, 0.1)',
        borderWidth: 2,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Equipment Parameters',
      },
    },
  };

  return (
    <div className="charts-container">
      <h2>Data Visualization</h2>
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Equipment Type Distribution</h3>
          <div className="chart-wrapper">
            <Pie data={pieData} options={chartOptions} />
          </div>
        </div>
        <div className="chart-card">
          <h3>Flowrate by Equipment (Top 10)</h3>
          <div className="chart-wrapper">
            <Bar data={flowrateBarData} options={chartOptions} />
          </div>
        </div>
        <div className="chart-card">
          <h3>Pressure by Equipment (Top 10)</h3>
          <div className="chart-wrapper">
            <Line data={pressureLineData} options={chartOptions} />
          </div>
        </div>
        <div className="chart-card">
          <h3>Temperature by Equipment (Top 10)</h3>
          <div className="chart-wrapper">
            <Line data={temperatureLineData} options={chartOptions} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Charts;
