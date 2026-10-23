mx = pd.read_csv("{{artifact:2215c5a6-45a7-4639-be44-48dfaecac199}}")
print([c for c in mx.columns][:40])
ec=[c for c in mx.columns if 'eta' in c.lower()]
print(ec)
print(mx.drop_duplicates(subset=[mx.columns[0]])[[mx.columns[0]]+ec].to_string()[:2500])
print(sg.head(1)[['eta_post_med']].to_string())