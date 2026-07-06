/**
 * KuttyPy serial protocol — mirrors KuttyPyLib.py connectToPort / getReg / setReg.
 * ATMEGA32 register map from utilities/REGISTERS.py
 */

import { isAndroidChrome } from './platform.js';
import { resolveRegister } from './registers.js';
import { ConnectDebug, setLastConnectDebug, showConnectDebugPanel, hideConnectDebugPanel, isConnectUserCancelled } from './connect-debug.js';

export const BAUD = 38400;

export const CMD = {
  GET_VERSION: 1,
  READB: 2,
  WRITEB: 3,
  I2C_READ: 4,
  I2C_WRITE: 5,
  I2C_SCAN: 6,
};

export const VERSION_ATMEGA32 = 99;

/** Bootloader / device type bytes KuttyPyLib accepts */
export const VERSION_BYTES = [98, 99, 100, 101];

/** USB filters: CH340 and MCP2200 only */
export const USB_FILTERS = [
  { usbVendorId: 0x1a86, usbProductId: 0x7523 }, // CH340
  { usbVendorId: 0x04d8, usbProductId: 0x00df }, // MCP2200
];

export const REGISTERS = {
  PIND: 0x30,
  DDRD: 0x31,
  PORTD: 0x32,
  PINC: 0x33,
  DDRC: 0x34,
  PORTC: 0x35,
  PINB: 0x36,
  DDRB: 0x37,
  PORTB: 0x38,
  PINA: 0x39,
  DDRA: 0x3a,
  PORTA: 0x3b,
  ADCL: 0x24,
  ADCH: 0x25,
  ADCSRA: 0x26,
  ADMUX: 0x27,
  TWBR: 0x20,
};

export const PORTS = ['A', 'B', 'C', 'D'];

/** Pin display order per port (matches KuttyPyGUI.addPins) */
export const PIN_ORDER = {
  A: [7, 6, 5, 4, 3, 2, 1, 0],
  B: [7, 6, 5, 4, 3, 2, 1, 0],
  C: [0, 1, 2, 3, 4, 5, 6, 7],
  D: [7, 6, 5, 4, 3, 2, 1, 0],
};

export const SPECIALS = {
  PD5: 'OC1A',
  PD7: 'OC2',
  PB3: 'OC0',
  PB1: 'T1',
  PA0: 'ADC0',
  PA1: 'ADC1',
  PA2: 'ADC2',
  PA3: 'ADC3',
  PA4: 'ADC4',
  PA5: 'ADC5',
  PA6: 'ADC6',
  PA7: 'ADC7',
};

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Force 0–255 unsigned byte (avoids sign/extension issues). */
function asByte(n) {
  return n & 0xff;
}

/** Resolve register name (PORTB) or numeric address to protocol byte. */
function regAddress(reg) {
  if (typeof reg === 'number' && Number.isFinite(reg)) return asByte(reg);
  const resolved = resolveRegister(reg);
  if (resolved) return resolved.addr;
  const key = String(reg ?? '').trim().toUpperCase();
  if (key in REGISTERS) return REGISTERS[key];
  throw new Error(`Unknown register: ${reg}`);
}

export function regDisplayName(reg) {
  if (typeof reg === 'number' && Number.isFinite(reg)) {
    const resolved = Object.entries(REGISTERS).find(([, addr]) => addr === asByte(reg));
    return resolved?.[0] ?? `0x${asByte(reg).toString(16).toUpperCase()}`;
  }
  return resolveRegister(reg)?.name ?? String(reg ?? '').trim().toUpperCase();
}

/**
 * Background reader for post-connect traffic.
 * Not used during the initial version handshake.
 */
class RxBuffer {
  constructor(reader) {
    this.reader = reader;
    this.queue = [];
    this.waiters = [];
    this.running = false;
  }

  start() {
    if (this.running) return;
    this.running = true;
    this._loop();
  }

  stop() {
    this.running = false;
    for (const w of this.waiters) {
      clearTimeout(w.timer);
      w.reject(new Error('disconnected'));
    }
    this.waiters = [];
    this.queue = [];
  }

  drain() {
    this.queue = [];
  }

