import numpy as np
c = cy[(cy.t_shot > 4580) & (cy.t_shot < 4620)]
f = lambda t: f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):04.1f}"
for _,r in cy[(cy.t_shot>4550)&(cy.t_shot<4680)].iterrows():
    print(f"shot {f(r.t_shot)}  next {f(r.t_next)}  gap-max {f(r.t_gapmax)}  E {r.E_shot:.3f} (z {r.z_E_shot:+.2f})  Pgap {r.P_gap:.4f} (z {r.z_P_gap:+.2f})")
n = len(cy)
print(f"\ncycles: {n}; count with |z_P_gap|>2: {(cy.z_P_gap.abs()>2).sum()}; expected under a normal model: {n*0.0455:.1f}")
print(f"count with z_P_gap>2: {(cy.z_P_gap>2).sum()}; expected one-sided: {n*0.0228:.1f}")
print("predicted arrival 01:16:54 minus gap-max 01:16:47 =", 4614-4607.0, "s (using that cycle's t_gapmax)")
