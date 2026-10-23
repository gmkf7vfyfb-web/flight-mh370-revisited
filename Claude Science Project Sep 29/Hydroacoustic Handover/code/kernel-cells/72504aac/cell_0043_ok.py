
def sph_az(la1,lo1,la2,lo2):
    p1,p2=np.radians(la1),np.radians(la2); dl=np.radians(lo2-lo1)
    return np.degrees(np.arctan2(np.sin(dl)*np.cos(p2), np.cos(p1)*np.sin(p2)-np.sin(p1)*np.cos(p2)*np.cos(dl)))%360
for r in ['H01W','H08S']:
    la,lo=rx[r]; print(r, sph_az(la,lo,G['lat'],G['lon']), hav(la,lo,G['lat'],G['lon']))
