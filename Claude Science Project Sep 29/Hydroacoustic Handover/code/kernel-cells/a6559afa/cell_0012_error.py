for tb in ['frame_blobs','frame_branch_archives','transcript_annotations']:
    print(tb, host.query(f"SELECT sql FROM sqlite_master WHERE name='{tb}'")['rows'][0][0][:400])
print(host.query("SELECT frame_id, count(*) FROM frame_blobs WHERE frame_id IN ('676a6e64-2eac-490f-b67d-6c3f5c82f047','a35831fe-107a-4961-bc9f-e6fd6d255601') GROUP BY frame_id"))
print(host.query("SELECT frame_id, count(*), max(idx) FROM frame_messages WHERE frame_id IN ('676a6e64-2eac-490f-b67d-6c3f5c82f047','a35831fe-107a-4961-bc9f-e6fd6d255601') GROUP BY frame_id"))