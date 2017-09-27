def classFactory(iface):  # pylint: disable=invalid-name
    """

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .radius_selector_feature import SelectByRadiusPlus
    return SelectByRadiusPlus(iface)
