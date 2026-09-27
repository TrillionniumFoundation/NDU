# R89 submission checklist snapshot (2026-05-27)

## R89 scope

- Preserved the R88 root/ZIP forensic parity gate.
- Added `artifact/ndu_or_release_manifest_parity_ledger.json` and
  `artifact/ndu_or_release_manifest_parity_check.py`.
- The release-manifest parity gate checks current root release files,
  distributable ZIP source entries, ZIP sidecar, package hash ledger rows,
  reviewer handoff index, PASS result JSON files, and R89 local-only boundary
  text.
- This is a local package/evidence release-manifest parity check only; it does
  not rerun full PyTorch/CEM training and provides no external review,
  submission, upload, acceptance, or Strong Accept evidence.

## R89 gates

- Release-manifest parity: PASS after local verification; the detailed count
  and hashes are recorded in
  `artifact/ndu_or_release_manifest_parity_check_results.json` and the R89
  status note.
- Root/ZIP forensic parity, ZIP source/result partition, reviewer handoff
  index, result-freshness gate, external-boundary scan, extracted hash-ledger
  replay, package hash ledger, ZIP-closure audit, reproducibility checker,
  OR-positioning checker, LaTeX build, ZIP integrity, and extracted package gate
  are rerun as local gates.

## R89 remaining risk

- Missing optional packages in the current system interpreter remain explicitly
  recorded for full-regeneration paths; the lightweight package gates are the
  verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal
  action, independent reproduction, upload, acceptance outcome, or Strong
  Accept evidence is evidenced.

# R88 submission checklist snapshot (2026-05-27)

## R88 scope

- Preserved the R87 ZIP source/result partition gate.
- Added `artifact/ndu_or_root_zip_forensic_parity_check.py`.
- The root/ZIP forensic parity gate checks current root files, distributable ZIP entries, ZIP sidecar, package hash ledger rows, referenced PASS result JSON files, and R88 local-only boundary text.
- This is a local package/evidence root/ZIP forensic parity check only; it does not rerun full PyTorch/CEM training and provides no external review, submission, upload, acceptance, or Strong Accept evidence.

## R88 gates

- Root/ZIP forensic parity: PASS after local verification; the detailed count and hashes are recorded in `artifact/ndu_or_root_zip_forensic_parity_check_results.json` and the R88 status note.
- Reviewer handoff index, result-freshness gate, external-boundary scan, extracted hash-ledger replay, package hash ledger, ZIP-closure audit, ZIP source/result partition, reproducibility checker, OR-positioning checker, LaTeX build, ZIP integrity, and extracted package gate are rerun as local gates.

## R88 remaining risk

- Missing optional packages in the current system interpreter remain explicitly recorded for full-regeneration paths; the lightweight package gates are the verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal action, independent reproduction, upload, acceptance outcome, or Strong Accept evidence is evidenced.

# R87 submission checklist snapshot (2026-05-27)

## R87 scope

- Preserved the R86 reviewer handoff index local route.
- Added `artifact/ndu_or_zip_source_result_partition_check.py`.
- The ZIP source/result partition gate checks that source-side audit scripts,
  static handoff ledgers, manuscript files, approved reproducibility evidence,
  and the OR-positioning result are present in `NDU_RL_OR.zip`, while mutable
  local audit result JSON/MD outputs remain root-side only.
- This is a local package/evidence ZIP source/result partition check only; it
  does not rerun full PyTorch/CEM training and provides no external review,
  submission, upload, acceptance, or Strong Accept evidence.

## R87 gates

- ZIP source/result partition: PASS after local verification; the detailed
  count and hashes are recorded in
  `artifact/ndu_or_zip_source_result_partition_check_results.json` and the R87
  status note.
- Reviewer handoff index, result-freshness gate, external-boundary scan,
  extracted hash-ledger replay, package hash ledger, ZIP-closure audit,
  reproducibility checker, OR-positioning checker, LaTeX build, ZIP integrity,
  and extracted package gate are rerun as local gates.

## R87 remaining risk

- Missing optional packages in the current system interpreter remain explicitly
  recorded for full-regeneration paths; the lightweight package gates are the
  verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal
  action, independent reproduction, upload, acceptance outcome, or Strong
  Accept evidence is evidenced.

# R86 submission checklist snapshot (2026-05-27)

## R86 scope

- Preserved the R85 result-freshness local handoff.
- Added `artifact/ndu_or_reviewer_handoff_index.json` and
  `artifact/ndu_or_reviewer_handoff_index_check.py`.
- The reviewer handoff index maps the manuscript/PDF, reproducibility checker,
  OR-positioning checker, ZIP closure, package hash ledger, extracted
  hash-ledger replay, external-boundary scan, result-freshness gate, ZIP
  sidecar, and local status checklist into one local reviewer replay route.
- This is a local package/evidence reviewer handoff index only; it does not
  rerun full PyTorch/CEM training and provides no external review, submission,
  upload, acceptance, or Strong Accept evidence.

## R86 gates

- Reviewer handoff index: PASS after local verification; the detailed count and
  hashes are recorded in
  `artifact/ndu_or_reviewer_handoff_index_check_results.json` and the R86
  status note.
- Result-freshness gate, external-boundary scan, extracted hash-ledger replay,
  package hash ledger, ZIP-closure audit, reproducibility checker,
  OR-positioning checker, LaTeX build, ZIP integrity, and extracted package
  gate are rerun as local gates.

