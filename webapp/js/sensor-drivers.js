/**
 * I2C sensor driver implementations — ported from KuttyPyLib.py
 */

import { vl53l0xInit, vl53l0xReadRangeMm } from './vl53l0x.js';

export function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export function signit(v) {
  return v >= 0x8000 ? v - 0x10000 : v;
}

export function bytesToUint16(hi, lo) {
  return (hi << 8) | lo;
}

export async function i2cRead(device, address, reg, total) {
  const { data, ok } = await device.i2cReadBulk(address, reg, total);
  if (!ok || !data || data.length < total) return null;
  return data;
}

export async function i2cWrite(device, address, bytes) {
  return device.i2cWriteBulk(address, bytes);
}

// ── BMP180 ──────────────────────────────────────────────────────────

export class BMP180Driver {
  constructor(device, address = 0x77) {
    this.device = device;
    this.address = address;
    this.oversampling = 0;
    this._cal = {};
    this.T = 25;
    this.P = 1000;
  }

  setOversampling(n) {
    this.oversampling = Math.max(0, Math.min(3, Number(n) | 0));
  }

  async _readUInt(reg) {
    const b = await i2cRead(this.device, this.address, reg, 2);
    return b ? bytesToUint16(b[0], b[1]) : null;
  }

  async _readInt(reg) {
    const u = await this._readUInt(reg);
    return u === null ? null : signit(u);
  }

  async init() {
    this._cal.c3 = 160.0 * 2 ** -15 * (await this._readInt(0xae));
    this._cal.c4 = 10 ** -3 * 2 ** -15 * (await this._readUInt(0xb0));
    this._cal.b1 = 160 ** 2 * 2 ** -30 * (await this._readInt(0xb6));
    this._cal.c5 = (2 ** -15 / 160) * (await this._readUInt(0xb2));
    this._cal.c6 = await this._readUInt(0xb4);
    this._cal.mc = (2 ** 11 / 160 ** 2) * (await this._readInt(0xbc));
    this._cal.md = (await this._readInt(0xbe)) / 160.0;
    this._cal.x0 = await this._readInt(0xaa);
    this._cal.x1 = 160.0 * 2 ** -13 * (await this._readInt(0xac));
    this._cal.x2 = 160 ** 2 * 2 ** -25 * (await this._readInt(0xb8));
    this._cal.y0 = this._cal.c4 * 2 ** 15;
    this._cal.y1 = this._cal.c4 * this._cal.c3;
    this._cal.y2 = this._cal.c4 * this._cal.b1;
    this._cal.p0 = (3791.0 - 8.0) / 1600.0;
    this._cal.p1 = 1.0 - 7357.0 * 2 ** -20;
    this._cal.p2 = 3038.0 * 100.0 * 2 ** -36;
    await this._initTemperature();
    await this._readTemperature();
    await this._initPressure();
  }

  async _initTemperature() {
    await i2cWrite(this.device, this.address, [0xf4, 0x2e]);
    await delay(5);
  }

  async _readTemperature() {
    const b = await i2cRead(this.device, this.address, 0xf6, 2);
    if (!b) return null;
    const T = bytesToUint16(b[0], b[1]);
    const a = this._cal.c5 * (T - this._cal.c6);
    this.T = a + this._cal.mc / (a + this._cal.md);
    return this.T;
  }

  async _initPressure() {
    const os = [0x34, 0x74, 0xb4, 0xf4];
    const delays = [5, 8, 14, 26];
    await i2cWrite(this.device, this.address, [0xf4, os[this.oversampling]]);
    await delay(delays[this.oversampling]);
  }

  async _readPressure() {
    const b = await i2cRead(this.device, this.address, 0xf6, 3);
    if (!b) return null;
    const Praw = (b[0] << 8) + b[1] + b[2] / 256.0;
    const s = this.T - 25.0;
    const x = this._cal.x2 * s ** 2 + this._cal.x1 * s + this._cal.x0;
    const y = this._cal.y2 * s ** 2 + this._cal.y1 * s + this._cal.y0;
    const z = (Praw - x) / y;
    this.P = this._cal.p2 * z ** 2 + this._cal.p1 * z + this._cal.p0;
    return this.P;
  }

  async read() {
    await this._initTemperature();
    await this._readTemperature();
    await this._initPressure();
    await this._readPressure();
    return { pressure: this.P, temp: this.T };
  }
}

// ── ADS1115 ─────────────────────────────────────────────────────────

