from qgis.core import Qgis, QgsMessageLog, QgsLocatorFilter, QgsLocatorResult, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsSettings
from .networkaccessmanager import NetworkAccessManager, RequestsException
from qgis.PyQt.QtCore import pyqtSignal
import json
from .solrsearchsettings import SolrSearchSettings
from .solrsearchlocatorfilter import SolrSearchLocatorFilter

class SolrSearchPlugin:
    def __init__(self, iface):

        self.iface = iface
        self.filter = SolrSearchLocatorFilter(self.iface)

        self.filter.resultProblem.connect(self.show_problem)
        self.iface.registerLocatorFilter(self.filter)

    def show_problem(self, err):
        self.filter.info("showing problem???")
        self.iface.messageBar().pushWarning("SolrSearch Error", '{}'.format(err))

    def initGui(self):
        pass

    def unload(self):
        self.iface.deregisterLocatorFilter(self.filter)

