# Coupling tables for hydro_data.sqlite (import package, 25 October 2026)

This package follows the data-inventory thread's proposal (session 9e0bf4fe, 24 Oct 2026). Coupling goes into the existing `hydro_data.sqlite`: the definition class and the required propagation chain are mandatory, views give each chain only its valid values, and the build fails on a wrong pairing. The inventory thread stays the single writer. Import these CSVs with its builder and call `validate_coupling_tables.py` from the build; do not edit the database by hand.

## Change from the proposal, from Pete's statement of 24 Oct 2026

No coupling value is an "anchor" and none awaits a ruling. The F-35A figure 2.26e-3 is one estimate from our model, a point on a ridge over (eta_rad, z_eff, S). It is stored as `EVIDENCE`. The validator rejects any `ANCHOR` status or role. Ranges come from the family structure (`coupling_family`, status `PROPOSED_STRUCTURE`, awaiting Pete's approval of the structure, not of a number).

Registry constants affected (the registry stays the authority; these are proposed status changes for its owner):

| registry constant | present status | proposed status |
|---|---|---|
| eta_F35A_metz (2.26e-3) | PENDING_RULING | EVIDENCE (CV02, a ridge point; not a parameter) |
| eta_brown_arons (2.1e-4) | RETIRED_AS_ANCHOR | EVIDENCE (CV14/CV15, consistency check, same recording as E01) |
| eta_prior_bounds [1e-6, 1e-2] | AGENT_CHOICE_NOT_RULED | superseded by coupling_family (PROPOSED_STRUCTURE) |

## Tables

| table | file | rows | key | content |
|---|---|---|---|---|
| coupling_evidence | db_coupling_evidence.csv | 17 | evidence_id | each source, what it measures, its observation operator, its use, its independence group and status |
| coupling_value | db_coupling_value.csv | 25 | value_id | every numeric coupling-type value: definition_class (D1, D2, D3, D4, S1), numerator, denominator, band, source depth, peak definition, propagation_chain_required, independence group, role, status, registry_id |
| coupling_family | db_coupling_family.csv | 5 | family_id | R1, R2, R3, I, X with the selection rule from end of flight and how each prior is built |
| family_element_evidence | db_family_element_evidence.csv | 18 | (family, element) | which evidence informs each element (eta_rad, z_eff, S, tau, E_t, propagation) of each family, and how strongly |
| impact_case | db_impact_case.csv | 18 | case_id | historical aircraft impacts: regime, energy, data held, raw IMS availability, seismic search, search gaps, role, coupling treatment, Kadri claim |
| reference_event | db_reference_event.csv | 16 | ref_id | non-aircraft reference events (explosions, implosions, airguns, ice, analogs, earthquakes, background) |
| received_observation | db_received_observation.csv | 6 | obs_id | received levels measured from raw records (first: F-35A at H11, 25 Oct 2026) |
| data_availability_probe | db_data_availability_probe.csv | 35 | (case, station) | EarthScope probe results (HTTP 200 / 204) |

## Vocabularies

- definition_class: D1 model-inverted source radiated energy / KE; D2 Arons-equivalent, path-blind; D3 near-field measured; D4 in-band; S1 land-recorded seismic energy / KE.
- propagation_chain_required: MODULE_KRAKEN_RAM, MODULE_KRAKEN_ONLY, ARONS_1954, NEAR_FIELD_SOURCE_MODEL, SEISMIC_LAND.
- Allowed pairs: D1 and D4 with MODULE_*; D2 with ARONS_1954 only; D3 with NEAR_FIELD_SOURCE_MODEL (or MODULE_KRAKEN_RAM for deep implosion sources); S1 with SEISMIC_LAND only.
- role: LIKELIHOOD_RIDGE_POINT, MODEL_ERROR_MEASURE, CONSISTENCY_CHECK, ENVELOPE_AND_SCALING, SEPARATE_SOURCE_PRIOR, CROSS_CHECK, SUPERSEDED, EXCLUDED_FROM_CALIBRATION.
- status: EVIDENCE, EVIDENCE_SUPERSEDED, COMPARISON_SET, EXCLUDED_FROM_CALIBRATION, PROPOSED_STRUCTURE.

## Rules enforced by validate_coupling_tables.py

1. Mandatory fields are present.
2. Each definition class pairs only with its allowed chain.
3. Vocabularies hold; no ANCHOR anywhere.
4. Every value links to an evidence row; families exist.
5. Values are positive and value_low <= value <= value_high.
6. All F-35A values share one independence group, so the event is counted once.
7. The views are v_module_chain (12 rows), v_arons_screen (3), v_envelope (4) and v_cross_check (1). The module-chain view holds no D2 or S1 value.

Negative test run: putting Brown's D2 value on the module chain and giving CV02 an ANCHOR status gives 4 failures and RESULT FAIL.

## Open items for the importer

- Noise tables are not part of this package; they stay with the inventory thread's design.
- The impact-case and reference-event tables may also belong under the existing `event` table. Map them as the builder's schema requires, and keep the case_id and ref_id keys.
- The raw-data probes are single 30-s requests; full-window coverage is not verified except for the F-35A (downloaded 10:50-11:20 UTC, all six elements).