const ADS1115_GAINS = [
  { pga: 0 << 9, scale: 0.1875, vmax: 6.144 },
  { pga: 1 << 9, scale: 0.125, vmax: 4.096 },
  { pga: 2 << 9, scale: 0.0625, vmax: 2.048 },
  { pga: 3 << 9, scale: 0.03125, vmax: 1.024 },
  { pga: 4 << 9, scale: 0.015625, vmax: 0.512 },
  { pga: 5 << 9, scale: 0.0078125, vmax: 0.256 },
];
const ADS1115_RATES = [8, 16, 32, 64, 128, 250, 475, 860];
const ADS1115_RATE_BITS = [0, 1, 2, 3, 4, 5, 6, 7].map((n) => n << 5);
const ADS1115_MUX = [0x4000, 0x5000, 0x6000, 0x7000, 0x0000, 0x3000];

export class ADS1115Driver {
  constructor(device, address = 0x48) {
    this.device = device;
    this.address = address;
    this.channel = 0;
    this.dataRate = 250;
    this.gainIndex = 1;
  }

  setChannel(i) { this.channel = Math.max(0, Math.min(5, i | 0)); }
  setRate(i) { this.dataRate = ADS1115_RATES[Math.max(0, Math.min(7, i | 0))]; }
  setGain(i) { this.gainIndex = Math.max(0, Math.min(5, i | 0)); }
  getVoltageRange() { return ADS1115_GAINS[this.gainIndex].vmax; }

  async init() {
    await i2cWrite(this.device, this.address, [0x80, 0x03]);
  }

  async read() {
    const gain = ADS1115_GAINS[this.gainIndex];
    const rateIdx = ADS1115_RATES.indexOf(this.dataRate);
    const rateBits = ADS1115_RATE_BITS[rateIdx >= 0 ? rateIdx : 5];
    let mux = ADS1115_MUX[this.channel] ?? 0x4000;
    const config = 0x0003 | rateBits | 0x0100 | gain.pga | mux | 0x8000;
    await i2cWrite(this.device, this.address, [0x01, (config >> 8) & 0xff, config & 0xff]);
    await delay(1000 / this.dataRate + 2);
    const b = await i2cRead(this.device, this.address, 0x00, 2);
    if (!b) return null;
    let raw = (b[0] << 8) | b[1];
    if (raw & 0x8000) raw -= 65536;
    return { voltage: raw * gain.scale * 1e-3 };
  }
}

// ── MPU6050 ─────────────────────────────────────────────────────────

export class MPU6050Driver {
  constructor(device, address = 0x68) {
    this.device = device;
    this.address = address;
  }

  async setGyroRange(i) {
    await i2cWrite(this.device, this.address, [0x1b, (i & 3) << 3]);
  }

  async setAccelRange(i) {
    await i2cWrite(this.device, this.address, [0x1c, (i & 3) << 3]);
  }

  setKalman() { /* Kalman filter omitted in web UI */ }

  async init() {
    await i2cWrite(this.device, this.address, [0x1b, 0]);
    await i2cWrite(this.device, this.address, [0x1c, 0]);
    await i2cWrite(this.device, this.address, [0x6b, 0x00]);
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x3b, 14);
    if (!b) return null;
    const vals = [];
    for (let x = 0; x < 7; x++) {
      vals.push(signit((b[x * 2] << 8) | b[x * 2 + 1]));
    }
    return {
      ax: vals[0], ay: vals[1], az: vals[2],
      temp: vals[3], gx: vals[4], gy: vals[5], gz: vals[6],
    };
  }
}

// ── HMC5883L ────────────────────────────────────────────────────────

const HMC_GAIN_SCALE = [1370, 1090, 820, 660, 440, 390, 330, 230];

export class HMC5883LDriver {
  constructor(device, address = 0x1e) {
    this.device = device;
    this.address = address;
    this.gainIndex = 7;
  }

  async init() {
    await i2cWrite(this.device, this.address, [0x00, (6 << 2)]);
    await i2cWrite(this.device, this.address, [0x01, this.gainIndex << 5]);
    await i2cWrite(this.device, this.address, [0x02, 0]);
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x03, 6);
    if (!b) return null;
    const s = HMC_GAIN_SCALE[this.gainIndex];
    return {
      mx: signit((b[0] << 8) | b[1]) / s,
      my: signit((b[2] << 8) | b[3]) / s,
      mz: signit((b[4] << 8) | b[5]) / s,
    };
  }
}

// ── QMC5883L ────────────────────────────────────────────────────────

export class QMC5883LDriver {
  constructor(device, address = 0x0d) {
    this.device = device;
    this.address = address;
    this.scaling = 3000;
  }

