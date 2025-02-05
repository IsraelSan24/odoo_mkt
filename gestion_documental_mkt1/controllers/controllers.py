# -*- coding: utf-8 -*-
import base64
from doctest import REPORT_UDIFF
from odoo.http import request, content_disposition, route
from werkzeug.utils import redirect
from odoo import fields, http, SUPERUSER_ID, _

class GestionRequest(http.Controller):

   # Levantamiento de vistas qweb
    @http.route(['/requerimiento'], method="post", type='http', auth='user', website=True, csrf=False)
    def request_requerimiento(self, **post):
       
        #maintenance_requests = request.env['maintenance.equipment'].sudo().search([])
        #maintenance_team = request.env['maintenance.team'].sudo().search([])
        user = request.env.user.id
        #employee = request.env['hr.employee'].sudo().search([('user_id', '=', user)])
        request_dict = []
        team_name = []
        #for record in maintenance_requests:
            #name = record.name
            #request_dict.append({'id': record.id, 'name': name})
        #for record in maintenance_team:
            #name = record.name
            #team_name.append({'id': record.id, 'name': name})
            #request.env['purchase.order'].sudo().create(values)

        return http.request.render('gestion_documental_mkt.requerimientos', {})
    
    @http.route(['/liquidacion'], method="post", type='http', auth='user', website=True, csrf=False)
    def request_liquidacion(self, **post):

        return http.request.render('gestion_documental_mkt.liquidacion', {})

    @http.route(['/gastos'], method="post", type='http', auth='user', website=True, csrf=False)
    def request_gastos(self, **post):
       
        return http.request.render('gestion_documental_mkt.gastos', {})

    @http.route(['/equipos'], method="post", type='http', auth='user', website=True, csrf=False)
    def request_equipos(self, **post):
       
      return http.request.render('gestion_documental_mkt.equipos', {})


    # Levantamiento de gmail y Reporte pdf
    @http.route('/guardar/requerimiento', method='post', type='http', auth='public', website=True, csrf=False)
    def guardar_pdf_requerimiento(self, **post):

        fecha_solicitud=post['fecha_solicitud']
        banco=post['banco']
        ncta=post['ncta']
        girado=post['Girado']
        suma=post['suma']
        cliente=post['cliente']
        actividad=post['actividad']
        concepto=post['concepto']

        ppto=post['ppto']
        centro_costo=post['centro_costo']
        operacion=post['operacion']
        importe_s=post['importe_s']
        importe_uss=post['importe_uss']
        importe_cheque=post['importe_cheque']

        responsable=post['responsable']
        dni_responsable=post['dni_responsable']
        detalle_responsable=post['detalle_responsable']
        
        numeros_requerimiento= 0
        numeros_requerimiento_text=""
        dato = int(post['idnumeric_requerimiento'])
        val = dato - 1
        secuenciasgeneral = request.env['report.requerimiento'].sudo().search([])
        valor = 0
        for a in secuenciasgeneral:
           valor = a.number_requerimiento

        if valor >=0:
          values ={'number_requerimiento': (valor + (dato - val))}
          request.env['report.requerimiento'].sudo().create(values)
          secuenciasfinal = request.env['report.requerimiento'].sudo().search([])
          for p in secuenciasfinal:
              obtener = p.number_requerimiento
              numeros_requerimiento = obtener


        #operacion de 000
        if numeros_requerimiento <=9:
            numeros_requerimiento_text ="E-000" + str(numeros_requerimiento)
        elif numeros_requerimiento >=10 and numeros_requerimiento <=99:
             numeros_requerimiento_text ="E-00" + str(numeros_requerimiento)
        elif numeros_requerimiento >=100 and numeros_requerimiento <=999:
             numeros_requerimiento_text ="E-0" + str(numeros_requerimiento)
        elif numeros_requerimiento >=1000:
             numeros_requerimiento_text = "E-"+ str(numeros_requerimiento)
        
        
  
        pdf = request.env.ref('gestion_documental_mkt.action_report_requerimiento').sudo()._render_qweb_pdf([REPORT_UDIFF],
        {"banco":banco,'ncta':ncta,"Girado":girado,'suma':suma,"cliente":cliente,"actividad":actividad,"concepto":concepto,"ppto":ppto,"centro_costo":centro_costo,"operacion":operacion,
        "importe_s":importe_s,"importe_uss":importe_uss,"importe_cheque":importe_cheque,"fecha_solicitud":fecha_solicitud,"numeros_requerimiento_text":numeros_requerimiento_text,
        "responsable":responsable,"dni_responsable":dni_responsable,"detalle_responsable":detalle_responsable})[0]

        #pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        #pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)), ('Content-Disposition', 'attachment; filename="Requerimiento '+numeros_requerimiento_text+'.pdf')]
        #return request.make_response(pdf, headers=pdfhttpheaders)

        data_record = base64.b64encode(pdf)

        ir_values = {
            'name': "Requerimiento"+" "+numeros_requerimiento_text+".pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'data_record',
            'mimetype': 'application/pdf',
        }

        user = request.env.user.id
        user_requerimiento = request.env['res.users'].sudo().search([('id', '=', user)])

        values = {
          'correos_requerimientos': post['correos_requerimientos'],
          'number_requerimiento_email':numeros_requerimiento_text,
          'correo_copia':user_requerimiento.login,
        }
        request_id = request.env['report.email'].sudo().create(values)
        data_id = request.env['ir.attachment'].sudo().create(ir_values)
        template = request.env.ref('gestion_documental_mkt.mail_template_requerimientos')
        template.attachment_ids = [(6, 0, [data_id.id])]
        template.sudo().send_mail(request_id.id,force_send=True)
        return redirect('/correo_enviado')

    @http.route('/guardar/liquidacion', method='post', type='http', auth='public', website=True, csrf=False)
    def guardar_pdf_liquidacion(self, **post):

        responsable=post['responsable']
        dni=post['dni']
        fecha_liquidacion=post['fecha_liquidacion']
        valor=post['valor']
        centro_costo=post['centro_costo']
        total_liquidacion=post['total_liquidacion']
        saldo_liquidacion=post['saldo_liquidacion']

        numeros_liquidacion= 0
        numeros_liquidacion_text=""
        
        dato = int(post['idnumeric_liquidacion'])
        val = dato - 1
        secuenciasgeneral = request.env['report.liquidacion'].sudo().search([])
        value = 0
        for a in secuenciasgeneral:
           value = a.number_liquidacion


        if value >=0:
          values ={'number_liquidacion': (value + (dato - val))}
          request.env['report.liquidacion'].sudo().create(values)
          secuenciasfinal = request.env['report.liquidacion'].sudo().search([])
          for p in secuenciasfinal:
              obtener = p.number_liquidacion
              numeros_liquidacion = obtener


         #operacion de 000
        if numeros_liquidacion <=9:
            numeros_liquidacion_text ="E-000" + str(numeros_liquidacion)
        elif numeros_liquidacion >=10 and numeros_liquidacion <=99:
            numeros_liquidacion_text ="E-00" + str(numeros_liquidacion)
        elif numeros_liquidacion >=100 and numeros_liquidacion <=999:
            numeros_liquidacion_text ="E-0" + str(numeros_liquidacion)
        elif numeros_liquidacion >=1000:
            numeros_liquidacion_text ="E-" +  str(numeros_liquidacion)

        #Datos de Tabla
        documento1=post['documento1']
        motivo1=post['motivo1']
        monto1=post['monto1']
        fecha_tabla1 = post['fecha_tabla1']
        
        documento2=post['documento2']
        motivo2=post['motivo2']
        monto2=post['monto2']
        fecha_tabla2 = post['fecha_tabla2']
        
        documento3=post['documento3']
        motivo3=post['motivo3']
        monto3=post['monto3']
        fecha_tabla3 = post['fecha_tabla3']
        
        documento4=post['documento4']
        motivo4=post['motivo4']
        monto4=post['monto4']
        fecha_tabla4 = post['fecha_tabla4']
        
        documento5=post['documento5']
        motivo5=post['motivo5']
        monto5=post['monto5']
        fecha_tabla5 = post['fecha_tabla5']

        documento6=post['documento6']
        motivo6=post['motivo6']
        monto6=post['monto6']
        fecha_tabla6 = post['fecha_tabla6']

        documento7=post['documento7']
        motivo7=post['motivo7']
        monto7=post['monto7']
        fecha_tabla7 = post['fecha_tabla7']

        documento8=post['documento8']
        motivo8=post['motivo8']
        monto8=post['monto8']
        fecha_tabla8 = post['fecha_tabla8']

        documento9=post['documento9']
        motivo9=post['motivo9']
        monto9=post['monto9']
        fecha_tabla9 = post['fecha_tabla9']

        documento10=post['documento10']
        motivo10=post['motivo10']
        monto10=post['monto10']
        fecha_tabla10 = post['fecha_tabla10']

        documento11=post['documento11']
        motivo11=post['motivo11']
        monto11=post['monto11']
        fecha_tabla11 = post['fecha_tabla11']

        documento12=post['documento12']
        motivo12=post['motivo12']
        monto12=post['monto12']
        fecha_tabla12 = post['fecha_tabla12']


        pdf = request.env.ref('gestion_documental_mkt.action_report_liquidacion').sudo()._render_qweb_pdf([REPORT_UDIFF],
        {"responsable":responsable,"dni":dni,"valor":valor,"centro_costo":centro_costo,"fecha_liquidacion":fecha_liquidacion,"numeros_liquidacion_text":numeros_liquidacion_text,
        "fecha_tabla1":fecha_tabla1,"documento1":documento1,"motivo1":motivo1,"monto1":monto1,
        "fecha_tabla2":fecha_tabla2,"documento2":documento2,"motivo2":motivo2,"monto2":monto2,
        "fecha_tabla3":fecha_tabla3,"documento3":documento3,"motivo3":motivo3,"monto3":monto3,
        "fecha_tabla4":fecha_tabla4,"documento4":documento4,"motivo4":motivo4,"monto4":monto4,
        "fecha_tabla5":fecha_tabla5,"documento5":documento5,"motivo5":motivo5,"monto5":monto5,
        "fecha_tabla6":fecha_tabla6,"documento6":documento6,"motivo6":motivo6,"monto6":monto6,
        "fecha_tabla7":fecha_tabla7,"documento7":documento7,"motivo7":motivo7,"monto7":monto7,
        "fecha_tabla8":fecha_tabla8,"documento8":documento8,"motivo8":motivo8,"monto8":monto8,
        "fecha_tabla9":fecha_tabla9,"documento9":documento9,"motivo9":motivo9,"monto9":monto9,
        "fecha_tabla10":fecha_tabla10,"documento10":documento10,"motivo10":motivo10,"monto10":monto10,
        "fecha_tabla11":fecha_tabla11,"documento11":documento11,"motivo11":motivo11,"monto11":monto11,
        "fecha_tabla12":fecha_tabla12,"documento12":documento12,"motivo12":motivo12,"monto12":monto12,
        "total_liquidacion":total_liquidacion,"saldo_liquidacion":saldo_liquidacion})[0]
        
        #pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        #return request.make_response(pdf, headers=pdfhttpheaders)

        data_record = base64.b64encode(pdf)

        ir_values = {
            'name': "Liquidacion"+" "+numeros_liquidacion_text+".pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'data_record',
            'mimetype': 'application/pdf',
        }

        user = request.env.user.id
        user_liquidacion = request.env['res.users'].sudo().search([('id', '=', user)])

        values = {
          'correos_liquidacion': post['correos_liquidacion'],
          'number_liquidacion_email':numeros_liquidacion_text,
          'correo_copia_liquidacion':user_liquidacion.login,
        }
        request_id = request.env['report.email'].sudo().create(values)
        data_id = request.env['ir.attachment'].sudo().create(ir_values)
        template = request.env.ref('gestion_documental_mkt.mail_template_liquidacion')
        template.attachment_ids = [(6, 0, [data_id.id])]
        template.sudo().send_mail(request_id.id,force_send=True)
        return redirect('/correo_enviado')

    @http.route('/guardar/gastos', method='post', type='http', auth='public', website=True, csrf=False)
    def guardar_pdf_gastos(self, **post):

        razon="MARKETING ALTERNO PERÚ SAC"
        ruc="20512433821"
        periodo=post['periodo']
        emision=post['emision']
        datos=post['datos']
        dni=post['dni']
        ppto=post['ppto']
        costo=post['costo']
        total_gastos = post['total_gastos']

        #Totales de Importe por Fecha
        fecha_importe1 = post['fecha_importe1']
        importe_total_fecha1 = post['importe_total_fecha1']

        fecha_importe2 = post['fecha_importe2']
        importe_total_fecha2 = post['importe_total_fecha2']

        fecha_importe3 = post['fecha_importe3']
        importe_total_fecha3 = post['importe_total_fecha3']

        fecha_importe4 = post['fecha_importe4']
        importe_total_fecha4 = post['importe_total_fecha4']

        fecha_importe5 = post['fecha_importe5']
        importe_total_fecha5 = post['importe_total_fecha5']

        fecha_importe6 = post['fecha_importe6']
        importe_total_fecha6 = post['importe_total_fecha6']


        numeros_gastos= 0
        numeros_gastos_text=""
        dato = int(post['idnumeric_gastos'])
        val = dato - 1
        secuenciasgeneral = request.env['report.gastos'].sudo().search([])
        value = 0
        for a in secuenciasgeneral:
           value = a.number_gastos


        if value >=0:
          values ={'number_gastos': (value + (dato - val))}
          request.env['report.gastos'].sudo().create(values)
          secuenciasfinal = request.env['report.gastos'].sudo().search([])
          for p in secuenciasfinal:
              obtener = p.number_gastos
              numeros_gastos = obtener


         #operacion de 000
        if numeros_gastos <=9:
            numeros_gastos_text ="E-000" + str(numeros_gastos)
        elif numeros_gastos >=10 and numeros_gastos <=99:
            numeros_gastos_text ="E-00" + str(numeros_gastos)
        elif numeros_gastos >=100 and numeros_gastos <=999:
            numeros_gastos_text ="E-0" + str(numeros_gastos)
        elif numeros_gastos >=1000:
            numeros_gastos_text = "E-"+ str(numeros_gastos)



        destino1=post['destino1']
        motivo1=post['motivo1']
        importe1=post['importe1']
        fecha_tabla1 = post['fecha_tabla1']

        
        destino2=post['destino2']
        motivo2=post['motivo2']
        importe2=post['importe2']
        fecha_tabla2 = post['fecha_tabla2']

        
        destino3=post['destino3']
        motivo3=post['motivo3']
        importe3=post['importe3']
        fecha_tabla3 = post['fecha_tabla3']
        
        destino4=post['destino4']
        motivo4=post['motivo4']
        importe4=post['importe4']
        fecha_tabla4 = post['fecha_tabla4']
        
        destino5=post['destino5']
        motivo5=post['motivo5']
        importe5=post['importe5']
        fecha_tabla5 = post['fecha_tabla5']
        
        destino6=post['destino6']
        motivo6=post['motivo6']
        importe6=post['importe6']
        fecha_tabla6 = post['fecha_tabla6']

        destino7=post['destino7']
        motivo7=post['motivo7']
        importe7=post['importe7']
        fecha_tabla7 = post['fecha_tabla7']

        destino8=post['destino8']
        motivo8=post['motivo8']
        importe8=post['importe8']
        fecha_tabla8 = post['fecha_tabla8']

        destino9=post['destino9']
        motivo9=post['motivo9']
        importe9=post['importe9']
        fecha_tabla9 = post['fecha_tabla9']

        destino10=post['destino10']
        motivo10=post['motivo10']
        importe10=post['importe10']
        fecha_tabla10 = post['fecha_tabla10']

        destino11=post['destino11']
        motivo11=post['motivo11']
        importe11=post['importe11']
        fecha_tabla11 = post['fecha_tabla11']

        destino12=post['destino12']
        motivo12=post['motivo12']
        importe12=post['importe12']
        fecha_tabla12 = post['fecha_tabla12']
     

        pdf = request.env.ref('gestion_documental_mkt.action_report_gastos').sudo()._render_qweb_pdf([REPORT_UDIFF],
        {"razon":razon,"ruc":ruc,"emision":emision,"periodo":periodo,"datos":datos,
        "dni":dni,"ppto":ppto,"costo":costo,"numeros_gastos_text":numeros_gastos_text,
        "fecha_tabla1":fecha_tabla1,"destino1":destino1,"motivo1":motivo1,"importe1":importe1,
        "fecha_tabla2":fecha_tabla2,"destino2":destino2,"motivo2":motivo2,"importe2":importe2,
        "fecha_tabla3":fecha_tabla3,"destino3":destino3,"motivo3":motivo3,"importe3":importe3,
        "fecha_tabla4":fecha_tabla4,"destino4":destino4,"motivo4":motivo4,"importe4":importe4,
        "fecha_tabla5":fecha_tabla5,"destino5":destino5,"motivo5":motivo5,"importe5":importe5,
        "fecha_tabla6":fecha_tabla6,"destino6":destino6,"motivo6":motivo6,"importe6":importe6,
        "fecha_tabla7":fecha_tabla7,"destino7":destino7,"motivo7":motivo7,"importe7":importe7,
        "fecha_tabla8":fecha_tabla8,"destino8":destino8,"motivo8":motivo8,"importe8":importe8,
        "fecha_tabla9":fecha_tabla9,"destino9":destino9,"motivo9":motivo9,"importe9":importe9,
        "fecha_tabla10":fecha_tabla10,"destino10":destino10,"motivo10":motivo10,"importe10":importe10,"total_gastos":total_gastos,
        "fecha_tabla11":fecha_tabla11,"destino11":destino11,"motivo11":motivo11,"importe11":importe11,
        "fecha_tabla12":fecha_tabla12,"destino12":destino12,"motivo12":motivo12,"importe12":importe12,
        "fecha_importe1":fecha_importe1,"importe_total_fecha1":importe_total_fecha1,"fecha_importe2":fecha_importe2,"importe_total_fecha2":importe_total_fecha2,
        "fecha_importe3":fecha_importe3,"importe_total_fecha3":importe_total_fecha3,"fecha_importe4":fecha_importe4,"importe_total_fecha4":importe_total_fecha4,
        "fecha_importe5":fecha_importe5,"importe_total_fecha5":importe_total_fecha5,"fecha_importe6":fecha_importe6,"importe_total_fecha6":importe_total_fecha6})[0]

        #pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        #return request.make_response(pdf, headers=pdfhttpheaders)
        data_record = base64.b64encode(pdf)

        ir_values = {
            'name': "Planilla de Gasto por Movilidad"+" "+numeros_gastos_text+".pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'data_record',
            'mimetype': 'application/pdf',
        }

        user = request.env.user.id
        user_gastos = request.env['res.users'].sudo().search([('id', '=', user)])

        values = {
          'correos_gastos': post['correos_gastos'],
          'number_gasto_email':numeros_gastos_text,
          'correo_copia_gasto':user_gastos.login,
        }

        request_id = request.env['report.email'].sudo().create(values)
        data_id = request.env['ir.attachment'].sudo().create(ir_values)
        template = request.env.ref('gestion_documental_mkt.mail_template_gastos')
        template.attachment_ids = [(6, 0, [data_id.id])]
        template.sudo().send_mail(request_id.id,force_send=True)
        return redirect('/correo_enviado')

    @http.route('/guardar/equipos', method='post', type='http', auth='public', website=True, csrf=False)
    def guardar_pdf_equipos(self, **post):

        fecha_equipos = post['fecha_equipos']
        nombre_equipos=post['nombre_equipos']
        dni_equipos=post['dni_equipos']
        #domicilio=post['domicilio']
        equipo=post['equipo']
        serie_equipos=post['serie_equipos']
        operador_equipos=post['operador_equipos']
        cargador_equipos=post['cargador_equipos']
        marca_equipo=post['marca_equipo']
        modelo_equipo=post['modelo_equipo']
        numero_equipo = post['numero_equipo']
        inventario_equipo = post['inventario_equipo']
        valorizado_equipos= post['valorizado_equipos']


        numeros_equipos= 0
        numeros_equipos_text=""
        dato = int(post['idnumeric_equipos'])
        val = dato - 1
        secuenciasgeneral = request.env['report.equipos'].sudo().search([])
        valor = 0
        for a in secuenciasgeneral:
           valor = a.number_equipos

        if valor >=0:
          values ={'number_equipos': (valor + (dato - val))}
          request.env['report.equipos'].sudo().create(values)
          secuenciasfinal = request.env['report.equipos'].sudo().search([])
          for p in secuenciasfinal:
              obtener = p.number_equipos
              numeros_equipos = obtener

        #operacion de 000
        if numeros_equipos <=9:
            numeros_equipos_text ="E-000" + str(numeros_equipos)
        elif numeros_equipos >=10 and numeros_equipos <=99:
             numeros_equipos_text ="E-00" + str(numeros_equipos)
        elif numeros_equipos >=100 and numeros_equipos <=999:
             numeros_equipos_text ="E-0" + str(numeros_equipos)
        elif numeros_equipos >=1000:
             numeros_equipos_text = "E-" + str(numeros_equipos)
       
        pdf = request.env.ref('gestion_documental_mkt.action_report_equipos').sudo()._render_qweb_pdf([REPORT_UDIFF],{
        "nombre_equipos":nombre_equipos,"dni_equipos":dni_equipos,"equipo":equipo,"serie_equipos":serie_equipos,"operador_equipos":operador_equipos,
        "cargador_equipos":cargador_equipos,"marca_equipo":marca_equipo,"modelo_equipo":modelo_equipo,"numero_equipo":numero_equipo,"inventario_equipo":inventario_equipo,
        "valorizado_equipos":valorizado_equipos,"numeros_equipos_text":numeros_equipos_text,"fecha_equipos":fecha_equipos})[0]
          
        #pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        #return request.make_response(pdf, headers=pdfhttpheaders)

        data_record = base64.b64encode(pdf)

        ir_values = {
            'name': "Entrega de Equipos Moviles"+" "+numeros_equipos_text+".pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': 'data_record',
            'mimetype': 'application/pdf',
        }

        user = request.env.user.id
        user_equipos = request.env['res.users'].sudo().search([('id', '=', user)])

        values = {
          'correos_equipos': post['correos_equipos'],
          'number_equipos_email':numeros_equipos_text,
          'correo_copia_equipos':user_equipos.login,
        }

        request_id = request.env['report.email'].sudo().create(values)
        data_id = request.env['ir.attachment'].sudo().create(ir_values)
        template = request.env.ref('gestion_documental_mkt.mail_template_equipos')
        template.attachment_ids = [(6, 0, [data_id.id])]
        template.sudo().send_mail(request_id.id,force_send=True)
        return redirect('/correo_enviado')