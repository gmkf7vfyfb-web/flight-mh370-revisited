
import os; os.chdir(os.path.expanduser(os.getcwd()))
apply_figure_style(sizes=(7,6,5.5))
exec(open("leg/fig_windows.py").read().replace('exec(open(sys.argv[1]).read()) if len(sys.argv) > 1 else None','None'))
host.view_image("leg/fig/arrival-windows-corrected.png")
