
LOC_TXT={k:v.replace('CL ','Cape Leeuwin ').replace('DG ','Diego Garcia ') for k,v in LOC_TXT.items()}
LOC_TXT['G']='G · Cape Leeuwin 00:52:04 × Diego Garcia 01:12:49\n(this pair), impact 00:31:41'
LOC_OFF3['G']=(30,34)
fig=chart3(); save(fig,'chart3-hpd-maps-pair-g')
