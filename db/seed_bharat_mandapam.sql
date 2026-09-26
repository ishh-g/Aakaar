-- Aakaar demo expansion: Bharat Mandapam (IECC), Pragati Maidan, New Delhi.
-- Run AFTER base seed.sql and seed_new_sites.sql (order matters for FK ids).
-- Idempotent: re-running changes nothing (ON CONFLICT DO NOTHING).
--
-- Site:
--   Parcel 15  DELHI110002B01  Bharat Mandapam convention complex (28.61944 N, 77.24250 E)
--   Building 12 (convention hall block, 4 floors; F01 west-half unit overlaps full-floor unit)
--
-- Coordinates verified against Bharat Mandapam: 28°37'10"N 77°14'33"E (28.61944, 77.24250).

-- ---------------------------------------------------------------- parcel
INSERT INTO parcels (parcel_id, ulpin_2d, boundary_geom, area_sqm)
VALUES
    (15, 'DELHI110002B01', ST_GeomFromText('POLYGON((77.2421 28.6190, 77.2429 28.6190, 77.2429 28.6198, 77.2421 28.6198, 77.2421 28.6190))', 4326), 6900.0)
ON CONFLICT (parcel_id) DO NOTHING;

-- --------------------------------------------------------------- building
INSERT INTO buildings (building_id, parcel_id, footprint_geom, total_floors)
VALUES
    (12, 15, ST_GeomFromText('POLYGON((77.2422 28.6192, 77.2428 28.6192, 77.2428 28.6196, 77.2422 28.6196, 77.2422 28.6192))', 4326), 4)
ON CONFLICT (building_id) DO NOTHING;

-- --------------------------------------------------------------- properties
INSERT INTO properties (
    property_id, ulpin_3d, building_id, parcel_id, owner_id, floor_number, unit_index,
    elevation_min_m, elevation_max_m, footprint_geom, area_sqm, verification_status
)
VALUES
    -- Convention hall ground floor (plenary, clean)
    (39, 'DELHI110002B01-B01F00U01', 12, 15, 1, 0, 1, 0.0, 5.0, ST_GeomFromText('POLYGON((77.2422 28.6192, 77.2428 28.6192, 77.2428 28.6196, 77.2422 28.6196, 77.2422 28.6192))', 4326), 2550.0, 'verified'),

    -- F01 west-half unit overlaps full-floor unit above it (3D + floor overlap demo)
    (40, 'DELHI110002B01-B01F01U01', 12, 15, 2, 1, 1, 5.0, 10.0, ST_GeomFromText('POLYGON((77.2422 28.6192, 77.2425 28.6192, 77.2425 28.6196, 77.2422 28.6196, 77.2422 28.6192))', 4326), 1275.0, 'conflict'),
    (41, 'DELHI110002B01-B01F01U02', 12, 15, 3, 1, 2, 7.5, 12.5, ST_GeomFromText('POLYGON((77.2422 28.6192, 77.2428 28.6192, 77.2428 28.6196, 77.2422 28.6196, 77.2422 28.6192))', 4326), 2550.0, 'conflict'),

    -- Upper exhibition floors (clean)
    (42, 'DELHI110002B01-B01F02U01', 12, 15, 1, 2, 1, 12.5, 17.5, ST_GeomFromText('POLYGON((77.2422 28.6192, 77.2428 28.6192, 77.2428 28.6196, 77.2422 28.6196, 77.2422 28.6192))', 4326), 2550.0, 'verified'),
    (43, 'DELHI110002B01-B01F03U01', 12, 15, 2, 3, 1, 17.5, 22.5, ST_GeomFromText('POLYGON((77.2422 28.6192, 77.2428 28.6192, 77.2428 28.6196, 77.2422 28.6196, 77.2422 28.6192))', 4326), 2550.0, 'verified')
ON CONFLICT (property_id) DO NOTHING;

-- ----------------------------------------------------------- conflict logs
INSERT INTO conflict_logs (property_id_a, property_id_b, conflict_type, resolved)
VALUES
    -- Bharat Mandapam hall 3D + floor overlaps (40 vs 41)
    (40, 41, 'overlap', FALSE),
    (41, 40, 'overlap', FALSE),
    (40, 41, 'floor_overlap', FALSE),
    (41, 40, 'floor_overlap', FALSE)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------- sequences
SELECT setval('parcels_parcel_id_seq', COALESCE((SELECT MAX(parcel_id) FROM parcels), 1));
SELECT setval('buildings_building_id_seq', COALESCE((SELECT MAX(building_id) FROM buildings), 1));
SELECT setval('properties_property_id_seq', COALESCE((SELECT MAX(property_id) FROM properties), 1));
