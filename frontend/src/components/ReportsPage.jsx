import React from 'react';

export default function ReportsPage({ summary, onRefresh }) {
  if (!summary) {
    return (
      <div className="reports-container">
        <div className="reports-loading">Loading Analytics Summary...</div>
      </div>
    );
  }

  const {
    parcels_total = 0,
    buildings_total = 0,
    properties_total = 0,
    properties_verified = 0,
    properties_conflict = 0,
    properties_unverified = 0,
    total_unresolved_conflicts = 0,
    conflicts_by_type = {}
  } = summary;

  const verifiedPercent = properties_total > 0 ? ((properties_verified / properties_total) * 100).toFixed(1) : 0;
  const conflictPercent = properties_total > 0 ? ((properties_conflict / properties_total) * 100).toFixed(1) : 0;

  const conflictEntries = [
    { type: 'boundary_violation', label: 'Boundary Violation', count: conflicts_by_type.boundary_violation || 0, color: '#ef4444' },
    { type: 'building_parcel_mismatch', label: 'Building-Parcel Mismatch', count: conflicts_by_type.building_parcel_mismatch || 0, color: '#3b82f6' },
    { type: 'overlap', label: '3D Spatial Overlap', count: conflicts_by_type.overlap || 0, color: '#f59e0b' },
    { type: 'floor_overlap', label: 'Floor Level Overlap', count: conflicts_by_type.floor_overlap || 0, color: '#ec4899' },
    { type: 'duplicate', label: 'Duplicate Property', count: conflicts_by_type.duplicate || 0, color: '#a855f7' }
  ];

  const maxConflictCount = Math.max(...conflictEntries.map(e => e.count), 1);

  return (
    <div className="reports-container">
      <div className="reports-header">
        <div>
          <h2>Cadastral Analytics & Spatial Audit Reports</h2>
          <p>Real-time vertical cadastre statistics and PostGIS topological validation metrics</p>
        </div>
        <button className="reports-refresh-btn" onClick={onRefresh}>
          Refresh Live Metrics
        </button>
      </div>

      {/* Top Level Summary Cards */}
      <div className="reports-cards-grid">
        <div className="report-card">
          <div className="card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
              <line x1="8" y1="2" x2="8" y2="18"></line>
              <line x1="16" y1="6" x2="16" y2="22"></line>
            </svg>
          </div>
          <div className="card-content">
            <span className="card-title">Total Land Parcels</span>
            <span className="card-number">{parcels_total}</span>
            <span className="card-sub">BVCOE Cadastral Zone</span>
          </div>
        </div>

        <div className="report-card">
          <div className="card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
              <line x1="9" y1="22" x2="9" y2="22.01"></line>
              <line x1="15" y1="22" x2="15" y2="22.01"></line>
              <line x1="9" y1="6" x2="9" y2="6.01"></line>
              <line x1="15" y1="6" x2="15" y2="6.01"></line>
              <line x1="9" y1="10" x2="9" y2="10.01"></line>
              <line x1="15" y1="10" x2="15" y2="10.01"></line>
              <line x1="9" y1="14" x2="9" y2="14.01"></line>
              <line x1="15" y1="14" x2="15" y2="14.01"></line>
            </svg>
          </div>
          <div className="card-content">
            <span className="card-title">Total Buildings</span>
            <span className="card-number">{buildings_total}</span>
            <span className="card-sub">Extruded Structures</span>
          </div>
        </div>

        <div className="report-card">
          <div className="card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
          </div>
          <div className="card-content">
            <span className="card-title">3D Property Units</span>
            <span className="card-number">{properties_total}</span>
            <span className="card-sub">Vertical Space Titles</span>
          </div>
        </div>

        <div className="report-card report-card-alert">
          <div className="card-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <div className="card-content">
            <span className="card-title">Active Conflict Logs</span>
            <span className="card-number">{total_unresolved_conflicts}</span>
            <span className="card-sub">Unresolved Spatial Issues</span>
          </div>
        </div>
      </div>

      {/* Analytics Sections */}
      <div className="reports-charts-grid">
        {/* Verification Status Breakdown */}
        <div className="analytics-box">
          <div className="analytics-box-header">
            <h3>Title Verification Distribution</h3>
            <span className="analytics-total">{properties_total} Units Total</span>
          </div>

          <div className="status-progress-bar">
            <div 
              className="progress-segment seg-verified" 
              style={{ width: `${verifiedPercent}%` }}
              title={`Verified: ${properties_verified} (${verifiedPercent}%)`}
            />
            <div 
              className="progress-segment seg-conflict" 
              style={{ width: `${conflictPercent}%` }}
              title={`Conflicts: ${properties_conflict} (${conflictPercent}%)`}
            />
          </div>

          <div className="status-breakdown-list">
            <div className="status-item">
              <div className="status-item-left">
                <span className="status-dot-lg" style={{ backgroundColor: '#22c55e' }} />
                <div>
                  <strong>Verified Titles</strong>
                  <small>Passed all geometric checks</small>
                </div>
              </div>
              <div className="status-item-right">
                <span className="status-count">{properties_verified}</span>
                <span className="status-pct">({verifiedPercent}%)</span>
              </div>
            </div>

            <div className="status-item">
              <div className="status-item-left">
                <span className="status-dot-lg" style={{ backgroundColor: '#ef4444' }} />
                <div>
                  <strong>Spatial Conflicts</strong>
                  <small>Requires survey adjudication</small>
                </div>
              </div>
              <div className="status-item-right">
                <span className="status-count">{properties_conflict}</span>
                <span className="status-pct">({conflictPercent}%)</span>
              </div>
            </div>

            <div className="status-item">
              <div className="status-item-left">
                <span className="status-dot-lg" style={{ backgroundColor: '#9ca3af' }} />
                <div>
                  <strong>Unverified / Pending</strong>
                  <small>Awaiting segmentation</small>
                </div>
              </div>
              <div className="status-item-right">
                <span className="status-count">{properties_unverified}</span>
                <span className="status-pct">(0.0%)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Conflict Type Breakdown */}
        <div className="analytics-box">
          <div className="analytics-box-header">
            <h3>Conflict Type Classification</h3>
            <span className="analytics-total">{total_unresolved_conflicts} Total Logs</span>
          </div>

          <div className="conflicts-bars-list">
            {conflictEntries.map((entry) => {
              const barWidth = ((entry.count / maxConflictCount) * 100).toFixed(0);
              return (
                <div key={entry.type} className="conflict-bar-item">
                  <div className="conflict-bar-meta">
                    <span className="conflict-bar-label">{entry.label}</span>
                    <span className="conflict-bar-val">{entry.count} log(s)</span>
                  </div>
                  <div className="conflict-bar-track">
                    <div
                      className="conflict-bar-fill"
                      style={{
                        width: `${barWidth}%`,
                        backgroundColor: entry.color
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
