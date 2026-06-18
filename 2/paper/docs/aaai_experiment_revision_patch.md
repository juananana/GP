# Revision patch for `evidence_condition_geometry_aaai_v2_repro2`

## Author-side diagnosis

The paper is much closer to a complete AAAI-style submission than earlier versions. The experimental story already has the right skeleton: bounded task families, generated plus external repository audits, source-only/source-route/full-controller ablations, repair-target variants, fixed seeds, fixed budgets, and explicit oracle-leakage restrictions. The remaining weakness is not that the experiments are missing entirely; it is that the main paper still asks the reader to trust too much of the experimental closure from the supplement.

The safest revision is to pull a small amount of reproducibility and decision-count evidence into the main paper, rather than adding new unsupported claims. In particular, the main text should explicitly connect each research question to one metric, one comparison, and one figure/table; report denominators or SAFE/CONTINUE/ABSTAIN counts for Figure 4; and state the exact reproducibility package at the end of Section 6 or before the discussion. This will also use the lower half of page 7 more effectively before the references begin.

## Main content changes to make

1. **Section 6 should be reorganized into a closed experimental protocol.** Keep it compact, but make the loop explicit: proposed stop state → runtime-visible exposure and repair → controller decision → oracle-only post-hoc scoring. This directly answers credibility and leakage concerns.

2. **Move one count table from the supplement to the main paper.** Figure 4 currently says that denominators and SAFE/CONTINUE/ABSTAIN counts are in the supplement. For reviewers, this is a weak point. Add a small Table 2 with seeded unsafe-state counts and complete-state counts. Do not invent new numbers; generate it from the existing result files.

3. **Add one reproducibility paragraph with concrete artifacts.** The paper already mentions a three-seed reproduction configuration and full seeded validation configuration. Make this visible: config files, frozen snapshots, seeds, thresholds, and output tables/figures. This should be main-paper text, not only supplement.

4. **Add a short “Reproducibility and validity” paragraph before References.** This fills page 7 and strengthens the paper. It should say what is frozen, what is oracle-visible only after decisions, what is pattern-defined, and what still needs human annotation.

5. **Do not over-expand experiments.** The page budget is tight. The goal is not to add a new benchmark; it is to show a credible closed-loop validation of the proposed certificate semantics.

## Suggested LaTeX patch

### Replace the opening of Section 6 with this more closed-loop version

```latex
\section{Experiments}

The experiments test whether a proposed stop can be accepted as a bounded completion certificate under a declared source-route scope. They are not intended to benchmark the best item-discovery policy. Each run follows the same closed protocol. First, a workflow trajectory produces a proposed stop state using only runtime-visible evidence. Second, the compared decision rule observes the exposure log, applies any allowed repair under the fixed budget, and returns \textsc{Safe}, \textsc{Continue}, or \textsc{Abstain}. Third, the oracle is revealed only for post-hoc scoring. Thus the controller is evaluated on whether it accepts unsafe completion claims, not on whether it has oracle access to the remaining workload.

We organize the evaluation around five questions aligned with the method. Q1 asks whether naive stop signals create false certification. Q2 asks whether source-route geometry detects risks that source-only exposure misses. Q3 asks whether broad eligibility is sufficient for safety. Q4 asks whether the full controller rejects unsafe stops without degenerating into a never-stop rule. Q5 compares residual-potential repair with random and high-potential repair under the same decision rule. Table~\ref{tab:exp_coverage} summarizes the bounded tasks and validation scale.
```

### Replace or tighten the “Seeds, budgets, thresholds, and cost” paragraph

```latex
\paragraph{Seeds, budgets, thresholds, and cost.}
Generated tasks use repair budget 4. The external \texttt{requests} and \texttt{urllib3} audits use 200 seeded validations with repair budgets 4 and 5, respectively. We use $\tau_s=0.75$ and $\tau_g=0.70$ as pre-specified operational test points; they are not tuned against oracle recall. A recall threshold of 0.90 is used only to label false certification after the decision has been made. Repair cost counts additional scanned source lines and extraction events after the proposed stop state is fixed. Seeds, route assignments, repair orders, and challenger states are fixed before oracle scoring.

\paragraph{Reproducibility and leakage control.}
We provide both a lightweight three-seed reproduction configuration and the full seeded validation configuration. The reproduction package specifies the task snapshots, route sets, thresholds, budgets, seeds, repair rule, and oracle-scoring paths in configuration files. Runtime decisions may use only the evidence log, source text, lexical route matches, route identifiers, source size, and non-oracle ledger notes. They may not use oracle totals, undiscovered item counts, post-hoc recall, or scorer-visible target distributions. The released scripts regenerate Table~\ref{tab:exp_coverage}, Figure~\ref{fig:main_results}, Figure~\ref{fig:controller_variants}, and the controller-count table from the same fixed configs.
```

### Add this table after Figure 4 or just before the Discussion

