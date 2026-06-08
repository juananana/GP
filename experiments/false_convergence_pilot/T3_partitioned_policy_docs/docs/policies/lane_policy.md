# Lane Policy

A case normally counts only when the case flow is allowed for the service lane.

- lane: charge; allowed_flows: charge
- lane: manual; allowed_flows: none
- lane: queue; allowed_flows: fallback_queue, replay
- lane: refund; allowed_flows: refund
- lane: replay; allowed_flows: replay
