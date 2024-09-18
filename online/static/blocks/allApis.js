var audioReadyCallback  = ()=>{};

var startRecord = function(callback){
    audioReadyCallback = callback;
    if(typeof JSBridge != 'undefined'){
        if(!JSBridge.isAudioAvailable()){
            console.log('record permission not granted. wait.');
            JSBridge.getAudioPermission();
            return;
            }
    }
    audioReadyCallback();
}



var storageReadyCallback  = ()=>{};

var startStorage = function(callback){
    storageReadyCallback = callback;
    if(typeof JSBridge != 'undefined'){
        if(!JSBridge.isStorageAvailable()){
            console.log('storage permission not granted. wait.');
            JSBridge.getStoragePermission();
            return;
            }
    }
    storageReadyCallback();
}

//Kuttypy.js

var textElements={};
var txt;
// ----------DOM MANIPULATION
const SVG_NS = "http://www.w3.org/2000/svg";
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

// FLOT


var colors = ['red','orange','yellow','olive','green','teal','blue','violet','purple','pink','brown','grey','black'];
var recentcolor=0;

var mydata = {};
var startTime = new Date();
var activePlot=null;
var myplots = {}
var options = {}
var plotdatastack = {};

var clearPlot = function(){
    plotdatastack = {};
	 resultplots.empty();
	 myplots  = {};
	 options = {};
}

function createPlots(latestCode){
            mydata = {}; startTime = new Date();
            if(latestCode.indexOf('plot_radar(')>=0)
              addPolarPlot();
}


var polarPositions = [];

var addPolarPlot = function(){
	polarPositions = [];

	resultplots.append(`
	<div id="polarplot" style="min-width:300px;width:100%;height:100%;position:relative;">
	<!-- Grey circle -->
	 <svg viewBox="0 0 200 200" class="circle" style="position:absolute;">
	     <circle cx="100" cy="100" r="100" fill="#9cb" />
	</svg>

	<!-- Pie -->
	 <svg class="polar" viewBox="-1 -1 2 2" style="transform: rotate(-90deg);position: absolute;">
	</svg>

	<!-- Slice borders -->
	<svg viewBox="0 0 200 200" style="transform: rotate(0deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(60deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(-60deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(30deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(-30deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(90deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>


	<!-- Concentric circles -->
	<svg viewBox="0 0 200 200" class="polar circle" style="position:absolute;">
	    <circle cx="100" cy="100" r="100" fill="none" stroke="white" stroke-width="1"  stroke-opacity=".5" />
	    <circle cx="100" cy="100" r="80" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	    <circle cx="100" cy="100" r="60" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	    <circle cx="100" cy="100" r="40" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	    <circle cx="100" cy="100" r="20" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	</svg>


	</div>
	`);



	plt = document.querySelector('.polar.circle');

	for(var i=0;i<361;i++){
		dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
		dot.setAttribute('cx',100);
		dot.setAttribute('cy',100);
		dot.setAttribute('r',2);
		dot.setAttribute('stroke','lightgreen');
		dot.setAttribute('fill','green');
		polarPositions.push(dot);
		plt.appendChild(dot);
	}

}

var makePlotIfUnavailable = function(plotname){
    if(!(plotname in myplots)){
        mydata[plotname] = [];
        var w = resultplots.width()<300?300:resultplots.width();
        var h = resultplots.height()<300 ? 300:resultplots.height();
        if(h>400)h=400;
        startTime = new Date();
        resultplots.append($('<span style="color:red" onclick="savePlotData(\''+plotname+'\');">'+plotname+' [Touch to Save Data]</span><hr color="red">'));
        resultplots.append($('<div id="cs_'+plotname+'">').width(w).height(h));
        myplots[plotname] = 0;
        options[plotname] = {
                series: {
                    lines: {
                        show: true,
                        lineWidth: 2
                    },
                    points: {
                        radius: 2,
                        show: true,
                        symbol: "cross"
                    }
                },
                xaxis: {
                    gridLines: true,
                    autoScaleMargin : 0.1,
                    autoScale: 'exact',
                    growOnly : true
                },
                yaxis: {
                    gridLines: true,
                    autoScaleMargin : 0.1,
                    autoScale: 'exact',
                    growOnly : true
                },

                legend: {
                    show: true,
                    noColumns: 1,
                    labelFormatter: null, // fn: string -> string
                    container: null, // container (as jQuery object) to put legend in, null means default on top of graph
                    position: 'ne', // position of default legend container within plot
                    margin: 5, // distance from grid edge to default legend container within plot
                    sorted: null // default to no legend sorting
                }
        };

    }
}


