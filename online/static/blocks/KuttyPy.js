var textElements={};
var txt;

var stepper_pos=[0,0];
var set_stepper_pos = [[],[]], cursteppos=[0,0];
var step_positions=[[3,6,12,9,0], [3<<4,6<<4,12<<4,9<<4, 0]];

// ----------DOM MANIPULATION
const SVG_NS = "http://www.w3.org/2000/svg";
const SVG_XLINK = "http://www.w3.org/1999/xlink"
// an object to define the properties and text content of the text element 

// a function to create a text element 
function drawText(parent, props, textcontent) {
  // create a new text element
  let text = document.createElementNS(SVG_NS, "text");
  //set the attributes for the text
  for (var name in props) {
    if (props.hasOwnProperty(name)) {
      text.setAttributeNS(null, name, props[name]);
    }
  }
  text.textContent = textcontent;
  parent.appendChild(text);
  return text;
}

//Create arrow
function createArrow(parent, startX, startY, endX, endY, color = "black") {
  // create a new line element
  let line = document.createElementNS(SVG_NS, "line");
  // set attributes for the line (start and end points, stroke color)
  line.setAttributeNS(null, "x1", startX);
  line.setAttributeNS(null, "y1", startY);
  line.setAttributeNS(null, "x2", endX);
  line.setAttributeNS(null, "y2", endY);
  line.setAttributeNS(null, "stroke", color);
  line.setAttributeNS(null, "stroke-width", 2);

  // append the line to the parent SVG element
  parent.appendChild(line);
  return line;
}

// a function to create an image
function drawImage(parent, props, url) {
  // create a new text element
  let img = document.createElementNS(SVG_NS, "image");
  //set the attributes for the text
  for (var name in props) {
    if (props.hasOwnProperty(name)) {
      img.setAttributeNS(null, name, props[name]);
    }
  }
  img.setAttributeNS(SVG_XLINK, 'xlink:href', url);
  //text.textContent = textcontent;
  parent.appendChild(img);
  return img;
}


/*----- BINARY VALUE -------*/

Blockly.Blocks['binary_value'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("BINARY NUMBER");
    this.appendDummyInput()
        .appendField("7")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B7")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B6")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B5")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B4")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B3")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B2")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B1")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B0")
        .appendField("0");

    this.setOutput(true, "Number");
    this.setInputsInline(false);
    this.setColour(230);

    props= {
      x: 145,
      y: 15,
      "fill": "lightgreen",
      "dominant-baseline": "middle",
      "text-anchor": "left",
    };

    this.txt = drawText(this.getSvgRoot(),props,":");


 this.setTooltip("get binary value");
 this.setHelpUrl("");
  },
  bitset: function(val) {
  setTimeout(() => {

      var dropdown_channel = this.getFieldValue('REGISTER');
      var value=0;
      if( this.getFieldValue('B0') == "TRUE" )value|=1;
      if( this.getFieldValue('B1') == "TRUE" )value|=2;
      if( this.getFieldValue('B2') == "TRUE" )value|=4;
      if( this.getFieldValue('B3') == "TRUE" )value|=8;
      if( this.getFieldValue('B4') == "TRUE" )value|=16;
      if( this.getFieldValue('B5') == "TRUE" )value|=32;
      if( this.getFieldValue('B6') == "TRUE" )value|=64;
      if( this.getFieldValue('B7') == "TRUE" )value|=128;

      this.txt.textContent = '='+value+", 0x"+parseInt(value, 10).toString(16).toUpperCase();//+'[0b'+Number(value).toString(2)+']';

      }, 100);

  },


};


Blockly.JavaScript['binary_value'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value=0;
  if( block.getFieldValue('B0') == "TRUE" )value|=1;
  if( block.getFieldValue('B1') == "TRUE" )value|=2;
  if( block.getFieldValue('B2') == "TRUE" )value|=4;
  if( block.getFieldValue('B3') == "TRUE" )value|=8;
  if( block.getFieldValue('B4') == "TRUE" )value|=16;
  if( block.getFieldValue('B5') == "TRUE" )value|=32;
  if( block.getFieldValue('B6') == "TRUE" )value|=64;
  if( block.getFieldValue('B7') == "TRUE" )value|=128;

  var code = value;
  return [code,Blockly.JavaScript.ORDER_NONE];

};


