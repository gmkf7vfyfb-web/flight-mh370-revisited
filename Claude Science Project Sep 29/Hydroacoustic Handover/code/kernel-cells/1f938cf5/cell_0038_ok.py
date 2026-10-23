
print(Lm.groupby('stratum')[['t_impact_s','weight','vh','vd','latent:debris_class','latent:breakup_p_intact','loglik:r600/no-offset','latent:impact_heading_deg']].apply(lambda g:g.isna().mean()).round(3))
print(Lm.groupby('stratum').t_impact_s.describe().round(0))
