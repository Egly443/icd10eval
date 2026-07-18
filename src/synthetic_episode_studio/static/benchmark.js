const report = window.EPICODE_REPORT;
const body = document.querySelector('#leaderboard-body');
const awaiting = document.querySelector('#awaiting');
const status = document.querySelector('#run-status');

const modelLabel = model => model === 'gpt-5.6-sol' ? 'GPT-5.6 Sol' : model === 'gpt-5.6-luna' ? 'GPT-5.6 Luna' : model;
const modelTier = (model, effort) => model.includes('sol') ? [`Frontier model · ${effort} reasoning`, 'sol'] : [`Cost-sensitive model · ${effort} reasoning`, 'luna'];
const metric = (value, suffix = '%') => value === undefined ? '<span class="pending">—</span>' : `${value}${suffix}`;

function render() {
  const runByModel = Object.fromEntries((report.runs || []).map(run => [run.model, run]));
  const ranked = [...(report.models || [])].sort((a, b) => (runByModel[b]?.summary.resolved_percent ?? -1) - (runByModel[a]?.summary.resolved_percent ?? -1));
  const ranks = ranked.map((model, index) => {
    if (!runByModel[model]) return '–';
    const score = runByModel[model].summary.resolved_percent;
    const earlierBetter = ranked.slice(0, index).filter(other => runByModel[other].summary.resolved_percent > score).length;
    return earlierBetter + 1;
  });
  body.innerHTML = ranked.map((model, index) => {
    const run = runByModel[model];
    const summary = run?.summary || {};
    const [tier, colour] = modelTier(model, run?.reasoning_effort || 'low');
    return `<tr>
      <td><span class="rank">${ranks[index]}</span></td>
      <td><div class="model"><i class="${colour}"></i><span><b>${modelLabel(model)}</b><small>${tier} · ${model}</small></span></div></td>
      <td class="hero-metric">${run ? `<b>${summary.resolved}/${summary.total}</b><span>${summary.resolved_percent}%</span>` : '<span class="pending">Awaiting run</span>'}</td>
      <td>${metric(summary.code_micro_f1)}</td><td>${metric(summary.evidence_micro_f1)}</td>
      <td>${metric(summary.abstention_trap_resolved_percent)}</td><td>${metric(summary.hallucination_percent)}</td><td>${metric(summary.average_latency_ms, ' ms')}</td>
    </tr>`;
  }).join('');
  const complete = Boolean(report.runs?.length);
  const summaries = (report.runs || []).map(run => run.summary || {});
  if (complete) {
    document.querySelector('#poster-resolved').textContent = `${Math.max(...summaries.map(item => item.resolved_percent ?? 0))}%`;
    document.querySelector('#poster-code').textContent = `${Math.max(...summaries.map(item => item.code_micro_f1 ?? 0))}%`;
    document.querySelector('#poster-evidence').textContent = `${Math.max(...summaries.map(item => item.evidence_micro_f1 ?? 0))}%`;
  }
  awaiting.hidden = complete;
  status.classList.toggle('complete', complete);
  status.querySelector('span').textContent = complete ? `Run completed · ${new Date(report.generated_at).toLocaleDateString('en-GB')}` : 'Awaiting first official run';
}

render();