  pushBytes(bytes) {
    const view = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
    for (let i = 0; i < view.length; i++) {
      const b = asByte(view[i]);
      if (this.waiters.length) {
        const w = this.waiters.shift();
        clearTimeout(w.timer);
        w.resolve(b);
      } else {
        this.queue.push(b);
      }
    }
  }

  readByte(timeoutMs = 500) {
    if (this.queue.length) {
      return Promise.resolve(this.queue.shift());
    }
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        const idx = this.waiters.findIndex((w) => w.resolve === resolve);
        if (idx >= 0) this.waiters.splice(idx, 1);
        reject(new Error('No response from device'));
      }, timeoutMs);
      this.waiters.push({ resolve, reject, timer });
    });
  }

  async _loop() {
    try {
      while (this.running) {
        const { value, done } = await this.reader.read();
        if (done) break;
        if (value?.length) this.pushBytes(value);
      }
    } catch (_) {
      /* reader cancelled on disconnect */
    }
  }
}

export class KuttyPyDevice {
  constructor() {
    this.port = null;
    this.reader = null;
    this.writer = null;
    this.rx = null;
    this.ioLock = Promise.resolve();
    this.connected = false;
    this.version = 0;
    this.lastConnectDebug = null;
  }

  /** Desktop Web Serial — original working handshake (unchanged for Android). */
  async _connectDesktop(debug) {
    debug.log('connect: desktop Web Serial');
    this.port = await navigator.serial.requestPort({ filters: USB_FILTERS });
    debug.log(`connect: opening port @ ${BAUD} baud`);
    await this.port.open({ baudRate: BAUD });

    this.reader = this.port.readable.getReader();
    this.writer = this.port.writable.getWriter();

    let version = -1;
    for (let attempt = 0; attempt < 3 && version !== VERSION_ATMEGA32; attempt++) {
      debug.log(`connect: GET_VERSION attempt ${attempt + 1}/3`);
      version = await this.__getVersionDesktop();
      debug.log(`connect: attempt ${attempt + 1} returned ${version}`);
    }

    if (version !== VERSION_ATMEGA32) {
      const msg = version < 0
        ? 'No response from device — is KuttyPy connected and not in use by another app?'
        : `Unexpected firmware version ${version} (expected ${VERSION_ATMEGA32})`;
      throw new Error(msg);
    }

    this.rx = new RxBuffer(this.reader);
    this.rx.start();

    this.version = version;
    this.connected = true;
    debug.log(`connect: OK — firmware v${version}`);
    return version;
  }

  async connect() {
    if (!('serial' in navigator) && !('usb' in navigator)) {
      throw new Error('Web Serial / WebUSB not available. Use Chrome or Edge.');
    }

    const debug = new ConnectDebug();
    this.lastConnectDebug = debug;
    setLastConnectDebug(debug);
    hideConnectDebugPanel();

    try {
      debug.log(`connect: start (android=${isAndroidChrome()} serial=${!!navigator.serial} usb=${!!navigator.usb})`);

      if (isAndroidChrome()) {
        const { connectAndroid } = await import('./android-connect.js');
        const version = await connectAndroid(this, USB_FILTERS, debug);
        this.rx = new RxBuffer(this.reader);
        this.rx.start();
        this.version = version;
        this.connected = true;
        debug.log(`connect: OK — firmware v${version}`);
      } else {
        if (!('serial' in navigator)) {
          throw new Error('Web Serial API is not available. Use Chrome or Edge.');
        }
        await this._connectDesktop(debug);
      }

      hideConnectDebugPanel();
      return this.version;
    } catch (err) {
      debug.logErr('connect: exception', err);
      const cancelled = isConnectUserCancelled(err);
      if (!cancelled && this.lastConnectDebug) {
        showConnectDebugPanel(err.message || 'Connection failed', this.lastConnectDebug);
      }
      await this.disconnect();
      if (cancelled) {
        const e = new Error('Connection cancelled');
        e.userCancelled = true;
        throw e;
      }
      throw err;
    }
  }

  async disconnect() {
    this.connected = false;
    if (this.rx) {
      this.rx.stop();
      this.rx = null;
    }
    try {
      if (this.reader) {
        await this.reader.cancel();
        await this.reader.releaseLock();
      }
    } catch (_) { /* ignore */ }
    try {
      if (this.writer) {
        await this.writer.close();
        await this.writer.releaseLock();
      }
    } catch (_) { /* ignore */ }
    try {
      if (this.port?.readable) await this.port.readable.cancel();
    } catch (_) { /* ignore */ }
    try {
      if (this.port) await this.port.close();
    } catch (_) { /* ignore */ }

    this.reader = null;
    this.writer = null;
    this.port = null;
  }

