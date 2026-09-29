"""Check exact fine-resolution outputs where matched guides select the same draw."""
import hashlib,json,time
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;B=D.parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(path):
    result={}
    for line in path.open():
        r=json.loads(line);key=(r['source_index'],r['draw'],r.get('family'))
        assert key not in result;result[key]=r
    return result
start=time.monotonic();state=read(D/'progress.json');results=[]
for run in state['runs']:
    fine=B/'terminal-mixed-contact-proposal'/('terminal-seed-'+str(run['seed']))
    coarse=Path(run['source']);fp=fine/'continuations.jsonl';cp=coarse/'continuations.jsonl'
    assert sha(fp)==read(fine/'summary.json')['continuations_sha256']
    assert sha(cp)==read(coarse/'summary.json')['continuations_sha256']
    original=rows(fp);new=rows(cp);assert original.keys()==new.keys()
    matched=0;selected=0;differences=[]
    for key,a in original.items():
        b=new[key];sa=a.get('contact_proposal_selection');sb=b.get('contact_proposal_selection')
        if sa is None or sb is None:assert sa is None and sb is None
        else:
            selected+=1
            assert sb['selected_trajectory_uses_original_integration']
            if sa['selected_index']!=sb['selected_index']:continue
            # The correction changes with the preview proposal even when the
            # same physical candidate is selected. Remove only that known
            # numerical factor before comparing complete fine-resolution rows.
            a['control_log_prior_over_proposal']=sa['coordinate_log_prior_over_proposal']
            b['control_log_prior_over_proposal']=sb['coordinate_log_prior_over_proposal']
            fine_contacts={r['id']:r for r in b.get('contacts',[])}
            for preview in sb.get('selected_preview_contacts') or []:
                if preview['id'] in fine_contacts:
                    full=fine_contacts[preview['id']]['fit_against_0011_bias'];approx=preview['fit_against_0011_bias']
                    differences.append(abs(full['predicted_bfo_without_bias_hz']-approx['predicted_bfo_without_bias_hz']))
        for row in [a,b]:
            row.pop('contact_proposal_selection',None);row.pop('atmosphere_sampling_counts',None)
        assert a==b, 'Selected candidate differs from its previously computed fine-resolution trajectory'
        matched+=1
    assert matched>0
    results.append(dict(seed=run['seed'],fine_source_sha256=sha(fp),coarse_source_sha256=sha(cp),rows=len(original),guided_rows=selected,exact_matched_rows=matched,matched_contact_preview_bfo_absolute_difference_hz=dict(maximum=max(differences,default=0),median=float(np.median(differences)) if differences else 0,p95=float(np.quantile(differences,.95)) if differences else 0)))
result=dict(status='passed',runs=results,elapsed_seconds=time.monotonic()-start,source_code_sha256=sha(Path(__file__)),scope=__doc__.strip())
(D/'matched-preview-verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result))
