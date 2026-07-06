/**
 * Save / open Blockly workspace XML files.
 */

export function workspaceToXmlText(ws) {
  const xml = Blockly.Xml.workspaceToDom(ws);
  return Blockly.Xml.domToText(xml);
}

export function loadXmlIntoWorkspace(ws, xmlText) {
  const xml = Blockly.Xml.textToDom(xmlText);
  ws.clear();
  Blockly.Xml.domToWorkspace(xml, ws);
}

export function downloadWorkspaceXml(ws, filename = 'kuttypy-blocks.xml') {
  const text = workspaceToXmlText(ws);
  const blob = new Blob([text], { type: 'application/xml;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function pickWorkspaceXmlFile() {
  return new Promise((resolve) => {
    const input = document.getElementById('visual-file-input');
    if (!input) {
      resolve(null);
      return;
    }

    const onChange = () => {
      input.removeEventListener('change', onChange);
      const file = input.files?.[0] ?? null;
      input.value = '';
      resolve(file);
    };

    input.addEventListener('change', onChange);
    input.click();
  });
}

export async function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.onerror = () => reject(reader.error || new Error('Could not read file'));
    reader.readAsText(file);
  });
}
