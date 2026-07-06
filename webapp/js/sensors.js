/**
 * Supported I2C sensor registry and driver factory.
 */

import {
  BMP180Driver,
  ADS1115Driver,
  MPU6050Driver,
  HMC5883LDriver,
  QMC5883LDriver,
  BMP280Driver,
  BH1750Driver,
  TSL2591Driver,
  VL53L0XDriver,
  AS5600Driver,
  Atmega32ADCDriver,
} from './sensor-drivers.js';

/** @typedef {{ key: string, label: string, unit: string, min: number, max: number }} SensorField */
/** @typedef {{ key: string, label: string, options: string[], method: string, defaultIndex?: number }} SensorConfig */

/** @type {Record<string, { id: string, name: string, addresses: number[], icon: string, fields: SensorField[], config: SensorConfig[] }>} */
export const SENSOR_TYPES = {
  BMP180: {
    id: 'BMP180',
    name: 'BMP180',
    addresses: [0x77],
    icon: 'BMP180.jpeg',
    fields: [
      { key: 'pressure', label: 'Pressure', unit: 'hPa', min: 300, max: 1100 },
      { key: 'temp', label: 'Temperature', unit: '°C', min: -40, max: 85 },
    ],
    config: [{
      key: 'oversampling', label: 'Oversampling', options: ['0', '1', '2', '3'],
      method: 'setOversampling', defaultIndex: 0,
    }],
  },
  ADS1115: {
    id: 'ADS1115',
    name: 'ADS1115',
    addresses: [0x48, 0x49, 0x4a, 0x4b],
    icon: 'ADS1115.jpeg',
    fields: [{ key: 'voltage', label: 'Voltage', unit: 'V', min: -6.144, max: 6.144 }],
    config: [
      { key: 'channel', label: 'Channel', options: ['UNI_0', 'UNI_1', 'UNI_2', 'UNI_3', 'DIFF_01', 'DIFF_23'], method: 'setChannel', defaultIndex: 0 },
      { key: 'rate', label: 'Data rate', options: ['8', '16', '32', '64', '128', '250', '475', '860'], method: 'setRate', defaultIndex: 5 },
      { key: 'gain', label: 'Gain', options: ['2/3', '1', '2', '4', '8', '16'], method: 'setGain', defaultIndex: 1 },
    ],
  },
  MPU6050: {
    id: 'MPU6050',
    name: 'MPU6050',
    addresses: [0x68, 0x69],
    icon: 'MPU6050.jpeg',
    fields: [
      { key: 'ax', label: 'Ax', unit: 'LSB', min: -32768, max: 32767 },
      { key: 'ay', label: 'Ay', unit: 'LSB', min: -32768, max: 32767 },
      { key: 'az', label: 'Az', unit: 'LSB', min: -32768, max: 32767 },
      { key: 'temp', label: 'Temp', unit: 'LSB', min: 0, max: 65535 },
      { key: 'gx', label: 'Gx', unit: 'LSB', min: -32768, max: 32767 },
      { key: 'gy', label: 'Gy', unit: 'LSB', min: -32768, max: 32767 },
      { key: 'gz', label: 'Gz', unit: 'LSB', min: -32768, max: 32767 },
    ],
    config: [
      { key: 'gyro', label: 'Gyro range', options: ['250', '500', '1000', '2000'], method: 'setGyroRange', defaultIndex: 0 },
      { key: 'accel', label: 'Accel range', options: ['2g', '4g', '8g', '16g'], method: 'setAccelRange', defaultIndex: 0 },
    ],
  },
  HMC5883L: {
    id: 'HMC5883L',
    name: 'HMC5883L',
    addresses: [0x1e, 0x3c, 0x3d],
    icon: 'HMC5883L.jpeg',
    fields: [
      { key: 'mx', label: 'Mx', unit: 'G', min: -8, max: 8 },
      { key: 'my', label: 'My', unit: 'G', min: -8, max: 8 },
      { key: 'mz', label: 'Mz', unit: 'G', min: -8, max: 8 },
    ],
    config: [],
  },
  QMC5883L: {
    id: 'QMC5883L',
    name: 'QMC5883L',
    addresses: [0x0d, 0x13],
    icon: 'QMC5883L.jpeg',
    fields: [
      { key: 'mx', label: 'Mx', unit: 'G', min: -8, max: 8 },
      { key: 'my', label: 'My', unit: 'G', min: -8, max: 8 },
      { key: 'mz', label: 'Mz', unit: 'G', min: -8, max: 8 },
      { key: 'heading', label: 'Heading', unit: '°', min: -180, max: 180 },
    ],
    config: [{
      key: 'range', label: 'Range', options: ['2G', '8G'], method: 'setRange', defaultIndex: 1,
    }],
  },
  TSL2591: {
    id: 'TSL2591',
    name: 'TSL2591',
    addresses: [0x29],
    icon: 'TSL2561.jpeg',
    fields: [
      { key: 'raw', label: 'Raw', unit: 'cnt', min: 0, max: 37889 },
      { key: 'lux', label: 'Lux', unit: 'lx', min: 0, max: 88000 },
      { key: 'ir', label: 'IR lux', unit: 'lx', min: 0, max: 88000 },
    ],
    config: [
      { key: 'gain', label: 'Gain', options: ['1x', '25x', '428x', '9876x'], method: 'setGain', defaultIndex: 0 },
      { key: 'timing', label: 'Integration', options: ['100ms', '200ms', '300ms', '400ms', '500ms', '600ms'], method: 'setTiming', defaultIndex: 0 },
    ],
  },
  AS5600: {
    id: 'AS5600',
    name: 'AS5600',
    addresses: [0x36],
    icon: 'undefined.jpeg',
    fields: [{ key: 'angle', label: 'Angle', unit: '°', min: 0, max: 360 }],
    config: [],
  },
  BMP280: {
    id: 'BMP280',
    name: 'BMP280',
    addresses: [0x76, 0x77],
    icon: 'BMP280.jpeg',
    fields: [
      { key: 'pressure', label: 'Pressure', unit: 'hPa', min: 300, max: 1100 },
      { key: 'temp', label: 'Temperature', unit: '°C', min: -40, max: 85 },
    ],
    config: [],
  },
  BME280: {
    id: 'BME280',
    name: 'BME280',
    addresses: [0x76, 0x77],
    icon: 'BMP280.jpeg',
    fields: [
      { key: 'pressure', label: 'Pressure', unit: 'hPa', min: 300, max: 1100 },
      { key: 'temp', label: 'Temperature', unit: '°C', min: -40, max: 85 },
      { key: 'humidity', label: 'Humidity', unit: '%', min: 0, max: 100 },
    ],
    config: [],
  },
  VL53L0X: {
    id: 'VL53L0X',
    name: 'VL53L0X',
    addresses: [0x29],
    icon: 'VL53L0X.jpeg',
    fields: [{ key: 'mm', label: 'Distance', unit: 'mm', min: 0, max: 2000 }],
    config: [],
  },
  BH1750: {
    id: 'BH1750',
    name: 'BH1750',
    addresses: [0x23],
    icon: 'BH1750.jpeg',
    fields: [{ key: 'lux', label: 'Lux', unit: 'lx', min: 0, max: 65535 }],
    config: [{
      key: 'gain', label: 'Sensitivity', options: ['500 mlx', '1000 mlx', '4000 mlx'], method: 'setGain', defaultIndex: 0,
    }],
  },
  ATMEGA32_ADC: {
    id: 'ATMEGA32_ADC',
    name: 'ATmega32 ADC',
    addresses: [],
    icon: 'gauge.gif',
    iconPath: 'images/gauge.gif',
    fields: [{ key: 'raw', label: 'PA0', unit: 'LSB', min: 0, max: 1023 }],
    config: [{
      key: 'channel',
      label: 'Channel',
      options: [
        'PA0 (ADC0)', 'PA1 (ADC1)', 'PA2 (ADC2)', 'PA3 (ADC3)',
        'PA4 (ADC4)', 'PA5 (ADC5)', 'PA6 (ADC6)', 'PA7 (ADC7)',
      ],
      method: 'setChannel',
      defaultIndex: 0,
    }],
  },
};

const ADDRESS_MAP = new Map();
for (const type of Object.values(SENSOR_TYPES)) {
  for (const addr of type.addresses) {
    if (!ADDRESS_MAP.has(addr)) ADDRESS_MAP.set(addr, []);
    ADDRESS_MAP.get(addr).push(type.id);
  }
}

export function sensorsAtAddress(addr) {
  return (ADDRESS_MAP.get(addr) || []).map((id) => SENSOR_TYPES[id]);
}

const DRIVER_MAP = {
  BMP180: BMP180Driver,
  ADS1115: ADS1115Driver,
  MPU6050: MPU6050Driver,
  HMC5883L: HMC5883LDriver,
  QMC5883L: QMC5883LDriver,
  BMP280: BMP280Driver,
  BME280: BMP280Driver,
  BH1750: BH1750Driver,
  TSL2591: TSL2591Driver,
  VL53L0X: VL53L0XDriver,
  AS5600: AS5600Driver,
};

export function createSensorDriver(typeId, device, address, options = {}) {
  if (typeId === 'ATMEGA32_ADC') {
    return new Atmega32ADCDriver(device, options.channel ?? 0);
  }
  const Cls = DRIVER_MAP[typeId];
  return Cls ? new Cls(device, address) : null;
}
