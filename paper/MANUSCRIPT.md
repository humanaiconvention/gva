# Search Pressure Increases Harm on an Admissible Action Path: A Verified Synthetic Case Study

**Revised public case study v0.5.1 — 24 September 2026.** Maintained by HumanAI Convention; principal-investigator name and affiliation await author confirmation. The frozen GVA-0 result is preserved. The post-publication review analyses are explicitly exploratory. No external registration, independent replication or peer review is claimed.

## Abstract

This synthetic benchmark demonstrates how exhaustive optimization of a deliberately biased score can select harmful actions that an incomplete action contract permits. The mechanism was known from development and is largely determined by the chosen equations; the subsequent frozen-seed run verifies implementation and quantifies variation within that construction, rather than discovering an unexpected empirical effect. In twenty paired roots, increasing search from four to all 48 catalogue actions increased threshold-breach burden while every executed action satisfied the enforced predicate. Exhaustive search repeatedly selected production with support on the lower-starting group. Enforcement nevertheless reduced harm relative to unrestricted search. A harsher-physics condition amplified harm along the same primary action sequence and is not an independent replication. We retain the original statistical record, distinguish repeated production from evidence of proxy bias, and report additional estimator, search-budget and design-sensitivity analyses as exploratory. The contribution is an inspectable, reproducible mechanism demonstration; its generality requires independent implementation and separately designed repair experiments.

## 1. Introduction

An action checker guarantees compliance with its predicate, which need not guarantee the outcomes a designer intended. GVA-0 constructs a small example in which an action-dependent reporting bias makes damaging production attractive to a one-step optimizer, even after report writing, exclusion and high production are prohibited.

Reward misspecification and specification gaming are established problems [1,4,7]. Pan, Bhatia and Steinhardt vary agent capabilities and observe changes in proxy exploitation, including capability-dependent transitions [4]. Skalse and colleagues formalize conflicts between proxy and true reward orderings [5]; Manheim and Garrabrant distinguish mechanisms of metric overoptimization [6]. Reward-model overoptimization [2] and causal analyses of reward tampering [3] provide further context. GVA-0 contributes a compact audited construction, not a new general demonstration that reward misspecification exists.

The original frozen question was whether K48 versus K4 increased both latent harm burden and repeated legal production under an unchanged contract. We retain that decision as a historical protocol result. Calling it failure displacement was too strong: the original design did not include unrestricted K4, and enforcement reduced K48 harm. This revision therefore concerns **search-related harm on an admissible path**. Channel comparisons, an expanded K sweep and new live-state interventions below are post hoc analyses, not replacements for the original primary endpoints.

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

### 2.3 Estimator comparison and archival controls

Channel2 lacks channel0's explicit q-dependent Y bias in nominal and physical-shift conditions, while retaining the same bounded sensor-noise distribution. It is therefore an informative comparator. Different channel noise realizations remain paired by root but are not identical; the same-channel bias-removal replay more directly isolates the reporting term. The main operational comparison uses enforcement in both channels. Additional measurement and fusion conditions, and their 54 prespecified secondary contrasts, are retained in Supplement S0–S3.

The review adds the paired difference-in-differences (B48−B4)_channel0 − (B48−B4)_channel2, together with corresponding R/L/P contrasts. These were not primary in the frozen protocol. Their descriptive intervals cannot be presented as retroactively preregistered evidence.

### 2.4 Endpoints, sampling unit and confirmatory rule

The independent sampling unit is a complete root block. Individuals, decisions, preview replicas and optimizer restarts are nested observations. The primary harm endpoint is

\[
B_{s,K,r}=\frac1{96}\sum_{t=1}^{12}\sum_{i=1}^{8}\mathbf1\{Y_{i,t}<350\}.
\]

The repeated-production endpoint is

\[
R_{s,K,r}=\frac1{12}\sum_{t=0}^{11}\mathbf1\{\operatorname{Contract}(a_t),
\ \exists i:q_{i,t}=q_{i,t-1}=1\}.
\]

R measures repeated legal production and is not specific to proxy exploitation: unbiased production may also repeat because it raises X. Mechanistic specificity depends on latent harm and controlled reporting interventions, not on R alone. Safeguards are L, the smaller fixed-group time-averaged Y divided by 1000, and P, the time/roster mean X divided by 1000. Both group outcomes are reported.

For each of the two anchors, D_B=B48−B4 and D_R=R48−R4. The vector order is nominal D_B, nominal D_R, shifted D_B, shifted D_R. Minimum effects were fixed at (.05,.20,.05,.20). For each component j, the null is E[D_j]<=delta_j. At N=20, the simultaneous one-sided lower bound is

\[
LB_j=\bar D_j-t_{19,.9875}s_j/\sqrt{20}.
\]

