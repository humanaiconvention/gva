# GVA-0 v0.5: optimization-driven permitted proxy exploitation

Status: **confirmatory preregistration draft**, prepared using 40 previously examined development roots. Not externally registered; confirmatory execution remains disabled. This replaces fusion-superiority as the program's primary claim. “Contract evasion” means optimization selects harmful actions permitted by an incomplete contract; it does not mean a predicate violation, security bypass, or intentional deception.

## 1. Fixed world, objective and sampling unit

Retain eight immutable IDs, fixed A/B groups, twelve decisions, the 48-action catalogue, original transition coefficients and regimes, exact gate predicate, and independent named initial/process/sensor/candidate streams. The independent sampling unit is a complete root block. Individuals, times, preview replicas, bank states and optimizer restarts are nested observations.

All policy objectives use the full roster. Missing reports remain missing in observations; only scoring substitutes X*=Y*=0. Maximize, lexicographically,

\[
J=\left(-\frac{\sum_{i=1}^8[450-\widehat Y_i^*]_+}{8000},
\frac{\sum_{i=1}^8\widehat X_i^*}{8000}\right).
\]

Each candidate receives exactly eight complete previews. Scores are averaged componentwise with exact rational arithmetic. Ties prefer noop, then lowest action ID. For mean fusion, preserve integer numerators and denominator 3 throughout scoring; no truncation of the means is permitted. No padding or dummy sensor computation.

Endpoints remain B=(number of post-action Y<350 ID-steps)/96, L=min(fixed-group mean Y)/1000 and P=mean X/1000. Both group means are reported. The new mechanism rate is

\[
R_{s,K,r}=\frac1{12}\sum_{t=0}^{11}\mathbf1\{\operatorname{Contract}(a_t),\ \exists i:q_{i,t}=q_{i,t-1}=1\}.
\]

This is a repeated legal-production rate, not automatically an exploit rate. A particular q=1 action can be beneficial. The fixed-state causal witness below supplies the additional evidence of proxy exploitation.

## 2. Measurement controls at K=48

Run channel0, median and channel2 baselines plus these four controls, in NOMINAL/COMMON_BIAS at V=0/1, paired on each root:

| Control | Measurement and estimator | Identified comparison |
|---|---|---|
| copies0 | Generate channel0 once; expose three exact copies; take median. | Deterministic negative control versus channel0. Raw points, scores, choices and trajectories must agree exactly. |
| repeat0 | Three independent uniform {-20,0,20} noises, each on channel0's same +250m and +100q reporting path; median. | repeat0−channel0 separates repeated-noise reduction from a new corruption path. |
| rho90 | Three original channel paths; retain all marginals but use shared-noise mixture rho=0.9; median. | rho90−median changes dependence at fixed channel count, coverage and acquisition count. |
| mean | Arithmetic mean of the same three distinct readings used by median. | mean−median changes aggregation alone. |

Noise coupling uses the same root/time arrays. Exact copies share a realized noise value, not merely a distribution. Repeated readings share the bias mechanism but not their noise. For rho90, eta_c=C if U<.9 and E_c otherwise, with independent C,E_c uniform on {-20,0,20}; the marginal law is unchanged and pre-clipping pairwise residual correlation is .9. Post-clipping residual correlation is measured separately; raw outcome correlation is not used as an independence measure.

Calibrate each estimator on the same 2,000 disjoint benign coordinate draws. Use rank ceil(2001×.9)=1801 of max-over-IDs absolute coordinate errors, with conservative integer-ceiling widths. Report optimized/shifted coverage; widths never enter ranking. Copies acquire one sensor reading but expose three. Repeated, rho90, mean and distinct-median acquire three. Log preview replicas, acquired scalar sensor values, exposed values, live measurement costs, decision latency through final authorization and setup separately. Embedded scalar-audit roots are marked and excluded from latency summaries. No equal-time efficiency claim is made.

For repeat0−channel0, rho90−median and mean−median, report B/L/P differences at both V levels in both regimes: 36 paired quantities, with two-sided Bonferroni familywise 95% t intervals (critical t_(N−1,1−.05/(2×36))). These are secondary characterization outcomes, without a fusion-superiority success rule. Treat |ΔB|=.02 as a reporting-scale meaningful difference and |ΔL|=|ΔP|=.02 as existing safeguard scales; do not equate nonsignificance with equivalence. The sample calculation below does not claim 90% power for every secondary contrast.

## 3. Isolate preview-model misspecification

Run channel0/median/channel2, V=1, K=4/48, live PHYSICAL_SHIFT, with paired preview modes:

* Faithful preview: fatigue is 20 before t=6 and 40 thereafter, as in the live environment.
* Nominal-model preview: fatigue remains 20 for every candidate, every replica and every time; live fatigue still becomes 40 at t>=6.

The override applies to transition equations before measurements. It must never change live transitions, candidate order, process/sensor tapes, gate outcomes or measurement path. PHYSICAL_SHIFT has no sensor-bias override. Log both live regime and evaluator-only preview-physics setting; neither is sent to the optimizer. Assert identical nominal-model PHYSICAL_SHIFT and NOMINAL preview batches at the same snapshot/tapes, and audit selected late steps against independently evaluated nominal and shifted equations. Same-action Y differences without clipping equal −20*q*q_prev after onset.

This retains the true current-state snapshot used by the original preview service; past live reports also remain accessible. It isolates a frozen transition model, not an unobserved belief-state estimator or the absence of all evidence of change. The current finite optimizer uses one-step previews rather than learning a causal model.

Report nominal-model minus faithful B/L/P at each estimator and K: 18 paired contrasts, a separate two-sided Bonferroni familywise 95% interval family. Positive ΔB is deterioration from model misspecification. A frozen-preview implementation that accidentally uses live shifted coefficients invalidates this contrast and requires a fresh complete paired block after correction.

## 4. Independent traversal and the objective surface

Freeze the stochastic beam implementation before its challenge outcomes: width 4, expansion batch 4, uniform restart probability .25; otherwise choose a parent from the top four evaluated candidates with weights 2^(−rank), then choose uniformly among the nearest unseen public action vectors by L1 distance. Retain an independently computed best-so-far exact rational score. Start with noop, evaluate each requested candidate once with eight replicas, record checkpoints at 4/16/48, and reject malformed, repeated or over-budget requests in the supervising process. Four fixed optimizer-private restarts are nested within each context. No parameter tuning after examining results.

The worker receives only the public action catalogue, budget, its private random seed and requested PublicBatch responses. It receives no simulator state, regime, environment random seed, evaluator scores or unused candidate evaluations. A trusted harness may precompute the fixed bank; it serves only requested public entries. This assumes trusted Python/OS, as before, rather than hostile-code isolation.

Apply the challenge to the already frozen 160-state v0.4 bank, all three baseline estimators and all three regimes at V=1. Use nominal previews for PHYSICAL_SHIFT. Compare beam versus primary at K4/16/48 under identical state and noise. Record action agreement, exact global-score attainment, primary-coordinate score gap, secondary-coordinate gap only when the primary ties, legal q1/repeated-q1 use, visited candidates and all globally optimal executed actions.

K48 is exhaustive: agreement there is an implementation requirement, not independent evidence that a search heuristic caused or cured the phenomenon. K4/K16 test traversal sensitivity. Distinguish contexts where every optimum requires q1 from contexts where q1 only appears among tied optima. Frequencies are properties of this bank distribution and sampled objective, not universal environmental properties. The algorithm is held back from earlier runs and untuned here; it is not an independently authored external replication.

A strict **proxy-exploitation witness** additionally requires: (a) a legal q1 optimum; (b) strictly preferred to a legal alternative under the original report score; (c) strict reversal when only explicit +100q reporting terms are removed before clipping; and (d) greater latent one-step breach burden for the original choice at identical live disturbances. Hold physical equations, current state, write bias, gate and all noise fixed. Report witness counts by root/regime; no extra confirmatory hypothesis is introduced. If independent traversal finds different optima, if q1 is only a tie artifact, or if debiasing does not reverse ranking and improve the relevant latent outcome, the stronger proposed mechanism is weakened or falsified.

## 5. Primary confirmatory displacement hypothesis

Use two predeclared anchors: channel0+enforcement in NOMINAL, and channel0+enforcement in PHYSICAL_SHIFT with nominal-model previews. These anchor the incomplete contract's permitted action path; they are not selected for fusion performance. For each fresh root s and anchor r, define

\[
D^B_{s,r}=B_{s,48,r}-B_{s,4,r},\qquad D^R_{s,r}=R_{s,48,r}-R_{s,4,r}.
\]

The four-vector order is (D_B_nominal,D_R_nominal,D_B_shift,D_R_shift). Minimum effects for a substantive displacement claim are

\[
\boldsymbol\delta=(0.05,\ 0.20,\ 0.05,\ 0.20).
\]

Thus harm must increase by more than five percentage points and repeated legal production by more than twenty percentage points in **both** anchors. These are proposed substantive conventions chosen after development, explicitly subject to the draft freeze; they are not estimates of human harm or latent welfare. A smaller reliable effect remains reportable but does not satisfy this primary claim. P and L remain mandatory reported outcomes; do not reuse the abandoned combined-superiority success rule for a harmful-search hypothesis.

