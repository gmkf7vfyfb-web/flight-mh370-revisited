"""Validate the coupling tables for import into hydro_data.sqlite.

Builds an in-memory SQLite database from the db_*.csv files, applies the
pairing rules, creates the per-chain views, and exits non-zero on any failure.
Intended to be called by build_hydro_data_db.py (one writer), not by hand edits.
"""
import sqlite3, sys, pandas as pd, math

FILES = {
 'coupling_evidence': 'db_coupling_evidence.csv',
 'coupling_value': 'db_coupling_value.csv',
 'coupling_family': 'db_coupling_family.csv',
 'family_element_evidence': 'db_family_element_evidence.csv',
 'impact_case': 'db_impact_case.csv',
 'reference_event': 'db_reference_event.csv',
 'received_observation': 'db_received_observation.csv',
 'data_availability_probe': 'db_data_availability_probe.csv',
}
CHAIN_FOR_CLASS = {          # definition class -> allowed propagation chains
 'D1': {'MODULE_KRAKEN_RAM', 'MODULE_KRAKEN_ONLY'},
 'D4': {'MODULE_KRAKEN_RAM', 'MODULE_KRAKEN_ONLY'},
 'D2': {'ARONS_1954'},
 'D3': {'NEAR_FIELD_SOURCE_MODEL', 'MODULE_KRAKEN_RAM'},   # implosion D3 values pair with the deep-source module chain
 'S1': {'SEISMIC_LAND'},
}
STATUS = {'EVIDENCE','EVIDENCE_SUPERSEDED','COMPARISON_SET','EXCLUDED_FROM_CALIBRATION','PROPOSED_STRUCTURE'}
ROLES = {'LIKELIHOOD_RIDGE_POINT','MODEL_ERROR_MEASURE','CONSISTENCY_CHECK','ENVELOPE_AND_SCALING',
         'SEPARATE_SOURCE_PRIOR','CROSS_CHECK','SUPERSEDED','EXCLUDED_FROM_CALIBRATION'}

def main(path='.'):
    con = sqlite3.connect(':memory:')
    for t, f in FILES.items():
        pd.read_csv(f'{path}/{f}').to_sql(t, con, index=False)
    fails = []
    def check(name, ok, detail=''):
        print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -> {detail}'))
        if not ok: fails.append(name)
    cv = pd.read_sql('select * from coupling_value', con)
    ev = pd.read_sql('select * from coupling_evidence', con)
    # 1 mandatory fields
    for col in ['definition_class','propagation_chain_required','status','role','independence_group','evidence_id']:
        bad = cv[cv[col].isna() | (cv[col].astype(str).str.strip()=='')]
        check(f'coupling_value.{col} present', bad.empty, bad.value_id.tolist())
    # 2 class/chain pairing
    bad = cv[[r.propagation_chain_required not in CHAIN_FOR_CLASS.get(r.definition_class,set()) for r in cv.itertuples()]]
    check('definition class paired only with its allowed propagation chain', bad.empty, bad[['value_id','definition_class','propagation_chain_required']].values.tolist())
    # 3 vocabularies; no 'anchor' status anywhere
    check('coupling_value.status in vocabulary', cv.status.isin(STATUS).all(), cv[~cv.status.isin(STATUS)].value_id.tolist())
    check('coupling_value.role in vocabulary', cv.role.isin(ROLES).all(), cv[~cv.role.isin(ROLES)].value_id.tolist())
    check('coupling_evidence.status in vocabulary', ev.status.isin(STATUS).all(), ev[~ev.status.isin(STATUS)].evidence_id.tolist())
    anchor = [t for t in ['coupling_value','coupling_evidence','coupling_family']
              if pd.read_sql(f'select * from {t}', con).astype(str).apply(lambda s: s.str.contains('ANCHOR', case=True)).any().any()]
    check('no table uses an ANCHOR status or role', not anchor, anchor)
    # 4 referential integrity
    bad = cv[~cv.evidence_id.isin(ev.evidence_id)]
    check('every coupling_value links to a coupling_evidence row', bad.empty, bad.value_id.tolist())
    fe = pd.read_sql('select * from family_element_evidence', con)
    fam = pd.read_sql('select * from coupling_family', con)
    bad = fe[~fe.family.isin(set(fam.family_id) | {'PROP'})]
    check('family_element_evidence families exist', bad.empty, bad.family.unique().tolist())
    # 5 numeric sanity
    def ok_range(r):
        vals = [x for x in [r.value_low, r.value, r.value_high] if not (x is None or (isinstance(x,float) and math.isnan(x)))]
        return all(x > 0 for x in vals) and vals == sorted(vals)
    bad = cv[[not ok_range(r) for r in cv.itertuples()]]
    check('values positive and value_low <= value <= value_high', bad.empty, bad.value_id.tolist())
    # 6 independence: all F-35A items in one group
    f35 = cv[cv.event_or_mechanism.str.contains('F-35A', na=False)]
    check('all F-35A values share one independence group (counted once)', f35.independence_group.nunique() == 1, f35.independence_group.unique().tolist())
    # 7 per-chain views; a wrong join must return nothing
    con.executescript("""
     CREATE VIEW v_module_chain AS SELECT * FROM coupling_value
       WHERE propagation_chain_required LIKE 'MODULE_%' AND status = 'EVIDENCE';
     CREATE VIEW v_arons_screen AS SELECT * FROM coupling_value
       WHERE propagation_chain_required = 'ARONS_1954' AND status = 'EVIDENCE';
     CREATE VIEW v_envelope AS SELECT * FROM coupling_value
       WHERE role = 'ENVELOPE_AND_SCALING' AND status = 'EVIDENCE';
     CREATE VIEW v_cross_check AS SELECT * FROM coupling_value WHERE definition_class = 'S1';
    """)
    n = con.execute("select count(*) from v_module_chain where definition_class in ('D2','S1')").fetchone()[0]
    check('module-chain view holds no Arons or seismic values', n == 0, n)
    n = con.execute("select count(*) from v_arons_screen where definition_class != 'D2'").fetchone()[0]
    check('Arons view holds only D2 values', n == 0, n)
    for vname in ['v_module_chain','v_arons_screen','v_envelope','v_cross_check']:
        print(f'  {vname}: {con.execute(f"select count(*) from {vname}").fetchone()[0]} rows')
    print('RESULT:', 'FAIL' if fails else 'PASS', f'({len(fails)} failures)')
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
