set -e
F="warn|z\[j\]|out\['d0'\]"
OUT=run14v2 NSLIDE=1000 python run14.py 2>&1 | grep -v -i -E "$F" | grep model
OUT=run14v2_null3275 NULLSUB=IMOS3275:IMOS3274 NSLIDE=1000 python run14.py 2>&1 | grep -v -i -E "$F" | grep model
OUT=run14v2_null3315 NULLSUB=IMOS3315:IMOS3376 NSLIDE=1000 python run14.py 2>&1 | grep -v -i -E "$F" | grep model
OUT=run14v2_a6floor A6FLOOR=1 MODELS=primary NSLIDE=1000 python run14.py 2>&1 | grep -v -i -E "$F" | grep -E "model|IMOS"
INJ_OUT=imos_injections_physics_v2.csv NPER=60 OMP_NUM_THREADS=1 python imos_inject.py 2>&1 | grep -v -i -E "$F" | tail -16
INJ_OUT=imos_injections_purenull_v2.csv OMP_NUM_THREADS=1 python inject_null.py 2>&1 | grep -v -i -E "$F" | tail -8
