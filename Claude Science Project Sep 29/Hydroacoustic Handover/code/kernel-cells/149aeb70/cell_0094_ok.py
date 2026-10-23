clear_lat, blocked_lat = -29.5, -28.0
for _ in range(40):
    mid = (clear_lat+blocked_lat)/2
    if blocked(mid, float(np.polyval(cf, mid)), RX["Portland 3274"]): blocked_lat = mid
    else: clear_lat = mid
print(f"Portland: clear to {clear_lat:.3f} deg, blocked from {blocked_lat:.3f} deg (arc lon {float(np.polyval(cf,blocked_lat)):.2f} E)")
import pandas as pd
kw = pd.read_csv(host.artifact_path("bc160a0c-61b4-40a0-bf50-8377bff7d36d"))
print("\nkadri_windows cols:", list(kw.columns)); print(kw.head(8).to_string(index=False))
bm = pd.read_csv(host.artifact_path("610384ee-d6d6-496e-bd29-a2f58e7d7d12"))
print("\nbearing-mixture cols:", list(bm.columns)); print(bm.head(12).to_string(index=False))
