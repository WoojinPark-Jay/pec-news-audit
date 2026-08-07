# PEC Methods, Formulas, and Results Study Notes

Generated: 2026-07-10  
Manuscript: `paper/icwsm_pec_gap_v47_author_year_protocol_blind_full.md`

This document records the PEC paper's methods for collaborator review and project documentation. It covers the concepts, formulas, statistical checks, modeling choices, and what the observed values mean in the data.

## 1. The Central Problem

Personalized news systems often treat several traces as if they were one pipeline:

1. A user states preferences.
2. The system recommends articles.
3. The user clicks articles.
4. The platform evaluates personalization by interpreting clicks as preference.

The paper argues that this pipeline assumption is too simple. In a real mobile news app, a user may click from headline modules, category tabs, home/feed, newsroom tabs, search, notifications, or article-detail pathways. A click may reflect preference, curiosity, breaking-news salience, UI position, habit, or chance. A recommendation log may capture one exposure channel but not total exposure. A profile preference may capture broad intent but not all situational consumption.

The PEC audit separates these layers:

- **P: Preference**: stated categories, stated sources, weighted profile-state distributions.
- **E: Logged exposure**: user-date recommendation lists and ranks recorded by the system.
- **S: Surface pathways**: app pathway through which a click was observed.
- **C: Consumption**: clicked articles linked to category, publisher, date, and other metadata.

The main claim is:

> Preferences, logged exposure, and clicks are informative but non-substitutable.

That means each layer carries signal, but no layer can safely stand in for another without checking the relationship.

The PEC gap is not one aggregate score. It is a family of relation-specific
discrepancies: preference-consumption alignment, exposure-consumption
traceability, exposure-consumption diversity shift, and structured
preference-consumption divergence. Each comparison uses its own denominator and
validity check, because the meaning of a gap changes depending on which traces
are being compared.

## 2. Data Objects and Notation

For each user \(u\):

- \(P_{cat}(u)\): stated category preference set.
- \(P_{pub}(u)\): stated publisher/source preference set.
- \(E(u,d)\): articles logged as recommendation exposure for user \(u\) on day \(d\).
- \(E_u=\bigcup_d E(u,d)\): all logged exposure items for user \(u\) over the observation window.
- \(C_u\): clicked articles for user \(u\), linked to metadata.
- \(C^{top}_{cat}(u)\): user's top three clicked categories, or fewer if fewer categories are observed.
- \(p^P_u\): weighted profile-state distribution.
- \(p^E_u\): logged-exposure distribution.
- \(p^C_u\): click-consumption distribution.

Each article \(i\) has:

- category \(\operatorname{cat}(i)\)
- publisher \(\operatorname{pub}(i)\)
- date \(\operatorname{date}(i)\)

In plain words, the paper converts raw logs into comparable distributions over categories or publishers. It then asks whether the preference distribution, exposure distribution, and click distribution agree.

## 3. RQ1: Preference-Consumption Alignment

RQ1 asks:

> To what extent do stated news preferences align with actual consumption?

### 3.1 Top-Category Match

The simplest check asks whether the user's most-clicked category appears in the user's stated category preferences.

If yes, the user's dominant consumption category is represented in their profile. If no, their biggest observed interest is absent from stated preference.

**The result**: 77.22% of the 698 profile-and-click users have their top consumed category inside stated preferences. The 19 users with empty stated-category sets remain in this denominator as nonmatches.

**Interpretation**: explicit preferences are meaningful. They often capture the user's dominant topical orientation.

### 3.2 Category Jaccard Overlap

Jaccard overlap compares two sets:

\[
J_u=\frac{|P_{cat}(u)\cap C^{top}_{cat}(u)|}{|P_{cat}(u)\cup C^{top}_{cat}(u)|}.
\]

It ranges from 0 to 1:

- 0 means no overlap.
- 1 means perfect overlap.
- A middle value means the sets partially overlap.

**The result**: across all 698 users, mean category Jaccard is 0.2283 and median Jaccard is 0.2000. The 19 current snapshots with an observed empty stated-category set contribute zero overlap; restricting to the 679 nonempty stated sets gives a sensitivity mean of 0.2347 and the same median.

Applying that same rule in the click-history sensitivity checks gives mean top-3 Jaccard of 0.3004 among users with at least five clicks (n=302) and 0.3104 among users with at least ten clicks (n=175). These are higher than the full-cohort value but remain far from complete overlap.

The observed values exceed two 10,000-permutation chance checks. The
shuffled-set null yields 61.54% top-category match and mean Jaccard 0.161; the
size-preserving category-frequency null yields 54.81% and 0.137.

**Interpretation**: top-category match and Jaccard tell different stories. Top-category match says the main clicked category is often covered. Jaccard says the full breadth of clicked categories is not well captured. Together, the result is not "profiles fail" and not "profiles fully work." The bounded finding is: stated preferences capture dominant orientation but not consumption breadth.

