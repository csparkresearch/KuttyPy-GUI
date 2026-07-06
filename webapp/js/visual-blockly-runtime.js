/**
 * Blockly JS-Interpreter APIs — uses KuttyPyDevice instead of Flask/datachannel fetch.
 */

import { VisualPlotManager } from './visual-chart-plots.js?v=27';
import { VisualSensorManager } from './visual-sensor-runtime.js';
import { installStepperApis } from './visual-stepper-runtime.js';
import { regDisplayName } from './kuttypy-serial.js';

/**
 * @param {import('./kuttypy-serial.js').KuttyPyDevice} device
 * @param {{
 *   outputEl: HTMLElement,
 *   registersEl: HTMLElement,
 *   plotsHost: HTMLElement,
 *   highlightBlock: (id: string) => void,
 * }} ui
 */
export function createVisualRuntime(device, ui) {
  const plots = new VisualPlotManager(ui.plotsHost);
  const sensors = new VisualSensorManager(device);
  const regLabels = new Map();

  function appendOutput(text) {
    const line = document.createElement('div');
    line.className = 'visual-output-line';
    line.textContent = String(text);
    ui.outputEl.appendChild(line);
    ui.outputEl.scrollTop = ui.outputEl.scrollHeight;
  }

  function clearOutput() {
    ui.outputEl.innerHTML = '';
    ui.registersEl.innerHTML = '';
    regLabels.clear();
    plots.clear();
    sensors.clear();
  }

  function showReg(reg, val) {
    const key = String(reg).replace(/ /g, '_');
    let el = regLabels.get(key);
    if (!el) {
      el = document.createElement('div');
      el.className = 'visual-reg-item';
      ui.registersEl.appendChild(el);
      regLabels.set(key, el);
    }
    el.textContent = `${reg} = ${val}`;
  }

  function requireDevice(apiName) {
    if (!device?.connected) {
      throw new Error(`USB not connected — ${apiName} requires hardware`);
    }
  }

  function installInterpreterApis(interpreter, scope) {
    interpreter.setProperty(scope, 'sleep', interpreter.createAsyncFunction((seconds, callback) => {
      setTimeout(callback, Math.max(0, Number(seconds) || 0) * 1000);
    }));

    interpreter.setProperty(scope, 'waitForSeconds', interpreter.createAsyncFunction((seconds, callback) => {
      setTimeout(callback, Math.max(0, Number(seconds) || 0) * 1000);
    }));

    interpreter.setProperty(scope, 'highlightBlock', interpreter.createNativeFunction((id) => {
      ui.highlightBlock(id ? String(id) : '');
    }));

    interpreter.setProperty(scope, 'print', interpreter.createNativeFunction((text) => {
      appendOutput(text);
    }));

    interpreter.setProperty(scope, 'alert', interpreter.createNativeFunction((text) => {
      appendOutput(text);
    }));

    interpreter.setProperty(scope, 'sticker', interpreter.createNativeFunction((label, text) => {
      showReg(label, text);
    }));

    interpreter.setProperty(scope, 'setGauge', interpreter.createNativeFunction((id, value) => {
      showReg(String(id), value);
    }));

    interpreter.setProperty(scope, 'log', interpreter.createNativeFunction((value) => {
      console.log(value);
    }));

    interpreter.setProperty(scope, 'get_voltage', interpreter.createAsyncFunction(async (channel, callback) => {
      try {
        requireDevice('get_voltage');
        const raw = await device.readADC(Number(channel) | 0);
        callback((raw / 1023) * 5.0);
      } catch (err) {
        console.error(err);
        appendOutput(`ADC error: ${err.message}`);
        throw err;
      }
    }));

    const getRegWrapper = interpreter.createAsyncFunction(async (channel, callback) => {
      try {
        requireDevice('get_reg');
        const label = regDisplayName(channel);
        const val = await device.getReg(channel);
        showReg(label, val);
        callback(val);
      } catch (err) {
        console.error(err);
        showReg(regDisplayName(channel), 'err');
        appendOutput(`Register read error: ${err.message}`);
        throw err;
      }
    });
    interpreter.setProperty(scope, 'get_reg', getRegWrapper);
    interpreter.setProperty(scope, 'getReg', getRegWrapper);

    const setRegWrapper = interpreter.createAsyncFunction(async (channel, value, callback) => {
      try {
        requireDevice('set_reg');
        const label = regDisplayName(channel);
        const n = Number(value) & 0xff;
        await device.setReg(channel, n);
        showReg(label, n);
        callback();
      } catch (err) {
        console.error(err);
        showReg(regDisplayName(channel), 'err');
        appendOutput(`Register write error: ${err.message}`);
        throw err;
      }
    });
    interpreter.setProperty(scope, 'set_reg', setRegWrapper);
    interpreter.setProperty(scope, 'setReg', setRegWrapper);

    interpreter.setProperty(scope, 'plot', interpreter.createNativeFunction((plotname, value) => {
      plots.plot(String(plotname), interpreter.pseudoToNative(value));
    }));

    interpreter.setProperty(scope, 'plot_array', interpreter.createNativeFunction((plotname, values) => {
      plots.plot(String(plotname), interpreter.pseudoToNative(values));
    }));

    interpreter.setProperty(scope, 'plot_xy', interpreter.createNativeFunction((plotname, x, y) => {
      plots.plotXy(String(plotname), x, y);
    }));

    interpreter.setProperty(scope, 'subtract_lists', interpreter.createNativeFunction((x, y) => {
      const a = Object.values(x?.a ?? x ?? {});
      const b = Object.values(y?.a ?? y ?? {});
      if (a.length !== b.length) return interpreter.nativeToPseudo([]);
      const c = [];
      for (let i = 0; i < a.length; i++) c.push(a[i] - b[i]);
      return interpreter.nativeToPseudo(c);
    }));

    interpreter.setProperty(scope, 'readKuttyPySensor', interpreter.createAsyncFunction(
      async (blockId, typeId, address, fieldKeysJson, configJson, callback) => {
        try {
          let configIndices = {};
          let fieldKeys = [];
          try {
            configIndices = JSON.parse(String(configJson || '{}'));
          } catch {
            configIndices = {};
          }
          try {
            const parsed = JSON.parse(String(fieldKeysJson || '[]'));
            fieldKeys = Array.isArray(parsed) ? parsed : [String(fieldKeysJson)];
          } catch {
            fieldKeys = String(fieldKeysJson || '').split(',').map((s) => s.trim()).filter(Boolean);
          }
          const val = await sensors.readFields(
            String(blockId),
            String(typeId),
            Number(address),
            fieldKeys,
            configIndices,
          );
          callback(interpreter.nativeToPseudo(val));
        } catch (err) {
          console.error(err);
          appendOutput(`Sensor error: ${err.message}`);
          throw err;
        }
      },
    ));

    installStepperApis(interpreter, scope, device, { requireDevice });
  }

  return {
    installInterpreterApis,
    clearOutput,
    clearPlots: () => plots.clear(),
  };
}
