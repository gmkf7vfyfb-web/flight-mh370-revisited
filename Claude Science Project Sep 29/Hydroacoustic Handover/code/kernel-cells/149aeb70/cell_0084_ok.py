import numpy as np
B=S["baseline"]; fpa=B[:,ci["flight_path_angle_deg"]]; tau=B[:,ci["tau90_s"]]
edges=[0,2,5,10,15,20,25,30,35,40,45,50,60,90]
h,_=np.histogram(fpa,bins=edges)
print("impact flight-path angle, run I baseline draw (n=20,000)")
for i in range(len(edges)-1):
    print(f"  {edges[i]:3d}-{edges[i+1]:3d} deg : {h[i]:6d}  ({h[i]/len(fpa)*100:5.2f}%)   median tau90 "
          f"{np.median(tau[(fpa>=edges[i])&(fpa<edges[i+1])]) if h[i] else float('nan'):7.3f} s")
print("\nfraction with 10 <= fpa < 45 deg:", round(float(((fpa>=10)&(fpa<45)).mean()),5))
