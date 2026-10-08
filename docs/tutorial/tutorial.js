const scenarios = {
  listed: {
    p: ['Climate', 'The stored profile assigns climate a high weight.'],
    e: ['Present · rank 3', 'The article appears in the retained same-day recommendation list.'],
    s: ['Home / feed', 'The click event records a feed entry pathway.'],
    c: ['Clicked', 'A click is observed. Reading depth is not.'],
    supported: 'This article is present in the retained list and later appears as a click event.',
    unsupported: 'The logs do not establish that the user visually attended to the list entry or read the article deeply.'
  },
  search: {
    p: ['Local news', 'The profile includes a modest local-news weight.'],
    e: ['Absent from list', 'The article is not found in the retained same-day recommendation list.'],
    s: ['Search', 'The click event records a search entry pathway.'],
    c: ['Clicked', 'A click is observed after the search pathway.'],
    supported: 'The click came through search and cannot be traced to the retained recommendation list.',
    unsupported: 'List absence does not prove that no other platform component displayed or suggested the article.'
  },
  noclick: {
    p: ['Technology', 'The stored profile assigns technology a high weight.'],
    e: ['Present · rank 2', 'The article appears near the top of the retained list.'],
    s: ['Unobserved', 'No click pathway is available for this item.'],
    c: ['No observed click', 'The item is not present in the click log for this query.'],
    supported: 'The article was recorded in the list and has no observed click in the available click log.',
    unsupported: 'The records do not establish whether the user saw, ignored, disliked, or read the item elsewhere.'
  }
};

