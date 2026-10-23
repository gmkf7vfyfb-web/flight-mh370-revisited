set -e
mkdir -p tools && cd tools
tar xzf "{{artifact:1bd321c2-571c-42e1-a8f4-b0a2c3eff82e}}"
ls; find . -name 'kraken.exe' -o -name 'field.exe' | head
AT=$(dirname $(dirname $(find . -name kraken.exe | head -1)))
echo "AT=$PWD/$AT"
file $(find . -name kraken.exe | head -1) | cut -c1-120
cd ..
echo "=== mh370-hydro env check"; /Users/pete/.claude-science/conda/envs/mh370-hydro/bin/python -c "import gsw,pyproj,scipy,numpy,pandas,matplotlib; print('ok', scipy.__version__)" 2>&1 | tail -1
echo "=== otool deps"; otool -L $(find tools -name kraken.exe | head -1) 2>/dev/null | head -6