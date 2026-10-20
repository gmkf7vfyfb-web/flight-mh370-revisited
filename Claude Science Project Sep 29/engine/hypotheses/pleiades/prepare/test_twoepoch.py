"""Tests for the two-epoch machinery (brief section 12). Run: python test_twoepoch.py"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import twoepoch as te  # noqa: E402


def test_enumeration_counts_match_closed_form():
    # brief: 1,045 cluster assignments and 18,001 object assignments, generated and counted
    for m, n, want in [(4, 6, 1045), (4, 12, 18001), (3, 6, 229), (3, 12, 1753)]:
        a = te.assignments(m, n)
        assert len(a) == want == te.n_assignments(m, n), (m, n, len(a))
        assert len(set(a)) == len(a), "duplicates"
        for x in a:
            used = [t for t in x if t >= 0]
            assert len(used) == len(set(used)), "not injective"
    assert te.n_assignments(4, 39) == 2_202_409


def test_k_nodes_are_a_normalised_log_uniform_quadrature():
    K, w = te.k_nodes(8, 30.0, 1000.0)
    assert abs(w.sum() - 1) < 1e-12 and (K > 30).all() and (K < 1000).all()
    # E[ln K] under log-uniform is the midpoint of the logs
    assert abs((w * np.log(K)).sum() - 0.5 * (math.log(30) + math.log(1000))) < 1e-10


def test_ou_variance_limits():
    dt = 40.5 * 3600
    assert te.var_ou_km2(0.0, 86400, dt) == 0.0
    # short-time limit is ballistic, sigma^2 dt^2; long-time is diffusive, 2 sigma^2 T dt
    assert abs(te.var_ou_km2(0.05, 1e9, dt) / (0.0025 * dt**2 / 1e6) - 1) < 1e-3
    assert abs(te.var_ou_km2(0.05, 60.0, 1e8) / (2 * 0.0025 * 60 * 1e8 / 1e6) - 1) < 1e-3


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
