# Current task checkpoint — IGOGU conditional inference

Model and observation scope are frozen in model.py and src/engine.cpp. Never weaken them to get survivors. Priors: IGOGU arrival normal 18:38 +/-60s truncated18:36–18:40; immediate finite south turn before first 18:40 burst; 0..4 further turns equal .2; altitude constant / two normal step climbs .5/.5; triangular exhaustion00:15–00:19 mode00:17:30, fuel inverse Jacobian retained. BTO29us and BFO4.3Hz likelihoods at five R1200 epochs + two call means; every BTO±58us/BFO±8.6Hz selection. Known times are evaluated exactly. Legacy additional nominal-centre crossing±60s is diagnostic only (near-tangent imposes ~1us error); user informed, report must disclose and preferably give strict-test sensitivity. C-channel carrier parser corrected.

User's PRIOR EXPLICIT CONSTRAINT confirmed by Personal Context: use00:19 only as fuel-event timing, exclude ALL00:19 BTO/BFO from location likelihood. This scope must remain. Pre-IGOGU segment is conditioned on, not refitted.

NO SUBAGENTS allowed or used. PDF skill marker ALREADY run ONCE this turn. Do not repeat. Library and PDF skills read; final artifacts must be saved with Library helper.

Exploratory SMC run_a/run_b both complete (~30.6million evaluations). They DISAGREE materially and are NOT final evidence. They trained importance proposals. Four adaptive importance training rounds of65,536/cell complete; zero-turn cells stop after one because no survivors. Base proposals at output/proposals_final.

Large importance pilot ensembles (1,048,576/cell, all10cells) STILL RUNNING:
- importance_a session25240 (first1,0 cell completed earlier session65789); log output/importance_a.log; seed970260919; threads4.
- importance_b session89432; log output/importance_b.log; seed1070260919; threads4.
These are now TRAINING because ESS still poor. Each saves cell*.json/.npz, raw exact endpoint importance_measure*.npz and adaptation reservoirs.

A further empirical proposal refinement DRAMATICALLY IMPROVED one-turn constant-alt ESS:1114 from131,072 draws vs120 from1million earlier. Script refine_proposals.py fits24 empirical t-mixture clusters to pooled large-pilot posterior display samples, adds local-sensitivity covariance floors, retains25% previous mixture plus10% full prior. Correct final weights unchanged. It writes output/proposals_refined. Importance density independently checked versus scipy.stats.multivariate_t, max log-density error7.2e-9 (qa/importance_density_validation.json).

Refinement driver session94706: waits for both large pilots' cells, then builds2,0;2,1;3,0;3,1;4,0;4,1;0,0;0,1. Log output/refine_other.log. Refined1,0 and1,1 proposals already built. Zero-support cells retain full-support original proposal.

FRESH FINAL refined samples RUNNING for1,0;1,1 (1,048,576/cell):
- refined_a session97998, seed1270260919, threads2, log output/refined_a.log
- refined_b session28808, seed1370260919, threads2, log output/refined_b.log
After these finish, RESUME SAME output/seed for remaining cells2,0;2,1;3,0;3,1;4,0;4,1;0,0;0,1 with --proposal-dir proposals_refined --wait-for-proposals. Do not accidentally build fallback unrefined proposal if file not ready. Allfinalrawmeasures now include nominal_crossing_error_s for sensitivity checks. Older pilot rawmeasures do not.

Once fresh final all10cells complete, assemble_results.py refined_a refined_b. Assembly already adds exact raw-weight endpoint measure, global ESS, largest weight, perreplicate evidenceSE/quantiles, evidence discrepancy inSE, model-weight differences. Flag provisional ifESS<1000 ormaxweight>1% ordiscrepancy>3SE orturnweightdiff>5pp. Need inspect modelweights/ESS before interpreting as stable. No proof ofremote-mode coverage. Trace/reported displayed resamples are not independent. Need UPDATE exploration evaluation counts to include big importance pilots.

make_report.py authored (not run):9pages currently, exact endpoint density map, assumptions, diagnostics, sampling table,5BTO-epoch maps. 5km equalarea grid with5km Gaussian display kernel. Labels conditional/provisional, notimpact. Need update samplerdescription to include new empirical refinement and final names. Need optionally add legacystrictcrossing diagnostic/sensitivity page using raw final weights. Need render ALL pages and inspect for layout/overlap before saving.

