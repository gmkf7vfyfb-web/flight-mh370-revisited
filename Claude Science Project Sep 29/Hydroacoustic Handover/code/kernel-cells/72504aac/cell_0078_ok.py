
src6=src6.replace("a1=fig.add_axes([0.06,0.40,0.40,0.52]); a2=fig.add_axes([0.53,0.40,0.44,0.52])","a1=fig.add_axes([0.06,0.44,0.40,0.49]); a2=fig.add_axes([0.53,0.44,0.44,0.49])")
src6=src6.replace("xytext=(25,45),textcoords='offset points',fontsize=6.5,color=C_G","xytext=(-10,60),textcoords='offset points',fontsize=6.5,color=C_G,ha='center'")
src6=src6.replace("bbox_to_anchor=(0.06,0.375),ncol=4","bbox_to_anchor=(0.06,0.385),ncol=4")
exec(src6); fig=chart6(); save(fig,'chart6-neighbourhood-pair-g')
