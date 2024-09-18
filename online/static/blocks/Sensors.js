/*---------- Get Sensor --------------*/
var allsensors = [];

Blockly.Blocks['scanI2C'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Scan I2C port, and get a")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('scanI2C');},'SS'));
    this.appendDummyInput()
        .appendField("list of detected sensors")
    this.setColour(330);
    this.setOutput(true, null);
    this.setTooltip("Scan I2C");
    this.setHelpUrl("");
  },

};


Blockly.JavaScript['scanI2C'] = function(block) {
  var code = 'JSON.parse(scanI2C())';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['scanI2C'] = function(block) {
  var code = 'I2C.scan()';
  return [code,Blockly.Python.ORDER_NONE];
};




Blockly.Blocks['scanI2CString'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Scan I2C port, and get detected")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('scanI2CString');},'SS'));
    this.appendDummyInput()
        .appendField("sensors in a comma separated string")
    this.setColour(330);
    this.setOutput(true, null);
    this.setTooltip("Scan I2C");
    this.setHelpUrl("");
  },

};


Blockly.JavaScript['scanI2CString'] = function(block) {
  var code = 'scanI2CString()';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['scanI2CString'] = function(block) {
  var code = 'I2C.scan()';
  return [code,Blockly.Python.ORDER_NONE];
};



Blockly.Blocks['scanI2Cselector'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Scan and select sensor")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('scanI2Cselector');},'SS'));
    this.setColour(330);
    this.setOutput(true, null);
    this.setTooltip("Scan I2C");
    this.setHelpUrl("");
  },

};


