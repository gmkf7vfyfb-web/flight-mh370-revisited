#!/usr/bin/env python3
"""Generate deterministic 00:11 lateral-control structural-sensitivity figures.

The script reads estimator artifacts only. Structural families are never pooled;
the only pooling is equal weighting of the three numerical seeds within a family.
"""

from __future__ import annotations

import argparse, base64, csv, hashlib, json, math, os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1394237459")
import matplotlib as mpl
mpl.use("Agg")
mpl.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.5, "axes.facecolor": "#fbfcfd",
    "axes.grid": True, "grid.color": "#dfe4e9", "grid.linewidth": .65,
    "pdf.fonttype": 42, "svg.fonttype": "none",
    "svg.hashsalt": "mh370-0011-lateral-structural-sensitivity", "savefig.dpi": 300,
})
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter, gaussian_filter1d
from scipy.optimize import brentq
from scipy.spatial import cKDTree

SEEDS = (370023, 370024, 370025)
META = (
    ("constant-true-track", "Constant true track", "#0072B2", "o"),
    ("constant-true-heading", "Constant true heading", "#E69F00", "s"),
    ("constant-magnetic-track", "Constant magnetic track", "#009E73", "D"),
    ("constant-magnetic-heading", "Constant magnetic heading", "#CC79A7", "^"),
)
LAT_BOUNDS, LON_BOUNDS = (-38.8, -30.8), (85.5, 97.0)
BANDWIDTH_NM, ARC_ALT_FT = 7.5, 35_000.0
EPOCH = "2014-03-08T00:10:59Z"
SCOPE = ("Shared one-turn boundary: one post-radar switch, then one fixed control interpretation; "
         "excludes later mode changes, waypoint/LNAV routes, arbitrary heading schedules, fuel and end-of-flight dynamics.")
WARNING = ("PROVISIONAL 00:11 diagnostic — not an impact PDF; 3/4 families are nonconverged "
           "and final R600 largely disconfirms the spread under unchanged modes.")

def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""): value.update(block)
    return value.hexdigest()

def replace_text(path,text):
    temporary=path.with_name(f".{path.name}.tmp")
    temporary.write_text(text)
    os.replace(temporary,path)

def quantile(x, w, ps):
    order = np.argsort(x, kind="mergesort"); x, w = np.asarray(x)[order], np.asarray(w)[order]
    return np.interp(ps, np.cumsum(w) / np.sum(w), x)

def distance(a, b):
    p1, p2 = np.radians([a[0], b[0]]); dp, dl = np.radians([b[0]-a[0], b[1]-a[1]])
    h = np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return float(2*3440.065*np.arcsin(np.sqrt(np.clip(h, 0, 1))))

def load_run(run):
    suite_path, manifest_path = run/"suite-summary.json", run/"run-manifest.json"
    suite, manifest = json.loads(suite_path.read_text()), json.loads(manifest_path.read_text())
    if suite.get("schema_version") not in (1, 2) or manifest.get("schema_version") != suite.get("schema_version"):
        raise ValueError("unsupported or mixed source artifact schemas")
    if suite["schema_version"] == 2:
        if suite.get("config_schema_version") != manifest.get("config_schema_version"):
            raise ValueError("source config schema mismatch")
        if suite.get("handoff_schema_version") != 2 or manifest.get("handoff_schema_version") != 2:
            raise ValueError("source handoff schema mismatch")
        structural = {item["name"]: item for item in manifest.get("structural_families", [])}
        if sorted(structural) != sorted(item[0] for item in META):
            raise ValueError("source structural-family manifest mismatch")
        if any(item.get("fixed_waypoint") is not None for item in structural.values()):
            raise ValueError("lateral-control reporter does not accept fixed-waypoint families")
    lookup = {item["name"]: item for item in suite["families"]}
    if sorted(lookup) != sorted(item[0] for item in META): raise ValueError("wrong family set")
    if any(lookup[key]["antenna_gain_applied"] for key, *_ in META): raise ValueError("antenna must be off")
    if any(lookup[key]["pooled_particles"] != 90_000 for key, *_ in META): raise ValueError("requires 30k x 3")
    if manifest["config_sha256"] != digest(Path(manifest["config_path"])): raise ValueError("config hash mismatch")
    columns = ["weight", "last_contact_latitude_deg", "last_contact_longitude_deg", "altitude_ft",
               "mach", "turn_time_s", "post_turn_track_true_deg", "bfo_bias_hz"]
    inputs, families = [suite_path, manifest_path], []
    for key, label, color, marker in META:
        seeds, pieces = [], []
        for seed in SEEDS:
            folder = run/key/f"seed-{seed}"; csv_path, sm_path = folder/"posterior.csv", folder/"summary.json"
            cp_path = folder/"checkpoints.json"; inputs += [csv_path, sm_path, cp_path]
            frame, seed_artifact = pd.read_csv(csv_path, usecols=columns), json.loads(sm_path.read_text())
            if suite["schema_version"] == 2:
                if seed_artifact.get("schema_version") != 2 or seed_artifact.get("handoff_schema_version") != 2:
                    raise ValueError(f"invalid seed artifact schema: {sm_path}")
                run_identity = seed_artifact.get("run", {})
                if (run_identity.get("model_family"), run_identity.get("seed"), run_identity.get("lateral_mode")) != (key, seed, key):
                    raise ValueError(f"seed guidance identity mismatch: {sm_path}")
                if run_identity.get("fixed_waypoint") is not None or seed_artifact.get("fixed_waypoint_identity_sha256") is not None:
                    raise ValueError(f"scalar seed unexpectedly carries a route: {sm_path}")
                sm = seed_artifact["summary"]
            else:
                sm = seed_artifact
            if len(frame) != 30_000 or not np.isclose(frame.weight.sum(), 1, atol=2e-9): raise ValueError(csv_path)
            keys = ["last_contact_latitude_deg", "last_contact_longitude_deg", "altitude_ft", "mach",
                    "turn_time_s", "post_turn_track_true_deg"]
            combined = frame.groupby(keys, sort=False, dropna=False).weight.sum()
            seeds.append({"seed": seed, "frame": frame, "lat": sm["last_contact_mean"]["latitude"],
                          "lon": sm["last_contact_mean"]["longitude"], "logz": sm["log_evidence"],
                          "accept": sm["minimum_mutation_acceptance"],
                          "unique_ess": 1/np.square(combined.to_numpy()).sum(), "max_dup": combined.max()})
            piece = frame.copy(); piece.weight /= 3; pieces.append(piece)
        families.append({"key": key, "label": label, "color": color, "marker": marker,
                         "summary": lookup[key], "seeds": seeds, "frame": pd.concat(pieces, ignore_index=True)})
    return suite, families, inputs

