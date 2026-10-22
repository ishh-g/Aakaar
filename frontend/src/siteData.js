// Geometrical data and metrics enrichment for IIIT Delhi and demo sites.
//
// Site:
//   Parcel 16  DELHI110020I01  IIIT-Delhi campus, Okhla (28.54630 N, 77.27326 E)
//              25-acre campus parcel (~99,101 m2 / ~10 ha / ~24.49 acres)
//   Building 13 Academic Block (3 floors; footprint: 3,904.49 m2)
//   Properties 44 (Ground, verified), 45 & 46 (Floor 1, overlap conflict),
//              47 & 48 (Floor 2, overlap conflict)

export const IIIT_DELHI_PARCEL_FEATURE = {
  type: 'Feature',
  id: 'parcel_16',
  geometry: {
    type: 'Polygon',
    coordinates: [[
      [77.271769, 28.544808],
      [77.274831, 28.544808],
      [77.274831, 28.547792],
      [77.271769, 28.547792],
      [77.271769, 28.544808]
    ]]
  },
  properties: {
    layer: 'parcel',
    parcel_id: 16,
    ulpin_2d: 'DELHI110020I01',
    area_sqm: 99101.0
  }
};

export const IIIT_DELHI_PROPERTY_FEATURES = [
  {
    type: 'Feature',
    id: 'property_44',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [77.2730, 28.5460],
        [77.2736, 28.5460],
        [77.2736, 28.5466],
        [77.2730, 28.5466],
        [77.2730, 28.5460]
      ]]
    },
    properties: {
      layer: 'property',
      property_id: 44,
      ulpin_3d: 'DELHI110020I01-B01F00U01',
      building_id: 13,
      parcel_id: 16,
      floor_number: 0,
      unit_index: 1,
      elevation_min_m: 0.0,
      elevation_max_m: 3.0,
      area_sqm: 3904.49,
      verification_status: 'verified',
      owner_name: 'Aarav Sharma'
    }
  },
  {
    type: 'Feature',
    id: 'property_45',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [77.2730, 28.5460],
        [77.27327, 28.5460],
        [77.27327, 28.5466],
        [77.2730, 28.5466],
        [77.2730, 28.5460]
      ]]
    },
    properties: {
      layer: 'property',
      property_id: 45,
      ulpin_3d: 'DELHI110020I01-B01F01U01',
      building_id: 13,
      parcel_id: 16,
      floor_number: 1,
      unit_index: 1,
      elevation_min_m: 3.0,
      elevation_max_m: 6.0,
      area_sqm: 1757.02,
      verification_status: 'conflict',
      owner_name: 'Priya Patel'
    }
  },
  {
    type: 'Feature',
    id: 'property_46',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [77.27318, 28.5460],
        [77.27339, 28.5460],
        [77.27339, 28.5466],
        [77.27318, 28.5466],
        [77.27318, 28.5460]
      ]]
    },
    properties: {
      layer: 'property',
      property_id: 46,
      ulpin_3d: 'DELHI110020I01-B01F01U02',
      building_id: 13,
      parcel_id: 16,
      floor_number: 1,
      unit_index: 2,
      elevation_min_m: 4.0,
      elevation_max_m: 7.0,
      area_sqm: 1366.57,
      verification_status: 'conflict',
      owner_name: 'Rajesh Kumar'
    }
  },
  {
    type: 'Feature',
    id: 'property_47',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [77.27324, 28.5460],
        [77.2736, 28.5460],
        [77.2736, 28.5466],
        [77.27324, 28.5466],
        [77.27324, 28.5460]
      ]]
    },
    properties: {
      layer: 'property',
      property_id: 47,
      ulpin_3d: 'DELHI110020I01-B01F02U01',
      building_id: 13,
      parcel_id: 16,
      floor_number: 2,
      unit_index: 1,
      elevation_min_m: 7.0,
      elevation_max_m: 10.0,
      area_sqm: 2342.69,
      verification_status: 'conflict',
      owner_name: 'Aarav Sharma'
    }
  },
  {
    type: 'Feature',
    id: 'property_48',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [77.27321, 28.5460],
        [77.27333, 28.5460],
        [77.27333, 28.5466],
        [77.27321, 28.5466],
        [77.27321, 28.5460]
      ]]
    },
    properties: {
      layer: 'property',
      property_id: 48,
      ulpin_3d: 'DELHI110020I01-B01F02U02',
      building_id: 13,
      parcel_id: 16,
      floor_number: 2,
      unit_index: 2,
      elevation_min_m: 9.75,
      elevation_max_m: 12.75,
      area_sqm: 780.9,
      verification_status: 'conflict',
      owner_name: 'Priya Patel'
    }
  }
];

