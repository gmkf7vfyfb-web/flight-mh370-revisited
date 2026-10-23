pe  = Y[:,ci["latent:pushover_eligible"]]; pdn = Y[:,ci["latent:pushover_drawn"]]
rate = Y[:,ci["latent:pushover_rate_fpm"]]; floor_ = Y[:,ci["latent:pushover_n_floor_g"]]
p2s  = Y[:,ci["latent:pushover_to_surface"]]
drawn = np.isfinite(rate)
print("rows push-over drawn:", int(drawn.sum()), "of", len(Y), f"({drawn.mean():.3f})")

def unif_test(v, lo, hi, ww, name, aim=None):
    m = np.isfinite(v) & (ww>0)
    vv, wk = v[m], ww[m]
    u = (vv-lo)/(hi-lo)
    # weighted CDF at deciles vs uniform
    dec = np.arange(0.1,1.0,0.1)
    emp = [float(wk[u<=d].sum()/wk.sum()) for d in dec]
    md = max(abs(e-d) for e,d in zip(emp,dec))
    extra = ""
    if aim:
        a0,a1 = aim
        share_prior = float(wk[(vv>=a0)&(vv<=a1)].sum()/wk.sum())
        share_unif  = (a1-a0)/(hi-lo)
        extra = f"  | in aim window: corrected {share_prior:.4f} vs uniform {share_unif:.4f}"
    print(f"{name:26s} support[{lo},{hi}] max|CDF-uniform|={md:.4f}{extra}")

print("\n--- corrected PRIOR (sampling weight only): is the aimed latent still uniform on its support? ---")
unif_test(rate, 6500, 40000, w, "push-over rate (ft/min)", aim=(18000,40000))
unif_test(floor_, -1.0, 0.8, w, "push-over load floor (g)", aim=(0.15,0.45))
unif_test(Y[:,ci["latent:pitchdown_n_g"]], -0.31, 0.69, w, "pitch-down load factor (g)")
unif_test(Y[:,ci["latent:pitchdown_delay_s"]], 0.0, 900.0, w, "pitch-down delay (s)")

print("\n--- same latents under the 00:19 POSTERIOR (should move: that is the evidence selecting) ---")
unif_test(rate, 6500, 40000, P["both/no-offset"], "push-over rate (ft/min)", aim=(18000,40000))
unif_test(floor_, -1.0, 0.8, P["both/no-offset"], "push-over load floor (g)", aim=(0.15,0.45))

print("\n--- dive-branch latent: prior vs posterior share of 'push-over continued to the surface' ---")
for lab,wk in [("corrected prior",w),("R600 only",P["r600/no-offset"]),("R1200 only",P["r1200/no-offset"]),
               ("both, raw",P["both/no-offset"]),("both, start-up offset",P["both/startup-offset"])]:
    m = np.isfinite(p2s) & (wk>0)
    print(f"  {lab:22s} P(to surface | push-over drawn) = {float(wk[m & (p2s==1)].sum()/wk[m].sum()):.4f}")
