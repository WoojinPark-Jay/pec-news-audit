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

const claims = {
  logged: { status: 'Supported', className: 'supported', title: 'Directly observed in E', copy: 'The retained recommendation log can establish list membership and recorded rank for that list. It does not establish visual attention.', chips: ['E'] },
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
