import React from 'react';

export default function LegendPanel() {
  return (
    <div className="legend-panel">
      <div className="legend-title">3D Cadastre Legend</div>
      <div className="legend-items">
        <div className="legend-item">
          <span className="legend-color-box" style={{ backgroundColor: '#22c55e' }} />
          <span>Verified Property (Clean 3D Volume)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color-box" style={{ backgroundColor: '#ef4444' }} />
          <span>Spatial Conflict (Overlap / Boundary / Dup)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color-box" style={{ backgroundColor: '#9ca3af' }} />
          <span>Unverified Property</span>
        </div>
        <div className="legend-item">
          <span className="legend-line" style={{ borderColor: '#00f2fe' }} />
          <span>Parcel Cadastral Boundary (2D)</span>
        </div>
      </div>
      <div className="legend-footer">
        <span>Location: BVCOE Paschim Vihar, Delhi</span>
      </div>
    </div>
  );
}
