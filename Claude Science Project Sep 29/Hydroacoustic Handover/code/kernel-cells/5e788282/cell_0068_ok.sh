X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a; mkdir -p $X/at && tar xzf "{{artifact:1bd321c2-571c-42e1-a8f4-b0a2c3eff82e}}" -C $X/at && ls $X/at && du -sh $X/at
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib
cd /tmp && $X/at/Kraken/kraken.exe 2>&1 | head -3