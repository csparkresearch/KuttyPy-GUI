import os
from . import build_details
ENVIRON = build_details.QT_VERSION

os.environ['PYQTGRAPH_QT_LIB'] = ENVIRON
os.environ['CSMCA_QT_LIB'] = ENVIRON

#For remote operation
#os.environ['DATABASE_URL'] = 'postgres:///eyes_db'
