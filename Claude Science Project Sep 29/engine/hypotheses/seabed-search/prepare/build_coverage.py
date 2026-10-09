#!/usr/bin/env python3
"""Build the seabed-search coverage rasters used by hypotheses/seabed-search.

Each campaign becomes one raster on a 0.01 degree grid. A cell holds the fraction of its
area in which the campaign recorded valid sonar data (or, for the inferred Ocean Infinity
variant, the fraction inside the traced outline). The module reads these rasters; nothing
here enters the estimate except through them.

    .venv/bin/python hypotheses/seabed-search/prepare/build_coverage.py [--refresh]

Phase 2 (2014-2017) is measured from the four 5 m backscatter mosaics Geoscience Australia
publishes as cloud-optimised GeoTIFFs inside one 5.7 GB zip. Each mosaic is streamed with
HTTP range requests and never written to disk: every full-resolution tile is inflated,
its valid pixels (not 0, not 256) are counted into 0.001 degree cells, and the tile is
dropped. The zip CRC-32s are checked end to end. Per-sensor counts are cached in
data/external/search-coverage/ so later steps rerun in seconds.

The vector layers (Phase 2 deep-tow footprint, Bluefin-21 display polygons, the Ocean
Infinity 2018 outline) are rasterised at the same 0.001 degree cell centres.

The Ocean Infinity 2018 outline is a community tracing of unclear licence, so neither it
nor its raster is in git: the outline is read from, and the raster written to,
data/external/search-coverage/ (the outline's provenance is in its properties).

Outputs:
  hypotheses/seabed-search/coverage/<campaign>.cov   embedded rasters, from CC BY 4.0 GA data
  data/external/search-coverage/                     per-sensor caches; ocean-infinity-2018.cov
  runs/seabed-search-analysis/coverage.pdf (+ .png)  maps and the area checks
"""

import argparse
import hashlib
import json
import math
import struct
import sys
import time
import urllib.request
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
CACHE = ROOT / "data" / "external" / "search-coverage"
FIGURES = ROOT / "runs" / "seabed-search-analysis"

R_KM = 6371.0072  # authalic radius: the sphere with the WGS-84 ellipsoid's area

ZIP_URL = "https://files.ausseabed.gov.au/survey/MH370-Phase2-SOnarImagery-Backscatter-5m-2018.zip"
SENSORS = {  # label -> entry in the GA zip (each holds one COG)
    "deep-tow": "Deep Tow Side Scan Sonar 2014-2016 5m.zip",
    "go-phoenix": "GoPhoenix Synthetic Aperture Sonar 2014-2015 5m.zip",
    "dhj": "DHJ Synthetic Aperture Sonar 2016 5m.zip",
    "auv": "Autonomous Underwater Vehicle Side Scan Sonar 2015-2017 5m.zip",
}
NODATA = (0, 256)  # 0 everywhere; DHJ also pads its blocks with 256
DEEP_TOW_WFS = (
    "https://warehouse.ausseabed.gov.au/geoserver/wfs?service=WFS&version=2.0.0&request=GetFeature"
    "&outputFormat=application%2Fjson&srsName=EPSG%3A4326&typeNames=ausseabed%3A"
    "MH370_Phase_2_Sonar_Imagery_Backscatter_Inverse_Deep_Tow__SSS__5m_2018_L0_Coverage"
)
# Canonical JSON (volatile timeStamp removed) as retrieved 31 Aug and again 25 Sep 2026.
DEEP_TOW_WFS_SHA256 = "6591be13bbd38ce9de3ae2208a82cb8524184e3ef2cf1e2a46f2468f84e488c8"
BLUEFIN_URL = (
    "https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Bluefin_21_AreaSearched2014"
    "/FeatureServer/0/query?where=1%3D1&outFields=%2A&returnGeometry=true&outSR=4326&f=geojson"
)
OI_2018_OUTLINE = CACHE / "ocean-infinity-2018-outline.geojson"

FINE = 0.001  # degrees; per-sensor counting and unions happen at this resolution
COARSE = 0.01  # degrees; the module rasters
BLOCK = 10  # fine cells per coarse cell, each way
# Grids as (south, west, rows, cols) in COARSE cells; FINE grids are BLOCK times denser.
GRIDS = {
    "phase2": (-40.2, 85.0, 760, 1150),
    "bluefin-2014": (-21.4, 103.7, 60, 60),
    "ocean-infinity-2018": (-35.8, 90.9, 1120, 1150),
}


