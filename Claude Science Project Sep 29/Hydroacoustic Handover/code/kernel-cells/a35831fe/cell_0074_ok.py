k=R.verdict.str.startswith(('FEASIBLE','WEAK','LIKELY'))
print(R[k][['id','receivers','times','implied_lat','implied_lon','implied_impact','prior_mass_1deg','energy_test','verdict']].to_string())
print(Pc[(Pc.rx_a=='3315')&(Pc.t_a=='00:47:16')|(Pc.band_a if 'band_a' in Pc else False)].shape if False else '')
print((P.band_a.astype(str).str.startswith('2-5')|P.band_b.astype(str).str.startswith('2-5')).sum(), s.band.astype(str).str.startswith('2-5').sum())