var addDataPoint = function(plotname, x){
    makePlotIfUnavailable(plotname);
    if(myplots[plotname]==0){
        	startTime = new Date();
        	mydata[plotname].push([0,x]);
    }else{
        	mydata[plotname].push([(new Date() - startTime)/1000.,x]);
	}
	myplots[plotname] ++;
	//if(myplots[plotname]>20)options[plotname].series.points.show = false;
	//else options[plotname].series.points.show = true;
	options[plotname].series.lines.show = false;

    options[plotname].xaxes = [{ position: 'bottom', axisLabel: 'Time (S)', show: true }];
    $.plot("#cs_"+plotname, [{color: "red", lines: {show: true, lineWidth: 2}, data: mydata[plotname], label: "Y data"}], options[plotname]);
}


var addDataPoints = function(plotname, x){ // X is an Array of points
    x = myInterpreter.pseudoToNative(x); // Convert to native array
    makePlotIfUnavailable(plotname);
    var t=0;
    if(myplots[plotname]==0){
        	startTime = new Date();
        	for(var i=0;i<x.length;i++){
                mydata[plotname].push({ lines: {show: true, lineWidth: 1}, data: [] ,label:'Y'+(i+1) } ); //, label: params[i]
        	}
    }else{
        t = (new Date() - startTime)/1000.;
	}
	// Push points in
	try{
        for(var i=0;i<x.length;i++){
            mydata[plotname][i].data.push([t,x[i]]);
            if(myplots[plotname]==20)mydata[plotname][i].points = {show:false};
        }

        myplots[plotname] ++;
        //if(myplots[plotname]>20)options[plotname].series.points.show = false;
        //else options[plotname].series.points.show = true;
        options[plotname].series.lines.show = false;

        options[plotname].xaxes = [{ position: 'bottom', axisLabel: 'Time (S)', show: true }];
        $.plot("#cs_"+plotname, mydata[plotname], options[plotname]);
    }catch(e){
        console.log('Plot Err:'+e);
    }
}


var addDataPointXY = function(plotname, x,y){
    makePlotIfUnavailable(plotname);
    mydata[plotname].push([x,y]);
	myplots[plotname] ++;
	//if(myplots[plotname]>200)options[plotname].series.points.show = false;
	//else options[plotname].series.points.show = true;
	options[plotname].series.lines.show = false;
    $.plot("#cs_"+plotname, [ mydata[plotname] ], options[plotname]);
}


var plotArraysXYStack = function(plotname,X,Y, state){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    if(!(plotname in plotdatastack))plotdatastack[plotname] = [];

    if(state)plotdatastack[plotname] = [ {color: colors[plotdatastack[plotname].length % colors.length], lines: {show: true, lineWidth: 2}, data: [], label: "Chan "+plotdatastack[plotname].length} ];
    else plotdatastack[plotname].push( {color: colors[plotdatastack[plotname].length % colors.length], lines: {show: true, lineWidth: 2}, data: [], label: "Chan "+plotdatastack[plotname].length} );

    nx = myInterpreter.pseudoToNative(X); // Convert to native array
    ny = myInterpreter.pseudoToNative(Y); // Convert to native array
    //nx = Object.values(X.a)
    //ny = Object.values(Y.a)
    dat = plotdatastack[plotname][plotdatastack[plotname].length - 1];
    for (i=0;i<nx.length;i++){
        dat.data.push([nx[i],ny[i]]);
    }

    $.plot("#cs_"+plotname, plotdatastack[plotname], options[plotname]);

}

