# Next Method Memo

Current diagnosis:

- `exposure_localization` is the stable diagnostic for completion-certificate risk.
- `low_exposure` alone repairs certificate gaps but can waste budget on visibly irrelevant regions.
- `residual_potential` is the current runtime-computable repair rule for weak evidence conditions.

Observed on two blind tasks:

- policy docset: residual-potential expanded weak source-route conditions and recovered 4 scored true targets, above random mean 2.15
- code repo: residual-potential expanded weak source-route conditions and recovered 9 scored true targets, above random mean 4.35
- external `requests` repo: diagnostic replicated, but high-potential-only tied residual-potential

Interpretation:

The theory should now use a two-stage controller:

1. measure exposure localization;
2. if risk is high, repair the completion evidence condition before stopping;
3. if repair cannot make the certificate defensible, abstain rather than certify completion.

Why this is the right next step:

- It still does not use oracle labels.
- It is more faithful to the geometry story than plain low-exposure bottom-k because it repairs weak evidence conditions only where runtime-visible potential remains.
- It keeps item discovery as an evaluation subclass rather than the method definition.

What remains to verify:

- repeatability across more seeds;
- robustness to different route granularities;
- support expansion and support gap reduction after repair;
- false-stop reduction and abstain calibration;
- whether high-potential-only explains most of the gain in real-code settings.

Honesty boundary:

Residual-potential is mechanism-aligned, but not proven uniquely optimal. If high-potential-only remains tied across external tasks, the paper should keep residual-potential as an exploratory coverage-certificate repair candidate and make exposure localization the main contribution.