### 3.3 Divergence Score

The paper defines a user-level preference-consumption divergence:

\[
D_u=1-J_u.
\]

Higher \(D_u\) means lower overlap between stated preferences and top clicked categories.

This score is used later for diagnostic modeling. It is not a production target. It is an audit label that lets us ask whether high-divergence users are patterned by observable features.

### 3.4 Weighted Preference-Click Cosine

The app also has weighted profile-state values. Instead of treating the profile as a set, we can treat it as a probability-like vector. Cosine similarity compares the direction of two vectors:

\[
A_u=\cos(p^P_u,p^C_u).
\]

Cosine is high when profile weights and click shares point in similar directions.

**The result**: mean category preference-click cosine is 0.452.

**Interpretation**: weighted profile-state contains stronger directional signal than raw preference sets, but it still does not fully explain consumption.

### 3.5 Publisher-Level Alignment

The same idea is applied to publisher/source preferences.

**The result**:

- mean weight on top clicked publisher: 0.014
- mean publisher preference-click cosine: 0.080

**Interpretation**: source-level preference is much weaker in the available profile representation, but this should be read with support size in mind. Category taxonomies have a relatively small fixed support, whereas publisher/source spaces are much larger and sparser. The 0.014 top-publisher weight therefore should not be treated as directly comparable to a category weight on the same scale. The safer conclusion is that clicked publishers rarely receive salient mass in the observed source-profile state, while category preferences capture broad topical orientation more clearly.

## 4. RQ2: Exposure-Consumption Traceability

RQ2 asks:

> How much observed click consumption can be traced to logged recommendation exposure?

This is not CTR. CTR starts from impressions and asks how many were clicked. Our measure starts from clicks and asks whether the clicked article was present in the logged recommendation exposure.

### 4.1 Same-Day Hit

For clicked article \(i\):

\[
H_{ui}=\mathbf{1}\{i\in E(u,\operatorname{date}(i))\}.
\]

This equals 1 if the clicked article appeared in user \(u\)'s logged recommendation list on the same date.

**The result**:

- 17,232 matched clicks
- 11,440 clicks with same-day recommendation lists available
- same-day hits: 1,292
- same-day hit rate: \(1{,}292/11{,}440=11.29\%\)
- six-month recommendation-history overlaps: 2,477
- six-month recommendation-history overlap rate: \(2{,}477/17{,}232=14.37\%\)

The denominators are different. Same-day hit can only be computed for clicks where the user has an observed same-day recommendation list, so its denominator is the 11,440 comparable clicks. Six-month recommendation-history overlap asks whether the clicked article appeared anywhere in the user's logged recommendation history, so its denominator is all 17,232 matched clicks. The history-overlap rate is higher because the timing condition is looser and click-date ordering is not enforced.

**Interpretation**: logged recommendations are one pathway into click consumption, but they do not explain most observed clicks. This supports "logged exposure is partial" rather than "recommendations are irrelevant."

### 4.2 Date-Matched Random Baseline

A hit rate is only meaningful if compared to a baseline. The date-matched logged-list candidate-pool baseline preserves the same day and list size, then asks:

> If we drew a random list from that day's recommendation candidate pool, how often would the clicked item appear?

**The result**:

- logged same-day hit: 11.29%
- date-matched random hit: 9.13%

**Interpretation**: logged recommendation exposure is above random. It carries signal. But the margin is modest, and many clicks still come from other surfaces.

### 4.3 Top-k Lift

For top-k recommendations:

\[
Lift_k=\frac{\mathbb{E}[H^k_{obs}]}{\mathbb{E}[H^k_{rand}]}.
\]

If lift is greater than 1, the logged recommendation list performs above random expectation.

**The result**:

- top-5 logged hit: 4.99%
- top-5 random hit: 3.41%
- top-5 lift: 1.47x

**Interpretation**: high-ranked recommendations are not arbitrary. The top of the list has measurable traceability signal.

### 4.4 Popularity-Aware Baselines

Random baselines do not address popularity. A clicked article may appear in recommendation logs because it is globally popular. The paper therefore compares against simple popularity baselines:

- same-day global recommendation popularity
- prior-day click popularity
- prior-week click popularity

**Interpretation**: these are descriptive checks. They do not fully isolate editorial salience, but they help show whether logged exposure is doing more than random or generic popularity.

## 5. Surface Pathways

Surface-pathway analysis asks:

> Through which app pathway did observed consumption happen?

The surface layer \(S\) is crucial because not all clicks come from recommendation lists. Clicks can come from headline, category, home/feed, newsroom, article-detail, search, notification, or other pathways.

**The result**:

- headline: 65.4% of matched clicks
- category: 14.0%
- home/feed: 9.3%
- newsroom: 7.0%
- article-detail: 4.1%

