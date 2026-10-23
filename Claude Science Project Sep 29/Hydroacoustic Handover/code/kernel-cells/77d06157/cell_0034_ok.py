import inspect
print(inspect.signature(apply_figure_style)); print((apply_figure_style.__doc__ or '')[:1500])
print([n for n in dir() if not n.startswith('_')][:40])