cd .tmp/standin; python - <<'EOF'
s=open("chart_calibration.py").read()
s=s.replace('ax[0].invert_yaxis()','ax[0].set_ylim(166, 104)')
s=s.replace('ax[0].set_xticks([5, 10, 20, 40]); ax[0].set_xticklabels(["5", "10", "20", "40"])','ax[0].set_xticks([5, 10, 20, 40]); ax[0].set_xticklabels(["5", "10", "20", "40"]); ax[0].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())')
s=s.replace('ax[2].set_xticks([5, 10, 20, 40]); ax[2].set_xticklabels(["5", "10", "20", "40"])','ax[2].set_xticks([5, 10, 20, 40]); ax[2].set_xticklabels(["5", "10", "20", "40"]); ax[2].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())')
s=s.replace('"C. Navy charge (provisional, plain 2-D):\\nsource level that the model needs; numbers = fewest modes"','"C. Navy charge (provisional, plain 2-D): source level\\nthe model needs (numbers: fewest modes on the path)"')
s=s.replace('0.36, 0.27, 0.52','0.33, 0.27, 0.56')
s=s.replace('the model\\n"','the model "').replace('am. 1),\\n"','am. 1), "').replace('bottom model.\\n"','bottom model. "')
s=s.replace('fig.text(0.015, 0.215, ste, fontsize=7.3, va="top", wrap=True)','import textwrap\nfig.text(0.015, 0.215, textwrap.fill(ste, 250), fontsize=7.3, va="top")')
s=s.replace('fig.text(0.015, 0.115, tech, fontsize=7.0, va="top", color="0.2", wrap=True)','fig.text(0.015, 0.14, textwrap.fill(tech, 262), fontsize=7.0, va="top", color="0.2")')
s=s.replace('import matplotlib.pyplot as plt','import matplotlib.pyplot as plt, matplotlib.ticker')
open("chart_calibration.py","w").write(s)
EOF
python chart_calibration.py && echo ok