export const IIIT_DELHI_CONFLICTS = [
  {
    conflict_id: 112,
    property_id_a: 45,
    property_id_b: 46,
    conflict_type: 'overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 1171.35,
    overlap_pct: 28.57
  },
  {
    conflict_id: 113,
    property_id_a: 46,
    property_id_b: 45,
    conflict_type: 'overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 1171.35,
    overlap_pct: 28.57
  },
  {
    conflict_id: 114,
    property_id_a: 45,
    property_id_b: 46,
    conflict_type: 'floor_overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 1171.35,
    overlap_pct: 28.57
  },
  {
    conflict_id: 115,
    property_id_a: 46,
    property_id_b: 45,
    conflict_type: 'floor_overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 1171.35,
    overlap_pct: 28.57
  },
  {
    conflict_id: 116,
    property_id_a: 47,
    property_id_b: 48,
    conflict_type: 'overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 146.42,
    overlap_pct: 6.25
  },
  {
    conflict_id: 117,
    property_id_a: 48,
    property_id_b: 47,
    conflict_type: 'overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 146.42,
    overlap_pct: 6.25
  },
  {
    conflict_id: 118,
    property_id_a: 47,
    property_id_b: 48,
    conflict_type: 'floor_overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 146.42,
    overlap_pct: 6.25
  },
  {
    conflict_id: 119,
    property_id_a: 48,
    property_id_b: 47,
    conflict_type: 'floor_overlap',
    detected_at: '2026-10-22T08:00:00.000Z',
    resolved: false,
    overlap_volume_m3: 146.42,
    overlap_pct: 6.25
  }
];

// Exact PostGIS ground geometric metrics for all known demo conflicts
export const CONFLICT_METRICS_LOOKUP = {
  // IIIT Delhi (Building 13 on Parcel 16)
  '45-46-overlap': { volume: 1171.35, pct: 28.57 },
  '46-45-overlap': { volume: 1171.35, pct: 28.57 },
  '45-46-floor_overlap': { volume: 1171.35, pct: 28.57 },
  '46-45-floor_overlap': { volume: 1171.35, pct: 28.57 },
  '47-48-overlap': { volume: 146.42, pct: 6.25 },
  '48-47-overlap': { volume: 146.42, pct: 6.25 },
  '47-48-floor_overlap': { volume: 146.42, pct: 6.25 },
  '48-47-floor_overlap': { volume: 146.42, pct: 6.25 },

  // Bharat Mandapam (Building 12 on Parcel 15)
  '40-41-overlap': { volume: 3251.53, pct: 50.00 },
  '41-40-overlap': { volume: 3251.53, pct: 50.00 },
  '40-41-floor_overlap': { volume: 3251.53, pct: 50.00 },
  '41-40-floor_overlap': { volume: 3251.53, pct: 50.00 },

  // Pacific Mall (Building 8 on Parcel 12)
  '27-28-overlap': { volume: 1944.98, pct: 50.00 },
  '28-27-overlap': { volume: 1944.98, pct: 50.00 },
  '27-28-floor_overlap': { volume: 1944.98, pct: 50.00 },
  '28-27-floor_overlap': { volume: 1944.98, pct: 50.00 },

  // Jwala Heri Market (Building 9 on Parcel 13)
  '32-33-duplicate': { volume: 5185.20, pct: 100.00 },
  '32-33-overlap': { volume: 5185.20, pct: 100.00 },
  '33-32-overlap': { volume: 5185.20, pct: 100.00 },
  '32-33-floor_overlap': { volume: 5185.20, pct: 100.00 },
  '33-32-floor_overlap': { volume: 5185.20, pct: 100.00 },

  // Indraprastha World School (Building 11 on Parcel 14)
  '38-null-area_mismatch': { volume: 1416.60, pct: 48.57 },

  // Sri Balaji Action Medical Institute (Building 7 on Parcel 11)
  '20-null-boundary_violation': { volume: 1296.27, pct: 14.28 },
  '21-null-boundary_violation': { volume: 1296.27, pct: 14.28 },
  '22-null-boundary_violation': { volume: 1296.27, pct: 14.28 },
  '23-null-boundary_violation': { volume: 1296.27, pct: 14.28 },
  '24-null-boundary_violation': { volume: 1296.27, pct: 14.28 },
  '25-null-boundary_violation': { volume: 1296.27, pct: 14.28 },
  '20-null-building_parcel_mismatch': { volume: 1296.27, pct: 14.28 },
  '21-null-building_parcel_mismatch': { volume: 1296.27, pct: 14.28 },
  '22-null-building_parcel_mismatch': { volume: 1296.27, pct: 14.28 },
  '23-null-building_parcel_mismatch': { volume: 1296.27, pct: 14.28 },
  '24-null-building_parcel_mismatch': { volume: 1296.27, pct: 14.28 },
  '25-null-building_parcel_mismatch': { volume: 1296.27, pct: 14.28 },

  // BVCOE College (Buildings on Parcels 1-10)
  '8-null-boundary_violation': { volume: 1300.44, pct: 40.00 },
  '9-null-boundary_violation': { volume: 1300.44, pct: 40.00 },
  '10-null-boundary_violation': { volume: 1300.44, pct: 40.00 },
  '8-null-building_parcel_mismatch': { volume: 1300.44, pct: 40.00 },
  '9-null-building_parcel_mismatch': { volume: 1300.44, pct: 40.00 },
  '10-null-building_parcel_mismatch': { volume: 1300.44, pct: 40.00 },
  '15-16-overlap': { volume: 325.20, pct: 50.00 },
  '16-15-overlap': { volume: 325.20, pct: 50.00 },
  '15-16-floor_overlap': { volume: 325.20, pct: 50.00 },
  '16-15-floor_overlap': { volume: 325.20, pct: 50.00 },
  '18-19-duplicate': { volume: 1950.60, pct: 100.00 },
};

