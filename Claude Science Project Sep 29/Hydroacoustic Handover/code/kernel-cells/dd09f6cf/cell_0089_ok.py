def clean(o):
    if isinstance(o,dict): return {str(k):clean(v) for k,v in o.items()}
    if isinstance(o,(list,tuple)): return [clean(v) for v in o]
    if isinstance(o,(np.floating,float)): return None if not np.isfinite(o) else float(o)
    if isinstance(o,(np.integer,)): return int(o)
    return o
summary={'run':'run J (4 strata, core P(family) waypoints 0.9982 / free 0.0013 / repro-radar 0.0003 / descent-climb 0.0002), headline key D{d} total q=0.333 (C2 silent)',
 'locality':res,'surface_expectations_ref':{d:surf[(d,REF_A,'csiro')] for d in DK},'seed_bootstrap_lnB':BOOT,'characterisation':char,
 'oi2018_along_bearing_km_rel_R7':[-47.1,42.0],'phase1_bathy_along_bearing_km_rel_R7':[[-73.4,-63.8],[-8.6,-0.5]],
 'L_surface_cell':{'crossing':float(Lgrid[(REF_A,'csiro')][int(np.floor((-25.732-GLAT0)/GST))*GNX+int(np.floor((101.369-GLON0)/GST))]),'haixun':float(Lgrid[(REF_A,'csiro')][hcell])},
 'gebco2026_tid_check':{'crossing_tid':40,'oi_only_pixels_black_fraction':0.137,'phase1_pixels_black_fraction':0.998,'by_lat':{'-33..-30':0.175,'-30..-28':0.048,'-28..-26.5':0.310,'-26.5..-24.7':0.141}}}
json.dump(clean(summary),open('locality-search-summary.json','w'),indent=1); print('ok')