def load_compatibility(run):
    folder=run/"r600-predictive-control"
    result_path=folder/"r600_predictive_compatibility.json"
    csv_path=folder/"r600_predictive_compatibility.csv"
    manifest_path=folder/"r600_predictive_compatibility_manifest.json"
    result=json.loads(result_path.read_text()); manifest=json.loads(manifest_path.read_text())
    if result.get("schema_version") != 2 or manifest.get("schema_version") != 2 or manifest.get("result_schema_version") != 2 or result.get("status") != "complete_control":
        raise ValueError("R600 compatibility control is incomplete")
    if (result.get("source_suite_artifact_schema_version"), result.get("source_config_schema_version"), result.get("source_handoff_schema_version")) != (1, 1, 1):
        raise ValueError("R600 compatibility does not identify the canonical legacy scalar source")
    if result.get("source_epoch_id") != "m0011" or result.get("structural_pooling") != "none":
        raise ValueError("R600 compatibility control has the wrong scientific boundary")
    for path in (result_path,csv_path):
        if manifest["output_sha256"].get(path.name) != digest(path):
            raise ValueError(f"R600 compatibility hash mismatch: {path}")
    lookup={item["family"]:item for item in result["families"]}
    if sorted(lookup) != sorted(item[0] for item in META):
        raise ValueError("R600 compatibility control has the wrong family set")
    return result,lookup,[result_path,csv_path,manifest_path]

def ecef(lat, lon, altitude):
    a, f = 6378.137, 1/298.257223563; e2 = f*(2-f); lat, lon = np.radians(lat), np.radians(lon)
    n = a/np.sqrt(1-e2*np.sin(lat)**2)
    return np.stack([(n+altitude)*np.cos(lat)*np.cos(lon), (n+altitude)*np.cos(lat)*np.sin(lon),
                     (n*(1-e2)+altitude)*np.sin(lat)], axis=-1)

def bto_arc():
    sat, ges = np.array([18181.15895,38050.48229,434.568805]), np.array([-2368.8,4881.1,-3342.0])
    ground_range, altitude = np.linalg.norm(sat-ges), ARC_ALT_FT*.0003048
    def residual(lat, lon):
        predicted = 2*(np.linalg.norm(sat-ecef(lat,lon,altitude))+ground_range)/299792.458*1e6-499962+4283
        return float(predicted-18040)
    lats, trial = np.linspace(-30.5,-39,851), np.linspace(75,110,701); lons=[]
    for lat in lats:
        values=np.array([residual(lat,lon) for lon in trial]); roots=[]
        for lo,hi,a,b in zip(trial[:-1],trial[1:],values[:-1],values[1:]):
            if a*b<0: roots.append(brentq(lambda lon: residual(lat,lon),lo,hi))
        if not roots: raise RuntimeError(f"no BTO root at {lat}")
        lons.append(max(roots))
    lons=np.asarray(lons); along=np.zeros(len(lats))
    for i in range(1,len(lats)): along[i]=along[i-1]+distance((lats[i-1],lons[i-1]),(lats[i],lons[i]))
    along -= np.interp(-31,lats[::-1],along[::-1]); return lats,lons,along