# ---------------------------------------------------------------- HTTP and zip streaming

def http(url, start=None, end=None):
    headers = {"User-Agent": "mh370-seabed-search/1"}
    if start is not None:
        headers["Range"] = f"bytes={start}-{end}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=300)


def byte_range(url, start, length, chunk=1 << 22, retries=5):
    """Yield bytes [start, start + length) of url, resuming after dropped connections."""
    done = 0
    while done < length:
        try:
            with http(url, start + done, start + length - 1) as r:
                while done < length:
                    block = r.read(min(chunk, length - done))
                    if not block:
                        raise ConnectionError("short read")
                    done += len(block)
                    yield block
        except (OSError, ConnectionError) as e:
            retries -= 1
            if retries < 0:
                raise
            print(f"  connection dropped at {done:,} bytes ({e}); resuming", file=sys.stderr)
            time.sleep(5)


def zip_entries(url):
    """Central directory of a remote zip64 archive: name -> (local offset, method, size, crc)."""
    with http(url, 0, 0) as r:
        total = int(r.headers["Content-Range"].split("/")[1])
    tail = b"".join(byte_range(url, total - 65536, 65536))
    loc = tail.rfind(b"PK\x06\x07")
    eocd64 = struct.unpack("<Q", tail[loc + 8:loc + 16])[0]
    rec = b"".join(byte_range(url, eocd64, 56))
    cd_size, cd_offset = struct.unpack("<QQ", rec[40:56])
    cd = b"".join(byte_range(url, cd_offset, cd_size))
    entries, i = {}, 0
    while cd[i:i + 4] == b"PK\x01\x02":
        method, crc, csize, usize, nlen, xlen, clen = struct.unpack("<H4xIIIHHH", cd[i + 10:i + 34])
        offset = struct.unpack("<I", cd[i + 42:i + 46])[0]
        name = cd[i + 46:i + 46 + nlen].decode()
        extra = cd[i + 46 + nlen:i + 46 + nlen + xlen]
        j = 0
        while j < len(extra):  # zip64 fields replace the 0xFFFFFFFF placeholders, in order
            tag, size = struct.unpack("<HH", extra[j:j + 4])
            if tag == 1:
                vals = list(struct.unpack(f"<{size // 8}Q", extra[j + 4:j + 4 + size]))
                if usize == 0xFFFFFFFF:
                    usize = vals.pop(0)
                if csize == 0xFFFFFFFF:
                    csize = vals.pop(0)
                if offset == 0xFFFFFFFF:
                    offset = vals.pop(0)
            j += 4 + size
        entries[name] = (offset, method, csize, crc)
        i += 46 + nlen + xlen + clen
    return entries


class Stream:
    """Sequential reads over an iterator of byte chunks, with a running CRC-32."""

    def __init__(self, chunks):
        self.chunks, self.buf, self.crc = iter(chunks), b"", 0

    def read(self, n):
        while len(self.buf) < n:
            block = next(self.chunks, b"")
            if not block:
                break
            self.crc = zlib.crc32(block, self.crc)
            self.buf += block
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def rest(self):
        if self.buf:
            yield self.buf
            self.buf = b""
        for block in self.chunks:
            self.crc = zlib.crc32(block, self.crc)
            yield block


def inflate(chunks):
    d = zlib.decompressobj(-15)
    for block in chunks:
        out = d.decompress(block)
        if out:
            yield out
    yield d.flush()