## R86 remaining risk

- Missing optional packages in the current system interpreter remain explicitly
  recorded for full-regeneration paths; the lightweight package gates are the
  verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal
  action, independent reproduction, upload, acceptance outcome, or Strong
  Accept evidence is evidenced.

# R85 submission checklist snapshot (2026-05-27)

## R85 scope

- Preserved the R84 external-boundary scan local handoff.
- Added `artifact/ndu_or_result_freshness_check.py`.
- The result-freshness gate checks that current checker/result hashes,
  `NDU_RL_OR.zip`, `NDU_RL_OR.zip.sha256`, the package hash ledger, extracted
  hash-ledger replay, ZIP closure, external-boundary scan, reproducibility
  result, and OR-positioning result remain mutually current.
- This is a local package/evidence result-freshness gate only; it does not
  rerun full PyTorch/CEM training and provides no external review, submission,
  upload, acceptance, or Strong Accept evidence.

## R85 gates

- Result-freshness gate: PASS after local verification; the detailed count and
  hashes are recorded in
  `artifact/ndu_or_result_freshness_check_results.json` and the R85 status note.
- External-boundary scan, extracted hash-ledger replay, package hash ledger,
  ZIP-closure audit, reproducibility checker, OR-positioning checker, LaTeX
  build, ZIP integrity, and extracted package gate are rerun as local gates.

## R85 remaining risk

- Missing optional packages in the current system interpreter remain explicitly
  recorded for full-regeneration paths; the lightweight package gates are the
  verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal
  action, independent reproduction, upload, acceptance outcome, or Strong
  Accept evidence is evidenced.

# R84 submission checklist snapshot (2026-05-27)

## R84 scope

- Preserved the R83 extracted hash-ledger replay local handoff.
- Added `artifact/ndu_or_external_boundary_scan_check.py`.
- The external-boundary scan checks the manuscript, checklist,
  reproducibility boundary data, packaged audit scripts, and distributable ZIP
  text entries for unnegated claims of upload, external review, submission,
  acceptance, or Strong Accept outcomes.
- The scan also requires explicit local-only boundary wording in the manuscript,
  checklist, and reproducibility boundary artifacts.
- This is a local package/evidence external-boundary scan gate only; it does
  not rerun full PyTorch/CEM training and provides no external review,
  submission, upload, acceptance, or Strong Accept evidence.

## R84 gates

- External-boundary scan: PASS after local verification; the detailed count and
  hashes are recorded in
  `artifact/ndu_or_external_boundary_scan_check_results.json` and the R84
  status note.
- Extracted hash-ledger replay: PASS after local verification.
- Package hash ledger: PASS after local verification, including the new
  external-boundary scan result.
- ZIP-closure audit: PASS after local verification.
- Reproducibility checker, OR-positioning checker, LaTeX build, ZIP integrity,
  and extracted package gates were rerun as local gates.

## R84 remaining risk

- Missing optional packages in the current system interpreter remain explicitly
  recorded for full-regeneration paths; the lightweight package gates are the
  verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal
  action, independent reproduction, upload, acceptance outcome, or Strong
  Accept evidence is evidenced.

# R83 submission checklist snapshot (2026-05-27)

## R83 scope

- Preserved the R82 package hash-ledger local handoff.
- Added `artifact/ndu_or_extracted_hash_ledger_replay_check.py`.
- The extracted hash-ledger replay audit temporarily extracts the current
  `NDU_RL_OR.zip` and checks that the root `NDU_RL_OR.zip.sha256`, root package
  hash ledger, ZIP-closure record, ZIP entries, extracted files, and current
  root files remain synchronized.
- This is a local package/evidence extracted hash-ledger replay gate only; it
  does not rerun full PyTorch/CEM training and provides no external review,
  submission, acceptance, or Strong Accept evidence.

## R83 gates

- Extracted hash-ledger replay: PASS after local verification; the detailed
  count and hashes are recorded in
  `artifact/ndu_or_extracted_hash_ledger_replay_check_results.json` and the
  R83 status note.
- Package hash ledger: PASS after local verification.
- ZIP-closure audit: PASS after local verification.
- Reproducibility checker, OR-positioning checker, LaTeX build, ZIP integrity,
  and extracted package gate were rerun as local gates.

## R83 remaining risk

- Missing optional packages in the current system interpreter remain explicitly
  recorded for full-regeneration paths; the lightweight package gates are the
  verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal
  action, independent reproduction, or acceptance outcome is evidenced.

# R82 submission checklist snapshot (2026-05-26)

## R82 scope

- Preserved the R81 ZIP-closure local handoff.
- Added `NDU_RL_OR.zip.sha256`.
- Added `artifact/ndu_or_package_hash_ledger_check.py`.
- The package hash ledger audit checks the root ZIP sidecar and the current
  hashes for `main.tex`, `main.pdf`, `NDU_RL_OR.zip`, the reproducibility
  manifest/checker result, OR-positioning result, ZIP-closure result, and the
  hash-ledger script itself.
- This is a local package/evidence hash-ledger gate only; it does not rerun
  full PyTorch/CEM training and provides no external review, submission,
  acceptance, or Strong Accept evidence.

## R82 gates

