import os, sys, importlib
WS_ROOT = os.getcwd()
os.environ["OMP_NUM_THREADS"]="1"
exec(open("gfx/charts_levels.py").read())
style()
print(chart_station("H01W", "chart01-noise-vs-levels-H01W"))