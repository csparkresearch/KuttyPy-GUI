/**
 * Blockly block asset paths — relative to the webapp (not site-root /media).
 */
window.KUTTYPY_MEDIA = 'visual/media/';
window.kuttypyMedia = function (name) {
  const file = String(name).replace(/^media\//, '');
  return window.KUTTYPY_MEDIA + file;
};
window.showBlockHelp = window.showBlockHelp || function () {};
