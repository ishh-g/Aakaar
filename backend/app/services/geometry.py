from shapely.geometry import Polygon, shape
from shapely.wkt import loads as wkt_loads
from typing import Union

def parse_footprint_geometry(geom_input: Union[str, dict, Polygon]) -> Polygon:
    """
    Parses footprint input (WKT string, GeoJSON dict, or Shapely Polygon) into a valid 2D Shapely Polygon.
    """
    if isinstance(geom_input, Polygon):
        return geom_input
    elif isinstance(geom_input, str):
        parsed = wkt_loads(geom_input)
        if not isinstance(parsed, Polygon):
            raise ValueError("Input WKT geometry is not a Polygon.")
        return parsed
    elif isinstance(geom_input, dict):
        parsed = shape(geom_input)
        if not isinstance(parsed, Polygon):
            raise ValueError("Input GeoJSON geometry is not a Polygon.")
        return parsed
    else:
        raise ValueError(f"Unsupported geometry type: {type(geom_input)}")

def extrude_footprint_to_polyhedral_surface(
    footprint: Union[str, dict, Polygon],
    elevation_min: float,
    elevation_max: float
) -> str:
    """
    Extrudes a 2D footprint polygon into a closed 3D prism PolyhedralSurfaceZ WKT string.

    :param footprint: 2D Polygon geometry (WKT string, GeoJSON dict, or Shapely Polygon)
    :param elevation_min: Minimum elevation in meters (z_min)
    :param elevation_max: Maximum elevation in meters (z_max)
    :return: POLYHEDRALSURFACE Z WKT string representation
    """
    poly = parse_footprint_geometry(footprint)
    if elevation_max <= elevation_min:
        raise ValueError(f"elevation_max ({elevation_max}) must be strictly greater than elevation_min ({elevation_min}).")

    coords = list(poly.exterior.coords)
    # Remove duplicate last coordinate for processing edges
    if coords[0] == coords[-1] and len(coords) > 1:
        ring = coords[:-1]
    else:
        ring = coords

    faces = []

    # 1. Bottom Face (z = elevation_min)
    bottom_pts = [f"{x} {y} {elevation_min}" for x, y in coords]
    faces.append(f"(({', '.join(bottom_pts)}))")

    # 2. Top Face (z = elevation_max, reversed orientation for outward normal)
    top_pts = [f"{x} {y} {elevation_max}" for x, y in reversed(coords)]
    faces.append(f"(({', '.join(top_pts)}))")

    # 3. Side Wall Faces
    n = len(ring)
    for i in range(n):
        p1 = ring[i]
        p2 = ring[(i + 1) % n]
        
        side_pts = [
            f"{p1[0]} {p1[1]} {elevation_min}",
            f"{p2[0]} {p2[1]} {elevation_min}",
            f"{p2[0]} {p2[1]} {elevation_max}",
            f"{p1[0]} {p1[1]} {elevation_max}",
            f"{p1[0]} {p1[1]} {elevation_min}"  # Close ring
        ]
        faces.append(f"(({', '.join(side_pts)}))")

    polyhedral_wkt = f"POLYHEDRALSURFACE Z ({', '.join(faces)})"
    return polyhedral_wkt
