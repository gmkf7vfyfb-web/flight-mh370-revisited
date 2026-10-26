#!/bin/sh
# rebuild_all.sh - rebuild hydro_data.sqlite in the fixed stage order (26 Oct 2026). Never edit the database by hand.
# Usage: sh rebuild_all.sh <module root on hypothesis/hydroacoustics> <'Claude Science Project Sep 29' folder on claude-science-sep29> <out.sqlite> [log]
#   needs (read-only): ~/Downloads/mh370-inputs/hydroacoustics/imos (stage 1), ~/Downloads/mh370-ocean-data/gebco/grid (arc stage)
# Stage order (meta table key stage_order): build_hydro_data_db.py -> build_noise_coupling.py -> build_imports.py -> build_noise_fixes.py
#   -> arc_line_of_sight.py -> arc_station_count.py -> VACUUM.  Maps and the opportunity charts (make_sites_map.py,
#   arc_recording_opportunity.py) read the database only and are re-made when their inputs change.
set -e
MOD="$1"; WORK="$2"; OUT="$3"; LOG="${4:-build_log.txt}"
HERE=$(cd "$(dirname "$0")" && pwd)
IMOS="${MH370_HYDRO_INPUTS:-$HOME/Downloads/mh370-inputs/hydroacoustics}/imos"
GEBCO="${MH370_OCEAN_DATA:-$HOME/Downloads/mh370-ocean-data}/gebco/grid"
rm -f "$OUT"
HEAD=$(git -C "$MOD" rev-parse --short HEAD)
{
python "$HERE/build_hydro_data_db.py" --mod "$MOD" --imos "$IMOS" --fdsn "$HERE/ims_stations_all.txt" --out "$OUT" --git-head "$HEAD"
echo "# stage 2"; python "$HERE/build_noise_coupling.py" --db "$OUT" --mod "$MOD" --coupling "$HERE/inputs/coupling" --record "$HERE/NOISE_COUPLING_RECORD.md"
echo "# stage 3"; python "$HERE/build_imports.py" --db "$OUT" --mod "$MOD" --work "$WORK" --manifest "$HERE/imports.yaml"
echo "# stage 4"; python "$HERE/build_noise_fixes.py" --db "$OUT" --mod "$MOD"
echo "# arc"; python "$HERE/arc_line_of_sight.py" --db "$OUT" --gebco "$GEBCO"
python "$HERE/arc_station_count.py" --db "$OUT" --out "$HERE/arc_los_station_count"
} > "$LOG" 2>&1
sqlite3 "$OUT" "DELETE FROM meta WHERE key='stage_order'; INSERT INTO meta VALUES ('stage_order', 'build_hydro_data_db.py -> build_noise_coupling.py -> build_imports.py -> build_noise_fixes.py -> arc_line_of_sight.py -> arc_station_count.py (rebuild_all.sh)'); VACUUM;"
sqlite3 "$OUT" "SELECT result, count(*) FROM check_log GROUP BY result"
