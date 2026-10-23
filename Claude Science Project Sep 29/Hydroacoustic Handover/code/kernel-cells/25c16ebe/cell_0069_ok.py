rows2 = [
 ["descending_fraction_q05_q50_q95","0.572 / 0.931 / 1.001","fraction of onset-to-impact time spent descending","held-out weighting; CORRECTS the earlier 600 s statistic"],
 ["descending_fraction_below_060","0.0582","weight share with descending fraction under 0.60","requirement MET; dynamics note's own test threshold"],
 ["descending_fraction_below_090","0.4148","weight share with descending fraction under 0.90",""],
 ["max_nondescending_s","2407.5","longest level segment in file (s)","configured leveloff_seconds cap is 2,400 s"],
 ["long_descent_share","0.1082","weight share with onset-to-impact over 1,800 s",""],
 ["long_descent_nondescending_q50","132.2","median non-descending seconds among those","the narrow residual concern"],
 ["leveloff_altitude_verifiable","no","realised level-off altitude is not an emitted column","dynamics note records 10,000 ft and 4,000 ft as always-present candidates; config interval is the ADDITIONAL sampled altitude; earlier 'gap' finding WITHDRAWN"],
 ["WITHDRAWN_nondescending_gt600","1.75 per cent","superseded statistic, retained for traceability","threshold near-unsatisfiable at a 1,176 s median duration; replaced by the fraction"],
]
with open("eof-audit-measurements.csv","a",newline="") as f: csv.writer(f).writerows(rows2)
print(sum(1 for _ in open("eof-audit-measurements.csv")),"rows")