- Package hash ledger: PASS, 7 checks / 0 failures.
- ZIP-closure audit: PASS, 6 checks / 0 failures; 180 file entries.
- Lightweight dependency-closure audit: PASS, 9 scripts / 0 forbidden optional full-regeneration imports.
- Reproducibility environment audit: PASS; lightweight gate PASS, Python 3.12, required stdlib modules and system tools available; optional full-regeneration packages missing in this interpreter are recorded as a boundary.
- Package self-replay certificate: PASS, 7 commands / 6 artifacts.
- Reproducibility checker: PASS, 2988 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 80 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no citation warnings, no LaTeX warnings.
- Zip integrity: PASS, 180 file entries.
- Extracted package gate: PASS; extracted dependency-closure audit, package self-replay, reproducibility checker, OR-positioning checker, LaTeX compile, page-count check, and log scan all pass.

## R82 remaining risk

- Missing optional packages in the current system interpreter remain explicitly recorded for full-regeneration paths; the lightweight package gates are the verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R81 submission checklist snapshot (2026-05-26)

## R81 scope

- Preserved the R80 lightweight dependency-closure local handoff.
- Added `artifact/ndu_or_zip_closure_check.py`.
- The audit checks `NDU_RL_OR.zip` against the current package tree for
  expected source/evidence files, absence of draft/cache/build byproducts, and
  byte-for-byte alignment between ZIP entries and root copies.
- This is a local ZIP-closure/package-boundary gate only; it does not rerun
  full PyTorch/CEM training and does not evidence external review, submission,
  acceptance, or Strong Accept.

## R81 gates

- ZIP-closure audit: PASS, 6 checks / 0 failures.
- Lightweight dependency-closure audit: PASS, 9 scripts / 0 forbidden optional full-regeneration imports.
- Reproducibility environment audit: PASS; lightweight gate PASS, Python 3.12, required stdlib modules and system tools available; optional full-regeneration packages missing in this interpreter are recorded as a boundary.
- Package self-replay certificate: PASS, 7 commands / 6 artifacts.
- Reproducibility checker: PASS, 2988 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 80 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no citation warnings, no LaTeX warnings.
- Zip integrity: PASS, 179 file entries.
- Extracted package gate: PASS; extracted dependency-closure audit, package self-replay, reproducibility checker, OR-positioning checker, LaTeX compile, page-count check, and log scan all pass.

## R81 remaining risk

- Missing optional packages in the current system interpreter remain explicitly recorded for full-regeneration paths; the lightweight package gates are the verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R80 submission checklist snapshot (2026-05-26)

## R80 scope

- Preserved the R79 package self-replay and environment/dependency local handoff.
- Added `reproducibility/scripts/make_lightweight_replay_dependency_closure_audit.py` and `reproducibility/data/lightweight_replay_dependency_closure_audit.csv`.
- Wired the AST import-closure audit into `reproducibility/manifest.json` and `reproducibility/check_ndu_reproducibility.py`.
- The audit proves the lightweight checker, environment audit, package self-replay command, and six finite neural-guard builders import no optional full-regeneration packages (`numpy`, `pandas`, `matplotlib`, `seaborn`, `torch`). It is local provenance only; it does not rerun full PyTorch/CEM training and does not evidence external review/submission/acceptance.

## R80 gates

- Lightweight dependency-closure audit: PASS, 9 scripts / 0 forbidden optional full-regeneration imports.
- Reproducibility environment audit: PASS; lightweight gate PASS, Python 3.12, required stdlib modules and system tools available; optional full-regeneration packages missing in this interpreter are recorded as a boundary.
- Package self-replay certificate: PASS, 7 commands / 6 artifacts.
- Reproducibility checker: PASS, 2988 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 80 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no citation warnings, no LaTeX warnings.
- Zip integrity: PASS, 182 entries.
- Extracted package gate: PASS; extracted dependency-closure audit, package self-replay, reproducibility checker, OR-positioning checker, LaTeX compile, page-count check, and log scan all pass.

## R80 remaining risk

- Missing optional packages in the current system interpreter remain explicitly recorded for full-regeneration paths; the lightweight package gates are the verified target.
- Full PyTorch/CEM regeneration was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R79 submission checklist snapshot (2026-05-26)

## R79 scope

- Preserved the R78 package self-replay certificate and finite compact-domain neural guard chain.
- Added `reproducibility/scripts/make_reproducibility_environment_audit.py` and `reproducibility/data/reproducibility_environment_audit.json`.
- Wired the local environment/dependency audit into `reproducibility/manifest.json` and `reproducibility/check_ndu_reproducibility.py`.
- The audit records Python, required system tools, declared requirement availability, and the boundary between lightweight package gates and optional full regeneration. It is local provenance only; it does not rerun full PyTorch training and does not evidence external review/submission/acceptance.

## R79 gates

- Reproducibility environment audit: PASS; lightweight gate PASS, Python 3.12, required stdlib modules and system tools available; optional full-regeneration packages missing in this interpreter are recorded as a boundary.
- Package self-replay certificate: PASS, 7 commands / 6 recent finite-neural-guard artifacts.
- Reproducibility checker: PASS, 2945 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 80 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no citation warnings, no LaTeX warnings.
- Zip integrity: PASS, 180 entries.
- Extracted package gate: PASS; extracted environment audit, package self-replay, reproducibility checker, OR-positioning checker, LaTeX compile, page-count check, and log scan all pass.

## R79 remaining risk

- Missing optional packages in the current system interpreter remain explicitly recorded for full-regeneration paths; the lightweight package gates are the verified target.
- Full PyTorch retraining was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R78 submission checklist snapshot (2026-05-26)

