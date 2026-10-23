n2=n2.replace("Sighting: JACC 5-6 Apr 2014 (grade A), position not published.","Sighting on 5 Apr 2014, 03:05-03:25 UTC; source JACC releases of 5-6 Apr 2014 (grade A); position not published.")
n2b=n2b.replace("Sighting: JACC 5-6 Apr 2014 (grade A), direction not published.","Sighting on 5 Apr 2014, 03:05-03:25 UTC; source JACC releases of 5-6 Apr 2014 (grade A); direction not published.")
assert 'releases of 5-6 Apr' in n2 and 'releases of 5-6 Apr' in n2b
fig_forward(exec_title)
fig_backward(OD, lons, lats, 'Objects 70-110 km from the Haixun 01 contact on 5 April started away from the bearing-arc crossing on 8 March (provisional grid)', n1b, n2b)
