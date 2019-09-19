# -*- coding: utf-8 -*-

# Copyright (C) 2017 Nyall Dawson (nyall.dawson@gmail.com)
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

from qgis.core import (QgsProject)
from PyQt4.QtCore import (QObject)

from olwriter import (OpenLayersWriter)
from leafletWriter import (LeafletWriter)
from configparams import (getDefaultParams)

translator = QObject()


class WriterRegistry(object):

    """
    A registry for known writer types.
    """

    def __init__(self):
        self.writers = {e.type(): e for e in
                        [OpenLayersWriter, LeafletWriter]}

    def getWriters(self):
        """
        :return: List of available writers
        """
        return self.writers.values()

    def saveTypeToProject(self, type):
        """
        Stores a writer type as the type associated with the loaded project
        :param type: type string for associated writer class
        """
        assert QgsProject.instance().writeEntry("qgis2ol5", "mapFormat", type)

    def getWriterFactoryFromProject(self):
        """
        Returns the factory for the writer type associated with the
        load project.
        :return:
        """
        try:
            type = QgsProject.instance().readEntry("qgis2ol5",
                                                   "mapFormat")[0]
            for w in self.writers.values():
                if type.lower() == w.type().lower():
                    return w

        except:
            pass

        return OpenLayersWriter  # default to OpenLayersWriter

    def saveBasemapsToProject(self, basemaps):
        """
        Stores a list of enabled basemaps for the writer
        in the current project.
        :param basemaps: list of basemap names
        """
        basemaplist = ",".join(basemaps)
        QgsProject.instance().writeEntry("qgis2ol5", "Basemaps", basemaplist)

    def getBasemapsFromProject(self):
        """
        Returns a list of enabled basemaps for the writer stored
        in the current project.
        """
        try:
            basemaps = QgsProject.instance().readEntry(
                "qgis2ol5", "Basemaps")[0]
            if basemaps.strip() == '':
                return []
            return basemaps.split(",")
        except:
            return []

    @staticmethod
    def sanitiseKey(key):
        """
        Sanitises a parameter key to make it safe to store in settings
        """
        return key.replace(' ', '')

    def saveParamsToProject(self, params):
        """
        Saves writer parameters to the current project
        :param params: writer parameter dictionary
        """
        for group, settings in params.iteritems():
            for param, value in settings.iteritems():
                if isinstance(value, bool):
                    QgsProject.instance().writeEntryBool("qgis2ol5",
                                                         self.sanitiseKey(
                                                             param),
                                                         value)
                else:
                    QgsProject.instance().writeEntry("qgis2ol5",
                                                     self.sanitiseKey(param),
                                                     value)

    def readParamFromProject(self, parameter, default_value):
        """
        Reads the value of a single parameter from the current
        project.
        :param parameter: parameter key
        :param default_value: default value for parameter
        """
        project = QgsProject.instance()
        key_string = self.sanitiseKey(parameter)

        value = default_value
        if isinstance(default_value, bool):
            if project.readBoolEntry(
                    "qgis2ol5", key_string)[1]:
                value = project.readBoolEntry("qgis2ol5",
                                              key_string)[0]
        elif isinstance(default_value, int):
            if project.readNumEntry(
                    "qgis2ol5", key_string)[1]:
                value = project.readNumEntry("qgis2ol5",
                                             key_string)[0]
        else:
            if (isinstance(project.readEntry("qgis2ol5",
                                             key_string)[0],
                           basestring) and
               project.readEntry("qgis2ol5",
               key_string)[0] != ""):
                value = project.readEntry(
                    "qgis2ol5", key_string)[0]

        return value

    def readParamsFromProject(self):
        """
        Reads all writer parameters from the current project
        :return: default writer parameters within parameters replaced
        by any matching settings in the current projects
        """

        default_params = getDefaultParams()
        read_params = default_params
        for group, settings in default_params.iteritems():
            for param, default_value in settings.iteritems():
                value = self.readParamFromProject(param, default_value)
                read_params[group][param] = value

        return read_params

    def createWriterFromProject(self):
        """
        Creates a writer matching the state from the current project
        """
        writer = self.getWriterFactoryFromProject()()
        writer.params = self.readParamsFromProject()
        writer.params["Appearance"][
            "Base layer"] = self.getBasemapsFromProject()
        return writer

    def saveWriterToProject(self, writer):
        """
        Saves the settings from a writer to the current project
        """
        QgsProject.instance().removeEntry("qgis2ol5", "/")

        self.saveTypeToProject(writer.type())
        self.saveParamsToProject(writer.params)

        basemaps = writer.params["Appearance"]["Base layer"]
        WRITER_REGISTRY.saveBasemapsToProject(basemaps)


# canonical instance.
WRITER_REGISTRY = WriterRegistry()
