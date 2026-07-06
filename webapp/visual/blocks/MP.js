var camCallBack= null;
var mycam='front';


Blockly.Blocks['ai_isHandAvailable'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_isHandAvailable",
            "lastDummyAlign0": "CENTRE",
            "message0": "Is hand Visible?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is hand Visible?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_isHandAvailable'] = function (block) {
    return ['isHandAvailable()', Blockly.JavaScript.ORDER_NONE];
};


Blockly.Blocks['ai_isIndexExtendend'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_isIndexExtendend",
            "lastDummyAlign0": "CENTRE",
            "message0": "Is Index Finger Extended?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is Index Finger Extended?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_isIndexExtendend'] = function (block) {
    return ['isIndexFingerExtended()', Blockly.JavaScript.ORDER_NONE];
};

Blockly.Blocks['ai_isMiddleExtendend'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_isMiddleExtendend",
            "lastDummyAlign0": "CENTRE",
            "message0": "Is Middle Finger Extended?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is Middle Finger Extended?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_isMiddleExtendend'] = function (block) {
    return ['isMiddleFingerExtended()', Blockly.JavaScript.ORDER_NONE];
};

Blockly.Blocks['ai_isRingExtendend'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_isRingExtendend",
            "lastDummyAlign0": "CENTRE",
            "message0": "Is Ring Finger Extended?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is Ring Finger Extended?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_isRingExtendend'] = function (block) {
    return ['isRingFingerExtended()', Blockly.JavaScript.ORDER_NONE];
};

Blockly.Blocks['ai_isLittleExtendend'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_isLittleExtendend",
            "lastDummyAlign0": "CENTRE",
            "message0": "Is Little Finger Extended?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is Little Finger Extended?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_isLittleExtendend'] = function (block) {
    return ['isLittleFingerExtended()', Blockly.JavaScript.ORDER_NONE];
};

Blockly.Blocks['ai_isHandOpen'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_isHandOpen",
            "lastDummyAlign0": "CENTRE",
            "message0": "Is Hand Open?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is Hand Open?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_isHandOpen'] = function (block) {
    return ['isHandExtended()', Blockly.JavaScript.ORDER_NONE];
};

Blockly.Blocks['ai_vertices'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_vertices",
            "lastDummyAlign0": "CENTRE",
            "message0": "Get Coordinate Array",
            "output": "Array",
            "colour": 75,
            "tooltip": "Get Coordinates",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_vertices'] = function (block) {
    return ['getCoordinates()', Blockly.JavaScript.ORDER_NONE];
};


Blockly.Blocks['ai_getcoord'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_getcoord",
            "message0": "Save X value into %1 and save Y value into %2 from finger joint %3",
            "args0": [
              {
                "type": "field_variable",
                "name": "X_VAR",
                "variable": "finger_x"
              },
              {
                "type": "field_variable",
                "name": "Y_VAR",
                "variable": "finger_y"
              },
              {
                "type": "field_dropdown",
                "name": "finger_joint",
                "options": [
                  [
                    "0",
                    "0"
                  ],
                  [
                    "1",
                    "1"
                  ],
                  [
                    "2",
                    "2"
                  ],
                  [
                    "3",
                    "3"
                  ],
                  [
                    "4",
                    "4"
                  ],
                  [
                    "5",
                    "5"
                  ],
                  [
                    "6",
                    "6"
                  ],
                  [
                    "7",
                    "7"
                  ],
                  [
                    "8",
                    "8"
                  ],
                  [
                    "9",
                    "9"
                  ],
                  [
                    "10",
                    "10"
                  ],
                  [
                    "11",
                    "11"
                  ],
                  [
                    "12",
                    "12"
                  ],
                  [
                    "13",
                    "13"
                  ],
                  [
                    "14",
                    "14"
                  ],
                  [
                    "15",
                    "15"
                  ],
                  [
                    "16",
                    "16"
                  ],
                  [
                    "17",
                    "17"
                  ],
                  [
                    "18",
                    "18"
                  ],
                  [
                    "19",
                    "19"
                  ],
                  [
                    "20",
                    "20"
                  ]
                ]
              }
            ],
            "previousStatement": null,
            "nextStatement": null,
            "colour": 180,
            "tooltip": "",
            "helpUrl": ""
        });
    }
};

