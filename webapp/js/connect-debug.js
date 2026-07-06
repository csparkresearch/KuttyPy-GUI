/**
 * Connection debug trace — Android USB bring-up steps for failure diagnosis.
 */

export class ConnectDebug {
  constructor() {
    this.lines = [];
    this.t0 = performance.now();
  }

  log(message) {
    const sec = ((performance.now() - this.t0) / 1000).toFixed(2);
    this.lines.push(`[${sec}s] ${message}`);
  }

  logErr(message, err) {
    const detail = err?.message || String(err);
    this.log(`${message}: ${detail}`);
  }

  toString() {
    return this.lines.join('\n');
  }
}

/** Last Android connection attempt trace (survives disconnect cleanup). */
export let lastConnectDebug = null;

export function setLastConnectDebug(debug) {
  lastConnectDebug = debug;
}

let panelEl = null;
let bodyEl = null;

function ensurePanel() {
  if (panelEl) return;
  panelEl = document.getElementById('connect-debug-panel');
  bodyEl = panelEl?.querySelector('.connect-debug-body');
  panelEl?.querySelector('.connect-debug-close')
    ?.addEventListener('click', () => hideConnectDebugPanel());
}

/** Show closable in-page trace panel (works when alert() is blocked). */
export function showConnectDebugPanel(errorMessage, debug) {
  ensurePanel();
  if (!panelEl || !bodyEl) return;

  const trace = debug?.toString?.()
    || (typeof debug === 'string' ? debug : null)
    || lastConnectDebug?.toString()
    || '(no trace recorded)';

  const title = panelEl.querySelector('.connect-debug-title');
  if (title && errorMessage) {
    title.textContent = errorMessage;
  }

  bodyEl.textContent = trace;
  panelEl.hidden = false;
}

export function hideConnectDebugPanel() {
  ensurePanel();
  if (panelEl) panelEl.hidden = true;
}

/** User dismissed the port/device picker without selecting (Web Serial / WebUSB). */
export function isConnectUserCancelled(err) {
  if (!err) return false;
  if (err.userCancelled) return true;
  if (err.name === 'NotFoundError') return true;
  const msg = String(err.message || '').toLowerCase();
  return msg.includes('no port selected')
    || msg.includes('no device selected')
    || msg.includes('user cancelled')
    || msg.includes('user canceled');
}
