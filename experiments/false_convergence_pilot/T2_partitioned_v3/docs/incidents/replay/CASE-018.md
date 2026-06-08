# Field note CASE-018

During the weekly payment-ops sweep, reviewers flagged CASE-018 as a
case touching svc-manual-adjust. The note describes customer capture and charge traffic; the case is still active in the production runbook.
Operators warned that the service name and the flow name should not be treated
as sufficient evidence because several late-cycle exceptions override lane
matching.

The incident note does not name the payment processor. Resolve the service
through the lineage changelog and adapter appendix before counting or excluding
the case.
