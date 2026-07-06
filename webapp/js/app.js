import {
  KuttyPyDevice,
  PORTS,
  PIN_ORDER,
  SPECIALS,
} from './kuttypy-serial.js';
import { portPanelFromRegister } from './registers.js';
import { buildRegisterDatalist, initRegisterTerminal } from './register-terminal.js';
import { initSensorsPanel } from './sensors-panel.js';
import { createSensorDriver } from './sensors.js';
import { openSensorDialog } from './sensor-dialog.js?v=20';
import { isAndroidChrome } from './platform.js';
import { hideConnectDebugPanel } from './connect-debug.js';
import { initViewRouter } from './view-router.js';
import { initVisualView } from './view-visual.js?v=37';

const POLL_MS = 20;

const device = new KuttyPyDevice();
let pollTimer = null;
let pollPortIndex = 0;
let regTerminal = null;
let sensorsPanel = null;
let adcDialog = null;

/** port -> { ddr, port, pin } cached register values */
const portState = {};
/** port -> bit -> pin UI state */
const pinElements = {};

const statusEl = document.getElementById('status');
const btnConnect = document.getElementById('btn-connect');
const btnDisconnect = document.getElementById('btn-disconnect');
const portsGrid = document.getElementById('ports-grid');

function setStatus(text, connected = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle('connected', connected);
}

function formatBin(val) {
  return val.toString(2).padStart(8, '0');
}

function updateLed(led, high, isOutput) {
  led.classList.toggle('high', high);
  led.classList.toggle('low', !high);
  led.classList.toggle('output', isOutput);
  led.classList.toggle('input', !isOutput);
  led.title = isOutput
    ? `Output: ${high ? 'HIGH — click to toggle' : 'LOW — click to toggle'}`
    : `Input: ${high ? 'HIGH' : 'LOW'}`;
}

function updatePortHeader(port) {
  const regsEl = document.querySelector(`#port-${port} .port-regs`);
  const s = portState[port];
  if (!regsEl || !s) return;
  regsEl.innerHTML =
    `<span class="port-reg">DDR${port}: ${formatBin(s.ddr)}</span>` +
    `<span class="port-reg">PORT${port}: ${formatBin(s.port)}</span>` +
    `<span class="port-reg">PIN${port}: ${formatBin(s.pin)}</span>`;
}

function setTristateUI(els, mode) {
  els.mode = mode;
  els.tristate.dataset.mode = mode;
  for (const btn of els.tristate.querySelectorAll('.io-pos')) {
    btn.classList.toggle('active', btn.dataset.mode === mode);
    btn.setAttribute('aria-pressed', String(btn.dataset.mode === mode));
  }
  const showAdc = mode === 'adc';
  els.adcVal.hidden = !showAdc;
  if (!showAdc) els.adcVal.textContent = '';
  if (els.pinLabel) {
    els.pinLabel.classList.toggle('pin-label--adc', showAdc);
    els.pinLabel.title = showAdc ? 'Open ADC monitor' : '';
  }
}

function syncPortAFromDdr(ddr) {
  for (const bit of PIN_ORDER.A) {
    const els = pinElements.A[bit];
    const isOutput = Boolean((ddr >> bit) & 1);
    if (isOutput) {
      setTristateUI(els, 'output');
    } else if (els.mode === 'output') {
      setTristateUI(els, 'input');
    }
  }
}

function applyPinStates(port) {
  const s = portState[port];
  if (!s) return;

  for (const bit of PIN_ORDER[port]) {
    const els = pinElements[port][bit];
    const isOutput = Boolean((s.ddr >> bit) & 1);
    const high = isOutput ? Boolean((s.port >> bit) & 1) : Boolean((s.pin >> bit) & 1);

    els.isOutput = isOutput;

    if (port === 'A') {
      if (isOutput) setTristateUI(els, 'output');
      else if (els.mode === 'output') setTristateUI(els, 'input');
    } else {
      els.switch.checked = isOutput;
    }

    if (port === 'A' && els.mode === 'adc') continue;
    updateLed(els.led, high, isOutput);
  }
  updatePortHeader(port);
}

