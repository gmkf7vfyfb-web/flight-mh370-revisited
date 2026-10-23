for t in fig.findobj(mpl.text.Text):
    s=t.get_text()
    if s.startswith(("objects reported","306.18","first contact","bearing meets","study area","towed-pinger")):
        t.set_bbox(dict(fc="white",ec="none",alpha=0.85,pad=0.6))
fig.savefig("out/fig-locality-sources-map.png",dpi=300); print("ok")