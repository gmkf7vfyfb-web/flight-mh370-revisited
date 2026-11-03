"""Value-of-information test, second version (3 Nov 2026, session d1ea5f58). Exploratory; unchecked.
Question: if a station detected the impact, how much would that move the probability along the 7th arc?
Prior: flat in latitude 41-20 S on the arc line (zero contour of the run J arc-distance field), cross-arc N(0, 20 NM),
5 NM steps to +/-60 NM. Arrival t = t0 + d/c, c = 1.482 +/- 0.006 km/s, pick error 10 s. Impact time t0 shared by all
stations, N(mu, sd), marginalised exactly (covariance diag(s_k^2) + sd^2). Direction: Cape Leeuwin 0.66 deg (plus 2 deg
north of 25.5 S), Diego Garcia South 1.0 deg (assumed). 300 synthetic sources from the prior per case.
Inputs: arc-grid.npz (mh370-exchange/searched-areas/run-j-supplement), site table of hydro_data.sqlite.
Output: value-of-information-test.csv, value-of-information-impact-time.csv.
Usage: python voi_v2.py <arc-grid.npz> <hydro_data.sqlite>"""
import sys, sqlite3, numpy as np, pandas as pd
from pyproj import Geod
G = Geod(ellps="WGS84"); rng = np.random.default_rng(20261103)
z = np.load(sys.argv[1]); arcg = z["arc"].astype(float); nn = z["n"]; s0, w0, st = float(z["south"]), float(z["west"]), float(z["step"])
lonsg = w0 + st*np.arange(arcg.shape[1])
def arc_lon(lat, off=0.0):
    i = int(round((lat - s0)/st)); ok = nn[i] > 0
    near = ok & (np.abs(arcg[i]-off) <= 150.0); use = near if near.sum() >= 20 else ok
    A = np.vstack([np.ones(use.sum()), arcg[i][use]]).T; c = np.linalg.lstsq(A, lonsg[use], rcond=None)[0]
    return float(c[0] + c[1]*off)
lats = np.round(np.arange(-41.0, -19.99, 0.1), 2); offs = np.arange(-60, 61, 5.0)
LAT = np.repeat(lats, len(offs)); OFF = np.tile(offs, len(lats)); LON = np.array([arc_lon(a, o) for a, o in zip(LAT, OFF)])
site = pd.read_sql("select * from site", sqlite3.connect(sys.argv[2])).set_index("site_id")
ST = ["H01W","H08S","IMOS3315","SSEIR","SWAMS3","MAD","NCRO","WKER"]
D, AZ = {}, {}
for k in ST:
    az, _, d = G.inv(np.full(len(LAT), site.loc[k,"lon"]), np.full(len(LAT), site.loc[k,"lat"]), LON, LAT); D[k] = d/1000; AZ[k] = az
C, SC = 1.482, 0.006
prior = np.exp(-0.5*(OFF/20.0)**2); prior /= prior.sum(); along = (LAT-LAT.min())*111.2
def bsd(k, lat):
    if k == "H01W": return np.sqrt(0.66**2 + (4.0 if lat > -25.5 else 0.0))
    if k == "H08S": return 1.0
    return None
def run(ks, bearing=False, sig_t=180.0, pick=10.0, ntruth=300):
    out = []; tr = rng.choice(len(LAT), size=ntruth, p=prior)
    Dm = np.stack([D[k] for k in ks], 1); AZm = np.stack([AZ[k] for k in ks], 1)
    for i in tr:
        s2 = pick**2 + (Dm[i]*SC/C**2)**2; Sig = np.diag(s2) + sig_t**2
        t_obs = Dm[i]/C + rng.multivariate_normal(np.zeros(len(ks)), Sig)
        Si = np.linalg.inv(Sig); r = t_obs[None,:] - Dm/C; ll = -0.5*np.einsum("ij,jk,ik->i", r, Si, r)
        if bearing:
            for j, k in enumerate(ks):
                if bsd(k, LAT[i]) is None: continue
                ob = AZm[i,j] + rng.normal(0, bsd(k, LAT[i])); dz = (AZm[:,j]-ob+180) % 360 - 180
                sdx = np.array([bsd(k, a) for a in LAT]); ll += -0.5*(dz/sdx)**2 - np.log(sdx)
        post = prior*np.exp(ll-ll.max()); post /= post.sum(); m = post > 0
        kl = np.sum(post[m]*np.log2(post[m]/prior[m])); mu = np.sum(post*along); sd = np.sqrt(np.sum(post*(along-mu)**2))
        out.append((kl, sd, abs(mu-along[i])/max(sd, 1e-9)))
    a = np.array(out); return dict(bits=np.median(a[:,0]), bits_p10=np.percentile(a[:,0],10), bits_p90=np.percentile(a[:,0],90), sd_km=np.median(a[:,1]), D=np.median(a[:,2]))
configs = [("Cape Leeuwin",["H01W"]),("Diego Garcia South",["H08S"]),("Perth Canyon logger",["IMOS3315"]),("SSEIR",["SSEIR"]),
           ("Cape Leeuwin + Perth Canyon",["H01W","IMOS3315"]),("Cape Leeuwin + Diego Garcia South",["H01W","H08S"]),
           ("Cape Leeuwin + SSEIR",["H01W","SSEIR"]),("Diego Garcia South + SSEIR",["H08S","SSEIR"]),
           ("Cape Leeuwin + Diego Garcia South + SSEIR",["H01W","H08S","SSEIR"]),("five OHASISBIO sites",["SSEIR","SWAMS3","MAD","NCRO","WKER"]),("all eight sites",ST)]
if __name__ == "__main__":
    rows = []
    for name, ks in configs:
        for b in (False, True):
            if b and not any(k in ("H01W","H08S") for k in ks): continue
            rows.append(dict(config=name, bearing=b, **run(ks, b)))
    pd.DataFrame(rows).to_csv("value-of-information-test.csv", index=False)
    sens = [dict(config=n, sig_t=s, **{k: v for k, v in run(ks, False, sig_t=s, ntruth=200).items() if k in ("bits","sd_km")})
            for n, ks in [c for c in configs if c[0] in ("Cape Leeuwin","SSEIR","Cape Leeuwin + Diego Garcia South","Cape Leeuwin + SSEIR","all eight sites")]
            for s in (60.0, 180.0, 600.0, 1200.0)]
    pd.DataFrame(sens).to_csv("value-of-information-impact-time.csv", index=False)
