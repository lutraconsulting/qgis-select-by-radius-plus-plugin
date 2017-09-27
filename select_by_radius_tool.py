from qgis.core import QgsMapLayer, QgsGeometry
from qgis.gui import QgsMapTool

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QCursor


class RadiusSelector(QgsMapTool):
    
    def __init__(self, canvas, radius_field, dist_unit_field):
        
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.radius_field = radius_field
        self.dist_unit = dist_unit_field
        self.cursor = QCursor(Qt.CrossCursor)


    def miles_to_meters(self, dist):
        return dist * 1609.344

    def kilometers_to_miles(self, dist):
        return dist * 1000
        
    def activate(self):
        self.canvas.setCursor(self.cursor)

    def canvasReleaseEvent(self, mouseEvent):

        layerData = []
        radius = self.radius_field.value()

        for layer in self.canvas.layers():

            if layer.type() != QgsMapLayer.VectorLayer:
                # Ignore this layer as it's not a vector
                continue

            if layer.featureCount() == 0:
                # There are no features - skip
                continue

            # Determine the location of the click in real-world coords
            layerPoint = self.toLayerCoordinates(layer, mouseEvent.pos())

            # Loop through all features in the layer
            for f in layer.getFeatures():
                dist = f.geometry().distance(QgsGeometry.fromPoint(layerPoint))

                if (self.dist_unit.currentText() == 'miles'):
                    radius = self.miles_to_meters(radius)
                elif (self.dist_unit.currentText() == 'km'):
                    print("converting km")
                    radius = self.kilometers_to_miles(radius)

                if dist <= radius:
                    info = (layer, f.id())
                    layerData.append(info)

            layer.removeSelection()

        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

        for singleInfo in layerData:
            layerWithClosestFeature, closestFeatureId = singleInfo
            layerWithClosestFeature.select(closestFeatureId)


