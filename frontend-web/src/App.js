import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import './App.css';
import FileUpload from './components/FileUpload';
import DataTable from './components/DataTable';
import SummaryStats from './components/SummaryStats';
import Charts from './components/Charts';
import History from './components/History';
import Login from './components/Login';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

const getStoredCredentials = () => {
  try {
    const stored = localStorage.getItem('auth_credentials');
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

const storeCredentials = (username, password) => {
  localStorage.setItem('auth_credentials', JSON.stringify({ username, password }));
};

const clearCredentials = () => localStorage.removeItem('auth_credentials');

function AppContent() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [equipmentData, setEquipmentData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const getAuthHeaders = () => {
    return {
      'Authorization': `Basic ${btoa(`${username}:${password}`)}`,
    };
  };

  const loadSummary = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/summary/`, { headers: getAuthHeaders() });
      setSummary(res.ok ? await res.json() : null);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };

  const loadData = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/data/`, { headers: getAuthHeaders() });
      setEquipmentData(res.ok ? await res.json() : []);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/history/`, { headers: getAuthHeaders() });
      if (res.ok) setHistory(await res.json());
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const loadInitialData = async () => {
    try {
      await Promise.all([
        loadSummary(),
        loadData(),
        loadHistory(),
      ]);
    } catch (err) {
      setError('Failed to load data');
    }
  };

  const verifyAuth = useCallback(async (user, pass) => {
    try {
      const res = await fetch(`${API_BASE_URL}/history/`, {
        headers: { 'Authorization': `Basic ${btoa(`${user}:${pass}`)}` },
      });
      if (!res.ok) return false;
      setIsAuthenticated(true);
      setUsername(user);
      setPassword(pass);
      storeCredentials(user, pass);
      loadInitialData();
      return true;
    } catch {
      return false;
    }
  }, []);


  useEffect(() => {
    const stored = getStoredCredentials();
    if (stored) {
      setUsername(stored.username);
      setPassword(stored.password);
      verifyAuth(stored.username, stored.password);
    }
  }, [verifyAuth]);


  const handleLogin = useCallback(async (e) => {
    e.preventDefault();
    setError(null);
    const ok = await verifyAuth(username, password);
    if (ok) navigate('/dashboard');
    else setError('Invalid credentials. Please check if the backend is running and credentials are correct.');
  }, [username, password, navigate, verifyAuth]);


  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername('');
    setPassword('');
    setEquipmentData([]);
    setSummary(null);
    setHistory([]);
    clearCredentials();
    navigate('/login');
  };

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });

      if (response.ok) {
        await response.json();
        await loadInitialData();
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Upload failed');
      }
    } catch (err) {
      setError('Upload failed. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async (datasetId = null) => {
    try {
      const url = datasetId ? `${API_BASE_URL}/pdf/${datasetId}/` : `${API_BASE_URL}/pdf/`;
      const res = await fetch(url, { headers: getAuthHeaders() });
      if (!res.ok) { setError('Failed to generate PDF'); return; }
      const blob = await res.blob();
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `equipment_report_${datasetId || 'latest'}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    } catch {
      setError('Failed to generate PDF');
    }
  };

  const Dashboard = () => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    return (
      <div className="App">
        <header className="App-header">
          <h1>Chemical Equipment Parameter Visualizer</h1>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </header>

        <div className="container">
          {error && (
            <div className="error-message">
              {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          <FileUpload onUpload={handleFileUpload} loading={loading} />

          {summary && (
            <>
              <SummaryStats summary={summary} />
              <div className="pdf-button-container">
                <button onClick={() => handleGeneratePDF()} className="pdf-btn">
                  Generate PDF Report
                </button>
              </div>
              <Charts data={equipmentData} summary={summary} />
              <DataTable data={equipmentData} />
            </>
          )}

          <History
            history={history}
            onSelectDataset={async (datasetId) => {
              const headers = getAuthHeaders();
              const dataRes = await fetch(`${API_BASE_URL}/data/${datasetId}/`, { headers });
              const summaryRes = await fetch(`${API_BASE_URL}/summary/${datasetId}/`, { headers });
              if (dataRes.ok) setEquipmentData(await dataRes.json());
              if (summaryRes.ok) setSummary(await summaryRes.json());
            }}
            onGeneratePDF={handleGeneratePDF}
            getAuthHeaders={getAuthHeaders}
          />
        </div>
      </div>
    );
  };

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/dashboard" replace /> : (
          <Login
            username={username}
            password={password}
            setUsername={setUsername}
            setPassword={setPassword}
            handleLogin={handleLogin}
            error={error}
          />
        )
      } />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
