-- Seed Accounts & Demo Data
-- Default Demo Password: 'demopassword123' (bcrypt hashed below)
-- Location: Bharati Vidyapeeth's College of Engineering (BVCOE), A-4 Paschim Vihar, New Delhi (28.6773° N, 77.1130° E)

INSERT INTO users (email, password_hash, role)
VALUES 
    ('admin@demo.com', '$2b$12$tPfDfzbGvhBew2h8VEk.SeAi6xKRaRj.6vz0dTTIPWPNgrBaNjfrO', 'admin'),
    ('surveyor@demo.com', '$2b$12$tPfDfzbGvhBew2h8VEk.SeAi6xKRaRj.6vz0dTTIPWPNgrBaNjfrO', 'surveyor'),
    ('citizen@demo.com', '$2b$12$tPfDfzbGvhBew2h8VEk.SeAi6xKRaRj.6vz0dTTIPWPNgrBaNjfrO', 'citizen')
ON CONFLICT (email) DO UPDATE SET password_hash = EXCLUDED.password_hash;

INSERT INTO owners (owner_id, name, contact_info)
VALUES 
    (1, 'Aarav Sharma', 'aarav@example.com'),
    (2, 'Priya Patel', 'priya@example.com'),
    (3, 'Rajesh Kumar', 'rajesh@example.com')
ON CONFLICT (owner_id) DO NOTHING;

-- 1. Insert 10 Parcels clustered around BVCOE Paschim Vihar (28.6773, 77.1130)
INSERT INTO parcels (parcel_id, ulpin_2d, boundary_geom, area_sqm)
VALUES 
    (1, 'DELHI110001P01', ST_GeomFromText('POLYGON((77.1125 28.6768, 77.1129 28.6768, 77.1129 28.6772, 77.1125 28.6772, 77.1125 28.6768))', 4326), 1000.0),
    (2, 'DELHI110001P02', ST_GeomFromText('POLYGON((77.1130 28.6768, 77.1134 28.6768, 77.1134 28.6772, 77.1130 28.6772, 77.1130 28.6768))', 4326), 1200.0),
    (3, 'DELHI110001P03', ST_GeomFromText('POLYGON((77.1135 28.6768, 77.1140 28.6768, 77.1140 28.6772, 77.1135 28.6772, 77.1135 28.6768))', 4326), 1500.0),
    (4, 'DELHI110001P04', ST_GeomFromText('POLYGON((77.1125 28.6773, 77.1129 28.6773, 77.1129 28.6777, 77.1125 28.6777, 77.1125 28.6773))', 4326), 1100.0),
    (5, 'DELHI110001P05', ST_GeomFromText('POLYGON((77.1130 28.6773, 77.1134 28.6773, 77.1134 28.6777, 77.1130 28.6777, 77.1130 28.6773))', 4326), 1300.0),
    (6, 'DELHI110001P06', ST_GeomFromText('POLYGON((77.1135 28.6773, 77.1140 28.6773, 77.1140 28.6777, 77.1135 28.6777, 77.1135 28.6773))', 4326), 1400.0),
    (7, 'DELHI110001P07', ST_GeomFromText('POLYGON((77.1125 28.6778, 77.1129 28.6778, 77.1129 28.6782, 77.1125 28.6782, 77.1125 28.6778))', 4326), 1000.0),
    (8, 'DELHI110001P08', ST_GeomFromText('POLYGON((77.1130 28.6778, 77.1134 28.6778, 77.1134 28.6782, 77.1130 28.6782, 77.1130 28.6778))', 4326), 1200.0),
    (9, 'DELHI110001P09', ST_GeomFromText('POLYGON((77.1135 28.6778, 77.1140 28.6778, 77.1140 28.6782, 77.1135 28.6782, 77.1135 28.6778))', 4326), 1600.0),
    (10, 'DELHI110001P10', ST_GeomFromText('POLYGON((77.1141 28.6778, 77.1146 28.6778, 77.1146 28.6782, 77.1141 28.6782, 77.1141 28.6778))', 4326), 1800.0)
ON CONFLICT (parcel_id) DO NOTHING;

