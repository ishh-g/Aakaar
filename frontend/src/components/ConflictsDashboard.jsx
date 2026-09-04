import React, { useState } from 'react';

export default function ConflictsDashboard({ conflicts, user, onVerify, onInspectProperty }) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const canVerify = user && (user.role === 'admin' || user.role === 'surveyor');

  const conflictTypes = ['ALL', 'overlap', 'boundary_violation', 'duplicate', 'floor_overlap', 'building_parcel_mismatch'];

  const filteredConflicts = conflicts.filter((c) => {
    const matchesFilter = filterType === 'ALL' || c.conflict_type === filterType;
    const matchesSearch = 
      c.conflict_id.toString().includes(searchQuery) ||
      c.property_id_a.toString().includes(searchQuery) ||
      (c.property_id_b && c.property_id_b.toString().includes(searchQuery)) ||
      c.conflict_type.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h2>Spatial Conflict Audit Log</h2>
          <p>Real-time PostGIS topological violations and 3D volumetric conflicts</p>
        </div>

        <div className="dashboard-controls">
          <input
            type="text"
            className="dashboard-search"
            placeholder="Search by ID or type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />

          <select
            className="dashboard-select"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            {conflictTypes.map((type) => (
              <option key={type} value={type}>
                {type === 'ALL' ? 'All Conflict Types' : type.toUpperCase().replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="conflicts-table">
          <thead>
            <tr>
              <th>Conflict ID</th>
              <th>Primary Property (A)</th>
              <th>Conflicting Target (B)</th>
              <th>Conflict Classification</th>
              <th>Detected Timestamp</th>
              <th>Resolution Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredConflicts.length > 0 ? (
              filteredConflicts.map((c) => (
                <tr key={c.conflict_id}>
                  <td>
                    <span className="id-badge">#{c.conflict_id}</span>
                  </td>
                  <td>
                    <strong>Property #{c.property_id_a}</strong>
                  </td>
                  <td>
                    {c.property_id_b ? (
                      <strong>Property #{c.property_id_b}</strong>
                    ) : (
                      <span className="text-muted">N/A (Cadastral Boundary)</span>
                    )}
                  </td>
                  <td>
                    <span className={`conflict-type-pill type-${c.conflict_type}`}>
                      {c.conflict_type.toUpperCase().replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td>
                    {new Date(c.detected_at).toLocaleString([], {
                      dateStyle: 'short',
                      timeStyle: 'medium'
                    })}
                  </td>
                  <td>
                    <span className="unresolved-status">Unresolved (Open)</span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="map-inspect-btn"
                        onClick={() => onInspectProperty(c.property_id_a)}
                        title="Locate on 3D Cesium Map"
                      >
                        &#127757; Inspect 3D
                      </button>

                      {canVerify ? (
                        <button
                          className="table-verify-btn"
                          onClick={() => onVerify(c.property_id_a)}
                        >
                          Resolve / Verify
                        </button>
                      ) : (
                        <span className="restricted-badge">Officer Only</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="empty-table">
                  No spatial conflicts found matching criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
