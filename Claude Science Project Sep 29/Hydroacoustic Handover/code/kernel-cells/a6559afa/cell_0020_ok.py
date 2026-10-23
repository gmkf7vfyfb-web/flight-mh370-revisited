r=host.query("SELECT id, model, delegate_name FROM frames WHERE id IN ('d74bf70e-a424-46a9-8149-902d027e782a','676a6e64-2eac-490f-b67d-6c3f5c82f047','a35831fe-107a-4961-bc9f-e6fd6d255601','0bb05edc-67da-48f0-9322-bf94577b110d') OR parent_frame_id='676a6e64-2eac-490f-b67d-6c3f5c82f047'")
from collections import Counter
print(Counter((x[1]) for x in r['rows']))
for x in r['rows']:
    if x[2] is None: print(x)