function buildPortAPinRow(name, special, bit) {
  const row = document.createElement('div');
  row.className = 'pin-row pin-row--tristate';
  row.innerHTML = `
    <div class="led low input" role="status" aria-label="${name} LED"></div>
    <div class="pin-label">
      <span class="pin-name">${name}<span class="pin-adc-val" hidden aria-live="polite"></span></span>
      ${special ? `<small>${special}</small>` : ''}
    </div>
    <div class="io-tristate" role="group" aria-label="${name} direction" data-mode="input">
      <button type="button" class="io-pos active" data-mode="input" aria-pressed="true">IN</button>
      <button type="button" class="io-pos" data-mode="adc" aria-pressed="false">ADC</button>
      <button type="button" class="io-pos" data-mode="output" aria-pressed="false">OUT</button>
    </div>
  `;

  const led = row.querySelector('.led');
  const tristate = row.querySelector('.io-tristate');
  const adcVal = row.querySelector('.pin-adc-val');
  const pinLabel = row.querySelector('.pin-label');

  led.addEventListener('click', () => onLedClick('A', bit));
  pinLabel.addEventListener('click', () => onPortALabelClick(bit));
  for (const btn of tristate.querySelectorAll('.io-pos')) {
    btn.addEventListener('click', () => onPortAModeChange('A', bit, btn.dataset.mode));
  }

  return { row, led, tristate, adcVal, pinLabel, mode: 'input', isOutput: false };
}

function buildStandardPinRow(port, name, special, bit) {
  const row = document.createElement('div');
  row.className = 'pin-row';
  row.innerHTML = `
    <div class="led low input" role="status" aria-label="${name} LED"></div>
    <div class="pin-label">
      <span class="pin-name">${name}</span>
      ${special ? `<small>${special}</small>` : ''}
    </div>
    <label class="io-switch" title="Output when ON, Input when OFF">
      <span class="io-in">IN</span>
      <input type="checkbox" aria-label="${name} direction">
      <span class="io-out">OUT</span>
    </label>
  `;

  const led = row.querySelector('.led');
  const ioSwitch = row.querySelector('input[type="checkbox"]');

  led.addEventListener('click', () => onLedClick(port, bit));
  ioSwitch.addEventListener('change', () => onDirectionChange(port, bit, ioSwitch));

  return { row, led, switch: ioSwitch, isOutput: false };
}

function buildUI() {
  portsGrid.innerHTML = '';

  for (const port of PORTS) {
    pinElements[port] = {};

    const card = document.createElement('article');
    card.className = 'port-card';
    card.id = `port-${port}`;
    card.innerHTML = `
      <div class="port-header">
        <h2>Port ${port}</h2>
        <div class="port-regs">
          <span class="port-reg">DDR${port}: --------</span>
          <span class="port-reg">PORT${port}: --------</span>
          <span class="port-reg">PIN${port}: --------</span>
        </div>
      </div>
      <div class="pin-list"></div>
    `;

    const pinList = card.querySelector('.pin-list');

    for (const bit of PIN_ORDER[port]) {
      const name = `P${port}${bit}`;
      const special = SPECIALS[name] || '';

      let built;
      if (port === 'A') {
        built = buildPortAPinRow(name, special, bit);
        pinElements[port][bit] = {
          led: built.led,
          tristate: built.tristate,
          adcVal: built.adcVal,
          pinLabel: built.pinLabel,
          mode: built.mode,
          isOutput: false,
        };
      } else {
        built = buildStandardPinRow(port, name, special, bit);
        pinElements[port][bit] = { led: built.led, switch: built.switch, isOutput: false };
      }

      pinList.appendChild(built.row);
    }

    portsGrid.appendChild(card);
    portState[port] = { ddr: 0, port: 0, pin: 0 };
  }
}

