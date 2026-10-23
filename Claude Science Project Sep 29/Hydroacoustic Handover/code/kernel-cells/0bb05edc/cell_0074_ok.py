
import json
r = host.query("""SELECT a.filename, av.id, av.size_bytes FROM artifact_versions av JOIN artifacts a ON a.id=av.artifact_id
WHERE lower(a.filename) LIKE '%durgadoo%' OR lower(a.filename) LIKE '%1755876x%' OR lower(a.filename) LIKE '%523313%' OR lower(a.filename) LIKE '%joo%2019%' ORDER BY a.filename""", limit=20)
print(r['rows'])
d = json.load(open('handoff/drive_index.json'))
for x in d:
    t=x['title'] or ''
    if t.startswith('MH370 – Search and debris examination update') or t.startswith('SEE APPENDIX B FOR HYDROPHONES') or t.startswith('Underwater_acoustic_analysis') or t.startswith('Kadri et al Acoustic') or 'Drift_simulation_of_MH370' in t:
        print(x['id'], t[:90], x['fileSize'], x['modifiedTime'][:10])
