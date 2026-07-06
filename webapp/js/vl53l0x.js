/**
 * VL53L0X — direct port of KuttyPyLib.VL53L0X_init / VL53L0X_all (no tuning/calibration).
 */

function delay(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

const REG = {
  SYSRANGE_START: 0x00,
  IDENTIFICATION_MODEL_ID: 0xc0,
  IDENTIFICATION_REVISION_ID: 0xc2,
  PRE_RANGE_CONFIG_VCSEL_PERIOD: 0x50,
  FINAL_RANGE_CONFIG_VCSEL_PERIOD: 0x70,
  RESULT_RANGE_STATUS: 0x14,
};

async function readByte(device, address, reg) {
  const { data, ok } = await device.i2cReadBulk(address, reg, 1);
  if (!ok || !data?.length) return null;
  return data[0];
}

/** KuttyPyLib.makeuint16(lsb, msb) */
function makeUint16(lsb, msb) {
  return ((msb & 0xff) << 8) | (lsb & 0xff);
}

/** Mirrors KuttyPyLib.VL53L0X_init — read-only ID checks, no register writes. */
export async function vl53l0xInit(device, address) {
  const modelId = await readByte(device, address, REG.IDENTIFICATION_MODEL_ID);
  if (modelId === null) return false;

  await readByte(device, address, REG.PRE_RANGE_CONFIG_VCSEL_PERIOD);
  await readByte(device, address, REG.FINAL_RANGE_CONFIG_VCSEL_PERIOD);

  const revisionId = await readByte(device, address, REG.IDENTIFICATION_REVISION_ID);
  if (revisionId === null || revisionId === 0x00 || revisionId === 0xff) {
    return false;
  }
  return true;
}

/** Mirrors KuttyPyLib.VL53L0X_all — returns distance mm or null. */
export async function vl53l0xReadRangeMm(device, address) {
  if (!(await device.i2cWriteBulk(address, [REG.SYSRANGE_START, 0x01]))) {
    return null;
  }

  let statusByte = null;
  for (let cnt = 0; cnt < 50; cnt++) {
    await delay(5);
    const { data, ok } = await device.i2cReadBulk(address, REG.RESULT_RANGE_STATUS, 1);
    if (!ok || !data?.length) continue;
    statusByte = data[0];
    if (statusByte & 0x01) break;
  }

  if (statusByte === null || !(statusByte & 0x01)) {
    return null;
  }

  const { data, ok } = await device.i2cReadBulk(address, REG.RESULT_RANGE_STATUS, 12);
  if (!ok || !data || data.length < 12) return null;

  let d = makeUint16(data[11], data[10]);
  const deviceRangeStatusInternal = (data[0] & 0x78) >> 3;
  if (deviceRangeStatusInternal !== 11) {
    return null;
  }
  return d;
}
