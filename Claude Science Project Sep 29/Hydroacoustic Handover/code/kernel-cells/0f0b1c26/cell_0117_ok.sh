python - <<'EOF'
s=open('fig2.py').read()
s=s.replace("ax.set_xscale('log'); ax.set_xticks([5,10,20,40]); ax.set_xticklabels(['5','10','20','40'])","ax.set_xscale('log'); ax.set_xticks([5,10,20,40]); ax.set_xticklabels(['5','10','20','40']); ax.xaxis.set_minor_formatter(mpl.ticker.NullFormatter())")
s=s.replace("ax.set_ylabel('Energy spectral density (dB re 1 µPa² s/Hz)')","ax.set_ylabel('Energy density (dB re 1 µPa² s/Hz)')")
s=s.replace("'The two models agree within 4 dB'","'Models agree on the charge path only'")
s=s.replace("The two models agree with each other, so the difference","The two models agree with each other on this path, so the difference")
s=s.replace("Paths: ocean transport","On the aircraft path the two models differ by up to 10 dB above 25 Hz. Paths: ocean transport")
open('fig2.py','w').write(s)
EOF
echo ok