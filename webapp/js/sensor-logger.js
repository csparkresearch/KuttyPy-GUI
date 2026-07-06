/**
 * Sensor data logger — Chart.js + chartjs-plugin-zoom (Y zoom/pan, X autoscroll).
 */

import {
  chartPointerInteraction,
  mobileTooltipLifetimePlugin,
  mobileTooltipOptions,
} from './chart-mobile-tooltip.js';

export const LOGGER_COLORS = ['#38bdf8', '#22c55e', '#f97316', '#a78bfa', '#f43f5e', '#eab308'];

export const DEFAULT_WINDOW_SEC = 10;
export const DEFAULT_SAMPLE_INTERVAL_MS = 20;

/** Suggested default sample interval (ms) per sensor type. */
export function defaultSampleIntervalMs(typeId, driver) {
  const table = {
    MTP10: 200,
    BMP180: 20,
    BMP280: 20,
    BME280: 20,
    AHT10: 100,
    TSL2561: 150,
    TCS34725: 100,
    MLX90614: 100,
    MPU6050: 50,
    ADXL345: 50,
    HMC5883L: 100,
    QMC5883L: 100,
    TSL2591: 250,
    BH1750: 200,
    VL53L0X: 100,
    AS5600: 50,
    ADS1115: 20,
    INA219: 100,
    MAX30100: 50,
    ATMEGA32_ADC: 20,
    ML8511: 50,
    AD8232: 20,
  };
  if (table[typeId] != null) return table[typeId];
  if (driver?.dataRate) return Math.max(DEFAULT_SAMPLE_INTERVAL_MS, Math.ceil(1000 / driver.dataRate));
  return DEFAULT_SAMPLE_INTERVAL_MS;
}

const MAX_POINTS = 800;
const MIN_WINDOW_SEC = 1;
const MAX_WINDOW_SEC = 600;

function chartTheme() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: chartPointerInteraction,
    plugins: {
      legend: { display: false },
      tooltip: {
        ...mobileTooltipOptions,
        callbacks: {
          title(items) {
            return items.length ? `t = ${Number(items[0].parsed.x).toFixed(2)} s` : '';
          },
        },
      },
      zoom: {
        limits: {
          x: { minRange: 0.25 },
          y: { minRange: 1e-6 },
        },
        pan: {
          enabled: true,
          mode: 'y',
          onPanComplete: ({ chart: c }) => {
            c.$sensorLogger.manualY = true;
          },
        },
        zoom: {
          wheel: { enabled: true, speed: 0.1 },
          pinch: { enabled: true },
          drag: { enabled: false },
          mode: 'y',
          onZoomComplete: ({ chart: c }) => {
            c.$sensorLogger.manualY = true;
          },
        },
      },
    },
    scales: {
      x: {
        type: 'linear',
        title: { display: true, text: 'Time (s)', color: '#94a3b8', font: { size: 12 } },
        ticks: { color: '#64748b', maxTicksLimit: 10 },
        grid: { color: 'rgba(51, 65, 85, 0.45)' },
        border: { color: '#475569' },
      },
      y: {
        title: { display: true, text: 'Value', color: '#94a3b8', font: { size: 12 } },
        ticks: { color: '#64748b' },
        grid: { color: 'rgba(51, 65, 85, 0.45)' },
        border: { color: '#475569' },
      },
    },
  };
}

