"""Tests for reverse_spectral.py (Amendment 2). Run: python -m pytest -q tests/test_reverse_spectral.py"""
import hashlib, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
import reverse_spectral as RS  # noqa: E402

GF = np.linspace(0, 125, 501)
GD = np.zeros_like(GF)          # flat gain for synthetic tests
MARK = "# ------------------------------------------------------------------ features"


def _noise(seed=0, n=int(307 * 250)):
    return np.random.default_rng(seed).normal(size=n)


def _scan(x):
    f, t, P = RS.spectrogram(x)
    return RS.s10_scan(RS.whiten(f, t, P), GF, GD)


def test_s10_part_hash_matches_fixed_record():
    src = (HERE / "reverse_spectral.py").read_text()
    fixed = json.loads((HERE / "amendment-2-fixed-code.json").read_text())
    assert hashlib.sha256(src[:src.index(MARK)].encode()).hexdigest() == fixed["s10_part_sha256"]


def test_whitening_zero_mean_unit_sd():
    f, t, P = RS.spectrogram(_noise(1))
    W = RS.whiten(f, t, P)
    assert abs(W.Z.mean()) < 0.1 and 0.9 < W.Z.std() < 1.2


def test_bank_metz_members_and_bandwidth():
    p = RS.draw_path_params()
    assert len(p["a"]) == RS.BANK_N == 240
    assert np.allclose(p["a"][:3], [3.1, 2.65, 3.5]) and np.allclose(p["fc"][:3], [5.1, 4.5, 5.75])
    assert np.all(p["f_hi"] >= 2 * p["f_lo"])
    assert p["a"].min() >= 0 and p["a"].max() <= 5 and p["fc"].min() >= 0.5 and p["fc"].max() <= 20
    assert len(RS.time_shapes()[0]) == 21


def test_injection_detected_above_noise():
    x = _noise(2)
    r0 = np.nanmax(_scan(x).R)
    rng = np.random.default_rng(3)
    p, rise, decay = RS.random_impact_draw(rng)
    sig = RS.synth_signal(len(x), 150.0, p, rise, decay, GF, GD, rng)
    xi, _ = RS.inject(x, sig, 150.0, 0.0)
    sr = _scan(xi)
    m = np.abs(sr.t - 150) <= 5
    assert np.nanmax(sr.R[m]) > 2 * r0


def test_shape_test_penalises_tonal_signal():
    x = _noise(4)
    tt = np.arange(len(x)) / 250.0
    tone = np.where((tt > 150) & (tt < 160), np.sin(2 * np.pi * 25.0 * tt), 0.0) * 3.0
    sr = _scan(x + tone)
    m = np.abs(sr.t - 150) <= 5
    k = np.where(m)[0][np.nanargmax(sr.R[m])]
    assert sr.chi2r[k] > 1.0 and sr.R[k] < sr.rho[k]


def test_decide_rules():
    classes = RS.CLASSES[:6] + ["background noise only"]
    probs = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.9, 0.1])
    bb = dict(bandwidth_oct=0.8, tonality_db=4.0, log_rise=0.0, repeat_strength=0.1)
    assert RS.decide(bb, probs, classes, 0.5)[0] == "impact-like"
    # envelope-only: spectrum unknown -> never impact-like (A2.11 deviation 2)
    env = dict(log_rise=0.0, repeat_strength=0.1)
    assert RS.decide(env, probs, classes, 0.5)[0] == "unclassified"
    # known class needs positive evidence: earthquake probability high but no catalogue timing
    pe = np.array([0.0, 0.0, 0.9, 0.0, 0.0, 0.05, 0.05])
    assert RS.decide(bb, pe, classes, 0.5)[0] != "earthquake sound arrival"
    assert RS.decide(bb, pe, classes, 0.5, {"earthquake sound arrival": 0.8})[0] == "earthquake sound arrival"
    # open-set reject
    assert RS.decide(bb, probs, classes, 1e-5)[0] == "unclassified"
    # noise first (A2.11 deviation 1)
    pn = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.7])
    assert RS.decide(bb, pn, classes, 0.5)[0] == "background noise only"


def test_classify_returns_calibrated_probabilities():
    if not (HERE / "classifier_models.pkl").exists():
        return
    x = _noise(5)
    out = RS.classify(dict(form="raw", x=x, t_on=100, t_off=110, station="IMOS3376", gain=(GF, GD)))
    assert abs(sum(out["probs"].values()) - 1) < 1e-6 and out["label"]
    env = RS.envelope_from_raw(x)
    out2 = RS.classify(dict(form="envelope", env=env, t_on=100, t_off=110))
    assert out2["label"] != "impact-like"


def test_tonality_feature_rises_with_tone():
    x = _noise(6)
    f, t, P = RS.spectrogram(x)
    W = RS.whiten(f, t, P)
    base = RS.features_raw(x, 150, 160, GF, GD, W=W)["tonality_db"]
    tt = np.arange(len(x)) / 250.0
    xt = x + np.where((tt > 150) & (tt < 160), np.sin(2 * np.pi * 25.0 * tt), 0.0) * 1.0
    f, t, P = RS.spectrogram(xt)
    ton = RS.features_raw(xt, 150, 160, GF, GD, W=RS.whiten(f, t, P))["tonality_db"]
    assert ton > base + 5