def project(families, lats, lons, along):
    phi, lam=np.radians(lats),np.radians(lons)
    tree=cKDTree(np.c_[np.cos(phi)*np.cos(lam),np.cos(phi)*np.sin(lam),np.sin(phi)])
    def one(lat,lon):
        phi,lam=np.radians(np.asarray(lat)),np.radians(np.asarray(lon)); unit=np.c_[np.cos(phi)*np.cos(lam),np.cos(phi)*np.sin(lam),np.sin(phi)]
        return along[tree.query(unit)[1]]
    for family in families:
        f=family["frame"]; family["along"]=one(f.last_contact_latitude_deg,f.last_contact_longitude_deg)
        offset=0
        for seed in family["seeds"]: seed["along"],offset=family["along"][offset:offset+30_000],offset+30_000
    return tree

def hpd(mass,p):
    ranked=np.sort(mass.ravel())[::-1]; return ranked[min(np.searchsorted(np.cumsum(ranked),p),len(ranked)-1)]

def surface(frame):
    ye=np.linspace(*LAT_BOUNDS,221); xe=np.linspace(*LON_BOUNDS,301)
    mass,_,_=np.histogram2d(frame.last_contact_latitude_deg,frame.last_contact_longitude_deg,
                            bins=(ye,xe),weights=frame.weight)
    sy=BANDWIDTH_NM/((ye[1]-ye[0])*60.0405); sx=BANDWIDTH_NM/((xe[1]-xe[0])*60.0405*np.cos(np.radians(-34.8)))
    mass=gaussian_filter(mass,(sy,sx),mode="constant"); mass/=mass.sum()
    return (xe[:-1]+xe[1:])/2,(ye[:-1]+ye[1:])/2,mass,hpd(mass,.5),hpd(mass,.9)

def map_axis(ax,lats,lons):
    ax.set_xlim(*LON_BOUNDS); ax.set_ylim(*LAT_BOUNDS); ax.set_aspect(1/np.cos(np.radians(-34.8)))
    ax.plot(lons,lats,color="#333b44",lw=1.1,ls=(0,(6,4)),zorder=3)
    ax.set_xticks(np.arange(86,97,2)); ax.set_yticks(np.arange(-38,-30,1))
    ax.set_xticklabels([f"{x:.0f}°E" for x in ax.get_xticks()]); ax.set_yticklabels([f"{abs(y):.0f}°S" for y in ax.get_yticks()])

def footer(fig):
    fig.text(.5,.030,SCOPE,ha="center",fontsize=8.4,color="#4c5966")
    fig.text(.5,.008,WARNING,ha="center",fontsize=8.7,color="#8a3b2f",weight="bold")

def save(fig,out,stem,title):
    created=datetime(2014,3,8,0,10,59,tzinfo=timezone.utc); paths=[]
    for suffix in ("svg","pdf","png"):
        path=out/f"{stem}.{suffix}"
        temporary=path.with_name(f".{path.name}.tmp")
        if suffix=="svg": meta={"Creator":"MH370 structural reporter","Title":title,"Date":EPOCH}
        elif suffix=="pdf": meta={"Creator":"MH370 structural reporter","Title":title,"CreationDate":created,"ModDate":created}
        else: meta={"Software":"MH370 structural reporter","Title":title}
        fig.savefig(temporary,format=suffix,dpi=300,facecolor="white",metadata=meta)
        os.replace(temporary,path); paths.append(path)
    plt.close(fig); return paths

def common_panels(families,lats,lons,out):
    title="Model-conditioned 00:11 densities under four lateral-control assumptions"
    fig,axes=plt.subplots(2,2,figsize=(13,9.2),sharex=True,sharey=True)
    fig.suptitle(title,y=.985,fontsize=17,weight="bold",color="#10243e")
    fig.text(.5,.954,"Same SATCOM data, priors, ERA5/IGRF environment and 4 Hz BFO; no auxiliary likelihoods.",ha="center",color="#465464")
    for ax,family in zip(axes.ravel(),families):
        map_axis(ax,lats,lons); x,y,m,t50,t90=surface(family["frame"])
        ax.contourf(x,y,m,levels=[t90,t50,m.max()*(1+1e-9)],colors=[family["color"]]*2,alpha=.22,zorder=2)
        ax.contour(x,y,m,levels=[t90],colors=[family["color"]],linewidths=2.1,zorder=4)
        ax.contour(x,y,m,levels=[t50],colors=[family["color"]],linewidths=1.4,linestyles="--",zorder=4)
        for seed in family["seeds"]:
            sx,sy,sm,_,st90=surface(seed["frame"])
            ax.contour(sx,sy,sm,levels=[st90],colors=[family["color"]],linewidths=.65,alpha=.42,zorder=4)
            ax.scatter(seed["lon"],seed["lat"],marker=family["marker"],s=22,facecolor="white",edgecolor=family["color"],lw=.9,zorder=6)
        mean=family["summary"]["pooled_mean"]; ax.scatter(mean["longitude"],mean["latitude"],marker=family["marker"],s=68,color=family["color"],edgecolor="white",lw=1.2,zorder=7)
        ok=family["summary"]["converged"] is True; ax.set_title(family["label"],loc="left",weight="bold",color=family["color"])
        ax.text(.985,.965,"CONVERGED" if ok else "NONCONVERGED",transform=ax.transAxes,ha="right",va="top",fontsize=7.5,weight="bold",color="white",
                bbox={"boxstyle":"round,pad=.25","facecolor":"#2A6F62" if ok else "#A23B3B","edgecolor":"none"})
        ax.text(.02,.025,f"mean {abs(mean['latitude']):.3f}°S, {mean['longitude']:.3f}°E\nseed sep {family['summary']['maximum_seed_mean_separation_nm']:.1f} NM; Δlog Z {family['summary']['log_evidence_range']:.3f}",
                transform=ax.transAxes,fontsize=7.3,va="bottom",bbox={"boxstyle":"round","facecolor":"white","alpha":.82,"edgecolor":"none"})
    for ax in axes[-1]: ax.set_xlabel("Longitude")
    for ax in axes[:,0]: ax.set_ylabel("Latitude")
    fig.text(.5,.061,f"Pooled 90%/50% HPD; thin contours/open markers are individual seeds. Display kernel σ={BANDWIDTH_NM:.1f} NM.",ha="center",fontsize=8,color="#4c5966")
    footer(fig); fig.subplots_adjust(left=.075,right=.985,bottom=.105,top=.92,wspace=.10,hspace=.16)
    return save(fig,out,"lateral_control_common_scale_panels",title)