  /**
   * Desktop only — mirrors KuttyPyLib.__get_version__.
   */
  async __getVersionDesktop() {
    await this._bootPulse();

    const t0 = performance.now();
    await this._drainDirect();

    const elapsed = performance.now() - t0;
    const wait = Math.max(0, 250 - elapsed);
    if (wait > 0) await delay(wait);

    await this._resetReader();

    await this._writeByte(CMD.GET_VERSION);

    const chunk = await this._readChunkDirect(500);
    if (!chunk || chunk.length !== 1) {
      return -1;
    }
    return asByte(chunk[0]);
  }

  /** RTS/DTR reset pulse — matches KuttyPyLib.__get_version__ */
  async _bootPulse() {
    try {
      await this.port.setSignals({ requestToSend: false, dataTerminalReady: false });
      await delay(10);
      await this.port.setSignals({ requestToSend: true, dataTerminalReady: true });
    } catch (_) {
      /* setSignals may be unsupported on some adapters */
    }
  }

  /** Discard buffered RX without a background reader running. */
  async _drainDirect() {
    const deadline = performance.now() + 100;
    while (performance.now() < deadline) {
      const chunk = await this._readChunkDirect(10);
      if (!chunk) break;
    }
  }

  /** Cancel pending reads and re-acquire a clean reader lock. */
  async _resetReader() {
    try {
      await this.reader.cancel();
    } catch (_) { /* ignore */ }
    try {
      await this.reader.releaseLock();
    } catch (_) { /* ignore */ }
    this.reader = this.port.readable.getReader();
  }

  async _readChunkDirect(timeoutMs) {
    const result = await Promise.race([
      this.reader.read(),
      delay(timeoutMs).then(() => null),
    ]);
    if (!result?.value?.length) return null;
    return result.value instanceof Uint8Array
      ? result.value
      : new Uint8Array(result.value);
  }

  _withIoLock(fn) {
    const run = this.ioLock.then(fn);
    this.ioLock = run.catch(() => {});
    return run;
  }

  /** Wait until any in-flight serial transaction has finished. */
  waitForBusIdle() {
    return this.ioLock;
  }

  /** @returns {number|null} mirrors KuttyPyLib.__getByte__ on timeout */
  async _getByte(timeoutMs = 500) {
    try {
      return await this.rx.readByte(timeoutMs);
    } catch {
      return null;
    }
  }

  async _getByteUntil(deadline) {
    const ms = Math.max(1, Math.ceil(deadline - performance.now()));
    return this._getByte(ms);
  }

  async _getRegUnlocked(reg) {
    const addr = regAddress(reg);
    await this._writeByte(CMD.READB);
    await this._writeByte(addr);
    const val = await this._getByte();
    if (val === null) throw new Error('No response from device');
    return val;
  }

  async _setRegUnlocked(reg, data) {
    const addr = regAddress(reg);
    await this._writeByte(CMD.WRITEB);
    await this._writeByte(addr);
    await this._writeByte(asByte(data));
  }

  async _writeByte(val) {
    await this.writer.write(new Uint8Array([asByte(val)]));
  }

  async getVersion() {
    return this._withIoLock(async () => {
      this.rx.drain();
      await this._writeByte(CMD.GET_VERSION);
      return this.rx.readByte();
    });
  }

  async getReg(reg) {
    return this._withIoLock(() => this._getRegUnlocked(reg));
  }

  async setReg(reg, data) {
    return this._withIoLock(() => this._setRegUnlocked(reg, data));
  }

  pinName(port, bit) {
    return `P${port}${bit}`;
  }

  ddrReg(port) {
    return REGISTERS[`DDR${port}`];
  }

  portReg(port) {
    return REGISTERS[`PORT${port}`];
  }

  pinReg(port) {
    return REGISTERS[`PIN${port}`];
  }

  async readPortState(port) {
    return this._withIoLock(async () => {
      const ddr = await this._getRegUnlocked(this.ddrReg(port));
      const portVal = await this._getRegUnlocked(this.portReg(port));
      const pin = await this._getRegUnlocked(this.pinReg(port));
      return { ddr, port: portVal, pin };
    });
  }

