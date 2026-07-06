/**
 * Visual programming view — Blockly workspace, toolbox, and program runner.
 */

import { createVisualRunner } from './visual-runner.js?v=30';
import { showConfirmDialog } from './confirm-dialog.js?v=25';
import { SENSOR_TYPES } from './sensors.js';
import { openSensorPicker } from './visual-sensor-picker.js?v=26';
import {
  downloadWorkspaceXml,
  loadXmlIntoWorkspace,
  pickWorkspaceXmlFile,
  readFileAsText,
} from './visual-workspace-files.js?v=25';
import { fetchSampleXml, openSamplesDialog } from './visual-samples-dialog.js?v=25';

const SCRIPT_V = '30';

const CORE_SCRIPTS = [
  'visual/blockly_compressed.js',
  'visual/blocks_compressed.js',
  'visual/javascript_compressed.js',
  'visual/python_compressed.js',
  'visual/msg/js/en.js',
];

const BLOCK_SCRIPTS = [
  'visual/blocks/block-media.js',
  'visual/blocks/blockHelp.js',
  'visual/blocks/wait-blocks.js',
  'visual/blocks/KuttyPy.js',
  'visual/blocks/IO.js',
  'visual/blocks/Lists.js',
  'visual/blocks/plot-blocks.js',
  'visual/blocks/legacy-extra-plots.js',
  'visual/blocks/api.js',
  'visual/blocks/Sensors.js',
  'visual/blocks/sensor-block.js',
  'visual/blocks/Games.js',
  'visual/blocks/MP.js',
  'visual/blocks/Mosquito.js',
  'visual/blocks/legacy-sample-stubs.js',
  'visual/blocks/acorn_interpreter.js',
];

const STORAGE_KEY = 'kuttypy-visual-workspace';

function injectSensorMeta() {
  window.KUTTYPY_SENSORS = {};
  for (const [id, meta] of Object.entries(SENSOR_TYPES)) {
    window.KUTTYPY_SENSORS[id] = {
      id,
      name: meta.name,
      addresses: meta.addresses,
      icon: meta.iconPath || `images/icons/${meta.icon}`,
      fields: meta.fields.map((f) => [f.label, f.key]),
      config: meta.config.map((c) => ({
        key: c.key,
        label: c.label,
        options: c.options,
        method: c.method,
        defaultIndex: c.defaultIndex ?? 0,
      })),
    };
  }
}

let loadPromise = null;
let workspace = null;
let runner = null;
let initialized = false;
let session = {
  getDevice: () => null,
  isConnected: () => false,
  withPollingPaused: async (fn) => fn(),
};
let abortedFlashTimer = null;
let forceAbortedState = false;

const MOBILE_MQ = window.matchMedia('(max-width: 900px)');

function isMobileVisual() {
  return MOBILE_MQ.matches;
}

function updateMobileToolbar() {
  const modeBtn = document.getElementById('btn-visual-mode');
  const ioBack = document.getElementById('btn-visual-back');
  const modeLabel = modeBtn?.querySelector('.btn-visual-mode__label');
  if (!modeBtn || !ioBack || !modeLabel) return;

  const mobile = isMobileVisual();
  const sideOpen = runner?.isMobileSideOpen?.() ?? false;
  const running = runner?.isRunning?.() ?? false;

  document.body.classList.toggle('visual-mobile-layout', mobile);
  document.body.classList.toggle('visual-mobile-side-open', mobile && sideOpen);

  if (!mobile) {
    modeBtn.hidden = true;
    ioBack.hidden = false;
    ioBack.classList.remove('is-suppressed');
    return;
  }

  ioBack.classList.toggle('is-suppressed', sideOpen);
  ioBack.hidden = sideOpen;

  if (forceAbortedState) {
    modeBtn.hidden = false;
    modeBtn.dataset.state = 'aborted';
    modeLabel.textContent = 'Aborted';
    modeBtn.title = 'Program stopped';
    return;
  }

  if (!sideOpen) {
    modeBtn.hidden = true;
    return;
  }

  modeBtn.hidden = false;
  if (running) {
    modeBtn.dataset.state = 'running';
    modeLabel.textContent = 'Running';
    modeBtn.title = 'Stop program and return to blocks';
  } else {
    modeBtn.dataset.state = 'editing';
    modeLabel.textContent = '← Editing';
    modeBtn.title = 'Return to blocks';
  }
}

