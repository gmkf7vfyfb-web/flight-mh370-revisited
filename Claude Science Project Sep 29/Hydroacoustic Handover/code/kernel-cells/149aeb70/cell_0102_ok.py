for L in (-28.9, -28.0, -22.0):
    print(f"lat {L:6.2f} -> dt {float(np.interp(L, lats, dt)):7.1f} s")
print("lat at dt=1390:", round(float(np.interp(1390, dt[::-1][::1][np.argsort(dt)], lats[np.argsort(dt)])),2))
