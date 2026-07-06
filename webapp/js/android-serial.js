/**
 * Android Chrome serial access via WebUSB (desktop keeps native Web Serial).
 */

import { isAndroidChrome } from './platform.js';
import { Ch340SerialPort } from './ch340-port.js';

const CH340_VENDOR = 0x1a86;

export { isAndroidChrome } from './platform.js';

function toUsbFilters(serialFilters) {
  return serialFilters.map((f) => ({
    vendorId: f.usbVendorId,
    productId: f.usbProductId,
  }));
}

/**
 * Request a KuttyPy serial port on Android via WebUSB (CH340 driver).
 * @param {SerialPortFilter[]} serialFilters
 * @returns {Promise<SerialPort>}
 */
export async function requestKuttyPyPort(serialFilters, debug) {
  if (!isAndroidChrome()) {
    if (!('serial' in navigator)) {
      throw new Error('Web Serial API is not available. Use Chrome or Edge.');
    }
    return navigator.serial.requestPort({ filters: serialFilters });
  }

  if (!('usb' in navigator)) {
    throw new Error(
      'WebUSB is not available on this Android browser. Use Chrome with USB OTG.',
    );
  }

  debug?.log('WebUSB: requestDevice');
  const device = await navigator.usb.requestDevice({ filters: toUsbFilters(serialFilters) });
  debug?.log(
    `WebUSB: picked 0x${device.vendorId.toString(16)}:0x${device.productId.toString(16)}`
    + (device.productName ? ` "${device.productName}"` : ''),
  );

  if (device.vendorId === CH340_VENDOR) {
    debug?.log('WebUSB: using Ch340SerialPort driver');
    return new Ch340SerialPort(device, debug);
  }

  const msg = `Unsupported USB device 0x${device.vendorId.toString(16)}:0x${device.productId.toString(16)} — KuttyPy expects CH340`;
  debug?.log(`WebUSB: ${msg}`);
  throw new Error(msg);
}
