// Shared by the teacher pages that talk to the AI assistant: a JSON POST helper,
// a busy state for buttons, and the "Refine with AI" panel that sits under a
// text field and proposes a rewrite the teacher can take or leave.
const AI = (() => {
  async function post(url, body) {
    let r;
    try {
      r = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(body || {})});
    } catch (e) {
      return {ok: false, error: 'Could not reach the server: ' + e.message};
    }
    try {
      const d = await r.json();
      if (!d.ok && !d.error) d.error = 'Something went wrong.';
      return d;
    } catch (e) {
      return {ok: false, error: r.status === 401 || r.redirected
        ? 'You have been signed out. Sign in again in another tab, then retry.'
        : 'The server returned an error (' + r.status + ').'};
    }
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function busy(btn, on, label) {
    if (on) {
      btn.dataset.label = btn.innerHTML;
      btn.innerHTML = '<span class="spinner"></span>' + (label || 'Working');
      btn.disabled = true;
    } else {
      if (btn.dataset.label) btn.innerHTML = btn.dataset.label;
      btn.disabled = false;
    }
  }

  const TEXT_CHIPS = ['Simpler language', 'Shorter', 'Add a worked example',
                      'Add a real-life BC example', 'Check and fix the maths', 'More detail'];

  // Put a refine panel under `field` (a textarea or input). Options:
  //   url      the /api/ai/refine endpoint
  //   what     what the text is, e.g. "Chapter introduction (Markdown)"
  //   extra    () => object merged into the request (chapter, topic brief)
  //   chips    quick instructions to offer
  //   title    optional heading shown at the top of the panel
  //   onApply  (newText, oldText) => void, after the field has been updated
  function refine(field, opts) {
    const box = document.createElement('div');
    box.className = 'refine';
    box.hidden = true;
    const chips = (opts.chips || TEXT_CHIPS).map(c =>
      '<button type="button" class="chip">' + esc(c) + '</button>').join('');
    box.innerHTML =
      (opts.title ? '<b class="refine-title">' + esc(opts.title) + '</b>' : '') +
      '<div class="refine-row"><div class="chips">' + chips + '</div>' +
      '<div class="refine-ask"><input type="text" placeholder="Or say what to change, e.g. use hockey for the examples">' +
      '<button type="button" class="btn blue sm go">Refine</button></div></div>' +
      '<div class="refine-out" hidden><div class="dh"><b>Suggested version</b>' +
      '<span>read it, then use it or discard it</span></div><pre></pre>' +
      '<div class="refine-actions"><button type="button" class="btn blue sm use">Use this</button> ' +
      '<button type="button" class="btn light sm drop">Discard</button></div></div>' +
      '<p class="refine-err" hidden></p>';
    field.insertAdjacentElement('afterend', box);

    const input = box.querySelector('input');
    const go = box.querySelector('.go');
    const out = box.querySelector('.refine-out');
    const err = box.querySelector('.refine-err');
    let proposal = null, undo = null;

    async function run(instruction) {
      if (!instruction) { input.focus(); return; }
      err.hidden = true; out.hidden = true;
      busy(go, true, 'Refining');
      const d = await post(opts.url, Object.assign(
        {text: field.value, instruction, what: opts.what}, opts.extra ? opts.extra() : {}));
      busy(go, false);
      if (!d.ok) { err.textContent = d.error; err.className = 'refine-err bad'; err.hidden = false; return; }
      proposal = d.text;
      out.querySelector('pre').textContent = proposal;
      out.hidden = false;
    }
    box.querySelectorAll('.chip').forEach(c =>
      c.addEventListener('click', () => { input.value = c.textContent; run(c.textContent); }));
    go.addEventListener('click', () => run(input.value.trim()));
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); run(input.value.trim()); }
    });
    box.querySelector('.use').addEventListener('click', () => {
      undo = field.value;
      field.value = proposal;
      field.dispatchEvent(new Event('input', {bubbles: true}));
      out.hidden = true;
      err.innerHTML = 'Replaced. Save the page to keep it. <button type="button" class="linkbtn">Undo</button>';
      err.className = 'refine-err';
      err.hidden = false;
      err.querySelector('button').addEventListener('click', () => {
        field.value = undo;
        field.dispatchEvent(new Event('input', {bubbles: true}));
        err.hidden = true;
      });
      if (opts.onApply) opts.onApply(proposal, undo);
    });
    box.querySelector('.drop').addEventListener('click', () => { out.hidden = true; });
    return box;
  }

  // Wire every <button data-refine="field-id" data-what="..."> on the page to
  // open a refine panel under that field.
  function wireButtons(opts) {
    document.querySelectorAll('[data-refine]').forEach(btn => {
      const field = document.getElementById(btn.dataset.refine);
      if (!field) return;
      let panel = null;
      btn.addEventListener('click', () => {
        if (!panel) panel = refine(field, Object.assign({}, opts, {what: btn.dataset.what}));
        panel.hidden = !panel.hidden;
        if (!panel.hidden) panel.querySelector('input').focus();
      });
    });
  }

  return {post, esc, busy, refine, wireButtons};
})();
