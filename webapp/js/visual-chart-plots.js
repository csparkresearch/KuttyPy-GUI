/**
 * Live plots for visual programs — Chart.js (replaces Flot in Blockly runtime).
 */

import {
  chartPointerInteraction,
  mobileTooltipLifetimePlugin,
  mobileTooltipOptions,
} from './chart-mobile-tooltip.js';

const PLOT_COLORS = ['#38bdf8', '#22c55e', '#f97316', '#a78bfa', '#f43f5e', '#eab308'];
const TIME_MS_THRESHOLD_SEC = 2;

function pickTimeUnit(maxSec) {
  return maxSec < TIME_MS_THRESHOLD_SEC ? 'ms' : 's';
}

function formatTimeTick(sec, unit) {
  if (unit === 'ms') return String(Math.round(sec * 1000));
  return Number(sec).toFixed(2);
}

function maxTimeSec(entry) {
  let max = 0;
  for (const ds of entry.chart.data.datasets) {
    for (const pt of ds.data) {
      const x = typeof pt === 'object' && pt != null ? Number(pt.x) : 0;
      if (x > max) max = x;
    }
  }
  return max;
}

function updateTimeAxis(entry) {
  if (entry.mode !== 'time') return;
  const unit = pickTimeUnit(maxTimeSec(entry));
  entry.timeUnit = unit;
  const xScale = entry.chart.options.scales.x;
  xScale.title.text = unit === 'ms' ? 'Time (ms)' : 'Time (s)';
  xScale.ticks.callback = (value) => formatTimeTick(value, unit);
}

function parseSeries(value) {
  if (value == null || value === '') return [{ label: 'Y', y: 0 }];
  if (typeof value === 'number' && Number.isFinite(value)) {
    return [{ label: 'Y', y: value }];
  }
  if (Array.isArray(value)) {
    return value.map((y, i) => ({ label: `Y${i + 1}`, y: Number(y) }));
  }
  if (typeof value === 'object') {
    return Object.entries(value).map(([label, y]) => ({
      label: String(label),
      y: Number(y),
    }));
  }
  const n = Number(value);
  return [{ label: 'Y', y: Number.isFinite(n) ? n : 0 }];
}

export class VisualPlotManager {
  constructor(hostEl) {
    this.host = hostEl;
    /** @type {Map<string, object>} */
    this.plots = new Map();
    this.colorIndex = 0;
  }

  clear() {
    for (const entry of this.plots.values()) {
      entry.chart.destroy();
    }
    this.plots.clear();
    if (this.host) this.host.innerHTML = '';
    this.colorIndex = 0;
  }

  _nextColor() {
    const c = PLOT_COLORS[this.colorIndex % PLOT_COLORS.length];
    this.colorIndex += 1;
    return c;
  }

  _ensure(name, { xy = false } = {}) {
    if (this.plots.has(name)) return this.plots.get(name);

    const wrap = document.createElement('div');
    wrap.className = 'visual-plot-card';
    const title = document.createElement('span');
    title.className = 'visual-plot-title';
    title.textContent = name;
    wrap.appendChild(title);

    const legend = document.createElement('div');
    legend.className = 'visual-plot-legend';
    legend.hidden = true;
    wrap.appendChild(legend);

    const chartArea = document.createElement('div');
    chartArea.className = 'visual-plot-chart';
    const canvas = document.createElement('canvas');
    chartArea.appendChild(canvas);
    wrap.appendChild(chartArea);
    this.host?.appendChild(wrap);

    const color = this._nextColor();
    const chart = new Chart(canvas, {
      type: 'line',
      plugins: [mobileTooltipLifetimePlugin],
      data: {
        datasets: [{
          label: 'Y',
          data: [],
          parsing: false,
          borderColor: color,
          backgroundColor: color + '33',
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: chartPointerInteraction,
        scales: {
          x: {
            type: 'linear',
            title: { display: true, text: xy ? 'X' : 'Time (ms)', color: '#94a3b8' },
            ticks: {
              color: '#64748b',
              maxTicksLimit: 8,
              callback: xy
                ? (value) => Number(value).toFixed(2)
                : (value) => formatTimeTick(value, 'ms'),
            },
            grid: { color: '#334155' },
          },
          y: {
            ticks: { color: '#64748b' },
            grid: { color: '#334155' },
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            ...mobileTooltipOptions,
            callbacks: {
              title(items) {
                if (!items.length) return '';
                const entry = items[0].chart?.$visualPlotEntry;
                const x = Number(items[0].parsed.x);
                if (entry?.mode === 'xy') return `X = ${x.toFixed(2)}`;
                const unit = entry?.timeUnit === 's' ? 's' : 'ms';
                const label = unit === 'ms' ? Math.round(x * 1000) : x.toFixed(2);
                return `t = ${label} ${unit}`;
              },
            },
          },
        },
      },
    });

    const entry = {
      chart,
      legendEl: legend,
      startMs: performance.now(),
      count: 0,
      mode: xy ? 'xy' : 'time',
      timeUnit: 'ms',
      datasets: chart.data.datasets,
    };
    chart.$visualPlotEntry = entry;
    this.plots.set(name, entry);
    return entry;
  }

  _syncDatasets(entry, series) {
    const { chart } = entry;
    while (chart.data.datasets.length > series.length) {
      chart.data.datasets.pop();
    }
    for (let i = 0; i < series.length; i++) {
      if (!chart.data.datasets[i]) {
        const color = this._nextColor();
        chart.data.datasets.push({
          label: series[i].label,
          data: [],
          parsing: false,
          borderColor: color,
          backgroundColor: color + '33',
          borderWidth: i === 0 ? 2 : 1.5,
          pointRadius: 2,
          tension: 0.1,
        });
      } else {
        chart.data.datasets[i].label = series[i].label;
      }
    }
  }

  _updateLegend(entry) {
    const { legendEl, chart } = entry;
    const datasets = chart.data.datasets;
    if (!legendEl) return;
    if (datasets.length <= 1) {
      legendEl.hidden = true;
      legendEl.innerHTML = '';
      return;
    }
    legendEl.hidden = false;
    legendEl.innerHTML = datasets.map((ds) => {
      const color = ds.borderColor || '#94a3b8';
      const label = ds.label || 'Y';
      return `<span class="visual-plot-legend-item" style="color:${color}">${label}</span>`;
    }).join('');
  }

  _refresh(entry) {
    if (entry.mode === 'time') updateTimeAxis(entry);
    entry.chart.update('none');
  }

  _plotTimeSeries(name, value) {
    const entry = this._ensure(name);
    const series = parseSeries(value);
    const t = entry.count === 0 ? 0 : (performance.now() - entry.startMs) / 1000;
    this._syncDatasets(entry, series);
    for (let i = 0; i < series.length; i++) {
      entry.chart.data.datasets[i].data.push({ x: t, y: series[i].y });
    }
    this._updateLegend(entry);
    entry.count += 1;
    this._refresh(entry);
  }

  plot(name, value) {
    this._plotTimeSeries(name, value);
  }

  plotXy(name, x, y) {
    const entry = this._ensure(name, { xy: true });
    entry.chart.data.datasets[0].data.push({ x: Number(x), y: Number(y) });
    entry.count += 1;
    entry.chart.update('none');
  }

  plotArray(name, values) {
    this._plotTimeSeries(name, values);
  }
}