def cog_bytes(url, entry, check):
    """The GeoTIFF inside one entry of the GA zip (a zip inside the zip), as a byte stream.
    `check` receives (what, expected crc, actual crc) once the stream is exhausted."""
    offset, method, csize, crc = entry
    head = b"".join(byte_range(url, offset, 30))
    nlen, xlen = struct.unpack("<HH", head[26:30])
    outer = byte_range(url, offset + 30 + nlen + xlen, csize)
    inner = Stream(inflate(outer) if method == 8 else outer)
    head = inner.read(30)
    assert head[:4] == b"PK\x03\x04" and struct.unpack("<H", head[8:10])[0] == 8, "unexpected inner entry"
    inner.read(sum(struct.unpack("<HH", head[26:30])))
    d, cog_crc, it = zlib.decompressobj(-15), 0, inner.rest()
    for block in it:
        out = d.decompress(block)
        cog_crc = zlib.crc32(out, cog_crc)
        yield out
        if d.eof:
            break
    tail = d.unused_data + b"".join(it)  # data descriptor, then the rest of the inner zip
    expected = struct.unpack("<I", tail[4:8] if tail[:4] == b"PK\x07\x08" else tail[:4])[0]
    check("COG", expected, cog_crc)
    check("inner zip", crc, inner.crc)


# ---------------------------------------------------------------- GeoTIFF tiles -> cell counts

TIFF_TYPES = {3: ("H", 2), 4: ("I", 4), 12: ("d", 8), 16: ("Q", 8)}


def first_ifd(header):
    """Tags of the first (full-resolution) image of a little-endian BigTIFF."""
    assert header[:4] == b"II+\x00", "expected a little-endian BigTIFF"
    off = struct.unpack("<Q", header[8:16])[0]
    n = struct.unpack("<Q", header[off:off + 8])[0]
    tags = {}
    for k in range(n):
        tag, typ, count = struct.unpack("<HHQ", header[off + 8 + 20 * k:off + 20 + 20 * k])
        raw = header[off + 20 + 20 * k:off + 28 + 20 * k]
        if typ not in TIFF_TYPES:
            continue
        fmt, size = TIFF_TYPES[typ]
        if size * count > 8:
            p = struct.unpack("<Q", raw)[0]
            raw = header[p:p + size * count]
        tags[tag] = struct.unpack(f"<{count}{fmt}", raw[:size * count])
    return tags


def pixels_per_cell(edges0, step, grid0, ncells, sign):
    """Pixel centres per FINE cell for the pixel lattice extended indefinitely (so partial
    cells at the raster's edge count their missing pixels as not searched)."""
    lo, hi = sorted([(grid0 - edges0) * sign / step, (grid0 + ncells * FINE - edges0) * sign / step])
    i = np.arange(math.floor(lo) - 2, math.ceil(hi) + 2)
    cell = np.floor((edges0 + sign * (i + 0.5) * step - grid0) / FINE).astype(np.int64)
    cell = cell[(cell >= 0) & (cell < ncells)]
    return np.bincount(cell, minlength=ncells)


