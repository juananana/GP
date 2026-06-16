# Internal Review Note v1

This note is for author-side review, not for direct inclusion in the main paper.
It checks boundary risks and suggests text-level repairs while keeping the claim
frozen:

```text
Local evidence cannot automatically support a global completion claim.
```

## Current Frozen Claim

The strongest defensible claim is:

```text
Source-route evidence-condition geometry diagnoses when a proposed completion
certificate is locally conditioned, and a conservative controller can avoid
accepting such evidence as SAFE.
```

The paper should not claim:

```text
residual-potential is optimal;
source-route Gini is a universal law;
broad exposure proves completion;
the experiments solve total recall or active search.
```

## Boundary With TAR / Total Recall

Likely reviewer attack:

```text
This is just total recall / technology-assisted review with different language.
```

Why the attack is partly fair:

- The scored subclasses report recall.
- False certification is operationalized using recall thresholds where bounded
  oracle totals exist.
- Some tasks look like item discovery.

Text-level repair:

```text
We use item-discovery tasks as scored subclasses because they provide bounded
oracle labels for evaluating false certification. The controller, however, does
not observe recall or oracle totals at runtime. Its decision object is the
evidence condition under which a completion claim was produced: which
source-route strata were exposed, whether weak plausible gaps remain, and whether
repair reveals residual evidence.
```

Where to add:

- End of Introduction.
- First paragraph of Experimental Protocol.
- Related Work subsection on TAR / total recall.

Avoid:

```text
Our method improves total recall.
```

Prefer:

```text
Our method prevents locally conditioned evidence from being accepted as a global
completion certificate in bounded total-recall-like subclasses.
```

## Boundary With Active Search

Likely reviewer attack:

```text
Residual-potential is an active-search heuristic, and the comparisons do not
prove it is better than simpler heuristics.
```

This attack is correct unless the paper is carefully framed.

Text-level repair:

```text
Residual-potential is evaluated as a mechanism-aligned repair instance inside the
controller, not as a standalone active-search method. The experiments ask whether
repair over weak plausible source-route strata can reveal residual evidence after
an unsafe stop. They do not establish residual-potential as an optimal search
policy.
```

Where to add:

- Method subsection "Residual-Potential as a Repair Instance".
- Results subsection "Repair Evidence Is Positive but Bounded".
- Caption of Table 2.

Avoid:

```text
Residual-potential outperforms active-search baselines.
```

Prefer:

```text
Residual-potential provides positive but bounded evidence that the controller's
weak-stratum repair mechanism can expose residual evidence.
```

## Boundary With Multi-Agent Collapse

Likely reviewer attack:

```text
This is another diversity/collapse paper; why not measure trace similarity or
answer similarity?
```

Text-level repair:

```text
The diagnostic is not semantic similarity between agent outputs. It records the
runtime condition under which the outputs were produced. Agents may agree because
the task is complete, or because they repeatedly searched the same
source-route region. Source-route exposure makes that distinction observable.
```

Where to add:

- Related Work subsection on multi-agent collapse.
- Figure 1 text around local agreement.

Avoid:

```text
We solve multi-agent collapse.
```

Prefer:

```text
We diagnose one completion-decision failure mode that can arise from correlated
or localized agent work.
```

## Boundary With Item Discovery Limitations

Likely reviewer attack:

```text
The problem is framed broadly, but the evidence is mostly item-discovery or
pattern-defined audit.
```

This is the most serious scope risk.

Text-level repair:

```text
The experiments instantiate completion certification in bounded audit and
item-discovery subclasses because these settings provide evaluable false-stop
labels. We do not claim that these subclasses exhaust all completion decisions.
They test the paper's mechanism: whether local source-route evidence can be
mistaken for global completion evidence.
```

Where to add:

- End of Introduction.
- Experimental Protocol.
- Limitations.

Avoid:

```text
We solve completion certification for arbitrary agent workflows.
```

Prefer:

```text
We provide evidence for a runtime diagnostic and controller in bounded
completion-audit subclasses, with broader claim-verification settings left for
future validation.
```

## Boundary With Broad Exposure

Likely reviewer attack:

```text
If broad exposure is not sufficient, what exactly is the contribution?
```

