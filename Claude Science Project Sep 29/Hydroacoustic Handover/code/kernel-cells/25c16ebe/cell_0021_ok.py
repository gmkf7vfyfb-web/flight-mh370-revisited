print("max |E_transferred - total KE| / KE :", float(np.nanmax(np.abs(etj-ke)/ke)))
print("debris_class:", dict(zip(*[a.tolist() for a in np.unique(Y[:,ci['latent:debris_class']], return_counts=True)])))
print("contact_speed_feasible weighted (none/both):",
      float(P['none'][Y[:,ci['latent:contact_speed_feasible']]==1].sum()/P['none'].sum()),
      float(P['both/no-offset'][Y[:,ci['latent:contact_speed_feasible']]==1].sum()/P['both/no-offset'].sum()))
# low-altitude sustained flight check: time between end of descent and impact
nondesc = (Y[:,ci["t_impact_s"]]-Y[:,ci["t_onset_s"]]) - Y[:,ci["latent:time_descending_s"]]
print("non-descending seconds between onset and impact, q (none):", [round(x,1) for x in wq(nondesc,P['none'])])
print("P(non-descending > 600 s | none):", float(P['none'][nondesc>600].sum()/P['none'].sum()))
np.savez("audit/figdata.npz",
   t_onset=Y[:,ci['t_onset_s']], t_impact=Y[:,ci['t_impact_s']], fpa=Y[:,ci['flight_path_angle_deg']],
   spd=spd, ke=ke, vke=vke, tau=tau, bank=Y[:,ci['latent:impact_bank_deg']], fam4=fam4,
   w_none=P['none'], w_r600=P['r600/no-offset'], w_both=P['both/no-offset'],
   w_r1200=P['r1200/no-offset'], w_sso=P['both/startup-offset'], lat=Y[:,ci['latitude_deg']])
print("saved figdata")
