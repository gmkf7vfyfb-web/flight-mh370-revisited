AT=$PWD/tools; W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python nx2d.py $AT $W/nx2d air7-H01W -22.91283333 87.01827803 -34.890303 114.142637 1055.0 $W/sections/builder/ssp_air7_H01W.csv --src-depths 10.0 --bands 16 20 25 31.5 40 50 63 > $W/nx2d.log 2>&1
tail -15 $W/nx2d.log