def count_valid(chunks, grid):
    """Valid-pixel fraction (x 255, uint8) of each FINE cell of `grid` for one streamed COG."""
    south, west, rows, cols = grid
    nrow, ncol = rows * BLOCK, cols * BLOCK
    it, buf, base = iter(chunks), bytearray(), 0
    while len(buf) < 8 << 20:
        block = next(it, b"")
        if not block:
            break
        buf += block
    tags = first_ifd(bytes(buf))
    width, height, bits = tags[256][0], tags[257][0], tags[258][0]
    tw, th, offsets, sizes = tags[322][0], tags[323][0], tags[324], tags[325]
    assert tags[259][0] == 8 and tags.get(317, (1,))[0] == 1, "expected DEFLATE without predictor"
    dx, dy = tags[33550][:2]
    west0, north0 = tags[33922][3:5]
    dtype = np.dtype("<u1" if bits == 8 else "<u2")
    # Pixel rows run south; FINE rows run north from `south`.
    row_cell = np.floor((north0 - (np.arange(height) + 0.5) * dy - south) / FINE).astype(np.int64)
    col_cell = np.floor((west0 + (np.arange(width) + 0.5) * dx - west) / FINE).astype(np.int64)
    assert row_cell.min() >= 0 and row_cell.max() < nrow and col_cell.min() >= 0 and col_cell.max() < ncol
    counts = np.zeros((nrow, ncol), np.uint16)
    across = -(-width // tw)
    started, total = time.time(), len(offsets)
    for done, k in enumerate(np.argsort(offsets)):
        o, n = offsets[k], sizes[k]
        while base + len(buf) < o + n:
            block = next(it, None)
            if block is None:
                raise SystemExit("stream ended before the last tile")
            buf += block
            if o > base:
                cut = min(o - base, len(buf))
                del buf[:cut]
                base += cut
        tile = np.frombuffer(zlib.decompress(bytes(buf[o - base:o - base + n])), dtype).reshape(th, tw)
        i0, j0 = (k // across) * th, (k % across) * tw
        tile = tile[:height - i0, :width - j0]
        valid = ((tile != NODATA[0]) & (tile != NODATA[1])).view(np.uint8)
        rc, cc = row_cell[i0:i0 + tile.shape[0]], col_cell[j0:j0 + tile.shape[1]]
        rs = np.flatnonzero(np.r_[True, rc[1:] != rc[:-1]])
        cs = np.flatnonzero(np.r_[True, cc[1:] != cc[:-1]])
        block_counts = np.add.reduceat(np.add.reduceat(valid, rs, axis=0, dtype=np.uint16), cs, axis=1)
        counts[rc[-1]:rc[0] + 1, cc[0]:cc[-1] + 1] += block_counts[::-1]
        if done % 20000 == 0:
            print(f"  tile {done:,}/{total:,} ({time.time() - started:.0f} s)", file=sys.stderr)
    for _ in it:  # drain so the CRC checks see every byte
        pass
    per_row = pixels_per_cell(north0, dy, south, nrow, -1).astype(np.float32)
    per_col = pixels_per_cell(west0, dx, west, ncol, 1).astype(np.float32)
    fraction = np.empty((nrow, ncol), np.uint8)  # x 255
    for r in range(0, nrow, 500):
        total_px = per_row[r:r + 500, None] * per_col[None, :]
        fraction[r:r + 500] = np.round(255.0 * counts[r:r + 500] / np.maximum(total_px, 1))
    return fraction


def phase2_sensor(name, refresh, entries):
    path = CACHE / f"phase2-{name}.npz"
    if path.is_file() and not refresh:
        return np.load(path)["fraction"]
    problems = []

    def check(what, expected, actual):
        print(f"  {name} {what} CRC-32 {actual:08x} (zip says {expected:08x})", file=sys.stderr)
        if expected != actual:
            problems.append(what)

    started = time.time()
    fraction = count_valid(cog_bytes(ZIP_URL, entries[SENSORS[name]], check), GRIDS["phase2"])
    if problems:
        raise SystemExit(f"{name}: CRC mismatch in {problems}; nothing cached")
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, fraction=fraction)
    print(f"  {name}: {time.time() - started:.0f} s", file=sys.stderr)
    return fraction


# ---------------------------------------------------------------- vectors

def rings_of(geometry):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return [np.asarray(ring, float)[:, :2] for polygon in polygons for ring in polygon]


def ring_area_km2(ring):
    """Signed spherical area (Chamberlain & Duquette 2007) of a closed lon/lat ring."""
    lon, lat = np.radians(ring[:, 0]), np.radians(ring[:, 1])
    return -0.5 * R_KM**2 * np.sum(np.diff(lon) * (2 + np.sin(lat[:-1]) + np.sin(lat[1:])))


def polygon_area_km2(geometry):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return sum(abs(sum(ring_area_km2(np.asarray(r, float)) for r in p)) for p in polygons)


def rasterise(rings, grid):
    """FINE cells of `grid` whose centre lies inside the rings (even-odd rule)."""
    south, west, rows, cols = grid
    nrow, ncol = rows * BLOCK, cols * BLOCK
    seg = np.concatenate([np.c_[r[:-1], r[1:]] for r in rings])  # x1 y1 x2 y2
    x1, y1, x2, y2 = seg.T
    # Row r (centre y_r) is crossed when min(y1, y2) <= y_r < max(y1, y2).
    lo = np.clip(np.ceil((np.minimum(y1, y2) - south) / FINE - 0.5), 0, nrow).astype(np.int64)
    hi = np.clip(np.ceil((np.maximum(y1, y2) - south) / FINE - 0.5), 0, nrow).astype(np.int64)
    n = hi - lo
    edge = np.repeat(np.arange(len(n)), n)
    row = lo[edge] + np.arange(len(edge)) - np.repeat(np.cumsum(n) - n, n)
    y = south + (row + 0.5) * FINE
    x = x1[edge] + (y - y1[edge]) / (y2[edge] - y1[edge]) * (x2[edge] - x1[edge])
    order = np.lexsort((x, row))
    row, x = row[order], x[order]
    assert len(row) % 2 == 0 and np.all(row[0::2] == row[1::2]), "rings are not closed"
    first = np.clip(np.ceil((x[0::2] - west) / FINE - 0.5), 0, ncol).astype(np.int64)
    last = np.clip(np.ceil((x[1::2] - west) / FINE - 0.5), 0, ncol).astype(np.int64)
    diff = np.zeros((nrow, ncol + 1), np.int8)
    np.add.at(diff, (row[0::2], first), 1)
    np.add.at(diff, (row[0::2], last), -1)
    return np.cumsum(diff, axis=1, dtype=np.int8)[:, :ncol] > 0


def canonical(raw):
    doc = json.loads(raw)
    doc.pop("timeStamp", None)
    return doc, json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode() + b"\n"


def cached_download(url, name, refresh):
    path = CACHE / name
    if refresh or not path.is_file():
        CACHE.mkdir(parents=True, exist_ok=True)
        with http(url) as r:
            path.write_bytes(r.read())
    return path.read_bytes()


# ---------------------------------------------------------------- grids, areas, output
# FINE arrays are uint8 fractions x 255 (about 90 MB each); COARSE arrays are float fractions.

def coarse(fine):
    rows, cols = fine.shape[0] // BLOCK, fine.shape[1] // BLOCK
    return fine.reshape(rows, BLOCK, cols, BLOCK).sum(axis=(1, 3), dtype=np.uint32) / (BLOCK * BLOCK * 255.0)


def area_km2(values, grid, scale=1.0):
    """Area (km2) of a FINE or COARSE array of fractions (x scale) on the authalic sphere."""
    south, west, rows, cols = grid
    step = COARSE if values.shape[0] == rows else FINE
    lat = np.radians(south + np.arange(values.shape[0] + 1) * step)
    row_area = R_KM**2 * np.radians(step) * np.diff(np.sin(lat))
    return float(row_area @ values.sum(axis=1, dtype=np.float64)) / scale


def write_cov(path, fraction, grid):
    """Module raster: b"MH370COV", u32 version (1), f64 south, f64 west, f64 step (deg),
    u32 rows, u32 cols, u32 runs, then `runs` records of (u8 value, u16 count), little-endian.
    Values are the covered fraction x 255, row-major from the south-west cell."""
    south, west, rows, cols = grid
    q = np.round(np.clip(fraction, 0, 1) * 255).astype(np.uint8).ravel()
    starts = np.flatnonzero(np.r_[True, q[1:] != q[:-1]])
    lengths = np.diff(np.r_[starts, q.size])
    records = bytearray()
    runs = 0
    for s, n in zip(starts, lengths):
        while n > 0:
            records += struct.pack("<BH", q[s], min(n, 65535))
            n -= min(n, 65535)
            runs += 1
    path.write_bytes(b"MH370COV" + struct.pack("<IdddIII", 1, south, west, COARSE, rows, cols, runs) + records)
    return q.reshape(rows, cols) / 255.0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--refresh", action="store_true", help="re-download everything, ignoring the cache")
    args = parser.parse_args()
    out = MODULE / "coverage"
    out.mkdir(exist_ok=True)
    g2, gb, go = GRIDS["phase2"], GRIDS["bluefin-2014"], GRIDS["ocean-infinity-2018"]

    # Phase 2: valid 5 m pixels of the four mosaics, their union taken per FINE cell.
    cached = all((CACHE / f"phase2-{s}.npz").is_file() for s in SENSORS)
    entries = None if cached and not args.refresh else zip_entries(ZIP_URL)
    sensors = {}
    for name in SENSORS:
        print(f"Phase 2 {name}", file=sys.stderr)
        sensors[name] = phase2_sensor(name, args.refresh, entries)
    union = np.maximum.reduce(list(sensors.values()))
    phase2 = write_cov(out / "phase2.cov", coarse(union), g2)

    raw = cached_download(DEEP_TOW_WFS, "phase2-deep-tow-l0.geojson", args.refresh)
    doc, canon = canonical(raw)
    sha = hashlib.sha256(canon).hexdigest()
    deep_geometry = doc["features"][0]["geometry"]
    deep_vector = rasterise(rings_of(deep_geometry), g2)

    bluefin_doc = json.loads(cached_download(BLUEFIN_URL, "bluefin-21-area-searched-2014.geojson", args.refresh))
    bluefin_fine = rasterise([r for f in bluefin_doc["features"] for r in rings_of(f["geometry"])], gb)
    bluefin = write_cov(out / "bluefin-2014.cov", coarse(bluefin_fine.view(np.uint8) * np.uint8(255)), gb)

    # Ocean Infinity 2018 (inferred): the traced outline without the ground Phase 2 had
    # already covered, which the outline encloses where OI searched on both sides of it.
    oi_doc = json.loads(OI_2018_OUTLINE.read_text())
    oi_rings = [r for f in oi_doc["features"] for r in rings_of(f["geometry"])]
    oi_fine = rasterise(oi_rings, go).view(np.uint8) * np.uint8(255)
    r0, c0 = round((go[0] - g2[0]) / FINE), round((go[1] - g2[1]) / FINE)
    assert r0 >= 0 and c0 >= 0, "the OI grid must start inside the Phase 2 grid"
    n, m = min(g2[2] * BLOCK - r0, go[2] * BLOCK), min(g2[3] * BLOCK - c0, go[3] * BLOCK)
    oi_fine[:n, :m] = oi_fine[:n, :m].astype(np.uint16) * (255 - union[r0:r0 + n, c0:c0 + m]) // 255
    oi = write_cov(CACHE / "ocean-infinity-2018.cov", coarse(oi_fine), go)

    # Area checks against the published figures.
    rows = []
    for name, f in sensors.items():
        others = np.maximum.reduce([g for n, g in sensors.items() if n != name])
        unique = area_km2(np.clip(f.astype(np.int16) - others, 0, None), g2, 255)
        rows.append((f"Phase 2 {name}: valid 5 m pixels", area_km2(f, g2, 255), f"not seen by another sensor: {unique:,.0f} km2"))
    upper = np.minimum(255, np.sum([f.astype(np.uint16) for f in sensors.values()], axis=0))
    rows.append(("Phase 2 union (per-cell maximum; used)", area_km2(union, g2, 255),
                 f"per-cell sum bound {area_km2(upper, g2, 255):,.0f} km2; ATSB ~120,000 km2"))
    del upper
    rows.append(("Phase 2 union, module raster (0.01 deg, 8-bit)", area_km2(phase2, g2), ""))
    vec_area = polygon_area_km2(deep_geometry)
    ras_area = area_km2(deep_vector.view(np.uint8), g2)
    rows.append(("Deep-tow WFS footprint, spherical polygon area", vec_area, "its attribute: 130,961 = square degrees x 111.12^2"))
    rows.append(("Deep-tow WFS footprint, rasterised", ras_area, f"{100 * (ras_area / vec_area - 1):+.2f}% vs polygon"))
    d = sensors["deep-tow"]
    rows.append(("Deep-tow pixels outside the WFS footprint", area_km2(np.where(deep_vector, 0, d), g2, 255), ""))
    rows.append(("WFS footprint without deep-tow pixels", area_km2(np.where(deep_vector, 255 - d, 0), g2, 255), ""))
    rows.append(("GO Phoenix outside the deep-tow WFS footprint", area_km2(np.where(deep_vector, 0, sensors["go-phoenix"]), g2, 255),
                 "brief: ~14,400 km2"))
    rows.append(("Bluefin-21 display polygons, spherical", sum(polygon_area_km2(f["geometry"]) for f in bluefin_doc["features"]),
                 "ATSB reports 860 km2"))
    rows.append(("Bluefin-21, module raster", area_km2(bluefin, gb), ""))
    oi_poly = sum(polygon_area_km2(f["geometry"]) for f in oi_doc["features"])
    oi_area = area_km2(oi, go)
    rows.append(("OI 2018 outline (grade C), spherical", oi_poly, "OI: >112,000 km2 (May 2018), 120,000 km2 (data donation)"))
    rows.append(("OI 2018 outline over Phase 2 coverage", area_km2(np.where(rasterise(oi_rings, g2), union, 0), g2, 255), ""))
    rows.append(("OI 2018 layer: outline less Phase 2, module raster", oi_area,
                 f"reported area / layer: {112000 / oi_area:.3f}-{120000 / oi_area:.3f} (coverage_fraction)"))
    width = max(len(r[0]) for r in rows)
    lines = [f"{label:<{width}}  {value:>10,.1f} km2  {note}" for label, value, note in rows]
    lines.append(f"{'PASS' if sha == DEEP_TOW_WFS_SHA256 else 'CHANGED'}: deep-tow WFS layer vs the 31 Aug 2026 snapshot (sha256 {sha[:12]})")
    print("\n".join(lines))
    figures(sensors, deep_vector, phase2, oi, lines)


def figures(sensors, deep_vector, phase2, oi, lines):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    FIGURES.mkdir(parents=True, exist_ok=True)
    g2, go = GRIDS["phase2"], GRIDS["ocean-infinity-2018"]

    def extent(grid):
        south, west, rows, cols = grid
        return [west, west + cols * COARSE, south, south + rows * COARSE]

    with PdfPages(FIGURES / "coverage.pdf") as pdf:
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.imshow(np.ma.masked_equal(oi, 0), origin="lower", extent=extent(go), cmap="Oranges",
                  vmin=0, vmax=2, interpolation="nearest")
        ax.imshow(np.ma.masked_equal(phase2, 0), origin="lower", extent=extent(g2), cmap="Blues",
                  vmin=0, vmax=1, interpolation="nearest")
        ax.set(xlim=(85, 104), ylim=(-40.5, -20.5), xlabel="Longitude (deg E)", ylabel="Latitude (deg)",
               title="Seabed search coverage: Phase 2 valid-data fraction (blue); OI 2018 outline less Phase 2, inferred (orange)")
        ax.plot(104.0, -21.0, "k+")
        ax.annotate("Bluefin-21 (2014)", (103.9, -21.0), ha="right", va="bottom", fontsize=8)
        ax.set_aspect(1 / np.cos(np.radians(32)))
        fig.savefig(FIGURES / "coverage.png", dpi=110)
        pdf.savefig(fig)
        plt.close(fig)

        fig, axs = plt.subplots(2, 2, figsize=(11, 8.5), sharex=True, sharey=True)
        for ax, (name, f) in zip(axs.flat, sensors.items()):
            ax.imshow(np.ma.masked_equal(coarse(f), 0), origin="lower", extent=extent(g2), cmap="Blues", vmin=0, vmax=1,
                      interpolation="nearest")
            ax.set_title(f"Phase 2 {name}: valid-pixel fraction per 0.01 deg cell")
            ax.set_aspect(1 / np.cos(np.radians(36)))
        fig.tight_layout()
        fig.savefig(FIGURES / "coverage-sensors.png", dpi=90)
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(11, 8.5))
        diff = coarse(sensors["deep-tow"]) - coarse(deep_vector.view(np.uint8) * np.uint8(255))
        im = ax.imshow(np.ma.masked_where(np.abs(diff) < 0.02, diff), origin="lower", extent=extent(g2), cmap="RdBu",
                       vmin=-1, vmax=1, interpolation="nearest")
        fig.colorbar(im, ax=ax, label="deep-tow valid pixels minus WFS footprint (fraction of cell)")
        ax.set_title("Deep tow: raster valid-data fraction vs the WFS L0 footprint (|difference| >= 0.02 shown)")
        ax.set_aspect(1 / np.cos(np.radians(36)))
        fig.savefig(FIGURES / "coverage-deep-tow-vs-wfs.png", dpi=90)
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(12, 4.2))
        fig.text(0.02, 0.95, "Area checks", fontsize=12, va="top")
        fig.text(0.02, 0.86, "\n".join(lines), family="monospace", fontsize=7.5, va="top")
        fig.savefig(FIGURES / "coverage-areas.png", dpi=110)
        pdf.savefig(fig)
        plt.close(fig)
    print(f"wrote {FIGURES / 'coverage.pdf'}", file=sys.stderr)


if __name__ == "__main__":
    main()
