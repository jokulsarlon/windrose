# -*- coding: utf-8 -*-

import numpy as np
from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsPointXY,
    QgsProject, QgsLayerTreeLayer, QgsRendererCategory, QgsCategorizedSymbolRenderer,
    QgsFillSymbol
)
from qgis.PyQt.QtCore import QVariant


def compute_frequencies(wind_dir_list):
    wd = np.array(wind_dir_list)
    wd_shift = (wd - 11.25) % 360
    bins = np.arange(0, 360 + 22.5, 22.5)
    labels = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    freq, _ = np.histogram(wd_shift, bins)
    angles = np.arange(0, 360, 22.5)
    return freq, labels, angles


def create_rose_layers(lon, lat, freq, labels, angles, group_name="风玫瑰", show_circles=False):
    project = QgsProject.instance()
    root = project.layerTreeRoot()

    old_group = root.findGroup(group_name)
    if old_group:
        layers_to_remove = []
        for child in old_group.children():
            if isinstance(child, QgsLayerTreeLayer):
                layers_to_remove.append(child.layerId())
        if layers_to_remove:
            project.removeMapLayers(layers_to_remove)
        root.removeChildNode(old_group)

    group = root.addGroup(group_name)
    layers = []

    # 1. 点图层
    pt_layer = QgsVectorLayer("Point?crs=EPSG:4326", "采集点", "memory")
    pr = pt_layer.dataProvider()
    pr.addAttributes([QgsField("Lon", QVariant.Double), QgsField("Lat", QVariant.Double)])
    pt_layer.updateFields()
    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
    ft.setAttributes([lon, lat])
    pr.addFeature(ft)
    layers.append(pt_layer)

    # 2. 风向频率表
    freq_layer = QgsVectorLayer("None", "风向频率", "memory")
    pr = freq_layer.dataProvider()
    pr.addAttributes([QgsField("Dir", QVariant.String),
                      QgsField("Angle", QVariant.Double),
                      QgsField("Freq", QVariant.Int)])
    freq_layer.updateFields()
    features = []
    for d, a, f in zip(labels, angles, freq):
        ft = QgsFeature(freq_layer.fields())
        ft.setAttributes([d, float(a), int(f)])
        features.append(ft)
    pr.addFeatures(features)
    layers.append(freq_layer)

    # 计算顶点
    center = QgsPointXY(lon, lat)
    points = []
    max_freq = max(freq) if max(freq) > 0 else 1
    scale = 1.0 / 1000.0
    for ang, f in zip(angles, freq):
        R = f * scale
        rad = np.radians((90 - ang) % 360)
        points.append(QgsPointXY(lon + R * np.cos(rad), lat + R * np.sin(rad)))

    # 3. 外环线
    line_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "外环线", "memory")
    pr = line_layer.dataProvider()
    pr.addAttributes([QgsField("MaxR", QVariant.Double)])
    line_layer.updateFields()
    polyline = points + [points[0]]
    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPolylineXY(polyline))
    ft.setAttributes([float(max_freq * scale)])
    pr.addFeature(ft)
    layers.append(line_layer)

    # 4. 闭合面 - 透明填充，黑色轮廓
    poly_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "闭合面", "memory")
    pr = poly_layer.dataProvider()
    pr.addAttributes([QgsField("MaxR", QVariant.Double)])
    poly_layer.updateFields()
    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPolygonXY([polyline]))
    ft.setAttributes([float(max_freq * scale)])
    pr.addFeature(ft)

    # 设置闭合面符号
    symbol = QgsFillSymbol.createSimple({
        'color': 'rgba(0,0,0,0)',
        'outline_color': 'black',
        'outline_width': '0.2'
    })
    poly_layer.renderer().setSymbol(symbol)
    layers.append(poly_layer)

    # 5. 扇区三角面 - 按Parity字段分类符号化
    tri_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "扇区面", "memory")
    pr = tri_layer.dataProvider()
    pr.addAttributes([
        QgsField("Dir", QVariant.String),
        QgsField("Angle", QVariant.Double),
        QgsField("Freq", QVariant.Int),
        QgsField("Parity", QVariant.Int)
    ])
    tri_layer.updateFields()
    features = []
    for i in range(16):
        p1 = points[i]
        p2 = points[(i + 1) % 16]
        geom = QgsGeometry.fromPolygonXY([[center, p1, p2, center]])
        ft = QgsFeature(tri_layer.fields())
        ft.setGeometry(geom)
        ft.setAttributes([labels[i], float(angles[i]), int(freq[i]), i % 2])
        features.append(ft)
    pr.addFeatures(features)

    # 分类渲染器
    categories = []
    sym0 = QgsFillSymbol.createSimple({'color': 'white', 'outline_color': 'black', 'outline_width': '0.2'})
    cat0 = QgsRendererCategory(0, sym0, "Parity 0")
    categories.append(cat0)
    sym1 = QgsFillSymbol.createSimple({'color': 'black', 'outline_color': 'black', 'outline_width': '0.2'})
    cat1 = QgsRendererCategory(1, sym1, "Parity 1")
    categories.append(cat1)

    renderer = QgsCategorizedSymbolRenderer('Parity', categories)
    tri_layer.setRenderer(renderer)
    layers.append(tri_layer)

    # 6. 坐标参考线
    ref_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "坐标线", "memory")
    pr = ref_layer.dataProvider()
    pr.addAttributes([QgsField("Type", QVariant.String)])
    ref_layer.updateFields()
    if max_freq > 0:
        EW_len = max(freq[4], freq[12]) * scale * 1.2
    else:
        EW_len = 0.001
    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(lon - EW_len, lat),
        QgsPointXY(lon + EW_len, lat)
    ]))
    ft.setAttributes(["EW"])
    pr.addFeature(ft)
    SN_len = max_freq * scale * 1.2
    ft = QgsFeature()
    ft.setGeometry(QgsGeometry.fromPolylineXY([
        QgsPointXY(lon, lat - SN_len),
        QgsPointXY(lon, lat + SN_len)
    ]))
    ft.setAttributes(["SN"])
    pr.addFeature(ft)
    layers.append(ref_layer)

    # 7. 同心圆参考线
    if show_circles:
        circle_layer = QgsVectorLayer("LineString?crs=EPSG:4326", "同心圆参考线", "memory")
        pr = circle_layer.dataProvider()
        pr.addAttributes([QgsField("Radius", QVariant.Double)])
        circle_layer.updateFields()
        max_r = max_freq * scale
        for percent in [0.2, 0.4, 0.6, 0.8, 1.0]:
            r = max_r * percent
            circle_points = []
            for angle in range(0, 360, 30):
                rad = np.radians(angle)
                circle_points.append(QgsPointXY(lon + r * np.cos(rad), lat + r * np.sin(rad)))
            circle_points.append(circle_points[0])
            ft = QgsFeature()
            ft.setGeometry(QgsGeometry.fromPolylineXY(circle_points))
            ft.setAttributes([float(r)])
            pr.addFeature(ft)
        layers.append(circle_layer)

    for lyr in layers:
        project.addMapLayer(lyr, False)
        group.addLayer(lyr)

    return layers