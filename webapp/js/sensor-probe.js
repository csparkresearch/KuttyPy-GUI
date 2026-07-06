/**
 * I2C sensor identification — chip-ID probes for shared addresses.
 */

import { SENSOR_TYPES, sensorsAtAddress } from './sensors.js';

async function readByte(device, address, reg) {
  const { data, ok } = await device.i2cReadBulk(address, reg, 1);
  if (!ok || !data?.length) return null;
  return data[0];
}

async function readWord(device, address, reg) {
  const { data, ok } = await device.i2cReadBulk(address, reg, 2);
  if (!ok || !data?.length) return null;
  return (data[0] << 8) | data[1];
}

/** @type {Record<string, (device: object, address: number) => Promise<number>>} */
const PROBES = {
  MTP10: async () => 95,

  BMP180: async (device, address) => {
    const id = await readByte(device, address, 0xd0);
    if (id === 0x55) return 100;
    return 0;
  },

  BMP280: async (device, address) => {
    const id = await readByte(device, address, 0xd0);
    if (id === 0x58 || id === 0x56 || id === 0x57) return 100;
    return 0;
  },

  BME280: async (device, address) => {
    const id = await readByte(device, address, 0xd0);
    if (id === 0x60) return 100;
    return 0;
  },

  AHT10: async (device, address) => {
    if (address !== 0x38 && address !== 0x39) return 0;
    const st = await readByte(device, address, 0x00);
    if (st === null) return 0;
    return (st & 0x80) === 0 ? 85 : 70;
  },

  TSL2591: async (device, address) => {
    const id = await readByte(device, address, 0xb2);
    if (id === 0x50) return 100;
    return 0;
  },

  TSL2561: async (device, address) => {
    const id = await readByte(device, address, 0x8a);
    if (id === 0x39 || id === 0x49 || id === 0x29) return 90;
    return 0;
  },

  TCS34725: async (device, address) => {
    const id = await readByte(device, address, 0x92);
    if (id === 0x44 || id === 0x4d) return 95;
    return 0;
  },

  VL53L0X: async (device, address) => {
    const id = await readByte(device, address, 0xc0);
    if (id === 0xee) return 100;
    return 0;
  },

  MPU6050: async (device, address) => {
    const id = await readByte(device, address, 0x75);
    if (id === 0x68 || id === 0x70 || id === 0x71 || id === 0x73) return 100;
    return 0;
  },

  ADXL345: async (device, address) => {
    const id = await readByte(device, address, 0x00);
    if (id === 0xe5) return 100;
    return 0;
  },

  HMC5883L: async (device, address) => {
    const idA = await readByte(device, address, 0x0a);
    if (idA === 0x48) return 100;
    return 0;
  },

  QMC5883L: async (device, address) => {
    const id = await readByte(device, address, 0x0d);
    if (id === 0xff) return 100;
    return 0;
  },

  AS5600: async (device, address) => {
    const fw = await readByte(device, address, 0xfe);
    if (fw === 0x41) return 100;
    const { ok } = await device.i2cReadBulk(address, 0x0c, 2);
    return ok ? 35 : 0;
  },

  BH1750: async () => 60,

  MLX90614: async (device, address) => {
    const vals = await device.i2cReadBulk(address, 0x07, 3);
    if (!vals.ok || !vals.data || vals.data.length < 3) return 0;
    const temp = ((((vals.data[1] & 0x7f) << 8) + vals.data[0]) * 0.02) - 273.15;
    return temp > -50 && temp < 400 ? 80 : 0;
  },

  INA219: async (device, address) => {
    const mfg = await readWord(device, address, 0xfe);
    if (mfg === 0x5449) return 100;
    if (address >= 0x40 && address <= 0x4f) return 55;
    return 0;
  },

  MAX30100: async (device, address) => {
    const id = await readByte(device, address, 0xff);
    if (id === 0x11) return 100;
    const rev = await readByte(device, address, 0xfe);
    if (rev === 0x11) return 90;
    return 0;
  },

  ADS1115: async (device, address) => {
    if (address >= 0x48 && address <= 0x4b) return 70;
    return 0;
  },
};

async function probeScore(device, typeId, address) {
  const fn = PROBES[typeId];
  if (!fn) return 50;
  try {
    return await fn(device, address);
  } catch {
    return 0;
  }
}

async function pickBest(device, typeIds, address) {
  let bestId = null;
  let bestScore = 0;
  for (const typeId of typeIds) {
    const score = await probeScore(device, typeId, address);
    if (score > bestScore) {
      bestScore = score;
      bestId = typeId;
    }
  }
  return bestScore > 0 ? bestId : null;
}

/**
 * Pick the best-matching sensor type at an I2C address (or null).
 * @returns {Promise<string|null>}
 */
export async function identifySensorAtAddress(device, address) {
  const candidates = sensorsAtAddress(address);
  if (!candidates.length) return null;

  if (address === 0x7f) return 'MTP10';

  if (address === 0x29) {
    const order = ['VL53L0X', 'TSL2591', 'TCS34725', 'TSL2561'];
    return pickBest(device, order, address);
  }

  if (address === 0x39 || address === 0x49) {
    const order = ['TSL2561', 'TCS34725', 'AHT10'];
    return pickBest(device, order, address);
  }

  if (address === 0x76 || address === 0x77) {
    const bme = await probeScore(device, 'BME280', address);
    if (bme > 0) return 'BME280';
    const bmp = await probeScore(device, 'BMP280', address);
    if (bmp > 0) return 'BMP280';
    const bmp180 = await probeScore(device, 'BMP180', address);
    if (bmp180 > 0) return 'BMP180';
    return null;
  }

  if (address === 0x40 || address === 0x41) {
    const ina = await probeScore(device, 'INA219', address);
    if (ina >= 90) return 'INA219';
  }

  if (candidates.length === 1) {
    const score = await probeScore(device, candidates[0].id, address);
    return score > 0 ? candidates[0].id : null;
  }

  return pickBest(device, candidates.map((c) => c.id), address);
}

/**
 * @param {object} device
 * @param {number[]} addresses
 * @returns {Promise<{ typeId: string, address: number }[]>}
 */
export async function identifyDetectedSensors(device, addresses) {
  const found = [];
  for (const address of addresses) {
    const typeId = await identifySensorAtAddress(device, address);
    if (typeId) found.push({ typeId, address });
  }
  return found;
}

export function sensorMeta(typeId) {
  return SENSOR_TYPES[typeId] ?? null;
}
