# Optimization Pressure and Proxy-Seeking Failure Displacement Under an Incomplete Action Contract

**Public case-study manuscript — 24 September 2026.** Maintained by HumanAI Convention; authorship metadata for journal submission remains pending. This manuscript reports a locally frozen confirmatory experiment; it has not been submitted, externally registered or peer reviewed.

## Abstract

An action contract can correctly restrict behavior while leaving harmful objective-seeking actions admissible. We investigate this distinction in GVA-0, a finite synthetic benchmark with eight persistent individuals, twelve decisions, a 48-action catalogue and an outcome-reporting path with action-dependent bias. We compare search budgets K=4 and K=48 under an unchanged enforced contract, using eight one-step previews per candidate and complete-roster scoring. After development on forty roots, we froze the protocol, executable source, runtime and a disjoint twenty-root seed manifest before generating confirmation outcomes. The preregistered conjunction requires harm-burden increases greater than .05 and repeated legal-production increases greater than .20 in both nominal and physical-shift conditions. The conjunction passed. Mean harm increased by 11.82 percentage points nominally and 19.38 points under shift, with simultaneous lower bounds 10.14 and 18.38 points. Repeated legal-production differences were 0.8792 and 0.8792, with lower bounds 0.8517 and 0.8517. Independent scalar checks verified 9,840 live transitions and 478,080 candidate previews; 0 contract violations occurred in enforced cells. Developmental fixed-state bias interventions and a separately implemented stochastic optimizer provide ancillary evidence that the harmful legal action path reflects the sampled objective surface rather than the primary traversal alone. The findings concern optimization-induced failure under an incomplete specification in this benchmark, without claims about intention, general alignment or learned-agent behavior.

## 1. Introduction

The behavior guaranteed by an action contract and the consequences preferred by an outcome objective are different objects. A checker can correctly enforce its predicate even when the predicate leaves actions that undermine the intended outcome. Increasing optimization pressure can make those permitted actions easier to discover and more frequently selected. A useful empirical question is therefore whether additional search moves failure into an admissible action path, and whether that movement can be verified against the actual execution semantics.

Reward hacking and distributional shift are established AI safety problems rather than new phenomena introduced by this benchmark [1]. Work on reward-model overoptimization measures how stronger optimization of a proxy can reduce performance against a separate reference [2]. Causal analyses of reward tampering distinguish modification of a reward function from modification of inputs to that function [3]. GVA-0 makes a narrower contribution: a small, inspectable experiment separating a finite action contract, a biased operational score, controlled search pressure and latent synthetic outcomes.

Our confirmatory question is: **does increasing search from K4 to K48 increase both latent threshold-breach burden and repeated legal q1 actions under the same incomplete contract?** We test two prespecified anchors, nominal dynamics and shifted live dynamics with a nominal preview model. We use the term *failure displacement* for increased harmful activity on this legal path. The confirmatory contrast does not, by itself, identify the causal effect of turning enforcement on; nor does it imply that enforcement worsens outcomes relative to unrestricted action.

## 2. Methods

### 2.1 Environment and action contract

Eight immutable IDs belong to two fixed groups of four. Every episode runs twelve decisions, without early termination after harm. Initial X/Y coordinates are independent integer draws on fixed group-specific intervals: group A starts at X in [500,650], Y in [550,700]; group B at X in [350,500], Y in [450,600]. X and Y are neutral synthetic variables, not measurements of human welfare.

The catalogue contains 48 actions: combinations of group-targeted production q in {0,1,2}, support u in {0,1}, report-writing m in {0,1}, and exclusion e in {0,1}, together with noop and an all-group support action. After process noise, the coordinate equations are clipped to [0,1000]:

\[
X_{i,t+1}=\operatorname{clip}(X_{i,t}+60q_{i,t}+30u_{i,t}-10+\epsilon^X_{i,t}),
\]
\[
Y_{i,t+1}=\operatorname{clip}(Y_{i,t}+40u_{i,t}-40q_{i,t}^{2}
-f_tq_{i,t}q_{i,t-1}-15m_{i,t}-20e_{i,t}+\epsilon^Y_{i,t}).
\]

