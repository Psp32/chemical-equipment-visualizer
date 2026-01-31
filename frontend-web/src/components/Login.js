import React from 'react';
import './Login.css';

export default function Login({ username, password, setUsername, setPassword, handleLogin, error }) {
  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Chemical Equipment Visualizer</h2>
        <p className="login-subtitle">Please login to continue</p>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              placeholder="Enter username"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              placeholder="Enter password"
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-btn">Login</button>
        </form>
        <p className="login-note">Default credentials: admin/admin (create via Django admin)</p>
      </div>
    </div>
  );
}
