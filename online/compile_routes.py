from flask import Blueprint, render_template, request, session, send_from_directory, current_app
import os, tempfile, subprocess, json, glob
from PyQt5 import QtCore

main = Blueprint('main', __name__)

showStatusSignal = None
kpyPath = 'kpy'
local_ip = 'localhost'


def setStatusSignal(sig):
	global showStatusSignal
	showStatusSignal = sig


def setKpyPath(pth, ip):
	global kpyPath, local_ip
	kpyPath = pth
	local_ip = ip


def is_c(code):
	assembly_keywords = ['mov', 'add', 'sub', 'jmp', 'ret', 'LDI', 'STS', 'SUB', 'LDS', 'main:', 'loop:', '.section',
	                     '.text']
	c_keywords = ['int', 'char', 'float', 'double', 'void', 'if', 'else', 'for', 'while', 'return']

	assembly_count = sum(keyword in code for keyword in assembly_keywords)
	c_count = sum(keyword in code for keyword in c_keywords)

	if assembly_count > c_count:
		return False
	elif c_count > assembly_count:
		return True


@main.route('/')
def index():
	return render_template('index.html')


@main.route('/favicon.ico')
def favicon():
	print(current_app.root_path)
	return send_from_directory(os.path.join(current_app.root_path,'static'), 'logo.png', mimetype='image/png')


@main.route('/compile', methods=['GET', 'POST'])
def mycompiler():
	global showStatusSignal, kpyPath
	try:
		print('compile...')
		extension = '.S'
		processor = 'atmega32'
		if 'processor' in request.form:
			processor = request.form.get('processor')
			print('processor specified', processor)

		if is_c(request.form.get('code')):
			extension = '.c'
		tfile = tempfile.NamedTemporaryFile(mode='w+', dir=kpyPath, suffix=extension)
		tfile.write(request.form.get('code'))
		tfile.flush()

		name = tfile.name.replace(extension, '')
		cmd = 'avr-gcc -Wall -O2 -mmcu=%s -o "%s" "%s%s"' % (processor, name, name, extension)
		res = subprocess.getstatusoutput(cmd)
		showStatusSignal.emit(f'Compiler Active at {local_ip},   Client: {str(request.remote_addr)}', False)
		if (res[0] == 1):  # Error
			return {'status': False, 'msg': 'compile error: ' + res[1], 'raw': request.form.get('code')}

		cmd = 'avr-objcopy -j .text -j .data -O ihex "%s" "%s.hex"' % (name, name)
		res2 = subprocess.getstatusoutput(cmd)
		if (res2[0] == 1):  # Error
			return {'status': False, 'hex': '', 'msg': 'objcopy error: ' + res2[1]}

		hexfile = open(name + '.hex', 'r')
		hx = hexfile.read()

		# Cleanup
		full_pattern = os.path.join(kpyPath, name + "*")
		matching_files = glob.glob(full_pattern)
		# Delete each matching file tmp file.
		for file_path in matching_files:
			if not file_path.endswith(extension):
				try:
					os.remove(file_path)
				# print(f"Deleted: {file_path}")
				except Exception as e:
					print(f"Error deleting {file_path}: {e}")

		return {'status': True, 'hex': json.dumps(hx)}
	except Exception as e:
		return {'status': False, 'msg': 'error: ' + str(e)}