Process noise takes values −5, 0 and 5 with probabilities .25, .50 and .25. Fatigue f_t is 20 in nominal conditions; in PHYSICAL_SHIFT it becomes 40 at t>=6. Candidate previews in the shifted primary anchor continue to use f_t=20, while actual execution uses the shifted value. Previews begin from the true current simulator snapshot. This intervention tests a misspecified one-step transition model, not a learned state estimator or complete lack of feedback about past changes.

The enforced predicate requires q_i<=1, total support sum_i u_i<=4, m_i=0 and e_i=0, in addition to the fixed administrative and schema conditions. It contains no lower bound on Y. Rejected or unchecked proposals map to noop. A symbolic checker runs on parsed catalogue actions; an independent scalar predicate audits actual execution. Python, the operating system and fixed actor code are trusted. The process boundary is not an adversarial operating-system sandbox, and no proof about arbitrary code is claimed.

### 2.2 Operational score and optimization pressure

The primary estimator is channel0. Its reports contain +250m on both coordinates and +100q on Y, plus independent uniform sensor noise in {−20,0,20}, followed by clipping. Exclusion marks both reported coordinates missing. The policy maximizes the lexicographic score

\[
J=\left(-\frac1{8000}\sum_{i=1}^{8}[450-\widehat Y_i^*]_+,
\quad\frac1{8000}\sum_{i=1}^{8}\widehat X_i^*\right).
\]

Only objective evaluation replaces an omitted report by X*=Y*=0. Original missingness and report values remain in observations and measurement records. This removes the direct advantage of dropping a low report from the denominator.

Each candidate receives eight complete preview replicas; component scores are averaged using exact rational arithmetic. No partially evaluated candidate competes. Candidate order is a root/time-seeded permutation, nested across K, with noop always included. Ties prefer noop, then the lowest action ID. K4 and K48 therefore differ in search opportunities under matched initial states and disturbances. K48 exhausts the finite catalogue. Both previews and final execution use the applicable gate.

The production actor receives public observations and requested preview batches, without root seeds, regime labels, simulator objects or evaluator-only outcomes. The current finite actor ranks one-step previews; it does not learn a policy or update a causal model.

### 2.3 Fusion architecture as a methodological negative control

Fusion is retained only in the control methodology, with no architectural-superiority hypothesis. At K48, seven measurement conditions—channel0, channel2, distinct-channel median, exact channel0 copies, independent repeated channel0 readings, high-correlation distinct readings and arithmetic mean—are crossed with enforcement on/off and nominal/common-bias regimes. Exact copies form the strict deterministic negative control for channel multiplicity. The other estimators and aggregation interventions test alternative explanations; they are not assumed to be null interventions.

Channel1 shares the report-writing path with channel0; channel2 does not. COMMON_BIAS adds the q-dependent Y reporting bias to channels1/2 from t=6. Independent repeated readings reproduce channel0's bias with independent noise. The high-correlation condition uses a .9 shared-noise mixture at fixed channel count and unchanged marginal noise laws. Arithmetic mean preserves exact fractional scores. Calibration uses the same frozen 2,000 benign states for every estimator; interval widths do not enter action ranking.

Thirty-six paired B/L/P control contrasts form one secondary interval family. Eighteen nominal-preview versus faithful-preview contrasts across three estimators and two K values form another. Both use separate two-sided Bonferroni-adjusted 95% paired-t intervals. These families are fully reported in the supplement, including unfavorable and zero-mass results; they are not collectively powered at 90%. No environmental parameter was changed to favor fusion.

### 2.4 Endpoints, sampling unit and confirmatory rule

The independent sampling unit is a complete root block. Individuals, decisions, preview replicas and optimizer restarts are nested observations. The primary harm endpoint is

\[
B_{s,K,r}=\frac1{96}\sum_{t=1}^{12}\sum_{i=1}^{8}\mathbf1\{Y_{i,t}<350\}.
\]

The mechanism-rate endpoint is

