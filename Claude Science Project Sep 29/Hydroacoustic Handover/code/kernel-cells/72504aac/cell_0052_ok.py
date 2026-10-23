
import inspect, types
src=inspect.getsource(chart1)
src=src.replace("figsize=(10.5,8.4)); ax=fig.add_axes([0.065,0.385,0.92,0.565])","figsize=(10.5,7.7)); ax=fig.add_axes([0.065,0.43,0.92,0.54])")
src=src.replace("xytext=(-175,-12),textcoords='offset points',fontsize=7,color=C_G","xytext=(-95,-62),textcoords='offset points',fontsize=7,color=C_G")
src=src.replace("bbox_to_anchor=(0.06,0.355)","bbox_to_anchor=(0.06,0.405)")
exec(src)
fig=chart1(); save(fig,'chart1-geometry-pair-g')
