const form = document.querySelector('#generator-form');
const shell = document.querySelector('#episode-shell');
const loader = document.querySelector('#loading-panel');
const errorPanel = document.querySelector('#error-panel');
const scenarioSelect = document.querySelector('#scenario');
let currentEpisode = null;

const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
const niceDate = (value, options = {}) => new Intl.DateTimeFormat('en-GB', {day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit', timeZone:'UTC', ...options}).format(new Date(value));
const titleCase = value => value.replaceAll('-', ' ').replace(/\b\w/g, c => c.toUpperCase());

function setTrack(track) {
  document.querySelectorAll('.track-card').forEach(card => card.classList.toggle('selected', card.querySelector('input').value === track));
  [...scenarioSelect.options].forEach(option => {
    if (option.value !== 'surprise') option.hidden = option.dataset.track !== track;
  });
  const selected = scenarioSelect.selectedOptions[0];
  if (selected?.hidden) scenarioSelect.value = 'surprise';
}

document.querySelectorAll('input[name="track"]').forEach(input => input.addEventListener('change', () => setTrack(input.value)));
document.querySelector('#randomise').addEventListener('click', () => { document.querySelector('#seed').value = Math.floor(Math.random() * 999999); });
document.querySelector('#run-demo').addEventListener('click', () => {
  document.querySelector('input[value="general-surgery"]').click();
  scenarioSelect.value = 'acute-appendicitis';
  document.querySelector('#seed').value = 2026;
  document.querySelector('#studio').scrollIntoView();
  setTimeout(() => form.requestSubmit(), 450);
});
document.querySelector('#retry').addEventListener('click', () => form.requestSubmit());

function resolvedScenario() {
  if (scenarioSelect.value !== 'surprise') return scenarioSelect.value;
  const track = document.querySelector('input[name="track"]:checked').value;
  const choices = window.SCENARIOS.filter(item => item.track === track);
  const seed = Number(document.querySelector('#seed').value);
  return choices[seed % choices.length].id;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  shell.hidden = true;
  errorPanel.hidden = true;
  loader.hidden = false;
  const stages = [
    ['Applying clinical constraints', 'Building a coherent chronology and document set…'],
    ['Mapping traceable classifications', 'Resolving each code to supporting passages…'],
    ['Running quality gates', 'Checking schema, provenance and evidence coverage…'],
  ];
  let stage = 0;
  const stageTimer = setInterval(() => {
    const item = stages[Math.min(stage++, stages.length - 1)];
    document.querySelector('#loading-title').textContent = item[0];
    document.querySelector('#loading-copy').textContent = item[1];
  }, 380);
  try {
    const response = await fetch('/api/episodes', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({scenario_id: resolvedScenario(), seed: Number(document.querySelector('#seed').value)}),
    });
    if (!response.ok) throw new Error((await response.json()).detail || 'Generation failed');
    currentEpisode = await response.json();
    await new Promise(resolve => setTimeout(resolve, 850));
    renderEpisode(currentEpisode);
    loader.hidden = true;
    shell.hidden = false;
    shell.scrollIntoView({behavior:'smooth', block:'start'});
  } catch (error) {
    loader.hidden = true;
    errorPanel.hidden = false;
    document.querySelector('#error-copy').textContent = error.message;
  } finally { clearInterval(stageTimer); }
});