function flashAbortedState() {
  forceAbortedState = true;
  updateMobileToolbar();
  clearTimeout(abortedFlashTimer);
  abortedFlashTimer = setTimeout(() => {
    forceAbortedState = false;
    updateMobileToolbar();
  }, 1800);
}

function handleMobileModeAction() {
  if (!isMobileVisual()) return;

  if (forceAbortedState) {
    forceAbortedState = false;
    clearTimeout(abortedFlashTimer);
    updateMobileToolbar();
    return;
  }

  const wasRunning = runner?.isRunning?.();
  if (wasRunning) {
    runner?.stop('abort');
    flashAbortedState();
  }
  runner?.returnToBlocksView();
  updateMobileToolbar();
}

function loadScript(src) {
  const url = `${src}?v=${SCRIPT_V}`;
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[data-visual-src="${src}"]`)) {
      resolve();
      return;
    }
    const el = document.createElement('script');
    el.src = url;
    el.dataset.visualSrc = src;
    el.onload = () => resolve();
    el.onerror = () => reject(new Error(`Failed to load ${src}`));
    document.head.appendChild(el);
  });
}

async function ensureBlocklyLoaded() {
  if (window.Blockly && window.Interpreter) return;
  if (!loadPromise) {
    loadPromise = (async () => {
      injectSensorMeta();
      for (const src of [...CORE_SCRIPTS, ...BLOCK_SCRIPTS]) {
        await loadScript(src);
      }
    })();
  }
  await loadPromise;
}

function shadowNumber(n) {
  return { kind: 'block', type: 'math_number', fields: { NUM: String(n) } };
}

function shadowText(t) {
  return { kind: 'block', type: 'text', fields: { TEXT: t } };
}

function buildToolbox() {
  return {
    kind: 'categoryToolbox',
    contents: [
      { kind: 'category', name: 'Variables', categorystyle: 'variable_category', custom: 'VARIABLE' },
      {
        kind: 'category',
        name: 'Values',
        colour: '#a55b80',
        contents: [
          { kind: 'block', type: 'math_number', fields: { NUM: '0' } },
          { kind: 'block', type: 'math_number', fields: { NUM: '1000' } },
          { kind: 'block', type: 'math_number', fields: { NUM: '1' } },
          { kind: 'block', type: 'math_number', fields: { NUM: '15' } },
          { kind: 'block', type: 'math_number', fields: { NUM: '255' } },
          { kind: 'block', type: 'binary_value' },
          { kind: 'block', type: 'reg' },
          { kind: 'block', type: 'text' },
          { kind: 'block', type: 'logic_boolean' },
          { kind: 'block', type: 'math_constant' },
        ],
      },
      {
        kind: 'category',
        name: 'Operators',
        colour: '#5b80a5',
        contents: [
          {
            kind: 'block', type: 'math_arithmetic', fields: { OP: 'ADD' },
            inputs: { A: { shadow: shadowNumber(1) }, B: { shadow: shadowNumber(1) } },
          },
          {
            kind: 'block', type: 'text_join', extraState: { itemCount: 2 },
            inputs: { ADD0: { shadow: shadowText('') }, ADD1: { shadow: shadowText('') } },
          },
          { kind: 'block', type: 'lists_subtract_return' },
          {
            kind: 'block', type: 'shift_bits',
            inputs: { VALUE: { shadow: shadowNumber(1) }, BITS: { shadow: shadowNumber(1) } },
          },
          {
            kind: 'block', type: 'clear_bit',
            inputs: { VALUE: { shadow: shadowNumber(255) } },
          },
          {
            kind: 'block', type: 'and_or',
            inputs: { VALUE: { shadow: shadowNumber(255) }, VALUE2: { shadow: shadowNumber(1) } },
          },
          { kind: 'block', type: 'logic_operation' },
          { kind: 'block', type: 'logic_negate' },
        ],
      },
      {
        kind: 'category',
        name: 'Logic',
        colour: '#5b80a5',
        contents: [
          { kind: 'block', type: 'logic_boolean' },
          { kind: 'block', type: 'logic_compare' },
          { kind: 'block', type: 'controls_if' },
          { kind: 'block', type: 'logic_ternary' },
        ],
      },
      {
        kind: 'category',
        name: 'In / Out',
        colour: '#5ba58c',
        contents: [
          {
            kind: 'block', type: 'cs_print',
            inputs: { TEXT: { shadow: shadowText('hello') } },
          },
          {
            kind: 'block', type: 'cs_sticker',
            inputs: {
              LABEL: { shadow: shadowText('Parameter') },
              TEXT: { shadow: shadowText('Reading') },
            },
          },
          {
            kind: 'block', type: 'cs_gauge',
            fields: { ID: 'gauge1', MIN: '0', MAX: '100' },
            inputs: { VALUE: { shadow: shadowNumber(0) } },
          },
        ],
      },
      {
        kind: 'category',
        name: 'Loops',
        colour: '#5ba55b',
        contents: [
          { kind: 'block', type: 'wait_seconds' },
          {
            kind: 'block', type: 'controls_repeat_ext',
            inputs: { TIMES: { shadow: shadowNumber(20) } },
          },
          { kind: 'block', type: 'controls_whileUntil' },
          { kind: 'block', type: 'controls_for' },
          { kind: 'block', type: 'controls_flow_statements' },
        ],
      },
      {
        kind: 'category',
        name: 'Text',
        colour: '%{BKY_TEXTS_HUE}',
        contents: [
          { kind: 'block', type: 'text' },
          {
            kind: 'block', type: 'text_join', extraState: { itemCount: 2 },
            inputs: { ADD0: { shadow: shadowText('') }, ADD1: { shadow: shadowText('') } },
          },
          { kind: 'block', type: 'text_append' },
          {
            kind: 'block', type: 'cs_search',
            inputs: {
              CHILD: { shadow: shadowText('small string') },
              PARENT: { shadow: shadowText('much longer string') },
            },
          },
        ],
      },
      {
        kind: 'category',
        name: 'Math',
        colour: '#5b67a5',
        contents: [
          { kind: 'block', type: 'math_number' },
          {
            kind: 'block', type: 'math_arithmetic',
            inputs: { A: { shadow: shadowNumber(1) }, B: { shadow: shadowNumber(1) } },
          },
          { kind: 'block', type: 'math_single' },
          { kind: 'block', type: 'math_constant' },
          { kind: 'block', type: 'math_round' },
          { kind: 'block', type: 'math_modulo' },
          { kind: 'block', type: 'math_constrain' },
          { kind: 'block', type: 'math_random_int' },
        ],
      },
      {
        kind: 'category',
        name: 'Plots',
        colour: '#a55b80',
        contents: [
          {
            kind: 'block', type: 'plot_datapoint',
            inputs: { VALUE: { shadow: shadowNumber(0) } },
          },
          {
            kind: 'block', type: 'plot_datapoints',
            inputs: { VALUE: { shadow: shadowNumber(0) } },
          },
          {
            kind: 'block', type: 'plot_xy',
            inputs: { X: { shadow: shadowNumber(0) }, Y: { shadow: shadowNumber(0) } },
          },
        ],
      },
      {
        kind: 'category',
        name: 'Lists',
        colour: '#745ba5',
        contents: [
          { kind: 'block', type: 'lists_new' },
          {
            kind: 'block', type: 'lists_push',
            inputs: { VALUE: { shadow: shadowNumber(0) } },
          },
          {
            kind: 'block', type: 'lists_push_time',
            inputs: { VALUE: { shadow: shadowNumber(0) } },
          },
          { kind: 'block', type: 'lists_subtract_return' },
        ],
      },
      { kind: 'category', name: 'Functions', categorystyle: 'procedure_category', custom: 'PROCEDURE' },
      {
        kind: 'category',
        name: 'KuttyPy',
        colour: '#995ba5',
        contents: [
          { kind: 'block', type: 'binary_value' },
          { kind: 'block', type: 'reg' },
          { kind: 'block', type: 'get_voltage', fields: { CHANNEL: '0' } },
          { kind: 'block', type: 'get_reg' },
          {
            kind: 'block', type: 'set_reg',
            inputs: { VALUE: { shadow: shadowNumber(255) } },
          },
          {
            kind: 'block', type: 'set_dac',
            inputs: { VALUE: { shadow: shadowNumber(128) } },
          },
          { kind: 'block', type: 'set_reg_bits', fields: { REGISTER: 'PORTB' } },
          {
            kind: 'block', type: 'bytes_to_int',
            inputs: { HIGH: { shadow: shadowNumber(0) }, LOW: { shadow: shadowNumber(0) } },
          },
          { kind: 'block', type: 'init_stepper' },
          {
            kind: 'block', type: 'move_stepper',
            fields: { PINS: 'B1' },
            inputs: { STEPS: { shadow: shadowNumber(50) }, DELAY: { shadow: shadowNumber(5) } },
          },
          {
            kind: 'block', type: 'move_steppers',
            inputs: {
              STEPS1: { shadow: shadowNumber(50) },
              STEPS2: { shadow: shadowNumber(50) },
              DELAY: { shadow: shadowNumber(5) },
            },
          },
        ],
      },
      {
        kind: 'category',
        name: 'Sensors',
        colour: '#c45ba5',
        contents: [
          { kind: 'block', type: 'kuttypy_sensor_read' },
        ],
      },
    ],
  };
}

function loadWorkspaceFromStorage(ws) {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const xml = Blockly.Xml.textToDom(raw);
    Blockly.Xml.domToWorkspace(xml, ws);
  } catch (err) {
    console.warn('Could not restore visual workspace', err);
  }
}

function saveWorkspaceToStorage(ws) {
  try {
    const xml = Blockly.Xml.workspaceToDom(ws);
    localStorage.setItem(STORAGE_KEY, Blockly.Xml.domToText(xml));
  } catch (err) {
    console.warn('Could not save visual workspace', err);
  }
}

function resizeWorkspace() {
  if (workspace && window.Blockly) Blockly.svgResize(workspace);
}

let blocklyUndoBtn = null;
let blocklyRedoBtn = null;

function updateBlocklyUndoRedoButtons(ws) {
  if (!blocklyUndoBtn || !blocklyRedoBtn || !ws) return;
  blocklyUndoBtn.disabled = ws.getUndoStack().length === 0;
  blocklyRedoBtn.disabled = ws.getRedoStack().length === 0;
}

function wireBlocklyUndoRedo(ws) {
  const toolbox = ws.getToolbox?.();
  const contentsDiv = toolbox?.contentsDiv_
    || ws.getInjectionDiv?.()?.querySelector('.blocklyToolboxContents');
  if (!contentsDiv || contentsDiv.querySelector('.blockly-toolbox-undo-bar')) return;

  const bar = document.createElement('div');
  bar.className = 'blockly-toolbox-undo-bar';
  bar.innerHTML = `
    <button type="button" class="blockly-toolbox-undo-btn" data-action="undo" title="Undo (Ctrl+Z)" aria-label="Undo" disabled>
      <span aria-hidden="true">↶</span>
      <span class="blockly-toolbox-undo-label">Undo</span>
    </button>
    <button type="button" class="blockly-toolbox-undo-btn blockly-toolbox-redo-btn" data-action="redo" title="Redo (Ctrl+Y)" aria-label="Redo" disabled>
      <span aria-hidden="true">↷</span>
    </button>
  `;
  contentsDiv.insertBefore(bar, contentsDiv.firstChild);

  blocklyUndoBtn = bar.querySelector('[data-action="undo"]');
  blocklyRedoBtn = bar.querySelector('[data-action="redo"]');

  blocklyUndoBtn?.addEventListener('click', () => {
    if (blocklyUndoBtn.disabled) return;
    ws.undo(false);
    updateBlocklyUndoRedoButtons(ws);
  });
  blocklyRedoBtn?.addEventListener('click', () => {
    if (blocklyRedoBtn.disabled) return;
    ws.undo(true);
    updateBlocklyUndoRedoButtons(ws);
  });

  ws.addChangeListener(() => updateBlocklyUndoRedoButtons(ws));
  updateBlocklyUndoRedoButtons(ws);
}

function wireSideTabs() {
  document.querySelectorAll('.visual-side-tab').forEach((btn) => {
    btn.addEventListener('click', () => {
      runner?.switchSideTab(btn.dataset.tab);
    });
  });
}

function workspaceHasBlocks(ws) {
  return ws.getTopBlocks(false).length > 0;
}

async function confirmReplaceWorkspace() {
  if (!workspace || !workspaceHasBlocks(workspace)) return true;
  return showConfirmDialog({
    title: 'Replace workspace',
    message: 'Loading will replace your current blocks. Continue?',
    confirmLabel: 'Load',
    cancelLabel: 'Cancel',
    variant: 'danger',
  });
}

function resetVisualOutputPanels() {
  const codegen = document.getElementById('visual-codegen');
  const output = document.getElementById('visual-output');
  const registers = document.getElementById('visual-registers');
  const plots = document.getElementById('visual-plots-host');
  if (codegen) codegen.textContent = '// (empty workspace)';
  if (output) output.innerHTML = '';
  if (registers) registers.innerHTML = '';
  if (plots) plots.innerHTML = '';
}

async function applyXmlToWorkspace(xmlText) {
  if (!(await confirmReplaceWorkspace())) return;
  if (runner?.isRunning()) runner.stop();
  loadXmlIntoWorkspace(workspace, xmlText);
  saveWorkspaceToStorage(workspace);
  resetVisualOutputPanels();
  resizeWorkspace();
  updateMobileToolbar();
}

function wireToolbar() {
  const btnRun = document.getElementById('btn-visual-run');
  const btnClear = document.getElementById('btn-visual-clear');
  const btnMode = document.getElementById('btn-visual-mode');
  const btnSave = document.getElementById('btn-visual-save');
  const btnOpen = document.getElementById('btn-visual-open');
  const btnSamples = document.getElementById('btn-visual-samples');

  btnRun?.addEventListener('click', () => runner?.run());

  btnMode?.addEventListener('click', () => handleMobileModeAction());

  btnClear?.addEventListener('click', async () => {
    if (!workspace) return;
    const ok = await showConfirmDialog({
      title: 'Clear workspace',
      message: 'Remove all blocks from the workspace? This cannot be undone.',
      confirmLabel: 'Clear',
      cancelLabel: 'Cancel',
      variant: 'danger',
    });
    if (!ok) return;
    if (runner?.isRunning()) runner.stop();
    workspace.clear();
    localStorage.removeItem(STORAGE_KEY);
    resetVisualOutputPanels();
    updateMobileToolbar();
  });

  btnSave?.addEventListener('click', async () => {
    await ensureWorkspace();
    downloadWorkspaceXml(workspace);
  });

  btnOpen?.addEventListener('click', async () => {
    const file = await pickWorkspaceXmlFile();
    if (!file) return;
    await ensureWorkspace();
    try {
      const text = await readFileAsText(file);
      await applyXmlToWorkspace(text);
    } catch (err) {
      console.error(err);
      const status = document.getElementById('visual-status');
      if (status) status.textContent = err.message || 'Could not open file';
    }
  });

  btnSamples?.addEventListener('click', () => {
    openSamplesDialog({
      onPick: async (path) => {
        await ensureWorkspace();
        try {
          const xml = await fetchSampleXml(path);
          await applyXmlToWorkspace(xml);
        } catch (err) {
          console.error(err);
          const status = document.getElementById('visual-status');
          if (status) status.textContent = err.message || 'Could not load sample';
        }
      },
    });
  });
}

async function ensureWorkspace() {
  if (workspace) {
    resizeWorkspace();
    return workspace;
  }

  await ensureBlocklyLoaded();

  const mount = document.getElementById('visual-blockly-div');
  if (!mount) throw new Error('Blockly mount missing');

  workspace = Blockly.inject(mount, {
    toolbox: buildToolbox(),
    media: 'visual/media/',
    grid: { spacing: 20, length: 3, colour: '#334155', snap: true },
    zoom: {
      controls: true,
      wheel: true,
      startScale: 0.9,
      maxScale: 3,
      minScale: 0.3,
      scaleSpeed: 1.1,
    },
    trashcan: true,
    sounds: true,
    theme: Blockly.Theme.defineTheme('kuttypy', {
      base: Blockly.Themes.Classic,
      componentStyles: {
        workspaceBackgroundColour: '#0f1419',
        toolboxBackgroundColour: '#1a2332',
        toolboxForegroundColour: '#e2e8f0',
        flyoutBackgroundColour: '#1a2332',
        flyoutForegroundColour: '#e2e8f0',
        flyoutOpacity: 0.98,
        scrollbarColour: '#475569',
        insertionMarkerColour: '#38bdf8',
        insertionMarkerOpacity: 0.4,
      },
    }),
  });

  wireBlocklyUndoRedo(workspace);
  loadWorkspaceFromStorage(workspace);
  workspace.addChangeListener((event) => {
    if (event.isUiEvent || event.type === Blockly.Events.FINISHED_LOADING) return;
    saveWorkspaceToStorage(workspace);
  });

  runner = createVisualRunner({
    getWorkspace: () => workspace,
    getDevice: () => session.getDevice(),
    outputEl: document.getElementById('visual-output'),
    registersEl: document.getElementById('visual-registers'),
    plotsHost: document.getElementById('visual-plots-host'),
    codeEl: document.getElementById('visual-codegen'),
    statusEl: document.getElementById('visual-status'),
    onRunningChange: (isOn) => {
      const btn = document.getElementById('btn-visual-run');
      if (!btn) return;
      const label = btn.querySelector('.btn-visual-run-label');
      if (label) label.textContent = isOn ? 'Stop' : 'Run';
      btn.classList.toggle('is-running', isOn);
      updateMobileToolbar();
    },
    onMobilePaneChange: () => updateMobileToolbar(),
  });

  return workspace;
}

export function initVisualView(options = {}) {
  if (options.getDevice) session.getDevice = options.getDevice;
  if (options.isConnected) session.isConnected = options.isConnected;
  if (options.withPollingPaused) session.withPollingPaused = options.withPollingPaused;
  if (initialized) return;
  initialized = true;

  window.kuttypyOpenSensorPicker = async (block) => {
    const pick = await openSensorPicker({
      device: session.getDevice(),
      isConnected: session.isConnected,
      withPollingPaused: session.withPollingPaused,
    });
    if (pick && block?.applySensor_) {
      block.applySensor_(pick.typeId, pick.address);
    }
  };

  wireToolbar();
  wireSideTabs();

  window.addEventListener('kuttypy:visual-enter', () => {
    updateMobileToolbar();
    ensureWorkspace().catch((err) => {
      console.error(err);
      const status = document.getElementById('visual-status');
      if (status) status.textContent = err.message;
    });
  });

  window.addEventListener('kuttypy:visual-leave', () => {
    clearTimeout(abortedFlashTimer);
    forceAbortedState = false;
    runner?.stop('abort');
    runner?.returnToBlocksView();
  });

  window.addEventListener('resize', () => {
    if (!document.body.classList.contains('view-visual-active')) return;
    updateMobileToolbar();
    resizeWorkspace();
  });

  if (typeof MOBILE_MQ.addEventListener === 'function') {
    MOBILE_MQ.addEventListener('change', () => {
      if (!document.body.classList.contains('view-visual-active')) return;
      updateMobileToolbar();
    });
  }
}
