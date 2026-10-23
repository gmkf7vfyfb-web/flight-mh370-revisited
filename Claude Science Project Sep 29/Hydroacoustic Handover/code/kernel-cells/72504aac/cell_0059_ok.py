
src4=src4.replace("off={'Pair':(-45,45,'right')","off={'Pair':(-75,45,'center')")
exec(src4); fig=chart4(); save(fig,'chart4-bearings-pair-g')
print(os.path.exists(X+'/hydroacoustics/graphics-2026-10-22/ranked/ranked_pairs.csv'))