def overlay(families,lats,lons,out):
    title="Lateral-control assumptions displace the 00:11 posterior"
    fig,ax=plt.subplots(figsize=(12.2,8.5)); map_axis(ax,lats,lons); means=[]
    label_offsets={
        "constant-true-track":(8,-32),
        "constant-true-heading":(12,8),
        "constant-magnetic-track":(12,8),
        "constant-magnetic-heading":(-180,10),
    }
    for family in families:
        x,y,m,t50,t90=surface(family["frame"]); c=family["color"]
        ax.contour(x,y,m,levels=[t90],colors=[c],linewidths=2.6,zorder=4); ax.contour(x,y,m,levels=[t50],colors=[c],linewidths=1.5,linestyles="--",zorder=4)
        mean=family["summary"]["pooled_mean"]; means.append((mean["latitude"],mean["longitude"]))
        for seed in family["seeds"]: ax.scatter(seed["lon"],seed["lat"],marker=family["marker"],s=28,facecolor="white",edgecolor=c,lw=1,zorder=6)
        ax.scatter(mean["longitude"],mean["latitude"],marker=family["marker"],s=88,color=c,edgecolor="white",lw=1.2,zorder=7)
        status="converged" if family["summary"]["converged"] else "nonconverged"
        ax.annotate(f"{family['label']}\n{abs(mean['latitude']):.3f}°S, {mean['longitude']:.3f}°E ({status})",(mean["longitude"],mean["latitude"]),xytext=label_offsets[family["key"]],textcoords="offset points",fontsize=8,color=c,weight="bold",bbox={"boxstyle":"round,pad=.2","facecolor":"white","alpha":.8,"edgecolor":"none"})
    ax.plot([means[0][1],means[-1][1]],[means[0][0],means[-1][0]],color="#586675",lw=1.2,ls=(0,(5,5)))
    mid=((means[0][1]+means[-1][1])/2,(means[0][0]+means[-1][0])/2)
    ax.text(*mid,f"{distance(means[0],means[-1]):.0f} NM between extreme means",ha="center",va="center",fontsize=11,weight="bold",bbox={"boxstyle":"round","facecolor":"white","edgecolor":"#75818c"},zorder=9)
    handles=[Line2D([0],[0],color=f["color"],marker=f["marker"],lw=2.4,label=f["label"]) for f in families]
    handles += [Line2D([0],[0],color="#333",lw=2.4,label="90% HPD"),Line2D([0],[0],color="#333",lw=1.5,ls="--",label="50% HPD"),Line2D([0],[0],color="#333",lw=1.1,ls=(0,(6,4)),label="nominal 00:11 BTO arc")]
    ax.legend(handles=handles,loc="lower left",ncol=2,framealpha=.95); ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    fig.suptitle(title,y=.98,fontsize=17,weight="bold",color="#10243e"); fig.text(.5,.942,"Families are separate structural alternatives; no model probabilities are assigned and no family pooling is performed.",ha="center",color="#465464")
    fig.text(.5,.058,f"HPD contours use a σ={BANDWIDTH_NM:.1f} NM display kernel; open markers are seed means.",ha="center",fontsize=8,color="#4c5966")
    footer(fig); fig.subplots_adjust(left=.085,right=.985,bottom=.11,top=.91)
    return save(fig,out,"lateral_control_contour_overlay",title)

def ridge_curve(values,weights,edges):
    hist,_=np.histogram(values,bins=edges,weights=weights); smooth=gaussian_filter1d(hist.astype(float),BANDWIDTH_NM/(edges[1]-edges[0]),mode="constant")
    return smooth/smooth.max()