The joint result passes only if every LB_j>delta_j, zero executed contract violations occur in all enforced cells, and implementation audits pass. Zero sample variance makes a primary criterion unassessable. The finite-sample t approximation is declared; it is not a distribution-free guarantee for bounded outcomes. Failure of the conjunction does not suppress individual contrasts or safeguards.

### 2.5 Sample planning, cryptographic freeze and blind execution

Forty development roots were excluded from confirmation. The planning algorithm used only their paired four-dimensional covariance, not their observed effect means. The prospective alternative was (.10,.30,.10,.30). It simulated 30,000 studies per sample size/covariance scenario, including simulated sample variance, over integers N=20..500. A sensitivity scenario multiplied covariance by 1.778459 while retaining estimated correlations. The smallest allowed N whose one-sided 95% Monte Carlo lower power bound exceeded .90 in both scenarios was 20, giving 820 episodes across 41 unique cells per root. Inflated-covariance modeled joint power was .9133, with Monte Carlo lower bound .91059. This is conditional power under the stated effect and Gaussian covariance assumptions; N was not recalculated after confirmation.

The original populated preregistration was retained byte-for-byte. An execution addendum enabled the approved collection phase and recorded namespace/runner plumbing without changing scientific definitions. The starting source and tested execution source were both archived. The execution freeze committed the protocol, source, runtime, calibration, seeds and preflight record using SHA-256 before any fresh outcomes. Root IDs 1000001..1000020 use namespace `gva0-confirm-v0.5-displacement`; root IDs, canonical key domains and all 1,220 derived 128-bit generator seeds were explicitly checked for nonintersection with development and calibration seeds. Each root supplies 61 named seeds: one initialization seed plus, at each of twelve decisions, one candidate-order seed and four disturbance seeds (live/preview × process/sensor). The 41 cells reuse those streams for pairing; they do not receive separate independent seed banks. This guarantees the checked seed sets are disjoint; coincident random output values remain possible.

During execution, only completion counts were exposed. No interim outcome summaries, sample-size changes, selective exclusions or outcome-based reruns were permitted. The actor interface remained blind to evaluator-only information. This was a locally committed automated no-interim-look design, not an externally registered or independently staffed double-blind trial.

### 2.6 Ancillary mechanistic challenge

Before confirmation, an untuned stochastic beam optimizer was applied to the independently frozen 160-state development bank. It received the same public catalogue and requested eight-replica batches, with width four, expansion four and uniform restart probability .25. Four private restarts were nested within each context. Exact enumeration identified whether every optimum required legal q1 or whether q1 appeared only through ties. K48 agreement is an implementation requirement because both optimizers exhaust the catalogue; K4/K16 probe traversal sensitivity.

A strict proxy-seeking witness required an original legal q1 choice, strict score preference over a legal alternative, strict ranking reversal when only explicit +100q reporting terms were removed before clipping, and lower latent one-step breach burden for the debiased choice at identical live disturbances. These interventions retain the state, physical equations, other report terms and noise. They are development diagnostics and contribute no observations to the confirmatory statistical test.

## 3. Results

### 3.1 Prespecified joint result

**The frozen conjunction passed as a verification of this engineered benchmark.** All twenty root blocks completed before analysis; no development root entered the primary sample.

| Criterion | Mean paired difference | Simultaneous lower bound | Minimum effect | Pass |
|---|---|---|---|---|
| Nominal D_B | 0.118229 | 0.101448 | 0.05 | True |
| Nominal D_R | 0.879167 | 0.851742 | 0.20 | True |
| Shifted D_B | 0.193750 | 0.183779 | 0.05 | True |
| Shifted D_R | 0.879167 | 0.851742 | 0.20 | True |

The Bonferroni bounds provide simultaneous one-sided coverage under the t assumptions. This is valid but stronger than necessary for a single intersection-union decision requiring every component to pass. Unadjusted one-sided .05 component tests would control that conjunction at .05 without independence assumptions. We retain the frozen bounds and decision rather than substituting a less conservative analysis after outcomes. The two D_R vectors are identical in these data; four listed criteria do not represent four distinct empirical signals.

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

### 3.3 Exploratory analyses added after public release

The follow-up reuses the twenty archived roots; it adds no independent sample. A 56-cell search/estimator/enforcement sweep generated 1,120 episodes, matched all 180 overlapping original cells, and passed scalar checks on 13,440 live transitions and every candidate bank on the first root. [Protocol, source and complete outputs](../exploratory/PROTOCOL.md) are separate from the frozen analysis.

