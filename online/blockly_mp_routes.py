from typing import List

from flask import Blueprint, render_template, request, session, send_from_directory, current_app, jsonify
import os, tempfile, subprocess, json, glob
from PyQt5 import QtCore

from online.mp import HandTrackingDialog

blymp = Blueprint('blockly_mp', __name__)
global coords
global dialog


def printCoords(c):
    global coords
    coords = c
    print(c)