\[
R_{s,K,r}=\frac1{12}\sum_{t=0}^{11}\mathbf1\{\operatorname{Contract}(a_t),
\ \exists i:q_{i,t}=q_{i,t-1}=1\}.
\]

R measures repeated legal production, not automatically exploitation. The mechanism intervention below supplies additional evidence. Safeguards are L, the smaller fixed-group time-averaged Y divided by 1000, and P, the time/roster mean X divided by 1000. Both group outcomes are reported.

For each of the two anchors, D_B=B48−B4 and D_R=R48−R4. The vector order is nominal D_B, nominal D_R, shifted D_B, shifted D_R. Minimum effects were fixed at (.05,.20,.05,.20). For each component j, the null is E[D_j]<=delta_j. At N=20, the simultaneous one-sided lower bound is

\[
LB_j=\bar D_j-t_{19,.9875}s_j/\sqrt{20}.
\]

The joint result passes only if every LB_j>delta_j, zero executed contract violations occur in all enforced cells, and implementation audits pass. Zero sample variance makes a primary criterion unassessable. The finite-sample t approximation is declared; it is not a distribution-free guarantee for bounded outcomes. Failure of the conjunction does not suppress individual contrasts or safeguards.

### 2.5 Sample planning, cryptographic freeze and blind execution

Forty development roots were excluded from confirmation. The planning algorithm used only their paired four-dimensional covariance, not their observed effect means. The prospective alternative was (.10,.30,.10,.30). It simulated 30,000 studies per sample size/covariance scenario, including simulated sample variance, over integers N=20..500. A sensitivity scenario multiplied covariance by 1.778459 while retaining estimated correlations. The smallest allowed N whose one-sided 95% Monte Carlo lower power bound exceeded .90 in both scenarios was 20, giving 820 episodes across 41 unique cells per root. Inflated-covariance modeled joint power was .9133, with Monte Carlo lower bound .91059. This is conditional power under the stated effect and Gaussian covariance assumptions; N was not recalculated after confirmation.

The original populated preregistration was retained byte-for-byte. An execution addendum recorded the user's subsequent authorization and necessary namespace/runner plumbing without changing scientific definitions. The starting source and tested execution source were both archived. The execution freeze committed the protocol, source, runtime, calibration, seeds and preflight record using SHA-256 before any fresh outcomes. Root IDs 1000001..1000020 use namespace `gva0-confirm-v0.5-displacement`; root IDs, canonical key domains and all 1,220 derived 128-bit generator seeds were explicitly checked for nonintersection with development and calibration seeds. This guarantees the checked seed sets are disjoint; coincident random output values remain possible.

During execution, only completion counts were exposed. No interim outcome summaries, sample-size changes, selective exclusions or outcome-based reruns were permitted. The actor interface remained blind to evaluator-only information. This was a locally committed automated no-interim-look design, not an externally registered or independently staffed double-blind trial.

### 2.6 Ancillary mechanistic challenge

Before confirmation, an untuned stochastic beam optimizer was applied to the independently frozen 160-state development bank. It received the same public catalogue and requested eight-replica batches, with width four, expansion four and uniform restart probability .25. Four private restarts were nested within each context. Exact enumeration identified whether every optimum required legal q1 or whether q1 appeared only through ties. K48 agreement is an implementation requirement because both optimizers exhaust the catalogue; K4/K16 probe traversal sensitivity.

A strict proxy-seeking witness required an original legal q1 choice, strict score preference over a legal alternative, strict ranking reversal when only explicit +100q reporting terms were removed before clipping, and lower latent one-step breach burden for the debiased choice at identical live disturbances. These interventions retain the state, physical equations, other report terms and noise. They are development diagnostics and contribute no observations to the confirmatory statistical test.

## 3. Results

### 3.1 Prespecified joint result

**The frozen confirmatory conjunction passed.** All twenty root blocks completed before analysis; no development root entered the primary sample.

| Criterion | Mean paired difference | Simultaneous lower bound | Minimum effect | Pass |
|---|---|---|---|---|
| Nominal D_B | 0.118229 | 0.101448 | 0.05 | True |
| Nominal D_R | 0.879167 | 0.851742 | 0.20 | True |
| Shifted D_B | 0.193750 | 0.183779 | 0.05 | True |
| Shifted D_R | 0.879167 | 0.851742 | 0.20 | True |

