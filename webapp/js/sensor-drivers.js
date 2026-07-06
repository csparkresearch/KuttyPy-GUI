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

export function sign24(v) {
  return v >= 0x800000 ? v - 0x1000000 : v;
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

  async setGain(i) {
    this.gainIndex = Math.max(0, Math.min(7, 7 - (i | 0)));
    await i2cWrite(this.device, this.address, [0x01, this.gainIndex << 5]);
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
    await this.setRange(1);
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

// ── MTP10-A6F55 PIR thermometer ─────────────────────────────────────

export class MTP10Driver {
  constructor(device, address = 0x7f) {
    this.device = device;
    this.address = address;
    this.currentGain = 0x05;
    this.currentOsr = 0x07;
  }

  async _updateHardware() {
    const chan1 = (0x00 << 7) | (this.currentGain << 3) | this.currentOsr;
    await i2cWrite(this.device, this.address, [0x95, chan1]);
    const cmdOff = (0x00 << 5) | (0x00 << 4) | (0x00 << 3) | 0x02;
    const cmdOn = (0x00 << 5) | (0x00 << 4) | (0x01 << 3) | 0x02;
    await i2cWrite(this.device, this.address, [0x30, cmdOff]);
    await i2cWrite(this.device, this.address, [0x30, cmdOn]);
  }

  async setGain(val) {
    if (val >= 0 && val <= 7) {
      this.currentGain = val;
      await this._updateHardware();
    }
  }

  async setOsr(val) {
    const osrLookup = [0x04, 0x05, 0x00, 0x01, 0x02, 0x03, 0x06, 0x07];
    if (val >= 0 && val < osrLookup.length) {
      this.currentOsr = osrLookup[val];
      await this._updateHardware();
    }
  }

  async init() {
    await i2cWrite(this.device, this.address, [0x93, 0x07]);
    await i2cWrite(this.device, this.address, [0x94, 0x80]);
    await i2cWrite(this.device, this.address, [0x97, 0x0d]);
    await this._updateHardware();
  }

  async read() {
    const status = await i2cRead(this.device, this.address, 0x02, 1);
    if (!status || (status[0] & 0x08) !== 0x08) return null;
    const pVals = await i2cRead(this.device, this.address, 0x10, 9);
    const rVals = await i2cRead(this.device, this.address, 0x22, 3);
    if (!pVals || pVals.length < 9 || !rVals || rVals.length < 3) return null;
    const toRaw = sign24((pVals[0] << 16) | (pVals[1] << 8) | pVals[2]);
    const taRaw = sign24((pVals[6] << 16) | (pVals[7] << 8) | pVals[8]);
    const irRaw = sign24((rVals[0] << 16) | (rVals[1] << 8) | rVals[2]);
    await i2cWrite(this.device, this.address, [0x02, 0xff, 0xff]);
    return {
      objectTemp: toRaw / 16384.0,
      ambientTemp: taRaw / 16384.0,
      rawVoltage: irRaw / 10000.0,
    };
  }
}

// ── TSL2561 ─────────────────────────────────────────────────────────

export class TSL2561Driver {
  constructor(device, address = 0x39) {
    this.device = device;
    this.address = address;
    this.gain = 0;
    this.timing = 0;
  }

  async _config() {
    await i2cWrite(this.device, this.address, [0x81, this.gain | this.timing]);
  }

  async setGain(i) {
    this.gain = (i & 1) << 4;
    await this._config();
  }

  async setTiming(i) {
    this.timing = Math.max(0, Math.min(2, i | 0));
    await this._config();
  }

  async init() {
    await i2cWrite(this.device, this.address, [0x80, 0x03]);
    await this._config();
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x8c, 4);
    if (!b) return null;
    return {
      total: (b[1] << 8) | b[0],
      ir: (b[3] << 8) | b[2],
    };
  }
}

// ── MLX90614 ────────────────────────────────────────────────────────

export class MLX90614Driver {
  constructor(device, address = 0x5a) {
    this.device = device;
    this.address = address;
  }

  async init() {}

  async read() {
    const vals = await i2cRead(this.device, this.address, 0x07, 3);
    if (!vals || vals.length < 3) return null;
    const temp = ((((vals[1] & 0x7f) << 8) + vals[0]) * 0.02) - 0.01 - 273.15;
    return { temp };
  }
}

// ── TCS34725 ────────────────────────────────────────────────────────

const TCS34725_CMD = 0x80;
const TCS34725_ENABLE = 0x00;
const TCS34725_ATIME = 0x01;
const TCS34725_APERS = 0x0c;
const TCS34725_CONTROL = 0x0f;
const TCS34725_RDATA = 0x16;
const TCS34725_GDATA = 0x18;
const TCS34725_BDATA = 0x1a;
const TCS34725_PON = 0x01;
const TCS34725_AEN = 0x02;
const TCS34725_AIEN = 0x10;

export class TCS34725Driver {
  constructor(device, address = 0x29) {
    this.device = device;
    this.address = address;
  }

  async setGain(g) {
    await i2cWrite(this.device, this.address, [TCS34725_CMD | TCS34725_CONTROL, g & 3]);
  }

  async init() {
    const en = await i2cRead(this.device, this.address, TCS34725_CMD | TCS34725_ENABLE, 1);
    const enable = en ? en[0] : 0;
    await i2cWrite(this.device, this.address, [TCS34725_CMD | TCS34725_ENABLE, enable | TCS34725_PON]);
    await delay(3);
    await i2cWrite(this.device, this.address, [
      TCS34725_CMD | TCS34725_ENABLE,
      enable | TCS34725_PON | TCS34725_AEN | TCS34725_AIEN,
    ]);
    await i2cWrite(this.device, this.address, [TCS34725_CMD | TCS34725_APERS, 10]);
    await i2cWrite(this.device, this.address, [TCS34725_CMD | TCS34725_ATIME, 256 - 40]);
  }

  async read() {
    const r = await i2cRead(this.device, this.address, TCS34725_CMD | TCS34725_RDATA, 2);
    const g = await i2cRead(this.device, this.address, TCS34725_CMD | TCS34725_GDATA, 2);
    const b = await i2cRead(this.device, this.address, TCS34725_CMD | TCS34725_BDATA, 2);
    if (!r || !g || !b) return null;
    return {
      red: r[0] | (r[1] << 8),
      green: g[0] | (g[1] << 8),
      blue: b[0] | (b[1] << 8),
    };
  }
}

// ── AHT10 / AHT21 ───────────────────────────────────────────────────

export class AHT10Driver {
  constructor(device, address = 0x38) {
    this.device = device;
    this.address = address;
  }

  async init() {
    await i2cWrite(this.device, this.address, [0xbe, 0x08, 0x00]);
    await delay(10);
  }

  async read() {
    await i2cWrite(this.device, this.address, [0xac, 0x33, 0x00]);
    await delay(80);
    const buf = await i2cRead(this.device, this.address, 0x00, 6);
    if (!buf || buf.length < 6) return null;
    const hum = (buf[1] << 12) | (buf[2] << 4) | (buf[3] >> 4);
    const humidity = (hum * 100.0) / 0x100000;
    const tempRaw = ((buf[3] & 0x0f) << 16) | (buf[4] << 8) | buf[5];
    const temp = (tempRaw * 200.0) / 0x100000 - 50;
    return { humidity, temp };
  }
}

// ── INA219 ──────────────────────────────────────────────────────────

const INA219_PG_LSB = [0.00001, 0.00002, 0.00004, 0.00008];

export class INA219Driver {
  constructor(device, address = 0x40) {
    this.device = device;
    this.address = address;
    this.gainIndex = 0;
    this.bus32V = true;
    this.shuntOhms = 0.1;
    this.maxCurrent = 3.2;
    this.calValue = 4096;
    this.currentLSB = 0.0001;
  }

  async _writeReg(reg, value) {
    await i2cWrite(this.device, this.address, [reg, (value >> 8) & 0xff, value & 0xff]);
  }

  async _calibrate() {
    this.currentLSB = this.maxCurrent / 32768;
    this.calValue = Math.trunc(0.04096 / (this.currentLSB * this.shuntOhms));
    if (this.calValue < 1) this.calValue = 1;
    await this._writeReg(0x05, this.calValue);
  }

  async _writeConfig() {
    const brng = this.bus32V ? (1 << 13) : 0;
    const pg = (3 - this.gainIndex) << 11;
    const config = 0x399f | brng | pg;
    await this._writeReg(0x00, config);
  }

  async setGain(i) {
    this.gainIndex = Math.max(0, Math.min(3, i | 0));
    await this._writeConfig();
    await this._calibrate();
  }

  async setBusRange(i) {
    this.bus32V = i === 1;
    await this._writeConfig();
  }

  async init() {
    await this._writeConfig();
    await this._calibrate();
  }

  async read() {
    const sv = await i2cRead(this.device, this.address, 0x01, 2);
    const bv = await i2cRead(this.device, this.address, 0x02, 2);
    const cur = await i2cRead(this.device, this.address, 0x04, 2);
    if (!sv || !bv) return null;
    let shunt = (sv[0] << 8) | sv[1];
    if (shunt & 0x8000) shunt -= 65536;
    let bus = (bv[0] << 8) | bv[1];
    bus >>= 3;
    if (bus & 0x2000) bus -= 8192;
    const shuntV = shunt * INA219_PG_LSB[this.gainIndex];
    const busV = bus * 0.004;
    let current = shuntV / this.shuntOhms;
    if (cur) {
      let raw = (cur[0] << 8) | cur[1];
      if (raw & 0x8000) raw -= 65536;
      current = raw * this.currentLSB;
    }
    return { current, voltage: busV, power: busV * current };
  }
}

// ── MAX30100 ────────────────────────────────────────────────────────

export class MAX30100Driver {
  constructor(device, address = 0x57) {
    this.device = device;
    this.address = address;
    this.ledCurrent = 0x0f;
  }

  async setLedCurrent(i) {
    this.ledCurrent = Math.max(0, Math.min(0x0f, i | 0));
    await i2cWrite(this.device, this.address, [0x0c, this.ledCurrent << 4 | this.ledCurrent]);
  }

  async init() {
    await i2cWrite(this.device, this.address, [0x09, 0x40]);
    await delay(100);
    await i2cWrite(this.device, this.address, [0x09, 0x03]);
    await i2cWrite(this.device, this.address, [0x0a, 0x3f]);
    await this.setLedCurrent(this.ledCurrent);
  }

  async read() {
    const st = await i2cRead(this.device, this.address, 0x00, 1);
    if (!st) return null;
    const d = await i2cRead(this.device, this.address, 0x07, 6);
    if (!d) return null;
    const ir = ((d[0] & 0x03) << 16) | (d[1] << 8) | d[2];
    const red = ((d[3] & 0x03) << 16) | (d[4] << 8) | d[5];
    return { ir, red };
  }
}

// ── ADXL345 ─────────────────────────────────────────────────────────

const ADXL345_SCALE = [0.0039, 0.0078, 0.0156, 0.0312];

export class ADXL345Driver {
  constructor(device, address = 0x53) {
    this.device = device;
    this.address = address;
    this.rangeIndex = 0;
  }

  async setRange(i) {
    this.rangeIndex = Math.max(0, Math.min(3, i | 0));
    await i2cWrite(this.device, this.address, [0x31, this.rangeIndex]);
  }

  async init() {
    await i2cWrite(this.device, this.address, [0x2d, 0x08]);
    await this.setRange(0);
  }

  async read() {
    const b = await i2cRead(this.device, this.address, 0x32, 6);
    if (!b) return null;
    const scale = ADXL345_SCALE[this.rangeIndex];
    return {
      ax: signit((b[0] << 8) | b[1]) * scale,
      ay: signit((b[2] << 8) | b[3]) * scale,
      az: signit((b[4] << 8) | b[5]) * scale,
    };
  }
}

// ── Analog pin sensors (ML8511, AD8232) ─────────────────────────────

export class AnalogPinDriver {
  constructor(device, channel = 0, { vref = 5.0, scale = 1, offset = 0 } = {}) {
    this.device = device;
    this.channel = (Number(channel) | 0) & 0x07;
    this.vref = vref;
    this.scale = scale;
    this.offset = offset;
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
    const voltage = (raw / 1023) * this.vref;
    return { value: voltage * this.scale + this.offset, raw };
  }
}

export class ML8511Driver extends AnalogPinDriver {
  constructor(device, channel = 0) {
    super(device, channel, { scale: 10 });
  }

  async read() {
    const r = await super.read();
    if (!r) return null;
    return { uv: Math.max(0, r.value), raw: r.raw };
  }
}

export class AD8232Driver extends AnalogPinDriver {
  constructor(device, channel = 0) {
    super(device, channel);
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
