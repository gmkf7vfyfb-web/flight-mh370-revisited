# FIR intercept experiment

This is a separate early-flight conditional feasibility and optimization study,
not a replacement posterior. The frozen IGOGU and R600-sensitivity measures are
unchanged. `prefix_engine.cpp` reuses the pinned weather, satellite observation,
wind/crab, finite-turn, and public-data aircraft checks from `igogu_followup`.
New code integrates an N571 approach turn that ends on the FIR meridian, then
an exactly southbound ground track and one finite second turn before 19:41.
The nominal unturned IGOGU arrival remains 18:36–18:40; actual IGOGU passage is
not required. Only observations through 19:41 are fitted by this experiment.
Any examples are local numerical fits, without Bayesian/evidence weights.
