python - <<'EOF'
s=open('fig1.py').read()
s=s.replace("ax.set_ylabel('Pressure (Pa); upper traces offset')","ax.set_ylabel('Pressure (Pa)')")
s=s.replace("bbox_to_anchor=(0,-0.30)","bbox_to_anchor=(0,-0.40)")
s=s.replace("ax.set_ylabel('5-40 Hz level (dB re panel max)')","ax.set_ylabel('Level, 5-40 Hz (dB)')")
s=s.replace("ax.set_xlim(100,350)","ax.set_xlim(100,345)")
s=s.replace("label='Nielsen et al. (2021) Fig. 3, scaled to the same peak')","label='Nielsen et al. (2021) Fig. 3, scaled to the same peak (upper traces offset)')")
s=s.replace("hspace=0.75","hspace=0.95").replace("bottom=0.33","bottom=0.30").replace("figsize=(7.2,6.6)","figsize=(7.2,7.0)")
s=s.replace("(d) CMST Fig. 2: jet colour scale","(d) level in dB relative to each panel's maximum; CMST Fig. 2: jet colour scale")
open('fig1.py','w').write(s)
EOF
echo done