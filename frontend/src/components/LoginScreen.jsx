import React, { useState } from 'react';

export default function LoginScreen({ onLoginSuccess }) {
  const [email, setEmail] = useState('admin@demo.com');
  const [password, setPassword] = useState('demopassword123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Authentication failed');
      }

      const authData = await response.json();
      onLoginSuccess(authData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (roleEmail) => {
    setEmail(roleEmail);
    setPassword('demopassword123');
  };

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="login-header">
          <div className="logo-badge">SIH26011</div>
          <h2>3D ULPIN Cadastre Portal</h2>
          <p>Vertical Property Mapping & Spatial Conflict Detection System</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. admin@demo.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In to 3D Cadastre'}
          </button>
        </form>

        <div className="demo-accounts">
          <span className="demo-accounts-title">Quick Demo Login Accounts:</span>
          <div className="demo-btns-grid">
            <button
              type="button"
              className={`demo-btn ${email === 'admin@demo.com' ? 'active' : ''}`}
              onClick={() => handleQuickLogin('admin@demo.com')}
            >
              <strong>Admin</strong>
              <small>admin@demo.com</small>
            </button>
            <button
              type="button"
              className={`demo-btn ${email === 'surveyor@demo.com' ? 'active' : ''}`}
              onClick={() => handleQuickLogin('surveyor@demo.com')}
            >
              <strong>Surveyor</strong>
              <small>surveyor@demo.com</small>
            </button>
            <button
              type="button"
              className={`demo-btn ${email === 'citizen@demo.com' ? 'active' : ''}`}
              onClick={() => handleQuickLogin('citizen@demo.com')}
            >
              <strong>Citizen</strong>
              <small>citizen@demo.com</small>
            </button>
          </div>
        </div>

        <div className="login-footer">
          <span>Target Locality: Bharati Vidyapeeth's College of Engineering (BVCOE), New Delhi</span>
        </div>
      </div>
    </div>
  );
}
