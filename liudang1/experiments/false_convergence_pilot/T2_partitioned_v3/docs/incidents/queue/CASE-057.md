# Field note CASE-057

During the weekly payment-ops sweep, reviewers flagged CASE-057 as a
case touching svc-ledger-replay. The note describes operator replay traffic; the case is still active in the production runbook.
Operators warned that the service name and the flow name should not be treated
as sufficient evidence because several late-cycle exceptions override lane
matching.

The incident note does not name the payment processor. Resolve the service
through the lineage changelog and adapter appendix before counting or excluding
the case.
