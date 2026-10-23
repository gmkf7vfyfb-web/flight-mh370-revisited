set -e
cd "$PWD"
SRC=/Users/pete/Downloads/mh370-exchange/hydroacoustics/sources
mkdir -p "$SRC/open-access-fetched-2026-10-22"
cd articles
declare -A NAMES=(
 ["10.1038_s41598-018-37626-z.pdf"]="Kadri_2019_Effect_of_sea-bottom_elasticity_SciRep9-912_s41598-018-37626-z.pdf"
 ["10.1017_jfm.2022.1091.pdf"]="Williams_2023_Slender_rupture_elastic_seabed_JFM_jfm.2022.1091.pdf"
 ["10.5194_nhess-7-243-2007.pdf"]="Nosov_2007_Tokachi-oki_water_column_NHESS_7-243.pdf"
 ["10.1038_s41597-024-04074-6.pdf"]="Chu_Fan_2024_Global_undersea_acoustic_parameters_SciData_s41597-024-04074-6.pdf"
)
for k in "${!NAMES[@]}"; do
  cp -p "$k" "$SRC/open-access-fetched-2026-10-22/${NAMES[$k]}"
  cp -p "$k" "../${NAMES[$k]}"
done
cd "$SRC/open-access-fetched-2026-10-22"; ls -la; shasum -a 256 *.pdf | cut -c1-16,65-
python3 - <<'EOF'
import pypdf,glob
for f in sorted(glob.glob('*.pdf')):
    r=pypdf.PdfReader(f); print(f[:40], len(r.pages),'pp |', (r.pages[0].extract_text() or '')[:90].replace('\n',' '))
EOF