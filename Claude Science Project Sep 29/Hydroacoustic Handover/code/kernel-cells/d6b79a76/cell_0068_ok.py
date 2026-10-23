import glob, re
NEED=['row','parent','f4','d_km','az_deg','db_deg','xt_km','dX_km','dH_km','tau90_s','energy_transferred_j','bank_deg_att','bank_source','in_strip','in_X200','in_H200','acoustic_keep',
 'unix_s','takeover_unix_s','latent:realised_flameout_unix_s','latent:onset_unix_s','latitude_deg','longitude_deg','velocity_east_mps','velocity_north_mps','velocity_up_mps','flight_path_angle_deg','mass_kg',
 'bto_residual_us:m0019a','bto_residual_us:m0019b','bfo_innovation_hz:m0019a','bfo_innovation_hz:m0019b','latent:onset_mechanism','latent:control_realised','latent:profile_shape','latent:engines_thrusting_at_onset',
 'latent:spiral_divergent','latent:max_descent_rate_fpm','latent:time_descending_s','latent:state_m0019a_altitude_ft','latent:state_m0019a_vertical_speed_fpm','latent:state_m0019b_altitude_ft','latent:state_m0019b_vertical_speed_fpm',
 'latent:impact_heading_deg','latent:impact_bank_deg','latent:pushover_drawn','latent:pitchdown_drawn','latent:turns_davey_begun','latent:turns_terminal_begun','latent:sweep_begun','latent:circuit_begun','latent:circuit_final_kind',
 'latent:heading_change_deg','latent:pushover_to_surface','latent:ap_loss_config','latent:free_dynamics_started_s','kinetic_energy_j','latent:last_burst_latitude_deg','latent:last_burst_longitude_deg','takeover_altitude_ft']
def load_rows(path):
    z=np.load(path); keys=set(z.files); d={}
    for c in NEED:
        cc=c.replace('/','_')
        d[c]=z[cc] if cc in keys else np.full(len(z['row']),np.nan)
    for k in z.files:
        if k.startswith('lm|') or k.startswith('lnL|') or k.startswith('z2|'): d[k]=z[k]
    df=pd.DataFrame(d); m=re.match(r'(.*)-seed-(\d+)\.npz',path.split('/')[-1]); df['stratum']=m.group(1); df['seed']=int(m.group(2)); return df
R=pd.concat([load_rows(p) for p in sorted(glob.glob('kh/out/rows/*.npz'))], ignore_index=True)
print(R.shape, R.memory_usage().sum()/1e9); print(R.stratum.value_counts().to_dict())