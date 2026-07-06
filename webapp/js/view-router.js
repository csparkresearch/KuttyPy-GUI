/**
 * Switch between I/O Monitor and Visual Programming without reloading (keeps Web Serial).
 */

const VIEWS = {
  monitor: 'view-monitor',
  visual: 'view-visual',
};

let currentView = 'monitor';
let hooks = {
  onVisualEnter: null,
  onVisualLeave: null,
};

export function initViewRouter(options = {}) {
  hooks = {
    onVisualEnter: options.onVisualEnter ?? null,
    onVisualLeave: options.onVisualLeave ?? null,
  };

  const monitorEl = document.getElementById(VIEWS.monitor);
  const visualEl = document.getElementById(VIEWS.visual);
  if (!monitorEl || !visualEl) return;

  document.getElementById('btn-open-visual')?.addEventListener('click', () => {
    showView('visual');
  });
  document.getElementById('btn-visual-back')?.addEventListener('click', () => {
    showView('monitor');
  });

  showView('monitor', { silent: true });
}

export function showView(name, { silent = false } = {}) {
  if (name !== 'monitor' && name !== 'visual') return;
  if (name === currentView && !silent) return;

  const monitorEl = document.getElementById(VIEWS.monitor);
  const visualEl = document.getElementById(VIEWS.visual);
  if (!monitorEl || !visualEl) return;

  if (currentView === 'visual' && name === 'monitor') {
    hooks.onVisualLeave?.();
    window.dispatchEvent(new CustomEvent('kuttypy:visual-leave'));
  }

  currentView = name;
  const isVisual = name === 'visual';

  monitorEl.hidden = isVisual;
  visualEl.hidden = !isVisual;
  document.body.classList.toggle('view-visual-active', isVisual);
  document.title = isVisual ? 'KuttyPy Visual Programming' : 'KuttyPy I/O Monitor';

  if (isVisual && !silent) {
    hooks.onVisualEnter?.();
    window.dispatchEvent(new CustomEvent('kuttypy:visual-enter'));
  }
}

export function activeView() {
  return currentView;
}
