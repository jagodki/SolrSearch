from qgis.core import (Qgis,
                       QgsMessageLog,
                       QgsLocatorFilter,
                       QgsLocatorResult,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsSettings,
                       QgsGeometry,
                       QgsBlockingNetworkRequest
)
from .networkaccessmanager import NetworkAccessManager, RequestsException
from qgis.PyQt.QtCore import pyqtSignal, QUrl
from qgis.gui import QgsRubberBand
from qgis.PyQt.QtGui import (QColor,
                             QIcon
)
from qgis.PyQt.QtNetwork import QNetworkRequest
import json, pathlib
from .solrsearchsettings import SolrSearchSettings

class SolrSearchLocatorFilter(QgsLocatorFilter):

    USER_AGENT = b'Mozilla/5.0 QGIS SolrSearchLocatorFilter'
    rubberbands = []

    resultProblem = pyqtSignal(str)

    def __init__(self, iface):
        # it is mandatory to save the handle to iface, else segfaults!!
        self.iface = iface
        super(QgsLocatorFilter, self).__init__()
        
        #read the settings
        settings_path = QgsSettings().value("SolrSearch/settings_path", str(pathlib.Path(__file__).parent.resolve()) + "/settings.json")
        self.settings = SolrSearchSettings(settings_path)

    def name(self):
        return self.__class__.__name__

    def clone(self):
        return SolrSearchLocatorFilter(self.iface)

    def displayName(self):
        return 'SolrSearch'

    def prefix(self):
        prefix = self.settings.getPluginPrefix()
        
        if prefix is None or prefix == "":
            prefix = "solr"
        
        return prefix
    
    def clearPreviousResults(self):
        self.removeRubberbands()
    
    def fetchResults(self, search, context, feedback):
        if len(search) < 2:
            return
        
        # if search[-1] != ' ':
            # return
        
        result = QgsLocatorResult()
        for core in self.settings.getCores():
        
            #look up for spaces in the search string
            search_string = ""
            for part in search.split(" "):
                search_string += part + "*" + core.get("query").get("connection")
            
            #create the request url
            url = (core.get("url")
                    + "q="
                    + core.get("query").get("query_field")
                    + ":*"
                    + "&fq="
                    + core.get("query").get("query_field")
                    + ":"
                    + core.get("query").get("query_prefix")
                    + "*"
                    + search_string
                    + "*"
                    + core.get("query").get("query_suffix")
                    + "&q.op=AND"
                    + "&wt=json&rows="
                    + str(self.settings.getMaxRows()))
            
            self.info('Search url {}'.format(url))
            nam = NetworkAccessManager()
            try:
                nam = QgsBlockingNetworkRequest()
                request = QNetworkRequest(QUrl(url))
                request.setHeader(QNetworkRequest.UserAgentHeader, self.USER_AGENT)
                nam.get(request, forceRefresh=True)
                reply = nam.reply()
                
                if reply.attribute(QNetworkRequest.HttpStatusCodeAttribute) == 200: 
                    content_string = reply.content().data().decode('utf8')
                    locations = json.loads(content_string).get("response").get("docs")
                    for loc in locations:
                        #get the icon
                        if core.get("icon_path") != "":
                            icon = QIcon(core.get("icon_path"))
                            result.icon = icon
                        
                        #set the results
                        result.group = core.get("external_name")
                        result.filter = self
                        result.displayString = loc.get(core.get("result_field"))
                        result.userData = loc
                        self.resultFetched.emit(result)
            
            except RequestsException as err:
                # Handle exception
                self.info(err)
                self.resultProblem.emit('{}'.format(err))

    def triggerResult(self, result):
        try:
            doc = result.getUserData()
        except:
            doc = result.userData
        extent = self.geometryExtent(doc.get(self.settings.getCore(1).get("geom_field")))
        self.iface.mapCanvas().setExtent(extent)
        self.iface.mapCanvas().zoomScale(self.settings.getScale())
        self.createRubberband(extent)
        self.iface.mapCanvas().refresh()
    
    def geometryExtent(self, wktGeometry):
        #init the extent
        extent = ""
        
        #crs-handling and transformation
        dest_crs = QgsProject.instance().crs()
        src_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        
        #get the geometry
        geom = QgsGeometry.fromWkt(wktGeometry)
        geom_type = geom.type()
        
        if geom_type == 0: #point
            point = geom.asPoint()
            rectangle = QgsRectangle(point.x() - 0.0001, point.y() - 0.0001, point.x() + 0.0001, point.y() + 0.0001)
            extent = transform.transformBoundingBox(rectangle)
        elif geom_type == 2 or geom_type == 1: #polygon or linestring
            polygon = geom.asQPolygonF()
            transform.transformPolygon(polygon)
            extent = QgsGeometry.fromQPolygonF(polygon).boundingBox()
        
        return extent
    
    def createRubberband(self, bbox):
        #remove all existing rubberbands
        self.removeRubberbands()
        
        #create a new rubberband
        r = QgsRubberBand(self.iface.mapCanvas(), True)
        r.setToGeometry(QgsGeometry.fromWkt(bbox.asWktPolygon()))
        r.setStrokeColor(QColor(255, 0, 0))
        r.setWidth(3)
        self.rubberbands.append(r)
    
    def removeRubberbands(self):
        for rb in self.rubberbands:
            self.iface.mapCanvas().scene().removeItem(rb)
        self.rubberbands = []
    
    def info(self, msg=""):
        QgsMessageLog.logMessage('{} {}'.format(self.__class__.__name__, msg), 'SolrSearch', Qgis.Info)
