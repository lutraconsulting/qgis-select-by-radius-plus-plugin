import math
from qgis.core import QgsMapLayer, QgsGeometry, QgsSpatialIndex, QgsRectangle, QgsFeature, QgsPoint, QgsPointLocator
from qgis.gui import QgsMapTool, QgsRubberBand

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QCursor, QColor, QApplication


class RadiusSelector(QgsMapTool):
    def __init__(self, canvas, radius_field, dist_unit_field, iface):

        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.radius_field = radius_field
        self.dist_unit = dist_unit_field
        self.cursor = QCursor(Qt.CrossCursor)
        self.iface = iface
        self.layer = None
        self.index = None
        self.allFeatures = []
        self.rubberBand = None
        self.prev_tool = None

    def canvasReleaseEvent(self, mouseEvent):
        print('canvasReleaseEvent')
        if self.iface.activeLayer() is None:
            return

        if self.iface.activeLayer() == QgsMapLayer.RasterLayer:
            return

        if self.iface.activeLayer().featureCount() == 0:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        if self.layer == None or self.iface.activeLayer() != self.layer:
            self.layer = self.iface.activeLayer()
            self.allFeatures, self.index = self.spatialIndex()

        # TODO @vsklencar onChange radius
        radius = self.getRadius()

        # Determine the location of the click in real-world coords
        layerPoint = self.toLayerCoordinates(self.layer, mouseEvent.pos())

        # apply snapping
        snap_utils = self.canvas.snappingUtils()
        matches = snap_utils.snapToCurrentLayer(mouseEvent.pos(), QgsPointLocator.All)
        if matches.isValid():
            point = matches.point()
            layerPoint = self.toLayerCoordinates(self.layer, point)

        # TODO @vsklencar delete rubberband
        # self.showRubberBand(layerPoint, radius)

        layerData = self.spatialIndexSearch(layerPoint, self.layer, radius, self.allFeatures, self.index)
        self.layer.removeSelection()

        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            QApplication.restoreOverrideCursor()
            return

        for singleInfo in layerData:
            selectedLayer, featureId = singleInfo
            selectedLayer.select(featureId)
        if self.prev_tool:
            self.iface.mapCanvas().setMapTool(self.prev_tool)
        else:
            self.iface.mapCanvas().unsetMapTool(self)


        QApplication.restoreOverrideCursor()

    def spatialIndex(self):

        allfeatures = {}
        index = QgsSpatialIndex()
        for feature in self.layer.getFeatures():
            feat_copy = QgsFeature(feature)
            allfeatures[feature.id()] = feat_copy
            index.insertFeature(feat_copy)
        return allfeatures, index

    def spatialIndexSearch(self, layerPoint, layer, radius, allFeatures, index):
        data = []

        ids = index.intersects(
            QgsRectangle(layerPoint.x() - (radius), layerPoint.y() - (radius), layerPoint.x() + (radius),
                         layerPoint.y() + (radius)))

        for id in ids:
            feature = allFeatures[id]
            dist = feature.geometry().distance(QgsGeometry.fromPoint(layerPoint))

            if dist <= radius:
                data.append((layer, id))

        return data

    def miles_to_meters(self, dist):
        return dist * 1609.344

    def kilometers_to_miles(self, dist):
        return dist * 1000

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def getRadius(self):
        radius = self.radius_field.value()
        if (self.dist_unit.currentText() == 'miles'):
            radius = self.miles_to_meters(radius)
        elif (self.dist_unit.currentText() == 'km'):
            radius = self.kilometers_to_miles(radius)

        return radius

    def showRubberBand(self, point, radius):
        if self.rubberBand != None:
            self.rubberBand.reset(True)

        segments = 360
        points = []
        for t in [(2 * math.pi) / segments * i for i in range(segments)]:
            points.append((radius * math.cos(t), radius * math.sin(t)))
        polygon = [QgsPoint(i[0] + point.x(), i[1] + point.y()) for i in points]
        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(QColor(255, 0, 0, (0.2) * 255))
        self.rubberBand.setWidth(1)

        self.rubberBand.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
