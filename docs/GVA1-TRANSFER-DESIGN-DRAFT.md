# GVA-1 transfer study: design brief, not a preregistration

Status: planning only. No transfer simulations, transfer seed draws, sample-size claim or success decision are authorized by this document. This stage must have its own scientific commitment and implementation validation before confirmation collection. The existing 145-root sample belongs only to the repair study.

## Question and scope

Which repairs retain their harm protection and production across declared changes to the decision horizon, physical response and available legal actions? Does the answer persist with a separately implemented optimizer that plans multiple steps? A repair that continues to work is an informative result. Preserve failed and successful challenges; do not choose a setting because it makes a preferred repair win or fail.

## Staged development work

1. Write an explicit transfer-specification table before running development outcomes. Separate longer horizons, physical-parameter changes and catalogue changes; retain a matched original setting to detect implementation drift. Include perturbations in both directions where meaningful. Keep the eight IDs, full-roster accounting and Y<350 harm threshold unless a separately justified protocol explicitly changes them.
2. Implement an independently written multistep planner against the same observation/action interface. Specify what it knows, how it predicts reports and stateful authorization, its rollout depth, candidate generation, noise coupling and budget. The frozen one-step optimizer remains a comparison. Account for every simulated transition and final gate check; do not call different-depth searches equal-cost merely because they expand equal numbers of nodes.
3. Test the implementation on deterministic fixtures and the retained original setting, without using fresh confirmation roots. Check horizon boundaries, delayed physical effects, history after rejected actions, missingness, clipping, cost accounting and planner termination. Publish these fixtures as another bounded independent-review package.
4. Freeze a separate development plan, disjoint namespace and resource cap. Use new development roots for new paired contrast variances. Declare planning alternatives and effect margins before those pilot outcomes; use the pilot for variance and feasibility, not to select favorable means or challenges.
5. Calculate the new sample and freeze the scientific protocol, search implementations, challenge catalogue, seeds and analysis. If the design is infeasible within its resource cap, publish that finding and narrow the scientific question prospectively; do not reuse the GVA-1 N=145 by default.

## Statistical choices to settle before the pilot

- Define the primary unit and pairing: one root supplies all compared repair/optimizer cells within each challenge. Do not treat steps, people or planning rollouts as independent observations.
- Define the primary transfer contrast, such as paired degradation of a repair's harm benefit from the original setting to a declared challenge. Specify the sign, normalization and minimum relevant degradation numerically before the pilot. Do not silently reuse the GVA-1 .05 margin for a different estimand.
- Keep both harm burden and any-harm episode incidence visible. Changing horizon changes the incidence opportunity and the denominator of burden; report both, and decide which has a primary interpretation before outcomes.
- State whether the scientific claim concerns each repair separately, any repair, all challenges, or a single aggregate over challenges. That choice determines the family of bounds and power target. Correlated challenge settings are not independent replications.
- Set production retention margins, treatment of zero variances, exact incidence bounds, missing runs, audit failures and multiplicity prospectively. Do not introduce a success endpoint after finding that a predefined one is uninformative.
- Use the new paired variances and a declared incidence alternative to calculate a resource-bounded N, including conservative variance sensitivity and an explicit dependence strategy. Preserve the full planning grid and rejected designs with their reasons.

## Expected review deliverables

A compact specification table; independently checkable planner fixtures; a development-only variance matrix; a sample-size reconstruction script; and a final protocol with no unresolved parameters. Keep each package versioned. Outside review remains welcome alongside progress, and its absence must remain explicit in reported evidence.
