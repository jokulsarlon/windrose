# -*- coding: utf-8 -*-

def classFactory(iface):
    from .windrose_plugin import WindRosePlugin
    return WindRosePlugin(iface)