
src4=inspect.getsource(chart4)
src4=src4.replace('''    ax.annotate("Kadri's 00:52 bearing, text p. 9: 57°\\n(towards land; never meets the arc)",(O[len(O)//3],L[len(L)//3]),xytext=(-40,-40),textcoords='offset points',fontsize=6.5,color=C_KADRI,ha='right',
                arrowprops=dict(arrowstyle='-',color=C_KADRI,lw=0.5))\n''','')
src4=src4.replace("Line2D([],[],color=C_ARC,ls='--',label='7th arc'),","Line2D([],[],color=C_ARC,ls='--',label='7th arc'),Line2D([],[],color=C_KADRI,lw=1.4,label=\"Kadri's 00:52 bearing, text p. 9: 57° (towards land; never meets the arc)\"),")
assert "never meets" in src4 and src4.count("never meets")==1
exec(src4); fig=chart4(); save(fig,'chart4-bearings-pair-g')
