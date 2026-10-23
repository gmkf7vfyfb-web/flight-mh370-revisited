md=open('out/README.md').read()
md=md.replace("Objects in the 70-110 km ring started 150-500 km south-west or east of the contact,\n   not on the bearing.",
 "Objects in the 70-110 km ring started mostly 150-650 km from the contact (90 % HPD; mass-weighted median 350 km GlobCurrent, 420 km GLORYS12),\n   to the south-west and south-east, not on the bearing.")
md=md.replace("(the surface varies by < 0.7 log units over 0-150 km)","(the point values change by at most 0.73 log units from the crossing to 150 km inside, §3)")
open('out/README.md','w').write(md); print('150-650' in md, '0.73' in md)
