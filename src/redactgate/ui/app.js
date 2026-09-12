const form = document.querySelector('#upload-form');
const input = document.querySelector('#file-input');
const dropzone = document.querySelector('.dropzone');
const selected = document.querySelector('#selected-file');
const sanitizeButton = document.querySelector('#sanitize-button');
const results = document.querySelector('#results');
const output = document.querySelector('#sanitized-output');
const reportOutput = document.querySelector('#report-output');
const errorMessage = document.querySelector('#error-message');
let currentResult = null;

document.querySelector('#browse-button').addEventListener('click', () => input.click());
input.addEventListener('change', () => updateFile(input.files[0]));
['dragenter', 'dragover'].forEach(event => dropzone.addEventListener(event, e => { e.preventDefault(); dropzone.classList.add('dragging'); }));
['dragleave', 'drop'].forEach(event => dropzone.addEventListener(event, e => { e.preventDefault(); dropzone.classList.remove('dragging'); }));
dropzone.addEventListener('drop', e => { const file = e.dataTransfer.files[0]; if (file) { input.files = e.dataTransfer.files; updateFile(file); } });

function updateFile(file) {
  if (!file) return;
  selected.hidden = false;
  selected.textContent = `${file.name} · ${formatBytes(file.size)}`;
  sanitizeButton.disabled = false;
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  sanitizeButton.disabled = true;
  sanitizeButton.innerHTML = 'Scanning artifact <span>…</span>';
  errorMessage.hidden = true;
  const response = await fetch('/api/sanitize', { method: 'POST', body: new FormData(form) });
  const data = await response.json();
  sanitizeButton.innerHTML = 'Sanitize artifact <span>→</span>';
  sanitizeButton.disabled = false;
  if (!response.ok) { showError(data.error || 'The artifact could not be sanitized.'); return; }
  currentResult = data;
  renderResult(data);
  results.hidden = false;
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

function renderResult(data) {
  const report = data.report;
  const verification = report.verification;
  document.querySelector('#result-title').textContent = `${data.filename} is ready`;
  const status = document.querySelector('#result-status');
  status.textContent = report.status === 'PASS' ? '✓ VERIFIED SAFE TO RELEASE' : '× REVIEW REQUIRED';
  status.classList.toggle('fail', report.status !== 'PASS');
  output.textContent = data.sanitized;
  reportOutput.textContent = JSON.stringify(report, null, 2);
  const metrics = document.querySelector('#metrics');
  metrics.innerHTML = '';
  [['REDACTIONS', report.metrics.redaction_count], ['REMAINING FINDINGS', verification.remaining_findings.length], ['PRESERVATION', `${Math.round((verification.benign_preservation || 0) * 100)}%`], ['MODEL CALLS', report.metrics.model_calls]].forEach(([label, value]) => {
    const card = document.createElement('div'); card.className = 'metric';
    card.innerHTML = `<span class="metric-label">${label}</span><span class="metric-value">${value}</span>`; metrics.appendChild(card);
  });
}

document.querySelector('#copy-button').addEventListener('click', async event => { await navigator.clipboard.writeText(output.textContent); event.target.textContent = 'copied'; setTimeout(() => event.target.textContent = 'copy', 1300); });
document.querySelector('#download-button').addEventListener('click', () => { const blob = new Blob([JSON.stringify(currentResult.report, null, 2)], { type: 'application/json' }); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = `${currentResult.filename}.redaction-report.json`; link.click(); URL.revokeObjectURL(link.href); });
function showError(message) { errorMessage.hidden = false; errorMessage.textContent = message; results.hidden = false; results.scrollIntoView({ behavior: 'smooth' }); }
function formatBytes(bytes) { return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`; }