## R78 scope

- Preserved the R75--R77 compact-domain neural guard chain, bounded-composition envelope, and stress-frontier bottleneck audit.
- Added `reproducibility/scripts/make_package_self_replay_certificate.py` and `reproducibility/data/package_self_replay_certificate.json`.
- Added a package self-replay layer: one deterministic command compiles the checker/builders, regenerates the six recent finite neural guard artifacts in order, and records their row counts and SHA256 hashes in a JSON certificate.
- Updated manuscript, README, manifest, checker, and zip. This is a local package self-replay certificate; it does not rerun full PyTorch training and does not evidence external review/submission/acceptance.

## R78 gates

- Package self-replay certificate: PASS, 7 commands / 6 artifacts.
- Reproducibility checker: PASS, 2931 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 80 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no LaTeX warnings.
- Zip integrity: PASS, 178 entries.
- Extracted package gate: PASS; extracted package self-replay regeneration, reproducibility checker, OR-positioning checker, LaTeX compile, page-count check, and log scan all pass.

## R78 remaining risk

- The largest neural rows are still finite compact-domain validation-cover/frontier diagnostics, not unrestricted global neural-network interval proofs.
- Full PyTorch retraining was not rerun in this local pass.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R77 submission checklist snapshot (2026-05-26)

## R77 scope

- Preserved the R75 bounded-composition compact-domain envelope and the R76 INFORMS one-and-a-half-spacing venue-footprint repair.
- Added `reproducibility/scripts/make_neural_guard_stress_frontier_audit.py` and `reproducibility/data/neural_guard_stress_frontier_audit.csv`.
- Added Corollary `cor:neural_guard_stress_frontier`, which computes bottleneck multipliers for the finite compact-domain neural guard chain rather than adding another copy of the bounded-composition join.
- The new audit identifies the active current-cover constraints: Exp. I is budget-stress limited at `1.06666666667`, inventory is current-cover sensitivity limited at `1.03540322525`; refined-cover sensitivity frontiers are `2.02803898271` and `1.88255131864`.
- Updated manuscript, README, manifest, checker, and zip. This remains a finite compact-domain guard-frontier diagnostic, not an unrestricted analytic global neural-network interval certificate.

## R77 gates

- Stress-frontier regeneration: PASS, 2 rows.
- Reproducibility checker: PASS, 2894 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 80 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no LaTeX warnings.
- Zip integrity: PASS, 172 entries.
- Extracted package gate: PASS; extracted stress-frontier regeneration, reproducibility checker, OR-positioning checker, LaTeX compile, page-count check, and log scan all pass.

## R77 remaining risk

- The largest neural rows now have a bottleneck-frontier diagnostic on top of the R75 bounded-composition envelope, but still not unrestricted global neural-network interval arithmetic over arbitrary states, actions, or weights.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R76 submission checklist snapshot (2026-05-26)

## R76 scope

- Preserved the R75 theorem/audit/reproducibility content and the bounded-composition compact-domain neural envelope certificate.
- Repaired the remaining process-footprint risk by restoring the INFORMS class default review spacing (`\OneAndAHalfSpacedXI`) instead of forcing `\DoubleSpacedXI`.
- This is a formatting/venue-footprint repair only: no theorem, numerical claim, script, CSV, checker condition, or claim boundary was removed.

## R76 gates

- Bounded-composition envelope regeneration: PASS, 2 rows.
- Reproducibility checker: PASS, 2861 checks / 0 failures.
- OR-positioning checker: PASS, 12 checks / 0 failures.
- LaTeX build: PASS, 79 pages; zero overfull hboxes, zero underfull hboxes, no undefined references, no LaTeX warnings.
- Zip integrity: PASS, 170 entries.
- Extracted package gate: PASS; extracted bounded-composition regeneration PASS, reproducibility checker PASS, OR-positioning PASS, LaTeX compile PASS at 79 pages, and extracted log scan has zero overfull hboxes/zero underfull hboxes/no undefined references/no LaTeX warnings.

## R76 remaining risk

- The largest neural rows have a compact-domain bounded-composition envelope over the declared clipped implementation domain, not unrestricted global neural-network interval arithmetic over arbitrary states/actions/weights.
- The package remains local-only; no external review, submission, portal action, independent reproduction, or acceptance outcome is evidenced.

# R75 submission checklist snapshot (2026-05-26)

## R75 scope