def ridgeline(families,lats,along,out):
    title="Narrow conditional densities occupy a broad 00:11 along-arc envelope"
    all_values=np.concatenate([f["along"] for f in families]); lo=math.floor(np.quantile(all_values,.0005)/25)*25-25; hi=math.ceil(np.quantile(all_values,.9995)/25)*25+25
    edges=np.linspace(lo,hi,int(hi-lo)+1); centers=(edges[:-1]+edges[1:])/2; fig,ax=plt.subplots(figsize=(12.6,8.4)); bases=np.arange(4)[::-1]
    for base,family in zip(bases,families):
        density=ridge_curve(family["along"],family["frame"].weight,edges); c=family["color"]
        ax.fill_between(centers,base,base+.72*density,color=c,alpha=.26); ax.plot(centers,base+.72*density,color=c,lw=2.1)
        for index,seed in enumerate(family["seeds"]): ax.plot(centers,base+.72*ridge_curve(seed["along"],seed["frame"].weight,edges),color=c,lw=.7,alpha=.42,ls=(0,(2+index,2)))
        q=quantile(family["along"],family["frame"].weight,[.05,.5,.95]); ax.plot(q[[0,2]],[base-.09]*2,color=c,lw=5,solid_capstyle="butt"); ax.scatter(q[1],base-.09,marker=family["marker"],s=46,color=c,edgecolor="white",zorder=5)
        status="converged" if family["summary"]["converged"] else "nonconverged"; ax.text(hi-4,base+.37,f"{status}; Δlog Z {family['summary']['log_evidence_range']:.3f}",ha="right",fontsize=8,color="#4b5967")
    ax.set_xlim(lo,hi); ax.set_ylim(-.4,4.0); ax.set_yticks(bases); ax.set_yticklabels([f["label"] for f in families])
    for tick,family in zip(ax.get_yticklabels(),families): tick.set_color(family["color"]); tick.set_weight("bold")
    ax.set_xlabel("Southward distance along nominal 35,000-ft 00:11 BTO arc from 31°S (NM)"); ax.set_ylabel("Fixed post-turn control interpretation")
    top=ax.twiny(); top.set_xlim(ax.get_xlim()); tick_lats=np.arange(-31,-39,-1); tick_dist=[np.interp(lat,lats[::-1],along[::-1]) for lat in tick_lats]; visible=[(d,lat) for d,lat in zip(tick_dist,tick_lats) if lo<=d<=hi]
    top.set_xticks([d for d,_ in visible]); top.set_xticklabels([f"{abs(lat):.0f}°S" for _,lat in visible]); top.set_xlabel("Approximate latitude on nominal arc")
    fig.suptitle(title,y=.98,fontsize=16.5,weight="bold",color="#10243e"); fig.text(.5,.942,"Filled curves pool numerical replicates only; thin curves show seeds; bars/markers show central 90% intervals and medians.",ha="center",color="#465464")
    fig.text(.5,.058,"Nearest-point arc projection is a display coordinate and does not remove cross-arc uncertainty.",ha="center",fontsize=8,color="#4c5966")
    footer(fig); fig.subplots_adjust(left=.20,right=.97,bottom=.12,top=.87)
    return save(fig,out,"lateral_control_along_arc_ridgeline",title)

def uncertainty(families,lats,lons,along,tree,out):
    title="Repeatable locations do not guarantee stable model evidence"
    def mean_along(lat,lon):
        p,l=np.radians([lat,lon]); unit=np.array([np.cos(p)*np.cos(l),np.cos(p)*np.sin(l),np.sin(p)]); return along[tree.query(unit)[1]]
    fig,(left,right)=plt.subplots(1,2,figsize=(13.2,8.5),gridspec_kw={"width_ratios":[1.45,1]}); bases=np.arange(4)[::-1]; offsets=(-.10,0,.10)
    for base,family in zip(bases,families):
        c=family["color"]; q=quantile(family["along"],family["frame"].weight,[.05,.5,.95]); left.plot(q[[0,2]],[base]*2,color=c,lw=6,alpha=.35,solid_capstyle="butt"); left.scatter(q[1],base,marker=family["marker"],s=85,color=c,edgecolor="white",zorder=5)
        logs=np.array([s["logz"] for s in family["seeds"]]); rel=logs-logs.min(); right.plot([0,rel.max()],[base]*2,color=c,lw=4,alpha=.35)
        for offset,seed,value in zip(offsets,family["seeds"],rel):
            left.scatter(mean_along(seed["lat"],seed["lon"]),base+offset,marker=family["marker"],s=42,facecolor="white",edgecolor=c,lw=1.2,zorder=6)
            right.scatter(value,base+offset,marker=family["marker"],s=44,facecolor="white",edgecolor=c,lw=1.2,zorder=6); right.text(value+.035,base+offset,str(seed["seed"])[-2:],fontsize=7,va="center",color=c)
        right.text(1.72,base,f"range {family['summary']['log_evidence_range']:.3f}\nmin unique-state ESS* {min(s['unique_ess'] for s in family['seeds']):.1f}\nmax duplicate mass {max(s['max_dup'] for s in family['seeds']):.3f}",fontsize=7.1,va="center",color="#42505e")
    all_values=np.concatenate([f["along"] for f in families]); left.set_xlim(math.floor(np.quantile(all_values,.001)/50)*50-25,math.ceil(np.quantile(all_values,.999)/50)*50+25); left.set_ylim(-.45,3.65); left.set_yticks(bases); left.set_yticklabels([f["label"] for f in families])
    for tick,family in zip(left.get_yticklabels(),families): tick.set_color(family["color"]); tick.set_weight("bold")
    left.set_xlabel("Southward distance along nominal 00:11 BTO arc from 31°S (NM)"); left.set_title("A. Location: seed means are comparatively close",loc="left",weight="bold")
    right.axvspan(0,.8,color="#cfe8df",alpha=.45); right.axvline(.8,color="#2A6F62",lw=1.4,ls="--"); right.text(.79,3.35,"declared range limit 0.8",ha="right",fontsize=8,color="#2A6F62")
    right.set_xlim(-.05,2.85); right.set_ylim(left.get_ylim()); right.set_yticks(bases); right.set_yticklabels([]); right.set_xlabel("Seed log evidence − within-family minimum (nats)"); right.set_title("B. Normalization: three ranges exceed limit",loc="left",weight="bold")
    fig.suptitle(title,y=.98,fontsize=17,weight="bold",color="#10243e"); fig.text(.5,.942,"Open symbols are the three deterministic seeds; filled symbols and thick bars are within-family pooled medians and central 90% intervals.",ha="center",color="#465464")
    fig.text(.5,.058,"*Duplicate-collapsed ESS combines exactly repeated particle states; it is a diversity diagnostic, not nominal weighted ESS.",ha="center",fontsize=8,color="#4c5966")
    footer(fig); fig.subplots_adjust(left=.18,right=.985,bottom=.12,top=.89,wspace=.20)
    return save(fig,out,"lateral_control_numerical_vs_structural",title)

