-- Aakaar demo expansion: 4 new sites around West Delhi.
-- Run this ONCE on the hosted DB (Supabase SQL Editor) AFTER the base seed.sql.
-- Idempotent: re-running changes nothing (ON CONFLICT DO NOTHING).
--
-- Sites:
--   Parcel 11  DELHI110063H01  Sri Balaji Action Medical Institute (hospital tower, 6 floors, boundary violation)
--   Parcel 12  DELHI110018M01  Pacific Mall, Tagore Garden (mall block, 4 floors, floor overlap)
--   Parcel 13  DELHI110087J01  Jwala Heri Market (market hall, 2 floors, duplicate unit)
--   Parcel 14  DELHI110063S01  Indraprastha World School campus (2 buildings B01/B02, one area mismatch)

-- ---------------------------------------------------------------- parcels
INSERT INTO parcels (parcel_id, ulpin_2d, boundary_geom, area_sqm)
VALUES
    (11, 'DELHI110063H01', ST_GeomFromText('POLYGON((77.1099 28.6734, 77.1106 28.6734, 77.1106 28.6741, 77.1099 28.6741, 77.1099 28.6734))', 4326), 5293.0),
    (12, 'DELHI110018M01', ST_GeomFromText('POLYGON((77.1061 28.6420, 77.1070 28.6420, 77.1070 28.6428, 77.1061 28.6428, 77.1061 28.6420))', 4326), 7779.9),
    (13, 'DELHI110087J01', ST_GeomFromText('POLYGON((77.1015 28.6668, 77.1023 28.6668, 77.1023 28.6676, 77.1015 28.6676, 77.1015 28.6668))', 4326), 6913.8),
    (14, 'DELHI110063S01', ST_GeomFromText('POLYGON((77.1075 28.6706, 77.1085 28.6706, 77.1085 28.6714, 77.1075 28.6714, 77.1075 28.6706))', 4326), 8641.9)
ON CONFLICT (parcel_id) DO NOTHING;

-- --------------------------------------------------------------- buildings
-- Building 7 (Balaji tower) footprint extends past parcel 11 east edge (77.1106) -> boundary violation.
INSERT INTO buildings (building_id, parcel_id, footprint_geom, total_floors)
VALUES
    (7, 11, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 6),
    (8, 12, ST_GeomFromText('POLYGON((77.1062 28.6422, 77.1068 28.6422, 77.1068 28.6426, 77.1062 28.6426, 77.1062 28.6422))', 4326), 4),
    (9, 13, ST_GeomFromText('POLYGON((77.1016 28.6670, 77.1020 28.6670, 77.1020 28.6674, 77.1016 28.6674, 77.1016 28.6670))', 4326), 2),
    (10, 14, ST_GeomFromText('POLYGON((77.1076 28.6708, 77.1080 28.6708, 77.1080 28.6712, 77.1076 28.6712, 77.1076 28.6708))', 4326), 3),
    (11, 14, ST_GeomFromText('POLYGON((77.1081 28.6708, 77.1084 28.6708, 77.1084 28.6711, 77.1081 28.6711, 77.1081 28.6708))', 4326), 2)
ON CONFLICT (building_id) DO NOTHING;