Blockly.JavaScript['ai_getcoord'] = function(block) {
    var variable_x_var = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('X_VAR'), Blockly.Variables.NAME_TYPE);
    var variable_y_var = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('Y_VAR'), Blockly.Variables.NAME_TYPE);
    var dropdown_finger_joint = block.getFieldValue('finger_joint');

    var code = `${variable_x_var} = getCoordinateX(${dropdown_finger_joint});\n`;
    code += `${variable_y_var} = getCoordinateY(${dropdown_finger_joint});\n`;

    return code;
};


Blockly.Blocks['ai_get'] = {
    init: function () {
        this.jsonInit({

            "output": "Number",

            "type": "ai_get",
            "message0": "Get %1 coordinate from finger joint %2",
            "args0": [
              {
                 "type": "field_dropdown",
                 "name": "axis",
                 "options": [
                   [
                     "X",
                     "X"
                   ],
                   [
                     "Y",
                     "Y"
                   ],
                   [
                     "Z",
                     "Z"
                   ]
                 ]
               },
            {
                "type": "field_dropdown",
                "name": "finger_joint",
                "options": [
                  [
                    "0",
                    "0"
                  ],
                  [
                    "1",
                    "1"
                  ],
                  [
                    "2",
                    "2"
                  ],
                  [
                    "3",
                    "3"
                  ],
                  [
                    "4",
                    "4"
                  ],
                  [
                    "5",
                    "5"
                  ],
                  [
                    "6",
                    "6"
                  ],
                  [
                    "7",
                    "7"
                  ],
                  [
                    "8",
                    "8"
                  ],
                  [
                    "9",
                    "9"
                  ],
                  [
                    "10",
                    "10"
                  ],
                  [
                    "11",
                    "11"
                  ],
                  [
                    "12",
                    "12"
                  ],
                  [
                    "13",
                    "13"
                  ],
                  [
                    "14",
                    "14"
                  ],
                  [
                    "15",
                    "15"
                  ],
                  [
                    "16",
                    "16"
                  ],
                  [
                    "17",
                    "17"
                  ],
                  [
                    "18",
                    "18"
                  ],
                  [
                    "19",
                    "19"
                  ],
                  [
                    "20",
                    "20"
                  ]
                ]
              }
            ],
            "colour": 180,
            "tooltip": "",
            "helpUrl": ""
        });
    }
};

Blockly.JavaScript['ai_get'] = function(block) {
    var coordinate = block.getFieldValue('axis');
    var dropdown_finger_joint = block.getFieldValue('finger_joint');

    return [`getCoord(\'${coordinate}\',${dropdown_finger_joint})`, Blockly.JavaScript.ORDER_NONE];

    return code;
};



Blockly.Blocks['ai_distance'] = {
    init: function () {
        this.jsonInit({

            "output": "Number",

            "type": "ai_distance",
            "message0": "Distance from joint %1 to %2",
            "args0": [
            {
                "type": "field_dropdown",
                "name": "finger_joint_1",
                "options": [
                  [
                    "0",
                    "0"
                  ],
                  [
                    "1",
                    "1"
                  ],
                  [
                    "2",
                    "2"
                  ],
                  [
                    "3",
                    "3"
                  ],
                  [
                    "4",
                    "4"
                  ],
                  [
                    "5",
                    "5"
                  ],
                  [
                    "6",
                    "6"
                  ],
                  [
                    "7",
                    "7"
                  ],
                  [
                    "8",
                    "8"
                  ],
                  [
                    "9",
                    "9"
                  ],
                  [
                    "10",
                    "10"
                  ],
                  [
                    "11",
                    "11"
                  ],
                  [
                    "12",
                    "12"
                  ],
                  [
                    "13",
                    "13"
                  ],
                  [
                    "14",
                    "14"
                  ],
                  [
                    "15",
                    "15"
                  ],
                  [
                    "16",
                    "16"
                  ],
                  [
                    "17",
                    "17"
                  ],
                  [
                    "18",
                    "18"
                  ],
                  [
                    "19",
                    "19"
                  ],
                  [
                    "20",
                    "20"
                  ]
                ]
              },
            {
                "type": "field_dropdown",
                "name": "finger_joint_2",
                "options": [
                  [
                    "0",
                    "0"
                  ],
                  [
                    "1",
                    "1"
                  ],
                  [
                    "2",
                    "2"
                  ],
                  [
                    "3",
                    "3"
                  ],
                  [
                    "4",
                    "4"
                  ],
                  [
                    "5",
                    "5"
                  ],
                  [
                    "6",
                    "6"
                  ],
                  [
                    "7",
                    "7"
                  ],
                  [
                    "8",
                    "8"
                  ],
                  [
                    "9",
                    "9"
                  ],
                  [
                    "10",
                    "10"
                  ],
                  [
                    "11",
                    "11"
                  ],
                  [
                    "12",
                    "12"
                  ],
                  [
                    "13",
                    "13"
                  ],
                  [
                    "14",
                    "14"
                  ],
                  [
                    "15",
                    "15"
                  ],
                  [
                    "16",
                    "16"
                  ],
                  [
                    "17",
                    "17"
                  ],
                  [
                    "18",
                    "18"
                  ],
                  [
                    "19",
                    "19"
                  ],
                  [
                    "20",
                    "20"
                  ]
                ]
              }

            ],
            "colour": 180,
            "tooltip": "",
            "helpUrl": ""
        });
    }
};