var plotArraysXY = function(plotname,X,Y){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    mydata[plotname] = [
        {color: "red", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 1"},
    ];
    nx = Object.values(X.a)
    ny = Object.values(Y.a)
    for (i=0;i<nx.length;i++){
        mydata[plotname][0].data.push([nx[i],ny[i]]);
    }

    $.plot("#cs_"+plotname, mydata[plotname], options[plotname]);

}


var plotArraysXYY = function(plotname, X,Y1, Y2){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    mydata[plotname] = [
        {color: "red", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 1"},
        {color: "blue", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 2"},
    ];

    nx = Object.values(X.a)
    ny1 = Object.values(Y1.a)
    ny2 = Object.values(Y2.a)
    for (i=0;i<nx.length;i++){
        mydata[plotname][0].data.push([nx[i],ny1[i]]);
        mydata[plotname][1].data.push([nx[i],ny2[i]]);
    }

    $.plot("#cs_"+plotname, mydata[plotname] , options[plotname]);

}

var plotArraysXYYY = function(plotname, X,Y1, Y2, Y3){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    mydata[plotname] = [
        {color: "red", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 1"},
        {color: "blue", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 2"},
        {color: "forestgreen", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 3"},
    ];

    nx = Object.values(X.a)
    ny1 = Object.values(Y1.a)
    ny2 = Object.values(Y2.a)
    ny3 = Object.values(Y3.a)
    for (i=0;i<nx.length;i++){
        mydata[plotname][0].data.push([nx[i],ny1[i]]);
        mydata[plotname][1].data.push([nx[i],ny2[i]]);
        mydata[plotname][2].data.push([nx[i],ny3[i]]);
    }

    $.plot("#cs_"+plotname, mydata[plotname] , options[plotname]);

}

var savePlotData = function(plotname){
   if(mydata[plotname].length == 0)return;
   if(mydata[plotname][0].constructor == Array){
       x=[];
       y=[];
       for (var i=0;i<mydata[plotname].length;i++){
           x.push(parseFloat(mydata[plotname][i][0]));
           y.push(parseFloat(mydata[plotname][i][1]));
       }
       JSBridge.save_lists(plotname+".csv",JSON.stringify(x),JSON.stringify(y),"[]","[]");
       alert("Saved to KuttyPy directory :"+plotname+".csv");

   }
   else if(mydata[plotname][0].constructor == Object){ // plot_xyyarray, xyyyarray etc store dicts.
        msg = ''
       for (var dset=0;dset<mydata[plotname].length;dset++){
           x=[];
           y=[];
           for (var i=0;i<mydata[plotname][dset].data.length;i++){
               x.push(parseFloat(mydata[plotname][dset].data[i][0]));
               y.push(parseFloat(mydata[plotname][dset].data[i][1]));
           }
           JSBridge.save_lists(plotname+'_'+dset+'.csv',JSON.stringify(x),JSON.stringify(y),"[]","[]");
           msg+=plotname+'_'+dset+'.csv ,';
        }
         alert("Saved to KuttyPy directory :"+msg);
   }


}

var addDataPointPolar = function(angle, radius, maxrad){
	angle = angle%360;
	x = 100+100*radius*Math.cos(3.1415*angle/180)/maxrad;
	y = 100-100*radius*Math.sin(3.1415*angle/180)/maxrad;
	polarPositions[Math.round(angle)].setAttribute('cx',x)
	polarPositions[Math.round(angle)].setAttribute('cy',y)

}


// GAME



/* --- Credit https://raw.githubusercontent.com/danba340/tiny-flappy-bird/master/index.html --*/

var birdX = score = bestScore = 0;
var birdSize = pipeWidth = topPipeBottomY = 24;
var interval = 40;
var birdY = pipeGap = 200;
var intervalID;

var context;
const bird = new Image();

var blit = function() {
	context.fillStyle = "skyblue";
	context.fillRect(0,0,canvasSize,canvasSize); // Draw sky
	context.drawImage(bird, birdX, birdY, birdSize * (524/374), birdSize); // Draw bird
	context.fillStyle = "green";
	context.fillRect(pipeX, 0, pipeWidth, topPipeBottomY); // Draw top pipe
	context.fillRect(pipeX, topPipeBottomY + pipeGap, pipeWidth, canvasSize); // Draw bottom pipe
	context.fillStyle = "blue";
	context.fillText(score++, 9, 25); // Increase and draw score
	context.fillText(`Best: ${bestScore}`, 9, 50); // Draw best score
}

var updateBird = function() {
	blit();
	pipeX -= 4; // Move pipe
	pipeX < -pipeWidth && // Pipe off screen?
	((pipeX = canvasSize), (topPipeBottomY = pipeGap * Math.random())); // Reset pipe and randomize gap.
	bestScore = bestScore < score ? score : bestScore; // New best score?
	if(((birdY < topPipeBottomY || birdY > topPipeBottomY + pipeGap) && pipeX < birdSize * (524/374)) ){// bird hit the pipe
	      context.fillStyle = "red";
	      context.fillRect(0,0,canvasSize,canvasSize); // Draw RED sky
	      birdY = 200;
	      pipeX = canvasSize;
	      score = 0; // Bird died
	     }
}

var addGame = function(){
	canvasSize = pipeX = resultplots.width()<400?400:resultplots.width();
        resplotarea.show();
	resultplots.append(
	`
	<div style="height: 400px; background: #111; text-align: center;touch-action: manipulation;">
	  <canvas id="c" width="$(pipeX)" height="400"></canvas>
	</div>
	`
	);
	context = c.getContext("2d");


	bird.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAOCAYAAADABlfOAAAA/0lEQVQ4y72TQWrDMBBF38gCqwtvC120YOgFegL3DrlFeppSanqc5iAlPUCgCy+kQOLJJkrkWE4TKBXMRuK/+fojwX8t773b1wzQXHnvn6b0ktt0ggIEe0v9+jU4W84rVBURIYRgnHN6qrcZpt69dxRs2J4cRyAQwX3OnElh+2I5r36NSERQ1dhEc041OkhFFCX12+rqmcgUNIXXbZeNYGAgicBe66JuuwgZzSKC7bGZDNwerp+4jE77RZltaJq1AqOWB+pj+5Odfr8oMc36bJx2KuOc4v4jYJoK/RynJs+b848foEjAD0kEaizfLzdjwfbIkwvno5f8xNzj/7O1A51fZ+BxD7C5AAAAAElFTkSuQmCC";


    //c.onclick = () => (birdDY = 9) ;


    intervalID = setInterval(updateBird, interval)


}


function setBirdY(val){ // 0-1000. scaled to 0-400
	birdY = 400 - val/2.5;
	blit();
}

function stopGame(){
  if(intervalID != null)clearInterval(intervalID);
}

// PIANO



var note, hints;
var audios = {};
var mykeys = {};



var addPiano = function(){

registers.append(`
    <section id="main" style="width:400px;">
      <div class="nowplaying"></div>
	      <div class="keys">
		<div class="key" data-note="C">
		    <span class="hints">C</span>
		</div>
		<div  class="key sharp" data-note="C#">
		    <span class="hints">C#</span>
		</div>
		<div  class="key" data-note="D">
		    <span class="hints">D</span>
		</div>
		<div  class="key sharp" data-note="D#">
		    <span class="hints">D#</span>
		</div>
		<div  class="key" data-note="E">
		    <span class="hints">E</span>
		</div>
		<div  class="key" data-note="F">
		    <span class="hints">F</span>
		</div>
		<div  class="key sharp" data-note="F#">
		    <span class="hints">F#</span>
		</div>
		<div  class="key" data-note="G">
		    <span class="hints">G</span>
		</div>
		<div  class="key sharp" data-note="G#">
		    <span class="hints">G#</span>
		</div>
		<div  class="key" data-note="A">
		    <span class="hints">A</span>
		</div>
		<div  class="key sharp" data-note="A#">
		    <span class="hints">A#</span>
		</div>
		<div  class="key" data-note="B">
		    <span class="hints">B</span>
		</div>
		<div  class="key" data-note="2C">
		    <span class="hints">2C</span>
		</div>
		<div  class="key sharp" data-note="2C#">
		    <span class="hints">2C#</span>
		</div>
		<div  class="key" data-note="2D">
		    <span class="hints">2D</span>
		</div>
		<div  class="key sharp" data-note="2D#">
		    <span class="hints">2D#</span>
		</div>
		<div  class="key" data-note="2E">
		    <span class="hints">2E</span>
		</div>
	      </div>

	      <audio data-note="C" src="sounds/040.wav"></audio>
	      <audio  data-note="C#" src="sounds/041.wav"></audio>
	      <audio  data-note="D" src="sounds/042.wav"></audio>
	      <audio  data-note="D#" src="sounds/043.wav"></audio>
	      <audio  data-note="E" src="sounds/044.wav"></audio>
	      <audio  data-note="F" src="sounds/045.wav"></audio>
	      <audio  data-note="F#" src="sounds/046.wav"></audio>
	      <audio  data-note="G" src="sounds/047.wav"></audio>
	      <audio  data-note="G#" src="sounds/048.wav"></audio>
	      <audio  data-note="A" src="sounds/049.wav"></audio>
	      <audio  data-note="A#" src="sounds/050.wav"></audio>
	      <audio  data-note="B" src="sounds/051.wav"></audio>
	      <audio  data-note="2C" src="sounds/052.wav"></audio>
	      <audio  data-note="2C#" src="sounds/053.wav"></audio>
	      <audio  data-note="2D" src="sounds/054.wav"></audio>
	      <audio  data-note="2D#" src="sounds/055.wav"></audio>
	      <audio  data-note="2E" src="sounds/056.wav"></audio>
      </section>
    `);

    const keys = document.querySelectorAll(".key");
    note = document.querySelector(".nowplaying");

    keys.forEach(key => key.addEventListener("transitionend", removeTransition));
    keys.forEach(key => key.addEventListener("touchstart", clicked));
    for(const x of ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B','2C','2C#','2D','2D#','2E' ]){
        audios[x] = document.querySelector(`audio[data-note="${x}"]`);
        mykeys[x] = document.querySelector(`.key[data-note="${x}"]`);
        }

}


function clicked(e) {
    playPiano(this.getAttribute("data-note"));
	}


function playPiano(notename) {
	  const audio = audios[notename]; // document.querySelector(`audio[data-note="${notename}"]`),
	  key = mykeys[notename];//document.querySelector(`.key[data-note="${notename}"]`);
	  if (!key) return;
	  key.classList.add("playing");
	  note.innerHTML = notename;
	  audio.currentTime = 0;
	  audio.play();
	}


function removeTransition(e) {
	  if (e.propertyName !== "transform") return;
	  this.classList.remove("playing");
	}


var gauges = [];



function addGauge(id){
        gaugearea.append(`
        <div class="item">
                <div id="${id}" class="gauge" style="
                --gauge-bg: #088478;
                --gauge-value:0;
                --gauge-display-value:0;">

                <div class="ticks">
                    <div class="tithe" style="--gauge-tithe-tick:1;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:2;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:3;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:4;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:6;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:7;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:8;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:9;"></div>
                    <div class="min"></div>
                    <div class="mid"></div>
                    <div class="max"></div>
                </div>
                <div class="tick-circle"></div>

                <div class="needle">
                    <div class="needle-head"></div>
                </div>
                <div class="labels">
                    <div class="value-label"></div>
                </div>
            </div>
        </div>`);
        return true;
}
// Gauge
function updateGauge(id, value, min, max) {
    const newGaugeValue = Math.floor(((value - min) / (max - min)) * 100);
    document.getElementById(id).style.setProperty('--gauge-display-value', Math.floor(value));
    document.getElementById(id).style.setProperty('--gauge-value', newGaugeValue);
}


function savePNG(){
    var scaleFactor = 1;
    //Any modifications are executed on a deep copy of the element
    var cp = Blockly.mainWorkspace.svgBlockCanvas_.cloneNode(true);
    cp.removeAttribute("width");
    cp.removeAttribute("height");
    cp.removeAttribute("transform");

    var styleElem = document.createElementNS("http://www.w3.org/2000/svg", "style");
    //I've manually pasted codethemicrobit.com's CSS for blocks in here, but that can be removed as necessary
    styleElem.textContent = ".blocklyToolboxDiv {background: rgba(0, 0, 0, 0.05);}.blocklyMainBackground {stroke:none !important;}.blocklyTreeLabel, .blocklyText, .blocklyHtmlInput {font-family:'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace !important;}.blocklyText { font-size:1rem !important;}.rtl .blocklyText {text-align:right;} .blocklyTreeLabel { font-size:1.25rem !important;} .blocklyCheckbox {fill: #ff3030 !important;text-shadow: 0px 0px 6px #f00;font-size: 17pt !important;}";
    cp.insertBefore(styleElem, cp.firstChild);

    //Creates a complete SVG document with the correct bounds (it is necessary to get the viewbox right, in the case of negative offsets)
    var bbox = Blockly.mainWorkspace.svgBlockCanvas_.getBBox();
    var xml = new XMLSerializer().serializeToString(cp);
    xml = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'+bbox.width+'" height="'+bbox.height+'" viewBox="' + bbox.x + ' ' + bbox.y + ' '  + bbox.width + ' ' + bbox.height + '"><rect width="100%" height="100%" fill="white"></rect>'+xml+'</svg>';
    //If you just want the SVG then do console.log(xml)
    //Otherwise we render as an image and export to PNG
    var svgBase64 = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(xml)));
    var img = document.createElement('img');
    img.src = svgBase64;

    var canvas = document.createElement("canvas");
    canvas.width = Math.ceil(bbox.width) * scaleFactor;
    canvas.height = Math.ceil(bbox.height) * scaleFactor;
    var ctx = canvas.getContext('2d');
    ctx.scale(scaleFactor, scaleFactor);

    ctx.drawImage(img, 0, 0);
    //Opens the PNG image in a new tab for copying/saving
    window.open(canvas.toDataURL(), '_blank');
}


// SENSORS

var I2CSelectionCallback;
function getSensorSelection(callback){
    I2CSelectionCallback = callback;
    var sensors = JSON.parse(HWBridge.scanI2C());
    if(sensors.length>0){
        var senslist = $('<div class="ui mini teal buttons i2clist"></div>');
        sensors.forEach((s, i) => {
              if(i>0) senslist.append('<div class="or"></div>');
              if(s.search('/') != -1){ // 2 sensor options. more than that unsupported.
                  addr = s.split(']')[0].substring(1);
                  sensor1 = s.split(']')[1].split('/')[0];
                  sensor2 = s.split(']')[1].split('/')[1];
                  senslist.append(`<button class="ui button" onclick="var t = this.textContent; this.parentElement.remove(); I2CSelectionCallback(t);">[${addr}]${sensor1}</button>`);
                  senslist.append('<div class="or"></div>');
                  senslist.append(`<button class="ui button" onclick="var t = this.textContent; this.parentElement.remove(); I2CSelectionCallback(t);">[${addr}]${sensor2}</button>`);
              }else{ // only one sensor
                  senslist.append(`<a class="ui button" onclick="var t = this.textContent; this.parentElement.remove(); I2CSelectionCallback(t);">${s}</a>`);
              }


        } );
        results.append(senslist);
    }else{
      results.append('<span>No sensors found. default to voltmeter</span>');
      callback('[0]ADCSENS'); // default to voltmeter
    }
}

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


//-------------------- API ------------------------

//ddone
function initApi(interpreter, scope) {
			/*Patch it
			 * // Desperate attempt at infiltrating the sandbox. Didn't work
		  patchInterpreter(Interpreter);
		  InterfaceDictionary={'get_voltage':'JSBridge.get_voltage'};
		  interpreter.setProperty(scope, 'JSBridge', interpreter.createConnectedObject(JSBridge), interpreter.READONLY_DESCRIPTOR);
		  //interpreter.setProperty(scope,'JSBridge', JSBridge);
		  */


		  // Add an API for the wait block.
		  interpreter.setProperty(scope, 'waitForSeconds', interpreter.createAsyncFunction(
                                                           			function(timeInSeconds, callback) {
                                                           			  // Delay the call to the callback.
                                                           			  setTimeout(callback, timeInSeconds * 1000);
                                                           			}));
		  interpreter.setProperty(scope, 'sleep', interpreter.createAsyncFunction(
                                                  			function(timeInSeconds, callback) {
                                                  			  // Delay the call to the callback.
                                                  			  setTimeout(callback, timeInSeconds * 1000);
                                                  			}));

		  // Add an API function for highlighting blocks.
		  var wrapper = function(id) {
			id = id ? id.toString() : '';
			return interpreter.createPrimitive(highlightBlock(id));
		  };
		  interpreter.setProperty(scope, 'highlightBlock',
			  interpreter.createNativeFunction(wrapper));


		  // Add an API for the console.log call
		  interpreter.setProperty(scope, 'log', interpreter.createNativeFunction(
				function( value) {
				  return console.log(value);
				})
			);

		  // Add an API for the JSON.parse call
		  interpreter.setProperty(scope, 'myparse', interpreter.createNativeFunction(
				function( value) {
				  return JSON.parse(value);
				})
			);



		  // Add APIs for the average analysis calls. pass entire data to native java for processing.
		  interpreter.setProperty(scope, 'average', interpreter.createNativeFunction(
				function(xin) {
				  x = myInterpreter.pseudoToNative(xin);
				  return x.reduce((a, b) => parseInt(a) + parseInt(b), 0) / x.length || 0;
				})
			);
		  interpreter.setProperty(scope, 'sum', interpreter.createNativeFunction(
				function(xin) {
				  x = myInterpreter.pseudoToNative(xin);
				  return x.reduce((a, b) => parseInt(a) + parseInt(b), 0) ;
				})
			);
		  // Add APIs for the program starting block.
		  interpreter.setProperty(scope, 'programStarting', interpreter.createAsyncFunction(
				function(callback) {
    				callback();
				})
			);

		  // Add APIs for the sine fit analysis calls. pass entire data to native java for processing.
		  interpreter.setProperty(scope, 'sine_fit_arrays', interpreter.createAsyncFunction(
				async function(x,y,param, callback) {
				  val = await JSBridge.sine_fit_arrays(JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y.a)),param);
				  callback( val.toFixed(3) );
				})
			);
		  interpreter.setProperty(scope, 'sine_fit_two_arrays', interpreter.createAsyncFunction(
				async function(x,y,x2,y2,param,callback) {
				  val =  await JSBridge.sine_fit_two_arrays(JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y.a)),JSON.stringify(Object.values(x2.a)),JSON.stringify(Object.values(y2.a)),param);
				  callback(val.toFixed(3));
				})
			);
		  // Add an API for the FFT block.  copied from wait_block. Async attempt
		  interpreter.setProperty(scope, 'fourier_transform', interpreter.createAsyncFunction(
				function fourier_transform(x,y,callback) {
                                JSBridge.fourier_transform(JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y.a)),callback);
                		  })
			);


			// File writing calls
		  // Add an API for the writeToFile call
		  interpreter.setProperty(scope, 'write_to_file', interpreter.createAsyncFunction(
				function(fname, txt, newline,callback) {
					if(newline){txt+='\n';}
			        return JSBridge.writeToFile(fname,txt,callback);
				})
			);

		  interpreter.setProperty(scope, 'fileopen', interpreter.createAsyncFunction(
				function(fname, callback) {
			        return JSBridge.fileopen(fname,callback);
				})
			);





	}

