W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal
python -c "
import json; L=json.load(open('$W/sections.json')) if False else json.load(open('$W/sections/sections.json'))
for k,v in L.items():
    if not k.startswith('air7_offset'): print(k, v)
"
ls $W/sections/builder $W/sections/shared; wc -l $W/sections/builder/ssp_air7_H01W.csv $W/sections/builder/bathy_air7_H01W.csv