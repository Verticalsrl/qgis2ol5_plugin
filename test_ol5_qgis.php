<?php
//Carico il progetto in PHP nella speranza che non faccia la cache ne' del progetto ne' dei js ad esso collegati...altrimenti e' un incubo!

//==> ad un certo punto dal plugin produco solo un JSON e non piu' dei file javascript pronti per essere letti da OL5 in quanto l'interfaccia web verrà implementata interamente da Alessandro: questo php NON SERVE PIU' a niente


date_default_timezone_set('UTC');

$root_dir_html = '/radar';

if (isset($_GET["progetto"])) {$progetto_js = $_GET["progetto"];}
else die();


?>


<!DOCTYPE html>
<html>
  <head>
    <!-- <meta http-equiv="expires" content="0"> -->
    <!-- <meta name="viewport" content="width=device-width" />  -->

<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE6" />
<meta name="Author" content="Armando Riccardo Gaeta">
<meta name="Email" content="ar_gaeta@yahoo.it">
<meta name="Subject" content="WebGIS">
<meta name="Description" content="Progetto WebGis da QGis">

    <title>QGis Server WMS to OL5</title>

    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">


    <link rel="stylesheet" href="https://openlayers.org/en/v5.3.0/css/ol.css" type="text/css">
    <script src="https://cdn.rawgit.com/openlayers/openlayers.github.io/master/en/v5.3.0/build/ol.js"></script>
    <!-- The line below is only needed for old environments like Internet Explorer and Android 4.x -->
    <script src="https://cdn.polyfill.io/v2/polyfill.min.js?features=requestAnimationFrame,Element.prototype.classList,URL,Object.assign"></script>

    <!-- ol-ext -->
    <link rel="stylesheet" href="/radar/ol-ext-master/dist/ol-ext.css" />
    <script type="text/javascript" src="/radar/ol-ext-master/dist/ol-ext.js"></script>
    <!-- ol-ext maki and fontawesome defintions used in fontsymbol -->
    <script type="text/javascript" src="/radar/ol-ext-master/dist/extra/FontAwesomeDef.js"></script>

    <script type="text/javascript" src="/radar/jQuery/jquery-1.12.4.js"></script>

    <!-- https://github.com/MrRio/jsPDF -->
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.3.2/jspdf.min.js"></script>
    <!-- filesaver-js -->
    <script type="text/javascript" src="https://cdn.rawgit.com/eligrey/FileSaver.js/aa9f4e0e/FileSaver.min.js"></script>

    <style>
      /*.map {
        height: 560px;
        width: 100%;
      }*/
      #map {
	width: 100%;
	height: 560px;
      }
    </style>

  </head>

  <body>

    <div id="map" class="map">

	    <div id="popup" class="ol-popup">
                <a href="#" id="popup-closer" class="ol-popup-closer"></a>
                <div id="popup-content"></div>
            </div>

    </div>

    <script>

	var progetto_js = "<?php echo $progetto_js; ?>";
	var root_dir_html = "<?php echo $root_dir_html; ?>";

	//a questo livello dovrei caricare un file di progetto js con tutte la variabili e la mappa da caricare, prendendo il nome del file da url
	//var script = document.createElement("script"); //Make a script DOM node
	//script.src = '/radar/qgis_progetti_js/' + progetto + '.js'; //Set it's src to the provided URL
	//document.head.appendChild(script); //Add it to the end of the head section of the page (could change 'head' to 'body' to add it to the end of the body section instead)

    </script>

<?php
	//Provo a caricare il file di progetto_js da PHP in modo da ricaricare la cache:
	$script_js = '<script type="text/javascript" src="'.$root_dir_html.'/qgis_progetti_js/'.$progetto_js.'.js?v='.microtime().'"></script>';
	echo $script_js;

	//temporaneamente carico un file js con le opzioni di selezione ehover, eventualmente poi da integrare nel js precedente - questo file dovrebbe essere uguali per tutti i progetti, tranne la definizione delle prime 2 variaibli:
	$script_js2 = '<script type="text/javascript" src="'.$root_dir_html.'/qgis_progetti_js/qgis2ol5_select_hover.js?v='.microtime().'"></script>';
        echo $script_js2;
?>

  </body>
</html>