Blockly.Python['binary_value'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value=0;
  if( block.getFieldValue('B0') == "TRUE" )value|=1;
  if( block.getFieldValue('B1') == "TRUE" )value|=2;
  if( block.getFieldValue('B2') == "TRUE" )value|=4;
  if( block.getFieldValue('B3') == "TRUE" )value|=8;
  if( block.getFieldValue('B4') == "TRUE" )value|=16;
  if( block.getFieldValue('B5') == "TRUE" )value|=32;
  if( block.getFieldValue('B6') == "TRUE" )value|=64;
  if( block.getFieldValue('B7') == "TRUE" )value|=128;
  //this.txt.textContent="Value:"+value+", 0x"+parseInt(value, 10).toString(16).toUpperCase();

  var code = value;
  return [code,Blockly.JavaScript.ORDER_NONE];

};

/*---------- REGISTER VALUE----------------*/

/*---------------------- SET REG---------------*/

Blockly.Blocks['reg'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["DDRA","DDRA"],["DDRB","DDRB"], ["DDRC","DDRC"], ["DDRD","DDRD"],
        ["PORTA","PORTA"],["PORTB","PORTB"],["PORTC","PORTC"],["PORTD","PORTD"],
        ["PINA","PINA"],["PINB","PINB"],["PINC","PINC"],["PIND","PIND"],
        ["ADCSRA","ADCSRA"],["ADMUX","ADMUX"],["ADCH","ADCH"],["ADCL","ADCL"],["TCNT0","TCNT0"]

        ]), "REGISTER");
    this.setInputsInline(false);
    this.setOutput(true);
    this.setColour(230);
 this.setTooltip("Get a register");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['reg'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  return [dropdown_channel,Blockly.JavaScript.ORDER_NONE];
};


/*---------------------- STEPDIR---------------*/

Blockly.Blocks['direction'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Clockwise","CW"],["Counter Clockwise","CCW"]

        ]), "DIR");
    this.setInputsInline(false);
    this.setOutput(true);
    this.setColour(230);
 this.setTooltip("Get a register");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['direction'] = function(block) {
  var dropdown_channel = block.getFieldValue('DIR');
  if( this.getFieldValue('DIR') == "CW" )
      return [1,Blockly.JavaScript.ORDER_NONE]; // clockwise is 1
  else
      return [0,Blockly.JavaScript.ORDER_NONE]; // clockwise is 1

};


Blockly.Python['direction'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  return [dropdown_channel,Blockly.Python.ORDER_NONE];
};



/* --------------- Get Voltage ------------ */



