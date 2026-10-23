import os, copernicusmarine as cm
u,p=host.credentials.get("COPERNICUS")['value'].split(':',1)
os.makedirs('ocean',exist_ok=True)
try:
    r=cm.subset(dataset_id="cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m", variables=["uo","vo"],
            minimum_longitude=78, maximum_longitude=114, minimum_latitude=-48, maximum_latitude=-10,
            start_datetime="2014-03-07T00:00:00", end_datetime="2014-04-30T00:00:00", minimum_depth=0, maximum_depth=1,
            output_directory="ocean", output_filename="globcurrent_2014.nc", username=u, password=p, disable_progress_bar=True)
    print(r)
except Exception as e:
    print(type(e).__name__, str(e)[:800])