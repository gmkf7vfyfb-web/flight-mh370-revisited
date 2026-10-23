cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('detectors.py').read()
s=s.replace('''sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "weak_signal"))
import preregistration as R''','''import preregistration as R
# weak_signal/bank.py and weak_signal/common.py are NOT imported (their `import preregistration` would resolve to this
# folder's module); the two helpers needed are copied verbatim below with their pre-registered constants.''')
s=s.replace('''def _pulse(T, key, tau, fs):
    import bank as B            # weak_signal/bank.py (pre-registered template conventions)
    return B.pulse(T, key, tau, fs=fs)
''','''TLEN, PEAK_AT = 50.0, 35.0          # weak_signal/bank.py conventions


def _source_filter(x, fs, tau):
    b, a = signal.butter(1, 1.0 / tau, btype="low", fs=fs)
    return signal.lfilter(b, a, x)


def _pulse(T, key, tau, fs):
    """weak_signal/bank.pulse, copied: 'h2' series rolled to peak at 35 s, 50 s cut, one-pole source for tau,
    5-40 Hz band-pass, resampled to fs, unit energy."""
    h = T[key]; fs0 = float(T["fs"])
    e = np.convolve(h ** 2, np.ones(int(fs0)) / fs0, "same")
    pk = int(np.argmax(e))
    h = np.roll(h, int(PEAK_AT * fs0) - pk)[: int(TLEN * fs0)]
    x = _source_filter(h, fs0, tau)
    sos = signal.butter(4, list(R.BAND_MAIN), btype="bandpass", fs=fs0, output="sos")
    x = signal.sosfiltfilt(sos, x)
    x = signal.resample_poly(x, int(fs), int(fs0))
    return (x / np.sqrt(np.sum(x ** 2))).astype(float)


def emulate_plot(x500, fs_out=R.PANEL_FS, bin_s=0.069):
    """weak_signal/common.emulate_plot, copied: 5-40 Hz series at 500 Hz -> per-bin min and max as vertices -> interp."""
    y = signal.sosfiltfilt(SOS_540, x500)
    nb = int(bin_s * R.FS_D)
    n = len(y) // nb
    Y = y[: n * nb].reshape(n, nb)
    imin, imax = Y.argmin(1), Y.argmax(1)
    base = np.arange(n) * nb
    tv = np.concatenate([base + imin, base + imax]) / R.FS_D
    pv = np.concatenate([Y[np.arange(n), imin], Y[np.arange(n), imax]])
    o = np.argsort(tv)
    tg = np.arange(0, len(y) / R.FS_D, 1 / fs_out)
    return np.interp(tg, tv[o], pv[o]).astype(np.float32)
''')
open('detectors.py','w').write(s)
w=open('null_worker.py').read()
w=w.replace('''sys.path.insert(0, str(Path(__file__).resolve().parent.parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "weak_signal"))
import imos_noise as N, imos_preregistration as P
import common as C
''','''sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import imos_noise as N, imos_preregistration as P
''').replace('x20 = C.emulate_plot(x500)','x20 = D.emulate_plot(x500)')
open('null_worker.py','w').write(w)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
time python null_worker.py 3376 0 672 /tmp/null_smoke.npz 2>&1 | tail -3
python -c "
import numpy as np; z=np.load('/tmp/null_smoke.npz'); print({k:(z[k].shape, np.round(z[k][:3],3)) for k in z.keys()})"