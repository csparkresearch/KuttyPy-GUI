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
  MTP10Driver,
  TSL2561Driver,
  MLX90614Driver,
  TCS34725Driver,
  AHT10Driver,
  INA219Driver,
  MAX30100Driver,
  ADXL345Driver,
  ML8511Driver,
  AD8232Driver,
  Atmega32ADCDriver,
} from './sensor-drivers.js';

/** @typedef {{ key: string, label: string, unit: string, min: number, max: number }} SensorField */
/** @typedef {{ key: string, label: string, options: string[], method: string, defaultIndex?: number }} SensorConfig */

const ADC_CHANNEL_OPTS = [
  'PA0 (ADC0)', 'PA1 (ADC1)', 'PA2 (ADC2)', 'PA3 (ADC3)',
  'PA4 (ADC4)', 'PA5 (ADC5)', 'PA6 (ADC6)', 'PA7 (ADC7)',
];

/** @type {Record<string, { id: string, name: string, addresses: number[], icon: string, iconPath?: string, fields: SensorField[], config: SensorConfig[] }>} */
export const SENSOR_TYPES = {
  MTP10: {
    id: 'MTP10',
    name: 'MTP10-A6F55',
    addresses: [0x7f],
    icon: 'THERMOMETER.png',
    fields: [
      { key: 'objectTemp', label: 'Object Temp', unit: 'degC', min: -40, max: 300 },
      { key: 'ambientTemp', label: 'Ambient T', unit: 'degC', min: -40, max: 85 },
      { key: 'rawVoltage', label: 'Raw Voltage', unit: 'V', min: -8, max: 8 },
    ],
    config: [
      { key: 'gain', label: 'Gain', options: ['8x', '12x', '16x', '32x', '48x', '64x', '96x', '128x'], method: 'setGain', defaultIndex: 5 },
      { key: 'osr', label: 'OSR', options: ['128x', '256x', '512x', '1024x', '2048x', '4096x', '8192x', '16384x'], method: 'setOsr', defaultIndex: 7 },
    ],
  },
  BMP180: {
    id: 'BMP180',
    name: 'BMP180',
    addresses: [0x77],
    icon: 'BMP180.jpeg',
    fields: [
      { key: 'pressure', label: 'Pressure', unit: 'hPa', min: 300, max: 1100 },
      { key: 'temp', label: 'Temperature', unit: 'degC', min: -40, max: 85 },
    ],
    config: [{
      key: 'oversampling', label: 'Oversampling', options: ['0', '1', '2', '3'],
      method: 'setOversampling', defaultIndex: 0,
    }],
  },
  BME280: {
    id: 'BME280',
    name: 'BME280',
    addresses: [0x76, 0x77],
    icon: 'BMP280.jpeg',
    fields: [
      { key: 'pressure', label: 'Pressure', unit: 'hPa', min: 300, max: 1100 },
      { key: 'temp', label: 'Temperature', unit: 'degC', min: -40, max: 85 },
      { key: 'humidity', label: 'Humidity', unit: '%', min: 0, max: 100 },
    ],
    config: [],
  },
  BMP280: {
    id: 'BMP280',
    name: 'BMP280',
    addresses: [0x76, 0x77],
    icon: 'BMP280.jpeg',
    fields: [
      { key: 'pressure', label: 'Pressure', unit: 'hPa', min: 300, max: 1100 },
      { key: 'temp', label: 'Temperature', unit: 'degC', min: -40, max: 85 },
    ],
    config: [],
  },
  AHT10: {
    id: 'AHT10',
    name: 'AHT10',
    addresses: [0x38, 0x39],
    icon: 'AHT10.jpeg',
    fields: [
      { key: 'humidity', label: 'Humidity', unit: '%', min: 0, max: 100 },
      { key: 'temp', label: 'Temperature', unit: 'degC', min: -40, max: 85 },
    ],
    config: [],
  },
  TSL2561: {
    id: 'TSL2561',
    name: 'TSL2561',
    addresses: [0x29, 0x39, 0x49],
    icon: 'TSL2561.jpeg',
    fields: [
      { key: 'total', label: 'Total', unit: 'cnt', min: 0, max: 32767 },
      { key: 'ir', label: 'IR', unit: 'cnt', min: 0, max: 32767 },
    ],
    config: [
      { key: 'gain', label: 'Gain', options: ['1x', '16x'], method: 'setGain', defaultIndex: 0 },
      { key: 'timing', label: 'Integration', options: ['3ms', '101ms', '402ms'], method: 'setTiming', defaultIndex: 0 },
    ],
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
  TCS34725: {
    id: 'TCS34725',
    name: 'TCS34725',
    addresses: [0x29, 0x39, 0x49],
    icon: 'TCS34725.jpeg',
    fields: [
      { key: 'red', label: 'Red', unit: 'cnt', min: 0, max: 65535 },
      { key: 'green', label: 'Green', unit: 'cnt', min: 0, max: 65535 },
      { key: 'blue', label: 'Blue', unit: 'cnt', min: 0, max: 65535 },
    ],
    config: [{
      key: 'gain', label: 'Gain', options: ['1x', '4x', '16x', '60x'], method: 'setGain', defaultIndex: 0,
    }],
  },
  MLX90614: {
    id: 'MLX90614',
    name: 'MLX90614',
    addresses: [0x5a],
    icon: 'MLX90614.jpeg',
    fields: [{ key: 'temp', label: 'Temperature', unit: 'degC', min: -40, max: 350 }],
    config: [],
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
    config: [{
      key: 'gain', label: 'Gain', options: ['±0.88G', '±1.3G', '±1.9G', '±2.5G', '±4.0G', '±4.7G', '±5.6G', '±8.1G'],
      method: 'setGain', defaultIndex: 0,
    }],
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
      { key: 'heading', label: 'Heading', unit: 'deg', min: -180, max: 180 },
    ],
    config: [{
      key: 'range', label: 'Range', options: ['2G', '8G'], method: 'setRange', defaultIndex: 1,
    }],
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
  ADXL345: {
    id: 'ADXL345',
    name: 'ADXL345',
    addresses: [0x53, 0x1d],
    icon: 'ADXL345.jpeg',
    fields: [
      { key: 'ax', label: 'Ax', unit: 'g', min: -16, max: 16 },
      { key: 'ay', label: 'Ay', unit: 'g', min: -16, max: 16 },
      { key: 'az', label: 'Az', unit: 'g', min: -16, max: 16 },
    ],
    config: [{
      key: 'range', label: 'Range', options: ['±2g', '±4g', '±8g', '±16g'], method: 'setRange', defaultIndex: 0,
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
  INA219: {
    id: 'INA219',
    name: 'INA219',
    addresses: [0x40, 0x41, 0x44, 0x45],
    icon: 'INA219.jpeg',
    fields: [
      { key: 'current', label: 'Current', unit: 'A', min: -3.2, max: 3.2 },
      { key: 'voltage', label: 'Bus V', unit: 'V', min: 0, max: 32 },
      { key: 'power', label: 'Power', unit: 'W', min: 0, max: 100 },
    ],
    config: [
      { key: 'gain', label: 'Shunt gain', options: ['±40mV', '±80mV', '±160mV', '±320mV'], method: 'setGain', defaultIndex: 0 },
      { key: 'bus', label: 'Bus range', options: ['16V', '32V'], method: 'setBusRange', defaultIndex: 1 },
    ],
  },
  MAX30100: {
    id: 'MAX30100',
    name: 'MAX30100',
    addresses: [0x57],
    icon: 'MAX30100.jpeg',
    fields: [
      { key: 'ir', label: 'IR', unit: 'cnt', min: 0, max: 262143 },
      { key: 'red', label: 'Red', unit: 'cnt', min: 0, max: 262143 },
    ],
    config: [{
      key: 'led', label: 'LED current', options: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'],
      method: 'setLedCurrent', defaultIndex: 15,
    }],
  },
  VL53L0X: {
    id: 'VL53L0X',
    name: 'VL53L0X',
    addresses: [0x29],
    icon: 'VL53L0X.jpeg',
    fields: [{ key: 'mm', label: 'Distance', unit: 'mm', min: 0, max: 2000 }],
    config: [],
  },
  AS5600: {
    id: 'AS5600',
    name: 'AS5600',
    addresses: [0x36],
    icon: 'undefined.jpeg',
    fields: [{ key: 'angle', label: 'Angle', unit: 'deg', min: 0, max: 360 }],
    config: [],
  },
  ML8511: {
    id: 'ML8511',
    name: 'ML8511 UV',
    addresses: [],
    icon: 'MAX44009.jpeg',
    fields: [
      { key: 'uv', label: 'UV index', unit: 'idx', min: 0, max: 15 },
      { key: 'raw', label: 'ADC', unit: 'LSB', min: 0, max: 1023 },
    ],
    config: [{
      key: 'channel', label: 'ADC channel', options: ADC_CHANNEL_OPTS, method: 'setChannel', defaultIndex: 0,
    }],
  },
  AD8232: {
    id: 'AD8232',
    name: 'AD8232 ECG',
    addresses: [],
    icon: 'pulse.png',
    fields: [
      { key: 'value', label: 'Signal', unit: 'V', min: 0, max: 5 },
      { key: 'raw', label: 'ADC', unit: 'LSB', min: 0, max: 1023 },
    ],
    config: [{
      key: 'channel', label: 'ADC channel', options: ADC_CHANNEL_OPTS, method: 'setChannel', defaultIndex: 0,
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
      options: ADC_CHANNEL_OPTS,
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
  MTP10: MTP10Driver,
  BMP180: BMP180Driver,
  ADS1115: ADS1115Driver,
  MPU6050: MPU6050Driver,
  HMC5883L: HMC5883LDriver,
  QMC5883L: QMC5883LDriver,
  BMP280: BMP280Driver,
  BME280: BMP280Driver,
  BH1750: BH1750Driver,
  TSL2591: TSL2591Driver,
  TSL2561: TSL2561Driver,
  VL53L0X: VL53L0XDriver,
  AS5600: AS5600Driver,
  MLX90614: MLX90614Driver,
  TCS34725: TCS34725Driver,
  AHT10: AHT10Driver,
  INA219: INA219Driver,
  MAX30100: MAX30100Driver,
  ADXL345: ADXL345Driver,
  ML8511: ML8511Driver,
  AD8232: AD8232Driver,
};

export function createSensorDriver(typeId, device, address, options = {}) {
  if (typeId === 'ATMEGA32_ADC') {
    return new Atmega32ADCDriver(device, options.channel ?? 0);
  }
  if (typeId === 'ML8511') {
    return new ML8511Driver(device, options.channel ?? 0);
  }
  if (typeId === 'AD8232') {
    return new AD8232Driver(device, options.channel ?? 0);
  }
  const Cls = DRIVER_MAP[typeId];
  return Cls ? new Cls(device, address) : null;
}
