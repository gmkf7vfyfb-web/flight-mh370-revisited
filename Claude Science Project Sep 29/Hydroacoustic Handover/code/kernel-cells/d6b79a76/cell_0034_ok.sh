cd kh && python3 - <<'E'
s=open('run_flight_leg.py').read()
a=s.index("    np.savez_compressed(out / 'maps.npz'"); b=s.index("    print('DONE'")
s=s[:a]+"    pickle.dump({k: (float(v[0]), v[1]) for k, v in maps.items()}, open(out / 'maps.pkl', 'wb'))\n    json.dump({'LOC': W.LOC, 'WIDE': W.WIDE, 'keys': list(maps)}, open(out / 'maps-meta.json', 'w'))\n"+s[b:]
open('run_flight_leg.py','w').write(s)
E
rm -rf rows_smoke; lockf -t 0 /tmp/.mh370-heavy.lock echo FREE || echo HELD; df -h ~/Downloads | tail -1