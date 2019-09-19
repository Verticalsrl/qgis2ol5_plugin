# qgis2ol5 Creates OpenLayers map from QGIS layers
# Copyright (C) 2014 Victor Olaya (volayaf@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from qgis.core import QgsApplication
import os
import shutil
from utils import tempFolder
from exporter import EXPORTER_REGISTRY


def getTemplates():
    src = os.path.join(os.path.dirname(__file__), "templates")
    dst = os.path.join(QgsApplication.qgisSettingsDirPath(), "qgis2ol5",
                       "templates")
    if not os.path.exists(dst):
        shutil.copytree(src, dst)
    else:
        for fname in os.listdir(src):
            with open(os.path.join(src, fname)) as s:
                srcCode = s.read()
            with open(os.path.join(dst, os.path.basename(fname)), 'w') as d:
                d.seek(0)
                d.write(srcCode)
                d.truncate()
    return tuple(f[:f.find(".")] for f in reversed(os.listdir(dst))
                 if f.endswith("html"))


def getParams(configure_exporter_action=None):
    params = {
        "Appearance": {
            "Add layers list": ("None", "Collapsed", "Expanded"),
            "Match project CRS": False,
            "Add address search": False,
            "Layer search": ("None", "placeholder"),
            "Measure tool": ("None", "Metric", "Imperial"),
            "Show popups on hover": False,
            "Highlight on hover": False,
            "Geolocate user": False,
            "Template": getTemplates()
        },
        "Data export": {
            "Precision": ("maintain", "1", "2", "3", "4", "5", "6", "7", "8",
                          "9", "10", "11", "12", "13", "14", "15"),
            "Minify GeoJSON files": True,
            "Mapping library location": ("Local", "CDN"),
            "Use debug libraries": False
        },
        "Scale/Zoom": {
            "Extent": ("Canvas extent", "Fit to layers extent"),
            "Restrict to extent": False,
            "Max zoom level": ("1", "2", "3", "4", "5", "6", "7",
                               "8", "9", "10", "11", "12", "13", "14",
                               "15", "16", "17", "18", "19", "20", "21",
                               "22", "23", "24", "25", "26", "27", "28"),
            "Min zoom level": ("1", "2", "3", "4", "5", "6", "7",
                               "8", "9", "10", "11", "12", "13", "14",
                               "15", "16", "17", "18", "19", "20", "21",
                               "22", "23", "24", "25", "26", "27", "28"),
        }
    }

    if configure_exporter_action:
        params["Data export"]["Exporter"] = {'option':
                                             EXPORTER_REGISTRY.getOptions(),
                                             'action':
                                             configure_exporter_action}
    else:
        params["Data export"]["Exporter"] = EXPORTER_REGISTRY.getOptions()

    return params


def getDefaultParams():
    params = getParams()
    for group, settings in params.iteritems():
        for param, value in settings.iteritems():
            if isinstance(value, tuple):
                if param == 'Max zoom level':
                    settings[param] = value[-1]
                else:
                    settings[param] = value[0]
    params['Appearance']['Base layer'] = []
    params['Appearance']['Search layer'] = None
    return params


baselayers = (
    "OSM",
    "OSM B&W",
    "Stamen Toner",
    "OSM DE",
    "OSM HOT",
    "Thunderforest Cycle",
    "Thunderforest Transport",
    "Thunderforest Landscape",
    "Thunderforest Outdoors",
    "OpenMapSurfer Roads",
    "OpenMapSurfer adminb",
    "OpenMapSurfer roadsg",
    "Stamen Terrain",
    "Stamen Terrain background",
    "Stamen Watercolor",
    "OpenWeatherMap Clouds",
    "OpenWeatherMap Precipitation",
    "OpenWeatherMap Rain",
    "OpenWeatherMap Pressure",
    "OpenWeatherMap Wind",
    "OpenWeatherMap Temp",
    "OpenWeatherMap Snow"
),

specificParams = {
}

specificOptions = {
}
