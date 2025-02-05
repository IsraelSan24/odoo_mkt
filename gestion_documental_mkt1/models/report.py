from email.policy import default
from odoo import _, api, fields, models


#Las clases de cada correlativo de documentos
class ReportRequerimiento(models.Model):
    _name = 'report.requerimiento'

    number_requerimiento =  fields.Integer(string='Number Requerimiento')

class ReportEquipos(models.Model):
    _name = 'report.equipos'

    number_equipos =  fields.Integer(string='Number Equipos')

class ReportLiquidacion(models.Model):
    _name = 'report.liquidacion'

    number_liquidacion =  fields.Integer(string='Number Liquidacion')

class ReportGastos(models.Model):
    _name = 'report.gastos'

    number_gastos =  fields.Integer(string='Number Gastos')
  

class ReportEmail(models.Model):
    _name = 'report.email'

    #Datos de Requerimiento
    correos_requerimientos = fields.Char(string='correos requerimientos')
    number_requerimiento_email = fields.Char(string='Number Requerimiento Email')
    correo_copia = fields.Char(string='correos copia')

    #Datos de Liquidacion
    correos_liquidacion = fields.Char(string='correos liquidacion')
    number_liquidacion_email = fields.Char(string='Number Liquidacion Email')
    correo_copia_liquidacion = fields.Char(string='correos liquidacion copia')

    #Datos de Gasto
    correos_gastos = fields.Char(string='correos gasto')
    number_gasto_email = fields.Char(string='Number Gasto Email')
    correo_copia_gasto = fields.Char(string='correos gasto copia')

    #Datos de Entrega de Equipos
    correos_equipos = fields.Char(string='Correos Equipos')
    number_equipos_email = fields.Char(string='Number Equipos Email')
    correo_copia_equipos = fields.Char(string='Correos Equipos Copia')