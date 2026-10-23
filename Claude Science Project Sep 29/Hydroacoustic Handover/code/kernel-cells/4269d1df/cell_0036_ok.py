for q in ['compose-runj-waypoints.npz','arc-latitude-profile.csv','core-release-points.json']:
    r=host.artifacts(filename=q, limit=5)
    print(q, [(a['filename'],a['latest_version_id'],a['size_bytes']) for a in r['artifacts']])
