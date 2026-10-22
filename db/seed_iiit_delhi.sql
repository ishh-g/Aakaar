-- Aakaar demo expansion: IIIT-Delhi, Okhla Phase III, New Delhi.
-- Run AFTER base seed.sql, seed_new_sites.sql and seed_bharat_mandapam.sql.
-- Idempotent: re-running changes nothing.
--
-- Site:
--   Parcel 16  DELHI110020I01  IIIT-Delhi campus, Okhla (28.54630 N, 77.27326 E)
--              25-acre campus parcel (~99,101 m2 / ~10 ha / ~24.49 acres)
--   Building 13 (academic block, 3 floors; two asymmetric F01/F02 overlaps)
--
-- Coordinates verified against OpenStreetMap: IIIT-Delhi campus centre
-- 28.546326 N, 77.273257 E (campus bbox 28.543383-28.548910, 77.269661-77.274492).
-- The parcel below is a 25-acre rectangle centred on the campus; its true
-- PostGIS geography area is 99,098.24 m2 (0.003% below the recorded 99,101 m2).
-- The academic block footprint is 3,904.49 m2.
--
-- The offsets below are deliberately asymmetric (not half/full overlaps) so
-- the severity demo shows non-round values:
--   45 vs 46 -> 1,171.35 m3 / 28.57% (Medium, amber)
--   47 vs 48 ->   146.42 m3 /  6.25% (Low, green)

-- ---------------------------------------------------------------- parcel
INSERT INTO parcels (parcel_id, ulpin_2d, boundary_geom, area_sqm)
VALUES
    (16, 'DELHI110020I01', ST_GeomFromText('POLYGON((77.271769 28.544808, 77.274831 28.544808, 77.274831 28.547792, 77.271769 28.547792, 77.271769 28.544808))', 4326), 99101.00)
ON CONFLICT (parcel_id) DO NOTHING;

-- --------------------------------------------------------------- building
INSERT INTO buildings (building_id, parcel_id, footprint_geom, total_floors)
VALUES
    (13, 16, ST_GeomFromText('POLYGON((77.2730 28.5460, 77.2736 28.5460, 77.2736 28.5466, 77.2730 28.5466, 77.2730 28.5460))', 4326), 3)
ON CONFLICT (building_id) DO NOTHING;

-- --------------------------------------------------------------- properties
INSERT INTO properties (
    property_id, ulpin_3d, building_id, parcel_id, owner_id, floor_number, unit_index,
    elevation_min_m, elevation_max_m, footprint_geom, area_sqm, verification_status
)
VALUES
    -- Academic block ground floor (clean, full footprint)
    (44, 'DELHI110020I01-B01F00U01', 13, 16, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.2730 28.5460, 77.2736 28.5460, 77.2736 28.5466, 77.2730 28.5466, 77.2730 28.5460))', 4326), 3904.49, 'verified'),

    -- F01: 0-45% unit vs 30-65% unit, overlapping height 4.0-6.0 m.
    -- Neither footprint contains the other -> 28.57% of the smaller volume.
    (45, 'DELHI110020I01-B01F01U01', 13, 16, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.2730 28.5460, 77.27327 28.5460, 77.27327 28.5466, 77.2730 28.5466, 77.2730 28.5460))', 4326), 1757.02, 'conflict'),
    (46, 'DELHI110020I01-B01F01U02', 13, 16, 3, 1, 2, 4.0, 7.0, ST_GeomFromText('POLYGON((77.27318 28.5460, 77.27339 28.5460, 77.27339 28.5466, 77.27318 28.5466, 77.27318 28.5460))', 4326), 1366.57, 'conflict'),

    -- F02: 40-100% unit vs 35-55% unit, overlapping height only 9.75-10.0 m.
    -- Small sliver -> 6.25% of the smaller volume (Low severity).
    (47, 'DELHI110020I01-B01F02U01', 13, 16, 1, 2, 1, 7.0, 10.0, ST_GeomFromText('POLYGON((77.27324 28.5460, 77.2736 28.5460, 77.2736 28.5466, 77.27324 28.5466, 77.27324 28.5460))', 4326), 2342.69, 'conflict'),
    (48, 'DELHI110020I01-B01F02U02', 13, 16, 2, 2, 2, 9.75, 12.75, ST_GeomFromText('POLYGON((77.27321 28.5460, 77.27333 28.5460, 77.27333 28.5466, 77.27321 28.5466, 77.27321 28.5460))', 4326), 780.90, 'conflict')
ON CONFLICT (property_id) DO NOTHING;

-- ----------------------------------------------------------- conflict logs
INSERT INTO conflict_logs (property_id_a, property_id_b, conflict_type, resolved)
SELECT v.a, v.b, v.t, FALSE
FROM (VALUES
    -- IIIT-Delhi academic block 3D + floor overlaps (45 vs 46)
    (45, 46, 'overlap'::conflict_type),
    (46, 45, 'overlap'::conflict_type),
    (45, 46, 'floor_overlap'::conflict_type),
    (46, 45, 'floor_overlap'::conflict_type),
    -- IIIT-Delhi F02 small sliver overlaps (47 vs 48)
    (47, 48, 'overlap'::conflict_type),
    (48, 47, 'overlap'::conflict_type),
    (47, 48, 'floor_overlap'::conflict_type),
    (48, 47, 'floor_overlap'::conflict_type)
) AS v(a, b, t)
WHERE NOT EXISTS (
    SELECT 1
    FROM conflict_logs cl
    WHERE cl.property_id_a = v.a
      AND cl.property_id_b = v.b
      AND cl.conflict_type = v.t
      AND cl.resolved = FALSE
);

-- ---------------------------------------------------------------- sequences
SELECT setval('parcels_parcel_id_seq', COALESCE((SELECT MAX(parcel_id) FROM parcels), 1));
SELECT setval('buildings_building_id_seq', COALESCE((SELECT MAX(building_id) FROM buildings), 1));
SELECT setval('properties_property_id_seq', COALESCE((SELECT MAX(property_id) FROM properties), 1));