README.md needs update to mention additional large-pilot/refine stage and final refined_a/b (currently describes importance_a/b as final). No targetphysics/prior changes during sampler refinement.

Full reproducibility: inputs weather.bin symlink -> 322MB pinned ERA5 file, must DEREFERENCE in ZIP. Include source, all selected inputs, frozen proposals, finalrawmeasures/posterior, SMC+trainingdiagnostics, reference Python model and validation. Exclude .so, __pycache__, old pilot* with differentpriors, temporarypreviews. New refined_pilot is same target, trainingonly, mayinclude diagnostics.

Finaldeliverables: output/mh370_igogu_conditional_posterior.pdf; fuel-exhaustion PNG;00:11 PNG; summary.json; reproducibleZIP. Save ALL in ONE ordered upload JSONbatch using /root/.codex/plugins/cache/openai-curated-remote/openai-library/0.1.55/skills/library/scripts/library_upload.py. New files: purpose create_library_file; local_path absolute. No LibraryIDs for this task yet. Helper performsprepare/upload/finalize/xattrs. Inspecteveryresult, final sandboxlinks. Do not mention storage internals on success.

Commentary<=60s whileactive. Mostrecentupdate: empirical proposal refinement gives~1100 effective samples from131k instead120from1m; validatingfreshdraws and applyingtootherclasses. Completedone-turncasesnear34S94E, butdo not claimfinalweightssettled.


## Latest live update
Final one-turn cells COMPLETE in refined_a/refined_b (each1,048,576 draws per altitude). They still have heavy-tail importance weights: 1,0 ESS565.6/748.7, logZ−33.116/−33.144;1,1ESS274.1/296.2, logZ−32.482/−32.502. FINAL remaining cells use262,144 proposals each, allocation chosen from pilot evidence, unchanged equal0.1priors and exactN denominators. Remaining refined jobs: session92237 (A) and33242 (B), currently4,1 then0,0;0,1. One-turn original final sessions97998/28808finished. Large pilot importance_a iscomplete;Bfinishingzero-turn cells. Refinement driver94706waitinglastzero-alt metadata. Zero-turncellsstillsupportedfalse. Proposals forotherk aredone.

Material remaining instability: refined_b3,1 hasESS1.015 and99.26%ofthatcell's weightonone draw (endpoint31.55195S95.40031E, logZ−34.377); refined_a3,1 logZ−37.967. The finalPDFMUST BEPROVISIONAL, notconverged, evenifmainmediannear34S94E. User was told complexturnclassesstilllowESS, one/fewtrajectoriesheavyweights, contoursandturnprobabilitiesnotsettled. Stopoptionalnew samplerphasesaftertheauthorizedlarger run; finishhonestreportwithlimitations.

Assembly/PDF backgrounddriver STARTED session46017. It waitsforall20finalcellJSON receipts, then runs assemble_results.py refined_a refined_b, then make_report.py; log output/assembly.log. No needlaunchduplicate. Onceitcompletes, inspectsummary, renderall9PDFpages andvisuallyQA. ReportalreadyaddsPROVISIONALconvergence-failedbannerandannotateslargestindividualweightonfuelmap; finalendpointmapusesexactrawweights. Legacy±60centrecrossingretentionmass/ESS calculatedinassemblerandreportedpage4. Fine-resolutionpassesnowexplicit. CDFreplicadifferencealsopartofsamplingstatus.

READMEupdatedfornewrefinementandNallocation;provisionaldetailsneededfromactualsummary. Addedpackage_results.py buildscompleteZIPincludingdereferencedweather, allpriors,consistenttraining/finals, sourceandchecks. Excludesobsoletepilot*otherpriors, binaries, cachesandTASK_STATUS. Addedverify_importance.py, whichmatchescompletedindependentdensitycheck. AllPythonsourcesastparsed.

Needfinish: summarizeactualcounts/diagnostic failureinPDF/README, renderinspectallpages(fitz/Poppler), adjustlayoutifneeded, runpackage_results.py, save5deliverables(PDF,2PNGs,summaryJSON,ZIP)inoneLibraryuploadbatch. NoartifactssavedtotheLibraryforthistaskyet. PDFartifactmarkerALREADYdoneonce;neverrepeat.