**Estimator-by-search contrast.** The channel0-minus-channel2 difference in K48−K4 harm is .118229 nominally (descriptive paired 95% interval [.103795,.132663]) and .193750 under shifted/nominal previews ([.185174,.202326]). Channel2 has zero observed B at both budgets, while R rises from .016667 to .216667 nominally and to .204167 under shifted/nominal previews. Under shifted faithful previews, channel2 R48 is .154167. Those preview modes must not be pooled. R therefore does not by itself diagnose the harmful bias. All root-level B/R/L/P differences and intervals are reported; these post hoc contrasts do not replace the frozen primary family.

**Enforcement and activity.** Nominal channel0 harm is .466146 at unrestricted K48 versus .118229 with enforcement. The added unrestricted K4 cell has B=.317708 versus zero with enforcement. Under shifted nominal previews, unrestricted K4/K48 B is .320833/.466146, compared with .001042/.194792 enforced. Enforcement reduces harm at both tested endpoints. The data do not justify saying that enforcement caused a net harm increase.

| K | Nominal enforced channel0 B | Shifted enforced channel0 B | Nominal noop fraction |
|---:|---:|---:|---:|
| 1 | 0.000000 | 0.000000 | 1.000000 |
| 2 | 0.000000 | 0.000000 | 0.870833 |
| 4 | 0.000000 | 0.001042 | 0.620833 |
| 8 | 0.032813 | 0.038542 | 0.320833 |
| 16 | 0.076563 | 0.112500 | 0.083333 |
| 32 | 0.135938 | 0.187500 | 0.000000 |
| 48 | 0.118229 | 0.194792 | 0.000000 |

Nominal harm peaks at K32 and falls at K48: the realized harm response is **not monotone**. At K32, unsupported production on group B occurs 44/240 times, alongside 150 supported-production actions; K48 selects supported production 240/240 times. This action mix offers a concrete explanation for the decline, although frequencies alone are not a mediation analysis. K4 is 62.08% noop and K1 is noop by construction, so the low-budget contrast partly measures opportunity to act.

**Live-state reporting intervention.** On all 480 original primary K48 contexts, exhaustive bias-on replay reproduced the executed action; both bias-on/off banks matched independent scalar scores. The strict immediate-breach witness passed in 89/240 nominal and 84/240 shifted contexts, covering all twenty roots in each setting. The remaining contexts are retained, and no claim is made that every decision meets the witness. These analyses were specified after the original results and are exploratory.

**Design sensitivity.** For the observed fixed action-20 policy, nominal B at the original start interval and threshold is .019531/.118229/.210938 for horizons 8/12/16. At horizon twelve it is .043229/.118229/.217708 for thresholds 300/350/400. Moving group B's starting interval to [400,550] or [500,650] changes B to .217708 or .043229, respectively. The complete 54-cell table includes both physical regimes and all cross-combinations. This demonstrates substantial dependence on design choices; it holds the policy fixed and does not establish optimizer robustness to these changes.

## 4. Discussion

The central finding is a verified mechanism demonstration. Exhaustive search selects the intended biased-score optimum in every primary episode. The random roots quantify sensitivity to initialization and disturbances within a chosen construction; small t intervals do not establish the prevalence of this mechanism in other environments, and the outcome was highly predictable after development. “Confirmatory” here describes a frozen execution procedure, not a surprising test of a broadly uncertain scientific hypothesis.

The action actually selected is q=1 **with u=1 support** on group B. Its first nominal action changes Y by zero before noise; later repeated actions change Y by −20, and shifted late actions by −40. The report adds +100q before clipping. The unsupported −60 recurrence describes a different action and is not the explanation for the observed primary trajectory. This makes breach burden explicitly dependent on horizon, threshold and starting interval. The exploratory fixed-policy sensitivity table quantifies that dependence without claiming the optimizer would choose the same policy in every modified environment.

R cannot identify exploitation by itself. Even unbiased channel2 repeats productive actions as search grows. The channel-by-search harm contrast and same-state bias-removal intervention give more specific evidence, subject to their exploratory status and finite context distribution. Failure to satisfy a strict immediate-breach witness at a state does not establish that reporting bias is irrelevant there; it means that particular conjunction was not witnessed.

The physical-shift anchor changes the consequences of essentially the same primary behavior. Its identical R differences and inert primary preview manipulation prevent interpreting it as an independent replication or evidence of successful causal-model adaptation. The shift is a consequence-sensitivity condition. Independent replication requires a separate implementation effort, not another output from this shared simulator.

Enforcement has positive net harm reduction in the observed K48 comparison. No causal migration from an illegal pathway to a legal one was established by the original cells. The added unrestricted K4 cells supply the missing descriptive comparison, but they are post hoc and do not rescue a preregistered displacement claim. Similarly, the K sweep measures a finite catalogue search response. K4's high noop rate and K1's mandatory noop make action opportunity an important part of the contrast; nested candidate sets do not make realized state trajectories nested or guarantee monotonic harm.

