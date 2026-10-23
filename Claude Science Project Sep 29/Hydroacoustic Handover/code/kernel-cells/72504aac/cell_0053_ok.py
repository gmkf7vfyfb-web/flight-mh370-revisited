
src=src.replace("xytext=(-95,-62),textcoords='offset points',fontsize=7,color=C_G","xytext=(30,-80),textcoords='offset points',fontsize=7,color=C_G")
src=src.replace("figsize=(10.5,7.7)); ax=fig.add_axes([0.065,0.43,0.92,0.54])","figsize=(10.5,7.2)); ax=fig.add_axes([0.065,0.44,0.92,0.53])")
src=src.replace("bbox_to_anchor=(0.06,0.405)","bbox_to_anchor=(0.06,0.41)")
exec(src); fig=chart1(); save(fig,'chart1-geometry-pair-g')
