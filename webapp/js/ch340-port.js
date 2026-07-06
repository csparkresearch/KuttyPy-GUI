/**
 * CH340 WebUSB for Android Chrome — Web Serial-shaped API.
 * Control + bulk I/O follow selevo/WebUsbSerialTerminal.
 * @see https://github.com/selevo/WebUsbSerialTerminal
 */

const CH340 = {
  REQUEST_READ_REGISTRY: 0x95,
  REQUEST_WRITE_REGISTRY: 0x9a,
  REQUEST_SERIAL_INITIATION: 0xa1,
  REG_SERIAL: 0xc29c,
  REG_MODEM_CTRL: 0xa4,
  REG_MODEM_VALUE_OFF: 0xff,
  REG_MODEM_VALUE_ON: 0xdf,
  REG_MODEM_VALUE_CALL: 0x9f,
  REG_BAUD_FACTOR: 0x1312,
  REG_BAUD_OFFSET: 0x0f2c,
  REG_BAUD_LOW: 0x2518,
  REG_CONTROL_STATUS: 0x2727,
  BAUD_RATE: {
    600: { FACTOR: 0x6481, OFFSET: 0x76 },
    1200: { FACTOR: 0xb281, OFFSET: 0x3b },
    2400: { FACTOR: 0xd981, OFFSET: 0x1e },
    4800: { FACTOR: 0x6482, OFFSET: 0x0f },
    9600: { FACTOR: 0xb282, OFFSET: 0x08 },
    14400: { FACTOR: 0xd980, OFFSET: 0xeb },
    19200: { FACTOR: 0xd982, OFFSET: 0x07 },
    38400: { FACTOR: 0x6483, OFFSET: null },
    57600: { FACTOR: 0x9883, OFFSET: null },
    115200: { FACTOR: 0xcc83, OFFSET: null },
  },
};

const MCR_DTR = 0x20;
const MCR_RTS = 0x40;

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function emptyDataView() {
  return new DataView(new ArrayBuffer(0));
}

function toU8(data) {
  if (data instanceof Uint8Array) return data;
  if (data?.buffer) {
    return new Uint8Array(data.buffer, data.byteOffset, data.byteLength);
  }
  return new Uint8Array(data);
}

/** Chunk queue for ReadableStream consumers after connect handshake. */
class RxQueue {
  constructor() {
    this._chunks = [];
    this._waiters = [];
  }

  clear() {
    this._chunks = [];
    for (const w of this._waiters) {
      if (w.timer) clearTimeout(w.timer);
      w.resolve(null);
    }
    this._waiters = [];
  }

  push(chunk) {
    const u8 = toU8(chunk);
    if (!u8.length) return;
    if (this._waiters.length) {
      const w = this._waiters.shift();
      if (w.timer) clearTimeout(w.timer);
      w.resolve(u8);
    } else {
      this._chunks.push(u8);
    }
  }

  takeChunk(timeoutMs) {
    if (this._chunks.length) {
      return Promise.resolve(this._chunks.shift());
    }
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        const idx = this._waiters.findIndex((w) => w.resolve === resolve);
        if (idx >= 0) this._waiters.splice(idx, 1);
        resolve(null);
      }, timeoutMs);
      this._waiters.push({ resolve, timer });
    });
  }

  takeChunkBlocking() {
    if (this._chunks.length) {
      return Promise.resolve(this._chunks.shift());
    }
    return new Promise((resolve) => {
      this._waiters.push({ resolve, timer: null });
    });
  }
}

class ChunkInSource {
  constructor(queue) {
    this.queue = queue;
  }

  pull(controller) {
    this.queue.takeChunkBlocking().then((chunk) => {
      if (chunk) controller.enqueue(chunk);
    });
  }
}

class BulkOutSink {
  constructor(port) {
    this.port = port;
  }

  async write(chunk, controller) {
    try {
      await this.port.rawSend(chunk);
    } catch (err) {
      controller.error(String(err));
    }
  }
}

export class Ch340SerialPort {
  constructor(usbDevice, debug = null) {
    this._device = usbDevice;
    this._debug = debug;
    this._interfaceNumber = null;
    this._endpointIn = null;
    this._endpointOut = null;
    this._readable = null;
    this._writable = null;
    this._opened = false;
    this._reading = false;
    this._rxQueue = new RxQueue();
    this._rxStash = [];
    this._inLock = Promise.resolve();
    this._claimedInterfaces = [];
    this._mcr = 0;
  }

  get rxQueueSize() {
    return this._rxQueue._chunks.reduce((n, c) => n + c.length, 0);
  }

  get isOpened() {
    return this._opened;
  }

  isReadLoopActive() {
    return this._reading;
  }

