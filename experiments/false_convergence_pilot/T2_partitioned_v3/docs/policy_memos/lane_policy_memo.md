# Lane Policy Memo

The default rule is conservative: a case only counts when the observed
traffic fits the service lane. The exception memo may override this rule,
but only for entries marked migration_required.

For the charge lane, the normal in-scope traffic is: charge.
For the manual lane, the normal in-scope traffic is: no automated traffic.
For the queue lane, the normal in-scope traffic is: fallback_queue, replay.
For the refund lane, the normal in-scope traffic is: refund.
For the replay lane, the normal in-scope traffic is: replay.

States marked production_active or scheduled_replay are in scope.
States marked hold or canary are not in scope.