//done
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

//done
function initPlots(interpreter, scope) {
			// PLOT CALLS
		  // Add an API for the plot call
		  interpreter.setProperty(scope, 'plot', interpreter.createNativeFunction(
				function(plotname,  value) {
				  return addDataPoint(plotname, value);
				})
			);

		  // Add an API for the plot array call
		  interpreter.setProperty(scope, 'plot_array', interpreter.createNativeFunction(
				function(plotname,  values) {
				  return addDataPoints(plotname, values);
				})
			);



		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_scale', interpreter.createNativeFunction(
				function( plotname, axis, vmin,vmax, scale) {
				    makePlotIfUnavailable(plotname);
				    if(axis === 'x'){options[plotname].xaxis.min = vmin; options[plotname].xaxis.max = vmax; options[plotname].xaxis.autoScale=scale;}
				    else if(axis === 'y'){options[plotname].yaxis.min = vmin; options[plotname].yaxis.max = vmax; options[plotname].yaxis.autoScale=scale;}
				})
			);
		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xy', interpreter.createNativeFunction(
				function(plotname, vx,vy) {
				  return addDataPointXY(plotname, vx,vy);
				})
			);


		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xyarray', interpreter.createNativeFunction(
				function(plotname,  X,Y, state) {
                      if(typeof state == 'undefined')state = false;
                      console.log(state);
    				  return plotArraysXYStack(plotname, X,Y, state);
				})
			);


		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyarray', interpreter.createNativeFunction(
				function( plotname, x,y1, y2) {
				  return plotArraysXYY(plotname, x,y1, y2);
				})
			);

		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyyarray', interpreter.createNativeFunction(
				function( plotname, x,y1, y2, y3) {
				  return plotArraysXYYY(plotname, x,y1, y2, y3);
				})
			);

		  // Add an API for the Polar plot call
		  interpreter.setProperty(scope, 'plot_radar', interpreter.createNativeFunction(
				function( angle,radius, maxrad) {
				  return addDataPointPolar(angle,radius, maxrad);
				})
			);





	}

