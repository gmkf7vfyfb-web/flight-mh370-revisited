import numpy as np
ts = g("latent:pushover_to_surface")
m = pd_ > 0.5
print(f"pushover drawn: {m.mean():.4f} of rows; to_surface among them: {ts[m].mean():.4f}")
print(f"median impact angle  to_surface=1: {np.median(fpa[m & (ts > .5)]):.2f} deg | to_surface=0: {np.median(fpa[m & (ts < .5)]):.2f} deg")
print(f"fraction steeper than 10 deg      to_surface=1: {(fpa[m & (ts > .5)] > 10).mean():.3f} | to_surface=0: {(fpa[m & (ts < .5)] > 10).mean():.3f}")
ess = lambda v: float(v.sum() ** 2 / np.square(v).sum())
base = ess(w)
print(f"\nreweighting to a dive probability p (x2p if to_surface, x2(1-p) if not, x1 if no push-over):")
print(f"{'p':>5} {'ESS':>12} {'ESS/ESS(0.5)':>13} {'share 10-45 deg':>16} {'share >45 deg':>14}")
for p in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0):
    f_ = np.ones_like(w)
    f_[m & (ts > .5)] = 2 * p
    f_[m & (ts < .5)] = 2 * (1 - p)
    ww = w * f_; s = ww.sum()
    mid = float((ww[(fpa >= 10) & (fpa < 45)]).sum() / s); st = float((ww[fpa > 45]).sum() / s)
    print(f"{p:5.2f} {ess(ww):12.0f} {ess(ww)/base:13.3f} {mid:16.4f} {st:14.4f}")
