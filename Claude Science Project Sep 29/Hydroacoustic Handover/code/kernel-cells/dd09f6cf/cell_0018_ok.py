for s in ["MH370 bathymetry coverage 150m","Phase 1 bathymetry extent","ausseabed MH370","haixun","settling seabed depth Haixun","kadri hydro haixun 26.2"]:
    r=host.artifacts(search=s, limit=6)
    print("==",s)
    for a in r['artifacts']: print(' ',a['filename'],a['latest_version_id'],a.get('size_bytes'),round(a.get('_score',0),2))