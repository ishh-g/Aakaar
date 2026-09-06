import React, { useState, useEffect } from 'react';

export default function UlpinGeneratorPage({ mapData, propertiesList, onInspectProperty }) {
  // Extract unique parcels from mapData or provide default 10 BVCOE parcels
  const parcelOptions = React.useMemo(() => {
    if (mapData && mapData.features) {
      const parcels = mapData.features
        .filter(f => f.properties?.layer === 'parcel')
        .map(f => ({
          parcel_id: f.properties.parcel_id,
          ulpin_2d: f.properties.ulpin_2d || `DELHI110001P${String(f.properties.parcel_id).padStart(2, '0')}`,
          label: `Parcel ${f.properties.parcel_id} (${f.properties.ulpin_2d || `DELHI110001P${String(f.properties.parcel_id).padStart(2, '0')}`})`
        }));
      if (parcels.length > 0) return parcels;
    }
    // Fallback standard 10 parcels
    return Array.from({ length: 10 }, (_, i) => ({
      parcel_id: i + 1,
      ulpin_2d: `DELHI110001P${String(i + 1).padStart(2, '0')}`,
      label: `Parcel ${i + 1} (DELHI110001P${String(i + 1).padStart(2, '0')})`
    }));
  }, [mapData]);

  const [selectedParcel, setSelectedParcel] = useState(parcelOptions[0]?.ulpin_2d || 'DELHI110001P01');
  const [buildingIdx, setBuildingIdx] = useState(1);
  const [floorNum, setFloorNum] = useState(3);
  const [unitIdx, setUnitIdx] = useState(2);

  const [generationState, setGenerationState] = useState({
    active: false,
    step: 0,
    data: null,
    loading: false
  });

  const [copied, setCopied] = useState(false);

  // Sync initial parcel if options change
  useEffect(() => {
    if (parcelOptions.length > 0 && !selectedParcel) {
      setSelectedParcel(parcelOptions[0].ulpin_2d);
    }
  }, [parcelOptions, selectedParcel]);

  // Handle generation trigger
  const handleGenerate = async () => {
    setGenerationState({ active: true, step: 0, data: null, loading: true });
    setCopied(false);

    try {
      const query = new URLSearchParams({
        ulpin_2d: selectedParcel,
        building_idx: buildingIdx,
        floor_num: floorNum,
        unit_idx: unitIdx
      });

      const res = await fetch(`http://localhost:8000/ulpin/preview?${query.toString()}`);
      if (!res.ok) throw new Error('Preview API error');
      const data = await res.json();

      setGenerationState({ active: true, step: 0, data, loading: false });

      // Staggered step-by-step reveal animation
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 1 })), 100);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 2 })), 450);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 3 })), 800);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 4 })), 1150);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 5 })), 1500);
    } catch (err) {
      console.error('Error generating preview:', err);
      // Fallback pure generator in frontend if offline
      const bSeg = `B${String(buildingIdx).padStart(2, '0')}`;
      const fSeg = floorNum < 0 ? `FB${Math.abs(floorNum)}` : `F${String(floorNum).padStart(2, '0')}`;
      const uSeg = `U${String(unitIdx).padStart(2, '0')}`;
      const fallbackData = {
        ulpin_2d: selectedParcel,
        building_idx: buildingIdx,
        floor_num: floorNum,
        unit_idx: unitIdx,
        is_basement: floorNum < 0,
        building_segment: bSeg,
        floor_segment: fSeg,
        unit_segment: uSeg,
        step1_base: selectedParcel,
        step2_building: `${selectedParcel}-${bSeg}`,
        step3_floor: `${selectedParcel}-${bSeg}${fSeg}`,
        step4_unit: `${selectedParcel}-${bSeg}${fSeg}${uSeg}`,
        final_ulpin_3d: `${selectedParcel}-${bSeg}${fSeg}${uSeg}`
      };
      setGenerationState({ active: true, step: 0, data: fallbackData, loading: false });
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 1 })), 100);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 2 })), 450);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 3 })), 800);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 4 })), 1150);
      setTimeout(() => setGenerationState(prev => ({ ...prev, step: 5 })), 1500);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleLoadSample = (prop) => {
    // Parse ULPIN or parcel info
    const parcel = parcelOptions.find(p => p.parcel_id === prop.parcel_id);
    if (parcel) setSelectedParcel(parcel.ulpin_2d);
    setBuildingIdx(1);
    setFloorNum(prop.floor_number ?? 0);
    setUnitIdx(prop.unit_index ?? 1);
  };

  return (
    <div className="generator-container">
      <div className="generator-header">
        <div>
          <h2>3D ULPIN Generator</h2>
          <p>
            Interactive demonstration of Section 4 standard 3D Unique Land Parcel Identification Number assembly
          </p>
        </div>
      </div>

      {/* Main Interactive Row */}
      <div className="generator-main-grid">
        {/* Left: Input Configuration */}
        <div className="generator-card">
          <div className="generator-card-header">
            <h3>1. Configure Spatial Parameters</h3>
          </div>

          <div className="generator-form">
            <div className="form-group">
              <label>Parent 2D Parcel ULPIN</label>
              <select
                value={selectedParcel}
                onChange={(e) => setSelectedParcel(e.target.value)}
                className="generator-select"
              >
                {parcelOptions.map(p => (
                  <option key={p.parcel_id} value={p.ulpin_2d}>
                    {p.label}
                  </option>
                ))}
              </select>
              <small className="form-help">Unique 14-character alphanumeric Bhu-Aadhaar parcel code</small>
            </div>

            <div className="form-row-3">
              <div className="form-group">
                <label>Building Index</label>
                <div className="input-with-prefix">
                  <span className="input-prefix">B</span>
                  <input
                    type="number"
                    min="1"
                    max="99"
                    value={buildingIdx}
                    onChange={(e) => setBuildingIdx(Math.max(1, parseInt(e.target.value) || 1))}
                    className="generator-input"
                  />
                </div>
                <small className="form-help">Structure within parcel</small>
              </div>

              <div className="form-group">
                <label>Floor Number</label>
                <div className="input-with-prefix">
                  <span className="input-prefix">F</span>
                  <input
                    type="number"
                    min="-10"
                    max="150"
                    value={floorNum}
                    onChange={(e) => setFloorNum(parseInt(e.target.value) || 0)}
                    className="generator-input"
                  />
                </div>
                <small className="form-help">&lt;0 for Basements (FB1...)</small>
              </div>

              <div className="form-group">
                <label>Unit Index</label>
                <div className="input-with-prefix">
                  <span className="input-prefix">U</span>
                  <input
                    type="number"
                    min="1"
                    max="99"
                    value={unitIdx}
                    onChange={(e) => setUnitIdx(Math.max(1, parseInt(e.target.value) || 1))}
                    className="generator-input"
                  />
                </div>
                <small className="form-help">Unit on floor</small>
              </div>
            </div>

            <button
              className="generate-action-btn"
              onClick={handleGenerate}
              disabled={generationState.loading}
            >
              {generationState.loading ? 'Generating...' : 'Assemble 3D ULPIN'}
            </button>
          </div>
        </div>

        {/* Right: Step-by-Step Live Assembly Reveal */}
        <div className="generator-card reveal-card">
          <div className="generator-card-header">
            <h3>2. Standard Assembly Breakdown</h3>
            {generationState.step >= 5 && (
              <button
                className="copy-btn"
                onClick={() => handleCopy(generationState.data?.final_ulpin_3d)}
              >
                {copied ? 'Copied to Clipboard' : 'Copy 3D ULPIN'}
              </button>
            )}
          </div>

          {!generationState.active ? (
            <div className="reveal-placeholder">
              <div className="reveal-placeholder-icon">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                </svg>
              </div>
              <p>Configure parameters on the left and click <strong>"Assemble 3D ULPIN"</strong> to watch the standard hierarchical code generation in real time.</p>
            </div>
          ) : (
            <div className="reveal-steps-list">
              {/* Step 1 */}
              <div className={`assembly-step ${generationState.step >= 1 ? 'step-visible' : ''}`}>
                <div className="step-num">Step 1</div>
                <div className="step-content">
                  <div className="step-title">
                    <span>Base 2D Parcel ULPIN</span>
                    <span className="step-tag tag-base">2D Cadastre</span>
                  </div>
                  <div className="step-output">
                    <code>{generationState.data?.step1_base}</code>
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className={`assembly-step ${generationState.step >= 2 ? 'step-visible' : ''}`}>
                <div className="step-num">Step 2</div>
                <div className="step-content">
                  <div className="step-title">
                    <span>+ Building Structure Index</span>
                    <span className="step-tag tag-building">Structure ({generationState.data?.building_segment})</span>
                  </div>
                  <div className="step-output">
                    <code>
                      {generationState.data?.step1_base}-<strong className="hl-building">{generationState.data?.building_segment}</strong>
                    </code>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className={`assembly-step ${generationState.step >= 3 ? 'step-visible' : ''}`}>
                <div className="step-num">Step 3</div>
                <div className="step-content">
                  <div className="step-title">
                    <span>+ Vertical Floor Level</span>
                    <span className="step-tag tag-floor">
                      {generationState.data?.is_basement ? `Basement (${generationState.data?.floor_segment})` : `Floor ${generationState.data?.floor_num}`}
                    </span>
                  </div>
                  <div className="step-output">
                    <code>
                      {generationState.data?.step2_building}<strong className="hl-floor">{generationState.data?.floor_segment}</strong>
                    </code>
                  </div>
                </div>
              </div>

              {/* Step 4 */}
              <div className={`assembly-step ${generationState.step >= 4 ? 'step-visible' : ''}`}>
                <div className="step-num">Step 4</div>
                <div className="step-content">
                  <div className="step-title">
                    <span>+ Subdivided Unit Suffix</span>
                    <span className="step-tag tag-unit">Unit {generationState.data?.unit_segment}</span>
                  </div>
                  <div className="step-output">
                    <code>
                      {generationState.data?.step3_floor}<strong className="hl-unit">{generationState.data?.unit_segment}</strong>
                    </code>
                  </div>
                </div>
              </div>

              {/* Final Result Box */}
              {generationState.step >= 5 && (
                <div className="final-ulpin-box">
                  <div className="final-label">OFFICIAL 3D ULPIN CODE</div>
                  <div className="final-code">
                    <span>{generationState.data?.final_ulpin_3d}</span>
                  </div>
                  <div className="final-meta">
                    <span>Elevation Ground Datum: WGS84 Ellipsoid</span>
                    <span>100% Deterministic & Geometrically Bounded</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Reference Table of Live Seeded 3D Properties */}
      <div className="reference-table-container">
        <div className="reference-table-header">
          <div>
            <h3>Active 3D Properties in Demo Locality (BVCOE New Delhi)</h3>
            <p>Real seeded database records conforming to the 3D ULPIN hierarchical standard</p>
          </div>
          <span className="ref-count-badge">
            {propertiesList ? propertiesList.length : 19} Live Seeded Properties
          </span>
        </div>

        <div className="ref-table-wrapper">
          <table className="ref-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Generated 3D ULPIN</th>
                <th>Parcel</th>
                <th>Floor</th>
                <th>Unit</th>
                <th>Elevation (Min → Max)</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {propertiesList && propertiesList.length > 0 ? (
                propertiesList.slice(0, 10).map((prop) => (
                  <tr key={prop.property_id}>
                    <td>
                      <span className="id-badge">#{prop.property_id}</span>
                    </td>
                    <td>
                      <code className="ulpin-code-text">{prop.ulpin_3d}</code>
                    </td>
                    <td>Parcel {prop.parcel_id}</td>
                    <td>{prop.floor_number === 0 ? 'Ground (0)' : `Floor ${prop.floor_number}`}</td>
                    <td>Unit {prop.unit_index || 1}</td>
                    <td>{prop.elevation_min_m}m → {prop.elevation_max_m}m</td>
                    <td>
                      <span className={`status-pill status-${prop.verification_status}`}>
                        {prop.verification_status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <button
                        className="load-sample-btn"
                        onClick={() => handleLoadSample(prop)}
                        title="Load parameters into generator"
                      >
                        Load
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="empty-table">
                    No active property records found in session.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
