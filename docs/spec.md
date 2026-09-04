# 3D ULPIN Generation and Vertical Property Mapping System (SIH26011) — Technical Spec (Source of Truth)

> Do not redesign anything this spec already defines. Verify existing code against it.

## Purpose

Software prototype: upload GIS/building data → auto-segment 3D property volumes → assign 3D ULPINs → detect spatial conflicts → visualize on an interactive 3D map → generate reports. Demo location: Bharati Vidyapeeth's College of Engineering, Delhi (~28.6773°N, 77.1130°E).

## Tech Stack

- Backend: Python FastAPI
- Database: PostgreSQL + PostGIS
- Frontend: React + Vite + CesiumJS
- Auth: JWT + role-based access (admin, surveyor, citizen)

## Data Model (already implemented — verify against actual schema.sql)

- Parcel: parcel_id, ulpin_2d, boundary_geom (POLYGON), area_sqm
- Building: building_id, parcel_id (FK), footprint_geom (POLYGON), total_floors
- Property: property_id, ulpin_3d, building_id (FK), parcel_id (FK), owner_id (FK),
  floor_number, elevation_min_m, elevation_max_m, footprint_geom,
  volume_geom (POLYHEDRALSURFACE Z), area_sqm, verification_status
- Owner: owner_id, name, contact_info
- User: user_id, email, password_hash, role ('admin'/'surveyor'/'citizen')
- ConflictLog: conflict_id, property_id_a, property_id_b (nullable), conflict_type,
  detected_at, resolved

## 3D ULPIN Encoding (already implemented — verify against actual ulpin.py)

3D-ULPIN = `<2D_ULPIN>-<BLDG><FLOOR><UNIT>`

Example: XXXXAAAA1234-B01F03U02

- B\<NN\> = building index, F\<NN\> = floor (FB1/FB2 for basements), U\<NN\> = unit

## Spatial Conflict Detection Algorithm (NOT yet implemented — this is next)

| Conflict type | Detection logic |
|---|---|
| Property overlap | ST_3DIntersects(volume_a, volume_b) between properties not in parent-child relation |
| Boundary violation | NOT ST_Contains(parcel.boundary_geom, building.footprint_geom) |
| Floor overlap | Two properties in same building with overlapping elevation ranges |
| Building-parcel mismatch | ST_Overlaps or ST_Disjoint between building footprint and parcel boundary |
| Area mismatch | abs(recorded_area - ST_Area(footprint_geom)) / ST_Area(footprint_geom) > 0.05 |
| Elevation/height conflict | Recorded floor height vs actual elevation range differs beyond tolerance |
| Duplicate property | ST_Equals-equivalent footprint AND overlapping elevation range |

Each check writes a ConflictLog row and sets verification_status to 'conflict'.

## Core API Endpoints (some implemented — verify against actual code)

- POST   /auth/login
- POST   /parcels/upload
- POST   /buildings/{parcel_id}
- POST   /properties/generate
- GET    /properties/{ulpin_3d}
- GET    /properties/conflicts
- POST   /properties/{id}/verify
- GET    /map/tiles
- GET    /reports/summary

No signup endpoint — login only against pre-seeded accounts (admin@demo.com, surveyor@demo.com, citizen@demo.com).

## What's Already Done (verify, don't redo)

- Monorepo scaffold (/backend, /frontend, /db) — running successfully
- Full DB schema + seed data: 10 parcels, 6 buildings, 18 properties, 3 users
- generate_3d_ulpin() function, unit tested, wired into property creation
- Auto-segmentation service (footprint → 3D floor volumes), unit tested
- JWT auth backend (login, password hashing, role-restricted endpoints) — may have just been added manually, verify it's present and working

## What's Still To Build, In Order

1. Conflict detection service — implement all 7 checks above using real PostGIS geometry functions, not approximations. Wire it to run automatically after segmentation and expose as an on-demand re-check endpoint.
2. Remaining API endpoints — whatever from the list above isn't wired up yet.
3. Frontend: 3D map rendering — draw the actual parcels/buildings/property volumes on the Cesium globe, colored by verification_status (green=verified, red=conflict, gray=unverified), clickable for a detail panel. Default camera should fly to the BVCOE coordinates on load, not the whole globe.
4. Frontend: login screen + conflicts dashboard — gate the app behind login, list unresolved conflicts with a Verify button (admin/surveyor only).
5. Frontend: reports/analytics page — counts by status and conflict type.

## Deliberately Seeded Conflict Fixtures (must survive until conflict detection runs)

- Properties 15/16 (Building 5): deliberately overlapping 3D elevation ranges (3.0–6.0m vs 4.5–7.5m).
- Properties 8/9/10 (Building 3): footprints deliberately extending outside their parcel boundary (building footprint extends beyond 77.2195).
- conflict_logs seeded with 4 rows: (15,16,'overlap'), (8,NULL,'boundary_violation'), (9,NULL,'boundary_violation'), (10,NULL,'boundary_violation').
- The segmentation service uses an upsert (ON CONFLICT ... DO UPDATE) and can silently overwrite these rows when re-run — it must refuse to run on buildings containing verification_status='conflict' rows unless force=True.
