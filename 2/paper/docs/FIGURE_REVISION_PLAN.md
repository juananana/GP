# Figure Revision Plan

This plan replaces the current memo-style figures with two top-conference-style
figures. The goal is not to add more figures; the paper should keep a balanced
mix of two figures and three main tables.

## Figure 1: Local Evidence Is Not Completion

### Role

Figure 1 is the first conceptual figure. It should be simple, high-impact, and
readable at column width. It communicates the failure before introducing the full
algorithm.

### Format

Single-column or 1.5-column width. Prefer a clean vector diagram.

### Visual Structure

Use four compact visual states:

```text
Localized source-route exposure
        ->
Local stop signal
        ->
Global completion claim
        ->
False certification risk
```

Then show the controller as a small corrective branch:

```text
Evidence-condition check -> repair/continue/abstain
```

### In-Figure Text

Keep text minimal:

```text
Local exposure
No-new signal
Global claim
Mismatch
Controller
```

Avoid full sentences inside the figure. Put explanation in the caption.

### Visual Motif

Use a small source-route grid:

- highlighted cells = exposed strata;
- empty cells = untested source-route conditions;
- an arrow from highlighted cells to `No-new`;
- a red mismatch marker between `No-new` and `Global completion`.

No decorative badges, large title bars, or poster-like footer slogans.

### Caption Draft

**Figure 1: Certificate mismatch from local stop evidence.** A workflow may
observe no-new findings or agreement under a localized source-route exposure
condition. Such evidence can support local exhaustion, but it does not by itself
certify completion over the intended source-route space. The
evidence-condition controller audits this condition before accepting `SAFE`.

## Figure 2: Evidence-Condition Controller

### Role

Figure 2 is the formal method figure. It should show how the controller turns the
geometry into a decision.

### Format

Two-column width. This is the main method figure.

### Visual Structure

Use a left-to-right pipeline:

```text
Evidence log E_t
    ->
Exposure distribution p_exp over Omega
    ->
Eligibility check
    ->
Repair weak plausible strata
    ->
Decision
```

The decision panel has three outputs:

```text
SAFE
CONTINUE
ABSTAIN
```

Add three small state examples above or below the pipeline:

```text
Localized -> not eligible
Broad + residual evidence -> CONTINUE
Broad + no residual evidence -> SAFE
```

### In-Figure Text

Use only compact labels:

```text
E_t
Omega = S x R
p_exp(t,s)
support, Gini
repair
SAFE / CONTINUE / ABSTAIN
```

Avoid putting Algorithm 1 text inside the figure.

### Caption Draft

**Figure 2: Evidence-condition controller.** The controller maps a runtime
evidence log to an exposure distribution over the intended source-route space.
The support/Gini check is an eligibility test, not a completion proof. If the
condition is localized or weak plausible gaps remain, the controller repairs or
continues. It returns `SAFE` only when the evidence condition is broad and repair
or audit reveals no residual evidence.

## What to Remove From Current Figures

Remove:

- large figure title embedded inside the image;
- bottom slogan ribbon;
- long explanatory text boxes;
- poster-like icons that duplicate the caption;
- too many nested panels.

Keep:

- source-route heatmap motif;
- local evidence to global claim mismatch;
- three controller outcomes;
- broad exposure is eligibility, not proof.

## Style

Use:

- black/gray structure with one accent color for exposure;
- red only for mismatch/false certification;
- green only for `SAFE`;
- blue only for runtime exposure/controller flow;
- consistent sans-serif labels;
- compact captions in the paper.

## Placement

Recommended placement:

- Figure 1 after the Introduction motivation paragraph or at the start of the
  Geometry section.
- Figure 2 after Algorithm 1 or immediately before the controller subsection.

Do not add a third figure unless a final claim-verification pilot is actually
run.
