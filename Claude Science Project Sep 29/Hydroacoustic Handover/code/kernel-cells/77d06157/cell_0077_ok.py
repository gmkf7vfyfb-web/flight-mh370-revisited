exec(open("gfx/charts_traces.py").read()); style()
print(chart9("chart09-illustrative-traces"))
print(pd.read_csv(OUT/"chart09-illustrative-traces-values.csv").round(2).to_string())