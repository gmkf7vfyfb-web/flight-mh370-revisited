F="warn|z\[j\]|out\['d0'\]"
OUT=run14v3_eqclean CALFILE=imos_calib_eqclean.pkl NSLIDE=1000 python run14.py 2>&1 | grep -v -i -E "$F" | grep -E "model|IMOS"
OUT=run14v3_eqclean_remove CALFILE=imos_calib_eqclean.pkl EQREMOVE=1 MODELS=primary NSLIDE=1000 python run14.py 2>&1 | grep -v -i -E "$F" | grep model