-- 2. Insert 6 Buildings across parcels
-- Note: Building 3 on Parcel 3 has a footprint extending outside Parcel 3 boundary (Boundary Violation Conflict)
INSERT INTO buildings (building_id, parcel_id, footprint_geom, total_floors)
VALUES 
    (1, 1, ST_GeomFromText('POLYGON((77.1126 28.6769, 77.1128 28.6769, 77.1128 28.6771, 77.1126 28.6771, 77.1126 28.6769))', 4326), 3),
    (2, 2, ST_GeomFromText('POLYGON((77.1131 28.6769, 77.1133 28.6769, 77.1133 28.6771, 77.1131 28.6771, 77.1131 28.6769))', 4326), 4),
    (3, 3, ST_GeomFromText('POLYGON((77.1137 28.6769, 77.1142 28.6769, 77.1142 28.6771, 77.1137 28.6771, 77.1137 28.6769))', 4326), 3), -- extends beyond 77.1140 boundary
    (4, 4, ST_GeomFromText('POLYGON((77.1126 28.6774, 77.1128 28.6774, 77.1128 28.6776, 77.1126 28.6776, 77.1126 28.6774))', 4326), 3),
    (5, 5, ST_GeomFromText('POLYGON((77.1131 28.6774, 77.1133 28.6774, 77.1133 28.6776, 77.1131 28.6776, 77.1131 28.6774))', 4326), 3),
    (6, 6, ST_GeomFromText('POLYGON((77.1136 28.6774, 77.1139 28.6774, 77.1139 28.6776, 77.1136 28.6776, 77.1136 28.6774))', 4326), 2)
ON CONFLICT (building_id) DO NOTHING;

