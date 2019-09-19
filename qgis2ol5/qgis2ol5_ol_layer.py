# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2ol5_ol_layer
                                 A QGIS plugin
 qgis2ol5
                             -------------------
        begin                : 2019-07-31
        git sha              : $Format:%H$
        copyright            : (C) 2019 by ar_gaeta@yahoo.it
        email                : ar_gaeta@yahoo.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

#LAYER DI BASE pre definiti
global OSM_base
OSM_base = """var OSM_base = new ol.layer.Tile({
    title: "OSM",
    baseLayer: true,
    visible: false,
    source: new ol.source.OSM(
        //{attributionsCollapsible: true}
    )
});"""

global OSM_land
OSM_land = """var OSM_land = new ol.layer.Tile({
    title: "OSM landscape",
    baseLayer: true,
    visible: false,
    source: new ol.source.OSM({
        //attributionsCollapsible: true
        url: 'http://{a-c}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png'
    })
});"""


global ESRI_base
ESRI_base = """var ESRI_base = new ol.layer.Tile({
    title: "ESRI",
    baseLayer: true,
    visible: false,
    source: new ol.source.XYZ({
        attributions: 'Tiles &#169; <a href="https://services.arcgisonline.com/ArcGIS/' +
            'rest/services/World_Topo_Map/MapServer">ArcGIS</a>',
        attributionsCollapsible: true,
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/' +
            'World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
    })
});"""

global ESRI_sat
ESRI_sat = """var ESRI_sat = new ol.layer.Tile({
    title: "ESRI satellite",
    baseLayer: true,
    visible: false,
    source: new ol.source.XYZ({
        attributions: ['Powered by Esri', 'Source: Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community'],
        attributionsCollapsible: true,
        url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        maxZoom: 23
    })
});"""

global Stamen_Toner
Stamen_Toner = """var Stamen_Toner = new ol.layer.Tile({
  title: "Stamen",
  baseLayer: true,
  visible: false,
  source: new ol.source.Stamen({
    layer: 'toner-lite',
    attributionsCollapsible: true
  })
});"""



#TEMPLATE per i layer WMS utente:
global template_wms_utente
template_wms_utente = """var %(ol_layer_variable)s = new ol.layer.Tile({
    title: '%(layertitle)s',
    visible: %(visible)s,
    //zIndex: %(order)s,
    source: new ol.source.TileWMS({
      url: '%(qgis_project_url)s',
      params: {'LAYERS': '%(layername)s', 'TILED': %(tiled)s, 'TRANSPARENT': true},
      transition: 0
    })
});"""
#ho deciso di commentare lo z-index dei layer perche' non permette di cambiarne poi l'ordine di visualizzazione tramite il layerswitcher...

#la variabile poi si compone cosi:
#var1 = template_wms_utente % {'order': order1, 'layertitle': title1, ...etc....}

template_group = """var %(ol_group_variable)s = new ol.layer.Group({
    title: '%(group_title)s',
    //name: ??
    layers: %(group_layer_list)s
});"""



#MAPPA:
mappa_var = """var map = new ol.Map({
  controls: ol.control.defaults({attribution:false}).extend([
    new ol.control.ScaleLine(),
    new ol.control.ZoomSlider(),
    new ol.control.MousePosition(),
    new ol.control.Attribution({collapsible: true}) //a quanto pare OSM sclera e non collassa le attributions...
  ]),
  layers: layers,
  target: 'map',
  view: new ol.View({
    maxZoom: %(maxzoom)s,
    minZoom: %(minzoom)s
  })
});"""

#restrict to extent?
zoom_restrict = """map.setView(
  new ol.View({
    //center: [%(center_x)i, %(center_y)i],
	//zoom: 8, //come prelevarlo da QGis?
    extent: [%(extent)s], //extent dichiarato qui blocca la view. esempio [742433.428457, 5472155.263975, 1026467.713806, 5855286.236467]
	maxZoom: %(maxzoom)s,
    minZoom: %(minzoom)s
  })
);"""

#zoom su vista utente/max layers: in questo modo non serve dichiarare center e zoom
zoom_var = """map.getView().fit([%(extent)s], map.getSize());"""


#CONTROLLI aggiuntivi
other_controls = """var ctrl = new ol.control.LayerSwitcher();
map.addControl(ctrl);
ctrl.on('toggle', function(e) {
    console.log('Collapse layerswitcher', e.collapsed);
}
);"""