Blockly.Blocks['get_voltage'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read ADC")
        .appendField(new Blockly.FieldDropdown([["A0","0"], ["A1","1"], ["A2","2"], ["A3","3"], ["A4","4"], ["A5","5"], ["A6","6"], ["A7","7"]]), "CHANNEL");
    this.setOutput(true, "Number");
    this.setColour(330);

 this.setTooltip("Read Voltage from selected channel");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['get_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = "get_voltage("+dropdown_channel+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble Python into code variable.
  var code = 'readAdc('+dropdown_channel+')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};


/* --------------- Get reg ------------ */



Blockly.Blocks['get_reg'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ REGISTER")
        .appendField(new Blockly.FieldDropdown([["PINA","PINA"],["PINB","PINB"], ["PINC","PINC"], ["PIND","PIND"],["PORTA","PORTA"],["PORTB","PORTB"],["PORTC","PORTC"],["PORTD","PORTD"]]), "REGISTER");
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Read Voltage from selected channel");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['get_reg'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var code = "get_reg('"+dropdown_channel+"')";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_reg'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  // TODO: Assemble Python into code variable.
  var code = 'getReg(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};


/*---------------------- SET REG---------------*/

Blockly.Blocks['set_reg'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET REGISTER")
        .appendField(new Blockly.FieldDropdown([["DDRA","DDRA"],["DDRB","DDRB"], ["DDRC","DDRC"], ["DDRD","DDRD"],["PORTA","PORTA"],["PORTB","PORTB"],["PORTC","PORTC"],["PORTD","PORTD"]]), "REGISTER");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set register to value");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_reg'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_reg(\''+dropdown_channel+'\','+value+');\n';
  return code;
};


Blockly.Python['set_reg'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value_voltage = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  // TODO: Assemble Python into code variable.
  var code = 'setReg(\''+dropdown_channel+'\','+value_voltage+')\n';
  return code;
};


/*---------- STEPPER MOTORS ------------*/

Blockly.Blocks['init_stepper'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Init Stepper Motor[ DDRB=255]");
    this.appendDummyInput()
        .appendField("S1 :PB0-3, S2:PB4-7 outputs.");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("init stepper");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['init_stepper'] = function(block) {
  stepper_pos=[0,0];
  cursteppos = [4,4];
  //return '';
  return 'set_reg(\'DDRB\','+255+');\n';
};


Blockly.Python['init_stepper'] = function(block) {
  return  'set_reg(\'DDRB\','+255+')\n';
};



Blockly.Blocks['move_stepper'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Move Stepper:          ");
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(new Blockly.FieldDropdown([["PB0-3","B1"],["PB4-7","B2"]]), "PINS");
    this.appendValueInput("STEPS")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("STEPS: ");
    this.appendValueInput("DELAY")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("DELAY: ");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("move stepper motor");
 this.setHelpUrl("");

  props= {
   x: 135,
   y: 15,
   "fill": "lightgreen",
   "dominant-baseline": "middle",
   "text-anchor": "middle",
  };


  this.txt = drawText(this.getSvgRoot(),props,":");

  imgprops= {
   x: 0,
   y: 30,
   "dominant-baseline": "middle",
   "text-anchor": "middle",
   width: '80px',
   height: '80px'
  };
  this.imgbody = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_body.png");
  this.imgshaft = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_shaft.png");



  },
  set_stepper_display: function(val, angle) {
      this.txt.textContent = '['+val+']';
      this.imgshaft.setAttributeNS(null, "transform", `rotate(${angle} ${41} ${71})`);
  }

};


Blockly.JavaScript['move_stepper'] = function(block) {
  var code = '';
  var motor=1;


  if( this.getFieldValue('PINS') == "B1" ){
      motor = 0;
  }

  var steps = Blockly.JavaScript.valueToCode(block, 'STEPS', Blockly.JavaScript.ORDER_NONE);
  var msdelay = Blockly.JavaScript.valueToCode(block, 'DELAY', Blockly.JavaScript.ORDER_NONE);
  set_stepper_pos[motor].push(block);
  if( steps>0 ) // clockwise
      code = 'for(var i=0;i<'+steps+';i++){\nmove_stepper_cw('+motor+');\nsleep('+msdelay*.001+');\n}\n';
  else
      code = 'for(var i=0;i<'+steps*-1+';i++){\nmove_stepper_ccw('+motor+');\nsleep('+msdelay*.001+');\n}\n';
  return code;
};


Blockly.Python['move_stepper'] = function(block) {
  var code = '';
  var steps = Blockly.JavaScript.valueToCode(block, 'STEPS', Blockly.JavaScript.ORDER_NONE);
  if(steps>0 )
      code = 'for a in range('+steps+'):move_stepper_cw('+motor+')\n';
  else
      code = 'for a in range('+steps*-1+'):move_stepper_ccw('+motor+')\n';
  return code;
};


/*------------- MOVE STEPPERS --------------*/
Blockly.Blocks['move_steppers'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Move Steppers:          ")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('move_steppers');},'SS'));

    this.appendDummyInput()
        .appendField("MOTOR PB0-3:");
    this.appendValueInput("STEPS1")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("STEPS: ");
    this.appendDummyInput()
        .appendField(" ");

    this.appendDummyInput()
        .appendField("MOTOR PB4-7:")
    this.appendValueInput("STEPS2")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("STEPS: ");
    this.appendValueInput("DELAY")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("DELAY/step: ");

    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("move stepper motor");
 this.setHelpUrl("");

  imgprops= {
   x: 30,
   y: 60,
   "dominant-baseline": "middle",
   "text-anchor": "middle",
   width: '60px',
   height: '60px'
  };
  this.imgbody1 = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_body.png");
  this.imgshaft1 = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_shaft.png");
  imgprops['y']=138;
  this.imgbody2 = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_body.png");
  this.imgshaft2 = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_shaft.png");


  props= {
   x: 140,
   y: 42,
   "fill": "magenta",
   "dominant-baseline": "middle",
   "text-anchor": "middle",
  };

  this.txt1 = drawText(this.getSvgRoot(),props,":");
  props['y']=130;
  this.txt2 = drawText(this.getSvgRoot(),props,":");


  },
  set_stepper_display: function(val1, val2) {
      this.txt1.textContent = '['+parseInt(val1)+']';
      this.txt2.textContent = '['+parseInt(val2)+']';

      this.imgshaft1.setAttributeNS(null, "transform", `rotate(${val1} ${61} ${91})`);
      this.imgshaft2.setAttributeNS(null, "transform", `rotate(${val2} ${61} ${169})`);


  },


};


Blockly.JavaScript['move_steppers'] = function(block) {
  var code = '';
  var motor=1;
  var dir1=0, dir2=0;

  var steps1 = Blockly.JavaScript.valueToCode(block, 'STEPS1', Blockly.JavaScript.ORDER_NONE);
  var steps2 = Blockly.JavaScript.valueToCode(block, 'STEPS2', Blockly.JavaScript.ORDER_NONE);
  var msdelay = Blockly.JavaScript.valueToCode(block, 'DELAY', Blockly.JavaScript.ORDER_NONE);

  set_stepper_pos[0].push(block);
  code = 'move_stepper('+steps1+','+steps2+','+msdelay+');\nsleep('+msdelay*.001+');\n';
  return code;
};


Blockly.Python['move_steppers'] = function(block) {
  var code = '';
  var motor=1;
  var dir1=0, dir2=0;

  var steps1 = Blockly.JavaScript.valueToCode(block, 'STEPS1', Blockly.JavaScript.ORDER_NONE);
  var steps2 = Blockly.JavaScript.valueToCode(block, 'STEPS2', Blockly.JavaScript.ORDER_NONE);
  var msdelay = Blockly.JavaScript.valueToCode(block, 'DELAY', Blockly.JavaScript.ORDER_NONE);

  code = 'move_stepper('+steps1+','+steps2+','+msdelay+')\nsleep('+msdelay*.001+')\n';
  return code;
};




/* ---------- set_pwm-------------*/

Blockly.Blocks['set_pwm'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setCheck(null)
        .appendField("Set Brightness of")
        .appendField(new Blockly.FieldDropdown([["RED LED","RED"], ["GREEN LED","GREEN"], ["BLUE LED","BLUE"]]), "NAME");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(0);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_pwm'] = function(block) {
  var dropdown_name = block.getFieldValue('NAME');
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_ATOMIC);
  var code = 'set_pwm(\''+dropdown_name+'\','+value+');\n';
  return code;
};

Blockly.Python['set_pwm'] = function(block) {
  var dropdown_name = block.getFieldValue('NAME');
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_ATOMIC);
  var code = 'set_pwm(\''+dropdown_name+'\','+value+')\n';
  return code;
};