function onPortALabelClick(bit) {
  const els = pinElements.A[bit];
  if (els.mode !== 'adc') return;
  openAdcMonitor(bit);
}

function openAdcMonitor(bit) {
  if (!device.connected) {
    setStatus('Connect device to view ADC');
    return;
  }
  adcDialog?.close?.();
  adcDialog = openSensorDialog({
    typeId: 'ATMEGA32_ADC',
    subtitle: `PA${bit} · ADC${bit}`,
    configDefaults: { channel: bit },
    driver: createSensorDriver('ATMEGA32_ADC', device, null, { channel: bit }),
    withPollingPaused,
    stopPolling,
    startPolling,
    isConnected: () => device.connected,
  });
}

async function onPortAModeChange(port, bit, mode) {
  const els = pinElements[port][bit];
  if (!device.connected) return;
  if (els.mode === mode) return;

  const prevMode = els.mode;
  setTristateUI(els, mode);

  try {
    if (mode === 'output') {
      const ddr = await device.setPinDirection(port, bit, true);
      portState[port].ddr = ddr;
    } else {
      const ddr = await device.setPinDirection(port, bit, false);
      portState[port].ddr = ddr;
    }
    els.isOutput = mode === 'output';
    applyPinStates(port);
  } catch (err) {
    console.error(err);
    setTristateUI(els, prevMode);
    setStatus(`Error: ${err.message}`);
  }
}

async function onDirectionChange(port, bit, ioSwitch) {
  if (!device.connected) {
    ioSwitch.checked = !ioSwitch.checked;
    return;
  }

  const isOutput = ioSwitch.checked;
  try {
    const ddr = await device.setPinDirection(port, bit, isOutput);
    portState[port].ddr = ddr;
    applyPinStates(port);
  } catch (err) {
    console.error(err);
    ioSwitch.checked = !isOutput;
    setStatus(`Error: ${err.message}`);
  }
}

async function onLedClick(port, bit) {
  const els = pinElements[port][bit];
  if (!device.connected || !els.isOutput) return;

  try {
    const portVal = await device.togglePinOutput(port, bit);
    portState[port].port = portVal;
    const high = Boolean((portVal >> bit) & 1);
    updateLed(els.led, high, true);
    updatePortHeader(port);
  } catch (err) {
    console.error(err);
    setStatus(`Error: ${err.message}`);
  }
}

function onRegisterChanged(name, val) {
  const info = portPanelFromRegister(name);
  if (!info) return;

  const { port, kind } = info;
  portState[port][kind] = val;

  if (kind === 'ddr' && port === 'A') {
    syncPortAFromDdr(val);
  }
  applyPinStates(port);
}

async function refreshPort(port) {
  const state = await device.readPortState(port);
  portState[port] = state;
  if (port === 'A') syncPortAFromDdr(state.ddr);
  applyPinStates(port);
}

async function pollOnce() {
  if (!device.connected) return;

  const port = PORTS[pollPortIndex];
  pollPortIndex = (pollPortIndex + 1) % PORTS.length;

  try {
    if (port === 'A') {
      const adcBits = [];
      for (const bit of PIN_ORDER.A) {
        if (pinElements.A[bit].mode === 'adc') adcBits.push(bit);
      }

      if (adcBits.length) {
        for (const bit of adcBits) {
          const els = pinElements.A[bit];
          const val = await device.readADC(bit);
          els.adcVal.textContent = ` ${val}`;
          updateLed(els.led, val > 511, false);
        }
      }

      const pin = await device.getReg(device.pinReg(port));
      portState[port].pin = pin;
      for (const bit of PIN_ORDER.A) {
        const els = pinElements.A[bit];
        if (els.mode === 'adc' || els.isOutput) continue;
        const high = Boolean((pin >> bit) & 1);
        updateLed(els.led, high, false);
      }
    } else {
      const pin = await device.getReg(device.pinReg(port));
      portState[port].pin = pin;

      const ddr = portState[port].ddr;
      for (const bit of PIN_ORDER[port]) {
        const els = pinElements[port][bit];
        const isOutput = Boolean((ddr >> bit) & 1);
        if (!isOutput) {
          const high = Boolean((pin >> bit) & 1);
          updateLed(els.led, high, false);
        }
      }
    }
    updatePortHeader(port);
  } catch (err) {
    console.error('Poll error', err);
    await handleDisconnect(`Lost connection: ${err.message}`);
  }
}