  async setRange(i) {
    if (i === 1) {
      this.scaling = 3000;
      await i2cWrite(this.device, this.address, [0x09, 0b001 | 0b000 | 0b100 | 0b10000]);
    } else {
      this.scaling = 12000;
      await i2cWrite(this.device, this.address, [0x09, 0b001 | 0b000 | 0b100 | 0b00000]);
    }
  }

  async init() {
    await i2cWrite(this.device, this.address, [0x0a, 0x80]);
    await i2cWrite(this.device, this.address, [0x0b, 0x01]);
    this.setRange(1);
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x00, 6);
    if (!b) return null;
    const mx = signit((b[1] << 8) | b[0]) / this.scaling;
    const my = signit((b[3] << 8) | b[2]) / this.scaling;
    const mz = signit((b[5] << 8) | b[4]) / this.scaling;
    const heading = Math.atan2(my, mx) * (180 / Math.PI);
    return { mx, my, mz, heading };
  }
}

// ── BMP280 / BME280 ─────────────────────────────────────────────────

function unpackCalibBMP280(bytes) {
  const u16 = (i) => bytes[i] | (bytes[i + 1] << 8);
  const s16 = (i) => signit(u16(i));
  return {
    temp: [u16(0), s16(2), s16(4)],
    pressure: [u16(6), s16(8), s16(10), s16(12), s16(14), s16(16), s16(18), s16(20), s16(22)],
  };
}

export class BMP280Driver {
  constructor(device, address = 0x76) {
    this.device = device;
    this.address = address;
    this.hasHumidity = false;
    this._tFine = 0;
    this._tempCalib = [];
    this._pressCalib = [];
    this._humCalib = [];
  }

  _calcTemp(adcT) {
    const [t0, t1, t2] = this._tempCalib;
    const v1 = (adcT / 16384.0 - t0 / 1024.0) * t1;
    const v2 = ((adcT / 131072.0 - t0 / 8192.0) ** 2) * t2;
    this._tFine = v1 + v2;
    return (v1 + v2) / 5120.0;
  }

  _calcPressure(adcP, adcT) {
    this._calcTemp(adcT);
    const c = this._pressCalib;
    let var1 = this._tFine / 2.0 - 64000.0;
    let var2 = var1 * var1 * c[5] / 32768.0;
    var2 = var2 + var1 * c[4] * 2.0;
    var2 = var2 / 4.0 + c[3] * 65536.0;
    var1 = (c[2] * var1 * var1 / 524288.0 + c[1] * var1) / 524288.0;
    var1 = (1.0 + var1 / 32768.0) * c[0];
    if (!var1) return 0;
    let p = 1048576.0 - adcP;
    p = ((p - var2 / 4096.0) * 6250.0) / var1;
    var1 = c[8] * p * p / 2147483648.0;
    var2 = p * c[7] / 32768.0;
    p = (p + (var1 + var2 + c[6]) / 16.0) / 100;
    return Math.max(0, Math.min(1600, p));
  }

  _calcHumidity(adcH, adcT) {
    this._calcTemp(adcT);
    const h = this._humCalib;
    let var1 = this._tFine - 76800.0;
    let var2 = h[3] * 64.0 + (h[4] / 16384.0) * var1;
    let var3 = adcH - var2;
    let var4 = h[1] / 65536.0;
    let var5 = 1.0 + (h[2] / 67108864.0) * var1;
    let var6 = 1.0 + (h[5] / 67108864.0) * var1 * var5;
    var6 = var3 * var4 * var5 * var6;
    let humidity = var6 * (1.0 - h[0] * var6 / 524288.0);
    return Math.max(0, Math.min(100, humidity));
  }

  async init() {
    await i2cWrite(this.device, this.address, [0xe0, 0xb6]);
    await delay(100);
    const id = await i2cRead(this.device, this.address, 0xd0, 1);
    if (!id) return;
    this.hasHumidity = id[0] === 0x60;
    const cal = await i2cRead(this.device, this.address, 0x88, 24);
    if (!cal) return;
    const c = unpackCalibBMP280(cal);
    this._tempCalib = c.temp;
    this._pressCalib = c.pressure;
    if (this.hasHumidity) {
      await i2cWrite(this.device, this.address, [0xf2, 0b101]);
      const h1 = await i2cRead(this.device, this.address, 0xa1, 1);
      const hc = await i2cRead(this.device, this.address, 0xe1, 7);
      if (h1 && hc) {
        this._humCalib = [
          h1[0], hc[0], hc[1],
          (hc[2] << 4) | (hc[3] & 0x0f),
          (hc[4] << 4) | (hc[3] >> 4),
          hc[5],
        ];
      }
    }
    await i2cWrite(this.device, this.address, [0xf4, 0xff]);
  }

