from flask import Blueprint, render_template, request, session, send_from_directory, current_app, jsonify
import os, tempfile, subprocess, json, glob
from PyQt5 import QtCore

bly = Blueprint('blockly', __name__)

showStatusSignal = None
kpyPath = 'kpy'
blockly_ip = ''
blocklyPath = ''

p = None
def setBlocklyPath(pth, ip):
    global blocklyPath, local_ip
    blocklyPath = pth
    print('blockly at',pth)
    blockly_ip = ip

def setP(dev):
    global p
    p = dev

@bly.route('/visual')
def index():
    return render_template('visual.html')

@bly.route('/editor')
def javaeditor():
    return render_template('editor.html')


@bly.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'logo.png', mimetype='image/png')

@bly.route('/loadxml', methods=['GET'])
def load_xml():
    file = request.args.get('file')
    # Do something with the file (e.g., load it, process it, etc.)
    # For now, return a dummy response
    print(file, blocklyPath)
    f =  open(os.path.join(blocklyPath,'samples',file+'.xml')).read()
    return jsonify({'status': 'success', 'message': f'Loaded {file}','xml':f})


@bly.route('/get_voltage/<int:chan>', methods=['GET'])
def get_voltage(chan):
    print('get_voltage',chan)
    return jsonify({'voltage': p.readADC(chan)})

@bly.route('/set_reg', methods=['POST'])
def set_reg():
    reg = request.json['reg']  # Get the 'reg' parameter from the JSON body
    data = request.json['data']  # Get the 'data' parameter from the JSON body
    p.setReg(reg, int(data%255)&0xFF)
    return jsonify({'status': 'success'})

@bly.route('/get_reg/<string:reg>', methods=['GET'])
def get_reg(reg):
    result = p.getReg(reg)
    return jsonify({'data': result})


@bly.route('/get_device_status', methods=['GET'])
def get_device_status():
    if p is not None:
        return jsonify({'connected': p.connected})
    else:
        return jsonify({'connected': False})

@bly.route('/get_sensor/<string:sensor>/<string:param>', methods=['GET'])
def get_sensor(sensor, param):
    result = p.get_sensor(sensor, int(param))
    return jsonify({'value': result})

@bly.route('/stepper_move', methods=['POST'])
def stepper_move():
    data = request.json
    steps = data['steps']
    dir = data['dir']
    delay = data['delay']
    p.stepper_move(steps, dir, delay)
    return jsonify({'status': 'success'})

@bly.route('/get_all_sensors', methods=['GET'])
def get_all_sensors():
    sensors = []
    if p is not None:
        for addr in p.addressmap:
            sensors.append(f'[{addr}]{p.addressmap[addr]}')
    print('getAllSensors', p.addressmap, sensors)
    return jsonify({'sensors': sensors})

@bly.route('/scan_i2c', methods=['GET'])
def scan_i2c():
    global p
    sensors = []
    p.active_sensors = {}  # Empty sensors list
    x = p.I2CScan()
    print('Responses from:', x)
    for a in x:
        possiblesensors = p.sensormap.get(a, [])
        for sens in possiblesensors:
            s = p.namedsensors.get(sens)
            sensors.append(f'[{a}]{s["name"].split(" ")[0]}')
    print('found', sensors)
    return jsonify({'sensors': sensors})


@bly.route('/get_sensor_parameters/<string:name>', methods=['GET'])
def get_sensor_parameters(name):
    print('found sensor params for', name, p.namedsensors)
    if name in p.namedsensors:
        return jsonify({'fields': p.namedsensors[name]["fields"]})
    else:
        return jsonify({'fields': ['0']})


@bly.route('/get_generic_sensor/<string:name>/<int:addr>', methods=['GET'])
def get_generic_sensor(name, addr):
    if name not in p.active_sensors:
        p.active_sensors[name] = p.namedsensors[name]
        p.namedsensors[name]['init'](address=addr)
    vals = p.active_sensors[name]['read']()
    #print(vals, type(vals))
    if vals is not None:
        return jsonify({'data': [float(a) for a in vals]})
    else:
        return jsonify({'data': None})
