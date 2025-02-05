import random
import requests

def ExtraerContenidoEntreTagString(cadena, posicion, nombreInicio, nombreFin, sensitivo=False):
    respuesta = ""
    if(sensitivo):
        cadena2 = cadena.lower()
        nombreInicio = nombreInicio.lower()
        nombreFin=nombreFin.lower()
        posicionInicio = cadena2.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena2.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                respuesta = cadena[posicionInicio:posicionFin]
    else:
        posicionInicio = cadena.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                respuesta = cadena[posicionInicio:posicionFin]
    return respuesta

def ExtraerContenidoEntreTag(cadena, posicion, nombreInicio, nombreFin, sensitivo=False):
    respuesta = list()
    if(sensitivo):
        cadena2 = cadena.lower()
        nombreInicio = nombreInicio.lower()
        nombreFin=nombreFin.lower()
        posicionInicio = cadena2.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena2.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                posicion = posicionFin + len(nombreFin)
                respuesta = [posicion, cadena[posicionInicio:posicionFin]]
    else:
        posicionInicio = cadena.find(nombreInicio, posicion)
        if (posicionInicio > -1):
            posicionInicio += len(nombreInicio)
            posicionFin = cadena.find(nombreFin, posicionInicio)
            if(posicionFin>-1):
                posicion = posicionFin + len(nombreFin)
                respuesta = [posicion, cadena[posicionInicio:posicionFin]]
    return respuesta

def ConsultarRUC(numeroRUC):
    tipoRespuesta = 2
    mensajeRespuesta = ""
    try:
        textoAleatorio = "IMPORTANTE LAS PALABRAS CLAVES DEBE SER ALEATORIO EXISTIR LETRAS Y ESTAR EN MAYUSCULA COMO RANDOM UAP UPC LIMA HOLA MUNDO COMO ESTAS TEST comparte LOS VIDEOS EN TUS REDES SOCIALES PARA MAS CONTENIDOS si quieres aprender sobre web api revisa lista de reproduccion del canal mr angel".upper()
        arrNombreAleatorio = textoAleatorio.split(' ')
        nPalabra = random.randint(0, len(arrNombreAleatorio) - 1)
        urlInicial = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        payload={}
        headers = {
			'Host': 'e-consultaruc.sunat.gob.pe',
			'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
			'sec-ch-ua-mobile': '?0',
			'Sec-Fetch-Dest': 'document',
			'Sec-Fetch-Mode': 'navigate',
			'Sec-Fetch-Site': 'none',
			'Sec-Fetch-User': '?1',
			'Upgrade-Insecure-Requests': '1',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
		}
        sesion = requests.Session()
        response = sesion.request("GET", urlInicial, headers=headers, data=payload, verify=True)
        if(response.status_code == 200):
            payload = {}
            headers = {
				'Host': 'e-consultaruc.sunat.gob.pe',
				'Origin': 'https://e-consultaruc.sunat.gob.pe',
				'Referer': urlInicial,
				'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
				'sec-ch-ua-mobile': '?0',
				'Sec-Fetch-Dest': 'document',
				'Sec-Fetch-Mode': 'navigate',
				'Sec-Fetch-Site': 'same-origin',
				'Sec-Fetch-User': '?1',
				'Upgrade-Insecure-Requests': '1',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
			}
            numeroDNI = "12345678"; # cualquier número DNI pero que exista en SUNAT.
            url = f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorTipdoc&razSoc=&nroRuc=&nrodoc={numeroDNI}&contexto=ti-it&modo=1&search1=&rbtnTipo=2&tipdoc=1&search2={numeroDNI}&search3=&codigo="
            contenidoHTML = ""
            nIntentos = 0
            codigoEstado = 401
            while(nIntentos < 3 and codigoEstado == 401):
                response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
                codigoEstado = response.status_code
                contenidoHTML = response.text 
                nIntentos = nIntentos + 1
            if(codigoEstado == 200):
                numeroRandom = ExtraerContenidoEntreTagString(contenidoHTML, 0, "name=\"numRnd\" value=\"", "\">")
                nIntentos = 0
                codigoEstado = 401
                while(nIntentos < 3 and codigoEstado == 401):
                    [tipoRespuesta, mensajeRespuesta, codigoEstado, lCadena] = ConsultarContenidoRUC(sesion, urlInicial, numeroRUC, numeroRandom)
                    nIntentos = nIntentos + 1
    except:
        print("NOOOOOOO")
    return [lCadena,1]

