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

document.querySelectorAll('[data-scenario]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-scenario]').forEach((item) => item.classList.toggle('active', item === button));
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
}
preferenceInputs.forEach((input) => input.addEventListener('input', updatePreference));
updatePreference();

const traceChecks = [...document.querySelectorAll('#click-table input[type="checkbox"]')];
function updateTraceability() {
  const matched = traceChecks.filter((box) => box.checked).length;
  const rate = matched / traceChecks.length * 100;
  document.querySelector('#trace-rate').textContent = `${rate.toFixed(2)}%`;
  document.querySelector('#trace-count').textContent = `${matched} of ${traceChecks.length}`;
  document.querySelector('#trace-meter').style.width = `${rate}%`;
}
traceChecks.forEach((box) => box.addEventListener('change', updateTraceability));

const categoryColors = ['#31363a', '#557087', '#788b76', '#a48568'];
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
function drawBars(target, categories, probabilities) {
  const label = target.querySelector(':scope > span').outerHTML;
  target.innerHTML = label + categories.map((category, index) => `
    <div class="bar-row"><b>${category}</b><div class="bar-track"><i style="width:${(probabilities[index] * 100).toFixed(1)}%;background:${categoryColors[index]}"></i></div><em>${(probabilities[index] * 100).toFixed(1)}%</em></div>
  `).join('');
}
function updateMetrics() {
  metricInputs.forEach((input) => { input.nextElementSibling.value = input.value; });
  const categories = [...new Set(metricInputs.map((input) => input.dataset.category))];
  const exposure = categories.map((category) => Number(metricInputs.find((input) => input.dataset.layer === 'exposure' && input.dataset.category === category).value));
  const clicks = categories.map((category) => Number(metricInputs.find((input) => input.dataset.layer === 'clicks' && input.dataset.category === category).value));
  const p = distribution(exposure); const q = distribution(clicks);
  drawBars(document.querySelector('#exposure-bars'), categories, p);
  drawBars(document.querySelector('#click-bars'), categories, q);
  const expEntropy = entropy(p); const clickEntropy = entropy(q); const gap = hhi(q) - hhi(p); const js = jsDivergence(p, q);
  document.querySelector('#exp-entropy').textContent = expEntropy.toFixed(3);
  document.querySelector('#click-entropy').textContent = clickEntropy.toFixed(3);
  document.querySelector('#hhi-gap').textContent = `${gap >= 0 ? '+' : '−'}${Math.abs(gap).toFixed(3)}`;
  document.querySelector('#js-divergence').textContent = js.toFixed(3);
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
  document.querySelectorAll('[data-evidence]').forEach((item) => item.classList.toggle('active', item === button));
  evidenceRenderers[button.dataset.evidence]();
}));
renderRQ1();

const claims = {
  logged: { status: 'Supported', className: 'supported', title: 'Directly observed in E', copy: 'The retained recommendation log can establish list membership and recorded rank for that list. It does not establish visual attention.', chips: ['E'] },
  profile: { status: 'Bounded', className: 'bounded', title: 'P records stated preference, not total interest', copy: 'The stored profile supports a claim about categories the user explicitly selected or weighted. It can miss latent, changing, or context-specific interests revealed in later clicks.', chips: ['P','C'] },
  seen: { status: 'Unsupported', className: 'unsupported', title: 'Attention is not logged', copy: 'A list record is a system-side trace. Without a verified impression or attention measure, it cannot establish that the user saw the item.', chips: ['E','?'] },
  clicked: { status: 'Supported', className: 'supported', title: 'Directly observed in C', copy: 'A click event supports the statement that the user clicked. It does not by itself measure reading depth or satisfaction.', chips: ['C'] },
  read: { status: 'Unsupported', className: 'unsupported', title: 'Reading depth is outside C', copy: 'A click is an entry event. Dwell time, scrolling, completion, and comprehension are not available in this audit.', chips: ['C','?'] },
  caused: { status: 'Unsupported', className: 'unsupported', title: 'Co-occurrence is not causation', copy: 'Finding a click in a same-day list supports traceability. It does not identify the counterfactual effect of the recommendation.', chips: ['E','C','?'] },
  diverse: { status: 'Bounded', className: 'bounded', title: 'Valid only for the logged layer', copy: 'Category diversity can be computed for retained recommendation items. The claim must name the eligible list, denominator, metric, and time window.', chips: ['E'] }
};
document.querySelectorAll('[data-claim]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-claim]').forEach((item) => item.classList.toggle('active', item === button));
    const claim = claims[button.dataset.claim];
    const status = document.querySelector('#claim-status');
    status.textContent = claim.status; status.className = `status ${claim.className}`;
    document.querySelector('#claim-title').textContent = claim.title;
    document.querySelector('#claim-copy').textContent = claim.copy;
    document.querySelector('#evidence-chips').innerHTML = claim.chips.map((chip) => `<b>${chip}</b>`).join('');
  });
});

const themeToggle = document.querySelector('#theme-toggle');
themeToggle.addEventListener('click', () => {
  const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  localStorage.setItem('pec-theme', next);
});
