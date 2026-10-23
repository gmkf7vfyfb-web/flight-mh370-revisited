for s in ['jacc_releases_2014_text','surface_search_daily_2014','amsa_mh370_media_2014','rnzaf_p3_image_positions','ga_search_and_rescue']:
    r=host.artifacts(search=s)
    for x in r['artifacts'][:3]: print(s,'|',x['filename'],x['latest_version_id'],x['size_bytes'])