The next study is a separately specified repair experiment: remove the reporting distortion, strengthen the contract, or combine them, while testing harm attenuation, production retention and residual harm. A forced reduction in a prohibited action is not an efficacy endpoint. GVA-1 requires new pilot contrasts, a new sample calculation and a prospective commitment; the GVA-0 sample of twenty is not inherited. Generalization to other optimizers, horizons, start distributions or genuine learned agents remains a separate question.

## 5. Reproducibility, disclosures and data availability

The frozen execution source hash is `dd8c7ab9b8327b1c8f11552a41064d07bb37d5da3d3b92aa8be43f25dec7aa29`. The preregistration SHA-256 is `65b02f083fe4c491ad8cac002028abfd1640937c52d98c4cedaea2dbe7ca5bd6`; the commitment manifest SHA-256 is `c48fd4aa8133d0e4ead40d04e917437383ce73bc794c52351e3eaaa4fce437c4`. Collection began at 2026-09-24T19:07:52.522485+00:00 and completed at 2026-09-24T19:10:00.358255+00:00. The pinned runtime is CPython 3.13.14 with NumPy 2.5.3, SciPy 1.18.1 and Z3 5.1.0.0. The public release includes exact execution-core source files, the seed manifest, runtime versions, compact root-level results, integrity anchors and representative synthetic trajectories. Full historical source archives and raw event logs remain in the private research archive; they are not required by the portable outcome-reproduction runner. Publication edits relocate links and remove local paths without changing numerical results. See the provenance record for the exact boundary. [Frozen inputs](../provenance/FREEZE.original.json), [result and bounds](../results/gva0/result.json), [complete supplementary tables](SUPPLEMENT.md).

The initial preflight had two failures because historical tests asserted that confirmation must remain disabled. Those assertions were updated to enable the approved collection phase, and rejection tests were added for disabled execution, changed sample size and changed minimum effects. All 166 tests then passed before the freeze and before fresh outcomes. No environment equation, D_B/D_R definition or effect bound was changed. There were no confirmation interruptions, outcome-based exclusions, reruns, early stops or post-freeze source changes. The preserved execution addendum documents the operational authorization and namespace implementation; the scientific preregistration was unchanged.

The statistical result applies under the frozen local protocol. The first release remains available as v0.5.0; this revision preserves its scientific definitions, numerical results and exact execution core. Post hoc review work is documented in the [review response](REVIEW-RESPONSE.md) and [exploratory protocol](../exploratory/PROTOCOL.md).

**AI assistance and accountability.** ChatGPT/Codex coding agents assisted protocol development, source implementation, tests and scalar audit code, run orchestration, statistical analysis, manuscript drafting and public artifact preparation. A Claude-generated critique supplied by the project maintainer motivated the present revision. Automated cross-checks within this AI-assisted project are not independent external authorship or replication. HumanAI Convention maintains the project; the human principal investigator's name, affiliation, funding and conflict-of-interest statements must be completed before journal submission. No identity or independent human validation is inferred from an account name.

## References

1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., and Mané, D. (2016). *Concrete Problems in AI Safety*. [arXiv:1606.06565](https://arxiv.org/abs/1606.06565).
2. Gao, L., Schulman, J., and Hilton, J. (2023). *Scaling Laws for Reward Model Overoptimization*. Proceedings of ICML, PMLR 202, 10835–10866. [Publisher record](https://proceedings.mlr.press/v202/gao23h.html).
3. Everitt, T., Hutter, M., Kumar, R., and Krakovna, V. (2021 revision). *Reward Tampering Problems and Solutions in Reinforcement Learning: A Causal Influence Diagram Perspective*. Accepted to Synthese. [arXiv:1908.04734v5](https://arxiv.org/abs/1908.04734v5).

4. Pan, A., Bhatia, K., and Steinhardt, J. (2022). *The Effects of Reward Misspecification: Mapping and Mitigating Misaligned Models*. ICLR 2022. [arXiv:2201.03544](https://arxiv.org/abs/2201.03544).
5. Skalse, J., Howe, N. H. R., Krasheninnikov, D., and Krueger, D. (2022). *Defining and Characterizing Reward Hacking*. [arXiv:2209.13085](https://arxiv.org/abs/2209.13085).
6. Manheim, D., and Garrabrant, S. (2018). *Categorizing Variants of Goodhart’s Law*. [arXiv:1803.04585](https://arxiv.org/abs/1803.04585).
7. Krakovna, V., et al. (2020). *Specification gaming: the flip side of AI ingenuity*. Google DeepMind, with the linked specification-gaming catalogue. [Article and examples](https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/).