export function createSensorLogger(canvas, fields, { windowSec = DEFAULT_WINDOW_SEC } = {}) {
  const Chart = window.Chart;
  if (!Chart) {
    throw new Error('Chart.js not loaded — include vendor scripts in index.html');
  }

  const ctx = canvas.getContext('2d');
  let viewWindowSec = clampWindow(windowSec);
  let lastTime = 0;

  const chart = new Chart(ctx, {
    type: 'line',
    plugins: [mobileTooltipLifetimePlugin],
    data: {
      datasets: fields.map((f, i) => ({
        label: f.label,
        data: [],
        borderColor: LOGGER_COLORS[i % LOGGER_COLORS.length],
        backgroundColor: `${LOGGER_COLORS[i % LOGGER_COLORS.length]}22`,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHitRadius: 12,
        tension: 0.12,
        fill: false,
      })),
    },
    options: chartTheme(),
  });

  const api = {
    colors: LOGGER_COLORS,
    manualY: false,

    getWindowSec() {
      return viewWindowSec;
    },

    setWindowSec(sec) {
      viewWindowSec = clampWindow(sec);
      api.scrollXTo(lastTime);
      chart.update('none');
    },

    setYRange(min, max) {
      chart.options.scales.y.min = min;
      chart.options.scales.y.max = max;
      const yScale = chart.scales.y;
      if (yScale) {
        yScale.options.min = min;
        yScale.options.max = max;
      }
    },

    autoScaleY() {
      if (api.manualY) return;

      const { datasets } = chart.data;
      let yMin = Infinity;
      let yMax = -Infinity;
      const hasData = datasets.some((ds) => !ds.hidden && ds.data.length > 0);

      if (!hasData) {
        api.setYRange(0, 1);
        return;
      }

      const xMin = chart.scales.x?.min ?? 0;
      const xMax = chart.scales.x?.max ?? Infinity;

      for (const ds of datasets) {
        if (ds.hidden) continue;
        for (const pt of ds.data) {
          if (pt.x < xMin || pt.x > xMax) continue;
          if (pt.y < yMin) yMin = pt.y;
          if (pt.y > yMax) yMax = pt.y;
        }
      }

      if (!Number.isFinite(yMin)) {
        for (const ds of datasets) {
          if (ds.hidden) continue;
          for (const pt of ds.data) {
            if (pt.y < yMin) yMin = pt.y;
            if (pt.y > yMax) yMax = pt.y;
          }
        }
      }

      if (!Number.isFinite(yMin)) return;

      if (yMin === yMax) {
        yMin -= 1;
        yMax += 1;
      }
      const pad = (yMax - yMin) * 0.1;
      api.setYRange(yMin - pad, yMax + pad);
    },

    setXRange(min, max) {
      chart.options.scales.x.min = min;
      chart.options.scales.x.max = max;
      const xScale = chart.scales.x;
      if (xScale) {
        xScale.options.min = min;
        xScale.options.max = max;
      }
    },

    scrollXTo(t) {
      lastTime = t;
      const pad = Math.max(0.05, viewWindowSec * 0.02);
      const xMax = t + pad;
      const xMin = Math.max(0, xMax - viewWindowSec);
      api.setXRange(xMin, xMax);
    },

    pushSample(t, values) {
      values.forEach((y, i) => {
        const ds = chart.data.datasets[i];
        ds.data.push({ x: t, y });
        if (ds.data.length > MAX_POINTS) ds.data.shift();
      });
      api.scrollXTo(t);
      api.autoScaleY();
      chart.update('none');
    },

    setVisible(index, on) {
      chart.setDatasetVisibility(index, on);
      api.autoScaleY();
      chart.update('none');
    },

    clear() {
      for (const ds of chart.data.datasets) ds.data.length = 0;
      api.manualY = false;
      lastTime = 0;
      chart.resetZoom();
      api.setXRange(0, viewWindowSec);
      chart.options.scales.y.min = undefined;
      chart.options.scales.y.max = undefined;
      chart.update('none');
    },

    resetView() {
      api.manualY = false;
      chart.resetZoom();
      api.scrollXTo(lastTime);
      api.autoScaleY();
      chart.update('none');
    },

    resize() {
      chart.resize();
      chart.update('none');
    },

    getSampleCount() {
      return chart.data.datasets[0]?.data.length ?? 0;
    },

    /** Multi-column CSV: time_s + one column per trace (all buffered samples). */
    toCsv(fields) {
      const datasets = chart.data.datasets;
      const n = datasets[0]?.data.length ?? 0;
      if (!n) return null;

      const colNames = fields?.length
        ? fields.map((f) => (f.unit ? `${f.label} (${f.unit})` : f.label))
        : datasets.map((ds) => ds.label);

      const headers = ['time_s', ...colNames];
      const lines = [headers.map(csvCell).join(',')];

      for (let i = 0; i < n; i++) {
        const t = datasets[0].data[i].x;
        const row = [
          csvNum(t),
          ...datasets.map((ds) => csvNum(ds.data[i]?.y)),
        ];
        lines.push(row.join(','));
      }

      return lines.join('\n');
    },

    destroy() {
      chart.destroy();
    },
  };

  chart.$sensorLogger = api;

  const wrap = canvas.parentElement;
  const ro = wrap ? new ResizeObserver(() => {
    chart.resize();
    chart.update('none');
  }) : null;
  ro?.observe(wrap);

  requestAnimationFrame(() => {
    api.setXRange(0, viewWindowSec);
    chart.resize();
    chart.update('none');
  });

  const prevDestroy = api.destroy;
  api.destroy = () => {
    ro?.disconnect();
    prevDestroy();
  };

  return api;
}

function clampWindow(sec) {
  const n = Number(sec);
  if (!Number.isFinite(n)) return DEFAULT_WINDOW_SEC;
  return Math.max(MIN_WINDOW_SEC, Math.min(MAX_WINDOW_SEC, n));
}

function csvNum(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return '';
  return String(n);
}

function csvCell(v) {
  const s = String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
