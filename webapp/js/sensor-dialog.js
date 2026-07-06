/**
 * Sensor monitor dialog — gauges on top, live chart below.
 */

import { createAnalogGauge } from './analog-gauge.js?v=20';
import { createSensorLogger, LOGGER_COLORS, DEFAULT_WINDOW_SEC, DEFAULT_SAMPLE_INTERVAL_MS, defaultSampleIntervalMs } from './sensor-logger.js?v=27';
import { SENSOR_TYPES } from './sensors.js?v=20';
import { ASSET_V } from './build.js?v=20';

export function openSensorDialog({
  typeId,
  address = null,
  subtitle = null,
  configDefaults = {},
  driver,
  withPollingPaused,
  stopPolling,
  startPolling,
  isConnected,
}) {
  const meta = SENSOR_TYPES[typeId];
  if (!meta) return null;

  const iconSrc = meta.iconPath || `images/icons/${meta.icon}`;
  const addrLine = subtitle
    ?? (address != null
      ? `I2C 0x${address.toString(16).toUpperCase().padStart(2, '0')}`
      : '');

  const overlay = document.createElement('div');
  overlay.className = 'sensor-overlay';
  overlay.innerHTML = `
    <div class="sensor-dialog" role="dialog" aria-modal="true" aria-labelledby="sensor-dialog-title">
      <header class="sensor-dialog-header">
        <img class="sensor-dialog-icon" src="${iconSrc}" alt="">
        <div>
          <h2 id="sensor-dialog-title">${meta.name}</h2>
          <p class="sensor-dialog-addr">${addrLine}</p>
        </div>
        <button type="button" class="sensor-close" title="Close">×</button>
      </header>
      <div class="sensor-config"></div>
      <div class="sensor-body">
        <div class="sensor-gauges-row" aria-label="Live readings"></div>
        <div class="sensor-logger-panel">
          <div class="sensor-logger-bar">
            <div class="sensor-logger-actions">
              <div class="sensor-timing-fields">
                <label class="sensor-num-field" title="Visible time range on X axis">
                  <span>Window</span>
                  <input type="number" class="sensor-window-sec" value="${DEFAULT_WINDOW_SEC}"
                         min="1" max="600" step="1" inputmode="numeric" aria-label="Chart window seconds">
                  <span class="sensor-num-unit">s</span>
                </label>
                <label class="sensor-num-field" title="Delay between samples (0 = use ${DEFAULT_SAMPLE_INTERVAL_MS} ms minimum)">
                  <span>Interval</span>
                  <input type="number" class="sensor-interval-ms" value="${DEFAULT_SAMPLE_INTERVAL_MS}"
                         min="0" max="60000" step="1" inputmode="numeric" aria-label="Sample interval milliseconds">
                  <span class="sensor-num-unit">ms</span>
                </label>
              </div>
              <button type="button" class="sensor-logger-pause">Pause</button>
              <button type="button" class="sensor-logger-clear">Clear</button>
              <button type="button" class="sensor-logger-reset" title="Reset zoom and auto-scale">Reset view</button>
              <button type="button" class="sensor-logger-download" title="Download trace data as CSV"><i class="fa-solid fa-download"></i> Download CSV</button>
            </div>
          </div>
          <div class="sensor-chart-wrap">
            <canvas class="sensor-chart"></canvas>
          </div>
        </div>
      </div>
      <footer class="sensor-dialog-footer">
        <span class="sensor-status">Initializing…</span>
        <span class="sensor-ui-version" hidden></span>
      </footer>
    </div>
  `;

  document.body.appendChild(overlay);

  const verEl = overlay.querySelector('.sensor-ui-version');
  if (verEl) {
    verEl.textContent = `UI ${ASSET_V}`;
    verEl.hidden = false;
  }

  const gaugesEl = overlay.querySelector('.sensor-gauges-row');
  const configEl = overlay.querySelector('.sensor-config');
  const statusEl = overlay.querySelector('.sensor-status');
  const headerTitle = overlay.querySelector('#sensor-dialog-title');
  const headerAddr = overlay.querySelector('.sensor-dialog-addr');
  const canvas = overlay.querySelector('.sensor-chart');
  const btnPause = overlay.querySelector('.sensor-logger-pause');
  const btnClear = overlay.querySelector('.sensor-logger-clear');
  const btnDownload = overlay.querySelector('.sensor-logger-download');
  const btnReset = overlay.querySelector('.sensor-logger-reset');
  const windowInput = overlay.querySelector('.sensor-window-sec');
  const intervalInput = overlay.querySelector('.sensor-interval-ms');

  function delay(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  const gauges = meta.fields.map((f, i) => {
    const color = LOGGER_COLORS[i % LOGGER_COLORS.length];
    const g = createAnalogGauge(f.label, f.unit, f.min, f.max, { traceColor: color });
    gaugesEl.appendChild(g.el);
    return { ...f, gauge: g, traceIndex: i };
  });

  const configSelects = [];
  for (const cfg of meta.config) {
    const wrap = document.createElement('label');
    wrap.className = 'sensor-config-item';
    wrap.innerHTML = `<span>${cfg.label}</span>`;
    const sel = document.createElement('select');
    for (const opt of cfg.options) {
      const o = document.createElement('option');
      o.value = opt;
      o.textContent = opt;
      sel.appendChild(o);
    }
    sel.selectedIndex = configDefaults[cfg.key] ?? cfg.defaultIndex ?? 0;
    wrap.appendChild(sel);
    configEl.appendChild(wrap);
    configSelects.push({ cfg, sel });
  }

  let logger = null;
  let pollGeneration = 0;
  let loggerPaused = false;
  let startTime = Date.now();
  let sampleIntervalMs = DEFAULT_SAMPLE_INTERVAL_MS;

  function pollDelayMs() {
    return sampleIntervalMs > 0 ? sampleIntervalMs : DEFAULT_SAMPLE_INTERVAL_MS;
  }

  function syncIntervalFromInput() {
    const ms = Number(intervalInput.value);
    if (!Number.isFinite(ms) || ms < 0) {
      intervalInput.value = String(sampleIntervalMs);
      return false;
    }
    sampleIntervalMs = Math.floor(ms);
    intervalInput.value = String(sampleIntervalMs);
    return true;
  }

  function beginMeasurements() {
    syncIntervalFromInput();
    restartPollLoop();
  }

  function updateAdcDialogLabels() {
    if (typeId !== 'ATMEGA32_ADC') return;
    const chSel = configSelects.find((x) => x.cfg.key === 'channel');
    const ch = chSel?.sel.selectedIndex ?? 0;
    headerTitle.textContent = `ADC — PA${ch}`;
    headerAddr.textContent = `ADC${ch} · 10-bit`;
    if (gauges[0]) gauges[0].gauge.setLabel(`PA${ch}`);
  }

  function applyConfig() {
    for (const { cfg, sel } of configSelects) {
      const idx = sel.selectedIndex;
      if (cfg.method && typeof driver[cfg.method] === 'function') {
        driver[cfg.method](idx);
      }
      if (cfg.key === 'gain' && typeId === 'ADS1115' && gauges[0]) {
        const vmax = driver.getVoltageRange();
        gauges[0].gauge.setRange(-vmax, vmax);
      }
    }
    updateAdcDialogLabels();
  }

  function fieldValues(reading) {
    if (!reading) return null;
    return meta.fields.map((f) => reading[f.key]);
  }

  function updateGauges(vals) {
    if (!vals) return;
    gauges.forEach((g, i) => g.gauge.update(vals[i]));
  }

  function pushLoggerSample(vals) {
    if (loggerPaused || !vals || !logger) return;
    const t = (Date.now() - startTime) / 1000;
    logger.pushSample(t, vals);
  }

  async function pollOnce() {
    if (!isConnected()) return;
    await initPromise;
    if (initError) {
      statusEl.textContent = initError;
      return;
    }
    try {
      const reading = await withPollingPaused(() => driver.read());
      const vals = fieldValues(reading);
      if (!vals) {
        statusEl.textContent = 'Read failed — check wiring';
        return;
      }
      statusEl.textContent = `Updated ${new Date().toLocaleTimeString()}`;
      updateGauges(vals);
      pushLoggerSample(vals);
    } catch (err) {
      statusEl.textContent = err.message;
    }
  }

  function initLogger() {
    logger = createSensorLogger(canvas, meta.fields);

    for (const { gauge, label, traceIndex } of gauges) {
      const toggleTrace = () => {
        const on = !gauge.isTraceActive();
        gauge.setTraceActive(on);
        logger.setVisible(traceIndex, on);
      };
      gauge.el.addEventListener('click', toggleTrace);
    }

    requestAnimationFrame(() => logger.resize());
  }

  function stopPollLoop() {
    pollGeneration += 1;
  }

  function startPollLoop() {
    const gen = pollGeneration;
    (async () => {
      while (gen === pollGeneration && isConnected()) {
        if (!loggerPaused) {
          await pollOnce();
        } else {
          await delay(100);
          continue;
        }
        if (gen !== pollGeneration) break;
        await delay(pollDelayMs());
      }
    })();
  }

  function restartPollLoop() {
    stopPollLoop();
    startPollLoop();
  }

  function bindNumericField(input, apply) {
    input.addEventListener('change', apply);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        apply();
        input.blur();
      }
    });
  }

  function applyWindowSec() {
    if (!logger) return;
    const sec = Number(windowInput.value);
    if (!Number.isFinite(sec) || sec < 1) {
      windowInput.value = String(logger.getWindowSec());
      return;
    }
    logger.setWindowSec(sec);
    windowInput.value = String(logger.getWindowSec());
  }

  function applyIntervalMs() {
    if (!syncIntervalFromInput()) return;
    restartPollLoop();
  }

  function downloadTraceCsv() {
    if (!logger) return;
    const csv = logger.toCsv(meta.fields);
    if (!csv) {
      statusEl.textContent = 'No trace data to download';
      return;
    }

    const safeName = meta.name.replace(/[^\w.-]+/g, '_');
    const addrPart = address != null
      ? `_0x${address.toString(16).toUpperCase()}`
      : '';
    const stamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const filename = `${safeName}${addrPart}_${stamp}.csv`;

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    statusEl.textContent = `Downloaded ${logger.getSampleCount()} row(s)`;
  }

  function close() {
    stopPollLoop();
    logger?.destroy();
    overlay.remove();
    if (isConnected()) startPolling();
  }

  btnPause.addEventListener('click', () => {
    loggerPaused = !loggerPaused;
    btnPause.textContent = loggerPaused ? 'Resume' : 'Pause';
  });
  btnClear.addEventListener('click', () => {
    startTime = Date.now();
    logger?.clear();
  });
  btnDownload.addEventListener('click', downloadTraceCsv);
  btnReset.addEventListener('click', () => logger?.resetView());
  bindNumericField(windowInput, applyWindowSec);
  bindNumericField(intervalInput, applyIntervalMs);
  overlay.querySelector('.sensor-close').addEventListener('click', close);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });

  for (const { sel } of configSelects) {
    sel.addEventListener('change', () => {
      applyConfig();
      statusEl.textContent = 'Configuration updated';
    });
  }

  stopPolling();
  applyConfig();
  if (typeId === 'ADS1115' && gauges[0]) {
    const vmax = driver.getVoltageRange();
    gauges[0].gauge.setRange(-vmax, vmax);
  }

  initLogger();

  let initError = null;
  const initPromise = (async () => {
    try {
      const result = await withPollingPaused(() => driver.init());
      if (result === false) {
        initError = typeId === 'ATMEGA32_ADC'
          ? 'ADC init failed — connect device'
          : 'Sensor init failed — check wiring / I2C address';
        return;
      }
      sampleIntervalMs = defaultSampleIntervalMs(typeId, driver);
      intervalInput.value = String(sampleIntervalMs);
      statusEl.textContent = 'Ready';
    } catch (err) {
      initError = `Init failed: ${err.message}`;
    }
  })();

  statusEl.textContent = 'Running…';
  beginMeasurements();

  return { close };
}
