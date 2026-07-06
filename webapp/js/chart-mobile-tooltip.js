/**
 * Chart.js plugin — auto-hide tooltips on mobile (touch tooltips otherwise stick).
 */

const MOBILE_MQ = window.matchMedia('(max-width: 900px), (pointer: coarse)');
const TOOLTIP_LIFETIME_MS = 2500;

export function isMobileChartUi() {
  return MOBILE_MQ.matches;
}

export const chartPointerInteraction = {
  mode: 'nearest',
  axis: 'x',
  intersect: false,
};

function hideChartTooltip(chart) {
  const active = chart.getActiveElements?.() ?? [];
  const tipActive = chart.tooltip?.getActiveElements?.() ?? [];
  if (!active.length && !tipActive.length) return;
  chart.setActiveElements([]);
  chart.tooltip?.setActiveElements([], { x: 0, y: 0 });
  chart.update('none');
}

function clearTooltipTimer(chart) {
  if (chart.$mobileTooltip?.timer) {
    clearTimeout(chart.$mobileTooltip.timer);
    chart.$mobileTooltip.timer = null;
  }
}

function scheduleTooltipHide(chart) {
  clearTooltipTimer(chart);
  chart.$mobileTooltip.timer = setTimeout(() => {
    chart.$mobileTooltip.timer = null;
    hideChartTooltip(chart);
  }, TOOLTIP_LIFETIME_MS);
}

export const mobileTooltipLifetimePlugin = {
  id: 'mobileTooltipLifetime',

  afterInit(chart) {
    chart.$mobileTooltip = { timer: null };

    chart.$mobileTooltip.onTouchOutside = (ev) => {
      if (!isMobileChartUi()) return;
      const canvas = chart.canvas;
      if (canvas && (canvas === ev.target || canvas.contains(ev.target))) return;
      clearTooltipTimer(chart);
      hideChartTooltip(chart);
    };

    document.addEventListener('touchstart', chart.$mobileTooltip.onTouchOutside, { passive: true });
  },

  afterEvent(chart, args) {
    if (!isMobileChartUi()) return;
    const active = chart.getActiveElements?.() ?? [];
    if (!active.length) return;
    scheduleTooltipHide(chart);
  },

  destroy(chart) {
    clearTooltipTimer(chart);
    if (chart.$mobileTooltip?.onTouchOutside) {
      document.removeEventListener('touchstart', chart.$mobileTooltip.onTouchOutside);
    }
    chart.$mobileTooltip = null;
  },
};

export const mobileTooltipOptions = {
  backgroundColor: 'rgba(15, 20, 25, 0.92)',
  titleColor: '#e2e8f0',
  bodyColor: '#94a3b8',
  borderColor: '#334155',
  borderWidth: 1,
  padding: 10,
};