  async read() {
    const n = this.hasHumidity ? 8 : 6;
    const data = await i2cRead(this.device, this.address, 0xf7, n);
    if (!data) return null;
    const adcP = (((data[0] & 0xff) * 65536) + ((data[1] & 0xff) * 256) + (data[2] & 0xf0)) / 16;
    const adcT = (((data[3] & 0xff) * 65536) + ((data[4] & 0xff) * 256) + (data[5] & 0xf0)) / 16;
    const out = {
      pressure: this._calcPressure(adcP, adcT),
      temp: this._calcTemp(adcT),
    };
    if (this.hasHumidity) {
      const adcH = data[6] * 256 + data[7];
      out.humidity = this._calcHumidity(adcH, adcT);
    }
    return out;
  }
}

// ── BH1750 ──────────────────────────────────────────────────────────

const BH1750_CMD = [0x11, 0x10, 0x13];

export class BH1750Driver {
  constructor(device, address = 0x23) {
    this.device = device;
    this.address = address;
    this.gainIndex = 0;
    this.scaling = 1;
  }

  async setGain(i) {
    this.gainIndex = Math.max(0, Math.min(2, i | 0));
    this.scaling = i === 0 ? 1 : 2;
    await i2cWrite(this.device, this.address, [BH1750_CMD[this.gainIndex]]);
  }

  async init() {
    await this.setGain(0);
    await delay(120);
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x00, 2);
    if (!b) return null;
    return { lux: ((b[0] << 8) | b[1]) * this.scaling / 2 };
  }
}

// ── TSL2591 ─────────────────────────────────────────────────────────

const TSL2591_CMD = 0xa0;
const TSL2591_GAINS = [0x00, 0x10, 0x20, 0x30];
const TSL2591_GAIN_MUL = [1, 25, 428, 9876];

export class TSL2591Driver {
  constructor(device, address = 0x29) {
    this.device = device;
    this.address = address;
    this.gain = 0;
    this.timing = 0;
  }

  setGain(i) {
    this.gain = Math.max(0, Math.min(3, i | 0)) << 4;
    return this._config();
  }

  setTiming(i) {
    this.timing = Math.max(0, Math.min(5, i | 0));
    return this._config();
  }

  async _config() {
    await i2cWrite(this.device, this.address, [TSL2591_CMD | 0x01, this.gain | this.timing]);
  }

  async init() {
    await i2cWrite(this.device, this.address, [TSL2591_CMD | 0x00, 0x01 | 0x02 | 0x10 | 0x80]);
    await i2cWrite(this.device, this.address, [TSL2591_CMD | 0x0c, 0x01]);
    await this._config();
  }

  async read() {
    const b = await i2cRead(this.device, this.address, TSL2591_CMD | 0x14, 4);
    if (!b) return null;
    const ch0 = (b[1] << 8) | b[0];
    const ch1 = (b[3] << 8) | b[2];
    const atime = 100 * this.timing + 100;
    const again = TSL2591_GAIN_MUL[this.gain >> 4];
    const cpl = (atime * again) / 408;
    const lux1 = (ch0 - 1.64 * ch1) / cpl;
    const lux2 = (0.59 * ch0 - 0.86 * ch1) / cpl;
    const raw = (ch1 << 16) | ch0;
    return { raw, lux: lux1, ir: lux2 };
  }
}

// ── VL53L0X ─────────────────────────────────────────────────────────

export class VL53L0XDriver {
  constructor(device, address = 0x29) {
    this.device = device;
    this.address = address;
  }

  async init() {
    return vl53l0xInit(this.device, this.address);
  }

  async read() {
    const mm = await vl53l0xReadRangeMm(this.device, this.address);
    if (mm === null) return null;
    return { mm };
  }
}

// ── AS5600 ──────────────────────────────────────────────────────────

export class AS5600Driver {
  constructor(device, address = 0x36) {
    this.device = device;
    this.address = address;
  }

  async init() {
    const b = await i2cRead(this.device, this.address, 0x00, 2);
    return Boolean(b);
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x0c, 2);
    if (!b) return null;
    const raw = ((b[0] & 0x0f) << 8) | b[1];
    return { angle: (raw * 360) / 4096 };
  }
}

// ── ATmega32 on-chip ADC (Port A) ───────────────────────────────────

export class Atmega32ADCDriver {
  constructor(device, channel = 0) {
    this.device = device;
    this.channel = (Number(channel) | 0) & 0x07;
  }

  setChannel(index) {
    this.channel = (Number(index) | 0) & 0x07;
  }

  async init() {
    return this.device.connected;
  }

  async read() {
    const raw = await this.device.readADC(this.channel);
    if (!Number.isFinite(raw)) return null;
    return { raw };
  }
}
