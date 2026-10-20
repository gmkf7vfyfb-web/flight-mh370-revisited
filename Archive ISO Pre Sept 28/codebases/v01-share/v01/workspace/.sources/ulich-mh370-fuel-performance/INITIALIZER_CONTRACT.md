# Fuel initializer contract — blocked for canonical use

The machine-readable interface is [`data/initializer_contract.json`](data/initializer_contract.json). It fixes the initializer at the official final ACARS record: `2014-03-07T17:06:43Z`, ZFW 174,369 kg, total fuel 43,800 kg, pressure altitude 35,004 ft, Mach 0.821, SAT −43.8 °C.

An implementation must receive an ordered, explicitly unit-tagged trajectory and one identified performance-model family. It returns total usable fuel and gross mass at each epoch with model/version/input hashes and convergence diagnostics. Engine-specific flameout additionally requires left/right engine-accessible fuel, unusable fuel, crossfeed state, and their uncertainty model; total ACARS fuel alone cannot supply that state.

Canonical integration is blocked for two concrete reasons:

1. The untuned public proxy over-burns the official calculated Arc‑1 comparison by 4,226.524 kg. Its close total ACARS match is cancellation among interval errors and does not validate level cruise.
2. No independently supported left/right accessible tank/feed allocation has been identified from the total-fuel anchor.

The blocker is resolved only by legally usable, independently validated Trent 892B/B772 cruise performance evidence and, for end-of-flight behavior, a defensible engine-feed split. Arc‑1 or a later event may validate the result but may not tune it. The legacy 18:22 quantity, 0.45 t spread, and back-solved 00:17:30 exhaustion time are prohibited inputs.
