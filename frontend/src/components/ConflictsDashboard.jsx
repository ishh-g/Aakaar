import React, { useMemo, useState } from 'react';
import { getSiteForParcel } from '../sites';

// Stretch goal: colour-code overlap severity. Thresholds are on the
// overlap percentage of the smaller property's volume.
function severityBadgeStyle(pct) {
  const color = pct >= 50 ? '#ef4444' : pct >= 10 ? '#f59e0b' : '#22c55e';
  return {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: '4px',
    border: `1px solid ${color}`,
    backgroundColor: `${color}22`,
    color,
    fontWeight: 600,
    fontSize: '0.75rem',
  };
}

function severityLabel(pct) {
  if (pct >= 50) return 'High';
  if (pct >= 10) return 'Medium';
  return 'Low';
}

export default function ConflictsDashboard({ conflicts, mapData, user, onVerify, onInspectProperty }) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortDir, setSortDir] = useState(null); // null | 'desc' | 'asc'

  const canVerify = user && (user.role === 'admin' || user.role === 'surveyor');

  const conflictTypes = ['ALL', 'overlap', 'boundary_violation', 'duplicate', 'floor_overlap', 'building_parcel_mismatch'];

  // The conflicts API only returns property IDs; mapData carries the
  // property -> parcel relation, so we can show/search the real site name.
  const propertySites = useMemo(() => {
    const map = new Map();
    for (const feature of mapData?.features || []) {
      const props = feature.properties || {};
      if (props.layer === 'property' && props.property_id != null) {
        map.set(props.property_id, getSiteForParcel(props.parcel_id).name);
      }
    }
    return map;
  }, [mapData]);

  const siteFor = (propertyId) => propertySites.get(propertyId) || null;

  const filteredConflicts = conflicts.filter((c) => {
    const matchesFilter = filterType === 'ALL' || c.conflict_type === filterType;
    const query = searchQuery.toLowerCase();
    const siteA = (siteFor(c.property_id_a) || '').toLowerCase();
    const siteB = (c.property_id_b ? siteFor(c.property_id_b) || '' : '').toLowerCase();
    const matchesSearch = 
      c.conflict_id.toString().includes(searchQuery) ||
      c.property_id_a.toString().includes(searchQuery) ||
      (c.property_id_b && c.property_id_b.toString().includes(searchQuery)) ||
      c.conflict_type.toLowerCase().includes(query) ||
      siteA.includes(query) ||
      siteB.includes(query);
    return matchesFilter && matchesSearch;
  });

  // Sorting is applied after filtering/searching so both keep working.
  // Rows without a severity (non-overlap conflicts) always sort last.
  const orderedConflicts = (() => {
    if (!sortDir) return filteredConflicts;
    return [...filteredConflicts].sort((a, b) => {
      const aVol = a.overlap_volume_m3;
      const bVol = b.overlap_volume_m3;
      if (aVol == null && bVol == null) return 0;
      if (aVol == null) return 1;
      if (bVol == null) return -1;
      return sortDir === 'desc' ? bVol - aVol : aVol - bVol;
    });
  })();

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
              <th
                onClick={() => setSortDir((prev) => (prev === 'desc' ? 'asc' : 'desc'))}
                title="Sort by 3D overlap volume"
                style={{ cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' }}
              >
                Overlap Volume (m³){' '}
                {sortDir === 'desc' ? '▼' : sortDir === 'asc' ? '▲' : '↕'}
              </th>
              <th>Overlap %</th>
              <th>Detected Timestamp</th>
              <th>Resolution Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {orderedConflicts.length > 0 ? (
              orderedConflicts.map((c) => (
                <tr key={c.conflict_id}>
                  <td>
                    <span className="id-badge">#{c.conflict_id}</span>
                  </td>
                  <td>
                    <strong>Property #{c.property_id_a}</strong>
                    {siteFor(c.property_id_a) && (
                      <div className="property-site-label">{siteFor(c.property_id_a)}</div>
                    )}
                  </td>
                  <td>
                    {c.property_id_b ? (
                      <>
                        <strong>Property #{c.property_id_b}</strong>
                        {siteFor(c.property_id_b) && (
                          <div className="property-site-label">{siteFor(c.property_id_b)}</div>
                        )}
                      </>
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
                    {c.overlap_volume_m3 != null ? (
                      <span style={{ whiteSpace: 'nowrap', fontVariantNumeric: 'tabular-nums' }}>
                        {Number(c.overlap_volume_m3).toLocaleString(undefined, {
                          maximumFractionDigits: 2,
                        })}{' '}
                        m³
                      </span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td>
                    {c.overlap_pct != null ? (
                      <span
                        style={severityBadgeStyle(c.overlap_pct)}
                        title={`${severityLabel(c.overlap_pct)} overlap severity`}
                      >
                        {Number(c.overlap_pct).toFixed(2)}%
                      </span>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
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
                        Inspect on 3D Map
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
                <td colSpan="9" className="empty-table">
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
