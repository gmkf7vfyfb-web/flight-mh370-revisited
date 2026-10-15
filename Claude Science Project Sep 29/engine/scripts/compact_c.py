# Copied 2026-10-15 from deskstar J/53d0d251-e343-4b9a-8a2c-cafdfacce879/compact_c.py (J = /home/pete/.claude-science-scratch/.claude-science/jobs), sha256 cff753aa0ec5e330bc184bc8cc0a5516578193d9e71732888225a3ebb0c6c436 (of the source without this line); no functional change. Core order 2026-10-15b step 2.
"""Compact core run C outputs in place (architecture ruling 10 Oct 14:30 -0600). Standard library only.
tanks.npy (<f8, C order) -> tanks32.npy (<f4; the three *_unix_s columns become seconds after
T0 = 2014-03-08 00:00:00 UTC, renamed *_s_after_t0). Each snapshot handoff.toml -> handoff.toml.gz.
Every conversion is read back and verified before the original is removed. Appends COMPACT.txt."""
import sys, os, gzip, hashlib, json, math, ast, struct
from array import array
T0 = 1394236800.0
COLS = ["left_kg", "right_kg", "flow_ratio_r_to_l", "left_exhausted_s_after_t0", "right_exhausted_s_after_t0",
        "first_exhausted_s_after_t0", "single_engine_s", "single_engine_above_ceiling_s"]
TIME = (3, 4, 5)
def read_npy(path):
    with open(path, "rb") as f:
        assert f.read(6) == b"\x93NUMPY"; major = f.read(2)[0]
        n = struct.unpack("<H" if major == 1 else "<I", f.read(2 if major == 1 else 4))[0]
        hdr = ast.literal_eval(f.read(n).decode("latin1"))
        code = {"<f8": "d", "<f4": "f"}[hdr["descr"]]; assert not hdr["fortran_order"]
        a = array(code); a.frombytes(f.read())
    return a, hdr["shape"]
def write_npy(path, a, shape):
    descr = {"d": "<f8", "f": "<f4"}[a.typecode]
    h = "{'descr': '%s', 'fortran_order': False, 'shape': (%d, %d), }" % (descr, shape[0], shape[1])
    h = h + " " * (63 - (10 + len(h)) % 64) + "\n"
    with open(path, "wb") as f:
        f.write(b"\x93NUMPY\x01\x00" + struct.pack("<H", len(h)) + h.encode("latin1")); f.write(a.tobytes())
def tanks(d, log):
    src = os.path.join(d, "tanks.npy"); dst = os.path.join(d, "tanks32.npy")
    a, shape = read_npy(src); assert shape[1] == 8 and a.typecode == "d", shape
    b = array("d", a)
    for c in TIME:
        b[c::8] = array("d", (x - T0 for x in a[c::8]))
    write_npy(dst + ".tmp", array("f", b), shape); os.replace(dst + ".tmp", dst)
    back, s2 = read_npy(dst); assert tuple(s2) == tuple(shape)
    et = ek = 0.0
    for c in range(8):
        col_a = a[c::8]; col_b = back[c::8]; off = T0 if c in TIME else 0.0
        for x, y in zip(col_a, col_b):
            if math.isnan(x):
                assert math.isnan(y), "NaN pattern changed"; continue
            e = abs(y + off - x)
            if c in TIME: et = max(et, e)
            elif c < 2: ek = max(ek, e)
    assert et < 0.02 and ek < 0.01, (et, ek)
    os.remove(src); log.append(f"{dst} rows={shape[0]} max_time_err_s={et:.4f} max_kg_err={ek:.5f}")
def toml(p, log):
    raw = open(p, "rb").read(); h = hashlib.sha256(raw).hexdigest()
    with gzip.open(p + ".gz.tmp", "wb", compresslevel=6) as f: f.write(raw)
    assert hashlib.sha256(gzip.open(p + ".gz.tmp").read()).hexdigest() == h
    os.replace(p + ".gz.tmp", p + ".gz"); os.remove(p)
    log.append(f"{p}.gz sha256(uncompressed)={h} {len(raw)}->{os.path.getsize(p + '.gz')}")
root = sys.argv[1]; log = []
for dp, dn, fn in sorted(os.walk(root)):
    if "tanks.npy" in fn: tanks(dp, log)
    if "handoff.toml" in fn and os.path.basename(dp).startswith("handoff-"): toml(os.path.join(dp, "handoff.toml"), log)
with open(os.path.join(root, "COMPACT.txt"), "a") as f:
    f.write("\n".join(log) + "\n" + json.dumps({"tanks32_columns": COLS, "t0_unix_s": T0}) + "\n")
print(len(log), "conversions")