const coreLenses = {
  alignment: {
    relation: 'P ↔ C',
    layers: ['p','c'],
    title: 'Does the stored profile align with later clicking?',
    copy: 'Compare dominant categories, active sets, and weighted distributions. Each statistic answers a different version of “alignment.”',
    methods: [
      ['argmax match', '1[argmax(P) = argmax(C)] · coarse dominant-category recovery.'],
      ['Jaccard J', 'J = |P⁺ ∩ C⁺| / |P⁺ ∪ C⁺| · active-set overlap; profile weights are ignored.'],
      ['cosine A', 'A = (P · C) / (‖P‖₂‖C‖₂) · directional similarity between weighted vectors.'],
      ['chance-based nulls', 'Compare observed alignment with size-matched random profiles to avoid treating base rates as personalization.']
    ],
    boundary: 'Agreement between P and C does not establish satisfaction, total interest, or causal personalization success.'
  },
  traceability: {
    relation: 'E ↔ C',
    layers: ['e','c'],
    title: 'How much clicked activity can the retained list trace?',
    copy: 'Condition on comparable user-days, search for the clicked item in E, and compare the observed hit against plausible non-personalized expectations.',
    methods: [
      ['same-day hit', 'H = Σᵢ 1[i ∈ E(u, date(i))] / N · the share of comparable clicks found in the retained list.'],
      ['candidate baseline', 'Date-match each click to the available candidate pool before estimating expected overlap.'],
      ['Lift@k', 'Lift@k = H_logged@k / H_base@k · relative gain above a non-personalized expectation.'],
      ['clustered bootstrap CI', 'Resample users, rather than individual clicks, to preserve within-user dependence.']
    ],
    boundary: 'A hit supports list–click co-occurrence, not visual attention or causation. A miss does not establish that no exposure occurred elsewhere.'
  },
  diversity: {
    relation: 'E ↔ C',
    layers: ['e','c'],
    title: 'Do the two layers differ in breadth, concentration, or composition?',
    copy: 'Normalize each distribution separately, control the event-count imbalance, and report multiple metrics because no single score captures every kind of gap.',
    methods: [
      ['normalized entropy', 'Hₙ(X) = −Σ pₓ log(pₓ) / log|X⁺| · evenness over the active support.'],
      ['HHI', 'HHI(X) = Σ pₓ² · concentration rises as mass collapses onto fewer categories.'],
      ['top share', 'TopShare(X) = maxₓ pₓ · the dominant category’s probability mass.'],
      ['JS divergence', 'JS(P,Q) compares category composition and stays finite on unequal supports.'],
      ['count matching', 'Sample |E′ᵤ| = |Cᵤ| before comparison so list volume does not mechanically inflate diversity.']
    ],
    boundary: 'Logged-list diversity describes retained E. It does not automatically describe what the user noticed, consumed, or read deeply.'
  },
  surface: {
    relation: 'S → C',
    layers: ['s','c'],
    title: 'Which interface pathway produced the recorded click entry?',
    copy: 'Use surface metadata to distinguish home/feed, search, category, headline, newsroom, and article-detail pathways before interpreting list coverage.',
    methods: [
      ['surface shares', 'Share(s) = N_click,s / N_click · composition of recorded click-entry pathways.'],
      ['pathway stratification', 'Recompute audit quantities within each surface instead of pooling distinct entry mechanisms.'],
      ['cohort sensitivity', 'Repeat the comparison under explicit activity and observability thresholds.'],
      ['traceable vs. other routes', 'Separate clicks found in retained E from clicks entering through other recorded pathways.']
    ],
    boundary: 'S records the click entry context available in the log. It does not reconstruct every screen view or preceding recommendation event.'
  }
};
function renderCoreMethod(lens, index) {
  const method = lens.methods[index];
  document.querySelectorAll('[data-core-method]').forEach((button) => {
    const active = Number(button.dataset.coreMethod) === index;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.querySelector('#core-method-name').textContent = method[0];
  document.querySelector('#core-method-detail').textContent = method[1];
}
function renderCoreLens(key) {
  const lens = coreLenses[key];
  document.querySelectorAll('[data-core-lens]').forEach((button) => {
    const active = button.dataset.coreLens === key;
    button.classList.toggle('active', active);
    button.setAttribute('aria-selected', String(active));
  });
  document.querySelector('#core-lens-relation').textContent = lens.relation;
  document.querySelector('#core-lens-title').textContent = lens.title;
  document.querySelector('#core-lens-copy').textContent = lens.copy;
  document.querySelectorAll('[data-core-layer]').forEach((layer) => layer.classList.toggle('is-related', lens.layers.includes(layer.dataset.coreLayer)));
  document.querySelector('#core-lens-methods').innerHTML = lens.methods.map((method, index) => `<button class="${index === 0 ? 'active' : ''}" data-core-method="${index}" type="button">${method[0]}</button>`).join('');
  document.querySelectorAll('[data-core-method]').forEach((button) => {
    ['mouseenter', 'focus', 'click'].forEach((eventName) => button.addEventListener(eventName, () => renderCoreMethod(lens, Number(button.dataset.coreMethod))));
  });
  renderCoreMethod(lens, 0);
  document.querySelector('#core-lens-boundary').textContent = lens.boundary;
}
document.querySelectorAll('[data-core-lens]').forEach((button) => {
  ['focus', 'click'].forEach((eventName) => button.addEventListener(eventName, () => renderCoreLens(button.dataset.coreLens)));
});
renderCoreLens('alignment');

document.querySelectorAll('[data-scenario]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-scenario]').forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    const s = scenarios[button.dataset.scenario];
    ['p','e','s','c'].forEach((key) => {
      document.querySelector(`#journey-${key}-title`).textContent = s[key][0];
      document.querySelector(`#journey-${key}-copy`).textContent = s[key][1];
    });
    document.querySelector('#supported-observation').textContent = s.supported;
    document.querySelector('#unsupported-inference').textContent = s.unsupported;
  });
});