/*---------------------- SET REG FROM STRING---------------*/

Blockly.Blocks['set_reg_from_string'] = {
  init: function() {
    this.appendValueInput("REGISTER")
        .appendField("Set Register");
    this.appendValueInput("VALUE")
        .appendField(", to:")
        .setCheck(null);
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['set_reg_from_string'] = function(block) {
  //var dropdown_channel = block.getFieldValue('REGISTER');
  var reg = Blockly.JavaScript.valueToCode(block, 'REGISTER', Blockly.JavaScript.ORDER_NONE);
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  if(reg.startsWith('\'') || reg.startsWith('\"')  ) // String has quotes.
      var code = 'set_reg('+reg+','+value+');\n';
  else // add quotes
      var code = 'set_reg(\''+reg+'\','+value+');\n';
  return code;
};


Blockly.Python['set_reg_from_string'] = function(block) {
  var reg = Blockly.Python.valueToCode(block, 'REGISTER', Blockly.Python.ORDER_NONE);
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  if(reg.startsWith('\'') || reg.startsWith('\"')  ) // String has quotes.
      var code = 'set_reg('+reg+','+value+')\n';
  else // add quotes
      var code = 'set_reg(\''+reg+'\','+value+')\n';
  return code;
};


/*---------------------- GET REG FROM STRING---------------*/

Blockly.Blocks['get_reg_from_string'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read Register")
        .appendField(new Blockly.FieldTextInput(""), "REGISTER")
    this.setInputsInline(false);
    this.setColour(230);
    this.setOutput(true, "Number");
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['get_reg_from_string'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var code = 'get_reg(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['get_reg_from_string'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  // TODO: Assemble Python into code variable.
  var code = 'get_reg(\''+dropdown_channel+'\')';
  return [code,Blockly.Python.ORDER_NONE];
};

/* ---------- Bytes to Integer -------------*/

Blockly.Blocks['bytes_to_int'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Bytes to Int");
    this.appendValueInput("HIGH")
        .setAlign(Blockly.ALIGN_RIGHT)
        .setCheck(null)
        .appendField("MSB        (");
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("<<8)");
    this.appendValueInput("LOW")
        .setAlign(Blockly.ALIGN_RIGHT)
        .setCheck(null)
        .appendField("LSB     |  (");
    this.appendDummyInput()
	.setAlign(Blockly.ALIGN_RIGHT)
        .appendField(")");
    this.setInputsInline(false);
    this.setOutput(true, null);
    this.setColour(135);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['bytes_to_int'] = function(block) {
  var value_low = Blockly.JavaScript.valueToCode(block, 'LOW', Blockly.JavaScript.ORDER_NONE);
  var value_high = Blockly.JavaScript.valueToCode(block, 'HIGH', Blockly.JavaScript.ORDER_NONE);
  var code = '('+value_low+')|('+value_high+'<<8)';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['bytes_to_int'] = function(block) {
  var value_low = Blockly.Python.valueToCode(block, 'LOW', Blockly.Python.ORDER_NONE);
  var value_high = Blockly.Python.valueToCode(block, 'HIGH', Blockly.Python.ORDER_NONE);
  var code = '('+value_low+')|('+value_high+'<<8)';
  return [code, Blockly.Python.ORDER_NONE];
};

/* ---------- Shift bits -------------*/

Blockly.Blocks['shift_bits'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("Shift bit:");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["<<","<<"], [">>",">>"]]), "DIRECTION")
    this.appendValueInput("BITS")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_LEFT)
    this.setInputsInline(true);
    this.setOutput(true, null);
    this.setColour(135);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['shift_bits'] = function(block) {
  var direction = block.getFieldValue('DIRECTION');
  var bits = Blockly.JavaScript.valueToCode(block, 'BITS', Blockly.JavaScript.ORDER_NONE);
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
    code = value+direction+bits;
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['shift_bits'] = function(block) {
  var direction = block.getFieldValue('DIRECTION');
  var bits = Blockly.JavaScript.valueToCode(block, 'BITS', Blockly.JavaScript.ORDER_NONE);
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  code = value+direction+bits;
  return [code, Blockly.Python.ORDER_NONE];
};


/* ---------- clear bit -------------*/

Blockly.Blocks['clear_bit'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("Set/Clear Bit:");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["&~(1<<","&~(1<<"], ["|(1<<","|(1<<"]]), "OPERATION")
        .appendField(new Blockly.FieldDropdown([["0","0"], ["1","1"], ["2","2"], ["2","2"], ["3","3"], ["4","4"], ["5","5"], ["6","6"], ["7","7"]]), "BITS");
    this.appendDummyInput()
        .appendField(")");
    this.setInputsInline(true);
    this.setOutput(true, null);
    this.setColour(135);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['clear_bit'] = function(block) {
  var operation = block.getFieldValue('OPERATION');
  var bits = block.getFieldValue('BITS');
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
    code = value+operation+bits+")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['clear_bit'] = function(block) {
  var operation = block.getFieldValue('OPERATION');
  var bits = block.getFieldValue('BITS');
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  code = value+operation+bits+")";
  return [code, Blockly.Python.ORDER_NONE];
};

/* ---------- AND/OR bit -------------*/

Blockly.Blocks['and_or'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_LEFT)
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["&","&"], ["|","|"]]), "OPERATION")
    this.appendValueInput("VALUE2")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_LEFT)
    this.setInputsInline(true);
    this.setOutput(true, null);
    this.setColour(135);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['and_or'] = function(block) {
  var operation = block.getFieldValue('OPERATION');
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  var value2 = Blockly.JavaScript.valueToCode(block, 'VALUE2', Blockly.JavaScript.ORDER_NONE);
    code = value+operation+value2;
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['and_or'] = function(block) {
  var operation = block.getFieldValue('OPERATION');
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var value2 = Blockly.JavaScript.valueToCode(block, 'VALUE2', Blockly.JavaScript.ORDER_NONE);
    code = value+operation+value2;
  return [code, Blockly.Python.ORDER_NONE];
};


/*---------------------- SET REG FROM STRING---------------*/

Blockly.Blocks['set_dac'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Set DAC on PORTC ");
    this.appendValueInput("VALUE")
        .setCheck(null)
        .appendField(", to:");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['set_dac'] = function(block) {
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  var code = "set_reg('DDRC',255);\nset_reg('PORTC',"+value+");\n";
  return code;
};


Blockly.Python['set_dac'] = function(block) {
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = "set_reg('DDRC',255)\nset_reg('PORTC',"+value+")\n";
  return code;
};


/*---------------------- SET REG BITS FROM STRING---------------*/

Blockly.Blocks['set_reg_bits_string'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("SET BITS")
        .appendField(new Blockly.FieldTextInput(""), "REGISTER");
    this.appendDummyInput()
        .appendField("7")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B7")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B6")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B5")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B4")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B3")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B2")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B1")
        .appendField(new Blockly.FieldCheckbox("FALSE",this.bitset.bind(this)), "B0")
        .appendField("0");

    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);

    props= {
      x: 145,
      y: 15,
      "fill": "lightgreen",
      "dominant-baseline": "middle",
      "text-anchor": "left",
    };

    this.txt = drawText(this.getSvgRoot(),props,":");


 this.setTooltip("Set register to value");
 this.setHelpUrl("");
  },
  bitset: function(val) {
  setTimeout(() => {

      var dropdown_channel = this.getFieldValue('REGISTER');
      var value=0;
      if( this.getFieldValue('B0') == "TRUE" )value|=1;
      if( this.getFieldValue('B1') == "TRUE" )value|=2;
      if( this.getFieldValue('B2') == "TRUE" )value|=4;
      if( this.getFieldValue('B3') == "TRUE" )value|=8;
      if( this.getFieldValue('B4') == "TRUE" )value|=16;
      if( this.getFieldValue('B5') == "TRUE" )value|=32;
      if( this.getFieldValue('B6') == "TRUE" )value|=64;
      if( this.getFieldValue('B7') == "TRUE" )value|=128;

      this.txt.textContent = '='+value;//+'[0b'+Number(value).toString(2)+']';

      }, 100);

  },


};


