const $ = q => document.querySelector(q);
const list = (q, items, empty) => { $(q).innerHTML = (items.length ? items : [empty]).map(x => `<li>${String(x).replaceAll('<','&lt;')}</li>`).join(''); };
let currentReceipt = null;
async function load(name) {
  const response = await fetch(`/api/receipt?scenario=${encodeURIComponent(name)}`); const r = await response.json(); currentReceipt = r;
  $('#decision').textContent = r.decision; $('#decision').className = `decision ${r.decision.toLowerCase()}`;
  const headline = r.headline_spread_pct == null ? 'UNKNOWN' : `${r.headline_spread_pct >= 0 ? '+' : ''}${r.headline_spread_pct.toFixed(2)}%`;
  const executable = r.executable_spread_pct == null ? 'UNKNOWN' : `${r.executable_spread_pct >= 0 ? '+' : ''}${r.executable_spread_pct.toFixed(2)}%`;
  $('#heroHeadline').textContent = headline; $('#heroExecutable').textContent = executable;
  $('#slippage').textContent = r.slippage_pct == null ? 'UNKNOWN' : `-${r.slippage_pct.toFixed(2)}%`;
  $('#cost').textContent = r.execution_cost_pct == null ? 'UNKNOWN' : `-${r.execution_cost_pct.toFixed(2)}%`;
  $('#provenance').textContent = r.reference_provenance === 'DERIVED_RWA_REFERENCE' ? 'Derived · not official exchange quote' : r.reference_provenance;
  $('#receiptId').textContent = r.receipt_id; $('#receiptHash').textContent = `SHA-256 ${r.receipt_hash}`;
  list('#reasons', r.decision_reasons, 'No reason available'); list('#unknown', r.critical_unknowns, 'No critical unknowns'); list('#changes', r.what_would_change_decision, 'No change condition');
}
document.querySelectorAll('button[data-case]').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('button[data-case]').forEach(x => x.classList.remove('active')); button.classList.add('active'); load(button.dataset.case); }));
$('#download').addEventListener('click', () => { if (!currentReceipt) return; const blob = new Blob([JSON.stringify(currentReceipt,null,2)],{type:'application/json'}); const link=document.createElement('a'); link.href=URL.createObjectURL(blob); link.download=`${currentReceipt.receipt_id}.json`; link.click(); URL.revokeObjectURL(link.href); });
load('false_arbitrage');

