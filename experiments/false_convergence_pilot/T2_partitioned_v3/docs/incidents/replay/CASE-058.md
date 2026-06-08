# Field note CASE-058

During the weekly payment-ops sweep, reviewers flagged CASE-058 as a
case touching svc-orbit-charge. The note describes refund reversal traffic; the case is queued for the scheduled replay window.
Operators warned that the service name and the flow name should not be treated
as sufficient evidence because several late-cycle exceptions override lane
matching. A margin note cites override XOV-102; the analyst must check the override memo before deciding whether the lane mismatch is real.

The incident note does not name the payment processor. Resolve the service
through the lineage changelog and adapter appendix before counting or excluding
the case.