Blockly.JavaScript['scanI2Cselector'] = function(block) {
  var code = 'scanI2Cselector()';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['scanI2Cselector'] = function(block) {
  var code = 'I2C.scan()[0]';
  return [code,Blockly.Python.ORDER_NONE];
};



// Flexible I2C read

Blockly.Blocks['read_I2C_sensor'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read I2C Sensor:")
        .appendField(new Blockly.FieldDropdown([["BMP280","BMP280"],["MS5611","MS5611"],["INA219","INA219"],["ADS1115","ADS1115"], ["HMC5883L","HMC5883L"], ["TCS34725","TCS34725"], ["TSL2561","TSL2561"], ["TSL2591","TSL2591"], ["MAX44009","MAX44009"], ["AHT10","AHT10"], ["QMC5883L","QMC5883L"], ["MPU6050","MPU6050"], ["AK8963","AK8963"],["MAX30100","MAX30100"],["VL53L0X","VL53L0X"]]), "NAME")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_I2C_sensor');},'SS'));
    this.appendDummyInput()
        .appendField("Address:")
        .appendField(new Blockly.FieldNumber(13, 1, 127, 1), "ADDR");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_I2C_sensor'] = function(block) {
  var name = block.getFieldValue('NAME');
  var addr = block.getFieldValue('ADDR');
  var code = 'get_generic_sensor(\''+name+'\','+addr+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_I2C_sensor'] = function(block) {
  var name = block.getFieldValue('NAME');
  var addr = block.getFieldValue('ADDR');
  var code = 'get_generic_sensor(\''+name+'\','+addr+')';
  return [code, Blockly.Python.ORDER_NONE];
};

// Super Flexible I2C read
Blockly.Blocks['read_i2c_sensor_flexible'] = {
  init: function() {
    this.appendValueInput("NAME")
        .setCheck(null)
        .appendField("Read I2C Sensor")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_i2c_sensor_flexible');},'SS'));
    this.appendDummyInput()
        .appendField("Parameter:")
        .appendField(new Blockly.FieldDropdown([["1","0"], ["2","1"], ["3","2"], ["4","3"], ["5","4"]]), "PARAM");
    this.setInputsInline(false);
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_i2c_sensor_flexible'] = function(block) {
  var value_name = Blockly.JavaScript.valueToCode(block, 'NAME', Blockly.JavaScript.ORDER_ATOMIC);
  var dropdown_param = block.getFieldValue('PARAM');
  var code = 'parseAndReadSensor('+value_name+','+dropdown_param+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_i2c_sensor_flexible'] = function(block) {
  var value_name = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC);
  var dropdown_param = block.getFieldValue('PARAM');
  var code = '';
  return [code, Blockly.Python.ORDER_NONE];
};



// Super Duper Flexible  dynamic I2C read
Blockly.Blocks['read_i2c_sensor_flexible_dynamic'] = {

  init: function() {

    this.appendDummyInput()
        .appendField(new Blockly.FieldImage("media/i2cscan.png", 100, 30,  "*", this.scan.bind(this),'SS'))
        .appendField(new Blockly.FieldDropdown(this.generateNameOptions.bind(this),this.validateName.bind(this)), "NAME")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 60, 60),'IMAGE')
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_i2c_sensor_flexible_dynamic');},'SS'));
    this.appendDummyInput()
        .appendField("Parameter")
        .appendField(new Blockly.FieldDropdown(this.generateParameterOptions.bind(this)), 'PARAM');
    this.appendDummyInput()
        .appendField("Configure")
        .appendField(new Blockly.FieldDropdown(this.generateConfigOptions.bind(this),this.validateConfiguration.bind(this)), 'CONFIG')
        .appendField(new Blockly.FieldDropdown(this.generateConfigSettings.bind(this),this.validateSettings.bind(this)), 'SETTING');
    this.setInputsInline(false);
    this.setOutput(true);
    this.setColour(330);
    this.setTooltip("");
    this.setHelpUrl("");
  },

  generateNameOptions: function() {

    //this.parameters=["Scan First"];

    if(typeof(this.availableSensors) === 'undefined'){
        var channels={};
        this.configParams = {};
        this.activeConfigurations = {};

        channels = allsensors;
        console.log('channels',channels);

        this.availableSensors = [];
        for(i=0;i<channels.length;i++){
            this.availableSensors.push(channels[i]);
        }

        if(this.availableSensors.length==0)
            this.currentValue = "No Sensor Found";
        else {
          if(this.availableSensors[0].search('/') != -1){ // 2 sensor options. more than that unsupported.
                this.currentValue = this.availableSensors[0].split('/')[0];
          }else{ // only one sensor
                this.currentValue = this.availableSensors[0];
          }
        }
    }

    ////console.log(this.id+'populate name dropdown:'+this.availableSensors);
    chans=[];
    for(i=0;i<this.availableSensors.length;i++){
      s = this.availableSensors[i];
      if(s.search('/') != -1){ // 2 sensor options. more than that unsupported.
          addr = s.split(']')[0].substring(1);
          sensor1 = s.split(']')[1].split('/')[0];
          sensor2 = s.split(']')[1].split('/')[1];
          chans.push([sensor1,'['+addr+']'+sensor1]);
          chans.push([sensor2,'['+addr+']'+sensor2]);
      }else{ // only one sensor
            var name = (s.search(']') == -1)?s : s.split(']')[1];
            chans.push([name,s]);
      }
    }
    if(chans.length>0)
        return chans;
    else
        return [["No Sensor Found","No Sensor Found"]];
  },

  validateName: function(newValue) {
    this.currentValue = newValue;

    if(!this.currentValue.startsWith("["))return [["",""]];
    var otherVal = this.currentValue;
    if(otherVal.search(']') != -1)otherVal = otherVal.split(']')[1];

    var paramsDropdown = this.getField('PARAM');
    var paropts=[["0","0"]];
    // This fetches the options for the parameters dropdown
    fetch(`/get_sensor_parameters/${otherVal}`)
                .then(response => response.json())
                .then(data => {
                    console.log('params updating with',  this.parameters);
                    this.parameters = data.fields;
                    console.log('now:',  this.parameters);

                    // This regenerates the options for the parameters dropdown
                    console.log('Force an update of the parameters dropdown');
                    paropts = paramsDropdown.getOptions(false);
                    paramsDropdown.doValueUpdate_();
                    paramsDropdown.setValue("0");
                })
                .catch(error => {
                    console.error('Error fetching parameters:', error);
                });

    /*
    var configDropdown = this.getField('CONFIG');

    var opts = configDropdown.getOptions(false); // This regenerates the options for the options dropdown
    configDropdown.setValue(opts[0][1]);
    */

    var image = this.getField('IMAGE');
    //console.log(image);
    //console.log("media/"+newValue.split(']')[1]+".jpeg");
    image.setValue("media/"+newValue.split(']')[1]+".jpeg");

  },

  generateParameterOptions: function() {
    if(typeof(this.currentValue) === 'undefined')return [["",""]];
    // this now refers to the block when it's called on the field dropdown because this was bound in init to the block
    try{
        var channels=this.parameters;
        chans=[];
        for(i=0;i<channels.length;i++){
            chans.push([channels[i],String(i)]);
        }
        return chans;
    }catch(e){
        console.log('couldnot generate parameter options list',e)
        return [["",""]];
    }
  },

  generateConfigOptions: function() {
    if(typeof(this.currentValue) === 'undefined')return [["",""]];
    // this now refers to the block when it's called on the field dropdown because this was bound in init to the block
    if(!this.currentValue.startsWith("["))return [["No Sensor Found","No Sensor Found"]];
    var otherVal = this.currentValue;
    //console.log(otherVal);
    if(otherVal.search(']') != -1)otherVal = otherVal.split(']')[1];
    var params = {};
    //TODO get sensoroptions
    //if(typeof(HWBridge) !== 'undefined'){params = JSON.parse(JSON.parse(HWBridge.getSensorOptions(otherVal)));}
    //else{params = {"TIMING":["1x","16x"]};}
    this.configParams = params;
    //this.activeConfigurations = {};

    console.log('generate configuration options:'+params+','+otherVal);
    chans=[];
    for(key in params){
        if(key.length>1){
            if(!(key in  this.activeConfigurations)) this.activeConfigurations[key]=params[key][0];
            chans.push([key,key]);
        }

    }

    if(chans.length==0){
            chans  = [["",""]];
            try{
                var settingsDropdown = this.getField('SETTING');
                var opts = settingsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
                settingsDropdown.setValue(opts[0][1]);
            }catch(e){}
        } // try block because SETTING is not created for the first run. will be null.
    return chans;
  },

  validateConfiguration: function(newValue) {
    this.currentConfig = newValue;
    var settingsDropdown = this.getField('SETTING');
    var opts = settingsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
    //console.log('settings dropdown to '+opts[0][1]+'|'+opts);
    //settingsDropdown.setValue(opts[0][1]);
    //console.log(this.activeConfigurations[newValue]+' | '+ newValue + ' len:' + opts.length);
    if(!(typeof(this.activeConfigurations[newValue]) == 'undefined'))settingsDropdown.setValue(this.activeConfigurations[newValue]);
  },

  generateConfigSettings: function() {
    if(typeof(this.currentConfig) === 'undefined' || typeof(this.configParams) === 'undefined')return [["",""]];
    if(!(this.currentConfig in this.configParams))return [["",""]];

    chans=[];
    for(i=0;i<this.configParams[this.currentConfig].length;i++){
        chans.push([this.configParams[this.currentConfig][i],this.configParams[this.currentConfig][i]]);
    }
    if(chans.length==0)chans  = [["",""]];
    console.log("Config Settings Generated:"+chans);
    return chans;
  },

  validateSettings:function(value){
      var name = this.getFieldValue('NAME');
      //var conf = this.getFieldValue('CONFIG');
      var conf = this.currentConfig;

      if(typeof(name) === 'undefined' || typeof(conf) === 'undefined')return;
      if(conf in this.configParams){
          //console.log(conf+'is in '+this.configParams);
          if(!this.configParams[conf].includes(value)){
            //console.log(value+'is not in '+this.configParams[conf]);
            return;
          }
          try{
              addr = name.split(']')[0].substring(1);
              sensor = name.split(']')[1].split('/')[0];
              if(sensor === "unsupported")return;
              this.activeConfigurations[conf]=value;
              //if(typeof(HWBridge) !== 'undefined')HWBridge.configure_sensor(sensor,parseInt(addr),conf,value);

          }catch(e){
              //console.log(e);
          }
      }
  },


  scan: function() {
    //console.log('pre scan:'+this.availableSensors);
    var nameDropdown = this.getField('NAME');

    fetch(`/scan_i2c`)
                .then(response => response.json())
                .then(data => {
                    var channels = data.sensors;
                    console.log(data+';'+channels);
                    this.availableSensors = [];
                    for(i=0;i<channels.length;i++){
                        this.availableSensors.push(channels[i]);
                    }
                    var opts = nameDropdown.getOptions(false); // This regenerates the options for the name dropdown
                    nameDropdown.doValueUpdate_();
                    nameDropdown.setValue(opts[0][1]);
                })
                .catch(error => {
                    console.error('Error scanning I2C', error);
                    //callback(0);  // Return 0 if there's an error
                });

  }

};

