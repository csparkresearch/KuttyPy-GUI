/* Legacy plot blocks for sample XML compatibility. */
Blockly.Blocks['plot_xyarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y[]:");
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .appendField(new Blockly.FieldCheckbox("TRUE"), "CLEAR")
        .appendField("Clear?");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var clr = block.getFieldValue('CLEAR');
  var state = (clr == "TRUE")?true:false;
  var code = 'sleep(0.001);\n'+'plot_xyarray(\''+name+'\','+X+','+Y+','+state+');\n';

  return code;
};


Blockly.Python['plot_xyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xyarray('+X+','+Y+')\n';

  return code;
};



/*---------------------- Plot plot_xyyarray ---------------*/



Blockly.Blocks['plot_xyyarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y1")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y1[]:")
    this.appendValueInput("Y2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .appendField("ARRAY Y2[]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y1, Y2 arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y1 = Blockly.JavaScript.valueToCode(block, 'Y1', Blockly.JavaScript.ORDER_NONE);
  var Y2 = Blockly.JavaScript.valueToCode(block, 'Y2', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var code = 'sleep(0.001);\n'+'plot_xyyarray(\''+name+'\','+X+','+Y1+','+Y2+');\n';

  return code;
};


Blockly.Python['plot_xyyarray'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y1 = Blockly.Python.valueToCode(block, 'Y1', Blockly.Python.ORDER_NONE);
  var Y2 = Blockly.Python.valueToCode(block, 'Y2', Blockly.Python.ORDER_NONE);
  var code = 'plot_xyyarray('+X+','+Y1+','+Y2+')\n';
  return code;
};

/*---------------------- Plot plot_xyyyarray ---------------*/



Blockly.Blocks['plot_xyyyarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y1")
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y1[]:")
    this.appendValueInput("Y2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y2[]:")
    this.appendValueInput("Y3")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y3[]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y1, Y2, Y3 arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyyyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y1 = Blockly.JavaScript.valueToCode(block, 'Y1', Blockly.JavaScript.ORDER_NONE);
  var Y2 = Blockly.JavaScript.valueToCode(block, 'Y2', Blockly.JavaScript.ORDER_NONE);
  var Y3 = Blockly.JavaScript.valueToCode(block, 'Y3', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var code = 'sleep(0.001);\n'+'plot_xyyyarray(\''+name+'\','+X+','+Y1+','+Y2+','+Y3+');\n';

  return code;
};


Blockly.Python['plot_xyyyarray'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y1 = Blockly.Python.valueToCode(block, 'Y1', Blockly.Python.ORDER_NONE);
  var Y2 = Blockly.Python.valueToCode(block, 'Y2', Blockly.Python.ORDER_NONE);
  var Y3 = Blockly.Python.valueToCode(block, 'Y3', Blockly.Python.ORDER_NONE);
  var code = 'sleep(0.001)\n'+'plot_xyyyarray('+X+','+Y1+','+Y2+','+Y3+')\n';
  return code;
};

/*---------------------- Plot XY ---------------*/


Blockly.Blocks['plot_xy'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("PLOT X,Y")
    this.appendValueInput("X")
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("X:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Y:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xy'] = function(block) {
  var name = block.getFieldValue('PLOTNAME');
  var vx = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var vy = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xy(\''+name+'\','+vx+','+vy+')\n';

  return code;
};


Blockly.Python['plot_xy'] = function(block) {
  var vx = Blockly.JavaScript.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var vy = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.Python.ORDER_NONE);
  var code = 'plot_xy('+vx+','+vy+')\n';

  return code;
};




/*---------------------- Polar Plot ---------------*/


Blockly.Blocks['plot_radar'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Polar Plot")
    this.appendValueInput("MAXRADIUS")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Maximum Radius:")
    this.appendValueInput("RADIUS")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("RADIUS:")
    this.appendValueInput("ANGLE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ANGLE(Deg):")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot R, Theta");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_radar'] = function(block) {
  var angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.JavaScript.ORDER_NONE);
  var radius = Blockly.JavaScript.valueToCode(block, 'RADIUS', Blockly.JavaScript.ORDER_NONE);
  var maxrad = Blockly.JavaScript.valueToCode(block, 'MAXRADIUS', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_radar('+angle+','+radius+','+maxrad+');\n';

  return code;
};


Blockly.Python['plot_radar'] = function(block) {
  var angle = Blockly.Python.valueToCode(block, 'ANGLE', Blockly.Python.ORDER_NONE);
  var radius = Blockly.Python.valueToCode(block, 'RADIUS', Blockly.Python.ORDER_NONE);
  var maxrad = Blockly.Python.valueToCode(block, 'MAXRADIUS', Blockly.Python.ORDER_NONE);
  var code = 'plot_radar('+angle+','+radius+','+maxrad+')\n';

  return code;
};
