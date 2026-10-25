
def footnotes(fig, ste, tech, top=0.17, w1=165, w2=175):
    import textwrap
    r = fig.canvas.get_renderer()
    t1 = fig.text(0.01, top, "\n".join(textwrap.wrap(ste, w1)), fontsize=6, va="top")
    bb = t1.get_window_extent(r).transformed(fig.transFigure.inverted())
    fig.text(0.01, bb.y0 - 0.012, "\n".join(textwrap.wrap(tech, w2)), fontsize=5.3, va="top", color="0.25")