const preferenceInputs = [...document.querySelectorAll('[data-pref]')];
const preferenceCategories = ['Politics', 'Technology', 'Climate', 'Culture'];
function cosine(a, b) {
  const dot = a.reduce((sum, value, index) => sum + value * b[index], 0);
  const magnitudeA = Math.sqrt(a.reduce((sum, value) => sum + value * value, 0));
  const magnitudeB = Math.sqrt(b.reduce((sum, value) => sum + value * value, 0));
  return magnitudeA && magnitudeB ? dot / (magnitudeA * magnitudeB) : 0;
}
function updatePreference() {
  preferenceInputs.forEach((input) => { input.nextElementSibling.value = input.value; });
  const p = preferenceInputs.filter((input) => input.dataset.pref === 'p').map((input) => Number(input.value));
  const c = preferenceInputs.filter((input) => input.dataset.pref === 'c').map((input) => Number(input.value));
  const topIndex = (values) => values.reduce((best, value, index) => value > values[best] ? index : best, 0);
  const pTop = topIndex(p); const cTop = topIndex(c); const match = pTop === cTop && Math.max(...p) > 0 && Math.max(...c) > 0;
  const pSet = new Set(p.map((value, index) => value > 0 ? index : -1).filter((index) => index >= 0));
  const cSet = new Set(c.map((value, index) => value > 0 ? index : -1).filter((index) => index >= 0));
  const intersection = [...pSet].filter((index) => cSet.has(index)).length;
  const union = new Set([...pSet, ...cSet]).size;
  document.querySelector('#pref-top-match').textContent = match ? 'Yes' : 'No';
  document.querySelector('#pref-top-detail').textContent = `${preferenceCategories[pTop]} ${match ? '=' : '≠'} ${preferenceCategories[cTop]}`;
  document.querySelector('#pref-jaccard').textContent = (union ? intersection / union : 0).toFixed(3);
  document.querySelector('#pref-cosine').textContent = cosine(p, c).toFixed(3);
  document.querySelector('#pref-top-formula').textContent = `${preferenceCategories[pTop]} ${match ? '=' : '≠'} ${preferenceCategories[cTop]} → ${match ? 'match' : 'no match'}`;
  document.querySelector('#pref-jaccard-formula').textContent = `${intersection} shared / ${union} active = ${(union ? intersection / union : 0).toFixed(3)}`;
  const dot = p.reduce((sum, value, index) => sum + value * c[index], 0);
  const pNorm = Math.sqrt(p.reduce((sum, value) => sum + value * value, 0));
  const cNorm = Math.sqrt(c.reduce((sum, value) => sum + value * value, 0));
  document.querySelector('#pref-cosine-formula').textContent = `${dot.toFixed(0)} / (${pNorm.toFixed(2)} × ${cNorm.toFixed(2)}) = ${cosine(p, c).toFixed(3)}`;
}
preferenceInputs.forEach((input) => input.addEventListener('input', updatePreference));
updatePreference();

const traceChecks = [...document.querySelectorAll('#click-table input[type="checkbox"]')];
function updateTraceability() {
  const matched = traceChecks.filter((box) => box.checked).length;
  const rate = matched / traceChecks.length * 100;
  const unmatched = traceChecks.length - matched;
  document.querySelector('#trace-rate').textContent = `${rate.toFixed(1)}%`;
  document.querySelector('#trace-numerator').textContent = matched;
  document.querySelector('#trace-denominator').textContent = traceChecks.length;
  document.querySelector('#trace-count').textContent = `${matched} matched click${matched === 1 ? '' : 's'}`;
  document.querySelector('#trace-reading').lastChild.textContent = ` support same-day list–click co-occurrence. The other ${unmatched} ${unmatched === 1 ? 'is' : 'are'} untraced by this retained list.`;
  document.querySelector('#trace-meter').style.width = `${rate}%`;
}
traceChecks.forEach((box) => box.addEventListener('change', updateTraceability));
updateTraceability();

const metricInputs = [...document.querySelectorAll('.slider-row input[type="range"]')];
const defaults = metricInputs.map((input) => Number(input.value));

