ls /Users/pete/Downloads/mh370-ocean-data/products/hydro-paths-2001-10/ /Users/pete/Downloads/mh370-ocean-data/products/hydro-paths-2001-10-ausseabed/ | head -60
ls /Users/pete/Downloads/mh370-ocean-data/gebco/grid/ /Users/pete/Downloads/mh370-ocean-data/woa23/soundspeed/ | head -30
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; sed -n '/^import/,/^def _grid/p' nx2d.py | grep -v "^$" | head -40
echo "=== station coords"; grep -i "H01W\|H08S\|H08N" ../data/stations.csv | head -12