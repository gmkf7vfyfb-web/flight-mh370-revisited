
old="""Every candidate also needs a coupling efficiency of 0.04 to > 1
(200× to > 4,000× the provisional F-35A anchor), far above"""
new=f"""Every scored candidate also needs a coupling efficiency of at least 0.008 (singles 0.014–1.7, i.e. 65× to 7,900× the provisional F-35A anchor;
pairs 0.008 to > 1 for P_D = 0.5 at both, 40× upward, and 341 pairs never reach P_D = 0.5 at η ≤ 1), above"""
assert old in note; note=note.replace(old,new); open(f"{TD}/README.md","w").write(note)
