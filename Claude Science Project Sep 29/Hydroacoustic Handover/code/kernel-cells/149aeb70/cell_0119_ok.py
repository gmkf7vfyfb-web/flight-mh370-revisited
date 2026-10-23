import matplotlib.pyplot as plt, pandas as pd; plt.close("all")
exec(open("make_h08s_fig.py").read())
o = pd.read_csv(host.artifact_path("cfb4a586-b3da-4c1b-80a8-b3ba11ec57b7"))
print(o[["cls","t_utc","z","coincident"]].to_string(index=False))