def compatibility_panel(families,compatibility,control,out):
    title="Final R600 strongly discriminates among unchanged-mode continuations"
    fig,(mass_ax,ratio_ax)=plt.subplots(1,2,figsize=(13.2,7.0),gridspec_kw={"width_ratios":[1.15,1]})
    bases=np.arange(4)[::-1]
    for base,family in zip(bases,families):
        item=compatibility[family["key"]]; prior=item["propagated_prior_at_0019"]; color=family["color"]
        within_one=max(0.0,prior["mass_within_one_bto_sd"]); within_two=max(0.0,prior["mass_within_two_bto_sd"])
        ratio=item["predictive_likelihood_ratio_to_constant_true_track"]
        mass_ax.plot([0,within_two],[base,base],color=color,lw=12,alpha=.24,solid_capstyle="butt")
        mass_ax.plot([0,within_one],[base,base],color=color,lw=6,solid_capstyle="butt")
        mass_ax.scatter(within_one,base,marker=family["marker"],s=58,color=color,edgecolor="white",zorder=5)
        mass_ax.text(1.025,base,f"{100*within_one:.3g}% / {100*within_two:.3g}%",ha="right",va="center",fontsize=8,color=color,weight="bold")
        ratio_ax.plot([1e-4,ratio],[base,base],color=color,lw=4,alpha=.35,solid_capstyle="butt")
        ratio_ax.scatter(ratio,base,marker=family["marker"],s=70,color=color,edgecolor="white",zorder=5)
        if ratio > .4:
            ratio_ax.text(ratio/1.22,base+.24,f"{ratio:.3g}×",ha="right",fontsize=8,color=color,weight="bold")
        else:
            ratio_ax.text(ratio*1.25,base+.24,f"{ratio:.3g}×",ha="left",fontsize=8,color=color,weight="bold")
    labels=[family["label"] for family in families]
    mass_ax.set_xlim(0,1.05); mass_ax.set_ylim(-.55,3.55); mass_ax.set_yticks(bases); mass_ax.set_yticklabels(labels)
    for tick,family in zip(mass_ax.get_yticklabels(),families):
        tick.set_color(family["color"]); tick.set_weight("bold")
    mass_ax.set_xlabel("Prior predictive mass around observed R600 BTO")
    mass_ax.set_title("A. Within ±1σ / ±2σ of the measurement",loc="left",weight="bold")
    mass_ax.legend(handles=[Line2D([0],[0],color="#526475",lw=6,label="within ±1σ"),Line2D([0],[0],color="#526475",lw=12,alpha=.24,label="within ±2σ")],loc="lower right",framealpha=.95)
    ratio_ax.set_xscale("log"); ratio_ax.set_xlim(7e-5,1.6); ratio_ax.set_ylim(mass_ax.get_ylim())
    ratio_ax.set_yticks(bases); ratio_ax.set_yticklabels([]); ratio_ax.axvline(1,color="#42505e",lw=1,ls="--")
    ratio_ax.set_xlabel("Predictive likelihood ratio (CTT = 1; log scale)")
    ratio_ax.set_title("B. Relative R600 predictive density",loc="left",weight="bold")
    selection=control["selection"]
    fig.suptitle(title,y=.98,fontsize=16.5,weight="bold",color="#10243e")
    fig.text(.5,.935,f"Forward replay to {selection['time_utc'][11:19]} UTC; corrected R600 BTO {selection['observed_bto_us']:.0f} ± {selection['standard_deviation_us']:.0f} μs is the only new likelihood.",ha="center",color="#465464")
    fig.text(.5,.085,"Predictive ratios compare these four unchanged-mode continuations only; they are neither posterior model probabilities nor impact-location probabilities.",ha="center",fontsize=8.2,color="#4c5966")
    fig.text(.5,.062,"The 435 NM 00:11 span is therefore largely disconfirmed under unchanged modes; CMT and especially CMH should not be read as viable impact families.",ha="center",fontsize=8.3,color="#8a3b2f",weight="bold")
    footer(fig); fig.subplots_adjust(left=.19,right=.985,bottom=.20,top=.85,wspace=.17)
    return save(fig,out,"lateral_control_r600_compatibility",title)

