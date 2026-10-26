"""Builds aadc-2014-access.csv from AADC EDS API responses saved on 2026-10-24 (aadc/ds*.json, aadc/obj*.json).
DOIs are NOT in the EDS JSON; they are parsed from the AADC metadata HTML pages saved the same day:
  aadc/meta.html  <- https://data.aad.gov.au/metadata/records/AAS_4102_longTermAcousticRecordings
  aadc/lib.html   <- https://data.aad.gov.au/metadata/records/AcousticTrends_BlueFinLibrary
Queries used (all anonymous GET):
  https://data.aad.gov.au/eds/api/dataset/<eds_id>                      -> dataset record
  https://data.aad.gov.au/eds/api/dataset/<uuid>/objects?recursive=true&removeBasePath=true -> file listing
  https://data.aad.gov.au/eds/api/dataset/<uuid>/download               -> {'error': {'showEmailForm': True}}
  https://data.aad.gov.au/eds/api/dataset/<uuid>/object?prefix=<name>   -> HTTP 401 (README, LICENSE, .meta, .wav)
"""
import json, re, pandas as pd
def page_doi(fn):
    m = re.search(r'dx\.doi\.org/doi:(10\.26179/[A-Za-z0-9.\-]+)', open(fn).read()); return m.group(1)
DOI_COLL = page_doi("aadc/meta.html"); DOI_LIB = page_doi("aadc/lib.html")
rows = []
sites = {"4501": ("Casey2014", "200", -63.7955, 111.7871, 2700), "4502": ("Kerguelen2014", "201", -62.3801, 81.7968, 2000),
         "5091": ("IWC-SORP annotated library (casey2014, kerguelen2014 folders)", "", None, None, None)}
for eid, (name, dep, la, lo, z) in sites.items():
    d = json.load(open(f"aadc/ds{eid}.json")); o = json.load(open(f"aadc/obj{eid}.json"))
    if eid == "5091":
        for sub, code in [("casey2014", "200"), ("kerguelen2014", "201")]:
            w = [x for x in o if x["name"].startswith(sub) and x["name"].endswith(".wav")]
            near = [x["name"].split("/")[-1] for x in w if re.search(r"2014-03-0[6-9]", x["name"])]
            rows.append(dict(dataset=f"IWC-SORP library {sub}", eds_id=eid, uuid=d["uuid"], doi=DOI_LIB, doi_source="aadc/lib.html (AADC metadata page link), not EDS JSON",
                             n_wav=len(w), wav_size_bytes_typical=w[0]["size"], sample_rate_hz="1000 (inferred from 7.2 MB per 1 h 16-bit file)",
                             duty_cycle="1-h files, about 200 sub-sampled hours per site-year", first_file=min(x["name"].split('/')[-1] for x in w),
                             last_file=max(x["name"].split('/')[-1] for x in w),
                             files_7Mar18_8Mar06="none (nearest: " + ", ".join(near) + ")", total_size_GB=round(sum(x['size'] for x in w)/1e9, 3),
                             lat=None, lon=None, recorder_depth_m=None,
                             calibration="HTI-90-U; library is downsampled; per-file calibration not in listing",
                             anonymous_listing="yes", anonymous_file_download="no (HTTP 401)",
                             access_route="email form at data.aad.gov.au/eds/5091/download (one-time zip link or S3 keys sent by email)",
                             registration_or_request="email-gated request; no account; not submitted on Pete's behalf"))
        continue
    wav = sorted([x for x in o if x["name"].endswith(".wav")], key=lambda x: x["name"])
    want = [x for x in wav if re.match(rf"{dep}_2014-03-0(7_(1[8-9]|2[0-3])|8_0[0-5])-00-00\.wav", x["name"])]
    rows.append(dict(dataset=name, eds_id=eid, uuid=d["uuid"], doi=DOI_COLL + " (collection DOI)", doi_source="aadc/meta.html (AADC metadata page link), not EDS JSON",
                     n_wav=len(wav), wav_size_bytes_typical=int(pd.Series([x['size'] for x in wav]).median()),
                     sample_rate_hz="12000 nominal (metadata record; 86.4 MB per 1 h 16-bit mono file is consistent)",
                     duty_cycle="continuous, 1-h files", first_file=wav[0]["name"], last_file=wav[-1]["name"],
                     files_7Mar18_8Mar06=f"{len(want)} of 12 present: {want[0]['name']} ... {want[-1]['name']}",
                     total_size_GB=round(d["counts"]["byte_count"] / 1e9, 1), lat=la, lon=lo, recorder_depth_m=z,
                     calibration="HTI-90-U nominal -165 dB re 1 V/uPa, preamp +20 dB, AC corner 6.6 Hz (Miller et al. 2018); ADC full-scale volts and per-unit cal not public in readable records (.meta sidecars 401)",
                     anonymous_listing="yes", anonymous_file_download="no (HTTP 401)",
                     access_route=f"email form at data.aad.gov.au/eds/{eid}/download (dataset >4 GB: S3 keys for transfer.data.aad.gov.au or one-time zip link sent by email)",
                     registration_or_request="email-gated request; no account; not submitted on Pete's behalf"))
pd.DataFrame(rows).to_csv("out/aadc-2014-access.csv", index=False)
print(pd.DataFrame(rows)[["dataset", "n_wav", "total_size_GB", "first_file", "last_file", "files_7Mar18_8Mar06"]].to_string())
