cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python "$H/prepare/digitise_kadri_2019.py" --pdf articles/10.1038_s41598-018-37626-z.pdf; python -c "
import json; m=json.load(open('$H/results-data/digitised/kadri-2019/METHOD.json')); print({k:v for k,v in m['text_layer_number_check'].items() if not v})"