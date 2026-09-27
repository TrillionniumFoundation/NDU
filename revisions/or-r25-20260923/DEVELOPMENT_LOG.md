# R25 development and evidence boundaries

The new studies were designed in response to the R24 report. The legacy hierarchy uses the first 24 nominal contexts in the frozen predecessor record, and the radius study uses its first eight. The new Markov family has 24 seeded contexts. No context was removed after a solver difficulty.

Development trials requesting excessively tight OSQP convergence stalled on a degenerate canonical instance. A HiGHS-only proposal route also did not solve every legacy case. The completed route uses exact algebra for the singleton class, OSQP for the two-service legacy model, and CasADi's HiGHS QP interface for the one-service Markov model with an IPOPT exception fallback. Each successful proposal records its actual engine and prior failed attempts. Failed attempts are not counted as certified measurements; every final result must pass rational primal/dual verification. Proposal time is not advertised as a matched performance benchmark.

The fine-radius study was rerun together with the final hierarchy/cache route so the completed execution records correspond to one source version. The existing R24 timing, robust costs, and their raw outputs were not rerun or overwritten as new R25 measurements. Their independent verifier was replayed unchanged.

The first LaTeX pass exposed duplicate bibliography imports in external-label files and a long EC design line. Label copies were restricted to `newlabel` entries, and the long expression was displayed across lines. The final main and companion were recompiled, and representative title, theory, and table pages were rendered and inspected. Exact arithmetic replay is separate from these document checks.

The source does not manufacture acceptance, novelty certification, field calibration, continuous-state approximation guarantees, or a speedup. The next referee can inspect the stated assumptions, proofs, examples, raw brackets, and retained unfavorable evidence directly.
