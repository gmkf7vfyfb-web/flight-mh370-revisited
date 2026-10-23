import numpy as np
from scipy import stats
A_TEXT = 3123 + 1493
for lbl, z in (("±1.0° bearing", 18.4), ("±3.3° bearing", 32.6)):
    lo_w, hi_w = A_TEXT - 2*z, A_TEXT + 2*z
    m = (cy.t_next > lo_w) & (cy.t_shot < hi_w)
    k = int((cy.loc[m, "z_P_gap"] > 2).sum()); n_ = int(m.sum())
    p1 = 1 - stats.norm.cdf(2)
    print(f"{lbl}: window {int(lo_w//3600):02d}:{int(lo_w%3600//60):02d}:{int(lo_w%60):02d}"
          f"-{int(hi_w//3600):02d}:{int(hi_w%3600//60):02d}:{int(hi_w%60):02d}, {n_} shot cycles, "
          f"{k} with gap z>2; expected {n_*p1:.2f}; P(>=1 by chance) = {1-(1-p1)**n_:.3f}")
print(f"\nwhole record: 1 of 107 cycles above +2 sd gap power, {107*(1-stats.norm.cdf(2)):.1f} expected")
