cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
python - <<'EOF'
s=open("charts.py").read()
s=s.replace('bbox_to_anchor=(0.5, 0.975))\n    fig.supxlabel(','bbox_to_anchor=(0.5, 0.935))\n    fig.supxlabel(')
s=s.replace('fontsize=8, y=0.215)','fontsize=8, y=0.2)')
s=s.replace('fig.subplots_adjust(top=0.85, bottom=0.25, left=0.06, right=0.99, hspace=0.3, wspace=0.08)','fig.subplots_adjust(top=0.82, bottom=0.25, left=0.06, right=0.99, hspace=0.3, wspace=0.08)')
s=s.replace('fig.suptitle("Matched filters built','fig.suptitle("Matched filters built'.replace('fig.suptitle','fig.suptitle'))
s=s.replace('fontsize=9.5, x=0.01, ha="left", y=0.995)','fontsize=9.5, x=0.01, ha="left", y=0.995, va="top")')
# fig 2: box labels inside the trace panel top, title moved up by pad
s=s.replace('ax.text((ta + tb) / 2, 1.02, name.replace("poster (a) ", "").replace(" time ", " "), fontsize=6, ha="center", va="bottom", transform=ax.get_xaxis_transform())',
            'ax.text((ta + tb) / 2, 0.97, name.replace("poster (a) ", "").replace(" time ", "\\n"), fontsize=6, ha="center", va="top", transform=ax.get_xaxis_transform())')
open("charts.py","w").write(s)
EOF
WS=$(cd ../../../../../../..; pwd); python charts.py "$WS/out" "$WS/out/figs" 2>&1 | grep -v Warning | tail -1