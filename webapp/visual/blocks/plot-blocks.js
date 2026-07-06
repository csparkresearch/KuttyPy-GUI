/* Plot blocks — runtime uses Chart.js via visual-blockly-runtime.js */

Blockly.Blocks.plot_datapoint = {
  init() {
    this.appendDummyInput().appendField('PLOT Y Vs Time:');
    this.appendValueInput('VALUE')
      .setAlign(Blockly.ALIGN_LEFT)
      .appendField(new Blockly.FieldTextInput('myplot'), 'PLOTNAME')
      .appendField('Y :');
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
    this.setTooltip('Plot value(s) against time — number, array, or {name: value} object');
  },
};

Blockly.JavaScript.plot_datapoint = function (block) {
  const value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  const name = block.getFieldValue('PLOTNAME');
  return `sleep(0.001);\nplot('${name}',${value});\n`;
};

Blockly.Blocks.plot_datapoints = {
  init() {
    this.appendDummyInput().appendField('PLOT Y[] Vs Time:');
    this.appendValueInput('VALUE')
      .setAlign(Blockly.ALIGN_LEFT)
      .appendField(new Blockly.FieldTextInput('myplot'), 'PLOTNAME')
      .appendField('Y[] :');
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
  },
};

Blockly.JavaScript.plot_datapoints = function (block) {
  const value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  const name = block.getFieldValue('PLOTNAME');
  return `sleep(0.001);\nplot_array('${name}',${value});\n`;
};

Blockly.Blocks.plot_xy = {
  init() {
    this.appendDummyInput().appendField('PLOT X,Y');
    this.appendValueInput('X')
      .appendField(new Blockly.FieldTextInput('myplot'), 'PLOTNAME')
      .setAlign(Blockly.ALIGN_RIGHT)
      .appendField('X:');
    this.appendValueInput('Y')
      .setAlign(Blockly.ALIGN_RIGHT)
      .appendField('Y:');
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
  },
};

Blockly.JavaScript.plot_xy = function (block) {
  const name = block.getFieldValue('PLOTNAME');
  const vx = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  const vy = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  return `sleep(0.001);\nplot_xy('${name}',${vx},${vy});\n`;
};
