from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.core import *
from qgis.gui import *

#recupero la versione di QGis dell'utente:
global qgis_version
try:
    from qgis.core import Qgis #versione qgis 3.x
except ImportError:
    from qgis.core import QGis as Qgis #versione qgis 2.x
qgis_version = Qgis.QGIS_VERSION

def getSridAndGeomType(con, table, geometry):
    args = {}
    args['table'] = table
    args['geometry'] = geometry
    cur = con.cursor()
    cur.execute("""
        SELECT ST_SRID(%(geometry)s), ST_GeometryType(%(geometry)s)
            FROM %(table)s 
            LIMIT 1
    """ % args)
    row = cur.fetchone()
    return row[0], row[1]

def refreshMapCanvas(mapCanvas):
    if QGis.QGIS_VERSION_INT < 20400:
        return mapCanvas.clear()
    else:
        return mapCanvas.refresh()

#def logMessage(message, level=QgsMessageLog.INFO):
if (int(qgis_version[0]) < 3):
    qgs_level = QgsMessageLog.INFO
else:
    qgs_level = Qgis.Info
def logMessage(message, level=qgs_level):
    QgsMessageLog.logMessage(message, 'qgis2ol5', level)