Blockly.JavaScript['ai_distance'] = function(block) {
    var dropdown_finger_joint_1 = block.getFieldValue('finger_joint_1');
    var dropdown_finger_joint_2 = block.getFieldValue('finger_joint_2');

    return [`getDistance(${dropdown_finger_joint_1},${dropdown_finger_joint_2})`, Blockly.JavaScript.ORDER_NONE];

    return code;
};



Blockly.Blocks['ai_gesture_available'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_gesture_available",
            "lastDummyAlign0": "CENTRE",
            "message0": "New Gesture Available?",
            "output": "Boolean",
            "colour": 75,
            "tooltip": "Is a new gesture available?",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_gesture_available'] = function (block) {
    return ['gestureAvailable()', Blockly.JavaScript.ORDER_NONE];
};


Blockly.Blocks['ai_get_gesture'] = {
    init: function () {
        this.jsonInit({
            "type": "ai_get_gesture",
            "lastDummyAlign0": "CENTRE",
            "message0": "Get new gesture",
            "output": "Number",
            "colour": 75,
            "tooltip": "Get the latest gesture",
            "helpUrl": "",
        });
    }
};

Blockly.JavaScript['ai_get_gesture'] = function (block) {
    return ['getGesture()', Blockly.JavaScript.ORDER_NONE];
};





Blockly.Blocks['ai_check_gesture'] = {
    init: function () {
        this.jsonInit({

            "output": "Boolean",

            "type": "ai_check_gesture",
            "message0": "Is Gesture %2 %1",
            "args0": [
              {
                 "type": "field_dropdown",
                 "name": "gesturetype",
                 "options": [
                   [
                     "INDEXFOLDED",
                     "INDEXFOLDED"
                   ],
                   [
                     "MIDDLEFOLDED",
                     "MIDDLEFOLDED"
                   ],
                   [
                     "RINGFOLDED",
                     "RINGFOLDED"
                   ],
                   [
                     "LITTLEFOLDED",
                     "LITTLEFOLDED"
                   ],
                   [
                     "INDEXEXTENDED",
                     "INDEXEXTENDED"
                   ],
                   [
                     "MIDDLEEXTENDED",
                     "MIDDLEEXTENDED"
                   ],
                   [
                     "RINGEXTENDED",
                     "RINGEXTENDED"
                   ],
                   [
                     "LITTLEEXTENDED",
                     "LITTLEEXTENDED"
                   ],
                   [
                     "CLOSED_FIST",
                     "CLOSED_FIST"
                   ],
                   [
                     "VICTORY",
                     "VICTORY"
                   ],
                   [
                     "POINTING_UP",
                     "POINTING_UP"
                   ],
                   [
                     "THUMB_UP",
                     "THUMB_UP"
                   ],
                   [
                     "THUMB_DOWN",
                     "THUMB_DOWN"
                   ],
                   [
                     "OPEN_PALM",
                     "OPEN_PALM"
                   ]
                ]
               },
               {
                  "type": "input_value",
                  "name": "gesture",
                  "check": "Number"
                }

            ],
            "colour": 180,
            "tooltip": "",
            "helpUrl": ""
        });
    }
};

Blockly.JavaScript['ai_check_gesture'] = function(block) {
    var gesture = Blockly.JavaScript.valueToCode(block, 'gesture', Blockly.JavaScript.ORDER_NONE);
    var gesturetype = block.getFieldValue('gesturetype');

    return [`checkGesture(\'${gesturetype}\', ${gesture})`, Blockly.JavaScript.ORDER_NONE];

    return code;
};





