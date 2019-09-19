Plugin Builder Results

Your plugin qgis2ol5 was created in:
    C:\Users\riccardo\.qgis2\python\plugins\qgis2ol5

Your QGIS plugin directory is located at:
    C:/Users/riccardo/.qgis2/python/plugins

What's Next:

  * Copy the entire directory containing your new plugin to the QGIS plugin
    directory

  * Compile the resources file using pyrcc4

  * Run the tests (``make test``)

  * Test the plugin by enabling it in the QGIS plugin manager

  * Customize it by editing the implementation file: ``qgis2ol5.py``

  * Create your own custom icon, replacing the default icon.png

  * Modify your user interface by opening .ui in Qt Designer

  * You can use the Makefile to compile your Ui and resource files when
    you make changes. This requires GNU make (gmake)

  * Per rimappare le immagini editare in modo adeguato il file "resources.qrc" e poi lanciare da shell:
    pyrcc4 -o resources.py resources.qrc
    ATTENZIONE!! Per QGis 3.x DEVE ESSERE RCIREATO QUESTO FILE:
    pyrcc5 -o resources.py resources.qrc

For more information, see the PyQGIS Developer Cookbook at:
http://www.qgis.org/pyqgis-cookbook/index.html

(C) 2011-2014 GeoApt LLC - geoapt.com
Git revision : $Format:%H$
