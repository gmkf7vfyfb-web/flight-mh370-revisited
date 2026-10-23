set +e
cat tools/BUILD-NOTES.txt | head -20
mkdir -p /tmp/krk && cd /tmp/krk
cat > t.env <<'EOF'
'test'
20.0
1
'NVW '
0 0.0 4000.0
0.0 1500.0 /
1000.0 1480.0 /
4000.0 1520.0 /
'A' 0.0
4000.0 1650.0 0.0 1.9 0.5 /
1400.0 1600.0
1
10.0 /
1
1000.0 /
EOF
for L in /Users/pete/.claude-science/conda/envs/mh370-hydro/lib /opt/homebrew/lib /usr/local/lib; do
  DYLD_LIBRARY_PATH=$L timeout 60 "$OLDPWD/tools/Kraken/kraken.exe" t 2>&1 | tail -2; echo "exit=$? with $L"; ls t.mod 2>/dev/null && break
done
ls