function initGames(interpreter, scope) {

		  // Add an API for the Add Game call
		  interpreter.setProperty(scope, 'addGame', interpreter.createNativeFunction(
				function() {
				  return addGame();
				})
			);
		  // Add an API for the Add Game call
		  interpreter.setProperty(scope, 'stopGame', interpreter.createNativeFunction(
				function() {
				  return stopGame();
				})
			);
		  // Add an API for the Add Game call
		  interpreter.setProperty(scope, 'setBirdY', interpreter.createNativeFunction(
				function(y) {
				  return setBirdY(y);
				})
			);

		  // Add an API for the Add Piano call
		  interpreter.setProperty(scope, 'addPiano', interpreter.createNativeFunction(
				function() {
				  return addPiano();
				})
			);
		  // Add an API for the Play Music call
		  interpreter.setProperty(scope, 'playPiano', interpreter.createNativeFunction(
				function(mynote) {
				  return playPiano(mynote);
				})
			);

	}

function initIO(interpreter, scope) {
        gauges = [];
        gaugearea.empty();

		  // Add an API function for the (alert) print() block.
		  var wrapper = function(text) {
			return results.html(results.html()+text+"<br>");
			//return document.getElementById("resulttext").innerHTML+=text+"<br>";
		  };
		  interpreter.setProperty(scope, 'alert',
			  interpreter.createNativeFunction(wrapper));
		  interpreter.setProperty(scope, 'print',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the sticker() block.
		  var wrapper = function(label, text) {
			return showReg(label, text);
		  };
		  interpreter.setProperty(scope, 'sticker',
			  interpreter.createNativeFunction(wrapper));


		  // Add an API function for the gauge() block.
		  var wrapper = function(label, val, min, max) {
		    if(!gauges.includes(label) ){
		        addGauge(label, val, min, max);
		        gauges.push(label);
                updateGauge(label, val, min, max);
		    }else{
                updateGauge(label, val, min, max);
			}
		  };
		  interpreter.setProperty(scope, 'setGauge',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the prompt() block.
		  var wrapper = function(text) {
			text = text ? text.toString() : '';
			return interpreter.createPrimitive(prompt(text));
		  };

		  interpreter.setProperty(scope, 'prompt',
			  interpreter.createNativeFunction(wrapper));


	}

function initLists(interpreter, scope) {

		  interpreter.setProperty(scope, 'startStorage', interpreter.createAsyncFunction(
                        function(callback) {
                              startStorage(callback);
                            })
                        );

		  interpreter.setProperty(scope, 'subtract_lists', interpreter.createNativeFunction(
				function(x,y) {
				  c = [];
				  a = Object.values(x.a);
				  b = Object.values(y.a);
				  if(a.length == b.length){
				          for(var i=0;i<a.length;i++)c.push(a[i]-b[i]);
				          return interpreter.nativeToPseudo(c);
    				  }
				})
			);

		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'save_lists', interpreter.createNativeFunction(
				function( fname,x,y1, y2, y3) {
				  return JSBridge.save_lists(fname,JSON.stringify(myInterpreter.pseudoToNative(x)),JSON.stringify(Object.values(y1.a)),JSON.stringify(Object.values(y2.a)),JSON.stringify(Object.values(y3.a)));
				})
			);

		  interpreter.setProperty(scope, 'initTime', interpreter.createNativeFunction(
				function() {
				    return new Date();
				})
			);
		  interpreter.setProperty(scope, 'getTime', interpreter.createNativeFunction(
				function( start_time) {
				  return new Date() - start_time;
				})
			);


	}

function initSounds(interpreter, scope) {
		  // Add an API for the set_voltage call
		  interpreter.setProperty(scope, 'stop_phone_frequency', interpreter.createNativeFunction(
				function() {
				  return JSBridge.stop_phone_frequency();
				})
			);
	  interpreter.setProperty(scope, 'set_phone_frequency', interpreter.createNativeFunction(
				function(val) {
				  return JSBridge.set_phone_frequency(val);
				})
			);

	  interpreter.setProperty(scope, 'set_phone_frequency_stereo', interpreter.createNativeFunction(
				function(val1, val2) {
				  return JSBridge.set_phone_frequency(val1, val2);
				})
			);

	}

//done
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



function initAllApis(interpreter, scope){
  initApi(interpreter, scope);
  initLists(interpreter, scope);
  initIO(interpreter, scope);
  initPlots(interpreter, scope);
  initGames(interpreter, scope);
  initKuttyPy(interpreter, scope);
  initSensors(interpreter, scope);
  initSounds(interpreter, scope);
}