  getInfo() {
    return {
      usbVendorId: this._device.vendorId,
      usbProductId: this._device.productId,
    };
  }

  get readable() {
    if (!this._readable && this._opened) {
      this._readable = new ReadableStream(new ChunkInSource(this._rxQueue), {
        highWaterMark: 8,
      });
    }
    return this._readable;
  }

  get writable() {
    if (!this._writable && this._opened) {
      this._writable = new WritableStream(new BulkOutSink(this), {
        highWaterMark: 64,
      });
    }
    return this._writable;
  }

  resetReadable() {
    this._readable = null;
  }

  /** Stop selevo readLoop so bulk IN is exclusive for handshake/drain. */
  async pauseReadLoop() {
    if (!this._reading) return;
    this._reading = false;
    await delay(80);
  }

  startReadLoop() {
    if (!this._opened || this._reading) return;
    this._reading = true;
    this._readLoop();
    this._debug?.log('CH340: readLoop started');
  }

  resumeReadLoop() {
    this.startReadLoop();
  }

  /** selevo Port.prototype.send — direct bulk OUT. */
  async rawSend(data) {
    if (!this._opened) throw new Error('Port closed');
    const bytes = toU8(data);
    const hex = [...bytes].map((b) => `0x${b.toString(16).padStart(2, '0')}`).join(' ');
    const result = await this._device.transferOut(this._endpointOut, bytes);
    if (result.status !== 'ok') {
      if (result.status === 'stall') {
        await this._device.clearHalt('out', this._endpointOut);
        const retry = await this._device.transferOut(this._endpointOut, bytes);
        if (retry.status === 'ok') {
          this._debug?.log(`CH340: rawSend ok (retry) ${retry.bytesWritten ?? bytes.length} byte(s): ${hex}`);
          return retry;
        }
      }
      throw new Error(`CH340 bulk OUT failed: ${result.status}`);
    }
    this._debug?.log(`CH340: rawSend ok ${result.bytesWritten ?? bytes.length} byte(s): ${hex}`);
    return result;
  }

  clearStash() {
    if (this._rxStash.length) {
      this._debug?.log(`CH340: clearStash dropped ${this._rxStash.length} byte(s)`);
    }
    this._rxStash = [];
  }

  /** One bulk-IN flight at a time — Android loses data if transferIn calls overlap. */
  _transferInExclusive() {
    const run = this._inLock.then(() =>
      this._device.transferIn(this._endpointIn, 64),
    );
    this._inLock = run.catch(() => {});
    return run;
  }

  _stashInResult(result) {
    if (!result) return;
    if (result.status === 'stall') {
      this._device.clearHalt('in', this._endpointIn).catch(() => {});
      return;
    }
    if (result.status === 'ok' && result.data?.byteLength) {
      const u8 = toU8(result.data);
      this._rxStash.push(...u8);
      const hex = [...u8].map((b) => `0x${b.toString(16).padStart(2, '0')}`).join(' ');
      this._debug?.log(`CH340: stashed IN ${u8.length} byte(s): ${hex}`);
    } else if (result.status !== 'ok') {
      this._debug?.log(`CH340: IN transfer status=${result.status}`);
    }
  }

  _takeStashChunk() {
    if (!this._rxStash.length) return null;
    return new Uint8Array(this._rxStash.splice(0, this._rxStash.length));
  }

  /** Direct bulk IN — never abandons transferIn; late bytes go to _rxStash. */
  async rawRead(timeoutMs = 500) {
    const stashed = this._takeStashChunk();
    if (stashed?.length) return stashed;

    const xfer = this._transferInExclusive();
    const outcome = await Promise.race([
      xfer.then((r) => ({ timedOut: false, r })),
      delay(timeoutMs).then(() => ({ timedOut: true })),
    ]);

    if (outcome.timedOut) {
      xfer.then((r) => this._stashInResult(r)).catch(() => {});
      const late = this._takeStashChunk();
      return late?.length ? late : null;
    }

    const result = outcome.r;
    if (result.status === 'stall') {
      await this._device.clearHalt('in', this._endpointIn);
      return this.rawRead(timeoutMs);
    }
    if (result.status === 'ok' && result.data?.byteLength) {
      return toU8(result.data);
    }
    this._debug?.log(`CH340: rawRead empty status=${result.status}`);
    return null;
  }