-- --------------------------------------------------------------- properties
INSERT INTO properties (
    property_id, ulpin_3d, building_id, parcel_id, owner_id, floor_number, unit_index,
    elevation_min_m, elevation_max_m, footprint_geom, area_sqm, verification_status
)
VALUES
    -- Balaji Action Hospital tower (Building 7, 6 floors, all conflict via boundary spillover)
    (20, 'DELHI110063H01-B01F00U01', 7, 11, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 3024.6, 'conflict'),
    (21, 'DELHI110063H01-B01F01U01', 7, 11, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 3024.6, 'conflict'),
    (22, 'DELHI110063H01-B01F02U01', 7, 11, 3, 2, 1, 6.0, 9.0, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 3024.6, 'conflict'),
    (23, 'DELHI110063H01-B01F03U01', 7, 11, 1, 3, 1, 9.0, 12.0, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 3024.6, 'conflict'),
    (24, 'DELHI110063H01-B01F04U01', 7, 11, 2, 4, 1, 12.0, 15.0, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 3024.6, 'conflict'),
    (25, 'DELHI110063H01-B01F05U01', 7, 11, 3, 5, 1, 15.0, 18.0, ST_GeomFromText('POLYGON((77.1100 28.6735, 77.1107 28.6735, 77.1107 28.6739, 77.1100 28.6739, 77.1100 28.6735))', 4326), 3024.6, 'conflict'),

    -- Pacific Mall (Building 8, 4 floors; F01 west-half unit overlaps full-floor unit above it)
    (26, 'DELHI110018M01-B01F00U01', 8, 12, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1062 28.6422, 77.1068 28.6422, 77.1068 28.6426, 77.1062 28.6426, 77.1062 28.6422))', 4326), 2593.3, 'verified'),
    (27, 'DELHI110018M01-B01F01U01', 8, 12, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1062 28.6422, 77.1065 28.6422, 77.1065 28.6426, 77.1062 28.6426, 77.1062 28.6422))', 4326), 1296.6, 'conflict'),
    (28, 'DELHI110018M01-B01F01U02', 8, 12, 3, 1, 2, 4.5, 7.5, ST_GeomFromText('POLYGON((77.1062 28.6422, 77.1068 28.6422, 77.1068 28.6426, 77.1062 28.6426, 77.1062 28.6422))', 4326), 2593.3, 'conflict'),
    (29, 'DELHI110018M01-B01F02U01', 8, 12, 1, 2, 1, 7.5, 10.5, ST_GeomFromText('POLYGON((77.1062 28.6422, 77.1068 28.6422, 77.1068 28.6426, 77.1062 28.6426, 77.1062 28.6422))', 4326), 2593.3, 'verified'),
    (30, 'DELHI110018M01-B01F03U01', 8, 12, 2, 3, 1, 10.5, 13.5, ST_GeomFromText('POLYGON((77.1062 28.6422, 77.1068 28.6422, 77.1068 28.6426, 77.1062 28.6426, 77.1062 28.6422))', 4326), 2593.3, 'verified'),

    -- Jwala Heri Market (Building 9; F01 has two identical units -> duplicate)
    (31, 'DELHI110087J01-B01F00U01', 9, 13, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1016 28.6670, 77.1020 28.6670, 77.1020 28.6674, 77.1016 28.6674, 77.1016 28.6670))', 4326), 1728.4, 'verified'),
    (32, 'DELHI110087J01-B01F01U01', 9, 13, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1016 28.6670, 77.1020 28.6670, 77.1020 28.6674, 77.1016 28.6674, 77.1016 28.6670))', 4326), 1728.4, 'conflict'),
    (33, 'DELHI110087J01-B01F01U02', 9, 13, 3, 1, 2, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1016 28.6670, 77.1020 28.6670, 77.1020 28.6674, 77.1016 28.6674, 77.1016 28.6670))', 4326), 1728.4, 'conflict'),

    -- Indraprastha World School, academic block B01 (Building 10, clean)
    (34, 'DELHI110063S01-B01F00U01', 10, 14, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1076 28.6708, 77.1080 28.6708, 77.1080 28.6712, 77.1076 28.6712, 77.1076 28.6708))', 4326), 1728.4, 'verified'),
    (35, 'DELHI110063S01-B01F01U01', 10, 14, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1076 28.6708, 77.1080 28.6708, 77.1080 28.6712, 77.1076 28.6712, 77.1076 28.6708))', 4326), 1728.4, 'verified'),
    (36, 'DELHI110063S01-B01F02U01', 10, 14, 3, 2, 1, 6.0, 9.0, ST_GeomFromText('POLYGON((77.1076 28.6708, 77.1080 28.6708, 77.1080 28.6712, 77.1076 28.6712, 77.1076 28.6708))', 4326), 1728.4, 'verified'),

    -- Indraprastha World School, sports block B02 (Building 11; F01 recorded area is wrong -> area mismatch)
    (37, 'DELHI110063S01-B02F00U01', 11, 14, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1081 28.6708, 77.1084 28.6708, 77.1084 28.6711, 77.1081 28.6711, 77.1081 28.6708))', 4326), 972.2, 'verified'),
    (38, 'DELHI110063S01-B02F01U01', 11, 14, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1081 28.6708, 77.1084 28.6708, 77.1084 28.6711, 77.1081 28.6711, 77.1081 28.6708))', 4326), 500.0, 'conflict')
ON CONFLICT (property_id) DO NOTHING;

-- ----------------------------------------------------------- conflict logs
INSERT INTO conflict_logs (property_id_a, property_id_b, conflict_type, resolved)
VALUES
    -- Balaji tower boundary violations + building-parcel mismatches (20-25)
    (20, NULL, 'boundary_violation', FALSE),
    (21, NULL, 'boundary_violation', FALSE),
    (22, NULL, 'boundary_violation', FALSE),
    (23, NULL, 'boundary_violation', FALSE),
    (24, NULL, 'boundary_violation', FALSE),
    (25, NULL, 'boundary_violation', FALSE),
    (20, NULL, 'building_parcel_mismatch', FALSE),
    (21, NULL, 'building_parcel_mismatch', FALSE),
    (22, NULL, 'building_parcel_mismatch', FALSE),
    (23, NULL, 'building_parcel_mismatch', FALSE),
    (24, NULL, 'building_parcel_mismatch', FALSE),
    (25, NULL, 'building_parcel_mismatch', FALSE),
    -- Pacific Mall 3D + floor overlaps (27 vs 28)
    (27, 28, 'overlap', FALSE),
    (28, 27, 'overlap', FALSE),
    (27, 28, 'floor_overlap', FALSE),
    (28, 27, 'floor_overlap', FALSE),
    -- Jwala Heri duplicate + overlaps (32 vs 33)
    (32, 33, 'duplicate', FALSE),
    (32, 33, 'overlap', FALSE),
    (33, 32, 'overlap', FALSE),
    (32, 33, 'floor_overlap', FALSE),
    (33, 32, 'floor_overlap', FALSE),
    -- School sports block area mismatch (38)
    (38, NULL, 'area_mismatch', FALSE)
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------- sequences
SELECT setval('parcels_parcel_id_seq', COALESCE((SELECT MAX(parcel_id) FROM parcels), 1));
SELECT setval('buildings_building_id_seq', COALESCE((SELECT MAX(building_id) FROM buildings), 1));
SELECT setval('properties_property_id_seq', COALESCE((SELECT MAX(property_id) FROM properties), 1));