Text-level repair:

```text
The contribution is the separation between eligibility and safety. Localized
evidence is not eligible for a global completion certificate. Broad exposure
makes certification eligible, but SAFE additionally requires that repair or audit
find no residual evidence. The `urllib3` result is included precisely to prevent
the overclaim that geometry alone proves completion.
```

Where to add:

- Introduction contribution list.
- Controller section.
- Results discussion of `urllib3`.
- Figure 2 caption.

Avoid:

```text
Broad source-route coverage certifies completion.
```

Prefer:

```text
Broad source-route coverage is a precondition for certification, not a
certificate by itself.
```

## Boundary With Thresholds

Likely reviewer attack:

```text
Support-ratio and Gini thresholds look arbitrary.
```

Text-level repair:

```text
The numeric thresholds are operational test points used to instantiate the
controller in the current experiments. The paper's claim is not that these
thresholds are universal, but that a stop controller must inspect the evidence
condition and distinguish localized evidence from broadly conditioned evidence.
```

Where to add:

- Method or Experimental Protocol.
- Limitations.

Avoid:

```text
Gini below 0.7 guarantees safety.
```

Prefer:

```text
In our implementation, the threshold defines an operational eligibility check;
final SAFE still depends on the absence of residual evidence after repair.
```

## Boundary With Pattern-Defined External Oracles

Likely reviewer attack:

```text
The external validations are not human annotated and may only reproduce the
patterns used to define the oracle.
```

Text-level repair:

```text
The external repository tasks are stronger than generated tasks because they
exercise real source structure and route interactions, but they remain
pattern-defined audits. We therefore treat them as external mechanism validation,
not as a final human-annotated benchmark.
```

Where to add:

- Experimental Protocol task description.
- Limitations.

Avoid:

```text
Real-world validation proves generality.
```

Prefer:

```text
External pattern-defined audits test whether the mechanism survives real
repository structure; human-annotated completion audits remain future work.
```

## Most Likely Reviewer Concerns, Ranked

1. Scope overreach: broad completion-certification framing with item-discovery
   evidence.
2. Method overclaim: residual-potential could be read as the main algorithm
   despite mixed high-potential comparisons.
3. Threshold arbitrariness: support/Gini cutoffs may look tuned.
4. Oracle construction: external tasks are pattern-defined, not human annotated.
5. Strata design: source-route definitions may be task-specific.

## Suggested Main-Paper Patch Sentences

Add to Introduction:

```text
The experiments use bounded audit and item-discovery subclasses because they
provide evaluable false-stop labels. The controller itself does not observe
oracle recall; it uses only the runtime evidence condition and repair outcome.
```

Add to Method:

```text
The threshold values instantiate an operational controller for the current
experiments. They should not be read as universal laws; the invariant is the
controller structure that separates eligibility from SAFE.
```

Add to Results:

```text
The `urllib3` result is the intended boundary case: route-partitioned exposure is
broad enough to make certification plausible, but residual evidence remains, so
the controller returns CONTINUE.
```

Add to Limitations:

```text
The current evidence supports an evidence-condition diagnostic and controller in
bounded completion-audit subclasses. It does not establish a universal
completion certificate for arbitrary agent workflows.
```

## Optional Claim-Verification Pilot Plan

Do not add this pilot to the main experimental claim unless it is actually run.
It can appear as future work.

Pilot objective:

```text
Test whether certificate mismatch appears in claim verification, where the stop
claim is that a natural-language assertion is sufficiently supported and
uncontradicted by a document or repository collection.
```

Suggested strata:

```text
source = document, section, file, or module
route = support search, contradiction search, exception search,
        temporal qualification, scope-boundary audit
```

Controller expectation:

```text
localized support evidence -> not eligible for SAFE
broad support evidence + unresolved contradiction route -> CONTINUE
broad support and contradiction audit + no residual evidence -> SAFE
budget exhausted with unresolved routes -> ABSTAIN
```

Mainline-safe phrasing:

```text
Claim verification is a natural future validation because it removes the
appearance that the framework is only an item-recall diagnostic. We leave it as
future work so that the current paper remains focused on the validated
completion-audit evidence.
```
