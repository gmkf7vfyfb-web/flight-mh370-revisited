fig.subplots_adjust(bottom=0.19)
fig.savefig(str(FIG)+".png",dpi=300); fig.savefig(str(FIG)+".pdf")
xl_=axc.xaxis.label.get_window_extent(r_); ft=[t for t in fig.texts if t.get_text().startswith("Run:")][0].get_window_extent(r_)
print(xl_.y0, ft.y1)