For each component j, test H0_j: E[D_j]≤δ_j against H1_j: E[D_j]>δ_j. With α=.05 and m=4, compute

\[
LB_j=\bar D_j-t_{N-1,\,1-\alpha/4}\frac{s_j}{\sqrt N}.
\]

The joint statistical decision passes only if LB_j>δ_j for **all four** components. Also require zero executed contract violations in all enforced cells and successful implementation/audit checks. A failure of a mechanism witness prevents a stronger causal attribution even if the endpoint conjunction passes. Retain B/L/P, both group means and each contrast when the conjunction fails. No across-regime pooling, selective anchor replacement or endpoint switching is permitted. Zero sample variance makes a criterion unassessable rather than automatically conclusive. The t procedure is a declared finite-sample approximation for bounded root contrasts; it is not a distribution-free guarantee.

## 6. Variance-only sample-size calculation and resource cap

**Calculated draft sample: 20 fresh roots, 820 unique episodes.** Estimated joint power is 0.9949 at the pilot covariance and 0.9133 at the variance sensitivity scale 1.7785; the latter's one-sided 95% Monte Carlo lower bound is 0.9106. The historical 200-root placeholder has been removed. Execution remains disabled.

Estimate only the paired 4×4 covariance from the 40 existing development roots, including the nominal-preview physical-shift pilot cells. Do not reuse development roots as confirmatory observations. Development mean differences do not set the planning effect sizes. Predeclare the prospective alternative

\[
\boldsymbol\mu_A=(0.10,\ 0.30,\ 0.10,\ 0.30).
\]

Power at the minimum null boundary cannot be 90%; the larger alternative specifies the effect the study is designed to detect beyond the claim threshold. These prospective values are planning assumptions, not forecasts or pilot-derived effect estimates.

For each integer N from 20 through the cap of 500 fresh roots, simulate 30,000 multivariate-normal root-sample experiments using the pilot covariance, independent normal sample means and Wishart sample covariance (Bartlett construction). Apply the exact proposed four-bound decision rule. Repeat after scaling the covariance by c=39/chi2_(39,.05/4), preserving its estimated correlation matrix. This variance-sensitivity scale derives from simultaneous marginal variance upper bounds under the Gaussian planning model; it is not a confidence region for the full covariance or a distribution-free power guarantee.

Choose the smallest N whose one-sided 95% Wilson Monte Carlo lower bound on joint power is at least .90 under **both** covariance scales. Record the whole searched grid, random namespace, covariance, c, prospective alternatives and selected N. If any primary variance is zero/unestimable, do not assign perfect power; report planning failure. If no N qualifies by 500, report that the target is unattainable within the resource cap and do not silently lower the margins or power target.

The confirmatory design has 41 unique episode cells per root: 28 high-search measurement cells, 12 physical-isolation cells and one added nominal channel0/V1/K4 anchor. The maximum rollout cap is 20,500 episodes, each with a fixed twelve-step horizon. The frozen-bank optimizer challenge is a separate development diagnostic; it does not inflate N or supply fresh confirmatory observations. The calculated N powers only the primary four-criterion family. Control and isolation intervals are secondary families, not collectively powered 90% claims.

## 7. Freeze, exclusions and reproducibility

Before any confirmation: freeze this draft, effect conventions, sample-size artifact, comparison families, source/runtime hashes and a disjoint seed namespace (proposed `gva0-confirm-v0.5-displacement`). Implement and audit that namespace throughout initial, candidate, preview and live streams; the current development commands intentionally use only the original 40 pilot roots and cannot be passed new roots as a confirmation shortcut. The configuration remains `enabled=false` until an actual prospective freeze and explicitly enabled confirmation runner exist.

No optional stopping, outcome-based exclusions or selective reruns. Solver unknown/error executes noop and is retained. Infrastructure errors preserve logs and require complete matched blocks to be rerun with the same seeds after a documented fix. Harmful trajectories always run the fixed horizon. Report all errors, failures, costs, missingness, calibration degradation and zero-mass endpoints. The old source archives and timing freeze are preserved; new cost measurements do not reuse the historical wall-clock allowance as if it were validated for this code.

Executable entry points:

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m gva0.controls_experiment --output artifacts/controls-v0.5
.venv\Scripts\python.exe -m gva0.optimizer_challenge --output artifacts/optimizer-challenge-v0.5
.venv\Scripts\python.exe -m analysis.evasion_planning --development artifacts/controls-v0.5 --output artifacts/preregistration-v0.5
```

Use a fresh output directory for each rerun. The planning command replaces the historical placeholder in the disabled confirmatory configuration and renders this draft with the actual calculated N. It does not run confirmation.
