import pandas as pd
print(bl.pivot_table(index="imp", columns="rx", values="len_km").to_string())
print("\nwhere each Scott Reef path is shallowest:")
print(bl[bl.rx=="3250"][["imp","len_km","min_depth_m","at_km","at","land_on_track","km_shallower_1000"]].to_string(index=False))
print("\nPortland 3274 detail:")
print(bl[bl.rx=="3274"][["imp","len_km","min_depth_m","at_km","at","land_on_track","km_shallower_1000"]].to_string(index=False))
