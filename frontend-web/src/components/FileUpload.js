import React, { useRef } from 'react';
import './FileUpload.css';

function FileUpload({ onUpload, loading }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    console.log('File selected:', file);
    if (file) {
      onUpload(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload-container">
      <h2>Upload CSV File</h2>
      <div className="upload-area" onClick={handleClick}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          disabled={loading}
        />
        <div className="upload-content">
          {loading ? (
            <div className="loading-spinner">Uploading...</div>
          ) : (
            <>
              <div className="upload-icon">📁</div>
              <p>Click to upload CSV file</p>
              <p className="upload-hint">Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default FileUpload;
