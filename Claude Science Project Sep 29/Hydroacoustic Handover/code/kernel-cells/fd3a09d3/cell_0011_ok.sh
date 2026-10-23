cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo ==== nx2d docstring+blockage; sed -n 1,45p prepare/nx2d.py; grep -n -i "block\|axis\|cut\|shallow" prepare/nx2d.py | head -30
echo ==== air8 blockage; grep -n -i "block\|axis\|cut\|shallow\|threshold" prepare/air8_negative_control.py | head -20
echo ==== imos_path_blockage; cat data/ocean_paths/imos_path_blockage.csv | head -30
echo ==== request_ims; python -c "
import json;d=json.load(open('data/ocean_paths/request_ims.json'));print(json.dumps(d)[:1200])"
echo ==== run_ims_tl; sed -n 1,40p prepare/exploratory/run_ims_tl.py