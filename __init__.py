# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BDOT10k_plugin
                                 A QGIS plugin
 This plugin operates on BDOT10k.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-01-06
        copyright            : (C) 2022 by marylaGIS
        email                : maryla.qgis@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BDOT10k_plugin class from file BDOT10k_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .bdot10k import BDOT10k_plugin
    return BDOT10k_plugin(iface)
