# -*- coding: utf-8 -*-

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, Qt, QThread
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QFileDialog, QApplication, QInputDialog, QPushButton, QMenu, QAction
from qgis.core import QgsProject
import os.path
import tempfile

from .windrose_worker import WindRoseWorker
from .windrose_utils import create_rose_layers
from .style_manager import StyleManager
from .export_helper import ExportHelper
from . import i18n

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'windrose_dialog.ui'))


class WindRoseDialog(QDialog, FORM_CLASS):
    """主设置对话框"""

    pick_point_clicked = pyqtSignal()

    def __init__(self, iface, parent=None):
        super(WindRoseDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.project = QgsProject.instance()

        self.current_lon = None
        self.current_lat = None

        self.style_manager = StyleManager()
        self.export_helper = ExportHelper(self.iface)

        # 存储原始样式键值
        self.internal_style_key = None
        self.internal_graph_style_key = None

        # 连接按钮信号
        self.btn_map_point.clicked.connect(self.on_map_point)
        self.btn_manual.clicked.connect(self.on_manual_input)
        self.btn_generate.clicked.connect(self.generate_rose)
        self.btn_browse_svg.clicked.connect(self.browse_svg_path)
        # 原有的导出SVG按钮只是提示，保留
        self.btn_export_svg.clicked.connect(self.export_svg)

        # 添加语言切换按钮
        self.btn_language = QPushButton()
        self.btn_language.clicked.connect(self.switch_language)
        # 将语言按钮添加到按钮布局中（水平布局 horizontalLayout_2）
        # 在生成按钮之前插入语言按钮
        layout = self.horizontalLayout_2
        layout.insertWidget(0, self.btn_language)  # 放在最左边

        # 初始化UI文本（第一次填充）
        self.refresh_ui_texts()

        # 默认值
        self.spin_year.setValue(2024)
        self.cmb_height.setCurrentIndex(0)  # 10m
        self.slider_opacity.setValue(80)
        self.line_svg_path.setText(os.path.join(tempfile.gettempdir(), 'windrose.svg'))

        self.worker = None
        self.thread = None
        self.group_name = None

    def refresh_ui_texts(self):
        """刷新所有UI文本，用于语言切换"""
        # 窗口标题
        self.setWindowTitle(i18n.tr("dialog_title"))
        
        # 分组框
        self.grp_input.setTitle(i18n.tr("grp_input"))
        self.groupBox.setTitle(i18n.tr("groupBox"))
        self.groupBox_2.setTitle(i18n.tr("groupBox_2"))
        
        # 标签
        self.label_lon.setText(i18n.tr("label_lon"))
        self.label_lat.setText(i18n.tr("label_lat"))
        self.label_year.setText(i18n.tr("label_year"))
        self.label_month.setText(i18n.tr("label_month"))
        self.label_height.setText(i18n.tr("label_height"))
        self.label_style.setText(i18n.tr("label_style"))
        self.label_graph_style.setText(i18n.tr("label_graph_style"))
        self.label_opacity.setText(i18n.tr("label_opacity"))
        self.label_svg_path.setText(i18n.tr("label_svg_path"))
        
        # 按钮
        self.btn_map_point.setText(i18n.tr("btn_map_point"))
        self.btn_manual.setText(i18n.tr("btn_manual"))
        self.btn_browse_svg.setText(i18n.tr("btn_browse_svg"))
        self.btn_generate.setText(i18n.tr("btn_generate"))
        self.btn_cancel.setText(i18n.tr("btn_cancel"))
        self.btn_export_svg.setText(i18n.tr("btn_export_svg"))
        
        # 语言按钮文本
        current_lang = i18n.get_language()
        if current_lang == 'zh':
            self.btn_language.setText("English")
        else:
            self.btn_language.setText("中文")
        
        # 复选框
        self.cb_add_to_project.setText(i18n.tr("cb_add_to_project"))
        self.cb_export_svg.setText(i18n.tr("cb_export_svg"))
        
        # 提示文本
        self.btn_map_point.setToolTip(i18n.tr("tooltip_map_point"))
        self.btn_manual.setToolTip(i18n.tr("tooltip_manual"))
        
        # 重新填充组合框（保存当前选中值）
        current_style = self._get_selected_style_key()
        current_graph = self._get_selected_graph_style_key()
        current_month = self.cmb_month.currentText()
        
        self._populate_combos()
        
        # 恢复选中值
        self._set_style_by_internal_key(current_style)
        self._set_graph_style_by_internal_key(current_graph)
        # 尝试恢复月份选中（根据文本匹配）
        idx = self.cmb_month.findText(current_month)
        if idx >= 0:
            self.cmb_month.setCurrentIndex(idx)
    
    def _populate_combos(self):
        """填充所有组合框的选项"""
        # 配色方案
        self.cmb_style.clear()
        style_names = i18n.get_style_names()
        for name in style_names:
            self.cmb_style.addItem(name)
        
        # 图形样式
        self.cmb_graph_style.clear()
        graph_styles = i18n.get_graph_style_names()
        for style in graph_styles:
            self.cmb_graph_style.addItem(style)
        
        # 月份
        self.cmb_month.clear()
        months = i18n.get_month_names()
        for month in months:
            self.cmb_month.addItem(month)
    
    def _get_selected_style_key(self):
        """获取选中的配色方案内部键名"""
        display_name = self.cmb_style.currentText()
        return i18n.get_style_key(display_name)
    
    def _set_style_by_internal_key(self, internal_key):
        """根据内部键名设置配色方案选择"""
        for i in range(self.cmb_style.count()):
            display_name = self.cmb_style.itemText(i)
            if i18n.get_style_key(display_name) == internal_key:
                self.cmb_style.setCurrentIndex(i)
                break
    
    def _get_selected_graph_style_key(self):
        """获取选中的图形样式内部键名"""
        display_name = self.cmb_graph_style.currentText()
        return i18n.get_graph_style_key(display_name)
    
    def _set_graph_style_by_internal_key(self, internal_key):
        """根据内部键名设置图形样式选择"""
        for i in range(self.cmb_graph_style.count()):
            display_name = self.cmb_graph_style.itemText(i)
            if i18n.get_graph_style_key(display_name) == internal_key:
                self.cmb_graph_style.setCurrentIndex(i)
                break

    def switch_language(self):
        """切换中英文语言"""
        current = i18n.get_language()
        if current == 'zh':
            i18n.set_language('en')
        else:
            i18n.set_language('zh')
        self.refresh_ui_texts()

    def init_controls(self):
        self.line_lon.setReadOnly(True)
        self.line_lat.setReadOnly(True)

    def on_map_point(self):
        self.pick_point_clicked.emit()

    def on_manual_input(self):
        lon, ok1 = QInputDialog.getDouble(self, i18n.tr("btn_manual"), i18n.tr("label_lon"), 0, -180, 180, 6)
        if not ok1:
            return
        lat, ok2 = QInputDialog.getDouble(self, i18n.tr("btn_manual"), i18n.tr("label_lat"), 0, -90, 90, 6)
        if not ok2:
            return
        self.set_coordinates(lon, lat)

    def set_coordinates(self, lon, lat):
        self.current_lon = lon
        self.current_lat = lat
        self.update_coord_display()
        self.raise_()
        self.activateWindow()

    def update_coord_display(self):
        if self.current_lon is not None and self.current_lat is not None:
            self.line_lon.setText(f'{self.current_lon:.6f}')
            self.line_lat.setText(f'{self.current_lat:.6f}')
        else:
            self.line_lon.clear()
            self.line_lat.clear()

    def browse_svg_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("btn_export_svg"), self.line_svg_path.text(), 'SVG files (*.svg)'
        )
        if path:
            self.line_svg_path.setText(path)

    def generate_rose(self):
        # 检查线程
        if self.thread is not None:
            try:
                if self.thread.isRunning():
                    QMessageBox.warning(self, i18n.tr("dialog_title"), i18n.tr("msg_wait_previous"))
                    return
                else:
                    self.thread = None
                    self.worker = None
            except RuntimeError:
                self.thread = None
                self.worker = None

        if self.current_lon is None or self.current_lat is None:
            QMessageBox.warning(self, i18n.tr("dialog_title"), i18n.tr("msg_no_point"))
            return

        year = self.spin_year.value()
        height_str = self.cmb_height.currentText()
        height = int(height_str.replace('m', ''))
        
        # 保存内部键名
        self.internal_style_key = self._get_selected_style_key()
        self.internal_graph_style_key = self._get_selected_graph_style_key()
        
        self.style_name = self.internal_style_key
        self.graph_style = self.internal_graph_style_key
        self.opacity = self.slider_opacity.value() / 100.0
        self.add_to_project = self.cb_add_to_project.isChecked()
        self.export_svg = self.cb_export_svg.isChecked()
        self.svg_path = self.line_svg_path.text() if self.export_svg else None

        month_text = self.cmb_month.currentText()
        if month_text == i18n.tr("month_full_year"):
            month = None
            month_str = i18n.tr("month_full_year")
        else:
            # 从本地化月份名称解析月份数字
            month_names = i18n.get_month_names()
            try:
                month = month_names.index(month_text)
            except ValueError:
                month = None
            month_str = month_text

        lon_str = f"{self.current_lon:.4f}".replace('.', '_')
        lat_str = f"{self.current_lat:.4f}".replace('.', '_')
        group_prefix = i18n.tr("group_prefix")
        self.group_name = f"{group_prefix}-{year}-{month_str}-{lon_str}_{lat_str}"

        self.btn_generate.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        self.worker = WindRoseWorker(
            self.current_lon, self.current_lat, year, month, height
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_data_ready)
        self.worker.error.connect(self.on_worker_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_data_ready(self, freq, labels, angles):
        """数据准备就绪，在主线程中创建图层"""
        QApplication.restoreOverrideCursor()
        self.btn_generate.setEnabled(True)

        try:
            if self.add_to_project:
                show_circles = (self.graph_style == "同心圆式")
                layers = create_rose_layers(
                    self.current_lon, self.current_lat, freq, labels, angles,
                    group_name=self.group_name, show_circles=show_circles
                )
                StyleManager.apply_style_to_layers(layers, self.style_name, self.opacity)

                if self.export_svg and layers:
                    # 选择需要导出的图层：扇区面、闭合面、坐标线、指北箭头
                    export_layer_names = [
                        i18n.tr("layer_sectors"),
                        i18n.tr("layer_closed_polygon"),
                        i18n.tr("layer_coord_lines"),
                        i18n.tr("layer_north_arrow")
                    ]
                    export_layers = [lyr for lyr in layers if lyr.name() in export_layer_names]
                    if export_layers:
                        self.export_helper.export_layers_as_svg(export_layers, self.svg_path, self.iface)
                    else:
                        # 如果没有找到，则导出全部图层（备用）
                        self.export_helper.export_layers_as_svg(layers, self.svg_path, self.iface)

            QMessageBox.information(self, i18n.tr("dialog_title"), i18n.tr("msg_complete"))
        except Exception as e:
            QMessageBox.critical(self, i18n.tr("dialog_title"), i18n.tr("msg_error_generate", error=str(e)))

        self.thread = None
        self.worker = None

    def on_worker_error(self, error_msg):
        QApplication.restoreOverrideCursor()
        self.btn_generate.setEnabled(True)
        QMessageBox.critical(self, i18n.tr("dialog_title"), error_msg)
        self.thread = None
        self.worker = None

    def export_svg(self):
        QMessageBox.information(self, i18n.tr("dialog_title"), i18n.tr("msg_export_hint"))