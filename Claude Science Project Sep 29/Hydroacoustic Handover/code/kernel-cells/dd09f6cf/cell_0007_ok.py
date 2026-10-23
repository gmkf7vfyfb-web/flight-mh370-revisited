for s in ["ga_search_and_rescue_search_area_2014","surface search polygons","amsa_mh370_media_2014","jacc_releases_2014_text","aerial_surface_search_source_ledger","ocean infinity 2018 northern","seabed-search-references"]:
    r=host.artifacts(search=s, limit=6)
    print("==",s)
    for a in r['artifacts']: print(' ',a['filename'],a['latest_version_id'],a.get('size_bytes'),round(a.get('_score',0),2))