function renderEpisode(episode) {
  const meta = episode.metadata;
  const patient = episode.patient;
  const scenario = window.SCENARIOS.find(item => item.id === meta.scenario_id);
  document.querySelector('#episode-id').textContent = meta.episode_id;
  document.querySelector('#patient-name').textContent = patient.display_name;
  document.querySelector('#patient-avatar').textContent = patient.display_name.split(' ').pop()[0];
  document.querySelector('#track-label').textContent = titleCase(meta.track);
  document.querySelector('#patient-meta').textContent = [patient.age, patient.sex, patient.gestational_age_weeks ? `${patient.gestational_age_weeks} weeks` : null, patient.birth_weight_grams ? `${patient.birth_weight_grams} g` : null].filter(Boolean).join(' · ');
  document.querySelector('#scenario-title').textContent = scenario.title;
  document.querySelector('#encounter-dates').textContent = `${niceDate(episode.encounter.admission_at)} — ${niceDate(episode.encounter.discharge_at)}`;
  document.querySelector('#encounter-summary').textContent = episode.encounter_summary;
  document.querySelector('#procedure-note').textContent = episode.procedure_note;
  document.querySelector('#safety-notice').textContent = episode.safety_notice;
  document.querySelector('#download-link').href = `/api/episodes/${encodeURIComponent(meta.episode_id)}/download`;
  document.querySelector('#code-count').textContent = episode.codes.length;

  document.querySelector('#quality-grid').innerHTML = [
    ['✓', 'Schema valid', 'Pydantic + JSON Schema'],
    [`${episode.validation.evidence_coverage_percent}%`, 'Evidence coverage', `${episode.codes.length} classifications traced`],
    ['#', `Seed ${meta.seed}`, 'Reproducible generation'],
    ['2', 'Current standards', 'ICD-10 · OPCS-4'],
  ].map(([icon,title,detail]) => `<div class="quality-metric"><span class="metric-icon">${escapeHtml(icon)}</span><div><strong>${escapeHtml(title)}</strong><small>${escapeHtml(detail)}</small></div></div>`).join('');

  document.querySelector('#documents').innerHTML = episode.documents.map(doc => `
    <article class="document-card">
      <header><div><span>${escapeHtml(doc.document_type)}</span><h4>${escapeHtml(doc.title)}</h4></div><small>${escapeHtml(niceDate(doc.authored_at))} · ${escapeHtml(doc.author_role)}</small></header>
      <div class="passages">${doc.passages.map(p => `<p class="passage" id="passage-${escapeHtml(p.id)}" data-passage-id="${escapeHtml(p.id)}">${escapeHtml(p.text)}</p>`).join('')}</div>
    </article>`).join('');

  document.querySelector('#codes').innerHTML = episode.codes.map((code, index) => `
    <button class="code-card" type="button" data-code-index="${index}">
      <span class="code-system">${escapeHtml(code.system)}</span>
      <span class="code-main"><strong>${escapeHtml(code.code)}</strong><span>${escapeHtml(code.display)}</span><small>${escapeHtml(code.version)}</small></span>
      <span class="evidence-count">${code.evidence_passage_ids.length} link${code.evidence_passage_ids.length === 1 ? '' : 's'}</span>
    </button>`).join('');
  document.querySelectorAll('.code-card').forEach(button => button.addEventListener('click', () => highlightEvidence(Number(button.dataset.codeIndex), button)));

  document.querySelector('#timeline').innerHTML = episode.timeline.map(item => `<article class="timeline-item"><time>${escapeHtml(niceDate(item.occurred_at))}</time><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.detail)}</p></article>`).join('');
  document.querySelector('#quality-detail').innerHTML = episode.validation.checks.map(item => `<article class="check-card"><span>✓</span><div><strong>${escapeHtml(item.name)}</strong><p>${escapeHtml(item.message)}</p></div></article>`).join('');
  selectView('dossier');
}

function highlightEvidence(index, button) {
  document.querySelectorAll('.passage').forEach(item => item.classList.remove('highlight'));
  document.querySelectorAll('.code-card').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  const evidenceIds = currentEpisode.codes[index].evidence_passage_ids;
  evidenceIds.forEach(id => document.querySelector(`[data-passage-id="${CSS.escape(id)}"]`)?.classList.add('highlight'));
  document.querySelector(`[data-passage-id="${CSS.escape(evidenceIds[0])}"]`)?.scrollIntoView({behavior:'smooth', block:'center'});
}

function selectView(view) {
  document.querySelectorAll('.episode-tabs button').forEach(button => button.classList.toggle('active', button.dataset.view === view));
  document.querySelectorAll('.episode-view').forEach(panel => panel.classList.toggle('active', panel.id === `view-${view}`));
}
document.querySelectorAll('.episode-tabs button').forEach(button => button.addEventListener('click', () => selectView(button.dataset.view)));
document.querySelector('#copy-id').addEventListener('click', async event => {
  if (!currentEpisode) return;
  await navigator.clipboard.writeText(currentEpisode.metadata.episode_id);
  event.currentTarget.textContent = 'Copied ✓';
  setTimeout(() => { event.currentTarget.textContent = 'Copy ID'; }, 1200);
});