Blockly.JavaScript['set_reg_bits_string'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value=0;
  if( block.getFieldValue('B0') == "TRUE" )value|=1;
  if( block.getFieldValue('B1') == "TRUE" )value|=2;
  if( block.getFieldValue('B2') == "TRUE" )value|=4;
  if( block.getFieldValue('B3') == "TRUE" )value|=8;
  if( block.getFieldValue('B4') == "TRUE" )value|=16;
  if( block.getFieldValue('B5') == "TRUE" )value|=32;
  if( block.getFieldValue('B6') == "TRUE" )value|=64;
  if( block.getFieldValue('B7') == "TRUE" )value|=128;

  var code = 'set_reg(\''+dropdown_channel+'\','+value+');\n';
  return code;
};


Blockly.Python['set_reg_bits_string'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value=0;
  if( block.getFieldValue('B0') == "TRUE" )value|=1;
  if( block.getFieldValue('B1') == "TRUE" )value|=2;
  if( block.getFieldValue('B2') == "TRUE" )value|=4;
  if( block.getFieldValue('B3') == "TRUE" )value|=8;
  if( block.getFieldValue('B4') == "TRUE" )value|=16;
  if( block.getFieldValue('B5') == "TRUE" )value|=32;
  if( block.getFieldValue('B6') == "TRUE" )value|=64;
  if( block.getFieldValue('B7') == "TRUE" )value|=128;
  this.txt.textContent="Value:"+value+", 0x"+parseInt(value, 10).toString(16).toUpperCase();
  var code = 'setReg(\''+dropdown_channel+'\','+value+')\n';
  return code;
};

