cd leg; rmdir out/path_blockage.csv; python - <<'E'
s=open('geometry_windows.py').read()
s=s.replace('OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)\n','')
a,b=s.split('rows, pts = [], []\n',1)
b='def main(OUT):\n    OUT = pathlib.Path(OUT); OUT.mkdir(parents=True, exist_ok=True)\n    rows, pts = [], []\n'+''.join('    '+l if l.strip() else l for l in b.splitlines(True))+'\n\nif __name__ == "__main__":\n    main(sys.argv[1])\n'
open('geometry_windows.py','w').write(a+b)
E
python geometry_windows.py out > /dev/null 2>&1 && md5 -q out/arrival_windows.csv; python blockage.py out/path_blockage.csv 2>&1 | grep -v -i proj