  /** while (fd.in_waiting) fd.read(...) — discard inbound while readLoop paused. */
  async drainInbound(maxMs = 120) {
    const captured = [];
    const deadline = performance.now() + maxMs;
    let idleRounds = 0;

    while (performance.now() < deadline && idleRounds < 3) {
      const chunk = await this.rawRead(Math.min(40, deadline - performance.now()));
      if (!chunk?.length) {
        idleRounds += 1;
        await delay(10);
        continue;
      }
      idleRounds = 0;
      captured.push(...chunk);
    }

    this.clearStash();
    this._rxQueue.clear();
    if (captured.length) {
      const hex = captured.map((b) => `0x${b.toString(16).padStart(2, '0')}`).join(' ');
      this._debug?.log(`CH340: drainInbound ${captured.length} byte(s): ${hex}`);
    }
    return captured;
  }

  async flushRx(maxMs = 80) {
    if (this._reading) await this.pauseReadLoop();
    try {
      const bytes = await this.drainInbound(maxMs);
      return { queued: 0, hw: bytes.length, bytes };
    } finally {
      if (this._opened) this.startReadLoop();
    }
  }

  async drainUntilEmpty(maxMs = 150) {
    if (this._reading) await this.pauseReadLoop();
    try {
      const bytes = await this.drainInbound(maxMs);
      return { total: bytes.length, bytes };
    } finally {
      if (this._opened) this.startReadLoop();
    }
  }

  async drainRx(ms = 100) {
    return this.flushRx(ms);
  }

  async open(options) {
    const baudRate = options?.baudRate ?? 9600;
    this._debug?.log(`CH340: open @ ${baudRate} (selevo model)`);

    await this._device.open();

    if (this._device.configuration === null) {
      await this._device.selectConfiguration(1);
    }

    this._discoverEndpoints();

    this._claimedInterfaces = [];
    for (const iface of this._device.configuration.interfaces) {
      const num = iface.interfaceNumber;
      await this._device.claimInterface(num);
      this._claimedInterfaces.push(num);
    }
    await this._device.selectAlternateInterface(this._interfaceNumber, 0);

    try {
      await this._device.clearHalt('in', this._endpointIn);
      await this._device.clearHalt('out', this._endpointOut);
    } catch (_) {}

    this._debug?.log(
      `CH340: claimed [${this._claimedInterfaces.join(', ')}]`
      + ` data iface=${this._interfaceNumber} IN ep${this._endpointIn} OUT ep${this._endpointOut}`,
    );

    await this._ch340Init(baudRate);

    this._opened = true;
    // Do NOT start readLoop here — an in-flight transferIn steals GET_VERSION replies.
    this._debug?.log('CH340: open complete (readLoop deferred until handshake)');
  }

  async close() {
    this._reading = false;
    this._opened = false;

    if (this._readable) {
      try { await this._readable.cancel(); } catch (_) {}
    }
    if (this._writable) {
      try { await this._writable.abort(); } catch (_) {}
    }
    this._readable = null;
    this._writable = null;
    this._rxQueue.clear();

    try {
      await this._controlledTransfer('out', CH340.REG_MODEM_CTRL, CH340.REG_MODEM_VALUE_OFF);
    } catch (_) {}

    if (this._device.opened) {
      for (const num of this._claimedInterfaces) {
        try {
          await this._device.releaseInterface(num);
        } catch (_) {}
      }
      this._claimedInterfaces = [];
      try {
        await this._device.close();
      } catch (_) {}
    }
  }

  async setSignals(signals) {
    if (!this._device.opened) return;
    if (signals.requestToSend === true) this._mcr |= MCR_RTS;
    if (signals.requestToSend === false) this._mcr &= ~MCR_RTS;
    if (signals.dataTerminalReady === true) this._mcr |= MCR_DTR;
    if (signals.dataTerminalReady === false) this._mcr &= ~MCR_DTR;
    await this._controlledTransfer('out', CH340.REG_MODEM_CTRL, (~this._mcr) & 0xff);
  }

  /** selevo readLoop — one IN transfer at a time via _transferInExclusive. */
  _readLoop() {
    if (!this._reading) return;

    this._transferInExclusive().then(
      (result) => {
        if (!this._reading) {
          this._stashInResult(result);
          return;
        }
        if (result.status === 'ok' && result.data?.byteLength) {
          this._rxQueue.push(result.data);
        } else if (result.status === 'stall') {
          this._device.clearHalt('in', this._endpointIn).catch(() => {});
        }
        this._readLoop();
      },
      (err) => {
        if (!this._reading) return;
        this._debug?.logErr('CH340: readLoop error', err);
        delay(100).then(() => this._readLoop());
      },
    );
  }

