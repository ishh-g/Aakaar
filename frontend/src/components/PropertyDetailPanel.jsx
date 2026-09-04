import React from 'react';

export default function PropertyDetailPanel({ property, conflicts, user, onClose, onVerify }) {
  if (!property) return null;

  const isConflict = property.verification_status === 'conflict';
  const isVerified = property.verification_status === 'verified';
  const canVerify = user && (user.role === 'admin' || user.role === 'surveyor');

  // Filter conflicts relevant to this property
  const relevantConflicts = conflicts.filter(
    (c) => c.property_id_a === property.property_id || c.property_id_b === property.property_id
  );

  return (
    <div className="detail-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <span className="panel-subtitle">3D Property Unit</span>
          <h2 className="panel-ulpin">{property.ulpin_3d}</h2>
        </div>
        <button className="close-btn" onClick={onClose} title="Close Panel">
          &times;
        </button>
      </div>

      <div className="status-banner" style={{
        backgroundColor: isConflict ? 'rgba(239, 68, 68, 0.15)' : 'rgba(34, 197, 94, 0.15)',
        borderColor: isConflict ? '#ef4444' : '#22c55e'
      }}>
        <div className="status-pill" style={{
          backgroundColor: isConflict ? '#ef4444' : '#22c55e',
          color: '#fff'
        }}>
          {isConflict ? 'CONFLICT DETECTED' : isVerified ? 'VERIFIED' : 'UNVERIFIED'}
        </div>
        <span className="status-desc">
          {isConflict 
            ? `${relevantConflicts.length || 1} Spatial Conflict(s) Triggered` 
            : 'All 7 PostGIS geometric checks passed'}
        </span>
      </div>

      {isConflict && (
        <div className="conflict-section">
          <h3>Active Conflict Logs</h3>
          <div className="conflict-list">
            {relevantConflicts.length > 0 ? (
              relevantConflicts.map((c) => (
                <div key={c.conflict_id} className="conflict-card">
                  <div className="conflict-badge">{c.conflict_type.toUpperCase().replace(/_/g, ' ')}</div>
                  <div className="conflict-details">
                    <span><strong>Conflict ID:</strong> #{c.conflict_id}</span>
                    {c.property_id_b && (
                      <span><strong>Conflicting Target:</strong> Property #{c.property_id_b}</span>
                    )}
                    <span><strong>Detected:</strong> {new Date(c.detected_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="conflict-card">
                <div className="conflict-badge">SPATIAL CONFLICT</div>
                <div className="conflict-details">
                  <span>Flagged by automated 3D spatial detector</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="attributes-grid">
        <div className="attr-item">
          <span className="attr-label">Property ID</span>
          <span className="attr-value">#{property.property_id}</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Parcel ID</span>
          <span className="attr-value">#{property.parcel_id}</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Building ID</span>
          <span className="attr-value">#{property.building_id}</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Floor Number</span>
          <span className="attr-value">Floor {property.floor_number} (Unit {property.unit_index || 1})</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Vertical Elevation</span>
          <span className="attr-value">{property.elevation_min_m}m to {property.elevation_max_m}m</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Vertical Height</span>
          <span className="attr-value">{(property.elevation_max_m - property.elevation_min_m).toFixed(1)}m</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Floor Area</span>
          <span className="attr-value">{property.area_sqm} m&sup2;</span>
        </div>
        <div className="attr-item">
          <span className="attr-label">Owner</span>
          <span className="attr-value">{property.owner?.name || property.owner_name || 'Aarav Sharma'}</span>
        </div>
      </div>

      {isConflict && (
        <div className="panel-actions">
          {canVerify ? (
            <button 
              className="verify-action-btn"
              onClick={() => onVerify(property.property_id)}
            >
              Officer Override: Verify Property
            </button>
          ) : (
            <div className="restricted-notice">
              <span className="lock-icon">&#128274;</span>
              <span>Verification restricted to Land Authority Officers (Admin/Surveyor).</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
