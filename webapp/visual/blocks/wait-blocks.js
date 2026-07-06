/* Wait / sleep block */

Blockly.Blocks.wait_seconds = {
  init() {
    this.appendDummyInput()
      .appendField('wait')
      .appendField(new Blockly.FieldNumber(1, 0, 600, 0.1), 'SECONDS')
      .appendField('seconds');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(120);
    this.setTooltip('Pause program execution');
  },
};

Blockly.JavaScript.wait_seconds = function (block) {
  const seconds = Number(block.getFieldValue('SECONDS'));
  return `sleep(${seconds});\n`;
};

Blockly.Python.wait_seconds = function (block) {
  const seconds = Number(block.getFieldValue('SECONDS'));
  return `time.sleep(${seconds})\n`;
};