Blockly.JavaScript['read_i2c_sensor_flexible_dynamic'] = function(block) {
  var value_name = block.getFieldValue('NAME');
  var dropdown_param = block.getFieldValue('PARAM');
  var code = 'parseAndReadSensor(\''+value_name+'\','+dropdown_param+')';
  //console.log(code);
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_i2c_sensor_flexible_dynamic'] = function(block) {
  var value_name = block.getFieldValue('NAME');
  var dropdown_param = block.getFieldValue('PARAM');
  var code = 'p.get_sensor(\''+value_name.split(']')[1].split('/')[0]+'\','+dropdown_param+')';
  return [code, Blockly.Python.ORDER_NONE];
};



// Super Duper Flexible  dynamic I2C read
Blockly.Blocks['read_i2c_sensor_flexible_dynamic_array'] = {

  init: function() {

    this.appendDummyInput()
        .appendField(new Blockly.FieldImage("media/i2cscan.png", 100, 30,  "*", this.scan.bind(this),'SS'))
        .appendField(new Blockly.FieldDropdown(this.generateNameOptions.bind(this),this.validateName.bind(this)), "NAME")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 60, 60),'IMAGE')
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_i2c_sensor_flexible_dynamic_array');},'SS'));
    this.appendDummyInput()
        .appendField("Return All Parameters as an Array",'PARAM')
    this.appendDummyInput()
        .appendField("Configure")
        .appendField(new Blockly.FieldDropdown(this.generateConfigOptions.bind(this),this.validateConfiguration.bind(this)), 'CONFIG')
        .appendField(new Blockly.FieldDropdown(this.generateConfigSettings.bind(this),this.validateSettings.bind(this)), 'SETTING');
    this.setInputsInline(false);
    this.setOutput(true);
    this.setColour(330);
    this.setTooltip("");
    this.setHelpUrl("");
  },

  generateNameOptions: function() {

    this.parameters=["Scan First"];

    if(typeof(this.availableSensors) === 'undefined'){
        var channels={};
        this.configParams = {};
        this.activeConfigurations = {};
        channels = allsensors;
        console.log('channels',channels);

        this.availableSensors = [];
        for(i=0;i<channels.length;i++){
            this.availableSensors.push(channels[i]);
        }

        if(this.availableSensors.length==0)
            this.currentValue = "No Sensor Found";
        else {
          if(this.availableSensors[0].search('/') != -1){ // 2 sensor options. more than that unsupported.
                this.currentValue = this.availableSensors[0].split('/')[0];
          }else{ // only one sensor
                this.currentValue = this.availableSensors[0];
          }
        }
    }

    ////console.log(this.id+'populate name dropdown:'+this.availableSensors);
    chans=[];
    for(i=0;i<this.availableSensors.length;i++){
      s = this.availableSensors[i];
      if(s.search('/') != -1){ // 2 sensor options. more than that unsupported.
          addr = s.split(']')[0].substring(1);
          sensor1 = s.split(']')[1].split('/')[0];
          sensor2 = s.split(']')[1].split('/')[1];
          chans.push([sensor1,'['+addr+']'+sensor1]);
          chans.push([sensor2,'['+addr+']'+sensor2]);
      }else{ // only one sensor
            var name = (s.search(']') == -1)?s : s.split(']')[1];
            chans.push([name,s]);
      }
    }
    if(chans.length>0)
        return chans;
    else
        return [["No Sensor Found","No Sensor Found"]];
  },

  validateName: function(newValue) {
    this.currentValue = newValue;

    if(!this.currentValue.startsWith("["))return [["",""]];
    var otherVal = this.currentValue;
    if(otherVal.search(']') != -1)otherVal = otherVal.split(']')[1];

    var paramsDropdown = this.getField('PARAM');
    var paropts=[["0","0"]];
    // This fetches the options for the parameters dropdown
    HWBridge.getSensorParameters(otherVal,(vals)=>{
        console.log('params updating with',  this.parameters);
        this.parameters = JSON.parse(vals);

        // This regenerates the options for the parameters dropdown
        console.log('Force an update of the parameters dropdown');
        paropts = paramsDropdown.getOptions(false);
        paramsDropdown.doValueUpdate_();
        paramsDropdown.setValue("0");

    })

    /*
    var configDropdown = this.getField('CONFIG');

    var opts = configDropdown.getOptions(false); // This regenerates the options for the options dropdown
    configDropdown.setValue(opts[0][1]);
    */

    var image = this.getField('IMAGE');
    //console.log(image);
    //console.log("media/"+newValue.split(']')[1]+".jpeg");
    image.setValue("media/"+newValue.split(']')[1]+".jpeg");

  },

  generateConfigOptions: function() {
    if(typeof(this.currentValue) === 'undefined')return [["",""]];
    // this now refers to the block when it's called on the field dropdown because this was bound in init to the block
    if(!this.currentValue.startsWith("["))return [["No Sensor Found","No Sensor Found"]];
    var otherVal = this.currentValue;
    //console.log(otherVal);
    if(otherVal.search(']') != -1)otherVal = otherVal.split(']')[1];
    var params = {};
    //TODO get sensoroptions
    //if(typeof(HWBridge) !== 'undefined'){params = JSON.parse(JSON.parse(HWBridge.getSensorOptions(otherVal)));}
    //else{params = {"TIMING":["1x","16x"]};}
    this.configParams = params;
    //this.activeConfigurations = {};

    console.log('generate configuration options:'+params+','+otherVal);
    chans=[];
    for(key in params){
        if(key.length>1){
            if(!(key in  this.activeConfigurations)) this.activeConfigurations[key]=params[key][0];
            chans.push([key,key]);
        }

    }

    if(chans.length==0){
            chans  = [["",""]];
            try{
                var settingsDropdown = this.getField('SETTING');
                var opts = settingsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
                settingsDropdown.setValue(opts[0][1]);
            }catch(e){}
        } // try block because SETTING is not created for the first run. will be null.
    return chans;
  },

  validateConfiguration: function(newValue) {
    this.currentConfig = newValue;
    var settingsDropdown = this.getField('SETTING');
    var opts = settingsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
    //console.log('settings dropdown to '+opts[0][1]+'|'+opts);
    //settingsDropdown.setValue(opts[0][1]);
    //console.log(this.activeConfigurations[newValue]+' | '+ newValue + ' len:' + opts.length);
    if(!(typeof(this.activeConfigurations[newValue]) == 'undefined'))settingsDropdown.setValue(this.activeConfigurations[newValue]);
  },

  generateConfigSettings: function() {
    if(typeof(this.currentConfig) === 'undefined' || typeof(this.configParams) === 'undefined')return [["",""]];
    if(!(this.currentConfig in this.configParams))return [["",""]];

    chans=[];
    for(i=0;i<this.configParams[this.currentConfig].length;i++){
        chans.push([this.configParams[this.currentConfig][i],this.configParams[this.currentConfig][i]]);
    }
    if(chans.length==0)chans  = [["",""]];
    console.log("Config Settings Generated:"+chans);
    return chans;
  },

  validateSettings:function(value){
      var name = this.getFieldValue('NAME');
      //var conf = this.getFieldValue('CONFIG');
      var conf = this.currentConfig;

      if(typeof(name) === 'undefined' || typeof(conf) === 'undefined')return;
      if(conf in this.configParams){
          //console.log(conf+'is in '+this.configParams);
          if(!this.configParams[conf].includes(value)){
            //console.log(value+'is not in '+this.configParams[conf]);
            return;
          }
          try{
              addr = name.split(']')[0].substring(1);
              sensor = name.split(']')[1].split('/')[0];
              if(sensor === "unsupported")return;
              this.activeConfigurations[conf]=value;
              if(typeof(HWBridge) !== 'undefined')HWBridge.configure_sensor(sensor,parseInt(addr),conf,value);
          }catch(e){
              //console.log(e);
          }
      }
  },


  scan: function() {
    //console.log('pre scan:'+this.availableSensors);
    var nameDropdown = this.getField('NAME');

    if(typeof(HWBridge) !== 'undefined'){
        HWBridge.scanI2C((vals)=>{
            var channels = JSON.parse(vals);
            console.log(vals);
            this.availableSensors = [];
            for(i=0;i<channels.length;i++){
                this.availableSensors.push(channels[i]);
            }
            var opts = nameDropdown.getOptions(false); // This regenerates the options for the name dropdown
            nameDropdown.doValueUpdate_();
            nameDropdown.setValue(opts[0][1]);

        });
    }


  }

};

