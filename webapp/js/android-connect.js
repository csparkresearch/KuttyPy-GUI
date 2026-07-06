/**
 * Android Chrome connect + GET_VERSION handshake (CH340 WebUSB).
 * Desktop uses native Web Serial in kuttypy-serial.js — do not mix paths.
 */

import { requestKuttyPyPort } from './android-serial.js';

const BAUD = 38400;
const GET_VERSION = 1;
const VERSION_ATMEGA32 = 99;
const VERSION_BYTES = [98, 99, 100, 101];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function asByte(n) {
  return n & 0xff;
}

async function getVersionRaw(port, debug) {
  const loopWasRunning = port.isReadLoopActive?.() ?? false;
  if (loopWasRunning) await port.pauseReadLoop();
  try {
    debug.log(`version: raw handshake (readLoop ${loopWasRunning ? 'paused' : 'off'})`);

    debug.log('version: boot pulse (RTS/DTR low → high)');
    await port.setSignals({ requestToSend: false, dataTerminalReady: false });
    await delay(10);
    await port.setSignals({ requestToSend: true, dataTerminalReady: true });

    const t0 = performance.now();
    const bootMs = 250;
    let flushed = 0;
    port.clearStash?.();

    debug.log(`version: flush RX during ${bootMs}ms boot window`);
    while (performance.now() - t0 < bootMs) {
      const left = bootMs - (performance.now() - t0);
      const chunk = await port.rawRead(Math.max(1, Math.ceil(left)));
      if (chunk?.length) {
        flushed += chunk.length;
        const hex = [...chunk].map((b) => `0x${b.toString(16).padStart(2, '0')}`).join(' ');
        debug.log(`version: flushed ${chunk.length} byte(s): ${hex}`);
      } else {
        await delay(Math.min(10, left));
      }
    }
    debug.log(`version: boot window done (${Math.round(performance.now() - t0)}ms, ${flushed} byte(s) flushed)`);

    port.clearStash?.();
    debug.log(`version: rawSend GET_VERSION (0x${GET_VERSION.toString(16)})`);
    await port.rawSend(new Uint8Array([GET_VERSION]));
    await delay(20);

    const buf = [];
    const deadline = performance.now() + 800;
    while (performance.now() < deadline) {
      const left = Math.max(1, Math.ceil(deadline - performance.now()));
      const chunk = await port.rawRead(left);
      if (!chunk?.length) continue;

      for (const b of chunk) {
        const byte = asByte(b);
        buf.push(byte);
        const rawHex = buf.map((x) => `0x${x.toString(16).padStart(2, '0')}`).join(' ');
        debug.log(`version: raw read [${buf.length} byte(s)]: ${rawHex}`);

        if (VERSION_BYTES.includes(byte)) {
          debug.log(`version: matched type ${byte} (0x${byte.toString(16)})`);
          return byte;
        }
        debug.log(`version: discard 0x${byte.toString(16).padStart(2, '0')} (not a version byte)`);
      }
    }

    if (!buf.length) {
      debug.log('version: raw read: (timeout, 0 bytes)');
      return -1;
    }

    const first = buf[0];
    debug.log(`version: no version byte — first=0x${first.toString(16)} (${first})`);
    return first;
  } finally {
    if (loopWasRunning) port.startReadLoop();
  }
}

/**
 * Open CH340 port, handshake, start readLoop, acquire reader/writer on device.
 * @param {import('./kuttypy-serial.js').KuttyPyDevice} device
 */
export async function connectAndroid(device, usbFilters, debug) {
  debug.log('connect: requesting USB device');
  device.port = await requestKuttyPyPort(usbFilters, debug);

  debug.log(`connect: opening port @ ${BAUD} baud`);
  await device.port.open({ baudRate: BAUD });

  let version = -1;
  for (let attempt = 0; attempt < 3 && version !== VERSION_ATMEGA32; attempt++) {
    debug.log(`connect: GET_VERSION attempt ${attempt + 1}/3`);
    version = await getVersionRaw(device.port, debug);
    debug.log(`connect: attempt ${attempt + 1} returned ${version}`);
  }

  if (version !== VERSION_ATMEGA32) {
    const msg = version < 0
      ? 'No response from device — is KuttyPy connected and not in use by another app?'
      : `Unexpected firmware version ${version} (expected ${VERSION_ATMEGA32})`;
    throw new Error(msg);
  }

  debug.log('connect: starting readLoop + reader/writer');
  if (typeof device.port.startReadLoop === 'function') {
    device.port.startReadLoop();
  }
  device.reader = await device.port.readable.getReader();
  device.writer = await device.port.writable.getWriter();
  debug.log('connect: reader/writer ready');

  return version;
}
