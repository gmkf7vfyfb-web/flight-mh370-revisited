import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rgb=np.array(Image.open(host.artifact_path("99b55187-e5c8-4c37-abff-0482499b5a7f")).convert("RGB"))
fig,ax=plt.subplots(figsize=(7,9)); ax.imshow(rgb, interpolation="nearest")
for st,P in panels.items():
    t=traces[st]; ax.plot(t.x_px, P["ytop"]+(150-t.tl_db)*3.6, "r.", ms=2)
ax.set_xlim(40,345); ax.set_ylim(420,140); ax.set_axis_off()
fig.savefig("hydro/fig23_trace_check.png", dpi=150, bbox_inches="tight")