# Field note CASE-032

During the weekly payment-ops sweep, reviewers flagged CASE-032 as a
case touching svc-fallback-charge. The note describes refund reversal traffic; the case is still active in the production runbook.
Operators warned that the service name and the flow name should not be treated
as sufficient evidence because several late-cycle exceptions override lane
matching. A margin note cites override XOV-206; the analyst must check the override memo before deciding whether the lane mismatch is real.

The incident note does not name the payment processor. Resolve the service
through the lineage changelog and adapter appendix before counting or excluding
the case.
