import json
from qgis.core import QgsSettings

class SolrSearchSettings:
    
    def __init__(self, path):
        #an empty settings object
        self.settings = {}
        
        # read file
        try:
            with open(path, 'r') as myfile:
                data=myfile.read()

                # parse file
                self.settings = json.loads(data)
        except IOError as e:
            print(("I/O error loading settings file ({0}): {1}").format(e.errno, e.strerror))
        except:
            #handle other exceptions such as attribute errors
            print("Unexpected error:", sys.exc_info()[0])
    
    def getCores(self):
        return self.settings.get("solr_cores")
    
    def getMaxRows(self):
        return self.settings.get("max_results")
    
    def getPluginPrefix(self):
        return self.settings.get("prefix")
        
    def getScale(self):
        return self.settings.get("point_scale")
    
    def getCores(self):
        return self.settings.get("solr_cores")
    
    def getCore(self, coreIndex):
        return self.getCores()[coreIndex]