- Preserved R66--R74 replay, empirical-envelope, interval-domain, interval-sensitivity, bounded-architecture budget, budget-stress, cross-artifact, refinement/stress, holdout/bootstrap, concordance, and leave-one-out guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_neural_bounded_composition_envelope_certificate.py` and `reproducibility/data/neural_bounded_composition_envelope_certificate.csv`.
- Added Corollary `cor:neural_bounded_composition_envelope`, joining interval, sensitivity, bounded-budget, stress-margin, concordance, and leave-one-out artifacts into a compact-domain bounded-composition envelope over the declared clipped implementation domain.
- Updated manuscript, README, manifest, checker, and zip. This is a compact-domain implementation/envelope certificate, not an unrestricted analytic full-domain neural certificate.

## R75 gates

- Live bounded-composition envelope regeneration: PASS, 2 rows.
- Live reproducibility checker: PASS, 2861 checks / 0 failures.
- Live OR-positioning checker: PASS, 12 checks / 0 failures.
- Live LaTeX build: PASS, 93 pages; zero overfull hboxes, no undefined references, no LaTeX warnings.
- Zip integrity: PASS, 170 entries.
- Extracted package gate: PASS; extracted bounded-composition regeneration PASS, reproducibility checker PASS, OR-positioning PASS, LaTeX compile PASS, and extracted log scan has zero overfull hboxes/no undefined references/no LaTeX warnings.

## R75 remaining risk

- The largest neural rows now have a compact-domain bounded-composition envelope, but not unrestricted global neural-network interval arithmetic over arbitrary states/actions/weights.
- Page length remains a process risk.

# R74 submission checklist snapshot (2026-05-26)

## R74 scope

- Preserved R66--R73 replay, empirical-envelope, interval-domain, interval-sensitivity, bounded-architecture budget, budget-stress, cross-artifact, refinement/stress, holdout/bootstrap, and concordance guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_neural_guard_leave_one_out_robustness_audit.py` and `reproducibility/data/neural_guard_leave_one_out_robustness_audit.csv`.
- Added Corollary `cor:neural_guard_leave_one_out_robustness`, checking six leave-one-guard-family omissions across the two large sampled neural rows.
- Updated manuscript, README, manifest, checker, and zip. This remains a finite validation-cover robustness audit, not an analytic full-domain neural Lipschitz certificate.

## R74 gates

- Live leave-one-out audit regeneration: PASS, 12 rows.
- Live reproducibility checker: PASS, 2809 checks / 0 failures.
- Live OR-positioning checker: PASS, 12 checks / 0 failures.
- Live LaTeX build: PASS, 93 pages; zero overfull hboxes, no undefined references, one nonfatal float-size warning.
- Zip integrity: PASS, 168 entries.
- Extracted package gate: PASS; extracted leave-one-out audit regeneration PASS, reproducibility checker PASS, OR-positioning PASS, LaTeX compile PASS, and extracted log scan has zero overfull hboxes/no undefined references.

## R74 remaining risk

- The largest neural rows are still finite sampled validation-cover guards, not full analytic global neural-domain certificates.
- Page length remains a process risk.

# R73 submission checklist snapshot (2026-05-26)

## R73 scope

- Preserved R66--R72 replay, empirical-envelope, interval-domain, interval-sensitivity, bounded-architecture budget, budget-stress, cross-artifact, refinement/stress, and holdout/bootstrap guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_neural_guard_concordance_audit.py` and `reproducibility/data/neural_guard_concordance_audit.csv`.
- Added Corollary `cor:neural_guard_concordance`, which requires all three holdout/bootstrap schemes to vote in the positive guard direction for each large neural row.
- Updated manuscript, README, manifest, checker, and zip. This remains a finite concordance audit for sampled validation-cover rows, not an analytic full-domain neural Lipschitz certificate.

## R73 gates

- Live reproducibility checker: pending final run.
- OR-positioning checker: pending final run.
- LaTeX build: pending final run.
- Zip integrity and extracted package gate: pending final run.

## R73 remaining risk

- The large neural HBO/NBO rows now have replay, stability, empirical-envelope, interval-domain, interval-sensitivity, bounded-budget, stress-margin, cross-artifact consistency, refinement/stress, holdout/bootstrap, and concordance guards. They still do not have analytic full-domain Lipschitz constants.

# R72 submission checklist snapshot (2026-05-26)

## R72 scope

- Preserved R66--R71 replay, empirical-envelope, interval-domain, interval-sensitivity, bounded-architecture budget, budget-stress, cross-artifact, and refinement/stress guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_neural_guard_holdout_bootstrap_stability_audit.py` and `reproducibility/data/neural_guard_holdout_bootstrap_stability_audit.csv`.
- Added Corollary `cor:neural_guard_holdout_bootstrap_stability`, which checks paired-seed bootstrap, leave-block-out, and tail-stress bootstrap floors after the refinement/stress guard.
- Updated manuscript, README, manifest, checker, and zip. This remains a finite holdout/bootstrap stability audit for sampled validation-cover rows, not an analytic full-domain neural Lipschitz certificate.

## R72 gates

- Live reproducibility checker: pending final run.
- OR-positioning checker: pending final run.
- LaTeX build: pending final run.
- Zip integrity and extracted package gate: pending final run.

## R72 remaining risk

- The large neural HBO/NBO rows now have replay, stability, empirical-envelope, interval-domain, interval-sensitivity, bounded-budget, stress-margin, cross-artifact consistency, refinement/stress, and holdout/bootstrap guards. They still do not have analytic full-domain Lipschitz constants.

# R71 submission checklist snapshot (2026-05-26)

## R71 scope

