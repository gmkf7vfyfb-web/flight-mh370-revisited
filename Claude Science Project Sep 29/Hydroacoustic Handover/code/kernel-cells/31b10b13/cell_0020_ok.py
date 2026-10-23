
import tl_grid_table as TT
for rx in R.RECEIVERS:
    print(rx, [round(float(TT.tl_at(M.xs, M.tl[rx][:,j], np.array([P.REF_LAT]))[0]),1) for j in range(len(R.BANDS_HZ))], round(M.bmed[rx],1), M.teff[rx].round(2))
