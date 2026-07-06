/**
 * I2C sensors panel — scan, ID probe, detected sensor tiles.
 */

import { createSensorDriver } from './sensors.js';
import { identifyDetectedSensors, sensorMeta } from './sensor-probe.js';
import { openSensorDialog } from './sensor-dialog.js?v=20';

export function initSensorsPanel(root, device, {
  setStatus,
  isConnected,
  withPollingPaused,
  stopPolling,
  startPolling,
}) {
  const btnScan = root.querySelector('.btn-i2c-scan');
  const buttonsEl = root.querySelector('.sensor-buttons');
  let openDialog = null;
  let hasSensorChips = false;
  let scanning = false;

  function setPanelEmpty(empty) {
    hasSensorChips = !empty;
    root.classList.toggle('sensors-panel--empty', empty);
    root.dataset.scanHint = empty ? 'Tap to scan I2C bus' : '';
  }

  function showEmptyHint(message = 'Tap to scan I2C bus') {
    buttonsEl.innerHTML = `<p class="sensor-buttons-empty">${message}</p>`;
    setPanelEmpty(true);
  }

  function clearButtons() {
    buttonsEl.innerHTML = '';
    setPanelEmpty(true);
  }

  function renderSensorButtons(detected) {
    buttonsEl.innerHTML = '';
    if (!detected.length) {
      showEmptyHint('No supported sensors identified — tap to rescan');
      return;
    }

    setPanelEmpty(false);

    for (const { typeId, address } of detected) {
      const meta = sensorMeta(typeId);
      if (!meta) continue;

      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'sensor-chip';
      btn.title = `${meta.name} @ 0x${address.toString(16).toUpperCase()}`;
      btn.innerHTML = `
        <img class="sensor-chip-icon" src="images/icons/${meta.icon}" alt="">
        <span class="sensor-chip-name">${meta.name}</span>
        <span class="sensor-chip-addr">0x${address.toString(16).toUpperCase().padStart(2, '0')}</span>
      `;
      btn.addEventListener('click', () => openSensor(typeId, address));
      buttonsEl.appendChild(btn);
    }
  }

  function openSensor(typeId, address) {
    if (!isConnected()) {
      setStatus('Connect device to open sensor');
      return;
    }
    openDialog?.close?.();
    const driver = createSensorDriver(typeId, device, address);
    if (!driver) return;

    openDialog = openSensorDialog({
      typeId,
      address,
      driver,
      withPollingPaused,
      stopPolling,
      startPolling,
      isConnected,
    });
  }

  async function scan() {
    if (scanning) return;
    if (!isConnected()) {
      setStatus('Connect device to scan I2C bus');
      return;
    }
    scanning = true;
    btnScan.disabled = true;
    btnScan.textContent = 'Scanning…';
    buttonsEl.innerHTML = '<p class="sensor-buttons-empty">Identifying sensors…</p>';
    setPanelEmpty(true);
    try {
      const detected = await withPollingPaused(async () => {
        const addrs = await device.i2cScan();
        if (!addrs.length) return { addrs, sensors: [] };
        const sensors = await identifyDetectedSensors(device, addrs);
        return { addrs, sensors };
      });

      if (detected.addrs.length) {
        btnScan.textContent = detected.addrs
          .map((a) => '0x' + a.toString(16).toUpperCase().padStart(2, '0'))
          .join(' ');
        renderSensorButtons(detected.sensors);
        if (!detected.sensors.length) {
          setStatus('I2C devices found but no supported sensor IDs matched');
        }
      } else {
        btnScan.textContent = 'No devices';
        showEmptyHint('No I2C devices — tap to rescan');
      }
    } catch (err) {
      btnScan.textContent = 'Scan failed';
      showEmptyHint('Scan failed — tap to retry');
      setStatus(err.message);
    } finally {
      scanning = false;
      btnScan.disabled = !isConnected();
    }
  }

  btnScan.addEventListener('click', (e) => {
    e.stopPropagation();
    scan();
  });

  root.addEventListener('click', () => {
    if (!hasSensorChips) scan();
  });

  showEmptyHint('Connect device, then tap to scan');

  return {
    setConnected(connected) {
      btnScan.disabled = !connected;
      if (!connected) {
        btnScan.textContent = 'I2C Scan';
        showEmptyHint('Connect device, then tap to scan');
        openDialog?.close?.();
        openDialog = null;
      } else if (!hasSensorChips) {
        showEmptyHint('Tap to scan I2C bus');
      }
    },
    reset() {
      btnScan.textContent = 'I2C Scan';
      showEmptyHint('Tap to scan I2C bus');
    },
  };
}
