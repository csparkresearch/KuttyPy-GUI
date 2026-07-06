/**
 * I2C sensor identification — chip-ID probes for shared addresses.
 */

import { SENSOR_TYPES, sensorsAtAddress } from './sensors.js';

async function readByte(device, address, reg) {
  const { data, ok } = await device.i2cReadBulk(address, reg, 1);
  if (!ok || !data?.length) return null;
  return data[0];
}

/** @type {Record<string, (device: object, address: number) => Promise<number>>} */
const PROBES = {
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

  TSL2591: async (device, address) => {
    const id = await readByte(device, address, 0xb2); // CMD | ID_REG
    if (id === 0x50) return 100;
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

/**
 * Pick the best-matching sensor type at an I2C address (or null).
 * @returns {Promise<string|null>}
 */
export async function identifySensorAtAddress(device, address) {
  const candidates = sensorsAtAddress(address);
  if (!candidates.length) return null;

  if (address === 0x29) {
    const vl53 = await probeScore(device, 'VL53L0X', address);
    if (vl53 > 0) return 'VL53L0X';
    const tsl = await probeScore(device, 'TSL2591', address);
    if (tsl > 0) return 'TSL2591';
    return null;
  }

  if (candidates.length === 1) {
    const score = await probeScore(device, candidates[0].id, address);
    return score > 0 ? candidates[0].id : null;
  }

  let bestId = null;
  let bestScore = 0;
  for (const type of candidates) {
    const score = await probeScore(device, type.id, address);
    if (score > bestScore) {
      bestScore = score;
      bestId = type.id;
    }
  }
  return bestScore > 0 ? bestId : null;
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
