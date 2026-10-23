cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - "$H/prepare/digitise_kadri_2019.py" <<'E'
import sys
p=sys.argv[1]; s=open(p).read()
s=s.replace('''"7 Mar (text: 'recorded at 11:57 on March 7th')"''','''"Fig. 1 label '247 recorded @ 23:57 UTC' and text 'March 7th': 11:57 is a 12-hour reading of 23:57 UTC 7 Mar"''')
s=s.replace('''"date not stated in the table; text implies 7 Mar"''','''"Fig. 1 label '170 recorded @ 00:11': 12:11 is a 12-hour reading of 00:11 UTC 8 Mar"''')
s=s.replace('''HA08s_gap="25 minutes''','''time_convention_note="Table 3 and the Fig. 4 panel titles (11.00, 12.00, 1.00, 3.00 UTC) use a 12-hour reading; Fig. 1 labels give 23:57, 00:11, 01:58, 03:47-03:55 UTC",
              HA08s_gap="25 minutes''')
open(p,'w').write(s)
E
python "$H/prepare/digitise_kadri_2019.py" --pdf articles/10.1038_s41598-018-37626-z.pdf >/dev/null && cat "$H/results-data/digitised/kadri-2019/kadri2019_table3_ha08s_signals.csv" | head -3