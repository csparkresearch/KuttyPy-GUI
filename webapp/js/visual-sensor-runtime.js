/**
 * Sensor driver cache for visual program execution.
 */

import { createSensorDriver, SENSOR_TYPES } from './sensors.js';

export class VisualSensorManager {
  constructor(device) {
    this.device = device;
    /** @type {Map<string, { driver: object }>} */
    this.entries = new Map();
  }

  clear() {
    this.entries.clear();
  }

  async _applyConfig(driver, typeId, configIndices) {
    const meta = SENSOR_TYPES[typeId];
    if (!meta) return;

    for (const cfg of meta.config) {
      const idx = configIndices[cfg.key];
      const index = idx === undefined ? (cfg.defaultIndex ?? 0) : Number(idx);
      const method = driver[cfg.method];
      if (typeof method === 'function') {
        method.call(driver, index);
      }
    }
  }

  async _getReading(blockId, typeId, address, configIndices) {
    if (!this.device?.connected) {
      throw new Error('USB not connected — sensor read requires hardware');
    }

    const meta = SENSOR_TYPES[typeId];
    if (!meta) throw new Error(`Unknown sensor type ${typeId}`);

    const key = `${blockId}|${typeId}|${address}|${JSON.stringify(configIndices)}`;
    let entry = this.entries.get(key);

    if (!entry) {
      const options = {};
      if (!meta.addresses.length) {
        const chIdx = configIndices.channel;
        options.channel = chIdx === undefined ? 0 : Number(chIdx);
      }

      const driver = createSensorDriver(typeId, this.device, address, options);
      if (!driver) throw new Error(`No driver for ${typeId}`);

      await this._applyConfig(driver, typeId, configIndices);
      if (typeof driver.init === 'function') {
        await driver.init();
        await this._applyConfig(driver, typeId, configIndices);
      }

      entry = { driver };
      this.entries.set(key, entry);
    }

    return entry.driver.read();
  }

  /** @param {string[]} fieldKeys */
  async readFields(blockId, typeId, address, fieldKeys, configIndices) {
    const reading = await this._getReading(blockId, typeId, address, configIndices);
    const keys = Array.isArray(fieldKeys) && fieldKeys.length
      ? fieldKeys
      : Object.keys(reading);

    if (keys.length === 1) {
      const k = keys[0];
      if (!(k in reading)) throw new Error(`Sensor ${typeId} has no reading "${k}"`);
      return reading[k];
    }

    const out = {};
    for (const k of keys) {
      if (!(k in reading)) {
        throw new Error(`Sensor ${typeId} has no reading "${k}"`);
      }
      const label = SENSOR_TYPES[typeId]?.fields?.find((f) => f.key === k)?.label || k;
      out[label] = reading[k];
    }
    return out;
  }
}
