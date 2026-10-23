cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n '/^import/,/^def observed_bands/p' air9_tl_validation.py | grep -v '^\s*$' | head -90
echo ===== ; sed -n '/^def main/,$p' air9_tl_validation.py | head -60
echo ===== convert; sed -n '/^def convert/,$p' shared_paths.py | head -50
echo ===== tl_path; sed -n '/^def tl_path/,/^def /p' kraken_tl.py | head -60