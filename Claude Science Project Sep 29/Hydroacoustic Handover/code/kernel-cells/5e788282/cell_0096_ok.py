src=open(str(MOD)+"/prepare/metz_f35a/charts.py").read().replace("def save(fig, name):","def _save_unused(fig, name):")
MOD=str(MOD); OUT=str(OUT); X=str(X)
exec(src)