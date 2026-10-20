# Located-passage ledger

| Claim | Retrieved source | Locator | Located passage/value | Status |
|---|---|---|---|---|
| The selected table identifies a B777-200ER with RR Trent 892 engines. | User-supplied `Martin-full-model-BSMv7-9-4.xlsx`, SHA-256 `508d4288…b8220` | `FUELModel!P4` | “These coefficients are for the Boeing 777-200ER with RR Trent 892 powerplants.” | FOUND |
| The selected family is LRC and its total two-engine flow is linear in gross mass. | Same workbook | `FUELModel!P6:P8` | “LONG RANGE CRUISE MODEL”; “dm/dt = A + B*m”; mass in kg and flow in kg/s for two powerplants. | FOUND |
| The four implemented coefficient rows are FL350/370/390/410. | Same workbook | `FUELModel!P12:R15` | Values pinned byte-for-byte in `data/coefficient-pins.json`. | FOUND |
| The occurrence aircraft used Trent 892B engines and official performance work used B777 and Rolls-Royce information. | Malaysian Safety Investigation Report and official Appendix 1.6E, already retrieved and passage-audited by `.sources/ulich-mh370-fuel-performance` | See that package’s `citation-ledger.md`, report pp. 84, 135–136; Appendix p. 5 after Table 3 | Aircraft/engine identity and official calculation basis. | FOUND |
| The Kong cells have kg/h-per-engine units and Trent-892/B772 provenance. | User-supplied `Kong-fuel.csv.xlsx`, SHA-256 `5fee5196…4437` | complete sheet inspection | No unit, aircraft, engine, author, or source field is present. | NOT FOUND — assumption stated; sanity check only |

