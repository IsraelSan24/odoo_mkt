from odoo import _, api, fields, models
from odoo.exceptions import Warning

class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean(string="Restrict Locations")

    stock_location_ids = fields.Many2many(comodel_name="stock.location", 
                                          relation="location_security_stock_location_users",
                                          column1="user_id",
                                          column2="location_id",
                                          string="Stock Locations")


    default_picking_type_ids = fields.Many2many(comodel_name="stock.picking.type",
                                                relation="stock_picking_type_users_rel",
                                                column1="user_id",
                                                column2="picking_type_id",
                                                string="Warehouse Operations")
    

    @api.constrains("default_picking_type_ids")
    def update_restrict(self):
        restrict_group = self.env.ref('mkt_stock_restriction.stock_restrictions_group')
        current_group = restrict_group
        if self.stock_location_ids:
            current_group.write({'users': [(3, self.id)]})
            self.groups_id = [(3, restrict_group.id)]
            self.restrict_locations = 0

            current_group.write({'users': [(4, self.id)]})
            self.groups_id = [(4, restrict_group.id)]
            self.restrict_locations = 1


    @api.constrains('stock_location_ids')
    def tgl_restrict(self):
        restrict_group = self.env.ref('mkt_stock_restriction.stock_restrictions_group')
        current_group = restrict_group
        if self.stock_location_ids:
            current_group.write({'users': [(3, self.id)]})
            self.groups_id = [(3, restrict_group.id)]
            self.default_picking_type_ids = False
            self.restrict_locations = 0
            pick_types = self.env['stock.picking.type'].sudo().search(['|','|','|',
                        ('default_location_src_id','in',[l.id for l in self.stock_location_ids]),
                        ('default_location_src_id.location_id','in',[l.id for l in self.stock_location_ids]),
                        ('default_location_dest_id','in',[l.id for l in self.stock_location_ids]),
                        ('default_location_dest_id.location_id','in',[l.id for l in self.stock_location_ids])])
            current_group.write({'users': [(4, self.id)]})
            self.groups_id = [(4, restrict_group.id)]
            self.default_picking_type_ids += pick_types
            self.restrict_locations = 1
        else:
            current_group.write({'users': [(3, self.id)]})
            self.groups_id = [(3, restrict_group.id)]
            self.default_picking_type_ids = False
            self.restrict_locations = 0