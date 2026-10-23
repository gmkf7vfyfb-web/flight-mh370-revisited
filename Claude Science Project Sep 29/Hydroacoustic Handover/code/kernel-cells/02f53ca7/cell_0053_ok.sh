W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
mkdir -p ../results-data/tl_recal_block9/nx2d_air7-H01W; cp $W/nx2d/air7-H01W/members.csv $W/nx2d/air7-H01W/corridor.csv ../results-data/tl_recal_block9/nx2d_air7-H01W/
python tl_recal_block9.py air7 ../results-data/tl_recal_block9 ../results-data/tl_recal_block9/nx2d_air7-H01W/corridor.csv ../results-data/airgun_sites_confirm 2>&1 | cut -c1-250