**Interpretation**: observed click consumption is multi-surface. A single recommendation log cannot represent the entire product environment.

Surface-level traceability also varies. Category clicks show a stronger same-day recommendation hit rate than headline clicks. That means surfaces differ in how strongly they connect to logged recommendation exposure.

## 6. RQ3: Diversity Shift

RQ3 asks:

> Does exposure-side diversity become consumption-side diversity?

This is one of the paper's central findings.

### 6.1 Normalized Entropy

Entropy measures breadth:

\[
E(X)=-\frac{\sum_x p_x\log p_x}{\log |X|}.
\]

Higher entropy means the distribution is spread across more categories or publishers.

**The result**:

- recommendation-category entropy: 0.8352
- click-category entropy: 0.5401
- recommendation-publisher entropy: 0.9129
- click-publisher entropy: 0.6256

**Interpretation**: logged recommendation exposure is broader than observed click consumption. But this raw comparison must be treated carefully because exposure lists contain many more items than clicks.

### 6.2 Top-Category Share

Top-share measures concentration:

\[
TopShare(X)=\max_x p_x.
\]

Higher top-share means more top-heavy behavior.

**The result**:

- recommendation top-category share: 0.3704
- click top-category share: 0.6928

**Interpretation**: click consumption is much more concentrated in a user's dominant category. This is not a contradiction with entropy. Entropy and top-share point in opposite interpretive directions:

- high entropy = broad distribution
- high top-share = concentrated distribution

So the finding is: exposure is broad, but clicks are top-heavy.

### 6.3 HHI Concentration

HHI is another concentration measure:

\[
HHI(X)=\sum_x p_x^2.
\]

If all mass is in one category, HHI is high. If mass is spread evenly, HHI is low.

**The result after count matching**:

- HHI gap: 0.082

**Interpretation**: even after correcting for count differences, click consumption remains more concentrated than matched exposure.

### 6.4 Jensen-Shannon Divergence

JS divergence compares two distributions:

\[
JS(p,q)=\frac{1}{2}KL(p\Vert m)+\frac{1}{2}KL(q\Vert m),\quad m=\frac{p+q}{2}.
\]

JS is useful because it asks whether exposure and click distributions differ in shape. Entropy asks how broad one distribution is; JS asks whether two distributions are the same distribution.

In this paper, JS is computed over the union of observed categories. Zero-mass terms do not require smoothing because the mixture distribution \(m\) handles categories that appear in one distribution but not the other.

**The result after count matching**:

- category JS divergence: 0.471

**Interpretation**: even when entropy gaps shrink, exposure and click distributions remain meaningfully different.

### 6.5 Count Matching

The raw comparison is unfair because recommendation exposure usually contains more items than clicks. More observations mechanically create broader distributions. Count matching fixes this by sampling exposure down to the number of clicks:

\[
\Delta_M(u)=M(E'_u)-M(C_u),\quad |E'_u|=|C_u|.
\]

Where:

- \(E'_u\) is a sampled subset of the user's logged exposure.
- \(C_u\) is the user's clicked article set.
- \(M\) can be entropy, HHI, top-share, or another metric.

**The result**:

- raw category entropy gap is large.
- among users with at least five clicks, count-matched category gap is 0.032.
- among users with at least ten clicks, the gap is near zero at 0.010.
- audit-eligible concentration gaps remain: HHI 0.082, top-share 0.069, JS 0.471.

**Interpretation**: the raw diversity gap is partly an observation-count artifact. But the remaining concentration and JS mismatch show that the exposure-consumption difference is not fully explained away. The careful claim is not "users ignore diversity." The careful claim is: exposure-side diversity and consumption-side diversity are different measurement layers, and residual concentration/distribution mismatch remains after count correction.

## 7. RQ4: Structured but Bounded Divergence

RQ4 asks:

> Are high preference-consumption gaps patterned by observable profile-state and behavioral features?

The model is diagnostic, not operational. It is not a recommender, not a targeting model, and not a prospective production forecast.

### 7.1 Label

The main high-divergence label uses \(D_u=1-J_u\). Users above the sample median are labeled high-divergence.

This label is close to preference-consumption alignment by construction. That is why the paper is careful about leakage and does not treat AUC as a standalone claim.

### 7.2 Feature Groups

Allowed feature groups include:

- basic profile indicators and category/source profile-support counts
- weighted profile-state distribution properties
- exposure diversity/count features
- behavior features such as click count, active days, and click timing

Excluded leakage features include:

- realized clicked-category weights
- preference-click cosine
- preference-click JS divergence
- other direct alignment-derived features

The internal variables `num_stated_categories` and `num_stated_publishers` are profile-support counts, not the explicit-set cardinalities used to construct Jaccard. The code takes the larger observed support across the explicit-selection and weighted-profile fields. In particular, category support is constant at 13 in the 698-user modeling cohort, so it cannot identify the 19 empty explicit stated-set cases.

### 7.3 AUC and AUPRC

AUC measures how well a classifier ranks positive examples above negative examples. AUC 0.5 is random; higher is better.

AUPRC measures precision-recall performance and is useful when labels are imbalanced.

**The result**:

- basic profile + support counts alone: AUC 0.544
- unweighted full model: AUC 0.784
- weighted profile-state only: AUC 0.696
- full audit + weighted profile-state: AUC 0.859, AUPRC 0.861
- full audit after excluding 19 empty stated-set users: AUC 0.853
- full audit after removing category/publisher support counts: AUC 0.862

**Interpretation**: weighted profile-state improves same-window diagnostic classification. The near-unchanged empty-state sensitivity and support-count ablation show that the headline result is not driven by deterministic empty cases or those two count features. But this is not the headline claim by itself because the label is related to preference-consumption divergence.

### 7.4 Temporal Split

The future-window diagnostic trains on Jan-Mar behavior and exposure features and evaluates Apr-Jun high-divergence labels. Because the later label still uses the available non-versioned preference snapshot, this is not a fully prospective preference-state forecast.

**The result**:

- temporal high-divergence AUC: 0.731

**Interpretation**: the signal survives a more difficult time-separated check, but it is weaker than same-window classification. This supports a bounded diagnostic interpretation.

### 7.5 Dense-History Checks

The model is rerun among users with denser click histories:

- users with at least 5 clicks: AUC 0.698
- users with at least 10 clicks: AUC 0.707

**Interpretation**: performance drops among denser users. This means some of the easier classification cases are tied to sparse histories or unstable observations. The model should not be sold as a strong production predictor.

### 7.6 SHAP / Feature Importance

The feature-importance result shows which variables contribute most to diagnostic classification.

Top feature in the release check:

- `click_count`, mean absolute SHAP about 0.076

**Interpretation**: behavior features are important. This supports the idea that high divergence is not only a static profile issue; it is also related to how users behave in the app. However, because click count can also reflect observation density, the analysis uses dense-history and temporal checks to avoid overclaiming.

## 8. Bootstrap Confidence Intervals

The paper uses bootstrap intervals for some aggregate metrics. Bootstrapping means repeatedly resampling the data and recomputing the statistic.

Why use it?

- It estimates uncertainty without requiring a strict parametric assumption.
- It is useful for empirical log metrics such as hit rates and entropy gaps.

Example:

- date-matched logged-list candidate-pool expectation: 9.13%, 95% CI [8.77%, 9.53%]
- publisher entropy gap: 0.274, 95% CI [0.238, 0.309]

**Interpretation**: the uncertainty intervals make the audit less like a single static dashboard number and more like an empirical measurement study.

## 9. Audit-Eligible Cohort

The audit-eligible cohort includes users with:

- at least five matched clicks
- at least 20 matched recommendation items
- at least two active click days
- at least two stated preference categories

Why this matters:

- If a user has only one click, entropy and Jaccard can be unstable.
- If a user has few recommendation items, exposure distribution is unreliable.
- If a user has too little preference data, preference-consumption alignment is hard to interpret.

The audit-eligible cohort is therefore not cherry-picking; it is a measurement-validity filter.

## 10. Finding-Level Interpretation Notes

### Finding 1: Preferences Are Meaningful but Shallow

Summary:

> User-stated preferences often include the dominant clicked category, but they do not capture the full breadth of observed consumption.

Evidence:

- top-category match: 77.22%
- primary mean Jaccard: 0.2283 (nonempty-set sensitivity: 0.2347)
- category cosine: 0.452

### Finding 2: Logged Exposure Carries Signal but Is Partial

Summary:

> Logged recommendations are above random and popularity-aware baselines, but they explain only one part of click consumption in a multi-surface app.

Evidence:

- same-day hit: 11.29%
- date-matched random: 9.13%
- top-5 lift: 1.47x
- many clicks come from headline/category/home/newsroom/article-detail surfaces

### Finding 3: Diversity Shift Is Layer-Dependent

Summary:

> Exposure is broader than clicks in raw logs, but raw entropy gaps partly reflect observation-count differences. After count matching, concentration and distributional mismatch remain.

Evidence:

- category entropy: exposure 0.8352 vs click 0.5401
- top-category share: exposure 0.3704 vs click 0.6928
- count-matched HHI gap: 0.082
- count-matched top-share gap: 0.069
- JS divergence: 0.471

### Finding 4: Divergence Is Structured but Bounded

Summary:

> High preference-consumption divergence is not pure noise. It is partly identifiable from profile-state and behavioral features, but the model is diagnostic, not a production predictor.

Evidence:

- full + weighted profile-state AUC: 0.859
- future-window diagnostic AUC: 0.731
- dense-history checks: 0.698 to 0.707

## 11. Common Misreadings and Correct Responses

### Misreading 1: "The recommender is bad because same-day hit is only 11.29%."

Correct response:

> No. Same-day hit is not CTR and not total recommender quality. It is a traceability statistic conditioned on observed clicks and available recommendation logs. The hit rate is above date-matched random, so logged recommendations carry signal, but they are not the whole exposure environment.

### Misreading 2: "The platform is diverse because exposure entropy is high."

Correct response:

> Exposure diversity is not the same as consumption diversity. The paper shows that click consumption is more top-heavy, and count-matched checks reveal residual concentration/distribution mismatch.

### Misreading 3: "Count matching removes the diversity result."

Correct response:

> Count matching reduces the raw entropy gap, which is important. But HHI, top-share, and JS divergence remain positive in the audit-eligible cohort. The robust claim is residual concentration/distribution mismatch, not raw entropy alone.

### Misreading 4: "AUC 0.859 is the main contribution."

Correct response:

> No. The model is a diagnostic extension. The main contribution is PEC as a measurement audit framework. The model shows that divergence is structured but bounded.

### Misreading 5: "This is only one app, so it does not generalize."

Correct response:

> The exact values may not generalize. The reusable contribution is the audit design: separate preference, exposure, surface, and consumption traces before making personalization claims.

## 12. Formula-by-Formula Notes

This section records formula-level interpretation notes. It explains not only what each formula means, but also why it appears in the paper and common interpretation risks.

### 12.1 Set Overlap: Why Jaccard Is Used

Jaccard overlap is useful when two objects are sets rather than probability distributions. In our case:

- stated category preferences are a set of categories the user explicitly selected;
- top clicked categories are a set of categories most frequently observed in the user's clicks.

\[
J_u=\frac{|P_{cat}(u)\cap C^{top}_{cat}(u)|}{|P_{cat}(u)\cup C^{top}_{cat}(u)|}.
\]

The numerator asks, "how many categories appear in both sets?" The denominator asks, "how many distinct categories appear in either set?" This makes the score strict. If a user says they like five categories but clicks heavily in only one of them, top-category match may be positive but Jaccard can still be low. That is exactly why the paper uses both.

**Result interpretation**: the 77.22% top-category match means the dominant clicked category is usually not alien to the profile. But the 0.2283 primary mean Jaccard means the broader shape of consumption is not fully represented by the stated preference set. So the right sentence is: "profiles are meaningful but shallow."

### 12.2 Why Divergence Is Defined as One Minus Jaccard

\[
D_u=1-J_u.
\]

This converts alignment into mismatch. A high value means the user's top clicked categories and stated categories overlap weakly. This is useful for modeling because it creates a target variable: high-divergence users versus lower-divergence users.

The key interpretation point is that \(D_u\) is an audit construct, not a moral judgment about the user and not an error label. A user can diverge from stated preferences for many reasonable reasons: breaking news, headline salience, UI pathways, temporary interest, or stale profile settings.

### 12.3 Cosine Similarity: Direction, Not Exact Equality

Cosine similarity compares the direction of two vectors:

\[
\cos(p^P_u,p^C_u)=
\frac{p^P_u\cdot p^C_u}{\|p^P_u\|\|p^C_u\|}.
\]

If two distributions put high weight on similar categories, cosine is high. It does not require the exact same magnitude in every category. That makes it useful for weighted profile states: the analysis focuses on whether profile weights point toward the same categories as click behavior.

**The result**: category preference-click cosine is 0.452, which is meaningfully higher than publisher/source cosine at 0.080. This tells a clear story: category-level profile state carries signal, but source-level profile state is weakly aligned with actual publisher consumption.

### 12.4 Same-Day Hit: Why It Is Not CTR

The hit indicator is:

\[
H_{ui}=\mathbf{1}\{i\in E(u,\operatorname{date}(i))\}.
\]

This is evaluated from the perspective of clicked items. It asks whether a clicked article can be found in the logged recommendation list for that user and date. CTR would start from exposures and ask which exposures were clicked. Our statistic starts from clicks and asks which clicks are traceable to logged exposure.

**Why this matters**: a reader might see 11.29% and think the recommender has low CTR. That would be wrong. The statistic is not measuring conversion from recommendation impressions. It measures traceability of observed click consumption to the available recommendation logs.

### 12.5 Lift: Why Baselines Matter

\[
Lift_k=\frac{\mathbb{E}[H^k_{obs}]}{\mathbb{E}[H^k_{rand}]}.
\]

Lift compares the observed logged recommendation traceability against a baseline. A top-5 lift of 1.47x means top-5 logged recommendations contain clicked items 47% more often than a comparable random list from the same date. This supports the claim that logged exposure carries signal.

The lift result should not be oversold. It does not prove causal personalization. It shows that the logged list is not arbitrary relative to observed clicks.

### 12.6 Entropy: Diversity as Spread

Normalized entropy is:

\[
E(X)=-\frac{\sum_x p_x\log p_x}{\log |X|}.
\]

Entropy increases when probability mass is spread across many categories. Normalization by \(\log |X|\) keeps the score comparable across supports of different sizes.

**Our raw result**: category entropy is 0.8352 for logged exposure and 0.5401 for clicks. That means exposure is broadly distributed across categories, while clicks are narrower.

**The caution**: entropy is sensitive to sample size. If exposure has many more items than clicks, exposure can look broader partly because it has more chances to include more categories. That is why count matching is essential.

### 12.7 Top-Share and HHI: Diversity's Opposite Direction

Top-share is:

\[
TopShare(X)=\max_x p_x.
\]

HHI is:

\[
HHI(X)=\sum_x p_x^2.
\]

Both measure concentration rather than diversity. Higher entropy means broader distribution; higher top-share or HHI means more concentrated distribution. This is why Figure 3 must be read carefully. The direction of the metric changes.

**The result**: click top-category share is 0.6928, while exposure top-category share is 0.3704. In plain English, the clicked distribution is more dominated by one category. After count matching, HHI gap remains 0.082 and top-share gap remains 0.069. This is the strongest version of the diversity finding because it survives a count-correction check.

### 12.8 Jensen-Shannon Divergence: Distributional Shape Difference

Jensen-Shannon divergence is:

\[
JS(p,q)=\frac{1}{2}KL(p\Vert m)+\frac{1}{2}KL(q\Vert m),
\quad m=\frac{p+q}{2}.
\]

Entropy asks, "how broad is one distribution?" HHI asks, "how concentrated is one distribution?" JS asks a different question: "how different are two distributions from each other?"

This is valuable because two distributions can have similar entropy but still emphasize different categories. For example, one user could have exposure spread across politics and economy, while clicks are spread across sports and entertainment. Entropy alone might miss that shift; JS captures it.

**The result**: count-matched category JS divergence is 0.471. This is why the paper can say that distributional mismatch remains even when the raw entropy gap shrinks.

### 12.9 Count Matching: Separating Measurement Artifact From Substantive Gap

Count matching samples exposure down to the number of clicks:

\[
\Delta_M(u)=M(E'_u)-M(C_u),\quad |E'_u|=|C_u|.
\]

This is a fairness correction between layers. Logged exposure has many more observations than clicks, so raw diversity comparisons can exaggerate the exposure-click gap. Count matching asks: if exposure had the same number of observations as clicks, would the gap remain?

**The result**: raw category entropy gap is large, but count-matched entropy gap shrinks to 0.032 among users with at least five clicks and to about 0.010 among users with at least ten clicks. This pattern strengthens the measurement interpretation because the raw gap is not treated as entirely behavioral. The more stable claim shifts to residual concentration and JS mismatch.

### 12.10 Bootstrap Confidence Intervals

Bootstrap resampling repeatedly samples users or events with replacement and recomputes the statistic. It gives an empirical uncertainty interval without requiring a simple closed-form standard error.

The paper uses bootstrap intervals because the metrics are not simple independent coin flips. Entropy, JS divergence, and user-level gaps are aggregate statistics built from uneven user histories.

**Interpretation note**: bootstrapping asks, "if this observed user/event population were resampled many times, how much would the statistic vary?" It turns a dashboard number into a measurement with uncertainty.

### 12.11 AUC and AUPRC in the Diagnostic Model

AUC measures ranking ability: if we randomly pick one high-divergence user and one lower-divergence user, how often does the model score the high-divergence user higher? AUC 0.5 is random ranking. AUC 1.0 is perfect ranking.

AUPRC focuses on precision and recall for the positive class. It is useful when the positive class is imbalanced or when the analysis focuses on about how concentrated correct positive predictions are near the top.

**The result**: full weighted model AUC is 0.859 in same-window diagnostics, but temporal AUC is 0.731 and dense-history AUC is around 0.70. The appropriate interpretation is not "the model is a production classifier." It is: "divergence is structured enough to audit, but the signal is bounded under harder validation."

## 13. How the Numbers Support the Paper's Claims

### Claim A: Preference Is Informative

Evidence:

- 77.22% top-category match
- category cosine 0.452

Meaning:

> The profile often points toward the user's main clicked category.

But:

- primary mean Jaccard 0.2283 (nonempty-set sensitivity 0.2347)
- publisher cosine 0.080

Meaning:

> Preference does not capture the full breadth of actual consumption, especially at the publisher/source level.

### Claim B: Logged Exposure Is Signal-Bearing

Evidence:

- same-day hit 11.29%
- date-matched random 9.13%
- top-5 lift 1.47x
- popularity-aware baselines are lower than the logged recommendation hit

Meaning:

> Recommendation logs are not irrelevant. They carry measurable signal.

But:

> They are only one logged layer in a multi-surface app. They should not be interpreted as total exposure or CTR.

### Claim C: Consumption Is More Concentrated Than Exposure

Evidence:

- exposure category entropy 0.8352 vs click category entropy 0.5401
- exposure top-category share 0.3704 vs click top-category share 0.6928
- count-matched HHI gap 0.082
- count-matched top-share gap 0.069
- count-matched JS divergence 0.471

Meaning:

> The platform can log broad recommendation exposure while observed clicks remain concentrated.

But:

> Raw entropy alone is not the robust claim because count matching shows that observation counts explain part of the raw gap.

### Claim D: Divergence Is Structured but Bounded

Evidence:

- weighted profile-state improves same-window AUC from 0.784 to 0.859
- temporal AUC drops to 0.731
- dense-history AUC drops to about 0.70

Meaning:

> High-divergence users are not random noise. Observable profile and behavior features contain signal.

But:

> The model is not a deployment tool. It is a diagnostic audit instrument.

## 14. Suggested Review Flow

For a project meeting or seminar, use this order:

1. Start with the pipeline assumption: preference -> exposure -> click.
2. Explain why real mobile news apps break this assumption through multi-surface consumption.
3. Define P, E, S, and C.
4. Explain RQ1 as "does stated preference match consumption?"
5. Explain RQ2 as "can clicked items be traced to logged recommendations?"
6. Explain RQ3 as "does exposure diversity become click diversity?"
7. Explain count matching before showing any strong diversity conclusion.
8. Explain RQ4 as diagnostic modeling, not prediction competition.
9. End with the reusable lesson: do not collapse the layers.

The most important sentence to repeat is:

> Preferences, logged exposure, and clicks are all meaningful signals, but none can safely stand in for the others.

## 15. One-Page Lecture Summary

This paper audits a deployed personalized news app by separating four traces: user preferences, logged recommendation exposure, app surface pathways, and click consumption. The central idea is that these traces are related but not interchangeable. Stated preferences capture the user's dominant interests but not the full breadth of consumption. Logged recommendation exposure is above random and popularity baselines, but it explains only part of clicks because users enter articles through many app surfaces. Exposure looks more diverse than consumption in raw logs, but count matching shows that some of the raw entropy gap comes from having more exposure observations than click observations. Even after this correction, click consumption remains more concentrated and distributionally different. Finally, weighted profile-state and behavior features can identify high-divergence users to some extent, but temporal and dense-history checks show that this is a bounded audit signal, not a production prediction model. The paper's main contribution is not a new recommender algorithm. It is a reusable measurement discipline: do not collapse preference, exposure, surface, and consumption into one preference signal.

## 16. Extended Classroom Walkthrough

This section gives an extended explanation. It is useful when explaining the paper to someone who understands recommendation systems but has not yet internalized the PEC framing.

### Step 1: Start With the Wrong Mental Model

Begin with the common pipeline:

\[
\text{preference} \rightarrow \text{recommendation exposure} \rightarrow \text{click}.
\]

This pipeline is not completely false. It is useful as a product story and as a simplified evaluation story. But the paper argues that it becomes dangerous when the three traces are treated as interchangeable. A stated preference is not the same as exposure. Logged exposure is not the same as all visible opportunities. A click is not the same as full attention or durable preference.

The interpretation point is:

> The problem is not that preference, exposure, and clicks are unrelated. The problem is that they are too easily collapsed into one another.

### Step 2: Explain Why Mobile News Is Different From a Clean Ranking Task

In a clean ranking task, a model scores candidate items and the user chooses from the displayed list. In a mobile news app, a user can reach articles through many paths. Some paths may be algorithmic, some editorial, some habitual, and some triggered by breaking-news salience.

This is why the paper adds surface pathways. Surface is not a cosmetic UI variable. It is a measurement layer. If most clicks arrive through headline modules, a recommendation-list audit alone will miss a large part of observed consumption. If category-tab clicks have higher same-day traceability than headline clicks, surfaces are not merely where clicks happen; they condition the relationship between exposure and consumption.

### Step 3: Teach the Three Main Non-Substitution Errors

The paper is built around three errors that platforms and researchers can make.

**Error 1: Clicks as preferences.** If every click is treated as preference, the platform may interpret curiosity, breaking news, UI salience, or accidental attention as stable user interest.

**Error 2: Recommendation logs as total exposure.** If logged recommendation lists are treated as all exposure, the analysis ignores headline modules, category tabs, newsroom pathways, search, notifications, and article-detail continuations.

**Error 3: Exposure diversity as consumption diversity.** If a platform says its recommendation list is diverse, that does not mean users actually consume diverse content. Diversity can be made available without becoming attended diversity.

PEC is a way to prevent these three errors.

### Step 4: Explain Why RQ1 Is Not a Simple "Profile Accuracy" Test

RQ1 does not ask whether the user profile is correct or wrong. It asks what kind of signal the profile contains.

The results are intentionally mixed:

- top-category match is high enough to show that stated preferences are meaningful;
- Jaccard is low enough to show that preference sets do not capture consumption breadth;
- weighted cosine is stronger than raw set overlap, showing that profile-state distributions matter;
- source-level alignment is weak, showing that not all preference representations are equally informative.

The concise phrasing is:

> The profile captures orientation, not the full itinerary of attention.

### Step 5: Explain Why RQ2 Is a Traceability Test

RQ2 is often misunderstood. It is not asking "what percentage of recommendations were clicked?" It asks "what percentage of clicks can be traced back to logged recommendations?"

This inversion matters. If a user clicks 100 articles and only 11 are found in same-day recommendation logs, that does not mean the recommender converted 11% of impressions. It means 11% of observed clicks are traceable to the available logged recommendation layer.

The correct interpretation is:

> Logged recommendations are visible in click behavior, but click behavior is larger than the logged recommendation layer.

### Step 6: Explain Why RQ3 Is the Most Methodologically Subtle Result

RQ3 can easily be overclaimed. The raw result is attractive: exposure entropy is high and click entropy is lower. But a careful reading may ask whether exposure has more observations than clicks. The paper answers that question with count matching.

This is the key interpretation sequence:

1. Raw logs show exposure is broader than clicks.
2. But raw entropy is sensitive to observation count.
3. Count matching reduces the entropy gap sharply.
4. Therefore, the raw entropy gap is partly a measurement artifact.
5. However, concentration and JS mismatch remain.
6. Therefore, the robust finding is not raw entropy alone; it is residual concentration and distributional mismatch after count correction.

This is one of the paper's strongest moments because it shows methodological self-discipline. The paper does not simply keep the biggest-looking number. It narrows the claim to the part that survives a validity check.

### Step 7: Explain Why RQ4 Is Helpful but Not the Center

RQ4 adds a machine-learning diagnostic model. It helps the paper because it shows that divergence is not pure noise. But it can also create risk if overemphasized.

The safe interpretation is:

> The model is a diagnostic microscope, not the treatment.

Weighted profile-state features improve same-window AUC, but temporal and dense-history checks reduce performance. That pattern is exactly why the paper says "structured but bounded." The result is strong enough to show that divergence has observable structure, but not strong enough to justify production targeting or causal intervention.

### Step 8: End With the Reusable Protocol

The final lesson is not tied to one app's exact numbers. The reusable contribution is a protocol:

1. separate preference, exposure, surface, and consumption traces;
2. compute relation-specific metrics instead of one global preference metric;
3. test obvious measurement artifacts such as sparse clicks and popularity;
4. pair every empirical claim with an observability boundary.

That is the PEC audit.

## 17. Glossary of Method Terms in This Paper

**Alignment** means that two layers point in similar directions. In this paper, preference-consumption alignment means stated or weighted preferences resemble observed click consumption.

**Traceability** means that a clicked item can be located inside an available logged exposure record. It does not mean the exposure caused the click.

**Diversity shift** means the relationship between diversity made available in logged exposure and diversity observed in click consumption.

**Concentration** means that consumption or exposure is dominated by a small number of categories or publishers. Top-share and HHI measure concentration.

**Distributional mismatch** means that two distributions have different shapes, not merely different breadth. JS divergence measures this.

**Count matching** means comparing exposure and clicks after equalizing the number of observations, so that a diversity gap is not inflated simply because exposure has more items.

**Bounded diagnostic model** means a model used to test whether a phenomenon is structured, while explicitly limiting the interpretation so it is not treated as a deployable predictor or causal model.

**Audit-eligible cohort** means the subset of users for whom the relevant metrics are stable enough to interpret. It is a measurement-validity filter, not a claim that other users do not matter.

**Observability boundary** means the limit of what the logs can support. For example, logged exposure is not total exposure, clicks are not complete attention, and profile snapshots are not edit histories.

## 18. What to Emphasize in a Defense

In a short discussion, emphasize these four bounded claims:

1. **Preference is meaningful but incomplete.** The top category often appears in stated preferences, but Jaccard and publisher alignment show limited breadth.
2. **Recommendation exposure is signal-bearing but partial.** Same-day hit and top-k lift exceed baselines, but clicks come from multiple surfaces.
3. **Diversity is layer-dependent.** Raw exposure is broader, but count matching shows part of the entropy gap is a measurement effect; concentration and JS mismatch remain.
4. **Divergence is structured but bounded.** Weighted profile-state helps diagnostic modeling, but temporal and dense-history checks prevent overclaiming.

The safest final sentence is:

> The paper is strongest when read as a measurement audit: it does not ask whether one signal wins, but whether the platform is justified in treating different signals as the same thing.