def contact_sheet(out):
    items=[("lateral_control_common_scale_panels","1. Common-scale 2×2 maps"),("lateral_control_contour_overlay","2. Single contour overlay"),("lateral_control_along_arc_ridgeline","3. Along-arc ridgeline"),("lateral_control_numerical_vs_structural","4. Numerical vs structural")]
    boxes=[(40,95),(920,95),(40,735),(920,735)]; parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1775" viewBox="0 0 1800 1775">','<rect width="100%" height="100%" fill="white"/>','<text x="900" y="45" text-anchor="middle" font-family="DejaVu Sans,Arial" font-size="30" font-weight="700" fill="#10243e">Four treatments of 00:11 lateral-control structural sensitivity</text>','<text x="900" y="73" text-anchor="middle" font-family="DejaVu Sans,Arial" font-size="16" fill="#465464">Thumbnails only; use separate full-resolution SVG/PDF/PNG files.</text>']
    for (stem,label),(x,y) in zip(items,boxes):
        encoded=base64.b64encode((out/f"{stem}.svg").read_bytes()).decode("ascii")
        parts += [f'<rect x="{x}" y="{y}" width="840" height="590" rx="10" fill="#fbfcfd" stroke="#b8c1ca"/>',f'<text x="{x+18}" y="{y+29}" font-family="DejaVu Sans,Arial" font-size="20" font-weight="700" fill="#24384d">{label}</text>',f'<image x="{x+10}" y="{y+40}" width="820" height="535" preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{encoded}"/>']
    encoded=base64.b64encode((out/"lateral_control_r600_compatibility.svg").read_bytes()).decode("ascii")
    parts += ['<rect x="40" y="1345" width="1720" height="355" rx="10" fill="#fbfcfd" stroke="#b8c1ca"/>','<text x="58" y="1375" font-family="DejaVu Sans,Arial" font-size="20" font-weight="700" fill="#24384d">Separate evidence control: corrected R600 predictive compatibility</text>',f'<image x="50" y="1384" width="1700" height="305" preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{encoded}"/>']
    parts += [f'<text x="900" y="1730" text-anchor="middle" font-family="DejaVu Sans,Arial" font-size="15" fill="#4c5966">{SCOPE}</text>',f'<text x="900" y="1760" text-anchor="middle" font-family="DejaVu Sans,Arial" font-size="16" font-weight="700" fill="#8a3b2f">{WARNING}</text>','</svg>']
    path=out/"lateral_control_treatment_contact_sheet.svg"; replace_text(path,"\n".join(parts)+"\n"); return path

