import React from 'react';

export default function StatsSummaryBar({ summary }) {
  if (!summary) return null;

  return (
    <div className="stats-bar">
      <div className="stat-pill">
        <span className="stat-label">Parcels</span>
        <span className="stat-val">{summary.parcels_total}</span>
      </div>
      <div className="stat-pill">
        <span className="stat-label">Buildings</span>
        <span className="stat-val">{summary.buildings_total}</span>
      </div>
      <div className="stat-pill">
        <span className="stat-label">3D Properties</span>
        <span className="stat-val">{summary.properties_total}</span>
      </div>
      <div className="stat-pill stat-verified">
        <span className="stat-label">Verified</span>
        <span className="stat-val">{summary.properties_verified}</span>
      </div>
      <div className="stat-pill stat-conflict">
        <span className="stat-label">Conflicts</span>
        <span className="stat-val">{summary.properties_conflict}</span>
      </div>
    </div>
  );
}
