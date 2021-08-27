def classFactory(iface):
    """Load SolrSearchFilterPlugin class from file solrsearchfilter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .solrsearch import SolrSearchPlugin
    return SolrSearchPlugin(iface)
