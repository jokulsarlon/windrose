# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject
import os.path

from .windrose_dialog import WindRoseDialog


class WindRosePlugin:
    """QGIS插件主类"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&风向玫瑰图')
        self.toolbar = self.iface.addToolBar(u'风向玫瑰图')
        self.toolbar.setObjectName(u'WindRoseToolbar')

        self.dialog = None
        self.point_tool = None

    def tr(self, message):
        return QCoreApplication.translate('WindRosePlugin', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True, status_tip=None,
                   whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip:
            action.setStatusTip(status_tip)
        if whats_this:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')  # 可放置一个图标文件
        self.add_action(
            icon_path,
            text=self.tr(u'风向玫瑰图'),
            callback=self.run,
            status_tip=self.tr(u'生成风向玫瑰图'),
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&风向玫瑰图'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        if self.dialog is None:
            self.dialog = WindRoseDialog(self.iface)
        self.dialog.pick_point_clicked.connect(self.activate_point_tool)
        self.dialog.show()

    def activate_point_tool(self):
        canvas = self.iface.mapCanvas()
        if self.point_tool is None:
            self.point_tool = QgsMapToolEmitPoint(canvas)
            self.point_tool.canvasClicked.connect(self.on_point_tool_clicked)
        canvas.setMapTool(self.point_tool)
        self.iface.messageBar().pushInfo("地图选点", "请在地图上点击一个点。")

    def on_point_tool_clicked(self, point, button):
        canvas = self.iface.mapCanvas()
        transform = QgsCoordinateTransform(
            canvas.mapSettings().destinationCrs(),
            QgsCoordinateReferenceSystem("EPSG:4326"),
            QgsProject.instance()
        )
        wgs84_point = transform.transform(point)
        self.dialog.set_coordinates(wgs84_point.x(), wgs84_point.y())
        canvas.unsetMapTool(self.point_tool)
        self.iface.messageBar().clearWidgets()