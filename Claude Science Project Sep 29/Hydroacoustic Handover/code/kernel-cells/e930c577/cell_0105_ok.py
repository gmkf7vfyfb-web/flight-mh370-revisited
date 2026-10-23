
s=open("leg/fig_levels.py").read()
s=s.replace('ax.set_title("a  Impacts on the bearing strip", loc="left"); ax.legend(frameon=False, loc="lower right", fontsize=5.5, handlelength=1)',
            'ax.set_title("a  Impacts on the bearing strip", loc="left"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2, fontsize=5.5, handlelength=1)')
s=s.replace('ax.set_title("b  If the Cape Leeuwin arrival is the impact", loc="left"); ax.legend(frameon=False, loc="lower right", fontsize=5.5, handlelength=1)',
            'ax.set_title("b  Implied by the Cape Leeuwin level", loc="left"); ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=2, fontsize=5.5, handlelength=1)')
s=s.replace('wspace=0.55','wspace=0.62').replace('fig.text(0.01, -0.08,','fig.text(0.01, -0.2,').replace('fig.text(0.01, -0.17,','fig.text(0.01, -0.29,')
open("leg/fig_levels.py","w").write(s); exec(s); host.view_image("leg/fig/received-level-detectability.png")