def supporting_files(out,families,compatibility,control):
    csv_path=out/"lateral_control_structural_sensitivity_summary.csv"
    csv_temporary=csv_path.with_name(f".{csv_path.name}.tmp")
    fields=["family","converged","mean_latitude_deg","mean_longitude_deg","maximum_seed_separation_nm","log_evidence_range_nats","minimum_mutation_acceptance","minimum_duplicate_collapsed_ess","maximum_duplicate_mass","r600_prior_mass_within_one_sd","r600_prior_mass_within_two_sd","r600_predictive_likelihood_ratio_to_ctt"]
    with csv_temporary.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator="\n"); writer.writeheader()
        for family in families:
            s=family["summary"]; control_family=compatibility[family["key"]]; prior=control_family["propagated_prior_at_0019"]
            writer.writerow({"family":family["key"],"converged":str(bool(s["converged"])).lower(),"mean_latitude_deg":f"{s['pooled_mean']['latitude']:.12f}","mean_longitude_deg":f"{s['pooled_mean']['longitude']:.12f}","maximum_seed_separation_nm":f"{s['maximum_seed_mean_separation_nm']:.9f}","log_evidence_range_nats":f"{s['log_evidence_range']:.9f}","minimum_mutation_acceptance":f"{s['minimum_mutation_acceptance']:.9f}","minimum_duplicate_collapsed_ess":f"{min(x['unique_ess'] for x in family['seeds']):.6f}","maximum_duplicate_mass":f"{max(x['max_dup'] for x in family['seeds']):.9f}","r600_prior_mass_within_one_sd":f"{max(0.0,prior['mass_within_one_bto_sd']):.12f}","r600_prior_mass_within_two_sd":f"{max(0.0,prior['mass_within_two_bto_sd']):.12f}","r600_predictive_likelihood_ratio_to_ctt":f"{control_family['predictive_likelihood_ratio_to_constant_true_track']:.12g}"})
    table=[]
    for family in families:
        item=compatibility[family["key"]]; prior=item["propagated_prior_at_0019"]
        table.append(f"| {family['label']} | {'yes' if family['summary']['converged'] else 'no'} | {100*max(0.0,prior['mass_within_one_bto_sd']):.3g}% | {100*max(0.0,prior['mass_within_two_bto_sd']):.3g}% | {item['predictive_likelihood_ratio_to_constant_true_track']:.3g} |")
    first,last=families[0]["summary"]["pooled_mean"],families[-1]["summary"]["pooled_mean"]
    span=distance((first["latitude"],first["longitude"]),(last["latitude"],last["longitude"]))
    os.replace(csv_temporary,csv_path)
    captions=out/"CAPTIONS.md"; replace_text(captions,
        "# Structural-family figure boundary\n\n"
        "All four primary treatments show model-conditioned location at 00:11 UTC under four mutually exclusive lateral-control interpretations. They use identical SATCOM observations, radar/performance priors, 4 Hz BFO error, ERA5 wind and IGRF-14 declination; antenna and auxiliary likelihoods are disabled. Families are not weighted or pooled. The common one-turn model permits one post-radar switch followed by one fixed control interpretation and excludes later changes, waypoint/LNAV routes, arbitrary heading schedules, fuel and end-of-flight dynamics. Only constant true track passes every declared numerical criterion. These are not seventh-arc or impact PDFs.\n\n"
        "## Primary treatments\n\n"
        "1. **Common-scale panels.** Pooled-within-family 90% and 50% HPD regions at 00:11 UTC, with individual-seed 90% contours and means. Every panel has identical geographic scale.\n"
        "2. **Contour overlay.** The same HPD contours on one map. The extreme conditional means are separated by "
        f"{span:.0f} NM, but this is structural spread between mutually exclusive assumptions, not a confidence interval.\n"
        "3. **Along-arc ridgeline.** Each conditional density projected to distance along the nominal 35,000-ft 00:11 BTO arc. Nearest-point projection is only a display coordinate and retains no cross-arc information.\n"
        "4. **Numerical versus structural.** Individual seed means and seed log-evidence ranges distinguish repeatable locations from normalization instability. Duplicate-collapsed ESS exposes exact-state genealogy that nominal particle ESS masks.\n\n"
        "## Separate corrected-R600 compatibility control\n\n"
        f"The source posteriors were replayed unchanged to {control['selection']['time_utc']} and evaluated with corrected R600 BTO {control['selection']['observed_bto_us']:.0f} ± {control['selection']['standard_deviation_us']:.0f} μs as the only new likelihood. The table reports prior predictive mass before conditioning and likelihood ratios relative to constant true track; these are not posterior model probabilities.\n\n"
        "| Family | 00:11 converged | within ±1σ | within ±2σ | predictive ratio to CTT |\n"
        "|---|---:|---:|---:|---:|\n" + "\n".join(table) + "\n\n"
        f"Under unchanged modes, final R600 therefore largely disconfirms the {span:.0f} NM 00:11 span: constant magnetic track is strongly disfavoured relative to CTT and constant magnetic heading is effectively incompatible. This control remains a forward replay, not an impact PDF; it does not evaluate BFO, fuel, endurance, flameout, descent, or impact displacement.\n"
    )
    return [csv_path,captions]

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--run",type=Path,required=True); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    suite,families,inputs=load_run(args.run); control,compatibility,control_inputs=load_compatibility(args.run); inputs += control_inputs
    lats,lons,along=bto_arc(); tree=project(families,lats,lons,along); outputs=[]
    outputs += common_panels(families,lats,lons,args.output); outputs += overlay(families,lats,lons,args.output); outputs += ridgeline(families,lats,along,args.output); outputs += uncertainty(families,lats,lons,along,tree,args.output)
    outputs += compatibility_panel(families,compatibility,control,args.output); outputs.append(contact_sheet(args.output)); outputs += supporting_files(args.output,families,compatibility,control)
    generator=Path(__file__).resolve(); manifest={"schema_version":1,"generator":str(generator),"generator_sha256":digest(generator),"source_run":str(args.run.resolve()),"source_run_status":suite["status"],"source_epoch_utc":EPOCH,"r600_control_input_set_sha256":control["input_set_sha256"],"arc_altitude_ft":ARC_ALT_FT,"display_bandwidth_nm":BANDWIDTH_NM,"structural_pooling":"none","seed_pooling":"equal weight within family only","scope":[SCOPE,WARNING],"software":{"python":os.sys.version.split()[0],"numpy":np.__version__,"pandas":pd.__version__,"matplotlib":mpl.__version__},"inputs":{str(p.resolve()):digest(p) for p in sorted(set(inputs))},"outputs":{p.name:digest(p) for p in sorted(outputs)},"reproduction_command":f".venv/bin/python {generator.relative_to(Path.cwd())} --run {args.run} --output {args.output}"}
    manifest_path=args.output/"figure_manifest.json"; replace_text(manifest_path,json.dumps(manifest,indent=2,sort_keys=True)+"\n"); print(f"generated {len(outputs)} artifacts and {manifest_path}")

if __name__ == "__main__": main()
