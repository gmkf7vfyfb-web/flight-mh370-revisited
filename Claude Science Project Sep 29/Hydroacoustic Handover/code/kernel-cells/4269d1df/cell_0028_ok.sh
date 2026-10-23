cd jobsnap && python3 - <<'EOF'
s=open('run.sh').read()
s=s.replace('cd $W\nfor M','TIME="/usr/bin/time -v"; [ -x /usr/bin/time ] || TIME=""\ncd $W\nfor M',1).replace('/usr/bin/time -v $BIN','$TIME $BIN')
open('run.sh','w').write(s)
EOF
grep -n TIME run.sh | head