- Preserved R66--R70 replay, empirical-envelope, interval-domain, interval-sensitivity, bounded-architecture budget, budget-stress, and cross-artifact guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_neural_guard_refinement_stress_audit.py` and `reproducibility/data/neural_guard_refinement_stress_audit.csv`.
- Added Corollary `cor:neural_guard_refinement_stress`, which checks current-cover, half-radius cover-refinement, and refined-cover slope-stress scenarios after the neural guard artifacts have been joined.
- Updated manuscript, README, manifest, checker, and zip. This remains a finite refinement/stress audit for sampled validation-cover rows, not an analytic full-domain neural Lipschitz certificate.

## R71 gates

- Live reproducibility checker: pending final run.
- OR-positioning checker: pending final run.
- LaTeX build: pending final run.
- Zip integrity and extracted package gate: pending final run.

## R71 remaining risk

- The large neural HBO/NBO rows now have replay, stability, empirical-envelope, interval-domain, interval-sensitivity, bounded-budget, stress-margin, cross-artifact consistency, and refinement/stress guards. They still do not have analytic full-domain Lipschitz constants.

# R70 submission checklist snapshot (2026-05-26)

## R70 scope

- Preserved R66--R69 replay, empirical-envelope, interval-domain, interval-sensitivity, bounded-architecture budget, and budget-stress guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_neural_guard_cross_artifact_consistency_audit.py` and `reproducibility/data/neural_guard_cross_artifact_consistency_audit.csv`.
- Added Corollary `cor:neural_guard_cross_artifact_consistency`, which joins validation-cover, replay, empirical-envelope, interval, sensitivity, budget, and stress artifacts by experiment id and preserves the explicit route label `validation-cover_not_global_lipschitz`.
- Updated manuscript, README, manifest, checker, and zip. This remains a finite cross-artifact consistency audit, not an analytic full-domain neural Lipschitz certificate.

## R70 gates

- Live reproducibility checker: pending final run.
- OR-positioning checker: pending final run.
- LaTeX build: pending final run.
- Zip integrity and extracted package gate: pending final run.

## R70 remaining risk

- The large neural HBO/NBO rows now have replay, stability, empirical-envelope, interval-domain, interval-sensitivity, bounded-budget, stress-margin, and cross-artifact consistency guards. They still do not have analytic full-domain Lipschitz constants.

# R69 submission checklist snapshot (2026-05-26)

## R69 scope

- Preserved R66--R68 replay, empirical-envelope, interval-domain, interval-sensitivity, and bounded-architecture budget guards for the large sampled neural rows.
- Added `reproducibility/scripts/make_bounded_architecture_budget_stress_audit.py` and `reproducibility/data/bounded_architecture_budget_stress_audit.csv`.
- Added Corollary `cor:bounded_architecture_budget_stress`, which checks nominal, `1.25x` slope-stress, and `1.50x` radius-stress scenarios for the seven bounded implementation components.
- Updated manuscript, README, manifest, checker, and zip. This remains an implementation stress-margin audit, not an analytic full-domain neural Lipschitz certificate.

## R69 gates

- Live reproducibility checker: PASS, 2534 checks / 0 failures.
- Live OR-positioning checker: PASS, 12 checks / 0 failures.
- Live compile: PASS; final `main.pdf` is 89 pages, and the fatal/undefined/overfull log scan is clean.
- Zip integrity: PASS; `NDU_RL_OR.zip` contains 158 files. The final zip hash is recorded after packaging because the checklist is itself inside the zip.
- Extracted package gate: PASS; extracted bounded-budget stress audit regeneration PASS, bounded-budget audit regeneration PASS, no-torch greedy-gap replay PASS, reproducibility checker PASS, OR-positioning PASS, LaTeX compile PASS, and extracted log scan clean.

## R69 current hashes

- Zip: recorded in the external handoff summary after final packaging.
- PDF: `f723c5cb113677facd4798ac45fbbbf0a505a46197f4bc5c08a7650fecb50915`
- main.tex: `6917b1d779d6470c5ee41fef89528de1f61dca9ebde4b14b1368ebd346b76dc6`
- manifest: `8e26eba09d9c3a110f89e91e5b1fe15460c9cd6b423c6c37fa9c10e8cd5a1f28`
- reproducibility checker: `917455483c777981a9fe8ced193e30b2d3e94ea9f9cdcc3e0b2aac26e0bfeabe`
- reproducibility result: `4db97e0cbda0b5ab8da0cbbfab6b49ae914f8ea933d07f1aafb2cf76df912613`
- budget-stress CSV: `7cd0e0b714375fece3428e45210c95bd949d454809ed0e604c34222708203428`
- budget-stress script: `9fc6f2a7725b19c5173bafb6110e4df802e063516b762d0e155e40508b4f7722`

## R69 remaining risk

- The large neural HBO/NBO rows now have replay, stability, empirical-envelope, interval-domain, interval-sensitivity, bounded-budget, and stress-margin guards. They still do not have analytic full-domain neural Lipschitz constants.

---

# R65 submission checklist snapshot (2026-05-26)

## R65 scope

- Preserved the R64 replay, validation-cover, and empirical-envelope guard repairs for the large sampled neural rows.
- Removed the optional memoryless LQ appendix from the blind PDF because it was explicitly outside the main empirical/theorem claim stack.
- Updated the local OR-positioning sentinel to track the current theorem-scope map through `cor:neural_empirical_envelope_guard` rather than the deleted optional LQ proposition.
- Updated the reproducibility manifest by removing the stale `value-function curvature` manuscript sentinel that only belonged to the deleted optional appendix.

## R65 gates

- Live reproducibility checker: PASS, 2356 checks / 0 failures.
- Live OR-positioning checker: PASS, 12 checks / 0 failures.
- Live compile: PASS; final `main.pdf` is 87 pages, and the fatal/undefined/overfull log scan is clean.
- Zip integrity: PASS; `NDU_RL_OR.zip` contains 155 files and 3,659,956 bytes.
- Extracted package gate: PASS; extracted reproducibility checker PASS, no-torch greedy-gap replay PASS, neural replay certificate regeneration PASS, empirical-envelope audit regeneration PASS, post-regeneration reproducibility checker PASS, extracted LaTeX compile PASS, and extracted log scan clean.

