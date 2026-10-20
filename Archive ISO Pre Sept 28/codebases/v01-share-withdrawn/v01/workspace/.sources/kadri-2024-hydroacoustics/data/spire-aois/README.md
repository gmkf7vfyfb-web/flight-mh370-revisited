# Spire/Kpler historical-AIS areas of interest

Run from this source directory:

```bash
python3 code/build_spire_aois.py
```

The GeoJSON coordinate order is longitude, latitude in WGS84/OGC:CRS84.

- `huzzas-geo-caspian-operational-area.geojson` is the upload-facing
  FeatureCollection for the published NOPSEMA operational polygon of the Huzzas
  survey undertaken by *Geo Caspian*. It is deliberately the full regulatory
  area rather than a guessed vessel position.
- `huzzas-geo-caspian-operational-area-geometry.json` is the same polygon as a
  bare GeoJSON geometry for direct API arguments.
- `seventh-arc-100nm-corridor.geojson` is a single polygon extending 100 NM on
  either side of the official ATSB FL400 seventh-arc reference from 20°S to its
  southern endpoint. The source arc ends at about 43.91°S, so there is no
  authoritative centreline to extend to 45°S. Its perpendicular 100 NM edge
  does extend south of 45°S. This file is an upload-facing FeatureCollection;
  `seventh-arc-100nm-corridor-geometry.json` is its bare API geometry.
- `seventh-arc-100nm-corridor-query-tiles.geojson` is a FeatureCollection of
  contiguous 100 km along-arc tiles. Each tile is below the documented
  50,000 km² limit for one Historical Vessel Points/Tracks spatiotemporal
  request. Extract and query one feature geometry at a time; submitting the
  complete FeatureCollection is not a single compliant HVP/HVT request.
- `manifest.json` records areas, bounds, source identity, source hash and useful
  UTC retrieval windows.

For the seventh arc, start with the padded 00:00–01:00 UTC window on 8 March
2014; the declared impact-control interval is 00:19:37–00:49:37 UTC. For the
survey vessel, 22:00–03:00 UTC supplies track context around midnight. These are
retrieval choices, not new scientific constraints.

Spire/Kpler accepts a closed Polygon or MultiPolygon as GeoJSON or WKT for an
area of interest. Historical Vessel Points/Tracks requests are documented as
having both a 50,000 km² maximum area and a 24-hour maximum duration per
request. The full corridor file is therefore for inspection or services that
permit a larger AOI; use the tiled file for HVP/HVT retrieval.
