/**
 * Stepper motor APIs for Blockly programs (PORTB half-step drive).
 */

const STEP_POSITIONS = [
  [3, 6, 12, 9, 0],
  [3 << 4, 6 << 4, 12 << 4, 9 << 4, 0],
];

export function installStepperApis(interpreter, scope, device, { requireDevice }) {
  let stepperPos = [0, 0];
  let curStepPos = [4, 4];

  async function writePortB() {
    requireDevice('stepper');
    const val = STEP_POSITIONS[0][curStepPos[0] % 4] + STEP_POSITIONS[1][curStepPos[1] % 4];
    await device.setReg('PORTB', val);
  }

  const moveCw = interpreter.createAsyncFunction(async (motor, callback) => {
    const m = Number(motor) | 0;
    stepperPos[m] += 1;
    curStepPos[m] = (curStepPos[m] + 1) % 4;
    await writePortB();
    callback();
  });

  const moveCcw = interpreter.createAsyncFunction(async (motor, callback) => {
    const m = Number(motor) | 0;
    stepperPos[m] -= 1;
    curStepPos[m] = (curStepPos[m] + 3) % 4;
    await writePortB();
    callback();
  });

  const moveBoth = interpreter.createAsyncFunction(async (steps1, steps2, msdelay, callback) => {
    const s1 = Number(steps1);
    const s2 = Number(steps2);
    const delayMs = Math.max(0, Number(msdelay));
    const longer = Math.max(Math.abs(s1), Math.abs(s2));
    if (longer === 0) {
      callback();
      return;
    }
    const d1 = s1 / longer;
    const d2 = s2 / longer;

    const stepOnce = async (i) => {
      stepperPos[0] += d1;
      stepperPos[1] += d2;
      curStepPos[0] = ((curStepPos[0] + (d1 >= 0 ? 1 : 3)) % 4 + 4) % 4;
      curStepPos[1] = ((curStepPos[1] + (d2 >= 0 ? 1 : 3)) % 4 + 4) % 4;
      await writePortB();
      if (i < longer - 1) {
        await new Promise((r) => setTimeout(r, delayMs));
        await stepOnce(i + 1);
      }
    };

    await stepOnce(0);
    callback();
  });

  interpreter.setProperty(scope, 'move_stepper_cw', moveCw);
  interpreter.setProperty(scope, 'move_stepper_ccw', moveCcw);
  interpreter.setProperty(scope, 'move_stepper', moveBoth);
}