/*---------------------- SET REG BITS---------------*/

Blockly.Blocks['set_reg_bits'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("SET BITS")
        .appendField(new Blockly.FieldDropdown([["DDRA","DDRA"],["DDRB","DDRB"], ["DDRC","DDRC"], ["DDRD","DDRD"],["PORTA","PORTA"],["PORTB","PORTB"],["PORTC","PORTC"],["PORTD","PORTD"]]), "REGISTER");
    this.appendDummyInput()
        .appendField("7")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B7")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B6")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B5")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B4")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B3")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B2")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B1")
        .appendField(new Blockly.FieldCheckbox("FALSE"), "B0")
        .appendField("0");

    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);

 this.setTooltip("Set register to value");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_reg_bits'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value=0;
  if( block.getFieldValue('B0') == "TRUE" )value|=1;
  if( block.getFieldValue('B1') == "TRUE" )value|=2;
  if( block.getFieldValue('B2') == "TRUE" )value|=4;
  if( block.getFieldValue('B3') == "TRUE" )value|=8;
  if( block.getFieldValue('B4') == "TRUE" )value|=16;
  if( block.getFieldValue('B5') == "TRUE" )value|=32;
  if( block.getFieldValue('B6') == "TRUE" )value|=64;
  if( block.getFieldValue('B7') == "TRUE" )value|=128;

  var code = 'set_reg(\''+dropdown_channel+'\','+value+');\n';
  return code;
};