  async setPinDirection(port, bit, isOutput) {
    return this._withIoLock(async () => {
      const reg = this.ddrReg(port);
      let ddr = await this._getRegUnlocked(reg);
      if (isOutput) {
        ddr |= 1 << bit;
      } else {
        ddr &= ~(1 << bit);
      }
      await this._setRegUnlocked(reg, ddr);
      return ddr;
    });
  }

  async setPinOutput(port, bit, state) {
    return this._withIoLock(async () => {
      const reg = this.portReg(port);
      let val = await this._getRegUnlocked(reg);
      if (state) {
        val |= 1 << bit;
      } else {
        val &= ~(1 << bit);
      }
      await this._setRegUnlocked(reg, val);
      return val;
    });
  }

  async togglePinOutput(port, bit) {
    return this._withIoLock(async () => {
      const reg = this.portReg(port);
      const val = await this._getRegUnlocked(reg);
      const newVal = val ^ (1 << bit);
      await this._setRegUnlocked(reg, newVal);
      return newVal;
    });
  }

  /** Read 10-bit ADC on channel 0–7 — mirrors KuttyPyLib.readADC */
  async readADC(channel) {
    const ch = (Number(channel) | 0) & 0x07;
    return this._withIoLock(async () => {
      await this._setRegUnlocked(REGISTERS.ADMUX, 64 | ch);
      await this._setRegUnlocked(REGISTERS.ADCSRA, 197);
      const low = await this._getRegUnlocked(REGISTERS.ADCL);
      const hi = await this._getRegUnlocked(REGISTERS.ADCH);
      return (hi << 8) | low;
    });
  }

  /**
   * I2C bus scan — mirrors KuttyPyLib.I2CScan address read loop.
   * Must run as one atomic transaction (no pin polling interleaved).
   */
  async i2cScan() {
    return this._withIoLock(async () => {
      this.rx.drain();

      await this._writeByte(CMD.I2C_SCAN);

      const addrs = [];
      // Firmware scans all 127 addresses before sending 255 — use one deadline for
      // the whole response, not a short per-byte timeout after the last address.
      const deadline = performance.now() + 30000;

      let val = await this._getByteUntil(deadline);
      if (val === null) {
        return [];
      }

      while (val < 254) {
        addrs.push(val);
        val = await this._getByteUntil(deadline);
        if (val === null) {
          this.rx.drain();
          return addrs;
        }
      }

      this.rx.drain();
      return addrs;
    });
  }

  /**
   * I2C write — mirrors KuttyPyLib.I2CWriteBulk.
   * @returns {boolean} true if the device ACK'd (no timeout)
   */
  async i2cWriteBulk(address, bytestream) {
    return this._withIoLock(async () => {
      const bytes = bytestream instanceof Uint8Array ? bytestream : new Uint8Array(bytestream);
      if (bytes.length > 255) {
        throw new Error('I2C write limited to 255 bytes');
      }
      await this._writeByte(CMD.I2C_WRITE);
      await this._writeByte(asByte(address));
      await this._writeByte(bytes.length);
      for (let i = 0; i < bytes.length; i++) {
        await this._writeByte(bytes[i]);
      }
      const tmt = await this._getByte(2000);
      return tmt !== null && Boolean(tmt);
    });
  }

  /**
   * I2C read — mirrors KuttyPyLib.I2CReadBulk.
   * @returns {{ data: number[], ok: boolean }}
   */
  async i2cReadBulk(address, register, total) {
    return this._withIoLock(async () => {
      if (total > 255) {
        throw new Error('I2C read limited to 255 bytes');
      }
      await this._writeByte(CMD.I2C_READ);
      await this._writeByte(asByte(address));
      await this._writeByte(asByte(register));
      await this._writeByte(asByte(total));
      const data = [];
      for (let i = 0; i < total; i++) {
        const val = await this._getByte(2000);
        data.push(val !== null ? val : 0);
      }
      const tmt = await this._getByte(2000);
      // Firmware sends 1 on success, 0 on I2C timeout — same as I2CWriteBulk.
      return { data, ok: tmt !== null && Boolean(tmt) };
    });
  }
}
