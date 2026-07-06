/**
 * Minimal Blockly definitions for legacy sample XML blocks with no surviving source.
 * Allows samples to load; runtime may not implement these APIs in the webapp.
 */

function legacyStmt(type, label) {
  Blockly.Blocks[type] = {
    init() {
      this.appendDummyInput().appendField(label || type);
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(45);
    },
  };
  Blockly.JavaScript[type] = () => `// legacy block: ${type}\n`;
}

function legacyExpr(type, label, fields = []) {
  Blockly.Blocks[type] = {
    init() {
      this.appendDummyInput().appendField(label || type);
      fields.forEach(([text, name, options]) => {
        if (options) {
          this.appendDummyInput().appendField(text).appendField(new Blockly.FieldDropdown(options), name);
        } else {
          this.appendDummyInput().appendField(text).appendField(new Blockly.FieldTextInput(''), name);
        }
      });
      this.setOutput(true, null);
      this.setColour(45);
    },
  };
  Blockly.JavaScript[type] = () => ['0', Blockly.JavaScript.ORDER_ATOMIC];
}

Blockly.Blocks.sendMessage = {
  init() {
    this.appendValueInput('TEXT').appendField('send message');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(160);
  },
};
Blockly.JavaScript.sendMessage = () => '// legacy: sendMessage\n';

legacyStmt('enable_gps', 'enable GPS');

Blockly.Blocks.get_phone_gps = {
  init() {
    this.appendDummyInput()
      .appendField('phone GPS')
      .appendField(new Blockly.FieldDropdown([['lat', '0'], ['lng', '1']]), 'CHANNEL');
    this.setOutput(true, null);
    this.setColour(160);
  },
};
Blockly.JavaScript.get_phone_gps = () => ['0', Blockly.JavaScript.ORDER_ATOMIC];

Blockly.Blocks.mqtt_publish_gps = {
  init() {
    this.appendValueInput('CHANNEL').appendField('mqtt publish gps');
    this.appendValueInput('SENSOR').appendField('sensor');
    this.appendValueInput('PARAMETER').appendField('parameter');
    this.appendValueInput('DATA').appendField('data');
    this.appendValueInput('LAT').appendField('lat');
    this.appendValueInput('LNG').appendField('lng');
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(260);
  },
};
Blockly.JavaScript.mqtt_publish_gps = () => '// legacy: mqtt_publish_gps\n';
