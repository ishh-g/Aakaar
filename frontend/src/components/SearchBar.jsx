import React, { useState, useMemo } from 'react';

export default function SearchBar({ properties, onSelectProperty }) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const filteredProperties = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase().trim();
    return properties.filter((p) => {
      const matchUlpin = p.ulpin_3d?.toLowerCase().includes(q);
      const matchId = p.property_id?.toString() === q;
      const matchBuilding = `building ${p.building_id}`.toLowerCase().includes(q);
      const matchParcel = `parcel ${p.parcel_id}`.toLowerCase().includes(q);
      const matchOwner = (p.owner_name || p.owner?.name || '').toLowerCase().includes(q);
      return matchUlpin || matchId || matchBuilding || matchParcel || matchOwner;
    }).slice(0, 8);
  }, [query, properties]);

  const handleSelect = (prop) => {
    setQuery(prop.ulpin_3d);
    setIsOpen(false);
    onSelectProperty(prop);
  };

  const handleClear = () => {
    setQuery('');
    setIsOpen(false);
  };

  return (
    <div className="search-container">
      <div className="search-input-wrapper">
        <svg className="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          type="text"
          className="search-input"
          placeholder="Search ULPIN, Property..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
        />
        {query && (
          <button className="search-clear-btn" onClick={handleClear}>
            &times;
          </button>
        )}
      </div>

      {isOpen && filteredProperties.length > 0 && (
        <div className="search-dropdown">
          {filteredProperties.map((prop) => (
            <div
              key={prop.property_id}
              className="search-item"
              onClick={() => handleSelect(prop)}
            >
              <div className="search-item-main">
                <span className="search-ulpin">{prop.ulpin_3d}</span>
                <span className="search-sub">
                  Building #{prop.building_id} &bull; Floor {prop.floor_number} &bull; {prop.elevation_min_m}-{prop.elevation_max_m}m
                </span>
              </div>
              <span
                className="search-status-tag"
                style={{
                  backgroundColor:
                    prop.verification_status === 'conflict'
                      ? '#ef4444'
                      : prop.verification_status === 'verified'
                      ? '#22c55e'
                      : '#9ca3af',
                }}
              >
                {prop.verification_status}
              </span>
            </div>
          ))}
        </div>
      )}

      {isOpen && query.trim() && filteredProperties.length === 0 && (
        <div className="search-dropdown search-empty">
          No properties matching "{query}"
        </div>
      )}
    </div>
  );
}
