# Field note CASE-049

During the weekly payment-ops sweep, reviewers flagged CASE-049 as a
case touching svc-sandbox-pay. The note describes refund reversal traffic; the case is still active in the production runbook.
Operators warned that the service name and the flow name should not be treated
as sufficient evidence because several late-cycle exceptions override lane
matching.

The incident note does not name the payment processor. Resolve the service
through the lineage changelog and adapter appendix before counting or excluding
the case.
