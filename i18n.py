# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QSettings

_LANGUAGE_KEY = "WindRose/Language"

# 中文翻译字典
_ZH = {
    # 对话框标题和分组
    "dialog_title": "风向玫瑰图设置",
    "grp_input": "位置输入",
    "btn_map_point": "地图选点",
    "btn_manual": "手动输入",
    "label_lon": "经度:",
    "label_lat": "纬度:",
    "groupBox": "数据参数",
    "label_year": "年份:",
    "label_month": "月份:",
    "label_height": "高度:",
    "groupBox_2": "输出样式",
    "label_style": "配色方案:",
    "label_graph_style": "图形样式:",
    "label_opacity": "扇区透明度:",
    "cb_add_to_project": "添加到QGIS项目",
    "cb_export_svg": "导出SVG",
    "label_svg_path": "SVG保存路径:",
    "btn_browse_svg": "浏览...",
    "btn_generate": "生成",
    "btn_export_svg": "导出SVG",
    "btn_cancel": "取消",
    
    # 月份
    "month_full_year": "全年",
    "month_jan": "1月",
    "month_feb": "2月",
    "month_mar": "3月",
    "month_apr": "4月",
    "month_may": "5月",
    "month_jun": "6月",
    "month_jul": "7月",
    "month_aug": "8月",
    "month_sep": "9月",
    "month_oct": "10月",
    "month_nov": "11月",
    "month_dec": "12月",
    
    # 图形样式
    "style_sector": "扇区式",
    "style_concentric": "同心圆式",
    
    # 配色方案
    "color_default": "默认",
    "color_warm": "暖色",
    "color_cold": "冷色",
    
    # 图层名称
    "layer_point": "采集点",
    "layer_freq_table": "风向频率",
    "layer_outline": "外环线",
    "layer_closed_polygon": "闭合面",
    "layer_sectors": "扇区面",
    "layer_coord_lines": "坐标线",
    "layer_north_arrow": "指北箭头",
    "layer_circles": "同心圆参考线",
    
    # 组名前缀
    "group_prefix": "风玫瑰图",
    
    # 消息框
    "msg_no_point": "请先选择一个点（地图选点或手动输入）",
    "msg_wait_previous": "上一个生成任务尚未完成，请稍候。",
    "msg_complete": "风玫瑰图生成完成",
    "msg_error_generate": "生成过程中发生错误: {}",
    "msg_error_api": "API请求失败: {}",
    "msg_no_wind_data": "未找到风向数据（高度{}m可能不支持）",
    "msg_wind_data_empty": "风向数据全部为空",
    "msg_pick_point": "请在地图上点击一个点。",
    "msg_export_hint": "请在生成时勾选“导出SVG”自动导出。",
    "msg_no_layers_export": "没有图层可导出",
    "msg_extent_empty": "图层范围为空",
    
    # 其他
    "tooltip_map_point": "点击地图选择点",
    "tooltip_manual": "手动输入经纬度",
    "status_generate": "生成风向玫瑰图",
}

# 英文翻译字典
_EN = {
    "dialog_title": "Wind Rose Settings",
    "grp_input": "Location Input",
    "btn_map_point": "Pick from Map",
    "btn_manual": "Manual Input",
    "label_lon": "Longitude:",
    "label_lat": "Latitude:",
    "groupBox": "Data Parameters",
    "label_year": "Year:",
    "label_month": "Month:",
    "label_height": "Height:",
    "groupBox_2": "Output Style",
    "label_style": "Color Scheme:",
    "label_graph_style": "Graph Style:",
    "label_opacity": "Sector Opacity:",
    "cb_add_to_project": "Add to QGIS Project",
    "cb_export_svg": "Export SVG",
    "label_svg_path": "SVG Save Path:",
    "btn_browse_svg": "Browse...",
    "btn_generate": "Generate",
    "btn_export_svg": "Export SVG",
    "btn_cancel": "Cancel",
    
    "month_full_year": "Full Year",
    "month_jan": "January",
    "month_feb": "February",
    "month_mar": "March",
    "month_apr": "April",
    "month_may": "May",
    "month_jun": "June",
    "month_jul": "July",
    "month_aug": "August",
    "month_sep": "September",
    "month_oct": "October",
    "month_nov": "November",
    "month_dec": "December",
    
    "style_sector": "Sector Style",
    "style_concentric": "Concentric Style",
    
    "color_default": "Default",
    "color_warm": "Warm",
    "color_cold": "Cold",
    
    "layer_point": "Sample Point",
    "layer_freq_table": "Frequency Table",
    "layer_outline": "Outline",
    "layer_closed_polygon": "Closed Polygon",
    "layer_sectors": "Sector Faces",
    "layer_coord_lines": "Coordinate Lines",
    "layer_north_arrow": "North Arrow",
    "layer_circles": "Concentric Circles",
    
    "group_prefix": "WindRose",
    
    "msg_no_point": "Please select a point first (pick from map or manual input)",
    "msg_wait_previous": "Previous generation task is still running, please wait.",
    "msg_complete": "Wind rose generated successfully",
    "msg_error_generate": "Error during generation: {}",
    "msg_error_api": "API request failed: {}",
    "msg_no_wind_data": "Wind direction data not found (height {}m may not be supported)",
    "msg_wind_data_empty": "All wind direction data are empty",
    "msg_pick_point": "Please click on the map to select a point.",
    "msg_export_hint": "Please check \"Export SVG\" during generation to auto-export.",
    "msg_no_layers_export": "No layers to export",
    "msg_extent_empty": "Layer extent is empty",
    
    "tooltip_map_point": "Click on map to select point",
    "tooltip_manual": "Enter longitude/latitude manually",
    "status_generate": "Generate wind rose diagram",
}

# 当前语言
_current_lang = None


def set_language(lang):
    """设置当前语言: 'zh' 或 'en'"""
    global _current_lang
    _current_lang = lang
    settings = QSettings()
    settings.setValue(_LANGUAGE_KEY, lang)


def get_language():
    """获取当前语言"""
    global _current_lang
    if _current_lang is None:
        settings = QSettings()
        _current_lang = settings.value(_LANGUAGE_KEY, 'zh')
    return _current_lang


def tr(key, **kwargs):
    """翻译函数，支持格式化参数"""
    lang = get_language()
    if lang == 'en':
        text = _EN.get(key, key)
    else:
        text = _ZH.get(key, key)
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text


def get_month_names():
    """获取月份名称列表（从1月到12月加全年）"""
    months = [tr("month_full_year")]
    month_keys = ["month_jan", "month_feb", "month_mar", "month_apr", "month_may", "month_jun",
                  "month_jul", "month_aug", "month_sep", "month_oct", "month_nov", "month_dec"]
    for key in month_keys:
        months.append(tr(key))
    return months


def get_style_names():
    """获取本地化的样式名称列表"""
    return [tr("color_default"), tr("color_warm"), tr("color_cold")]


def get_style_key(display_name):
    """将本地化显示名称映射回内部键名"""
    mapping = {
        tr("color_default"): "默认",
        tr("color_warm"): "暖色",
        tr("color_cold"): "冷色",
    }
    return mapping.get(display_name, "默认")


def get_graph_style_names():
    """获取本地化的图形样式名称"""
    return [tr("style_sector"), tr("style_concentric")]


def get_graph_style_key(display_name):
    """将本地化图形样式名称映射回内部键名"""
    mapping = {
        tr("style_sector"): "扇区式",
        tr("style_concentric"): "同心圆式",
    }
    return mapping.get(display_name, "扇区式")