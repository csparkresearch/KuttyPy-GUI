/**
 * Sensor picker modal for Blockly sensor blocks.
 */

import { SENSOR_TYPES } from './sensors.js';
import { identifyDetectedSensors } from './sensor-probe.js';

function sensorIcon(meta) {
  return meta.iconPath || `images/icons/${meta.icon}`;
}

function formatAddr(addr) {
  if (!addr) return 'ADC';
  return `0x${addr.toString(16).toUpperCase().padStart(2, '0')}`;
}

/**
 * @param {{ device: object, isConnected: () => boolean, withPollingPaused?: (fn: () => Promise<void>) => Promise<void> }} opts
 * @returns {Promise<{ typeId: string, address: number }|null>}
 */
export function openSensorPicker({ device, isConnected, withPollingPaused }) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.className = 'visual-sensor-picker-overlay';
    overlay.innerHTML = `
      <div class="visual-sensor-picker" role="dialog" aria-modal="true" aria-labelledby="vsp-title">
        <header class="visual-sensor-picker-header">
          <h2 id="vsp-title">Choose sensor</h2>
          <button type="button" class="visual-sensor-picker-close" aria-label="Close">×</button>
        </header>
        <div class="visual-sensor-picker-toolbar">
          <button type="button" class="visual-sensor-picker-scan">Scan I2C bus</button>
          <span class="visual-sensor-picker-status">Scan or pick a sensor below</span>
        </div>
        <div class="visual-sensor-picker-grid" aria-live="polite"></div>
        <section class="visual-sensor-picker-manual">
          <h3>Analog / onboard</h3>
          <div class="visual-sensor-picker-grid visual-sensor-picker-grid--manual"></div>
        </section>
      </div>
    `;
    document.body.appendChild(overlay);

    const grid = overlay.querySelector('.visual-sensor-picker-grid');
    const manualGrid = overlay.querySelector('.visual-sensor-picker-grid--manual');
    const statusEl = overlay.querySelector('.visual-sensor-picker-status');
    const btnScan = overlay.querySelector('.visual-sensor-picker-scan');
    let closed = false;

    function finish(result) {
      if (closed) return;
      closed = true;
      overlay.remove();
      resolve(result);
    }

    function renderCard(typeId, address, parent) {
      const meta = SENSOR_TYPES[typeId];
      if (!meta) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'visual-sensor-picker-card';
      btn.innerHTML = `
        <img src="${sensorIcon(meta)}" alt="" width="56" height="56">
        <span class="visual-sensor-picker-card-name">${meta.name}</span>
        <span class="visual-sensor-picker-card-addr">${formatAddr(address)}</span>
      `;
      btn.addEventListener('click', () => finish({ typeId, address }));
      parent.appendChild(btn);
    }

    for (const [typeId, meta] of Object.entries(SENSOR_TYPES)) {
      if (meta.addresses.length) continue;
      renderCard(typeId, 0, manualGrid);
    }

    async function runScan() {
      if (!isConnected()) {
        statusEl.textContent = 'Connect USB to scan I2C';
        return;
      }
      btnScan.disabled = true;
      statusEl.textContent = 'Scanning…';
      grid.innerHTML = '';
      try {
        const run = async () => {
          const addrs = await device.i2cScan();
          const detected = await identifyDetectedSensors(device, addrs);
          if (!detected.length) {
            statusEl.textContent = 'No supported sensors found on the bus';
            return;
          }
          statusEl.textContent = `${detected.length} sensor(s) found`;
          for (const { typeId, address } of detected) {
            renderCard(typeId, address, grid);
          }
        };
        if (withPollingPaused) await withPollingPaused(run);
        else await run();
      } catch (err) {
        statusEl.textContent = err.message || 'Scan failed';
      } finally {
        btnScan.disabled = false;
      }
    }

    overlay.querySelector('.visual-sensor-picker-close')
      ?.addEventListener('click', () => finish(null));
    overlay.addEventListener('click', (ev) => {
      if (ev.target === overlay) finish(null);
    });
    btnScan.addEventListener('click', () => runScan());

    document.addEventListener('keydown', function onKey(ev) {
      if (ev.key === 'Escape') {
        document.removeEventListener('keydown', onKey);
        finish(null);
      }
    });

    void runScan();
  });
}
