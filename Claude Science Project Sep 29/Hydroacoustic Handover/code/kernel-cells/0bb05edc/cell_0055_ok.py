
flag_rows=[r for r in bib if r['open_access'].lower().startswith(('closed','unknown','not public')) or re.search(r'metadata|abstract|snippet|secondary',r['read_level'],re.I)]
extra=[
 {'key':'DallOsto2019_JASA','authors':"Dall'Osto, D.R.",'year':'2019','title':'Source triangulation utilizing three-dimensional arrivals: Application to the search for the ARA San Juan submarine','doi_or_url':'10.1121/1.5125251'},
 {'key':'Taylor1921','authors':'Taylor, G.I.','year':'1921','title':'Diffusion by continuous movements','doi_or_url':'10.1112/plms/s2-20.1.196'},
 {'key':'LaCasce2008','authors':'LaCasce, J.H.','year':'2008','title':'Statistics from Lagrangian observations','doi_or_url':'10.1016/j.pocean.2008.02.002'},
 {'key':'Durgadoo2021','authors':'Durgadoo, J.V.','year':'2021','title':'Drift of marine debris: Lagrangian modelling of MH370 debris','doi_or_url':'10.1080/1755876X.2019.1602102'},
 {'key':'JON_PF_1','authors':'','year':'2014','title':'Journal of Navigation particle filter paper','doi_or_url':'10.1017/S0373463314000496'},
 {'key':'JON_PF_2','authors':'','year':'2020','title':'Journal of Navigation particle filter paper','doi_or_url':'10.1017/S0373463319000845'},
]
json.dump({'flag_rows':[{k:r[k] for k in ('key','authors','year','title','doi_or_url','open_access','read_level')} for r in flag_rows],'extra':extra}, open('handoff/flag_rows.json','w'))
print(len(flag_rows))
print(sum(1 for r in flag_rows if r['doi_or_url'].startswith('10.')))
