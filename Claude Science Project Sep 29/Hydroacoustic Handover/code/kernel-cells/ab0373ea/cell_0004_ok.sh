P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cat "$P"/tl_grid_table.py > /tmp/t.txt; echo; grep -n "def \|RAM\|ram\|rule 2\|fg\|no_modes" "$P"/tl_grid_table.py | head -60
echo ====RUNJ; grep -n "def \|fg\|FG\|rcv_depth\|kind\|seabed\|- 2" "$P"/tl_grid_run_j.py | head -60
echo ====KRAKEN; grep -n "def \|fg" "$P"/kraken_tl.py | head; 
echo ====LEVELS; grep -n "tl.table\|tl_table\|ramcorr\|argparse\|add_argument" "$P"/run_j_levels.py | head -40
uptime