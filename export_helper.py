# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QRectF, QSize
from qgis.PyQt.QtGui import QColor, QPainter
from qgis.PyQt.QtSvg import QSvgGenerator
from qgis.core import (
    QgsMapSettings, QgsMapRendererCustomPainterJob
)


class ExportHelper:
    def __init__(self, iface):
        self.iface = iface

    @staticmethod
    def export_layers_as_svg(layers, file_path, iface, dpi=96):
        """
        将指定的图层列表导出为SVG文件，使用直接渲染方式。
        layers: QgsMapLayer 列表
        """
        if not layers:
            raise Exception("没有图层可导出")

        # 合并所有图层的范围
        extent = layers[0].extent()
        for layer in layers[1:]:
            extent.combineExtentWith(layer.extent())

        if extent.isEmpty() or extent.isNull():
            raise Exception("图层范围为空")

        # 计算合适的输出尺寸
        target_width = 800
        target_height = int(target_width * (extent.height() / extent.width()))

        settings = QgsMapSettings()
        settings.setLayers(layers)
        settings.setExtent(extent)
        settings.setOutputSize(QSize(target_width, target_height))
        settings.setOutputDpi(dpi)
        settings.setBackgroundColor(QColor(255, 255, 255, 255))  # 白色背景

        svg_gen = QSvgGenerator()
        svg_gen.setFileName(file_path)
        svg_gen.setSize(QSize(target_width, target_height))
        svg_gen.setViewBox(QRectF(0, 0, target_width, target_height))
        svg_gen.setTitle("WindRose")
        svg_gen.setDescription("Exported from QGIS")

        painter = QPainter()
        painter.begin(svg_gen)
        job = QgsMapRendererCustomPainterJob(settings, painter)
        job.start()
        job.waitForFinished()
        painter.end()

        return True