
src3=src3.replace("xytext=(30,-95),textcoords='offset points',fontsize=6,color=C_T1","xytext=(30,-62),textcoords='offset points',fontsize=6,color=C_T1")
src3=src3.replace("fig.text(0.06,0.975,","fig.text(0.06,0.99,").replace("[0.06,0.36,0.43,0.58]),fig.add_axes([0.54,0.36,0.43,0.58])","[0.06,0.36,0.43,0.57]),fig.add_axes([0.54,0.36,0.43,0.57])")
exec(src3); fig=chart3(); save(fig,'chart3-hpd-maps-pair-g')
