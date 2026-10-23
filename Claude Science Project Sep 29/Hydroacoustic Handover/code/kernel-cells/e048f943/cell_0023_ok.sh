cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics
sed -n 75,130p prepare/imos_preregistration.py
python -c "
import json;p=json.load(open('data/imos/preregistration.json'));print({k:v for k,v in p['loggers'].items()})" | cut -c1-900
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/3376/20140301 | head -3; ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/3376/20140301 | wc -l
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/MH370/ /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/Portland_MH370/ | head; find /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos -iname "*alibration*" -maxdepth 3 | head