function distribution(values) {
  const total = values.reduce((sum, value) => sum + value, 0);
  if (!total) return values.map(() => 0);
  return values.map((value) => value / total);
}
function entropy(probabilities) {
  const active = probabilities.filter((p) => p > 0);
  if (active.length <= 1) return 0;
  return -active.reduce((sum, p) => sum + p * Math.log(p), 0) / Math.log(active.length);
}
function hhi(probabilities) { return probabilities.reduce((sum, p) => sum + p * p, 0); }
function jsDivergence(p, q) {
  const m = p.map((value, index) => (value + q[index]) / 2);
  const kl = (a, b) => a.reduce((sum, value, index) => value > 0 ? sum + value * Math.log2(value / b[index]) : sum, 0);
  return (kl(p, m) + kl(q, m)) / 2;
}
function drawDistributionChart(exposure, clicks) {
  const x = [55, 195, 335, 475];
  const baseline = 111;
  const y = (value) => baseline - Math.min(.75, value) / .75 * 96;
  const pointPairs = (values) => values.map((value, index) => [x[index], y(value)]);
  const smooth = (values) => {
    const points = pointPairs(values);
    let d = `M ${points[0][0]} ${points[0][1].toFixed(1)}`;
    for (let i = 0; i < points.length - 1; i += 1) {
      const previous = points[i - 1] || points[i];
      const current = points[i];
      const next = points[i + 1];
      const after = points[i + 2] || next;
      const c1x = current[0] + (next[0] - previous[0]) / 6;
      const c1y = current[1] + (next[1] - previous[1]) / 6;
      const c2x = next[0] - (after[0] - current[0]) / 6;
      const c2y = next[1] - (after[1] - current[1]) / 6;
      d += ` C ${c1x.toFixed(1)} ${c1y.toFixed(1)}, ${c2x.toFixed(1)} ${c2y.toFixed(1)}, ${next[0]} ${next[1].toFixed(1)}`;
    }
    return d;
  };
  const exposurePath = smooth(exposure); const clickPath = smooth(clicks);
  document.querySelector('#exposure-line').setAttribute('d', exposurePath);
  document.querySelector('#click-line').setAttribute('d', clickPath);
  document.querySelector('#exposure-area').setAttribute('d', `${exposurePath} L ${x[x.length - 1]} ${baseline} L ${x[0]} ${baseline} Z`);
  document.querySelector('#click-area').setAttribute('d', `${clickPath} L ${x[x.length - 1]} ${baseline} L ${x[0]} ${baseline} Z`);
  const circles = (values, className) => values.map((value, index) => `<circle class="distribution-point ${className}" cx="${x[index]}" cy="${y(value).toFixed(1)}" r="5"><title>${preferenceCategories[index]}: ${(value * 100).toFixed(1)}%</title></circle>`).join('');
  document.querySelector('#exposure-points').innerHTML = circles(exposure, 'exposure');
  document.querySelector('#click-points').innerHTML = circles(clicks, 'clicks');
}
function updateMetrics() {
  metricInputs.forEach((input) => { input.nextElementSibling.value = input.value; });
  const categories = [...new Set(metricInputs.map((input) => input.dataset.category))];
  const exposure = categories.map((category) => Number(metricInputs.find((input) => input.dataset.layer === 'exposure' && input.dataset.category === category).value));
  const clicks = categories.map((category) => Number(metricInputs.find((input) => input.dataset.layer === 'clicks' && input.dataset.category === category).value));
  const p = distribution(exposure); const q = distribution(clicks);
  drawDistributionChart(p, q);
  const expEntropy = entropy(p); const clickEntropy = entropy(q); const gap = hhi(q) - hhi(p); const js = jsDivergence(p, q);
  document.querySelector('#exp-entropy').textContent = expEntropy.toFixed(3);
  document.querySelector('#click-entropy').textContent = clickEntropy.toFixed(3);
  const effective = (normalizedEntropy, probabilities) => {
    const active = probabilities.filter((value) => value > 0).length;
    return active > 1 ? Math.exp(normalizedEntropy * Math.log(active)) : active;
  };
  document.querySelector('#exp-entropy-gauge').style.width = `${expEntropy * 100}%`;
  document.querySelector('#click-entropy-gauge').style.width = `${clickEntropy * 100}%`;
  document.querySelector('#exp-effective').textContent = `${expEntropy.toFixed(3)} · ${effective(expEntropy, p).toFixed(2)} effective categories`;
  document.querySelector('#click-effective').textContent = `${clickEntropy.toFixed(3)} · ${effective(clickEntropy, q).toFixed(2)} effective categories`;
  document.querySelector('#hhi-gap').textContent = `${gap >= 0 ? '+' : '−'}${Math.abs(gap).toFixed(3)}`;
  document.querySelector('#js-divergence').textContent = js.toFixed(3);
  document.querySelector('#entropy-formula').textContent = `Exposure ${expEntropy.toFixed(3)} · Clicks ${clickEntropy.toFixed(3)} · Δ ${(clickEntropy-expEntropy >= 0 ? '+' : '−')}${Math.abs(clickEntropy-expEntropy).toFixed(3)}`;
  document.querySelector('#hhi-formula').textContent = `${hhi(q).toFixed(3)} − ${hhi(p).toFixed(3)} = ${gap >= 0 ? '+' : '−'}${Math.abs(gap).toFixed(3)}`;
  document.querySelector('#js-formula').textContent = `M = (Exposure + Clicks) / 2 → ${js.toFixed(3)}`;
  const reading = gap > .015 ? 'The current click distribution is more concentrated than the logged exposure distribution.' : gap < -.015 ? 'The current click distribution is less concentrated than the logged exposure distribution.' : 'The two layers currently have similar concentration, although their category composition may still differ.';
  document.querySelector('#metric-reading').textContent = reading;
}
metricInputs.forEach((input) => input.addEventListener('input', updateMetrics));
document.querySelector('#reset-metrics').addEventListener('click', () => {
  metricInputs.forEach((input, index) => { input.value = defaults[index]; }); updateMetrics();
});
updateMetrics();

