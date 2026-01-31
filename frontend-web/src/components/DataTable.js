import React from 'react';
import './DataTable.css';

function DataTable({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="data-table-container">
        <h2>Equipment Data</h2>
        <p>No data available. Please upload a CSV file.</p>
      </div>
    );
  }

  return (
    <div className="data-table-container">
      <h2>Equipment Data Table</h2>
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Equipment Name</th>
              <th>Type</th>
              <th>Flowrate</th>
              <th>Pressure</th>
              <th>Temperature</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.id}>
                <td>{item.equipment_name}</td>
                <td>{item.equipment_type}</td>
                <td>{item.flowrate.toFixed(2)}</td>
                <td>{item.pressure.toFixed(2)}</td>
                <td>{item.temperature.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
