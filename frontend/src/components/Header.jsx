import React from 'react';
import aakaarLogo from '../assets/aakaar-logo.jpeg';
import SearchBar from './SearchBar';

export default function Header({
  activeTab,
  setActiveTab,
  conflictsCount = 0,
  propertiesList = [],
  onSelectProperty,
  currentUser,
  onLogout,
}) {
  return (
    <header className="header">
      <div className="header-left">
        <div className="header-title" onClick={() => setActiveTab('map')} style={{ cursor: 'pointer' }}>
          <div className="aakaar-logo-badge header-logo-badge">
            <img src={aakaarLogo} alt="Aakaar Logo" className="aakaar-logo-img" />
          </div>
          <div className="header-text-group">
            <h1>Aakaar</h1>
            <span className="header-subtitle">Vertical Property Mapping & Spatial Conflict Detection System</span>
          </div>
        </div>

        <nav className="header-nav">
          <button
            className={`nav-tab ${activeTab === 'map' ? 'active' : ''}`}
            onClick={() => setActiveTab('map')}
          >
            3D Globe Map
          </button>
          <button
            className={`nav-tab ${activeTab === 'conflicts' ? 'active' : ''}`}
            onClick={() => setActiveTab('conflicts')}
          >
            Conflicts Dashboard
            {conflictsCount > 0 && (
              <span className="conflicts-counter">{conflictsCount}</span>
            )}
          </button>
          <button
            className={`nav-tab ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            Reports & Analytics
          </button>
          <button
            className={`nav-tab ${activeTab === 'generator' ? 'active' : ''}`}
            onClick={() => setActiveTab('generator')}
          >
            ULPIN Generator
          </button>
        </nav>
      </div>

      <div className="header-center">
        <SearchBar
          properties={propertiesList}
          onSelectProperty={onSelectProperty}
        />
      </div>

      <div className="header-right">
        <div className="header-doc-ref" title="Official Cadastral Document Reference ID">
          <span className="doc-ref-prefix">REF:</span>
          <span className="doc-ref-id">DL-BVCOE-2026</span>
        </div>

        {currentUser && (
          <div className="user-profile-badge">
            <span className={`user-role-pill role-${currentUser.role || 'citizen'}`}>
              {(currentUser.role || 'CITIZEN').toUpperCase()}
            </span>
            <span className="user-email">{currentUser.email}</span>
          </div>
        )}

        <button className="logout-btn" onClick={onLogout} title="Sign Out">
          Sign Out
        </button>
      </div>
    </header>
  );
}
