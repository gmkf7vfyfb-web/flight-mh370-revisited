mkdir -p v6 && python3 - <<'E'
t=open('v5/hydro-fix-proposal.md').read()
t=t.replace('(proposal v5)','(proposal v6)')
old='6. Write one entry in the coordination inbox.'
new=old+'''
7. Kadri crash-panel timing check (`kadri_crash_timing_EXPLORATORY.csv`): set its registry status to "EXPLORATORY – model incomplete". Remove every statement in the notes that says or suggests that Kadri's panel times are wrong. Replace it with: "Our straight-path, single-speed arrival model does not agree with some of Kadri's panel times. The cause is not known. It can be an error in our model or inputs." The known limits of our check are: straight geodesic paths; one water speed; no seismic (T-phase) path from shallow sites; impact times and positions not checked against primary investigation reports; H10S position not from the IMS station list; Transair 810 and Lion Air 904 times assumed from the window centre, not read from a marked box.'''
assert old in t; t=t.replace(old,new,1)
old2='- The amplitude-aware likelihood.'
new2=old2+'\n- A pre-registered crash-panel timing test that removes the limits in Block 3 item 7, before any question goes to Kadri.'
t=t.replace(old2,new2,1)
open('v6/hydro-fix-proposal.md','w').write(t)
print(t.count('EXPLORATORY – model incomplete'), t.count('pre-registered crash-panel'))
E