  _discoverEndpoints() {
    const ifaces = this._device.configuration.interfaces;
    for (const element of ifaces) {
      for (const alt of element.alternates) {
        const eps = alt.endpoints.map(
          (ep) => `ep${ep.endpointNumber}:${ep.direction}/${ep.type}`,
        ).join(' ');
        this._debug?.log(
          `CH340: iface${element.interfaceNumber} class=0x${alt.interfaceClass.toString(16)} [${eps}]`,
        );
      }
    }

    // mik3y driver: bulk endpoints on the last interface
    const dataIface = ifaces[ifaces.length - 1];
    for (const alt of dataIface.alternates) {
      let inEp = null;
      let outEp = null;
      for (const ep of alt.endpoints) {
        if (ep.type === 'bulk' && ep.direction === 'in') inEp = ep.endpointNumber;
        if (ep.type === 'bulk' && ep.direction === 'out') outEp = ep.endpointNumber;
      }
      if (inEp != null && outEp != null) {
        this._interfaceNumber = dataIface.interfaceNumber;
        this._endpointIn = inEp;
        this._endpointOut = outEp;
        this._debug?.log('CH340: using last interface for bulk data');
        return;
      }
    }

    // selevo fallback: first 0xFF interface with bulk IN+OUT
    for (const element of ifaces) {
      for (const alt of element.alternates) {
        if (alt.interfaceClass !== 0xff) continue;
        let inEp = null;
        let outEp = null;
        for (const ep of alt.endpoints) {
          if (ep.type === 'bulk' && ep.direction === 'in') inEp = ep.endpointNumber;
          if (ep.type === 'bulk' && ep.direction === 'out') outEp = ep.endpointNumber;
        }
        if (inEp != null && outEp != null) {
          this._interfaceNumber = element.interfaceNumber;
          this._endpointIn = inEp;
          this._endpointOut = outEp;
          this._debug?.log('CH340: using 0xFF interface for bulk data');
          return;
        }
      }
    }

    throw new Error('CH340 bulk IN/OUT endpoints not found');
  }

  /** selevo serial.controlledTransfer */
  async _controlledTransfer(direction, request, value = 0, data = emptyDataView(), index) {
    const wIndex = index !== undefined ? index : this._interfaceNumber;
    const dir = direction.charAt(0).toUpperCase() + direction.slice(1);
    const setup = {
      requestType: 'vendor',
      recipient: 'device',
      request,
      value,
      index: wIndex,
    };

    let result;
    if (dir === 'Out') {
      result = await this._device.controlTransferOut(setup, data);
    } else {
      const length = typeof data === 'number' ? data : 0;
      result = await this._device.controlTransferIn(setup, length);
    }

    if (result.status !== 'ok') {
      throw new Error(
        `CH340 control ${dir} req=0x${request.toString(16)} val=0x${value.toString(16)}`
        + ` idx=0x${wIndex.toString(16)} → ${result.status}`,
      );
    }
    return result.data ?? null;
  }

  async _ch340SetBaudRate(baudRate) {
    const entry = CH340.BAUD_RATE[baudRate];
    if (!entry) throw new Error(`CH340: unsupported baud ${baudRate}`);
    const empty = emptyDataView();
    await this._controlledTransfer(
      'out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_BAUD_FACTOR, empty, entry.FACTOR,
    );
    await this._controlledTransfer(
      'out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_BAUD_OFFSET, empty, entry.OFFSET ?? 0,
    );
    await this._controlledTransfer(
      'out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_CONTROL_STATUS, empty,
    );
  }

  /** selevo serial["CH340"] init */
  async _ch340Init(baudRate) {
    const empty = emptyDataView();
    this._debug?.log('CH340: CH340 init sequence');

    await this._controlledTransfer(
      'out', CH340.REQUEST_SERIAL_INITIATION, CH340.REG_SERIAL, empty, 0xb2b9,
    );
    await this._controlledTransfer('out', CH340.REG_MODEM_CTRL, CH340.REG_MODEM_VALUE_ON);
    await this._controlledTransfer('out', CH340.REG_MODEM_CTRL, CH340.REG_MODEM_VALUE_CALL);

    await this._controlledTransfer('in', CH340.REQUEST_READ_REGISTRY, 0x0706, 2);

    await this._controlledTransfer('out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_CONTROL_STATUS, empty);
    await this._controlledTransfer('out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_BAUD_FACTOR, empty, 0xb282);
    await this._controlledTransfer('out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_BAUD_OFFSET, empty, 0x0008);
    await this._controlledTransfer('out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_BAUD_LOW, empty, 0x00c3);

    await this._controlledTransfer('in', CH340.REQUEST_READ_REGISTRY, 0x0706, 2);

    await this._controlledTransfer('out', CH340.REQUEST_WRITE_REGISTRY, CH340.REG_CONTROL_STATUS, empty);
    await this._ch340SetBaudRate(baudRate);

    this._mcr = 0;
    this._debug?.log(`CH340: init done @ ${baudRate}`);
  }
}
