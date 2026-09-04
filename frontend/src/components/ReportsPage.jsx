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
          &#8635; Refresh Live Metrics
        </button>
      </div>

      {/* Top Level Summary Cards */}
      <div className="reports-cards-grid">
        <div className="report-card">
          <div className="card-icon">&#128506;</div>
          <div className="card-content">
            <span className="card-title">Total Land Parcels</span>
            <span className="card-number">{parcels_total}</span>
            <span className="card-sub">BVCOE Cadastral Zone</span>
          </div>
        </div>

        <div className="report-card">
          <div className="card-icon">&#127970;</div>
          <div className="card-content">
            <span className="card-title">Total Buildings</span>
            <span className="card-number">{buildings_total}</span>
            <span className="card-sub">Extruded Structures</span>
          </div>
        </div>

        <div className="report-card">
          <div className="card-icon">&#128392;</div>
          <div className="card-content">
            <span className="card-title">3D Property Units</span>
            <span className="card-number">{properties_total}</span>
            <span className="card-sub">Vertical Space Titles</span>
          </div>
        </div>

        <div className="report-card report-card-alert">
          <div className="card-icon">&#9888;</div>
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