```latex
\begin{table}[t]
\centering
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{lrrrr}
\toprule
Decision rule & Unsafe states & Unsafe SAFE & FCR & Safe coverage \\
\midrule
Naive stop & \input{numbers/naive_unsafe_n} & \input{numbers/naive_unsafe_safe} & \input{numbers/naive_fcr} & \input{numbers/naive_safe_cov} \\
Source-only & \input{numbers/source_only_unsafe_n} & \input{numbers/source_only_unsafe_safe} & \input{numbers/source_only_fcr} & \input{numbers/source_only_safe_cov} \\
Eligibility-only & \input{numbers/elig_unsafe_n} & \input{numbers/elig_unsafe_safe} & \input{numbers/elig_fcr} & \input{numbers/elig_safe_cov} \\
Full controller & \input{numbers/full_unsafe_n} & \input{numbers/full_unsafe_safe} & \input{numbers/full_fcr} & \input{numbers/full_safe_cov} \\
\bottomrule
\end{tabular}
\caption{Seeded controller decision counts. All decision rules are evaluated on the same proposed stop boundaries. Oracle labels are used only to mark states as unsafe or complete after the decision. This table should be generated directly from the released result files.}
\label{tab:controller_counts}
\end{table}
```

If the `numbers/` files are inconvenient, replace the `\input{}` fields with values exported from the current result JSON/CSV. The important point is that denominators must appear in the main paper.

### Replace the current Section 8 with this more useful page-7 version

```latex
\section{Discussion, Limitations, and Conclusion}

The experiments support a bounded certificate claim rather than an open-world guarantee. The controller certifies that a stop claim is compatible with the evidence condition that produced it: exposure must be broad enough for eligibility, and repair must not reveal residual evidence within the allocated budget. It does not certify that the world contains no further facts, that future searches would fail, or that source-route is the only useful abstraction.

\paragraph{What the validation establishes.}
The ablations close the main experimental loop. Homogeneous route reuse produces locally conditioned stop evidence and leads to false certification under naive or source-only decision rules. Source-route exposure detects that risk. Eligibility alone is still insufficient on the \texttt{urllib3} boundary, where broad route-partitioned exposure can pass the gate while residual evidence remains. The full controller therefore uses eligibility as a precondition, not as proof, and reserves \textsc{Safe} for states in which repair is clean.

\paragraph{Reproducibility and auditability.}
The implementation fixes task snapshots, route definitions, seeds, thresholds, repair budgets, and oracle-scoring paths in configuration files. The lightweight three-seed configuration is intended for checking that the pipeline, figures, and tables regenerate correctly; the full seeded configuration is used for the reported validation. Runtime-visible fields are separated from oracle-only fields, and all proposed stop states are fixed before oracle scoring. This separation is central to the paper: otherwise the controller could appear safe by indirectly using the hidden workload it is supposed to audit.

\paragraph{Limitations.}
The external repository oracles are pattern-defined and therefore stronger than generated toy labels but weaker than human-annotated completion-audit benchmarks. Source-route strata are task-designed, and different domains may require different route inventories or eligibility thresholds. Residual-potential repair is a mechanism-aligned probe for weak plausible strata, not an optimal active-search policy. A natural extension is a human-annotated completion-claim audit in which route definitions, residual evidence, and stop decisions are independently reviewed.

Local evidence therefore does not automatically support a scope-wide completion claim. Evidence-condition geometry makes the conditioning of stop evidence explicit, and the controller uses that geometry to reject unsafe local stops, repair weak plausible strata, and abstain when no defensible certificate can be formed. The contribution is a bounded diagnostic and control principle: completion certificates should be judged by the evidence condition that produced them, not by stop signals alone.
```

## Form and layout fixes

- Keep references from starting too early on page 7 by inserting the revised Section 8 above. It adds useful validity and reproducibility content rather than filler.
- Shorten the Figure 4 caption after adding Table 2. The current caption carries too much methodological detail because the count table is absent.
- Rename task labels consistently: use either `policy-docset`, `code-repo`, `requests`, `urllib3`, or short small-caps labels. Avoid mixing `policy`, `code`, and package names without explanation.
- Avoid repeated phrases such as “This is the design point.” Use one synthesis sentence at the end of Results instead.
- Keep all oracle-related language conservative: “pattern-defined oracle,” “post-hoc scoring,” “bounded validation,” not “complete real-world oracle.”
- If space is still tight, reduce Figure 2 height or move Algorithm 1 closer to the text before cutting experimental detail. Do not cut the reproducibility paragraph.

## Prompt for Codex/Claude

```text
Revise the AAAI LaTeX paper for experimental credibility and page usage. Keep claims conservative and do not invent results. In Section 6, rewrite the experiment opening as a closed protocol: fixed stop state -> runtime-visible decision/repair -> oracle-only post-hoc scoring. Add a compact reproducibility/leakage-control paragraph listing configs, seeds, thresholds, budgets, frozen snapshots, and regenerated outputs. Pull the controller decision-count table from the supplement/results into the main paper after Figure 4, using actual result files for denominators and FCR/safe coverage. Replace Section 8 with a fuller Discussion/Limitations/Conclusion covering what validation establishes, reproducibility/auditability, and limitations. Shorten Figure 4 caption, standardize task names, remove repeated “design point” phrasing, and ensure references do not start too early on page 7 while staying within AAAI page limits.
```