function startPolling() {
  stopPolling();
  pollPortIndex = 0;
  pollTimer = setInterval(pollOnce, POLL_MS);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

/** Pause pin polling so serial transactions (I2C scan, etc.) are not interleaved. */
async function withPollingPaused(fn) {
  const wasPolling = pollTimer !== null;
  stopPolling();
  await device.waitForBusIdle();
  try {
    return await fn();
  } finally {
    if (wasPolling && device.connected) startPolling();
  }
}

function setPinControlsEnabled(connected) {
  for (const port of PORTS) {
    for (const bit of PIN_ORDER[port]) {
      const els = pinElements[port][bit];
      if (port === 'A') {
        for (const btn of els.tristate.querySelectorAll('.io-pos')) {
          btn.disabled = !connected;
        }
      } else {
        els.switch.disabled = !connected;
      }
    }
  }
}

function setControlsConnected(connected) {
  btnConnect.disabled = connected;
  btnConnect.classList.toggle('is-connected', connected);
  btnDisconnect.disabled = !connected;
  setPinControlsEnabled(connected);
  regTerminal?.setConnected(connected);
  sensorsPanel?.setConnected(connected);
}

async function handleConnect() {
  try {
    hideConnectDebugPanel();
    setStatus('Connecting…');
    const version = await device.connect();
    setControlsConnected(true);
    setStatus(`Yay! firmware v${version}`, true);

    for (const port of PORTS) {
      await refreshPort(port);
    }
    startPolling();
    regTerminal?.log('Connected — register terminal ready', 'read');
  } catch (err) {
    if (err?.userCancelled) {
      setStatus('Not connected');
      setControlsConnected(false);
      return;
    }
    console.error(err);
    setStatus(err.message || 'Connection failed');
    setControlsConnected(false);
  }
}

async function handleDisconnect(reason) {
  stopPolling();
  setControlsConnected(false);
  try {
    await device.disconnect();
  } catch (_) { /* ignore */ }
  setStatus(reason || 'Disconnected');
}

btnConnect.addEventListener('click', handleConnect);
btnDisconnect.addEventListener('click', () => handleDisconnect());

if (isAndroidChrome() && navigator.usb) {
  navigator.usb.addEventListener('disconnect', () => {
    handleDisconnect('Device unplugged');
  });
} else {
  navigator.serial?.addEventListener('disconnect', () => {
    handleDisconnect('Device unplugged');
  });
}

buildUI();
buildRegisterDatalist();
regTerminal = initRegisterTerminal(
  document.querySelector('.reg-terminal'),
  device,
  {
    setStatus,
    isConnected: () => device.connected,
    withPollingPaused,
    onRegisterChanged,
  },
);
sensorsPanel = initSensorsPanel(
  document.querySelector('.sensors-panel'),
  device,
  {
    setStatus,
    isConnected: () => device.connected,
    withPollingPaused,
    stopPolling,
    startPolling,
  },
);

initViewRouter({
  onVisualEnter: () => stopPolling(),
  onVisualLeave: () => {
    if (device.connected) startPolling();
  },
});
initVisualView({
  getDevice: () => device,
  isConnected: () => device.connected,
  withPollingPaused,
});
