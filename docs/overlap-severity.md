# 3D Overlap Severity — Technical Notes

Baseline: `ishh-g/Aakaar` @ `8b84e13` (Round 1 submission).
No database schema changes. Severity is computed on every
`GET /properties/conflicts` request.

## Files changed

| File | Change |
|---|---|
| `backend/app/services/conflicts.py` | `calculate_overlap_severity()` + `get_unresolved_conflicts_with_severity()`; single PostGIS query computes intersection area, elevation overlap, and both property volumes |
| `backend/app/api/conflicts.py` | `ConflictLogResponse` gains `overlap_volume_m3` and `overlap_pct`; endpoint returns the enriched rows |
| `frontend/src/components/ConflictsDashboard.jsx` | Two new columns, click-to-sort on overlap volume (nulls last), colour-coded severity |
| `backend/tests/test_overlap_severity.py` | Known-geometry calculation tests + API response-shape / failure-case test |

## Formula

For conflict types **`overlap`**, **`floor_overlap`** and **`duplicate`**
(the three two-property types):

```
overlap_area_m2   = ST_Area(ST_Intersection(a.footprint_geom, b.footprint_geom)::geography)
overlap_height_m  = max(0, min(a.elev_max, b.elev_max) - max(a.elev_min, b.elev_min))
overlap_volume_m3 = overlap_area_m2 * overlap_height_m
volume_x_m3       = ST_Area(x.footprint_geom::geography) * (x.elev_max - x.elev_min)
overlap_pct       = overlap_volume_m3 / min(volume_a_m3, volume_b_m3) * 100
```

- `::geography` gives true ground area in m² on the WGS84 ellipsoid, so no
  Web-Mercator area distortion at Delhi's latitude (~28.6° N).
- All other conflict types (`boundary_violation`, `building_parcel_mismatch`,
  `area_mismatch`, `elevation_conflict`) return `null` for both fields.
- The query uses `LEFT JOIN properties` on both sides. A conflict row whose
  property no longer exists yields `NULL` metrics → `null` severity, never a 500.

## Hand calculation — Bharat Mandapam (properties 40 and 41)

Geometry (EPSG:4326), building 12:

- Property 40 (west half): lon `77.2422 → 77.2425`, lat `28.6192 → 28.6196`,
  elevation `5.0 → 10.0 m`
- Property 41 (whole floor): lon `77.2422 → 77.2428`, lat `28.6192 → 28.6196`,
  elevation `7.5 → 12.5 m`

True ground areas (WGS84 geodesic, same basis as PostGIS `geography`):

| Quantity | Value |
|---|---|
| Property 40 footprint area | **1300.611341 m²** |
| Property 41 footprint area | **2601.222683 m²** |
| Footprint intersection (property 40 is inside 41) | **1300.611341 m²** |
| Overlapping elevation band `min(10, 12.5) − max(5, 7.5)` | **2.5 m** |
| **Overlap volume** `1300.611341 × 2.5` | **3251.528353 → 3251.53 m³** |
| Property 40 volume `1300.611341 × 5` | 6503.056707 m³ |
| Property 41 volume `2601.222683 × 5` | 13006.113413 m³ |
| Smaller volume | 6503.056707 m³ |
| **Overlap percentage** `3251.528353 ÷ 6503.056707 × 100` | **50.00 %** |

So the API should show `overlap_volume_m3 ≈ 3251.53` and `overlap_pct = 50.0`
for the 40/41 rows. (PostGIS `ST_Area(geography)` uses the same WGS84
ellipsoid; expect agreement within centimetres of area.)

Other seeded demo rows:

| Pair | Geometry | Overlap height | Expected % |
|---|---|---|---|
| 27 / 28 (Pacific Mall) | west half inside full floor | 1.5 m of 3 m | 50.00 % |
| 18 / 19 (BVCOE duplicate) | identical footprints | 3 m of 3 m | 100.00 % |
| 32 / 33 (Jwala Heri duplicate) | identical footprints | 3 m of 3 m | 100.00 % |

## Edge cases

- **Touch at boundary only** → intersection is a line/point, area `0` →
  `(null, null)`.
- **Footprint overlaps but elevation bands do not** → height `0` →
  `(null, null)`.
- **Either property missing** → `null` metrics → `(null, null)`, response 200.
- Invalid/zero/negative dimensions → `(null, null)`.

## Tests

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests/test_overlap_severity.py --noconftest -q
```

`--noconftest` is only used in this sandbox because no PostGIS database is
available locally. With the event database running, the normal command works:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Current result: **25 passed** (all DB-free unit tests incl. the 5 new tests).

## Demo script (~3 minutes)

1. Log in as admin, open **Conflicts Dashboard**.
2. Point out the two new columns: **Overlap Volume (m³)** and **Overlap %**.
3. Click the **Overlap Volume** header to sort descending.
4. The Bharat Mandapam rows (properties 40/41) show **3,251.53 m³ / 50.00 %**
   (red = high severity).
5. Click **Inspect on 3D Map** on property 40 → red volume next to 41.
6. Show this note's hand calculation: `1300.61 m² × 2.5 m = 3251.53 m³`,
   `3251.53 ÷ 6503.06 = 50 %`.
7. Point out boundary-violation rows show `—` (null), and filters/search still work.

## Severity colour thresholds (stretch goal)

`overlap_pct` ≥ 50 % → red **High**; ≥ 10 % → amber **Medium**; else green **Low**.
