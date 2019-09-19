# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2ol5
                                 A QGIS plugin
 qgis2ol5
                             -------------------
        begin                : 2019-07-31
        copyright            : (C) 2019 by ar_gaeta@yahoo.it
        email                : ar_gaeta@yahoo.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load qgis2ol5 class from file qgis2ol5.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgis2ol5 import qgis2ol5
    return qgis2ol5(iface)
