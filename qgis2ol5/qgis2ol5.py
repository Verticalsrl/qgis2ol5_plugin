# -*- coding: utf-8 -*-
from __future__ import print_function

"""
/***************************************************************************
 qgis2ol5
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


'''
DEBUG interfaccia/maschera da consolle python:
import imp
foo = imp.load_source('qgis2ol5Dialog', 'C:\\Users\\riccardo\\.qgis2\\python\\plugins\\qgis2ol5\\qgis2ol5_dialog.py')
dlg=foo.qgis2ol5Dialog()

Pero' non prende i valori!!!



OTTIMIZZAZIONI/DA FARE: ==> alcuni appinti potrebbero NON essere piu' validi nel momento in cui il plugin esporta non piu' il file javascript ma SOLO il JSON

- il layerTree non viene ricostruito, bisogna ricaricare il plugin, altrimenti sotto __init__ la funzione populate_layers_and_groups pare non venga richiamata. Potrebbe venir richiamata sotto "run()", ma in questo modo ricaricherebbe ogni volta il layerTree cancellando le modifiche effettuate...
==> PRENDI SPUNTO DA qgis2web.py!!  --> impossibile da replicare....

- cancellare tutto il precedente codice relativo alla stampa dell'Atlas

- migliorare la gestione dei layer di base: occorre chiedere all'utente quale layer di base vuole visualizzare di default

- I PUNTI non possono essere resi come TILE!!

- SELECT: aggiungerei per ogni layer non esterno la possibilita' di scegliere se interrogarlo o meno (dunque attivare il select o meno), se attivare o meno l'hover (con un'apertura minima del popup cioe' ad esempio solo UN campo). I layer scelti per essere interrogati confluiranno nella variabiale:
var layersList = [baseLayer,lyr_limiti_ammviPG96_0,lyr_limiti_ammviGPKG_1,lyr_risval_istanze_2];

Che potra' dunque essere richiamta copiando il codice da qgis2web.js per l'apertura del popup ad esempio:
if (layersList.indexOf(layer) === -1) {

ATTENZIONE!! nel progetto qgis2web.js i campi vengono tutti buttati nella popup, puoi solo scegliere se mettere il NOME del campo come header oppure inline oppure non mettere il nome del campo, ma il suo valore ci sara' sempre!
Quindi bisogna trovare un modo per escludere i campi che non si vogliono far vedere in popup

--> sempre per l'apertura della popup, estrarre gli alias dei campi definiti sotto QGis in modo da creare la seguente variabile per ogni layer selezionabile:

lyr_RISVAList_0.set('fieldAliases', {...etc...   ---> vedi qgis2web - layers.js

Come viene fatto su qgis2web??
NB: sebbene abbia gia' imbastito i campi per permettere di scegliere quale layer selezionare o hoverare, occhio che qgis2web interroga i GEOJSON e NON i WMS come nel tuo caso.
Potresti comunque copiare la parte in cui assegna uno stile ai GeoJson cioe' sotto layers e sotto styles


#######################################################
INCOMPATIBILITA con Qgis 2.x
Per quanto abbia cercato di renderlo funzionante anche per QGis 2.x ci sono ancora alcune cose che non funzionano:
- l'elenco dei fields per i layer, in particolare il riconoscimento corretto del valore di test_goodlayer, suppongo


'''


#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtGui import QAction, QIcon
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
#recupero la versione di QGis dell'utente:
global qgis_version
try:
    from qgis.core import Qgis #versione qgis 3.x
except ImportError:
    from qgis.core import QGis as Qgis #versione qgis 2.x
qgis_version = Qgis.QGIS_VERSION

from qgis.core import *
from qgis.gui import *
#from qgis.utils import *
import traceback
import json

#import plugin_utils as Utils
#import qgis2ol5.plugin_utils as Utils
from . import plugin_utils as Utils

# Initialize Qt resources from file resources.py
from . import resources
# Import the code for the dialog
from .qgis2ol5_dialog import qgis2ol5Dialog
import os.path
import sys
from collections import defaultdict, OrderedDict


if (int(qgis_version[0]) >= 3):
    #from qgis.PyQt.QtWidgets import QTreeWidgetItem, QAction
    #import PyQt5.QtWidgets
    from qgis.PyQt.QtWidgets import (QAction,
                                 QAbstractItemView,
                                 QDialog,
                                 QHBoxLayout,
                                 QTreeWidgetItem,
                                 QComboBox,
                                 QListWidget,
                                 QCheckBox,
                                 QLineEdit,
                                 QMessageBox,
                                 QToolButton,
                                 QWidget,
                                 QTextBrowser)
    xrange = range
    critical_level = Qgis.Critical
    point_geometry = QgsWkbTypes.PointGeometry
else:
    critical_level = QgsMessageLog.CRITICAL
    point_geometry = QGis.Point


#class qgis2ol5(QDialog, qgis2ol5Dialog):
class qgis2ol5():
    """QGIS Plugin Implementation."""
    
    items = {}

    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        stgs = QSettings()
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'qgis2ol5_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = qgis2ol5Dialog()
                
        #Definisco alcune variabili globali:
        global filename
        filename = None
        global dirname
        dirname = None
        global numero_layers
        numero_layers = None
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&qgis2ol5')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'qgis2ol5')
        self.toolbar.setObjectName(u'qgis2ol5')
        
        #SELEZIONA CARTELLA
        self.dlg.dirBrowse_txt.clear()
        self.dlg.titolo.clear()
        self.dlg.nome.clear()
        self.dlg.dirBrowse_btn.clicked.connect(self.select_output_dir)
        
        #AZIONO PULSANTE PERSONALIZZATO:
        self.dlg.importBtn.clicked.connect(self.esporta_filejs_configurazione)
        
        #compilo la parte riguardante i layers presenti
        #self.populate_layers_and_groups(self) #lo faccio fare solo dal run
        #self.layer_search_combo = None
        #self.populateLayerSearch()
        #self.dlg.layersTree.model().dataChanged.connect(self.populateLayerSearch)
        
        
    #--------------------------------------------------------------------------

            
    def esporta_filejs_configurazione(self):
        self.dlg.export_progressBar.setValue(0)
        #self.dlg.export_progressBar.setMaximum(len(self.LAYER_NAME_PNI))
        self.dlg.txtFeedback.setText("Sto esportando la configurazione, non interrompere, il processo potrebbe richiedere alcuni minuti...")
        #Controllo che tutti i campi siano compilati prima di procedere:
        msg = QMessageBox()
        try:
            nome = self.dlg.nome.text()
            titolo = self.dlg.titolo.text()
            dirname_text = self.dlg.dirBrowse_txt.text()         
            if ( (dirname_text is None) or (nome is None) or (titolo is None) or (dirname_text=='') or (nome=='') or (titolo=='') ):
                raise NameError('Specificare nome e titolo del progetto e il percorso in cui salvare il file JS di configurazione!')            
        except NameError as err:
            msg.setText(err.args[0])
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()
            self.dlg.txtFeedback.setText(err.args[0])
            return 0
        except ValueError:
            self.dlg.txtFeedback.setText('Specificare TUTTE le variabili')
            return 0
        except SystemError as e:
            Utils.logMessage('Errore di sistema!')
            self.dlg.txtFeedback.setText('Errore di sistema!')
            return 0
        else: #...se tutto ok proseguo:
            pathfile = dirname_text + '/' + nome + '.json'
            if (os.path.exists(pathfile) and  os.path.isfile(pathfile)):
                msg.setText("ATTENZIONE! Il file indicato per l'esportazione e' gia' presente su disco: si desidera sovrascriverlo?")
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Sovrascrivere il file " + pathfile + "?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                retval = msg.exec_()
                if (retval != 16384): #l'utente NON ha cliccato yes: sceglie di fermarsi, esco
                    self.dlg.txtFeedback.setText("...azione di esportazione interrotta dall'utente...")
                    return 0
                elif (retval == 16384): #l'utente HA CLICCATO YES. Esporto un file js
                    self.esporta_json(pathfile)
            else:
                self.esporta_json(pathfile)
        
            #presumo che fin qui sia andato tutto bene?
            self.dlg.export_progressBar.setValue(100)
            self.dlg.txtFeedback.setText("Esportazione completata!")
    
    def count_layers_in_TOC(self, TOC):
        #layers_in_TOC = [] deve essere definito prima di richiamare questa funzione come global
        for child in TOC.children():
            if isinstance(child, QgsLayerTreeLayer):
                #print child.layer().name()
                layers_in_TOC.append(child.layer().name())
            else:
                layers_in_TOC.append(child.name()) #aggiungo anche eventuale gruppo a questa lista
                self.count_layers_in_TOC(child)
    
    def esporta_json(self, pathfile):
        #Utils.logMessage('numero di layer da configurare: ' + str(self.dlg.layersTree.topLevelItemCount())) #da un numero scorretto
        root = QgsProject.instance().layerTreeRoot()
        #tree_layers = root.findLayers() #questo metodo recupera SOLO i layers, NON i gruppi
        global layers_in_TOC
        layers_in_TOC = []
        self.count_layers_in_TOC(root)
        Utils.logMessage('numero di layer da TOC: ' + str(len(layers_in_TOC)))
        Utils.logMessage('ordine layer da TOC: ' + str(layers_in_TOC))
        #NB: la variabile "layers_in_TOC" e' una lista con i layer e gruppi in ordine cosi come sono nella TOC, ma per OpenLayers quest'ordine deve essere ribaltato!
        #la lista si ribalta con "layers_in_TOC[::-1]"
        
        (layers, groups, popup, visible, jsons, cluster, getFeatureInfo, layers_to_load) = self.getLayersAndGroups()
        #Utils.logMessage('numero di layer da configurare: ' + str(len(layers)))
        #in realta anche questo numero e' scorretto. Occorre risalire direttamente alla TOC di QGis e fare riferimento ad essa per il numero e l'ordine dei layer
        Utils.logMessage('numero di gruppi da configurare? ' + str(len(groups)))
        
        qgis_project_url = self.dlg.qgis_project_url.text() + project_name + '.qgs'
        
        #cerco di recuperare le info utili per costruire il js dal mio dict layers_to_load e dalle opzioni spuntate
        #import qgis2ol5_ol_layer #qgis 2.x
        from . import qgis2ol5_ol_layer #qgis 3.x
        js_page_list = []
        #recupero il numero di gruppi presenti:
        num_gruppi = len(groups)
        if (int(qgis_version[0]) >= 3):
            #recupero il numero di layer contenuti nei gruppi:
            num_layer_in_gruppo = len({k: v for k, v in layers_to_load.items() if v['group'] == True })
            #ora dovrei riuscire a TOGLIERE da layers_in_TOC quei layers che sono nei gruppi, per calcolarmi correttamente gli indici e costruire una valida lista layers_sciolti
            layers_in_gruppo_dict = {k: v for k, v in layers_to_load.items() if v['group'] == True }
            layers_in_gruppo = list( {v['title'] for k, v in layers_to_load.items() if v['group'] == True } )
            Utils.logMessage("layers_in_gruppo: " + str( layers_in_gruppo ))
            #adesso tolgo questi layers_in_gruppo da layers_in_TOC:
            layers_in_TOC_sciolti = [x for x in layers_in_TOC if x not in list(layers_in_gruppo)]
            #recupero il numero dei layer "sciolti":
            num_layer_sciolti = len({k: v for k, v in layers_to_load.items() if v['group'] == False })

            #creo la variabile contenente tutti i layers "sciolti" e i gruppi:
            layers_sciolti = [None] * len(layers_in_TOC_sciolti)
        
            #compongo le variabili contenenti i layer da selezionare e sui quali attivare l'hover:
            layers_to_select = list( {v['name'] for k, v in layers_to_load.items() if v['select'] == True } )
            layers_to_hover = list( {v['name'] for k, v in layers_to_load.items() if v['hover'] == True } )
        else: #QGis 2.x
            #recupero il numero di layer contenuti nei gruppi:
            num_layer_in_gruppo = len({k: v for k, v in layers_to_load.iteritems() if v['group'] == True })
            #ora dovrei riuscire a TOGLIERE da layers_in_TOC quei layers che sono nei gruppi, per calcolarmi correttamente gli indici e costruire una valida lista layers_sciolti
            layers_in_gruppo_dict = {k: v for k, v in layers_to_load.iteritems() if v['group'] == True }
            layers_in_gruppo = list( {v['title'] for k, v in layers_to_load.iteritems() if v['group'] == True } )
            Utils.logMessage("layers_in_gruppo: " + str( layers_in_gruppo ))
            #adesso tolgo questi layers_in_gruppo da layers_in_TOC:
            layers_in_TOC_sciolti = [x for x in layers_in_TOC if x not in list(layers_in_gruppo)]
            #recupero il numero dei layer "sciolti":
            num_layer_sciolti = len({k: v for k, v in layers_to_load.iteritems() if v['group'] == False })

            #creo la variabile contenente tutti i layers "sciolti" e i gruppi:
            layers_sciolti = [None] * len(layers_in_TOC_sciolti)

            #compongo le variabili contenenti i layer da selezionare e sui quali attivare l'hover:
            layers_to_select = list( {v['name'] for k, v in layers_to_load.iteritems() if v['select'] == True } )
            layers_to_hover = list( {v['name'] for k, v in layers_to_load.iteritems() if v['hover'] == True } )

        
        Utils.logMessage('contenuto lista layers_in_TOC: ' + str(layers_in_TOC))
        Utils.logMessage('contenuto lista layers_in_TOC_sciolti: ' + str(layers_in_TOC_sciolti))
        for key,val in layers_to_load.items():
            #var_layer = qgis2ol5_ol_layer.template_wms_utente % {'order': val['order'], 'layertitle': val['title'], 'ol_layer_variable': key, 'layername': val['title'], 'qgis_project_url': '/wms/'+project_name+'?', 'visible': str(val['visible']).lower(), 'tiled': str(val['tiled']).lower()}
            #cambiando macchina, su Ubuntu ho visto che non riesco a redirigiere l'url sul percorso /var/www/wms. Quindi devo indicare per esteso il percorso del progetto qgs:
            var_layer = qgis2ol5_ol_layer.template_wms_utente % {'order': val['order'], 'layertitle': val['title'], 'ol_layer_variable': key, 'layername': val['title'], 'qgis_project_url': qgis_project_url, 'visible': str(val['visible']).lower(), 'tiled': str(val['tiled']).lower()}
            #mi sa che per QGis anche come layername vuole il title cioe' il nome con cui il layer e' indicato nella TOC. Penso che usero' il name solo per dare un nome alla variabile javascript
            js_page_list.append(var_layer)
            #verifico se il layer e' in un gruppo o meno:
            if (val['group'] == False):
                #inserisco il layer nella lista secondo la posizione specificata nella TOC di QGis
                #layers_sciolti.append(key)
                Utils.logMessage("indice del layer " + str(layers_in_TOC_sciolti[::-1].index(val['title'])))
                indice_corretto = layers_in_TOC_sciolti[::-1].index(val['title'])
                layers_sciolti.insert( indice_corretto, key)
            
        #ora creo l'eventuale gruppo:
        for key,val in groups.items():
            #val e' la lista dei layer contenuti nel gruppo, la converto in stringa:
            #val_list_encoded = (str([x.encode('UTF8') for x in val])).replace("'", "") #qgis 2.x
            val_list_encoded =('['+ ', '.join(val).replace("'", "") + ']')

            var_group = qgis2ol5_ol_layer.template_group % {'ol_group_variable': self.convert_string_to_valid_filename(key), 'group_title': key, 'group_layer_list': val_list_encoded}
            js_page_list.append(var_group)
            #appendo il nome del gruppo alla lista dei layers da caricare in mappa secondo la posizione specificata nella TOC di QGis
            #layers_sciolti.append(self.convert_string_to_valid_filename(key))
            indice_corretto = layers_in_TOC_sciolti[::-1].index(key)
            layers_sciolti.insert( indice_corretto, self.convert_string_to_valid_filename(key))
        
        #tolgo ora dalla lista layers_sciolti eventuali valori rimasti None:
        layers_sciolti = [x for x in layers_sciolti if x != None]
        
        #carico i layer di BASE - DA IMPLEMENTARE SECONDO LE SCELTE DELL'UTENTE!!!
        #inserisco all'inizio della lista layers_sciolti i layer di BASE
        base_layers = []
        osm_base = self.dlg.osm_base.isChecked()
        if (osm_base==True):
            js_page_list.append(qgis2ol5_ol_layer.OSM_base)
            layers_sciolti.insert(0, 'OSM_base')
            base_layers.append('OSM_base')
        osm_land = self.dlg.osm_land.isChecked()
        if (osm_land==True):
            js_page_list.append(qgis2ol5_ol_layer.OSM_land)
            layers_sciolti.insert(0, 'OSM_land')
            base_layers.append('OSM_land')
        osm_gray = self.dlg.osm_gray.isChecked()
        if (osm_gray==True):
            js_page_list.append(qgis2ol5_ol_layer.Stamen_Toner)
            layers_sciolti.insert(0, 'Stamen_Toner')
            base_layers.append('Stamen_Toner')
        esri_base = self.dlg.esri_base.isChecked()
        if (esri_base==True):
            js_page_list.append(qgis2ol5_ol_layer.ESRI_base)
            layers_sciolti.insert(0, 'ESRI_base')
            base_layers.append('ESRI_base')
        esri_sat = self.dlg.esri_sat.isChecked()
        if (esri_sat==True):
            js_page_list.append(qgis2ol5_ol_layer.ESRI_sat)
            layers_sciolti.insert(0, 'ESRI_sat')
            base_layers.append('ESRI_sat')
        
        #creo la variabile contenente tutti i layers "sciolti":
        #js_page_list.append("var layers = %s;" % ( (str([x.encode('UTF8') for x in layers_sciolti])).replace("'", "") )) #qgis 2.x
        #js_page_list.append("var layers_to_select = %s;" % ( (str([x.encode('UTF8') for x in layers_to_select])).replace("'", "") )) #qgis 2.x
        #js_page_list.append("var layers_to_hover = %s;" % ( (str([x.encode('UTF8') for x in layers_to_hover])).replace("'", "") )) #qgis 2.x
        js_page_list.append("var layers = %s;" % ( ('['+ ', '.join(layers_sciolti).replace("'", "") + ']') ))
        js_page_list.append("var layers_to_select = %s;" % ( ('['+ ', '.join(layers_to_select).replace("'", "") + ']') ))
        js_page_list.append("var layers_to_hover = %s;" % ( ('['+ ', '.join(layers_to_hover).replace("'", "") + ']') ))
        
        #prelevo l'estensione del canvas o la massima estensione del progetto?
        extent_var = self.dlg.extent_comboBox.currentText()
        self.iface.mapCanvas().setDestinationCrs(QgsCoordinateReferenceSystem(3857)) #converto tutto in 3857
        if (extent_var=='Fit to layers extent'):
            canvas_extent_tuple = self.iface.mapCanvas().fullExtent().toRectF().getCoords()
        elif (extent_var=='Canvas extent'):
            canvas_extent_tuple = self.iface.mapCanvas().extent().toRectF().getCoords()
        canvas_extent = str(canvas_extent_tuple)[1:-1]
        canvas_center = self.iface.mapCanvas().center()
        canvas_center_x = canvas_center.x()
        canvas_center_y = canvas_center.y()

        mappa_var_compilata = qgis2ol5_ol_layer.mappa_var % {'maxzoom': self.dlg.maxzoom_comboBox.currentText(), 'minzoom': self.dlg.minzoom_comboBox.currentText(), 'extent': canvas_extent, 'center_x': canvas_center_x, 'center_y': canvas_center_y }
        js_page_list.append(mappa_var_compilata)
        
        restricted = False
        restrict_extent = self.dlg.restrict_extent.isChecked()
        if (restrict_extent==True):
            zoom_restrict_compilata = qgis2ol5_ol_layer.zoom_restrict % { 'maxzoom': self.dlg.maxzoom_comboBox.currentText(), 'minzoom': self.dlg.minzoom_comboBox.currentText(), 'extent': canvas_extent, 'center_x': canvas_center_x, 'center_y': canvas_center_y }
            js_page_list.append(zoom_restrict_compilata)
            restricted = True
            
        map_var = {'maxzoom': self.dlg.maxzoom_comboBox.currentText(), 'minzoom': self.dlg.minzoom_comboBox.currentText(), 'extent': canvas_extent, 'center_x': canvas_center_x, 'center_y': canvas_center_y, 'restrict_extent': restricted } #creo un dictionary per json

        zoom_var_compilata = qgis2ol5_ol_layer.zoom_var % { 'extent': canvas_extent }
        js_page_list.append(zoom_var_compilata)        
        js_page_list.append(qgis2ol5_ol_layer.other_controls)
        
        #infine per impostare l'estensione e bloccarla, nel caso l'utente abbia scelto questo - in realta pare serva solo a settare lo zoom: come fissare invece che la finestra non vada oltre un estensione specificata??
        #map.getView().fit([444760.314632, 3985344.906749, 2348245.938683, 6567388.279622], map.getSize());

        
        #js_page_string = '\n'.join(js_page_list) #contiene dei caratteri strani?
        #for el in js_page_list: 
        #    Utils.logMessage( str(el) )
        js_page_string = '\n'.join(map(str, js_page_list))
        
        
        '''
        #contenuto delle varie variabili estratte dalla funzione getLayersAndGroups
        #layers e' una lista di QgsVectorLayer
        for layer in layers: 
            Utils.logMessage( layer.name() )
        #groups e' un dict di QgsVectorLayer, nome del gruppo e forse altre info su visibilita e altro?
        for key,val in groups.items():
            if type(val) is list:
                for v in val:
                    Utils.logMessage( key + "=>" + str(v))
            else:
                Utils.logMessage( key + "=>" + val)
        #popup e' una lista di dictionary
        #for pop in popup:
        #    for key,val in pop.items():
        #        Utils.logMessage( key + "=>" + val)
        #visible e' una lista di valori booleani
        for vis in visible:
            Utils.logMessage( str(vis) )
        #json e' una lista di valori booleani
        for js in jsons:
            Utils.logMessage( str(js) )
        #cluster e' una lista di valori booleani
        for clust in cluster:
            Utils.logMessage( str(clust) )
        #getFeatureInfo e' una lista di valori booleani
        for info in getFeatureInfo:
            Utils.logMessage( str(info) )
        '''
        
        #PER SCRIVERE IL FILE RICORDA:
        #1-controllare che il file non esista e se si chiedere conferma all'utente
        #2-nel JSON mancano info su: controlli mappa...
        
        #io ho raccolto tutte queste informazioni in un singolo dictionary:
        j = json.dumps(layers_to_load, indent=4)
        f = open(pathfile, 'w')
        #f.write("layers_to_load = ") #da indicazioni di MOCCO scrivo solo un json
        f.write('{"layers_to_load":')
        if (int(qgis_version[0]) >= 3):
            print(j, end="", file=f)
        else:
            #print >> f, j #importando from __future__ import print_function questa funzione non vale piu' nemmeno per QGis 2.x
            print(j, end="", file=f)
        f.write("\n")
        #f.close()
        
        j = json.dumps(groups, indent=4)
        #f = open(pathfile, 'a')
        #f.write("groups = ") #da indicazioni di MOCCO scrivo solo un json
        f.write(',"groups":')
        if (int(qgis_version[0]) >= 3):
            print(j, end="", file=f)
        else:
            #print >> f, j
            print(j, end="", file=f)
        f.write("\n")
        #f.close()

        f.write(',"qgis_project_url":"'+qgis_project_url+'"')
        f.write("\n")
        
        j = json.dumps(base_layers, indent=4)
        f.write(',"base_layers":')
        if (int(qgis_version[0]) >= 3):
            print(j, end="", file=f)
        else:
            #print >> f, j
            print(j, end="", file=f)
        f.write("\n")

        j = json.dumps(map_var, indent=4)
        f.write(',"map":')
        if (int(qgis_version[0]) >= 3):
            print(j, end="", file=f)
        else:
            #print >> f, j
            print(j, end="", file=f)
        f.write("\n")

        f.write("}") #chiudo il json

        #f.write(js_page_string) #da indicazioni di MOCCO scrivo solo un json
        f.close()
        
    
    def select_output_dir(self):
        dirname = QFileDialog.getExistingDirectory(self.dlg, "Open source directory","", QFileDialog.ShowDirsOnly)
        self.dlg.dirBrowse_txt.setText(dirname)
    
    def activate_export(self):
        #Verifico che alcune condizioni siano rispettate per abilitire il pulsante di esportazione:
        #filename = self.dlg.fileBrowse_txt.text()
        Utils.logMessage("filename: " + str(filename))
        filtro_check = self.dlg.filter_atlas_txt.toPlainText()
        radiocheck_pdf = self.dlg.radio_pdf.isChecked()
        radiocheck_png = self.dlg.radio_png.isChecked()
        if (filename and filtro_check and (radiocheck_pdf or radiocheck_png) ):
            self.dlg.atlas_btn.setEnabled(True);
        else:
            self.dlg.atlas_btn.setEnabled(False);
    
    def select_output_file(self):
        global filename
        filename = QFileDialog.getSaveFileName(self.dlg, "Save file", "", "*")
        #Altre opzioni QFileDialog:
        #filename = QFileDialog.getOpenFileName(self.dlg, "Load PNG file","", '*.png')
        #dirname = QFileDialog.getExistingDirectory(self.dlg, "Open output directory","", QFileDialog.ShowDirsOnly)
        self.dlg.fileBrowse_txt.setText(filename)
        self.activate_export() #controllo che l'atlante abbia un filtro e che sia stato scelto il nome del file e il tipo di file. allora abilito il pulsante di esportazione

    def get_field_type(self):
        if not(layer_da_filtrare):
            return 0
        field_da_filtrare = self.dlg.combo_fields.currentText()
        idx_field = layer_da_filtrare.fields().indexFromName(field_da_filtrare)
        if (idx_field == -1): #al cambio di combobox non riconosce subito l'indice del campo
            return 0
        type_field = layer_da_filtrare.fields().field(idx_field).typeName()
        Utils.logMessage("idx field: " + str(type_field))
        self.dlg.field_type.setText(str(type_field))
        
    def convert_string_to_valid_filename(self, string_input):
        keepcharacters = ('.','_')
        return "".join(c for c in string_input if c.isalnum() or c in keepcharacters).rstrip()
        
        
        
    #--------------------------------------------------------------------------

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('qgis2ol5', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action
        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qgis2ol5/qgis2ol5.png'
        self.add_action(
            icon_path,
            text=self.tr(u'qgis2ol5'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            #self.iface.removePluginDatabaseMenu(
            self.iface.removePluginMenu(
                self.tr(u'&qgis2ol5'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        #print "** CLOSING Core"
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        # remove this statement if dockwidget is to remain for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe when closing the docked window:
        # self.dockwidget = None
        self.pluginIsActive = False
        
    def populateLayerSearch(self):
        self.layer_search_combo.clear()
        self.layer_search_combo.addItem("None")
        (layers, groups, popup, visible,
         json, cluster, getFeatureInfo, layers_to_load) = self.getLayersAndGroups()
        for count, layer in enumerate(layers):
            if layer.type() == layer.VectorLayer:
                options = []
                fields = layer.pendingFields()
                for f in fields:
                    fieldIndex = fields.indexFromName(unicode(f.name()))
                    formCnf = layer.editFormConfig()
                    editorWidget = formCnf.widgetType(fieldIndex)
                    if editorWidget == QgsVectorLayer.Hidden \
                            or editorWidget == 'Hidden':
                        continue
                    options.append(unicode(f.name()))
                for option in options:
                    displayStr = unicode(layer.name() + ": " + option)
                    self.layer_search_combo.insertItem(0, displayStr)
                    sln = utils.safeName(layer.name())
                    self.layer_search_combo.setItemData(
                        self.layer_search_combo.findText(displayStr),
                        sln + "_" + unicode(count))
    
    def populate_layers_and_groups(self, dlg):
        """Populate layers on QGIS into our layers and group tree view."""
        root_node = QgsProject.instance().layerTreeRoot()
        tree_groups = []
        tree_layers = root_node.findLayers() #questo metodo recupera SOLO i layers, NON i gruppi
        self.layers_item = QTreeWidgetItem()
        self.groups_item = QTreeWidgetItem()
        self.layers_item.setText(0, "Layers and Groups")
        self.dlg.layersTree.setColumnCount(3)
        msg = QMessageBox()

        numero_layers = len(tree_layers)
        #qui inizio a prendere un layer alla volta e a costruirgli il form da configurare
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            #Utils.logMessage("layer name: " + layer.name())
            #if (layer.type() != QgsMapLayer.PluginLayer and layer.customProperty("ol_layer_type") is None):
            if (int(qgis_version[0]) >= 3):
                test_goodlayer = (layer.type() != QgsMapLayer.PluginLayer and
                    (layer.type() != QgsMapLayer.VectorLayer or
                     layer.wkbType() != QgsWkbTypes.NoGeometry) and
                    layer.customProperty("ol_layer_type") is None)
            else:
                test_goodlayer = (layer.type() != QgsMapLayer.PluginLayer and layer.customProperty("ol_layer_type") is None)
            if test_goodlayer:
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        #Utils.logMessage("layer type: vector!")
                        if (int(qgis_version[0]) >= 3):
                            testDump = layer.renderer().dump()
                        else:
                            testDump = layer.rendererV2().dump()
                    #Utils.logMessage("layer parent: " + str(layer.parent()))
                    layer_parent = tree_layer.parent()
                    if layer_parent.parent() is None:
                        item = TreeLayerItem(self.iface, layer, self.dlg.layersTree, dlg)
                        self.layers_item.addChild(item)
                    else:
                        if layer_parent not in tree_groups: #sposta il parent del layer all'interno dei gruppi se ancora non c'e'
                            tree_groups.append(layer_parent)
                except:
                    #QgsMessageLog.logMessage(traceback.format_exc(), "qgis2ol5", level=QgsMessageLog.CRITICAL)
                    QgsMessageLog.logMessage(traceback.format_exc(), "qgis2ol5", level=critical_level)

        #costruisco l'albero dei gruppi
        check_gruppo_annidato = 0
        for tree_group in tree_groups:
            group_name = tree_group.name()
            #cerco se all'interno di questo gruppo non vi sia un altro gruppo OVVERO ciclo all'interno dei suoi layer nel caso vi siano dei layer che ppartengono al gruppo annidato:
            group_layers = [] #in questo caso la lista la costruisco io
            for layeringroup in tree_group.findLayers():
                if layeringroup.parent().name() == group_name:
                    group_layers.append(layeringroup.layer())
                else:
                    Utils.logMessage("ATTENZIONE! Il gruppo " + group_name + " contiene il gruppo " + layeringroup.parent().name())
                    check_gruppo_annidato = 1
            #group_layers = [tree_layer.layer() for tree_layer in tree_group.findLayers()] #questo metodo findLayers NON VA BENE nel caso in cui vi siano dei gruppi dentro altri gruppi!
            Utils.logMessage("layer nei gruppi: " + str(len(group_layers)))
            #a differenza del plugin qgis2web anche all'interno dei gruppi faccio scegliere l'opzione sui singoli layers:
            item = TreeGroupItem(group_name, group_layers, self.dlg.layersTree, self.iface, dlg)
            self.layers_item.addChild(item)
        if (check_gruppo_annidato==1):
            msg.setText("ATTENZIONE! E' stata rilevata la presenza di gruppi annidati in altri gruppi\nI gruppi annidati potrebbero creare dei problemi in una corretta resa del progetto via Web.\nVerificare che l'albero dei layer in 'Opzioni layers' venga compilato correttamente.")
            msg.setWindowTitle("Gruppi annidati")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

        self.dlg.layersTree.addTopLevelItem(self.layers_item)
        self.dlg.layersTree.expandAll()
        self.dlg.layersTree.resizeColumnToContents(0)
        self.dlg.layersTree.resizeColumnToContents(1)
        #in questo ciclo for entro dentro i vari child ovvero nei singoli layer
        for i in xrange(self.layers_item.childCount()):
            item = self.layers_item.child(i)
            #questo if espande tutti i layer tranne quelli non accesi
            #if item.checkState(0) != Qt.Checked:
            #    item.setExpanded(False)
            #io pero' li voglio tutti collapsed:
            item.setExpanded(False)
    
    def get_layers_custom_order(self):
        bridge = self.iface.layerTreeCanvasBridge() 
        if (int(qgis_version[0]) >= 3):
            if (bridge.rootGroup().hasCustomLayerOrder()):
                QgsVectorLayer_type = bridge.rootGroup().customLayerOrder()
            else:
                QgsVectorLayer_type = bridge.rootGroup().layerOrder()
            layers_id_order = []
            for el in QgsVectorLayer_type:
                layers_id_order.append(el.id())
            return layers_id_order
        else:
            if (bridge.hasCustomLayerOrder()):
                return bridge.customLayerOrder()
            else:
                return bridge.defaultLayerOrder()
        #converto questa lista unicode in stringa:
        #layers_custom_order = [str(r) for r in layers_custom_order]
        #Utils.logMessage('ordine layer custom 1: ' + str(layers_custom_order))
    
    def getLayersAndGroups(self):
        layers = []
        groups = {}
        popup = []
        visible = []
        json = []
        cluster = []
        getFeatureInfo = []
        layers_to_load = dict() #mio dizionario
        layer_in_gruppo_da_non_esportare = []
        #se esiste, prelevo l'ordine custom dell'utente
        global layers_custom_order
        #layers_custom_order = []
        layers_custom_order = self.get_layers_custom_order()
        Utils.logMessage('ordine layer custom 2: ' + str(layers_custom_order))
        for i in xrange(self.layers_item.childCount()):
            item = self.layers_item.child(i)
            if isinstance(item, TreeLayerItem): #qui analizzo i layer
                if item.checkState(0) == Qt.Checked: #recupero solo quei layer che l'utente ha deciso di esportare
                    layers.append(item.layer)
                    popup.append(item.popup)
                    visible.append(item.visible)
                    json.append(item.json)
                    cluster.append(item.cluster)
                    getFeatureInfo.append(item.getFeatureInfo)
                    
                    #provo a compilare il mio dizionario
                    #le definizioni item.XXXXX pare prenderle da @property def XXXXX piu' oltre nel codice
                    layername_unique = self.convert_string_to_valid_filename((item.layer.name()).lower() + str(i))
                    layers_to_load[layername_unique] = dict()
                    layers_to_load[layername_unique]['title'] = item.layer.name()
                    layers_to_load[layername_unique]['name'] = layername_unique
                    layers_to_load[layername_unique]['popup'] = item.popup
                    layers_to_load[layername_unique]['visible'] = item.visible
                    layers_to_load[layername_unique]['group'] = False
                    layers_to_load[layername_unique]['json'] = item.json
                    layers_to_load[layername_unique]['cluster'] = item.cluster
                    layers_to_load[layername_unique]['getFeatureInfo'] = item.getFeatureInfo
                    layers_to_load[layername_unique]['refresh'] = item.refresh
                    layers_to_load[layername_unique]['tiled'] = item.tiled
                    layers_to_load[layername_unique]['select'] = item.select
                    layers_to_load[layername_unique]['hover'] = item.hover
                    #layers_to_load[layername_unique]['order'] = layers_in_TOC[::-1].index(item.layer.name())
                    #in layers_custom_order il nome del layer viene salvato con un suffisso, forse per renderlo univoco. Devo quindi fare un trucchetto per ritrovare i miei layer: recupero ID del layer invece che il nome
                    layers_to_load[layername_unique]['order'] = layers_custom_order[::-1].index(item.layer.id())
            else: #qui (forse) analizzo i gruppi
                #devo cercare di prendere i child del gruppo:
                Utils.logMessage( "Numero di layer dentro al gruppo: " + str(item.childCount()) ) #non e' corretto!
                #ripeto un po quanto fatto prima sui singoli layer
                for ii in xrange(item.childCount()):
                    subitem = item.child(ii)
                    if isinstance(subitem, TreeLayerItem):
                        if subitem.checkState(0) == Qt.Checked: #recupero solo quei layer che l'utente ha deciso di esportare
                            layers.append(subitem.layer)
                            popup.append(subitem.popup)
                            visible.append(subitem.visible)
                            json.append(subitem.json)
                            cluster.append(subitem.cluster)
                            getFeatureInfo.append(subitem.getFeatureInfo)
                            
                            #provo a compilare il mio dizionario
                            layername_unique = self.convert_string_to_valid_filename((subitem.layer.name()).lower() + str(i))
                            layers_to_load[layername_unique] = dict()
                            layers_to_load[layername_unique]['title'] = subitem.layer.name()
                            layers_to_load[layername_unique]['name'] = layername_unique
                            layers_to_load[layername_unique]['popup'] = subitem.popup
                            layers_to_load[layername_unique]['visible'] = subitem.visible
                            layers_to_load[layername_unique]['group'] = True
                            layers_to_load[layername_unique]['json'] = subitem.json
                            layers_to_load[layername_unique]['cluster'] = subitem.cluster
                            layers_to_load[layername_unique]['getFeatureInfo'] = subitem.getFeatureInfo
                            layers_to_load[layername_unique]['refresh'] = subitem.refresh
                            layers_to_load[layername_unique]['tiled'] = subitem.tiled
                            layers_to_load[layername_unique]['select'] = subitem.select
                            layers_to_load[layername_unique]['hover'] = subitem.hover
                            #layers_to_load[layername_unique]['order'] = layers_in_TOC[::-1].index(subitem.layer.name())
                            #in layers_custom_order il nome del layer viene salvato con un suffisso, forse per renderlo univoco. Devo quindi fare un trucchetto per ritrovare i miei layer: recupero ID del layer invece che il nome
                            layers_to_load[layername_unique]['order'] = layers_custom_order[::-1].index(subitem.layer.id())
                        else: #questi sono i layer DENTRO ad un GRUPPO che l'utente ha scelto di NON esportare: li tengo da parte cosi' da toglierli dalla lista dei layers contenuti nei gruppi
                            layer_in_gruppo_da_non_esportare.append(subitem.layer.id())
                
                group = item.name
                groupLayers = []
                if item.checkState(0) != Qt.Checked: #se ho deciso di NON esportare il gruppo lo salto
                    continue
                for layer in item.layers: #questi sono i layers contenuti nel gruppo in questione
                    #groupLayers.append(layer)
                    if (layer.id() in layer_in_gruppo_da_non_esportare): #escludo dal gruppo i layer che ho deciso di non esportare
                        continue
                    layers.append(layer)
                    #prelevo il nome del layer in modo che sia uguale al layer definito in layers_to_load
                    #groupLayers.append(layer.name())
                    layername_unique = self.convert_string_to_valid_filename((layer.name()).lower() + str(i))
                    groupLayers.append(layername_unique)
                    popup.append({})
                    if item.visible:
                        visible.append(True)
                    else:
                        visible.append(False)
                    if hasattr(item, "json") and item.json:
                        json.append(True)
                    else:
                        json.append(False)
                    if hasattr(item, "cluster") and item.cluster:
                        cluster.append(True)
                    else:
                        cluster.append(False)
                    if hasattr(item, "getFeatureInfo") and item.getFeatureInfo:
                        getFeatureInfo.append(True)
                    else:
                        getFeatureInfo.append(False)
                    
                groups[group] = groupLayers[::-1]

        return (layers[::-1],
                groups,
                popup[::-1],
                visible[::-1],
                json[::-1],
                cluster[::-1],
                getFeatureInfo[::-1],
                layers_to_load)

    
    def clean_elements(self):
        #All'apertura della finestra ripulisco eventuali tracce precedenti:
        self.dlg.combo_layer.clear()
        self.dlg.combo_fields.clear()
        self.dlg.filter_txt.clear()
        self.dlg.fileBrowse_txt.clear()
        self.dlg.pageBar.setValue(0)
        self.dlg.field_type.setText('field type')
        self.dlg.atlas_ckbox.setChecked(False)
        
        self.dlg.buttonGroup.setExclusive(False);
        self.dlg.radio_png.setChecked(False)
        self.dlg.radio_pdf.setChecked(False)
        self.dlg.buttonGroup.setExclusive(True);
    
    def run(self):
        #Se ho aggiunto il Dock, riporto il self.dlg al Dialog:
        #self.dlg = qgis2ol5Dialog()
        
        #All'apertura della finestra ripulisco eventuali tracce precedenti:
        #self.clean_elements()
        
        #Inizializzo i layer presenti in mappa:
        #self.inizializza_layer()

        global project_name
        project_name = None
        #recupero il nome del progetto qgs per precompilare alcuni campi
        prjfi = QFileInfo(QgsProject.instance().fileName())
        dirname = prjfi.absolutePath()
        project_name = prjfi.baseName()
        self.dlg.dirBrowse_txt.setText(dirname)
        self.dlg.titolo.setText(project_name)
        self.dlg.nome.setText(project_name)
        
        #pulisco la barra di progressione e l'area di testo per il feedback:
        self.dlg.export_progressBar.setValue(0)
        self.dlg.txtFeedback.clear()
        
        #Ricarico il tree dei layer
        self.dlg.layersTree.clear() #in questo modo pero ogni volta perdi tutte le modifiche!
        self.populate_layers_and_groups(self)
        
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # bring to front
        self.dlg.raise_()
        # Run the dialog event loop
        '''result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass'''


class TreeGroupItem(QTreeWidgetItem):
    groupIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "group.gif"))

    def __init__(self, name, layers, tree, parent_iface, parent_dlg):
        QTreeWidgetItem.__init__(self)
        tree_groups_2nd_level = []
        self.layers = layers
        self.name = name
        self.setText(0, name)
        self.setIcon(0, self.groupIcon)
        self.setCheckState(0, Qt.Checked)
        self.visibleItem = QTreeWidgetItem(self)
        self.visibleCheck = QCheckBox()
        self.visibleCheck.setChecked(True)
        self.visibleItem.setText(0, "Group visibility")
        self.addChild(self.visibleItem)
        tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)
        
        #provo ad aggiungere anche i singoli layer all'interno del gruppo:
        for group_layer in layers:
            Utils.logMessage("Nome layer nel gruppo: " + str(group_layer.name()))
            layer = group_layer
            #if (layer.type() != QgsMapLayer.PluginLayer and layer.customProperty("ol_layer_type") is None):
            if (int(qgis_version[0]) >= 3):
                test_goodlayer = (layer.type() != QgsMapLayer.PluginLayer and
                    (layer.type() != QgsMapLayer.VectorLayer or
                     layer.wkbType() != QgsWkbTypes.NoGeometry) and
                    layer.customProperty("ol_layer_type") is None)
            else:
                test_goodlayer = (layer.type() != QgsMapLayer.PluginLayer and layer.customProperty("ol_layer_type") is None)
            if test_goodlayer:
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        if (int(qgis_version[0]) >= 3):
                            testDump = layer.renderer().dump()
                        else:
                            testDump = layer.rendererV2().dump()
                    layer_parent = group_layer.parent()
                    #in QGis3 preleva come parent anche il progetto QgsProject. Devo dunque distinguere questo oggetto da QObject, che invece individua un layer
                    if ( (layer_parent.parent() is None) or ('QObject' not in str(type(layer_parent.parent())))  ):
                        item = TreeLayerItem(parent_iface, layer, tree, parent_dlg)
                        self.addChild(item)
                    else:
                        if layer_parent not in tree_groups_2nd_level: #sposta il layer all'interno del gruppo
                            #tree_groups_2nd_level.append(layer_parent)
                            Utils.logMessage("ATTENZIONE! C'e' un gruppo dentro il gruppo: non e' gestito!")
                except:
                    #QgsMessageLog.logMessage(traceback.format_exc(), "qgis2ol5", level=QgsMessageLog.CRITICAL)
                    QgsMessageLog.logMessage(traceback.format_exc(), "qgis2ol5", level=critical_level)

    @property
    def visible(self):
        return self.visibleCheck.isChecked()


#questa class preleva le varie informazioni dai layer presenti nella TOC
class TreeLayerItem(QTreeWidgetItem):
    layerIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "layer.png"))

    def __init__(self, iface, layer, tree, dlg):
        QTreeWidgetItem.__init__(self)
        self.iface = iface
        self.layer = layer
        self.setText(0, layer.name())
        self.setIcon(0, self.layerIcon)
        project = QgsProject.instance()
        #di default esporto TUTTO
        self.setCheckState(0, Qt.Checked)
        #e pongo a "visible" cio' che lo e' sulla TOC
        self.visibleItem = QTreeWidgetItem(self)
        self.visibleCheck = QCheckBox()
        if project.layerTreeRoot().findLayer(layer.id()).isVisible():
            #self.setCheckState(0, Qt.Checked)
            self.visibleCheck.setChecked(True)
        else:
            #self.setCheckState(0, Qt.Unchecked)
            self.visibleCheck.setChecked(False)
        #self.visibleItem = QTreeWidgetItem(self)
        #self.visibleCheck = QCheckBox()
        #vis = layer.customProperty("qgis2ol5/Visible", True) #ma questo cosa faceva??
        #if (vis == 0 or unicode(vis).lower() == "false"):
        #    self.visibleCheck.setChecked(False)
        #else:
        #    self.visibleCheck.setChecked(True)
        self.visibleItem.setText(0, "Visible")
        self.addChild(self.visibleItem)
        tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)
        
        #provo ad aggiungere l'opzione "refresh"
        self.refreshItem = QTreeWidgetItem(self)
        self.refreshText = QLineEdit()
        self.refreshText.setText("999")
        self.refreshItem.setText(0, "Refresh time (minutes)")
        self.addChild(self.refreshItem)
        tree.setItemWidget(self.refreshItem, 1, self.refreshText)

        if layer.type() == layer.VectorLayer:
            #provo ad aggiungere l'opzione "tiled" se NON sono punti
            if layer.geometryType() != point_geometry:
                self.tiledItem = QTreeWidgetItem(self)
                self.tiledCheck = QCheckBox()
                self.tiledCheck.setChecked(True)
                self.tiledItem.setText(0, "Tiled")
                self.addChild(self.tiledItem)
                tree.setItemWidget(self.tiledItem, 1, self.tiledCheck)
            
            #si vuole che gli elementi del layer siano seleizonabili?
            self.selectItem = QTreeWidgetItem(self)
            self.selectCheck = QCheckBox()
            self.selectCheck.setChecked(False)
            self.selectItem.setText(0, "Select")
            self.addChild(self.selectItem)
            tree.setItemWidget(self.selectItem, 1, self.selectCheck)
            
            #si vuole che gli elementi del layer si accendono al passare del mouse?
            self.hoverItem = QTreeWidgetItem(self)
            self.hoverCheck = QCheckBox()
            self.hoverCheck.setChecked(False)
            self.hoverItem.setText(0, "Hover")
            self.addChild(self.hoverItem)
            tree.setItemWidget(self.hoverItem, 1, self.hoverCheck)
            
            if layer.providerType() == 'WFS':
                self.jsonItem = QTreeWidgetItem(self)
                self.jsonCheck = QCheckBox()
                if layer.customProperty("qgis2ol5/Encode to JSON") == 2:
                    self.jsonCheck.setChecked(True)
                self.jsonItem.setText(0, "Encode to JSON")
                self.jsonCheck.stateChanged.connect(self.changeJSON)
                self.addChild(self.jsonItem)
                tree.setItemWidget(self.jsonItem, 1, self.jsonCheck)
            #if layer.geometryType() == QGis.Point:
            if layer.geometryType() == point_geometry:
                #se layer di punti tolgo la possibilita' di creare tile:
                #self.tiledCheck.setChecked(False)
                self.clusterItem = QTreeWidgetItem(self)
                self.clusterCheck = QCheckBox()
                if layer.customProperty("qgis2ol5/Cluster") == 2:
                    self.clusterCheck.setChecked(True)
                self.clusterItem.setText(0, "Cluster")
                self.clusterCheck.stateChanged.connect(self.changeCluster)
                self.addChild(self.clusterItem)
                tree.setItemWidget(self.clusterItem, 1, self.clusterCheck)
            self.popupItem = QTreeWidgetItem(self)
            self.popupItem.setText(0, "Popup fields")
            options = []
            if (int(qgis_version[0]) < 3):
              fields = self.layer.pendingFields()
              for f in fields:
                fieldIndex = fields.indexFromName(unicode(f.name()))
                formCnf = layer.editFormConfig()
                editorWidget = formCnf.widgetType(fieldIndex)
                if editorWidget == QgsVectorLayer.Hidden or \
                   editorWidget == 'Hidden':
                    continue
            else:
              fields = self.layer.fields()
              for f in fields:
                fieldIndex = fields.indexFromName(f.name())
                editorWidget = layer.editorWidgetSetup(fieldIndex).type()
                if editorWidget == 'Hidden':
                    continue

                options.append(f.name())
            for option in options:
                self.attr = QTreeWidgetItem(self)
                self.attrWidget = QComboBox()
                #self.attrWidget.addItem("no label")
                #self.attrWidget.addItem("inline label")
                #self.attrWidget.addItem("header label")
                self.attrWidget.addItem("no show")
                self.attrWidget.addItem("show on select")
                self.attrWidget.addItem("show on hover")
                self.attrWidget.addItem("show on hover and select")
                custProp = layer.customProperty("qgis2ol5/popup/" + option)
                if (custProp != "" and custProp is not None):
                    self.attrWidget.setCurrentIndex(
                        self.attrWidget.findText(
                            layer.customProperty("qgis2ol5/popup/" + option)))
                self.attr.setText(1, option)
                self.popupItem.addChild(self.attr)
                tree.setItemWidget(self.attr, 2, self.attrWidget)
            self.addChild(self.popupItem)
        else:
            if layer.providerType() == 'wms':
                self.getFeatureInfoItem = QTreeWidgetItem(self)
                self.getFeatureInfoCheck = QCheckBox()
                if layer.customProperty("qgis2ol5/GetFeatureInfo") == 2:
                    self.getFeatureInfoCheck.setChecked(True)
                self.getFeatureInfoItem.setText(0, "Enable GetFeatureInfo?")
                self.getFeatureInfoCheck.stateChanged.connect(self.changeGetFeatureInfo)
                self.addChild(self.getFeatureInfoItem)
                tree.setItemWidget(self.getFeatureInfoItem, 1, self.getFeatureInfoCheck)

    @property
    def popup(self):
        popup = []
        self.tree = self.treeWidget()
        for p in xrange(self.childCount()):
            item = self.child(p).text(1)
            if item != "":
                popupVal = self.tree.itemWidget(self.child(p), 2).currentText()
                pair = (item, popupVal)
                popup.append(pair)
        popup = OrderedDict(popup)
        return popup

    @property
    def visible(self):
        return self.visibleCheck.isChecked()

    @property
    def json(self):
        try:
            return self.jsonCheck.isChecked()
        except:
            return False

    @property
    def cluster(self):
        try:
            return self.clusterCheck.isChecked()
        except:
            return False

    @property
    def getFeatureInfo(self):
        try:
            return self.getFeatureInfoCheck.isChecked()
        except:
            return False
    
    @property
    def tiled(self):
        try:
            return self.tiledCheck.isChecked()
        except:
            return False
    
    @property
    def select(self):
        try:
            return self.selectCheck.isChecked()
        except:
            return False
    
    @property
    def hover(self):
        try:
            return self.hoverCheck.isChecked()
        except:
            return False
    
    @property
    def refresh(self):
        try:
            return self.refreshText.text()
        except:
            return False

    def changeJSON(self, isJSON):
        self.layer.setCustomProperty("qgis2ol5/Encode to JSON", isJSON)

    def changeCluster(self, isCluster):
        self.layer.setCustomProperty("qgis2ol5/Cluster", isCluster)

    def changeGetFeatureInfo(self, isGetFeatureInfo):
        self.layer.setCustomProperty("qgis2ol5/GetFeatureInfo",
                                     isGetFeatureInfo)

