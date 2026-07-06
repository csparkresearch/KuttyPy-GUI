/**
 * Acorn JS-Interpreter run loop for Blockly programs.
 */

import { createVisualRuntime } from './visual-blockly-runtime.js?v=30';

const RESERVED = [
  'highlightBlock', 'sleep', 'waitForSeconds', 'plot', 'plot_array', 'plot_xy',
  'get_voltage', 'get_reg', 'getReg', 'set_reg', 'setReg', 'print', 'sticker',
  'subtract_lists', 'log', 'readKuttyPySensor', 'setGauge',
  'move_stepper', 'move_stepper_cw', 'move_stepper_ccw',
];

/** Code panel view — strip runtime-only highlightBlock() calls. */
function formatCodeForDisplay(code) {
  return code.replace(/^[ \t]*highlightBlock\([^)]*\);\r?\n/gm, '').trimEnd();
}

export function createVisualRunner({
  getWorkspace,
  getDevice,
  outputEl,
  registersEl,
  plotsHost,
  codeEl,
  statusEl,
  onRunningChange,
  onMobilePaneChange,
}) {
  let interpreter = null;
  let runnerTimer = null;
  let running = false;
  let runtime = null;
  let lastStopReason = null;

  function isMobileLayout() {
    return window.matchMedia('(max-width: 900px)').matches;
  }

  function notifyMobilePane(open) {
    onMobilePaneChange?.(open);
  }

  function highlightBlock(id) {
    const ws = getWorkspace();
    if (ws) ws.highlightBlock(id || null);
  }

  function setStatus(text) {
    if (statusEl) statusEl.textContent = text;
  }

  function setRunning(isOn) {
    running = isOn;
    onRunningChange?.(isOn);
  }

  function stop(reason = 'abort') {
    if (runnerTimer) {
      clearTimeout(runnerTimer);
      runnerTimer = null;
    }
    interpreter = null;
    highlightBlock(null);
    const wasRunning = running;
    setRunning(false);
    lastStopReason = reason;
    if (wasRunning) {
      if (reason === 'complete') setStatus('Done');
      else if (reason === 'error') return;
      else setStatus('Program aborted');
    }
  }

  function showCode(code) {
    if (codeEl) codeEl.textContent = code || '// (empty workspace)';
  }

  function returnToBlocksView() {
    if (!isMobileLayout()) return;
    document.body.classList.remove('visual-mobile-show-side');
    document.body.dataset.visualMobileTab = 'blocks';
    notifyMobilePane(false);
  }

  function isMobileSideOpen() {
    return document.body.classList.contains('visual-mobile-show-side');
  }

  function switchSideTab(name) {
    document.querySelectorAll('.visual-side-tab').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.tab === name);
    });
    document.querySelectorAll('.visual-tab-panel').forEach((panel) => {
      panel.hidden = panel.dataset.panel !== name;
    });
    if (isMobileLayout()) {
      const open = name !== 'blocks';
      document.body.classList.toggle('visual-mobile-show-side', open);
      document.body.dataset.visualMobileTab = name;
      notifyMobilePane(open);
    }
  }

  function run() {
    if (running) {
      stop('abort');
      return;
    }

    const ws = getWorkspace();
    const device = getDevice();
    if (!ws || !window.Blockly) return;

    const usbConnected = Boolean(device?.connected);

    Blockly.JavaScript.STATEMENT_PREFIX = 'highlightBlock(%1);\n';
    Blockly.JavaScript.addReservedWords(RESERVED.join(' '));

    const code = Blockly.JavaScript.workspaceToCode(ws);
    showCode(formatCodeForDisplay(code));
    switchSideTab('code');

    if (!code.trim()) {
      setStatus('Add blocks to run');
      return;
    }

    runtime = createVisualRuntime(device, {
      outputEl,
      registersEl,
      plotsHost,
      highlightBlock,
    });
    runtime.clearOutput();

    if (!usbConnected) {
      const warn = 'USB not connected — blocks that use the board (ADC, registers, I/O) will error when executed.';
      setStatus(warn);
      if (outputEl) {
        const line = document.createElement('div');
        line.className = 'visual-output-line visual-output-line--warn';
        line.textContent = warn;
        outputEl.appendChild(line);
      }
    }

    lastStopReason = null;

    try {
      interpreter = new Interpreter(code, (interpreterInst, scope) => {
        runtime.installInterpreterApis(interpreterInst, scope);
      });
    } catch (err) {
      setStatus(`Compile error: ${err.message}`);
      switchSideTab('output');
      if (outputEl) {
        const line = document.createElement('div');
        line.className = 'visual-output-line visual-output-line--error';
        line.textContent = `${err.name}: ${err.message}`;
        outputEl.appendChild(line);
      }
      return;
    }

    window.myInterpreter = interpreter;
    setRunning(true);
    setStatus(usbConnected ? 'Running…' : 'Running (no USB)…');
    switchSideTab('output');

    const step = () => {
      if (!interpreter || !running) return;
      try {
        const hasMore = interpreter.run();
        if (hasMore) {
          runnerTimer = setTimeout(step, 2);
          return;
        }
      } catch (err) {
        console.error(err);
        if (outputEl) {
          const line = document.createElement('div');
          line.className = 'visual-output-line visual-output-line--error';
          line.textContent = `${err.name}: ${err.message}`;
          outputEl.appendChild(line);
        }
        stop('error');
        setStatus(`Error: ${err.message}`);
        switchSideTab('output');
        return;
      }
      stop('complete');
    };

    step();
  }

  return {
    run,
    stop,
    isRunning: () => running,
    getLastStopReason: () => lastStopReason,
    switchSideTab,
    returnToBlocksView,
    isMobileSideOpen,
  };
}
