set +e
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== shared_paths.py"; sed -n '1,60p' "$H/prepare/shared_paths.py" 2>/dev/null | cut -c1-200
echo "=== how kraken binaries are found"; grep -n -E 'at_bin|kraken\.exe|field\.exe|which|PATH|artifact' "$H/prepare/kraken_tl.py" "$H/prepare/air9_tl_validation.py" "$H/prepare/imos_stageB_tl.py" | cut -c1-200 | head -15
echo "=== ocean paths request (what transport gave us)"; head -c 600 "$H/data/ocean_paths/request.json"; echo; ls /Users/pete/Downloads/mh370-exchange/ocean-transport/; ls /Users/pete/Downloads/mh370-exchange/ocean-transport/paths* | head -40
echo "=== stageB tl: where bathy/ssp come from"; grep -n -E 'read_csv|np\.load|open\(|\.nc|gebco|GEBCO|woa|WOA|exchange|inputs' "$H/prepare/imos_stageB_tl.py" | cut -c1-200 | head -20