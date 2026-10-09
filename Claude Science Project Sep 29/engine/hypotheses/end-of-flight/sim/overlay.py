"""Overlay a fitted 6-DOF flight on a Boeing case: ground track, altitude, EAS and bank against time.
    python overlay.py <out.png> <fit.json> [<fit.json> ...]"""
import json, sys, math
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import fit as F
from model import schedules
F.SCHED = schedules(); tg, data = F.load()
fits = [json.load(open(p)) for p in sys.argv[2:]]
fig, axs = plt.subplots(len(fits), 4, figsize=(13, 3.0 * len(fits)), squeeze=False)
for i, fj in enumerate(fits):
    c = fj["case"]; d = data[c]
    val, rec = F.nll(c, tg, data, fj["shared"], fj["nuisance"], fj["law"], fj["tac"], return_rec=True)
    a = axs[i]
    a[0].plot(d["x_nm"], d["y_nm"], "k-", lw=1.2, label="Boeing"); a[0].plot(rec[:, 1], rec[:, 2], "C0-", lw=1, label="6-DOF fit")
    a[0].set_aspect("equal"); a[0].set_title(f"{c}: track (NM), law {fj['law']}", fontsize=8, loc="left"); a[0].legend(fontsize=6, frameon=False)
    a[1].plot(d["t_s"], d["alt_ft"], "k-", lw=1.2); a[1].plot(rec[:, 0], rec[:, 3], "C0-", lw=1); a[1].set_title("altitude (ft)", fontsize=8, loc="left")
    from scipy.signal import savgol_filter
    a[2].plot(rec[:, 0], rec[:, 6], "C0-", lw=1); a[2].set_title("6-DOF EAS (kt)", fontsize=8, loc="left")
    a[3].plot(rec[:, 0], rec[:, 4], "C0-", lw=1); a[3].set_title("6-DOF bank (deg)", fontsize=8, loc="left")
    for ax in a[1:]:
        ax.axvline(float(tg[c]["t_uncontrolled_s"]), color="r", lw=0.6, ls=":")
    print(c, "nll", round(val), "sim end t", int(rec[-1, 0]), "Boeing end t", int(d["t_s"][-1]), "sim max |bank|", round(float(np.abs(rec[:, 4]).max()), 1))
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=110)