## R65 current hashes

- Zip: `f7c8d47ae2295d4d1cc954bba6e78033b44d0aae43e605374f632d6e62bb30de`
- PDF: `c9eab4b9bcc62295fd4d45daeb8439b35fcc433ca1aa618f476078cdb0f63d74`
- main.tex: `5e02c102bc563296d4725a13dba2daa4f994d3f7587636f0eb8221b32401b0e3`
- manifest: `840e0552346bc74629e1a9e287a23be9de05e6340acbf3334df160aa80c696d2`
- reproducibility checker: `8cc231bbe431141891cfa8f3251d99374e57d07f63a7b208b525d26208731c37`
- reproducibility result: `6412629f51e3ae090c856b4476626e74b3ace50643d4a6f694977587ec4802f7`
- OR-positioning checker: `720da13c05b539375d188aa2330400568f5be80224da223d7d28b55461c715dd`

## R65 remaining risk

- The large neural HBO/NBO rows still do not have analytic full-domain Lipschitz constants. They remain sampled validation-cover evidence, now supported by deterministic replay, stability guards, and empirical-envelope guards.
- The PDF is back to 87 pages, but this was achieved by removing a non-core optional appendix, not by changing the main theorem/evidence claims.

---

# R64 submission checklist snapshot (2026-05-26)

## R64 scope

- Added a no-PyTorch deterministic archived replay mode to `make_hbo_greedy_gap_audit.py`; `--require-torch` preserves the strict retraining path.
- Added `neural_validation_cover_replay_certificate.csv` and its pure-Python builder to hash-anchor the large neural validation-cover rows to packaged residual, greedy-gap, normalized-residual, and stability evidence.
- Added `neural_empirical_envelope_audit.csv` and `make_neural_empirical_envelope_audit.py` to combine replay, stability, density, greedy-tail, held-out, and residual/terminal score guards for the large sampled neural rows.
- Updated manuscript text, README, manifest, and checker sentinels for the replay certificate and empirical-envelope guard without claiming external acceptance or full-domain neural Lipschitz certification.
- The closed-form LQ material remains in Appendix A. Current PDF/page/hash values below should be read after the R64 rebuild gates.

## R64 gates

- Live reproducibility checker: PASS, 2357 checks / 0 failures.
- Live OR-positioning checker: PASS, 12 checks / 0 failures.
- Live compile: PASS; final `main.pdf` is 91 pages, and the fatal/undefined/overfull log scan is clean.
- Zip integrity: PASS; `NDU_RL_OR.zip` contains 155 files and 3,687,471 bytes.
- Extracted package gate: PASS; extracted reproducibility checker PASS, no-torch greedy-gap replay PASS, neural replay certificate regeneration PASS, empirical-envelope audit regeneration PASS, post-regeneration reproducibility checker PASS, extracted LaTeX compile PASS, and extracted log scan clean.

## R64 current hashes

- Zip: `cce22cd3996c15a8603bfb1ab5dfa1cfa1b869fcea57d4f9b2cdfe91055ae321`
- PDF: `d320f8caa6127b28ec6a1710631a2b515196e67f1c53381030ff892e732ee61f`
- main.tex: `28f60d4d381cf731a700e393f9deb9a1494e09408a0fa81be72ca46ff3d99390`
- manifest: `91d10a553d03763a34ba7847a9d6239c6e4ca4511c67008b2b712cd720e2c44a`
- checker: `8cc231bbe431141891cfa8f3251d99374e57d07f63a7b208b525d26208731c37`
- empirical-envelope audit CSV: `07665ac3b4652685322f0a2899798aafcf8e185b1f0cdb5be3681a4ea2e0b706`
- empirical-envelope audit script: `5d6d43767d38dcb18ce88fbb95e2b45a827a15c15c1a608202f0251ef9f8ef6d`

## Superseded R63 hashes

- Zip: `ba0002dfea5d3c6cf70601928e207cddab6e2992928620ac2efe5749ebe9ee7f`
- PDF: `877881eb86099a7a0b8e82ddd4396c9224c01fbefa7d9a01c03cc00fb0c7e4f8`
- main.tex: `6aab09056db55b2ad522105a508b491f82fba48594765ea03a6c542576bf7aa2`
- manifest: `b02333ff96e9158e64c351ea37b5f525844d168a05296097df60f5166e4eb457`
- checker: `023be4028af07e75bc562e67bcf61ba1d676ec94587ad673b2ac2743c743f43e`
- replay certificate CSV: `2569a2843b0320556cada0cb9ec83cd370259dab3a7cfc0b5d2991472efb64a1`

## R64 remaining risk

- The large neural HBO/NBO rows now have deterministic artifact replay, validation-cover guards, and an empirical-envelope guard, but still do not have analytic full-domain Lipschitz constants. They remain sampled validation-cover evidence, not proof-certified global neural certificates.

---

# R58 submission checklist snapshot (2026-05-13)

## Locked identifiers

- Title preserved exactly: `NDU: A Generalization of Fixed-Preference Reinforcement Learning`.
- Template preserved: INFORMS Operations Research style, `\documentclass[opre,blindrev]{informs3}`.
- Current artifacts: `main.pdf`, `NDU_RL_OR.zip`.

## R58 scope

