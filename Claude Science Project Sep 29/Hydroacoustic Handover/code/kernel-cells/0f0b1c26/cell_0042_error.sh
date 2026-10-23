cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python -c "
import ast
for f in ['calibration_events.py','f35a_eta_calibration.py','segmented_paths.py','shared_paths.py']:
    print('=====',f); print(ast.get_docstring(ast.parse(open(f).read()))[:3000])
"; head -c 5000 "../../../../results/hydroacoustics-calibration-events-stage1-standin.md"