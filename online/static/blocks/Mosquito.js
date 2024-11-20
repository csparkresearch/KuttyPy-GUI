

var serverTitle= null;
var client = null;
subscriptionTitles = {};
subscriptionMessages = {};





const mqtturl = 'ws://iot.expeyes.in:9001/';
var mqttoptions = {
  // Clean session
  clean: true,
  connectTimeout: 2000,
  // Authentication
  clientId: 'emqx_test',
  username: '',
  password: '',
}

function connectToCloud(name,callback){
    mqttoptions.clientId = name;
    myname = name;

    client  = mqtt.connect(mqtturl, mqttoptions);
    console.log(client);
    client.on('connect', function () {
      console.log('Connected')
      // Subscribe to a topic
      client.subscribe('test', function (err) {
        if (!err) {
            serverTitle.setValue("Connected to IoT!");
           //client.publish('test', 'Hello mqtt')
        }else{
            serverTitle.setValue("Failed to Connect IoT!")
            console.log('failed to connect to server');
        }
      });

        // Log all messages received on subscribed channels
      client.on('message', (channel, message) => {
          //console.log(`Message received on ${channel}: ${message.toString()}`);
          if(subscriptionMessages.hasOwnProperty(channel)){ // topic has been subscribed to.
                subscriptionMessages[channel].push(JSON.parse(message));
                //subscriptionTitles[channel].setValue(`Subscribed to ${channel} <span color="red">[${subscriptionMessages[channel].length}]</span>`);
                subscriptionTitles[channel].fieldGroup_.setHTMLUnsafe(`<text fill="red" font-size="11" x=-5 y=10>[${subscriptionMessages[channel].length}]</text><text class="blocklyText" x=15 y=20>Subscribed To : ${channel}</text>`);
          }
      });

      callback();


    });
}


function mqttPublish(channel, data){
    client.publish(channel,data, {qos:2});
}

function mqttSubscribe(channel, callback){
      // Subscribe to a topic
      console.log('subscribe to : ',channel);
      client.subscribe(channel, function (err) {
        if (!err) {
              console.log('subscribe successful: '+channel);
              console.log(subscriptionTitles);
            subscriptionTitles[channel].setValue("Subscribed to "+channel)
            subscriptionMessages[channel] = [];
        }else{
              console.log('subscribe failed: ',channel);
            subscriptionTitles[channel].setValue("Subscription failed")
            delete subscriptionMessages[channel];
        }
        callback();
      }, {qos: 2});
}

function mqttHasData(channel){
    if(subscriptionMessages.hasOwnProperty(channel))
        return subscriptionMessages[channel].length;
    else
        return 0
}
function mqttFetchData(channel){
    if(subscriptionMessages.hasOwnProperty(channel))
        return subscriptionMessages[channel].pop();
    else
        return 0
}


function stopMQTT(){
            if(serverTitle != null)
                serverTitle.setValue("Connect to IOT Server");
             if(client != null){
                 for( let a in subscriptionTitles){
                     console.log('unsub:',a);
                     client.unsubscribe(a);
                 }
                client.end();
                }
            subscriptionTitles = {};
            subscriptionMessages = {};

}


//---------MQTT

