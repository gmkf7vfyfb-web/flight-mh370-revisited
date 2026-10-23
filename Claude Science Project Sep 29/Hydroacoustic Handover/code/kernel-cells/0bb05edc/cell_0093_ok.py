
old_line=mlines[hit[0]]
new_line=re.sub(r'^[0-9a-f]{64}\s+\d+', lambda mo: newh + str(len(newb)).rjust(11), old_line)
mlines[hit[0]]=new_line
wr(mf,'\n'.join(mlines))
print(old_line[:90]); print(new_line[:90]); print(len(newb))
# copy refreshed results files (identical old blobs on this branch -> new versions from the sep29 commit)
import subprocess
for rel in ['results/hydroacoustics-bibliography.csv','results/hydroacoustics-literature-review.md','results/hydroacoustics-prior-work-critique.md']:
    blob=subprocess.run(['git','-C',ROOT,'show',f'fix-sep29:Claude Science Project Sep 29/{rel}'],capture_output=True).stdout
    open(os.path.join(P,rel),'wb').write(blob)
MP='threads/master-prompts/hydroacoustics.md'
subh(MP,"ask Metz's group for the F-35 paper and waveforms","ask Metz's group for the H11 waveforms (the paper is held, artifact 7e4d336f)")
t=rd(MP); print('San Juan line present on module-branch prompt:', "Kadri 2019;" in t)
print(len(LOGH),'engine/data edits')