const rq2Points = {
  'Top 3': { observed: 3.28, baseline: 2.35, low: 1.53, high: 5.11 },
  'Top 5': { observed: 4.99, baseline: 3.48, low: 2.74, high: 7.43 },
  'Top 10': { observed: 7.76, baseline: 5.78, low: 4.34, high: 11.50 },
  'Top 20': { observed: 11.05, baseline: 8.96, low: 6.27, high: 16.20 },
  'All retained': { observed: 11.29, baseline: 9.13, low: 6.26, high: 16.70 }
};
const rq3Cohorts = {
  'All eligible': { n: 553, entropy: .219, hhi: .167, share: .162, js: .593 },
  '≥ 5 clicks': { n: 284, entropy: .032, hhi: .091, share: .077, js: .483 },
  'Audit eligible': { n: 251, entropy: .025, hhi: .082, share: .069, js: .471 },
  'Dense users': { n: 119, entropy: .000, hhi: .045, share: .039, js: .395 }
};
const rq4Conditions = {
  'Same-window': { auc: .859, note: 'The model is evaluated within the same observation window. This is descriptive discrimination, not future prediction.' },
  'Time split': { auc: .731, note: 'Training on earlier activity and testing on later activity lowers performance, showing temporal instability.' },
  '≥ 10 clicks': { auc: .707, note: 'Among denser users, the diagnostic remains above chance but is substantially weaker.' },
  '≥ 5 clicks': { auc: .698, note: 'Changing eligibility changes the user population and the diagnostic result.' },
  'Profile only': { auc: .696, note: 'Preference information alone carries signal, but leaves much of the observed behavior unexplained.' },
  'Upper bound': { auc: .896, note: 'The upper-bound specification includes direct alignment quantities and is shown as a diagnostic ceiling.' }
};
const evidencePanel = document.querySelector('#evidence-panel');
const resultRow = (label, value, max = 1, display = value.toFixed(3), color = 'var(--ink)') => `<div class="result-row"><b>${label}</b><div class="result-track"><i style="width:${Math.max(0, Math.min(100, value / max * 100))}%;background:${color}"></i></div><em>${display}</em></div>`;
function renderRQ1() {
  evidencePanel.innerHTML = `<div class="evidence-lead"><div><h3>Preference profiles recover the dominant category better than the full breadth of clicking.</h3><p>A top-category match is a coarse success: it can be high even when the profile omits many categories the user later explores. Set overlap and weighted similarity reveal that missing breadth.</p></div><div class="evidence-sample"><b>698 profile–click users</b>Aggregate user-level comparison</div></div>
  <div class="evidence-visuals"><div class="evidence-chart"><span>Top-category agreement</span><div class="stacked-result"><i style="width:77.2%">77.2% match</i><i style="width:22.8%">22.8%</i></div><p class="metric-definition"><b>Meaning:</b> the highest-weight profile category equals the most-clicked category. This does not require the rest of the category sets to agree.</p></div>
  <div class="evidence-chart"><span>Observed breadth versus stored profile</span>${resultRow('Clicked categories', 15, 76, '15', 'var(--c)')}${resultRow('Profile categories', 7, 76, '7', 'var(--p)')}${resultRow('Clicked publishers', 76, 76, '76', 'var(--c)')}${resultRow('Profile publishers', 10, 76, '10', 'var(--p)')}<p class="metric-definition">Distinct counts shown are medians. Click activity spans a much broader set of publishers than the stored profile.</p></div></div>
  <div class="evidence-takeaway"><b>How to read it</b>Mean category Jaccard is 0.228; mean cosine similarity is 0.452 for categories and 0.080 for publishers. Preference is informative, but it is a sparse and imperfect view of later consumption.</div>`;
}
function renderRQ2(selected = 'All retained') {
  const d = rq2Points[selected]; const scale = (value) => value / 18 * 100;
  evidencePanel.innerHTML = `<div class="evidence-lead"><div><h3>Observed list overlap is modest and only slightly above a candidate-pool expectation.</h3><p>A hit means a clicked article was found in the retained same-day recommendation list. A miss is bounded: the article may have been reached through another surface or an unretained recommendation event.</p></div><div class="evidence-sample"><b>${selected}</b>Observed rate with user-clustered 95% CI</div></div>
  <div class="evidence-controls">${Object.keys(rq2Points).map((key) => `<button class="${key === selected ? 'active' : ''}" data-rq2="${key}">${key}</button>`).join('')}</div>
  <div class="evidence-visuals"><div class="evidence-chart"><span>Observed hit and baseline</span><div class="dot-scale"><span class="dot-label" style="left:${scale(d.observed)}%">Observed ${d.observed.toFixed(2)}%</span><i class="ci-line" style="left:${scale(d.low)}%;width:${scale(d.high-d.low)}%"></i><i class="chart-dot" style="left:${scale(d.observed)}%"></i><i class="chart-dot baseline" style="left:${scale(d.baseline)}%"></i></div><p class="metric-definition"><b>Gray dot:</b> candidate-pool expectation ${d.baseline.toFixed(2)}%. Difference: <b>+${(d.observed-d.baseline).toFixed(2)} percentage points</b>.</p></div>
  <div class="evidence-chart"><span>Where clicks entered the app</span>${resultRow('Headline', 65.4, 100, '65.4%')}${resultRow('Category', 14.0, 100, '14.0%')}${resultRow('Home / feed', 9.3, 100, '9.3%')}${resultRow('Newsroom', 7.0, 100, '7.0%')}${resultRow('Article detail', 4.1, 100, '4.1%')}</div></div>
  <div class="evidence-takeaway"><b>How to read it</b>The retained recommendation list traces a real part of the journey, but interface pathways show that it is not the journey itself. Overlap supports traceability—not visual attention or causal attribution.</div>`;
  evidencePanel.querySelectorAll('[data-rq2]').forEach((button) => button.addEventListener('click', () => renderRQ2(button.dataset.rq2)));
}
function renderRQ3(selected = 'All eligible') {
  const d = rq3Cohorts[selected];
  evidencePanel.innerHTML = `<div class="evidence-lead"><div><h3>Diversity gaps shrink when exposure is count-matched to clicks and eligibility becomes stricter.</h3><p>Raw exposure contains many more items than clicks. Count matching removes that mechanical advantage before comparing entropy and concentration. Cohort filters then show how sparse users affect the aggregate result.</p></div><div class="evidence-sample"><b>${d.n} users</b>${selected} cohort</div></div>
  <div class="evidence-controls">${Object.keys(rq3Cohorts).map((key) => `<button class="${key === selected ? 'active' : ''}" data-rq3="${key}">${key}</button>`).join('')}</div>
  <div class="evidence-visuals"><div class="evidence-chart"><span>Count-matched gaps · clicks minus exposure</span>${resultRow('Entropy gap', d.entropy, .6, d.entropy.toFixed(3), 'var(--p)')}${resultRow('HHI gap', d.hhi, .6, `+${d.hhi.toFixed(3)}`, 'var(--s)')}${resultRow('Top-share gap', d.share, .6, `+${d.share.toFixed(3)}`, 'var(--c)')}${resultRow('JS divergence', d.js, .6, d.js.toFixed(3), 'var(--e)')}</div>
  <div class="evidence-chart"><span>Metric guide</span><p class="metric-definition"><b>Normalized entropy</b> rises as probability mass spreads across more active categories.</p><p class="metric-definition"><b>HHI</b> and <b>top share</b> rise as consumption becomes more concentrated.</p><p class="metric-definition"><b>JS divergence</b> measures composition mismatch even when two distributions have similar overall diversity.</p><p class="metric-definition"><b>Raw paper contrast:</b> click entropy was 0.30 lower and top-category share 0.32 higher than logged exposure before count matching.</p></div></div>
  <div class="evidence-takeaway"><b>How to read it</b>${selected === 'Dense users' ? 'For dense users, the count-matched entropy gap is nearly zero, while concentration and composition differences remain. One metric cannot summarize every form of mismatch.' : 'The conclusion depends on the comparison rule and eligible users. Report the denominator, sampling rule, and metric together.'}</div>`;
  evidencePanel.querySelectorAll('[data-rq3]').forEach((button) => button.addEventListener('click', () => renderRQ3(button.dataset.rq3)));
}
function renderRQ4(selected = 'Same-window') {
  const d = rq4Conditions[selected];
  evidencePanel.innerHTML = `<div class="evidence-lead"><div><h3>The diagnostic model separates profile–click mismatch, but performance changes across validation settings.</h3><p>AUC summarizes ranking discrimination between higher- and lower-gap users. It does not prove a causal mechanism, and same-window performance should not be read as prospective accuracy.</p></div><div class="evidence-sample"><b>AUC ${d.auc.toFixed(3)}</b>${selected} specification</div></div>
  <div class="evidence-controls">${Object.keys(rq4Conditions).map((key) => `<button class="${key === selected ? 'active' : ''}" data-rq4="${key}">${key}</button>`).join('')}</div>
  <div class="evidence-visuals"><div class="evidence-chart"><span>Diagnostic AUC · 0.50 is chance</span><div class="dot-scale auc"><span class="dot-label" style="left:${(d.auc-.5)/.4*100}%">${d.auc.toFixed(3)}</span><i class="chart-dot" style="left:${(d.auc-.5)/.4*100}%"></i></div><p class="metric-definition">Scale shown from 0.50 to 0.90. Switching the validation condition is part of the result, not a cosmetic robustness check.</p></div><div class="evidence-chart"><span>Interpretation</span><p class="metric-definition">${d.note}</p><p class="metric-definition"><b>Question answered:</b> can the available audit features discriminate users with different observed PEC-gap outcomes under this specification?</p><p class="metric-definition"><b>Question not answered:</b> which platform action caused a user’s preference–consumption mismatch?</p></div></div>
  <div class="evidence-takeaway"><b>How to read it</b>Model results are diagnostic evidence about structure in the logs. They do not convert observational traces into exposure, attention, or causal effects.</div>`;
  evidencePanel.querySelectorAll('[data-rq4]').forEach((button) => button.addEventListener('click', () => renderRQ4(button.dataset.rq4)));
}
const evidenceRenderers = { rq1: renderRQ1, rq2: renderRQ2, rq3: renderRQ3, rq4: renderRQ4 };
document.querySelectorAll('[data-evidence]').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('[data-evidence]').forEach((item) => {
    const active = item === button;
    item.classList.toggle('active', active);
    item.setAttribute('aria-selected', String(active));
  });
  evidenceRenderers[button.dataset.evidence]();
}));
renderRQ1();