Blockly.Blocks['mqtt_connect'] = {
  init: function() {
    this.appendDummyInput("TITLE")
        .appendField("Connect IOT Server")
        .appendField(new Blockly.FieldImage("media/remote.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));
    this.appendDummyInput()
        .appendField("Your Name:")
        .appendField(new Blockly.FieldTextInput(""), "NAME");

    this.setColour(230);
    this.setTooltip("Connect to IoT");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setHelpUrl("");
  }
};

Blockly.JavaScript['mqtt_connect'] = function(block) {
  var name  = block.getFieldValue('NAME');
  serverTitle = this.inputList[0].fieldRow[0];
  console.log(this);
  var code = 'mqttConnect(\'' + name + '\');\n';
  return code;
};


Blockly.Python['mqtt_connect'] = function(block) {
  var code = 'mqttConnect()\n';
  return code;
};






Blockly.Blocks['mqtt_publish'] = {
  init: function() {
    this.appendValueInput("CHANNEL")
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("MQTT Channel Name: ");
    this.appendValueInput("DATA")
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("Transmit: ");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Send Data");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['mqtt_publish'] = function(block) {
  var channel = Blockly.JavaScript.valueToCode(block, 'CHANNEL', Blockly.JavaScript.ORDER_NONE);
  var data = Blockly.JavaScript.valueToCode(block, 'DATA', Blockly.JavaScript.ORDER_NONE);
  var code = 'mqttPublish(' + channel + ','  + data +  ');\n';
  return code;
};

Blockly.Python['mqtt_publish'] = function(block) {
  var code = '\n';
  return code;
};





Blockly.Blocks['mqtt_subscribe'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Subscribe To Channel")
    this.appendDummyInput()
        .appendField("Channel Name:")
        .appendField(new Blockly.FieldTextInput("TEST"), "CHANNEL");

    this.setColour(230);
    this.setTooltip("Subscribe to IoT Channel");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setHelpUrl("");
  }
};

Blockly.JavaScript['mqtt_subscribe'] = function(block) {
  var chan  = block.getFieldValue('CHANNEL');
  subscriptionTitles[chan] = this.inputList[0].fieldRow[0];
  console.log(subscriptionTitles);
  console.log(chan);
  var code = 'mqttSubscribe(\'' + chan + '\');\n';
  return code;
};


Blockly.Python['mqtt_subscribe'] = function(block) {
  var code = 'mqttSubscribe()\n';
  return code;
};



Blockly.Blocks['mqtt_hasdata'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("IoT Channel:")
        .appendField(new Blockly.FieldTextInput("TEST"), "CHANNEL");
    this.appendDummyInput()
        .appendField("Has Data?")
        .appendField(new Blockly.FieldImage("media/mail.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));

    this.setOutput(true, null);
    this.setColour(230);
    this.setTooltip("check if data is available to read from IoT Channel");
    this.setHelpUrl("");
  }
};

Blockly.JavaScript['mqtt_hasdata'] = function(block) {
  var chan  = block.getFieldValue('CHANNEL');
  var code = 'mqttHasData(\'' + chan + '\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['mqtt_hasdata'] = function(block) {
  var chan  = block.getFieldValue('CHANNEL');
  var code = 'mqttHasData(\'' + chan + '\')';
  return [code, Blockly.Python.ORDER_NONE];
};


Blockly.Blocks['mqtt_fetchdata'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("IoT Channel:")
        .appendField(new Blockly.FieldTextInput("TEST"), "CHANNEL");
    this.appendDummyInput()
        .appendField("Latest Data")

    this.setOutput(true, null);
    this.setColour(230);
    this.setTooltip("check if data is available to read from IoT Channel");
    this.setHelpUrl("");
  }
};

Blockly.JavaScript['mqtt_fetchdata'] = function(block) {
  var chan  = block.getFieldValue('CHANNEL');
  var code = 'mqttFetchData(\'' + chan + '\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['mqtt_fetchdata'] = function(block) {
  var chan  = block.getFieldValue('CHANNEL');
  var code = 'mqttFetchData(\'' + chan + '\')';
  return [code, Blockly.Python.ORDER_NONE];
};




Blockly.Blocks['mqtt_json'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Parse JSON Objects")
    this.appendValueInput("RAWDATA")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("JSON Object:");
    this.appendValueInput("PARAMETER")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Variable Name:");
    this.setOutput(true, null);
    this.setInputsInline(false);
    this.setColour(230);
 this.setTooltip("Send Data");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['mqtt_json'] = function(block) {
  var rawdata = Blockly.JavaScript.valueToCode(block, 'RAWDATA', Blockly.JavaScript.ORDER_NONE);
  var parameter = Blockly.JavaScript.valueToCode(block, 'PARAMETER', Blockly.JavaScript.ORDER_NONE);
  var code = 'mqttParseJson(' + rawdata + ',' + parameter+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['mqtt_json'] = function(block) {
  var rawdata = Blockly.Python.valueToCode(block, 'RAWDATA', Blockly.Python.ORDER_NONE);
  var parameter = Blockly.Python.valueToCode(block, 'PARAMETER', Blockly.Python.ORDER_NONE);
  return [rawdata[parameter], Blockly.Python.ORDER_NONE];
};



//-------------------- API ------------------------

function initMQTT(interpreter, scope) {

            interpreter.setProperty(scope, 'mqttConnect', interpreter.createAsyncFunction(
                function(name,callback) {
                    serverTitle.setValue("Connecting...")
                    connectToCloud(name,callback);
                }
            ));

            interpreter.setProperty(scope, 'mqttPublish', interpreter.createNativeFunction(
                function(channel,data) {
                    mqttPublish(channel,JSON.stringify(data));
                }
            ));

            interpreter.setProperty(scope, 'mqttSubscribe', interpreter.createAsyncFunction(
                function(channel, callback) {
                    mqttSubscribe(channel, callback);
                }
            ));

            interpreter.setProperty(scope, 'mqttHasData', interpreter.createNativeFunction(
                function(channel,) {
                    return mqttHasData(channel);
                }
            ));

            interpreter.setProperty(scope, 'mqttFetchData', interpreter.createNativeFunction(
                function(channel) {
                    return mqttFetchData(channel);
                }
            ));
            interpreter.setProperty(scope, 'mqttParseJson', interpreter.createNativeFunction(
                function(rawdata,parameter) {
                    return rawdata[parameter];
                }
            ));


	}



