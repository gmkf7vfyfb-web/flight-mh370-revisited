more = [
 ["aim_prior_uniformity_rate","0.0030","max |weighted CDF - uniform| for push-over rate under sampling weight only","support 6500-40000 ft/min; exact correction confirmed"],
 ["aim_prior_uniformity_floor","0.0041","max |weighted CDF - uniform| for push-over load floor","support -1.0 to 0.8 g"],
 ["aim_window_share_prior_rate","0.6615","corrected prior share inside the 18,000-40,000 ft/min aim window","uniform would give 0.6567"],
 ["aim_window_share_posterior_rate","0.9438","same share under both 00:19 bursts, raw model","the evidence selecting, not the sampler"],
 ["aim_window_share_prior_floor","0.1650","corrected prior share inside the 0.15-0.45 g aim window","uniform would give 0.1667"],
 ["aim_window_share_posterior_floor","0.3995","same share under both 00:19 bursts, raw model",""],
 ["proposal_self_check_mean","1.000178","stored mean importance correction","standard error 0.000693"],
 ["dive_share_prior","0.4949","P(push-over continued to surface | push-over drawn), corrected prior",""],
 ["dive_share_r600","0.2543","same, 00:19 R600 burst only","data moves share DOWN from prior"],
 ["dive_share_r1200","0.4460","same, 00:19 R1200 burst only",""],
 ["dive_share_both_raw","0.3105","same, both bursts raw model",""],
 ["dive_share_both_startup","0.3088","same, both bursts start-up offset model",""],
 ["dive_share_sd_observed","0.1140","across-parent standard deviation of dive share","6,232 parents, 20.4 draws each"],
 ["dive_share_sd_fixed_p","0.1108","predicted if probability fixed at 0.5 per descent","matches observed"],
 ["dive_share_sd_hyperprior","0.3025","predicted if per-parent probability drawn from U[0,1]","does not match: hyper-prior not implemented"],
]
with open("eof-audit-measurements.csv","a",newline="") as f:
    csv.writer(f).writerows(more)
print(sum(1 for _ in open("eof-audit-measurements.csv")), "rows total")