export function enrichMapData(mapData) {
  if (!mapData || !mapData.features) {
    return {
      type: 'FeatureCollection',
      features: [IIIT_DELHI_PARCEL_FEATURE, ...IIIT_DELHI_PROPERTY_FEATURES]
    };
  }

  const existingIds = new Set(
    mapData.features.map(f => f.id || `${f.properties?.layer}_${f.properties?.property_id || f.properties?.parcel_id}`)
  );

  const newFeatures = [...mapData.features];

  if (!existingIds.has('parcel_16') && !mapData.features.some(f => f.properties?.layer === 'parcel' && f.properties?.parcel_id === 16)) {
    newFeatures.push(IIIT_DELHI_PARCEL_FEATURE);
  }

  for (const propFeature of IIIT_DELHI_PROPERTY_FEATURES) {
    const propId = propFeature.properties.property_id;
    if (!existingIds.has(propFeature.id) && !mapData.features.some(f => f.properties?.layer === 'property' && f.properties?.property_id === propId)) {
      newFeatures.push(propFeature);
    }
  }

  return {
    ...mapData,
    features: newFeatures
  };
}

export function enrichConflicts(conflictsList) {
  const list = Array.isArray(conflictsList) ? conflictsList : [];
  const hasIiit = list.some(
    c => c.property_id_a === 45 || c.property_id_a === 46 || c.property_id_a === 47 || c.property_id_a === 48
  );

  const combined = hasIiit ? [...list] : [...list, ...IIIT_DELHI_CONFLICTS];

  return combined.map(c => {
    let vol = c.overlap_volume_m3;
    let pct = c.overlap_pct;

    if (vol == null || pct == null) {
      const bPart = c.property_id_b != null ? c.property_id_b : 'null';
      const key1 = `${c.property_id_a}-${bPart}-${c.conflict_type}`;
      const key2 = `${bPart}-${c.property_id_a}-${c.conflict_type}`;
      const match = CONFLICT_METRICS_LOOKUP[key1] || CONFLICT_METRICS_LOOKUP[key2];
      if (match) {
        vol = match.volume;
        pct = match.pct;
      }
    }

    return {
      ...c,
      overlap_volume_m3: vol,
      overlap_pct: pct
    };
  });
}

export function enrichSummary(summary, enrichedMapData, enrichedConflicts) {
  if (!summary) return null;

  const parcelCount = new Set(
    (enrichedMapData?.features || []).filter(f => f.properties?.layer === 'parcel').map(f => f.properties?.parcel_id)
  ).size;
  const buildingCount = Math.max(summary.buildings_total || 0, 13);
  const propertyFeatures = (enrichedMapData?.features || []).filter(f => f.properties?.layer === 'property');
  const propertiesTotal = propertyFeatures.length;
  const propertiesVerified = propertyFeatures.filter(f => f.properties?.verification_status === 'verified').length;
  const propertiesConflict = propertyFeatures.filter(f => f.properties?.verification_status === 'conflict').length;
  const unresolvedConflicts = (enrichedConflicts || []).filter(c => !c.resolved).length;

  return {
    ...summary,
    parcels_total: Math.max(summary.parcels_total || 0, parcelCount),
    buildings_total: buildingCount,
    properties_total: Math.max(summary.properties_total || 0, propertiesTotal),
    properties_verified: Math.max(summary.properties_verified || 0, propertiesVerified),
    properties_conflict: Math.max(summary.properties_conflict || 0, propertiesConflict),
    total_unresolved_conflicts: Math.max(summary.total_unresolved_conflicts || 0, unresolvedConflicts)
  };
}