Blockly.JavaScript['read_i2c_sensor_flexible_dynamic_array'] = function(block) {
  var value_name = block.getFieldValue('NAME');
  var code = 'parseAndReadSensorVals(\''+value_name+'\')';
  //console.log(code);
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_i2c_sensor_flexible_dynamic_array'] = function(block) {
  var value_name = block.getFieldValue('NAME');
  var dropdown_param = block.getFieldValue('PARAM');
  var code = 'p.get_sensor(\''+value_name.split(']')[1].split('/')[0]+'\','+dropdown_param+')';
  return [code, Blockly.Python.ORDER_NONE];
};






//---------BMP280

Blockly.Blocks['read_BMP280'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read BMP280")
        .appendField(new Blockly.FieldDropdown([["TEMPERATURE","0"], ["PRESSURE","1"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 30, 30, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_BMP280');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_BMP280'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_BMP280'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};


//---------MS5611

Blockly.Blocks['read_MS5611'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read MS5611")
        .appendField(new Blockly.FieldDropdown([["PRESSURE","0"], ["TEMPERATURE","1"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 30, 30, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_MS5611');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MS5611'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MS5611\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MS5611'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MS5611\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//---------TSL2561

Blockly.Blocks['read_TSL2561'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read TSL2561(lum)")
        .appendField(new Blockly.FieldDropdown([["LUMINOSITY(total)","0"], ["Infrared","1"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_TSL2561');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_TSL2561'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TSL2561\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_TSL2561'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'TSL2561\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//---------TSL2591

Blockly.Blocks['read_TSL2591'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read TSL2591(lum)")
        .appendField(new Blockly.FieldDropdown([["Raw","0"], ["Luminosity(Vis)","1"], ["Luminosity(IR)","2"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_TSL2591'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TSL2591\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_TSL2591'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'TSL2591\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//---------MAX30100

Blockly.Blocks['read_MAX30100'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read MAX30100")
        .appendField(new Blockly.FieldDropdown([["RED LED","0"], ["IR LED","1"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/pulse.png", 30, 30, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_MAX30100');},'SS'));
    this.appendDummyInput()
        .appendField("Heart Rate");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MAX30100'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MAX30100\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MAX30100'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MAX30100\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};


//---------MAX30100

Blockly.Blocks['read_MAX6675'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read Temperature from")
        .appendField(new Blockly.FieldImage("media/THERMOMETER.png", 30, 30))
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_MAX6675');},'SS'));
    this.appendDummyInput()
        .appendField("MAX6675 Module on")
        .appendField(new Blockly.FieldDropdown([["CS1","1"], ["CS2","2"], ["CS3","3"], ["CS4","4"]]), "CHANNEL")
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MAX6675'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'MAX6675('+dropdown_channel+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MAX6675'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'read_MAX6675('+dropdown_channel+')';
  return [code, Blockly.Python.ORDER_NONE];
};


//----------------MPU6050

Blockly.Blocks['read_MPU6050'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read MPU6050")
        .appendField(new Blockly.FieldDropdown([["Ax","0"], ["Ay","1"], ["Az","2"], ["Gx","4"], ["Gy","5"], ["Gz","6"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/MPU6050.png", 20, 20, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_MPU6050');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MPU6050'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MPU6050'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------VL53L0X

Blockly.Blocks['read_VL53L0X'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read VL53L0X")
        .appendField(new Blockly.FieldDropdown([["Distance(mm)","0"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_VL53L0X');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_VL53L0X'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'VL53L0X\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_VL53L0X'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'VL53L0X\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

//----------------ML8511

Blockly.Blocks['read_ML8511'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read ML8511")
        .appendField(new Blockly.FieldDropdown([["UV Light mW/cm^2","0"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_ML8511');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_ML8511'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ML8511'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};



//----------------TCS34725

Blockly.Blocks['read_TCS34725'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read TCS34725(RGB)")
        .appendField(new Blockly.FieldDropdown([["Luminance","0"],["InfraRed","1"],["Red","2"], ["Green","3"], ["Blue","4"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_TCS34725'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TCS34725\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_TCS34725'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TCS34725\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------INA219

Blockly.Blocks['read_INA219'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read INA219")
        .appendField(new Blockly.FieldDropdown([["Current","0"], ["Shunt Voltage","1"], ["Bus Voltage","2"], ["Power","3"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_INA219'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'INA219\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_INA219'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'INA219\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};
//----------------ADS1115

Blockly.Blocks['read_ADS1115'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read ADS1115 (+/-0.25V)")
        .appendField(new Blockly.FieldDropdown([["Voltage","0"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_ADS1115'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'ADS1115\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ADS1115'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'ADS1115\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};
//----------------HMC5883L

Blockly.Blocks['read_HMC5883L'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read HMC5883L")
        .appendField(new Blockly.FieldImage("media/MAGNETOMETER.png", 20, 20, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldDropdown([["Hx","0"], ["Hy","1"], ["Hz","2"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_HMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_HMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------QMC5883L

Blockly.Blocks['read_QMC5883L'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read QMC5883L")
        .appendField(new Blockly.FieldImage("media/MAGNETOMETER.png", 20, 20, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldDropdown([["Hx","0"], ["Hy","1"], ["Hz","2"], ["Abs","3"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_QMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'QMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_QMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'QMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};
/*---------------------- SET PCA9685 for Servo Motors---------------*/


Blockly.Blocks['set_PCA9685'] = {
  init: function() {
    this.appendValueInput("ANGLE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SERVO(PCA9685) ")
        .appendField(new Blockly.FieldDropdown([["1 Angle","1"], ["2 Angle","2"], ["3 Angle","3"], ["4 Angle","4"], ["5 Angle","5"], ["6 Angle","6"]]), "CHANNEL");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set Angle on servo motor via PCA9685 module");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_PCA9685'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_PCA9685(\''+dropdown_channel+'\',' + value_angle+  ');\n';
  return code;
};


Blockly.Python['set_PCA9685'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.Python.ORDER_NONE);
  var code = 'set_PCA9685(\''+dropdown_channel+'\',' + value_angle+  ')\n';

  return code;
};

// AD9833 Sine Wave generator module

Blockly.Blocks['set_AD9833'] = {
  init: function() {
    this.appendValueInput("FREQ")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Set AD9833  ")
        .appendField(new Blockly.FieldDropdown([["CS1","1"], ["CS2","2"]]), "CHANNEL")
        .appendField("Frequency ");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set dual AD9833 module frequency");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_AD9833'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var freq = Blockly.JavaScript.valueToCode(block, 'FREQ', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_dual_AD9833('+dropdown_channel+',' + freq+  ');\n';
  return code;
};


Blockly.Python['set_AD9833'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var freq = Blockly.JavaScript.valueToCode(block, 'FREQ', Blockly.Python.ORDER_NONE);
  var code = 'set_dual_AD9833('+dropdown_channel+',' + freq+  ')\n';

  return code;
};


Blockly.Blocks['ws2812_rgb'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("WS2812 Controller")
    this.appendDummyInput()
        .appendField("CE 6250 IP:")
        .appendField(new Blockly.FieldTextInput("http://44.44.44.44"), "IP")
        .setAlign(Blockly.ALIGN_RIGHT);
    this.appendValueInput("R")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("RED:");
    this.appendValueInput("G")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("GREEN:");
    this.appendValueInput("B")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("BLUE:");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("set R G B");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['ws2812_rgb'] = function(block) {
  var ip = block.getFieldValue('IP');
  var R = Blockly.JavaScript.valueToCode(block, 'R', Blockly.JavaScript.ORDER_NONE);
  var G = Blockly.JavaScript.valueToCode(block, 'G', Blockly.JavaScript.ORDER_NONE);
  var B = Blockly.JavaScript.valueToCode(block, 'B', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var code = 'sleep(0.001);\n'+'ws2812_rgb(\''+ip+'\','+R+','+G+','+B+');\n';
  console.log(code);

  return code;
};


Blockly.Python['ws2812_rgb'] = function(block) {
  var code = '#unimplemented\n';
  return code;
};





//-------------------- API ------------------------
function getSensorList(){
            fetch(`/get_reg/${channel}`)
            .then(response => response.json())
            .then(data => {
                console.log('got following sensors',data);
                allsensors = JSON.parse(data.sensors);
            })
            .catch(error => {
                console.error('Error fetching sensors:', error);
            });



}



//analogph meter

Blockly.Blocks['read_ph_meter'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Analog pH Meter")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"]]), "CHANNEL");
    this.appendDummyInput()
        .appendField("Slope: ")
        .appendField(new Blockly.FieldNumber(0), "SLOPE");
    this.appendDummyInput()
        .appendField("Offset: ")
        .appendField(new Blockly.FieldNumber(0), "OFFSET");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};
Blockly.JavaScript['read_ph_meter'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var slope = Number(block.getFieldValue('SLOPE'));
  var offset = Number(block.getFieldValue('OFFSET'));
  var code = slope+"*get_voltage('"+dropdown_channel+"')+"+offset;
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ph_meter'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var slope = Number(block.getFieldValue('SLOPE'));
  var offset = Number(block.getFieldValue('OFFSET'));
  var code = slope+"*get_voltage('"+dropdown_channel+"')+"+offset;
  return [code, Blockly.Python.ORDER_NONE];
};

function initSensors(interpreter, scope) {

            fetch(`/get_all_sensors`)
                .then(response => response.json())
                .then(data => {
                    allsensors = data.sensors;
                })
                .catch(error => {
                    console.error('Error getting sensor list:', error);
                    allsensors = ["[129]ADCSENS"];
                });


            // Add an API for the get_sensor call
            interpreter.setProperty(scope, 'get_sensor', interpreter.createAsyncFunction(
                function(sensor, param, callback) {
                    fetch(`/get_sensor/${sensor}/${param}`)
                        .then(response => response.json())
                        .then(data => {
                            callback(myInterpreter.nativeToPseudo(data.value)); // Assuming the value is returned as 'value'
                        })
                        .catch(error => {
                            console.error('Error getting sensor value:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );

            // Add an API for the get_generic_sensor call
            interpreter.setProperty(scope, 'get_generic_sensor', interpreter.createAsyncFunction(
                function(sensor, addr, callback) {
                    fetch(`/get_generic_sensor/${sensor}/${addr}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log(data);
                            callback(myInterpreter.nativeToPseudo(data.data)); // Adjust based on the response format
                        })
                        .catch(error => {
                            console.error('Error getting generic sensor:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );

            // Add an API for the parseAndReadSensor call
            interpreter.setProperty(scope, 'parseAndReadSensor', interpreter.createAsyncFunction(
                function(descriptor, param, callback) {
                    const addr = descriptor.split(']')[0].substring(1);
                    const sensor = descriptor.split(']')[1].split('/')[0];
                    fetch(`/get_generic_sensor/${sensor}/${parseInt(addr)}`)
                        .then(response => response.json())
                        .then(data => {
                            callback(myInterpreter.nativeToPseudo(data.data[param])); // Adjust based on the response format
                        })
                        .catch(error => {
                            console.error('Error parsing and reading sensor:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );

            // Add an API for the parseAndReadSensorVals call
            interpreter.setProperty(scope, 'parseAndReadSensorVals', interpreter.createAsyncFunction(
                function(descriptor, param, callback) {
                    const addr = descriptor.split(']')[0].substring(1);
                    const sensor = descriptor.split(']')[1].split('/')[0];
                    fetch(`/get_generic_sensor/${sensor}/${parseInt(addr)}`)
                        .then(response => response.json())
                        .then(data => {
                            callback(myInterpreter.nativeToPseudo(data.data)); // Adjust based on the response format
                        })
                        .catch(error => {
                            console.error('Error parsing and reading sensor values:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );

            // Add an API for the get_generic_sensor_param call
            interpreter.setProperty(scope, 'get_generic_sensor_param', interpreter.createAsyncFunction(
                function(sensor, addr, param, callback) {
                    fetch(`/get_generic_sensor_param/${sensor}/${addr}/${param}`)
                        .then(response => response.json())
                        .then(data => {
                            callback(myInterpreter.nativeToPseudo(data)); // Adjust based on the response format
                        })
                        .catch(error => {
                            console.error('Error getting generic sensor parameter:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );

            // Add an API for the scanI2C call
            interpreter.setProperty(scope, 'scanI2C', interpreter.createAsyncFunction(
                function(callback) {
                    fetch('/scanI2C')
                        .then(response => response.json())
                        .then(data => {
                            callback(myInterpreter.nativeToPseudo(data)); // Adjust based on the response format
                        })
                        .catch(error => {
                            console.error('Error scanning I2C:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );

            // Add an API for the scanI2CString call
            interpreter.setProperty(scope, 'scanI2CString', interpreter.createAsyncFunction(
                function(callback) {
                    fetch('/scanI2CString')
                        .then(response => response.json())
                        .then(data => {
                            callback(myInterpreter.nativeToPseudo(data)); // Adjust based on the response format
                        })
                        .catch(error => {
                            console.error('Error scanning I2C string:', error);
                            callback(null); // Call callback with null on error
                        });
                })
            );



		  //WiFi RGB Controller
		  interpreter.setProperty(scope, 'ws2812_rgb', interpreter.createNativeFunction(
				function( ip,R,G, B) {
				  var packet ={ "body": JSON.stringify({"seg":{ "col":[[parseInt(R),parseInt(G),parseInt(B),"0"],[],[]],"pal":0}}) , "method": "POST", "mode": "cors" } ;
				  fetch(ip+"/json/si", packet);
				})
			);

	}


