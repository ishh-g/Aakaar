-- 3D ULPIN Generation & Vertical Property Mapping System - Schema
-- Database: PostgreSQL + PostGIS

CREATE EXTENSION IF NOT EXISTS postgis;

-- Clean drop existing tables for deterministic reset
DROP TABLE IF EXISTS conflict_logs CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS buildings CASCADE;
DROP TABLE IF EXISTS parcels CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS owners CASCADE;

-- Enum Types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'surveyor', 'citizen');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE property_verification_status AS ENUM ('unverified', 'verified', 'conflict');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE conflict_type AS ENUM (
        'overlap',
        'boundary_violation',
        'floor_overlap',
        'building_parcel_mismatch',
        'area_mismatch',
        'elevation_conflict',
        'duplicate'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 1. Owner Table
CREATE TABLE owners (
    owner_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255)
);

-- 2. User Table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'citizen'
);

-- 3. Parcel Table
CREATE TABLE IF NOT EXISTS parcels (
    parcel_id SERIAL PRIMARY KEY,
    ulpin_2d VARCHAR(14) UNIQUE NOT NULL,
    boundary_geom GEOMETRY(Polygon, 4326) NOT NULL,
    area_sqm DOUBLE PRECISION NOT NULL
);

-- 4. Building Table
CREATE TABLE IF NOT EXISTS buildings (
    building_id SERIAL PRIMARY KEY,
    parcel_id INT NOT NULL REFERENCES parcels(parcel_id) ON DELETE CASCADE,
    footprint_geom GEOMETRY(Polygon, 4326) NOT NULL,
    total_floors INT NOT NULL DEFAULT 1
);

-- 5. Property (3D volume) Table
CREATE TABLE IF NOT EXISTS properties (
    property_id SERIAL PRIMARY KEY,
    ulpin_3d VARCHAR(30) UNIQUE NOT NULL,
    building_id INT NOT NULL REFERENCES buildings(building_id) ON DELETE CASCADE,
    parcel_id INT NOT NULL REFERENCES parcels(parcel_id) ON DELETE CASCADE,
    owner_id INT REFERENCES owners(owner_id) ON DELETE SET NULL,
    floor_number INT NOT NULL DEFAULT 0,
    unit_index INT NOT NULL DEFAULT 1,
    elevation_min_m DOUBLE PRECISION NOT NULL,
    elevation_max_m DOUBLE PRECISION NOT NULL,
    footprint_geom GEOMETRY(Polygon, 4326) NOT NULL,
    volume_geom GEOMETRY(PolyhedralSurfaceZ, 4326),
    area_sqm DOUBLE PRECISION NOT NULL,
    verification_status property_verification_status NOT NULL DEFAULT 'unverified',
    CONSTRAINT unique_property_tuple UNIQUE (parcel_id, building_id, floor_number, unit_index)
);

-- 6. ConflictLog Table
CREATE TABLE IF NOT EXISTS conflict_logs (
    conflict_id SERIAL PRIMARY KEY,
    property_id_a INT NOT NULL REFERENCES properties(property_id) ON DELETE CASCADE,
    property_id_b INT REFERENCES properties(property_id) ON DELETE CASCADE,
    conflict_type conflict_type NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN NOT NULL DEFAULT FALSE
);

-- Spatial Indexes
CREATE INDEX IF NOT EXISTS idx_parcels_boundary ON parcels USING GIST (boundary_geom);
CREATE INDEX IF NOT EXISTS idx_buildings_footprint ON buildings USING GIST (footprint_geom);
CREATE INDEX IF NOT EXISTS idx_properties_footprint ON properties USING GIST (footprint_geom);
