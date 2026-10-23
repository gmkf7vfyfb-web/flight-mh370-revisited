set -e
src='/Users/pete/Downloads/art%3A10.1007%2Fs00024-022-03117-6.pdf'
dst='/Users/pete/Downloads/mh370-exchange/hydroacoustics/sources/Metz_Obana_Fukao_2023_Remote_hydroacoustic_detection_airplane_crash_PAGEOPH_s00024-022-03117-6.pdf'
cp -p "$src" "$dst"
cp -p "$src" ./Metz_Obana_Fukao_2023_Remote_hydroacoustic_detection_airplane_crash.pdf
shasum -a 256 "$src" "$dst" | cut -c1-24
ls -la "$dst"