# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication, QSettings
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject
import os.path

from .windrose_dialog import WindRoseDialog
from . import i18n


class WindRosePlugin:
    """QGIS插件主类"""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&Wind Rose')
        self.toolbar = self.iface.addToolBar(u'Wind Rose')
        self.toolbar.setObjectName(u'WindRoseToolbar')

        self.dialog = None
        self.point_tool = None
        
        # 初始化语言
        self.init_language()

    def tr(self, message):
        return QCoreApplication.translate('WindRosePlugin', message)

    def init_language(self):
        """初始化语言设置"""
        settings = QSettings()
        lang = settings.value("WindRose/Language", "zh")
        i18n.set_language(lang)

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
        icon_path = os.path.join(self.plugin_dir, 'icons', 'windrose.svg')
        self.add_action(
            icon_path,
            text=self.tr(u'Wind Rose'),
            callback=self.run,
            status_tip=self.tr(u'Generate wind rose diagram'),
            parent=self.iface.mainWindow())
        
        # 添加语言切换菜单
        self.language_menu = QMenu(self.tr(u'Language'))
        self.action_zh = QAction(self.tr(u'中文'), self.language_menu)
        self.action_en = QAction(self.tr(u'English'), self.language_menu)
        self.action_zh.triggered.connect(lambda: self.switch_language('zh'))
        self.action_en.triggered.connect(lambda: self.switch_language('en'))
        self.language_menu.addAction(self.action_zh)
        self.language_menu.addAction(self.action_en)
        
        # 添加到工具栏或菜单
        self.language_action = QAction(self.tr(u'Language'), self.iface.mainWindow())
        self.language_action.setMenu(self.language_menu)
        self.iface.addPluginToMenu(self.menu, self.language_action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Wind Rose'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def switch_language(self, lang):
        """切换语言"""
        if i18n.get_language() == lang:
            return
        i18n.set_language(lang)
        # 如果对话框已打开，刷新其界面
        if self.dialog is not None and self.dialog.isVisible():
            self.dialog.refresh_ui_texts()

    def run(self):
        if self.dialog is None:
            self.dialog = WindRoseDialog(self.iface)
        else:
            # 确保对话框的语言是最新的
            self.dialog.refresh_ui_texts()
        self.dialog.pick_point_clicked.connect(self.activate_point_tool)
        self.dialog.show()

    def activate_point_tool(self):
        canvas = self.iface.mapCanvas()
        if self.point_tool is None:
            self.point_tool = QgsMapToolEmitPoint(canvas)
            self.point_tool.canvasClicked.connect(self.on_point_tool_clicked)
        canvas.setMapTool(self.point_tool)
        self.iface.messageBar().pushInfo(i18n.tr("msg_pick_point"), i18n.tr("msg_pick_point"))

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