//---------GAME

Blockly.Blocks['add_mp_hands'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Add Hand Detector")
        .appendField(new Blockly.FieldDropdown([["FRONT","front"], ["BACK","back"] ]), "CAM");
    this.setColour(135);
 this.setTooltip("Add AI hand detector");
 this.setInputsInline(false);
 this.setPreviousStatement(true, null);
 this.setNextStatement(true, null);
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['add_mp_hands'] = function(block) {
  var cam = block.getFieldValue('CAM');
  var code = 'addMP(\'' + cam +'\');';
  return code;
};


Blockly.Python['add_mp_hands'] = function(block) {
  var cam = block.getFieldValue('CAM');
  var code = 'addMP(\'' + cam +'\')';
  return code;
};


Blockly.Blocks['del_mp_hands'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Stop Hand Detector");
    this.setColour(135);
 this.setTooltip("Stop AI hand detector");
 this.setInputsInline(false);
 this.setPreviousStatement(true, null);
 this.setNextStatement(true, null);
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['del_mp_hands'] = function(block) {
  var code = 'delMP();';
  return code;
};


Blockly.Python['del_mp_hands'] = function(block) {
  var code = 'delMP()\n';
  return code;
};


//-------------------- API ------------------------


function initMP(interpreter, scope) {
	          // kuttypy API CALLS
            interpreter.setProperty(scope, 'addMP', interpreter.createAsyncFunction(
                function(callback) {
                    fetch(`/addMP`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('camera initialized');
                        callback();
                    })
                    .catch(error => {
                        console.error('Error opening camera:', error);
                        callback(0);
                    });
                }
            ));

            interpreter.setProperty(scope, 'delMP', interpreter.createAsyncFunction(
                function(callback) {
                    fetch(`/delMP`)
                    .then(response => response.json())
                    .then(data => {
                        console.log('camera closed');
                        callback();
                    })
                    .catch(error => {
                        console.error('Error closing camera:', error);
                        callback(0);
                    });
                }
            ));

            interpreter.setProperty(scope, 'isHandAvailable', interpreter.createAsyncFunction(
                function(callback) {
                    fetch(`/isHandVisible`)
                    .then(response => response.json())
                    .then(data => {
                        callback(data.response);
                    })
                    .catch(error => {
                        console.error('Error closing camera:', error);
                        callback(0);
                    });
                }
            ));


	          // kuttypy API CALLS
            interpreter.setProperty(scope, 'getDistance', interpreter.createAsyncFunction(
                function(p1,p2, callback) {
                    fetch('/getMPDistance', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            p1: p1,
                            p2: p2
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        callback(data.distance);
                    })
                    .catch(error => {
                        console.error('Error reading landmrks:', error);
                        callback(0);
                    });
                  }
            ));

		  interpreter.setProperty(scope, 'gestureAvailable', interpreter.createNativeFunction(
                                                                  				function() {
                                                                  				  return JSBridge.gestureAvailable();
                                                                  				}));

		  interpreter.setProperty(scope, 'getGesture', interpreter.createNativeFunction(
                                                                  				function() {
                                                                  				  return JSBridge.getGesture();
                                                                  				}));

		  interpreter.setProperty(scope, 'checkGesture', interpreter.createNativeFunction(
                    function(g , v) {
                        //TODO . convert to list access for comparison
                        if(v==0 && g == 'INDEXFOLDED') return true;
                        else if(v==1 && g == 'MIDDLEFOLDED') return true;
                        else if(v==2 && g == 'RINGFOLDED') return true;
                        else if(v==3 && g == 'LITTLEFOLDED') return true;
                        else if(v==4 && g == 'INDEXEXTENDED') return true;
                        else if(v==5 && g == 'MIDDLEXTENDED') return true;
                        else if(v==6 && g == 'RINGEXTENDED') return true;
                        else if(v==7 && g == 'LITTLEEXTENDED') return true;
                        else if(v==8 && g == 'CLOSED_FIST') return true;
                        else if(v==9 && g == 'VICTORY') return true;
                        else if(v==10 && g == 'POINTING_UP') return true;
                        else if(v==11 && g == 'THUMB_UP') return true;
                        else if(v==12 && g == 'THUMB_DOWN') return true;
                        else if(v==13 && g == 'OPEN_PALM') return true;


                        return false;
                    }));







	}