-- 3. Insert 19 Properties across the 6 Buildings
INSERT INTO properties (
    property_id, ulpin_3d, building_id, parcel_id, owner_id, floor_number, unit_index, 
    elevation_min_m, elevation_max_m, footprint_geom, area_sqm, verification_status
)
VALUES 
    -- Building 1 (Parcel 1, 3 floors)
    (1, 'DELHI110001P01-B01F00U01', 1, 1, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1126 28.6769, 77.1128 28.6769, 77.1128 28.6771, 77.1126 28.6771, 77.1126 28.6769))', 4326), 433.5, 'verified'),
    (2, 'DELHI110001P01-B01F01U01', 1, 1, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1126 28.6769, 77.1128 28.6769, 77.1128 28.6771, 77.1126 28.6771, 77.1126 28.6769))', 4326), 433.5, 'verified'),
    (3, 'DELHI110001P01-B01F02U01', 1, 1, 3, 2, 1, 6.0, 9.0, ST_GeomFromText('POLYGON((77.1126 28.6769, 77.1128 28.6769, 77.1128 28.6771, 77.1126 28.6771, 77.1126 28.6769))', 4326), 433.5, 'verified'),

    -- Building 2 (Parcel 2, 4 floors)
    (4, 'DELHI110001P02-B01F00U01', 2, 2, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1131 28.6769, 77.1133 28.6769, 77.1133 28.6771, 77.1131 28.6771, 77.1131 28.6769))', 4326), 433.5, 'verified'),
    (5, 'DELHI110001P02-B01F01U01', 2, 2, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1131 28.6769, 77.1133 28.6769, 77.1133 28.6771, 77.1131 28.6771, 77.1131 28.6769))', 4326), 433.5, 'verified'),
    (6, 'DELHI110001P02-B01F02U01', 2, 2, 3, 2, 1, 6.0, 9.0, ST_GeomFromText('POLYGON((77.1131 28.6769, 77.1133 28.6769, 77.1133 28.6771, 77.1131 28.6771, 77.1131 28.6769))', 4326), 433.5, 'verified'),
    (7, 'DELHI110001P02-B01F03U01', 2, 2, 1, 3, 1, 9.0, 12.0, ST_GeomFromText('POLYGON((77.1131 28.6769, 77.1133 28.6769, 77.1133 28.6771, 77.1131 28.6771, 77.1131 28.6769))', 4326), 433.5, 'verified'),

    -- Building 3 (Parcel 3, 3 floors) - Boundary Violation
    (8, 'DELHI110001P03-B01F00U01', 3, 3, 2, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1137 28.6769, 77.1142 28.6769, 77.1142 28.6771, 77.1137 28.6771, 77.1137 28.6769))', 4326), 1083.7, 'conflict'),
    (9, 'DELHI110001P03-B01F01U01', 3, 3, 3, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1137 28.6769, 77.1142 28.6769, 77.1142 28.6771, 77.1137 28.6771, 77.1137 28.6769))', 4326), 1083.7, 'conflict'),
    (10, 'DELHI110001P03-B01F02U01', 3, 3, 1, 2, 1, 6.0, 9.0, ST_GeomFromText('POLYGON((77.1137 28.6769, 77.1142 28.6769, 77.1142 28.6771, 77.1137 28.6771, 77.1137 28.6769))', 4326), 1083.7, 'conflict'),

    -- Building 4 (Parcel 4, 3 floors)
    (11, 'DELHI110001P04-B01F00U01', 4, 4, 2, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1126 28.6774, 77.1128 28.6774, 77.1128 28.6776, 77.1126 28.6776, 77.1126 28.6774))', 4326), 433.5, 'verified'),
    (12, 'DELHI110001P04-B01F01U01', 4, 4, 3, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1126 28.6774, 77.1128 28.6774, 77.1128 28.6776, 77.1126 28.6776, 77.1126 28.6774))', 4326), 433.5, 'verified'),
    (13, 'DELHI110001P04-B01F02U01', 4, 4, 1, 2, 1, 6.0, 9.0, ST_GeomFromText('POLYGON((77.1126 28.6774, 77.1128 28.6774, 77.1128 28.6776, 77.1126 28.6776, 77.1126 28.6774))', 4326), 433.5, 'verified'),

    -- Building 5 (Parcel 5, 3 floors) - Partial 3D Overlap (Property 15 is West half, Property 16 is Full floor)
    (14, 'DELHI110001P05-B01F00U01', 5, 5, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1131 28.6774, 77.1133 28.6774, 77.1133 28.6776, 77.1131 28.6776, 77.1131 28.6774))', 4326), 433.5, 'verified'),
    (15, 'DELHI110001P05-B01F01U01', 5, 5, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1131 28.6774, 77.1132 28.6774, 77.1132 28.6776, 77.1131 28.6776, 77.1131 28.6774))', 4326), 216.8, 'conflict'),
    (16, 'DELHI110001P05-B01F01U02', 5, 5, 3, 1, 2, 4.5, 7.5, ST_GeomFromText('POLYGON((77.1131 28.6774, 77.1133 28.6774, 77.1133 28.6776, 77.1131 28.6776, 77.1131 28.6774))', 4326), 433.5, 'conflict'),

    -- Building 6 (Parcel 6, 2 floors)
    (17, 'DELHI110001P06-B01F00U01', 6, 6, 1, 0, 1, 0.0, 3.0, ST_GeomFromText('POLYGON((77.1136 28.6774, 77.1139 28.6774, 77.1139 28.6776, 77.1136 28.6776, 77.1136 28.6774))', 4326), 650.2, 'verified'),
    (18, 'DELHI110001P06-B01F01U01', 6, 6, 2, 1, 1, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1136 28.6774, 77.1139 28.6774, 77.1139 28.6776, 77.1136 28.6776, 77.1136 28.6774))', 4326), 650.2, 'conflict'),
    -- Property 19: Identical footprint and identical elevation to Property 18 (Duplicate Conflict)
    (19, 'DELHI110001P06-B01F01U02', 6, 6, 3, 1, 2, 3.0, 6.0, ST_GeomFromText('POLYGON((77.1136 28.6774, 77.1139 28.6774, 77.1139 28.6776, 77.1136 28.6776, 77.1136 28.6774))', 4326), 650.2, 'conflict')
ON CONFLICT (property_id) DO NOTHING;

-- Seed Initial Conflict Logs (11 baseline logs matching the 7 PostGIS geometric checks)
INSERT INTO conflict_logs (property_id_a, property_id_b, conflict_type, resolved)
VALUES 
    -- Building 3 Boundary Violations & Building-Parcel Mismatches (Properties 8, 9, 10)
    (8, NULL, 'boundary_violation', FALSE),
    (9, NULL, 'boundary_violation', FALSE),
    (10, NULL, 'boundary_violation', FALSE),
    (8, NULL, 'building_parcel_mismatch', FALSE),
    (9, NULL, 'building_parcel_mismatch', FALSE),
    (10, NULL, 'building_parcel_mismatch', FALSE),
    -- Building 5 3D Spatial & Floor Overlaps (Properties 15 and 16)
    (15, 16, 'overlap', FALSE),
    (16, 15, 'overlap', FALSE),
    (15, 16, 'floor_overlap', FALSE),
    (16, 15, 'floor_overlap', FALSE),
    -- Building 6 Duplicate Property (Properties 18 and 19)
    (18, 19, 'duplicate', FALSE)
ON CONFLICT DO NOTHING;

