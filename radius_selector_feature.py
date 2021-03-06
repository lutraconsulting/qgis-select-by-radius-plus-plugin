import os.path

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QComboBox, QDoubleSpinBox, QCheckBox
from qgis.PyQt.QtGui import QIcon

# Initialize Qt resources from file resources.py
# Import the code for the dialog
from .radius_selector_tool import RadiusSelector


class SelectByRadiusPlus(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Select by radius plus')
        self.toolbar = self.iface.addToolBar(u'SelectByRadiusPlus')
        self.toolbar.setObjectName(u'SelectByRadiusPlus')

        self.distance_units = ["m", "km", "miles"]

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SelectByRadiusPlus', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initDistanceWidget(self):
        widget = QDoubleSpinBox()
        widget.setMaximum(9999999.999)
        widget.setDecimals(3)

        return widget

    def initUnitWidget(self):
        widget = QComboBox()
        for unit in self.distance_units:
            widget.addItem(unit)

        return widget

    def initCheckbox(self):
        widget = QCheckBox("Use centroid")
        widget.setToolTip("If it's checked, a feature is selected if its centroid is in radius.")

        return widget

    def initGui(self):
        self.distance_unit_widget = self.initUnitWidget()
        self.distance_widget = self.initDistanceWidget()
        self.use_centroid_checkbox = self.initCheckbox()

        self.radiusSelectorFeatureMapTool = RadiusSelector(self.iface.mapCanvas(), self.distance_widget,
                                                           self.distance_unit_widget, self.use_centroid_checkbox,
                                                           self.iface)

        icon_path = os.path.join(self.plugin_dir, 'resources/icon.png')
        action = self.add_action(
            icon_path,
            text=self.tr(u'Select features in the active layer within a given radius.'),
            callback=self.run,
            parent=self.iface.mainWindow())

        action.setCheckable(True)
        self.radiusSelectorFeatureMapTool.setAction(action)

        self.toolbar.addWidget(self.distance_widget)
        self.toolbar.addWidget(self.distance_unit_widget)
        self.toolbar.addWidget(self.use_centroid_checkbox)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Select by radius plus'),
                action)
            self.iface.removeToolBarIcon(action)

        # Unset the map tool in case it's set
        self.iface.mapCanvas().unsetMapTool(self.radiusSelectorFeatureMapTool)

    def run(self):
        self.radiusSelectorFeatureMapTool.prev_tool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self.radiusSelectorFeatureMapTool)