All reported lower bounds use the four-comparison simultaneous one-sided rule. They are not ordinary unadjusted two-sided intervals.

| Anchor | K | Mean B | Mean R | Mean L | Mean P | Breached ID-steps |
|---|---|---|---|---|---|---|
| Nominal | 4 | 0.000000 | 0.037500 | 0.513479 | 0.517724 | 0/1920 |
| Nominal | 48 | 0.118229 | 0.916667 | 0.413758 | 0.682159 | 227/1920 |
| Shifted / nominal preview | 4 | 0.001042 | 0.037500 | 0.512313 | 0.517724 | 2/1920 |
| Shifted / nominal preview | 48 | 0.194792 | 0.916667 | 0.378758 | 0.682159 | 374/1920 |

L and P are retained as outcomes, rather than discarded because the study targets harm. Higher search changed mean L by -0.099721 nominally and -0.133554 under shift, while mean P changed by 0.164434 and 0.164434. Thus increased synthetic production co-occurred with deterioration in the lower-group outcome. Mean L averages each root's smaller group mean; it is not the minimum after pooling roots.

### 3.2 Execution validity and action mechanism

The run recorded 0 executed violations across all enforced cells. All 9,840 live transitions and reports matched scalar equations; 478,080 candidate-replica evaluations on the three predeclared audit roots matched independent scores. Every live disturbance matched the confirmation namespace, both log chains verified, eighty exact-copy trajectories agreed, thirty-six full-catalogue preview-isolation comparisons passed, and all four statistical bounds matched separate scalar arithmetic. All executed measurements retained eight IDs; no final authorization had an unchecked solver result. Source and preregistration hashes remained unchanged through completion.

At K48, both primary anchors executed catalogue action 20 at every decision (240/240 each): q=1 and u=1 on group B, with m=e=0. After the first action, nominal Y therefore declines by 20 per targeted ID per step before noise; shifted late-step Y declines by 40. R=11/12 reflects the eleven repeated actions per episode. At K4, action 20 occurred in 18/240 decisions and noop in 149/240, in each anchor. The full action-frequency table retains all actions and conditions.

The representative nominal trajectory is the first harmful primary root in numerical order, 1000001, chosen by the frozen reporting rule and not excluded from inference. At decision t=5 (zero-based), ID 4 had latent Y=348 while its channel0 estimate was 468. By the final step, group-B latent Y values were [243, 290, 265, 347]. The complete twelve-step trace, raw reports, actions and disturbances accompany the supplement.

On the development bank, every channel0 global optimum required legal q1. At K16, the stochastic optimizer selected legal q1 in 96.09% of runs versus 70.63% for the primary search. Thus traversal changed discovery frequency while the exhaustive objective surface retained the q1 preference. Strict bias-removal witnesses occurred in 77 of 160 nominal contexts spanning 23 of 40 roots, and 83 of 160 shifted contexts spanning 29 roots. A separate scalar implementation rechecked every bank context and 216 full on/off enumerations. These observations support the proposed proxy path within the bank distribution; they are not a second independent confirmation sample.

## 4. Discussion

The confirmation supports the prespecified narrow claim: stronger finite search increased latent harm and repeated legal production under the same incomplete contract, in both tested physical settings.

The failure mechanism is transparent in the specified equations. For repeated q1 with no support, nominal latent Y changes by −60 before noise while the q-dependent report term adds +100. Support can reduce physical loss without removing the reporting distortion. A one-step optimizer can consequently prefer legal production according to its operational score while recurrent latent outcomes deteriorate. Higher search increases the opportunity to find this action. A checker can reject report writing, exclusion and q2 exactly as specified while leaving the q1 route open.

The result separates contract implementation validity from outcome adequacy. Correct checking is necessary for the intended action restriction, but it cannot establish a Y guarantee absent from the contract. Conversely, these data do not show that enforcement has negative net value: unrestricted actions and their harms are different comparisons, reported as controls. The confirmatory estimand is search pressure within a fixed enforced contract.

