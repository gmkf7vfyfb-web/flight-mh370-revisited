for opt in ["D0","D3"]:
    z=np.load(GD/f"map_{opt}.npz"); s=z["snr_best_eta1"]; lat=z["lat"]
    print(opt, "nonfinite share", np.mean(~np.isfinite(s)), "lat of nonfinite q05/q50/q95", np.percentile(lat[~np.isfinite(s)],[5,50,95]) if (~np.isfinite(s)).any() else None, "share lat>-25", np.mean(lat>-25))
xs, tl = RL.tl_tables() if False else (None,None)