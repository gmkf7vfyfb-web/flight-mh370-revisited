
src=open("energy_chart.py").read()
a='''    for i in range(1, len(ys)): ys[i] = max(ys[i], ys[i-1] + sep)
'''
b='''    for i in range(1, len(ys)): ys[i] = max(ys[i], ys[i-1] + sep)
    sh = np.mean([v[0] for v in L]) - np.mean(ys); ys = [y + sh for y in ys]
'''
assert a in src; src=src.replace(a,b).replace('ax.text(2.2e9, e50_new*1.3,','ax.text(1.4e9, e50_new*1.3,').replace('ax.text(2.2e9, e50_old*1.3,','ax.text(1.4e9, e50_old*1.3,')
open("energy_chart.py","w").write(src); plt.close("all"); exec(src)
