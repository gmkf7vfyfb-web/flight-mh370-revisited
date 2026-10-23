
src4=src4.replace("'Table 1, 00:39:02':(-45,-118,'right')","'Table 1, 00:39:02':(-45,-100,'right')").replace("figsize=(8.2,8.6)); ax=fig.add_axes([0.09,0.37,0.88,0.57])","figsize=(8.2,8.0)); ax=fig.add_axes([0.09,0.385,0.88,0.565])")
ext4=(82,117,-44,-15); xc4,yc4,H4=hpd_grid(slat,slon,sw,ext4)
exec(src4); fig=chart4(); save(fig,'chart4-bearings-pair-g')
