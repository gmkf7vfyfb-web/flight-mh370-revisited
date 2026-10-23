"""Tests for gates.py. Targets are the numbers reported by the Take 2 review (artifact d28aa25a, section 5).
A failing target is reported, not tuned away: if the code disagrees with the review, the test output says by how much.
Run:  HYDRO_EX=<exchange hydro dir> HYDRO_ART=<handover artifacts dir> HYDRO_OCEAN=<ocean data dir> pytest -q test_gates.py
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import gates as G

HERE = Path(__file__).resolve().parent
MOD = HERE.parent.parent
EX = Path(os.environ.get("HYDRO_EX", "/Users/pete/Downloads/mh370-exchange/hydroacoustics"))
ART = Path(os.environ.get("HYDRO_ART", ""))
OCEAN = Path(os.environ.get("HYDRO_OCEAN", "/Users/pete/Downloads/mh370-ocean-data"))
RK = EX / "graphics-2026-10-22/ranked"


@pytest.fixture(scope="module")
def singles():
    return pd.read_csv(RK / "ranked_singles.csv", dtype={"rx": str})


@pytest.fixture(scope="module")
def pairs():
    return pd.read_csv(RK / "ranked_pairs.csv", dtype={"rx_a": str, "rx_b": str})


def test_band_rules():
    assert G.band_check("3315", "2-5").startswith("BELOW_CORNER")
    assert G.band_check("3274", "5-10").startswith("MOSTLY_BELOW")
    assert G.band_check("3274", "5-40").startswith("PARTLY_BELOW")
    assert G.band_check("3274", "10-20") == "IN_BAND"
    assert G.band_check("H01W", "5-40") == "IN_BAND"
    assert G.band_check("H08S", "1-9 (plot)").startswith("PARTLY_BELOW")
    assert G.band_check("H08S", "residual env").startswith("NOT_A_BAND")


def test_review_2to5_counts(singles, pairs):
    # review 5.7: "35 singles and 1,111 pairs use a 2-5 Hz band"
    assert (singles.band == "2-5").sum() == 35
    assert ((pairs.band_a == "2-5") | (pairs.band_b == "2-5")).sum() == 1111


def test_review_scott_reef_counts(singles, pairs):
    # review 5.6: "63 singles, 2,584 pairs (78 %) and 11,067 triples (90 %)"
    assert (singles.rx == "3250").sum() == 63
    assert ((pairs.rx_a == "3250") | (pairs.rx_b == "3250")).sum() == 2584
    tr = pd.read_csv(RK / "ranked_triples.csv", usecols=["rxs"])
    assert tr.rxs.astype(str).str.contains("3250").sum() == 11067


def test_review_airgun_44_of_47(singles):
    sh = G.Shots(MOD / "results-data/h08s_template/h08s_template_shots.csv",
                 EX / "run-j-weak-signal/h08s/surviving_candidates.csv")
    h = singles[singles.rx == "H08S"]
    v = [sh.check("H08S", G.hms(t))[0] for t in h.time_utc]
    assert len(h) == 47
    assert sum(x == "COINCIDENT_WITH_SHOT" for x in v) == 44


def test_review_land_201_of_2000():
    import json
    rx = json.load(open(EX / "run-j-searches/geometry/run.json"))["receivers"]["3275"]
    L = G.Land(OCEAN / "gebco/grid/gebco_2026.json")
    verdict, n_all, n_in = L.path(-26.34, 100.93, rx[0], rx[1])
    assert verdict == "CROSSES_LAND"
    assert abs(n_all - 201) <= 5, n_all   # review: 201 of 2,000 path points above sea level


def test_gebco_orientation():
    L = G.Land(OCEAN / "gebco/grid/gebco_2026.json")
    assert L.elev(-25.0, 120.0) > 0        # Western Australia interior
    assert L.elev(-35.0, 95.0) < -3000     # deep Indian Ocean


def test_royer_icequake_A_at_kadri_text_time():
    if not ART.exists() or str(ART) == "":
        pytest.skip("HYDRO_ART not set")
    R = G.Royer(ART / "a35831fe/239646ad_royer-events-crossid-all-sites.csv",
                MOD / "results-data/digitised/royer-2016/royer_figure_marks.csv")
    v = R.check("H01W", G.hms("00:52:03"))
    assert "fig4_eventA pick bar" in v


def test_time_and_coupling_rules():
    assert G.time_check(G.hms("00:15:45")).startswith("IMPOSSIBLE")
    assert G.time_check(G.hms("00:26:47")) == "AFTER_0019"
    eta, xo, xm, lab = G.coupling_labels(0.069, 1.13e9, 1.2e10)
    assert np.isclose(eta, 0.069 * 1.13e9 / 1.2e10) and lab.startswith("POSSIBLE")
    assert G.coupling_labels(30.0, 1.13e9, 1.2e10)[3].startswith("IMPOSSIBLE")


def test_royer_untabled_arrow_0048():
    if not ART.exists() or str(ART) == "":
        pytest.skip("HYDRO_ART not set")
    R = G.Royer(ART / "a35831fe/239646ad_royer-events-crossid-all-sites.csv",
                MOD / "results-data/digitised/royer-2016/royer_figure_marks.csv")
    assert "arrow 00:48:11.41 (untabled)" in R.check("H01W", G.hms("00:48:21"))