Blockly.Python['set_reg_bits'] = function(block) {
  var dropdown_channel = block.getFieldValue('REGISTER');
  var value=0;
  if( block.getFieldValue('B0') == "TRUE" )value|=1;
  if( block.getFieldValue('B1') == "TRUE" )value|=2;
  if( block.getFieldValue('B2') == "TRUE" )value|=4;
  if( block.getFieldValue('B3') == "TRUE" )value|=8;
  if( block.getFieldValue('B4') == "TRUE" )value|=16;
  if( block.getFieldValue('B5') == "TRUE" )value|=32;
  if( block.getFieldValue('B6') == "TRUE" )value|=64;
  if( block.getFieldValue('B7') == "TRUE" )value|=128;
  var code = 'setReg(\''+dropdown_channel+'\','+value+')\n';
  return code;
};






//Flask Endpoints



//-------------------- API ------------------------



function initKuttyPy(interpreter, scope) {

	          // kuttypy API CALLS
            interpreter.setProperty(scope, 'get_voltage', interpreter.createAsyncFunction(
                function(channel, callback) {
                    fetch(`/get_voltage/${channel}`)
                    .then(response => response.json())
                    .then(data => {
                        callback(data.voltage);
                    })
                    .catch(error => {
                        console.error('Error fetching voltage:', error);
                        callback(0);
                    });
                }
            ));


        var getRegWrapper = interpreter.createAsyncFunction(function(channel, callback) {
            fetch(`/get_reg/${channel}`)
            .then(response => response.json())
            .then(data => {
                showReg(channel,data.data);
                callback(data.data);  // Pass the register value to Blockly
            })
            .catch(error => {
                showReg(channel,'err');
                console.error('Error fetching register value:', error);
                callback(0);  // Return 0 if there's an error
            });
        });

        interpreter.setProperty(scope, 'get_reg', getRegWrapper);
        interpreter.setProperty(scope, 'getReg', getRegWrapper);

        var setRegWrapper = interpreter.createAsyncFunction(function(channel, value, callback) {
            fetch('/set_reg', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    reg: channel,
                    data: value
                })
            })
            .then(response => response.json())
            .then(data => {
                showReg(channel,value);
                callback();  // Just call the callback once the register is set
            })
            .catch(error => {
                showReg(channel,'err');
                console.error('Error setting register value:', error);
                callback();
            });
        });

        interpreter.setProperty(scope, 'set_reg', setRegWrapper);
        interpreter.setProperty(scope, 'setReg', setRegWrapper);


        // Add an API for stepper
        var wrapper = interpreter.createAsyncFunction(
            function(motor, callback) {
                stepper_pos[motor] += 1;
                cursteppos[motor] += 1;
                if (cursteppos[motor] > 3) cursteppos[motor] = 0;

                fetch('/set_reg', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        reg: 'PORTB',
                        data: step_positions[0][cursteppos[0]] + step_positions[1][cursteppos[1]]
                    })
                })
                .then(response => response.json())
                .then(data => {
                        for (var i = 0; i < set_stepper_pos[motor].length; i++) {
                            set_stepper_pos[motor][i].set_stepper_display(stepper_pos[motor], stepper_pos[motor]);
                        }
                        callback(); // Call the callback after updating the display
                })
                .catch(error => {
                        callback();
                });



            }
        );
        interpreter.setProperty(scope, 'move_stepper_cw', wrapper);

        var wrapper = interpreter.createAsyncFunction(
            function(motor, callback) {
                stepper_pos[motor] -= 1;
                cursteppos[motor] -= 1;
                if (cursteppos[motor] < 0) cursteppos[motor] = 3;

                fetch('/set_reg', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        reg: 'PORTB',
                        data: step_positions[0][cursteppos[0]] + step_positions[1][cursteppos[1]]
                    })
                })
                .then(response => response.json())
                .then(data => {
                        for (var i = 0; i < set_stepper_pos[motor].length; i++) {
                            set_stepper_pos[motor][i].set_stepper_display(stepper_pos[motor], stepper_pos[motor]);
                        }
                        callback(); // Call the callback after updating the display
                })
                .catch(error => {
                        callback();
                });






            }
        );
        interpreter.setProperty(scope, 'move_stepper_ccw', wrapper);

        var wrapper = interpreter.createAsyncFunction( // Move based on direction.
            function(steps1, steps2, msdelay, callback) {
                var longer_distance = 1. * Math.max(Math.abs(steps1), Math.abs(steps2));
                var d1 = steps1 / longer_distance, d2 = steps2 / longer_distance;

                var moveSteps = (mystep) => {
                    //Motor1
                    stepper_pos[0] += d1;
                    cursteppos[0] += d1;
                    if (cursteppos[0] < 0) cursteppos[0] = 3;
                    if (cursteppos[0] > 3) cursteppos[0] = 0;

                    //Motor2
                    stepper_pos[1] += d2;
                    cursteppos[1] += d2;
                    if (cursteppos[1] < 0) cursteppos[1] = 3;
                    if (cursteppos[1] > 3) cursteppos[1] = 0;


                    fetch('/set_reg', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            reg: 'PORTB',
                            data: step_positions[0][parseInt(cursteppos[0])] + step_positions[1][parseInt(cursteppos[1])]
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                            for (var i = 0; i < set_stepper_pos[0].length; i++) {
                                set_stepper_pos[0][i].set_stepper_display(stepper_pos[0], stepper_pos[1]);
                            }
                            callback(); // Call the callback after updating the display
                    })
                    .catch(error => {
                            callback();
                    });

                    if (mystep < longer_distance - 1) {
                        setTimeout(() => moveSteps(mystep + 1), msdelay);
                    } else {
                        callback(); // Call the callback after all steps are done
                    }



                };

                moveSteps(0); // Start moving steps
            }
        );
        interpreter.setProperty(scope, 'move_stepper', wrapper);


	}






