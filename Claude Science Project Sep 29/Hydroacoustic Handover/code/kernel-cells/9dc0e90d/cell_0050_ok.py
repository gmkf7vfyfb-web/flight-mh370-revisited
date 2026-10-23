gj = json.load(open(host.artifact_path("a74cc2b4-988c-4dad-95ff-468f16dfeaff")))
feats = gj['features']; print(len(feats), feats[0]['properties'], feats[0]['geometry']['type'])
names = pd.Series([f['properties'].get('Name') for f in feats]); print(names.value_counts().sort_index().head(5).to_dict(), names.nunique())
try:
    import cartopy; print("cartopy", cartopy.__version__)
except Exception as e: print("no cartopy", e)
try:
    import shapely; print("shapely", shapely.__version__)
except Exception as e: print("no shapely")