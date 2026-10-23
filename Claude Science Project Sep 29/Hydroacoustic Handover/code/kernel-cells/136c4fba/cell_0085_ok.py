C=pd.read_csv(O+"candidates.csv")
h=C[C.station=="H08S"]
cyc=[s for s in h.statistic.unique() if s!="D4_envelope_max_pa"]
closed=["E_shot","P_gap"]; shoulder=[s for s in cyc if s not in closed]
print("distinct H08S cycle statistics:",len(cyc),cyc)
print("closed-cycle:",len(closed),"| shot-and-shoulder:",len(shoulder),shoulder)
nc=C[C.computable==False]
print("\ncomputable=False rows:",len(nc))
print(nc.groupby([nc.station,nc.note.str.slice(0,40)]).size().to_string())
print("\nrows per group in caption window:",
      "closed", len(h[(h.option=='caption')&h.statistic.isin(closed)]),
      "| shoulder", len(h[(h.option=='caption')&h.statistic.isin(shoulder)]))
