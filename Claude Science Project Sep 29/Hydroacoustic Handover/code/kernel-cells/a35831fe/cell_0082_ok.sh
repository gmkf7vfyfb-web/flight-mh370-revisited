cd /Users/pete/Downloads/mh370-exchange; cat composer/run-j-views-v3.2/README.md; echo ====; cat composer/run-j-views-v3.2-australia/README.md | head -60; echo ====; cat searched-areas/spatial-fields-v2/README.md; python - <<'E'
import json,numpy as np
print(json.dumps(json.load(open('searched-areas/spatial-fields-v2/fields.json')))[:2500])
for f in ['composer/run-j-views-v3.2/maps-v3.npz','composer/run-j-views-v3.2/pdf01-v3.npz','composer/run-j-views-v3.2-australia/maps-australia-v3.2.npz','searched-areas/spatial-fields-v2/fields.npz']:
    d=np.load(f,allow_pickle=True); print(f,{k:(d[k].shape,d[k].dtype) for k in list(d.files)[:30]})
E