def ConsultarContenidoRUC(sesion, urlReferencia, numeroRUC, numeroRandom):
    tipoRespuesta = 2
    mensajeRespuesta = ""
    payload = {}
    headers = {
        'Host': 'e-consultaruc.sunat.gob.pe',
        'Origin': 'https://e-consultaruc.sunat.gob.pe',
        'Referer': urlReferencia,
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc=%s&contexto=ti-it&modo=1&numRnd=%s" % (numeroRUC, numeroRandom)
    response = sesion.request("POST", url, headers=headers, data=payload, verify=True)
    contenidoHTML = response.text
    if (response.status_code == 200):
        [eSunat, lCadena] = ObtenerDatosRUC(contenidoHTML)
        if eSunat == 1:
            tipoRespuesta = 1
            mensajeRespuesta = "Se realizó exitosamente la consulta del número de RUC " + numeroRUC
    return [tipoRespuesta, mensajeRespuesta, response.status_code, lCadena]

def ObtenerDatosRUC(contenidoHTML):
    lcadena = []
    arr = []
    eSunat =  0
    nombreInicio = ""
    nombreFin = ""
    posicion = 0
    arrResultado = list()
    nombreInicio = "<HEAD><TITLE>"
    nombreFin = "</TITLE></HEAD>"
    contenidoBusqueda = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
    if (contenidoBusqueda == ".:: Pagina de Mensajes ::."):
        nombreInicio = "<p class=\"error\">"
        nombreFin = "</p>"
        eSunat = 2
    elif (contenidoBusqueda == ".:: Pagina de Error ::."):
        nombreInicio = "<p class=\"error\">"
        nombreFin = "</p>"
        eSunat = 3
    else:
        eSunat = 2
        nombreInicio = "<div class=\"list-group\">"
        nombreFin = "<div class=\"panel-footer text-center\">"
        contenidoBusqueda = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
        if (contenidoBusqueda == ""):
            nombreInicio = "<strong>"
            nombreFin = "</strong>"
            MensajeRespuesta = ExtraerContenidoEntreTagString(contenidoHTML, 0, nombreInicio, nombreFin)
            if(MensajeRespuesta == ""):
                print("No se puede obtener los datos del RUC, porque no existe la clase principal \"list-group\" en el contenido HTML")
        else:
            nombreInicio = "<h4 class=\"list-group-item-heading\">"
            nombreFin = "</h4>"
            posicion = 0
            arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
            if(len(arrResultado)> 0):
                posicion = int(arrResultado[0])
                arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                posicion = int(arrResultado[0])
                eSunat = 1
            else:
                print("No se puede obtener la \"Razon Social\", porque no existe la clase \"list-group-item-heading\" en el contenido HTML")
            if(eSunat == 1):
                '''
                # Mensaje cuando el estado es "BAJA DE OFICIO" caso contrario inicia con "Tipo Contribuyente"
                # Tipo Contribuyente
                # Nombre Comercial
                # Fecha de Inscripción
                # Fecha de Inicio de Actividades
                # Estado del Contribuyente
                # Condición del Contribuyente
                # Domicilio Fiscal
                # Sistema Emisión de Comprobante
                # Actividad Comercio Exterior
                # Sistema Contabilidiad
                # Emisor electrónico desde:
                # Comprobantes Electrónicos:
                # Afiliado al PLE desde
                # n/a
                '''
                lCadena = list()
                lCadena.append(arrResultado[1])
                nombreInicio = "<p class=\"list-group-item-text\">"
                nombreFin = "</p>"
                posicion = 0
                arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                while(len(arrResultado)>0):
                    posicion = int(arrResultado[0])
                    lCadena.append(arrResultado[1].strip())
                    arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                print(lCadena)
                afecto_rus_item = lCadena[2].split()[-1]
                arr.append(arrResultado)
                lcadena.append(lCadena)
                if(len(lCadena) == 0):
                    eSunat = 2
                    print ("No se puede obtener los datos básicos, porque no existe la clase \"list-group-item-text\" en el contenido HTML")
                else:
                    inicio = 0 
                    if(len(lCadena) > 14): # Si estado es "BAJA DE OFICIO" caso contrario es 14
                        inicio = 1
                    print(lCadena)
                    '''
                    # Actividad(es) Económica(s)
                    # Comprobantes de Pago c/aut. de impresión (F. 806 u 816)
                    # Sistema de Emisión Electrónica # (opcional, em algunos casos no aparece)
                    # Padrones 
                    '''
                    afecto_rus_item = lCadena[2].split()[-1]
                    lCadena = list()
                    nombreInicio = "<tbody>"
                    nombreFin = "</tbody>"
                    posicion = 0
                    arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                    while(len(arrResultado)>0):
                        posicion = int(arrResultado[0])
                        lCadena.append(arrResultado[1].strip().replace('\r\n', ' ').replace('\t', ' '))
                        arrResultado = ExtraerContenidoEntreTag(contenidoHTML, posicion, nombreInicio, nombreFin, False)
                        lcadena.append(arrResultado)
                    if(len(lCadena) == 0):
                        eSunat = 2
                        print("No se puede obtener los datos de las tablas, porque no existe el tag \"tbody\" en el contenido HTML")
                    else:
                        print(lCadena)
    return [eSunat, lcadena]
