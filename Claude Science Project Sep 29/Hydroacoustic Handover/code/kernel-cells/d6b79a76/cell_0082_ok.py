src=open('kh/figures.py').read()
src=src.replace("ax.set_xticklabels([OPT[d] for d in ds], fontsize=6)","ax.set_xticklabels(['00:19 data\\nnot used','00:19:29\\nrange only','00:19:29 range\\nand frequency','Both 00:19\\nfrequencies\\nas recorded','Both 00:19\\nfrequencies, shared\\nstart-up offset','00:19:29 frequency\\nas recorded, 00:19:37\\nwith offset'], fontsize=6)")
src=src.replace("fig.text(0.0, -0.13,","fig.text(0.0, -0.17,").replace("fig.text(0.0, -0.22,","fig.text(0.0, -0.26,")
open('kh/figures.py','w').write(src); exec(src); fig_bf()