- Continued strong generalized-RL / HJB-solver strengthening without down-toning.
- Added Proposition `Full-support referee synthesis for generalized RL/HJB solver`, label `prop:full_support_referee_synthesis`.
- Added an eight-row referee full-support synthesis audit tying theorem/proof anchors to checked evidence for the main referee objections.
- Expanded certificate ledger to 26 rows with `referee_full_support_generalized_rl_hjb_solver_synthesis`.
- Updated manuscript contribution/scope map/proof/evidence ledger, README, manifest, checker, generalization certificate, and zip.
- Preserved the clean 87-page PDF.

## New R58 evidence

- New script:
  - `reproducibility/scripts/make_referee_full_support_synthesis_audit.py`
- New data:
  - `reproducibility/data/referee_full_support_synthesis_audit.csv`
- Eight-row audit status:
  - `8/8` guards pass with `full_support_synthesis_pass`.
- Key guard rows:
  - policy-class generalized-RL strictness: strict DP `0.19769026726`, exact valuation-MDP `0.015100525896`, non-collapse `5/5`, face hierarchy `5/5`;
  - no state/reward/single-channel relabeling: state/reward guards `5/5`, Full-minus-best-single-channel-face `0.123320778931`, Full-minus-valuation `0.123320778931`;
  - HJB-solver certificate core: strong pillars `6/6`, certificate ladder `7/7`, compact residual `1.56125112838e-16`, uniform bound `0.020190265445`, finite-cover bound `0`;
  - finite-cover refinement not one grid: zero certificate gaps, both faces contained, radius `1.20598507453 -> 0.54626001135`, margins `0 -> 0.111721183652 -> 0.117874280849 -> 0.19769026726`;
  - neural validation-cover route without overclaiming: stability guards `2/2`, max tail `4.09317873455`, max native HJB ratio `0.192341487123`, explicit validation-cover route rather than fake global Lipschitz constants;
  - direct-P shadow-price representation: same-benchmark ratio `19.6443998295`, learned ratio `27.6538247249`, neural ratio `21.3377019006`;
  - same-information empirical support: Exp I `+0.0255447681119`, Exp II parity abs `1.90683339125e-06`, Exp III feasible `+0.0122741423413`, selected Exp III `+0.000228546400698`, source-NBO Exp I `+0.393723037901`, source-NBO inventory `+0.665570306251`;
  - artifact traceability: 25 pre-existing certificate rows plus the new 8-row synthesis audit and registered source audits.

## Retained evidence

- Strict policy-face hierarchy / joint-control necessity retained.
- State-augmentation/reward-shaping equivalence exclusion retained.
- Positive-margin generalized-RL non-collapse retained.
- Strong-form six-pillar generalized-RL/HJB-solver claim closure retained.
- Validation-cover stability guard retained.
- Validation-cover HJB gap certificate and tuple audit retained.
- Referee-objection closure matrix retained.
- NBO HJB-solver certificate ladder retained.
- Cover-refinement HJB certificate sequence retained.
- Exact inventory finite-cover Bellman--HJB certificate retained.
- Same-architecture neural direct-P versus learned-Z retraining ablation retained.
- Analytic uniform residual/terminal/greedy-gap certificate retained.
- Direct-P vs learned-Z isomorphic ridge ablation retained.
- Greedy-gap audit retained.
- Exact-DP, SKU, inventory, HBO/NBO residual closing, normalized residual, selected Exp III, and selected equal-budget inventory evidence retained.

## Gates

- Python compile: PASS for all reproducibility scripts and checker (`draft/LATEST_R58_PY_COMPILE.txt`), 49 files.
- Live reproducibility checker: PASS, 2294 checks / 0 failures (`draft/LATEST_R58_REPRO_CHECK_DRAFT.txt`).
- Extracted reproducibility checker: PASS, 2294 checks / 0 failures (`draft/LATEST_R58_EXTRACTED_REPRO_CHECK.txt`).
- Live compile: PASS; warning/box/fatal scan clean (`draft/LATEST_R58_LATEXMK.log`, `draft/LATEST_R58_LOG_SCAN.txt`).
- Extracted compile: PASS; warning/box/fatal scan clean (`draft/LATEST_R58_EXTRACTED_LATEXMK.log`, `draft/LATEST_R58_EXTRACTED_LOG_SCAN.txt`).
- Zip integrity: PASS (`draft/LATEST_R58_ZIP_INTEGRITY.txt`).
- Trace scan: CLEAN (`draft/LATEST_R58_TRACE_SCAN.txt`).
- PDF info: title preserved, anonymous metadata, 87 pages on letter paper.
- Package: 152 zip entries, 2,110,803 bytes.

## Current hashes

- Zip: `c2a8410abc21198c5dfa2129a8d189acbcd29f9f90fcb585e884441112dcf613`
- PDF: `1064403f440e3912f0acd47925b03259980908033c838427cac7da6c4b164a01`
- main.tex: `16efbd1867e04923ab3509805846bc83ffdd59ce561d6a4a66b4d5345e0b5fe7`
- manifest: `45d18465d3b623dd8e7b515f5ef0900dd311cdb711b23a88baa6b2f204290e22`

## Remaining risk

- Remaining narrow risk: reviewers could still demand analytic full-domain Lipschitz constants for the largest neural rows.
- R58 further reduces presentation/referee risk: all active generalized-RL, anti-relabeling, strict-face, HJB-solver, validation-cover, direct-P, same-information, and traceability evidence is now assembled in one proposition and one checked eight-row synthesis audit.