const claims = {
  logged: { status: 'Supported', className: 'supported', title: 'Directly observed in E', copy: 'The retained recommendation log can establish list membership and recorded rank for that list. It does not establish visual attention.', evidence: 'Item identity, user-day list membership, and recorded rank in E.', boundary: 'A verified impression or any measure of visual attention.', rewrite: '“The article appears in the retained recommendation list.”', chips: ['E'] },
  absent: { status: 'Unsupported', className: 'unsupported', title: 'List absence is bounded missingness', copy: 'Not finding an article in one retained list does not establish that no recommender or interface surface presented it elsewhere.', evidence: 'The article is absent from the retained same-day list being queried.', boundary: 'Unretained recommendation events, other surfaces, and delivery context.', rewrite: '“This click is not traceable to the retained same-day list.”', chips: ['E','S','?'] },
  profile: { status: 'Bounded', className: 'bounded', title: 'P records stated preference, not total interest', copy: 'The stored profile supports a claim about categories the user explicitly selected or weighted. It can miss latent, changing, or context-specific interests revealed in later clicks.', evidence: 'The categories and weights stored in the observed preference profile.', boundary: 'Latent interests, changing intent, and interests expressed outside the profile.', rewrite: '“The profile records these stated or weighted preferences.”', chips: ['P','C'] },
  success: { status: 'Unsupported', className: 'unsupported', title: 'Agreement is descriptive, not a success criterion', copy: 'Profile–click similarity describes alignment between two observed traces. It does not show that personalization caused a better outcome.', evidence: 'Top-category match, Jaccard overlap, or cosine similarity between P and C.', boundary: 'User benefit, satisfaction, causal effect, and a counterfactual comparison.', rewrite: '“P and C agree by [metric] within the eligible cohort.”', chips: ['P','C','?'] },
  seen: { status: 'Unsupported', className: 'unsupported', title: 'Attention is not logged', copy: 'A list record is a system-side trace. Without a verified impression or attention measure, it cannot establish that the user saw the item.', evidence: 'The platform recorded the article in a recommendation list.', boundary: 'Viewport visibility, gaze, attention, or any verified impression event.', rewrite: '“The platform logged the article in the retained list.”', chips: ['E','?'] },
  clicked: { status: 'Supported', className: 'supported', title: 'Directly observed in C', copy: 'A click event supports the statement that the user clicked. It does not by itself measure reading depth or satisfaction.', evidence: 'An article-entry click event with its available timestamp and surface.', boundary: 'Dwell time, completion, comprehension, satisfaction, and downstream use.', rewrite: '“The user clicked the article through the recorded surface.”', chips: ['C'] },
  read: { status: 'Unsupported', className: 'unsupported', title: 'Reading depth is outside C', copy: 'A click is an entry event. Dwell time, scrolling, completion, and comprehension are not available in this audit.', evidence: 'The click log establishes entry into the article.', boundary: 'Time on page, scroll depth, completion, comprehension, and recall.', rewrite: '“The user clicked the article; subsequent reading depth is unobserved.”', chips: ['C','?'] },
  caused: { status: 'Unsupported', className: 'unsupported', title: 'Co-occurrence is not causation', copy: 'Finding a click in a same-day list supports traceability. It does not identify the counterfactual effect of the recommendation.', evidence: 'The same article occurs in retained E and later in C on the same day.', boundary: 'Randomized assignment or another credible counterfactual identification strategy.', rewrite: '“The click is traceable to an article in the retained same-day list.”', chips: ['E','C','?'] },
  diverse: { status: 'Bounded', className: 'bounded', title: 'Valid only for the logged layer', copy: 'Category diversity can be computed for retained recommendation items. The claim must name the eligible list, denominator, metric, and time window.', evidence: 'The category distribution of items stored in the retained recommendation log.', boundary: 'Verified attention, off-list exposure, and diversity of consumed or deeply read content.', rewrite: '“Retained list diversity is [value] by [metric] for [eligible cohort].”', chips: ['E'] }
};
document.querySelectorAll('[data-claim]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-claim]').forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    const claim = claims[button.dataset.claim];
    const status = document.querySelector('#claim-status');
    status.textContent = claim.status; status.className = `status ${claim.className}`;
    document.querySelector('#claim-title').textContent = claim.title;
    document.querySelector('#claim-copy').textContent = claim.copy;
    document.querySelector('#claim-evidence').textContent = claim.evidence;
    document.querySelector('#claim-boundary').textContent = claim.boundary;
    document.querySelector('#claim-rewrite').textContent = claim.rewrite;
    document.querySelector('#evidence-chips').innerHTML = claim.chips.map((chip) => `<b class="evidence-${chip === '?' ? 'unknown' : chip.toLowerCase()}">${chip}</b>`).join('');
  });
});

const themeToggle = document.querySelector('#theme-toggle');
const updateThemeLabel = () => themeToggle.setAttribute('aria-label', `Switch to ${document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'} theme`);
updateThemeLabel();
themeToggle.addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('pec-theme', next);
  updateThemeLabel();
});
