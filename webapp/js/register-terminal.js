import {
  REGISTER_NAMES,
  isCriticalRegister,
  criticalHint,
  resolveRegister,
  clampByte,
} from './registers.js';

const ARROW_UP = '↑';
const ARROW_DOWN = '↓';
const WARN = '⚠';

export function initRegisterTerminal(root, device, { setStatus, isConnected, withPollingPaused, onRegisterChanged }) {
  const converter = buildBitConverter(root.querySelector('.bit-converter'));
  const nameInput = root.querySelector('.reg-name');
  const valueInput = root.querySelector('.reg-value');
  const warnEl = root.querySelector('.reg-warn');
  const btnRead = root.querySelector('.reg-btn.read');
  const btnWrite = root.querySelector('.reg-btn.write');
  const historyEl = root.querySelector('.reg-history');

  nameInput.value = '';
  nameInput.placeholder = 'Register name';
  nameInput.addEventListener('input', () => {
    nameInput.placeholder = nameInput.value ? '' : 'Register name';
  });

  function appendHistory(line) {
    historyEl.value = historyEl.value ? `${historyEl.value}\n${line}` : line;
    historyEl.scrollTop = historyEl.scrollHeight;
  }

  function updateWarning() {
    const reg = resolveRegister(nameInput.value);
    const name = reg?.name ?? nameInput.value.trim().toUpperCase();
    const critical = isCriticalRegister(name);
    warnEl.hidden = !critical;
    warnEl.title = critical ? criticalHint(name) : '';
  }

  function getValue() {
    return parseValue(valueInput.value);
  }

  function setValue(val) {
    const b = clampByte(val);
    valueInput.value = String(b);
    converter.setValue(b);
  }

  converter.onChange = (val) => {
    valueInput.value = String(clampByte(val));
  };

  nameInput.addEventListener('input', updateWarning);
  nameInput.addEventListener('change', updateWarning);

  valueInput.addEventListener('input', () => {
    const v = parseValue(valueInput.value);
    if (v !== null) converter.setValue(v);
  });

  nameInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') readRegister();
  });
  valueInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') writeRegister();
  });

  btnRead.addEventListener('click', readRegister);
  btnWrite.addEventListener('click', writeRegister);

  async function readRegister() {
    if (!isConnected()) {
      setStatus('Connect device to read registers');
      return;
    }
    const reg = resolveRegister(nameInput.value);
    if (!reg) {
      appendHistory(`Unknown register: ${nameInput.value}`);
      return;
    }
    try {
      const val = await withPollingPaused(() => device.getReg(reg.addr));
      setValue(val);
      appendHistory(formatReadLine(reg.name, val));
      onRegisterChanged?.(reg.name, val);
    } catch (err) {
      appendHistory(`${reg.name} read failed: ${err.message}`);
      setStatus(err.message);
    }
  }

  async function writeRegister() {
    if (!isConnected()) {
      setStatus('Connect device to write registers');
      return;
    }
    const reg = resolveRegister(nameInput.value);
    if (!reg) {
      appendHistory(`Unknown register: ${nameInput.value}`);
      return;
    }
    const val = getValue();
    if (val === null) {
      appendHistory(`Invalid value for ${reg.name}`);
      return;
    }
    if (isCriticalRegister(reg.name)) {
      const hint = criticalHint(reg.name);
      if (!window.confirm(`Write ${reg.name} = ${val}?\n\n${hint}`)) return;
    }
    try {
      await withPollingPaused(() => device.setReg(reg.addr, val));
      appendHistory(formatWriteLine(reg.name, val));
      onRegisterChanged?.(reg.name, val);
    } catch (err) {
      appendHistory(`${reg.name} write failed: ${err.message}`);
      setStatus(err.message);
    }
  }

  function setEnabled(connected) {
    btnRead.disabled = !connected;
    btnWrite.disabled = !connected;
  }

  updateWarning();
  setEnabled(isConnected());

  return {
    setConnected(connected) {
      setEnabled(connected);
      if (!connected) appendHistory('Disconnected');
    },
    log(msg) {
      appendHistory(msg);
    },
  };
}

function formatWriteLine(name, val) {
  return `${name} set to ${val}`;
}

function formatReadLine(name, val) {
  const b = clampByte(val);
  const bin = b.toString(2).padStart(8, '0');
  const hex = '0x' + b.toString(16).toUpperCase().padStart(2, '0');
  return `${name} read as ${b} (0b${bin} / ${hex})`;
}

function parseValue(text) {
  const s = String(text).trim();
  if (!s) return 0;
  if (/^0x[0-9a-f]+$/i.test(s)) return clampByte(parseInt(s, 16));
  if (/^0b[01]+$/i.test(s)) return clampByte(parseInt(s.slice(2), 2));
  if (/^\d+$/.test(s)) return clampByte(parseInt(s, 10));
  return null;
}

function buildBitConverter(root) {
  const bitsEl = root.querySelector('.bit-leds');
  const decInput = root.querySelector('.conv-dec');
  const hexInput = root.querySelector('.conv-hex');
  const bits = [];
  let value = 0;
  let suppress = false;

  for (let i = 7; i >= 0; i--) {
    const led = document.createElement('button');
    led.type = 'button';
    led.className = 'bit-led low';
    led.dataset.bit = String(i);
    led.title = `Bit ${i}`;
    led.setAttribute('aria-label', `Bit ${i}`);
    led.textContent = String(i);
    led.addEventListener('click', () => {
      value ^= 1 << i;
      render();
      if (converter.onChange) converter.onChange(value);
    });
    bits.push({ bit: i, el: led });
    bitsEl.appendChild(led);
  }

  function render() {
    suppress = true;
    value = clampByte(value);
    for (const { bit, el } of bits) {
      const on = Boolean((value >> bit) & 1);
      el.classList.toggle('high', on);
      el.classList.toggle('low', !on);
    }
    decInput.value = String(value);
    hexInput.value = value.toString(16).toUpperCase().padStart(2, '0');
    suppress = false;
  }

  decInput.addEventListener('input', () => {
    if (suppress) return;
    const v = parseValue(decInput.value);
    if (v !== null) {
      value = v;
      render();
      if (converter.onChange) converter.onChange(value);
    }
  });

  hexInput.addEventListener('input', () => {
    if (suppress) return;
    const v = parseValue('0x' + hexInput.value.replace(/^0x/i, ''));
    if (v !== null) {
      value = v;
      render();
      if (converter.onChange) converter.onChange(value);
    }
  });

  const converter = {
    onChange: null,
    setValue(v) {
      value = clampByte(v);
      render();
    },
    getValue() {
      return value;
    },
  };

  render();
  return converter;
}

/** Populate datalist for register name autocomplete */
export function buildRegisterDatalist() {
  const dl = document.createElement('datalist');
  dl.id = 'reg-name-list';
  for (const name of REGISTER_NAMES) {
    const opt = document.createElement('option');
    opt.value = name;
    dl.appendChild(opt);
  }
  document.body.appendChild(dl);
}
