"""Reader for the debris-drift arrivals dump (arrivals.bin + responses.json; layout in lib.rs write_arrival_block).

Every beaching of every scored class, node and environment, so that the recovery layer can be re-run offline.
"""
import json, numpy as np

HDR = np.dtype([('magic', 'S4'), ('node', '<u4'), ('lat', '<f8'), ('lon', '<f8'), ('env_seed', '<u8'), ('cls', '<u4'),
                ('released', '<u4'), ('n', '<u4'), ('model_error', '<f8'), ('left_domain', '<f8')])
REC = np.dtype([('particle', '<u4'), ('w', '<f4'), ('t_days', '<f8'), ('t_leave_days', '<f4'), ('lon', '<f8'), ('lat', '<f8'),
                ('line', '<i4'), ('s_km', '<f8'), ('segment', '<i4')])
assert HDR.itemsize == 60 and REC.itemsize == 52

def read(path):
    """List of (header dict, records ndarray) in file order."""
    buf = open(path, 'rb').read(); off = 0; out = []
    while off < len(buf):
        h = np.frombuffer(buf, HDR, 1, off)[0]; off += HDR.itemsize
        assert h['magic'] == b'ARV1', off
        r = np.frombuffer(buf, REC, int(h['n']), off); off += REC.itemsize * int(h['n'])
        out.append(({k: h[k].item() for k in HDR.names if k != 'magic'}, r))
    return out

def responses(path):
    m = json.load(open(path))
    return {c['name']: np.array(c['responses']) for c in m['classes']}, m
