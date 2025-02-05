from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.mkt_documental_managment.models.api_dni import apiperu_dni

class DniConsult(models.Model):
    _name = 'dni.consult'
    _description = 'Dni consult'
    _order = 'id desc'
    _rec_name = 'dni'


    name = fields.Char(string="Name complete", copy=False)
    dni = fields.Char(string="DNI")


    def button_consult_dni(self):
        try:
            self.name = apiperu_dni(self.dni)
        except:
            raise ValidationError( _("We can't obtain information about %s DNI") % (self.dni) )