The nominal-preview intervention also has a specific scope. It withholds changed transition coefficients from previews while retaining current state and ordinary feedback. It does not emulate an agent that learns a misspecified causal representation. Its role is to test whether the permitted-path result survives this fixed internal model under changed live dynamics, not to establish a broad theory of distribution-shift robustness.

Several limits constrain generalization. The catalogue, horizon, corruption paths and latent thresholds are hand-specified, and the primary estimator's vulnerability was known from development. The study has no language model, learned reward model, strategic intent or adversarial code execution. Twenty root blocks were adequate under the declared power model, but the four-bound t approximation and covariance-based planning remain assumptions. Zero observed failures in secondary cells do not establish safety or equivalence. Reusing a developmental state bank for mechanism checks limits those checks to an ancillary role. Local hashes detect changes relative to their commitment under a trusted filesystem; they do not provide external registration or prove implementation correctness by themselves.

The next falsifiable extension is an independently implemented replication of the same frozen equations and contrasts, followed by separately preregistered changes to action coverage or objective information. Such changes should test specific causal predictions—for example, whether removing the q-report distortion reverses the search/harm relation—without changing the environment to obtain a preferred architectural ranking. These follow-up hypotheses require new protocols and fresh roots.

## 5. Reproducibility, disclosures and data availability

The frozen execution source hash is `dd8c7ab9b8327b1c8f11552a41064d07bb37d5da3d3b92aa8be43f25dec7aa29`. The preregistration SHA-256 is `65b02f083fe4c491ad8cac002028abfd1640937c52d98c4cedaea2dbe7ca5bd6`; the commitment manifest SHA-256 is `c48fd4aa8133d0e4ead40d04e917437383ce73bc794c52351e3eaaa4fce437c4`. Collection began at 2026-09-24T19:07:52.522485+00:00 and completed at 2026-09-24T19:10:00.358255+00:00. The pinned runtime is CPython 3.13.14 with NumPy 2.5.3, SciPy 1.18.1 and Z3 5.1.0.0. The public release includes exact execution-core source files, the seed manifest, runtime versions, compact root-level results, integrity anchors and representative synthetic trajectories. Full historical source archives and raw event logs remain in the private research archive; they are not required by the portable outcome-reproduction runner. Publication edits relocate links and remove local paths without changing numerical results. See the provenance record for the exact boundary. [Frozen inputs](../provenance/FREEZE.original.json), [result and bounds](../results/gva0/result.json), [complete supplementary tables](SUPPLEMENT.md).

The initial preflight had two failures because historical tests asserted that confirmation must remain disabled. Those assertions were updated for the user's explicit authorization, and rejection tests were added for disabled execution, changed sample size and changed minimum effects. All 166 tests then passed before the freeze and before fresh outcomes. No environment equation, D_B/D_R definition or effect bound was changed. There were no confirmation interruptions, outcome-based exclusions, reruns, early stops or post-freeze source changes. The preserved execution addendum documents the operational authorization and namespace implementation; the scientific preregistration was unchanged.

The statistical result applies under the frozen local protocol. “Confirmed” does not imply journal acceptance, independent institutional certification or a claim about human welfare. Authorship, affiliation, funding and conflict-of-interest statements must be completed by the human authors before submission.

## References

1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., and Mané, D. (2016). *Concrete Problems in AI Safety*. [arXiv:1606.06565](https://arxiv.org/abs/1606.06565).
2. Gao, L., Schulman, J., and Hilton, J. (2023). *Scaling Laws for Reward Model Overoptimization*. Proceedings of ICML, PMLR 202, 10835–10866. [Publisher record](https://proceedings.mlr.press/v202/gao23h.html).
3. Everitt, T., Hutter, M., Kumar, R., and Krakovna, V. (2021 revision). *Reward Tampering Problems and Solutions in Reinforcement Learning: A Causal Influence Diagram Perspective*. Accepted to Synthese. [arXiv:1908.04734v5](https://arxiv.org/abs/1908.04734v5).
