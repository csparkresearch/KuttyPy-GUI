/**
 * In-app confirm dialog (replaces window.confirm).
 */

let pendingResolve = null;

function getEls() {
  return {
    overlay: document.getElementById('app-confirm-overlay'),
    title: document.getElementById('app-confirm-title'),
    message: document.getElementById('app-confirm-message'),
    btnCancel: document.getElementById('app-confirm-cancel'),
    btnOk: document.getElementById('app-confirm-ok'),
  };
}

function closeConfirm(result) {
  const { overlay } = getEls();
  if (overlay) overlay.hidden = true;
  const resolve = pendingResolve;
  pendingResolve = null;
  resolve?.(result);
}

function onKeyDown(ev) {
  if (ev.key === 'Escape') {
    ev.preventDefault();
    closeConfirm(false);
  }
}

let wired = false;

function ensureWired() {
  if (wired) return;
  wired = true;

  const { overlay, btnCancel, btnOk } = getEls();
  btnCancel?.addEventListener('click', () => closeConfirm(false));
  btnOk?.addEventListener('click', () => closeConfirm(true));
  overlay?.addEventListener('click', (ev) => {
    if (ev.target === overlay) closeConfirm(false);
  });
  document.addEventListener('keydown', (ev) => {
    if (!pendingResolve) return;
    onKeyDown(ev);
  });
}

/**
 * @param {{ title: string, message: string, confirmLabel?: string, cancelLabel?: string, variant?: 'default' | 'danger' }} opts
 * @returns {Promise<boolean>}
 */
export function showConfirmDialog(opts) {
  ensureWired();
  const {
    title,
    message,
    confirmLabel = 'OK',
    cancelLabel = 'Cancel',
    variant = 'default',
  } = opts;

  const { overlay, title: titleEl, message: messageEl, btnCancel, btnOk } = getEls();
  if (!overlay || !titleEl || !messageEl || !btnCancel || !btnOk) {
    return Promise.resolve(window.confirm(message));
  }

  if (pendingResolve) closeConfirm(false);

  titleEl.textContent = title;
  messageEl.textContent = message;
  btnCancel.textContent = cancelLabel;
  btnOk.textContent = confirmLabel;
  btnOk.classList.toggle('app-confirm-btn--danger', variant === 'danger');

  pendingResolve = null;
  overlay.hidden = false;
  btnOk.focus();

  return new Promise((resolve) => {
    pendingResolve = resolve;
  });
}
