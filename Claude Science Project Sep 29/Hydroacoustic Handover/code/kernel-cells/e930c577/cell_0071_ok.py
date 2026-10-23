
import textwrap
src=open("leg/fig_windows.py").read()
src=src.replace('ax.plot(s(d[rk]) / 60, y + 0.42, marker="v", ms=3.2, color=PICK, zorder=5, clip_on=True)','ax.plot(s(d[rk]) / 60, y, marker="v", ms=3.6, color=PICK, mec="white", mew=0.4, zorder=6, clip_on=True)')
src=src.replace('fig.text(0.01, -0.06, f1, fontsize=5.6, wrap=True, ha="left", va="top"); fig.text(0.01, -0.16, f2, fontsize=5.6, wrap=True, ha="left", va="top", color="#444444")',
 'import textwrap\nfig.text(0.01, -0.04, "\\n".join(textwrap.wrap(f1, 190)), fontsize=5.6, ha="left", va="top"); fig.text(0.01, -0.12, "\\n".join(textwrap.wrap(f2, 190)), fontsize=5.6, ha="left", va="top", color="#444444")')
open("leg/fig_windows.py","w").write(src)
exec(src.replace('exec(open(sys.argv[1]).read()) if len(sys.argv) > 1 else None','None'))
host.view_image("leg/fig/arrival-windows-corrected.png")
