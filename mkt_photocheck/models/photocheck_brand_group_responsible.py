from odoo import fields, models

class PhotocheckBrandGroupResponsible(models.Model):
    _name = "photocheck.brand.group.responsible"
    _description = "Responsible per Brand Group with Cities"

    brand_group_id = fields.Many2one(
        "photocheck.brand.group",
        string="Brand Group",
        required=True,
        ondelete="cascade"
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        ondelete="cascade"
    )
    city_ids = fields.Many2many(
        "photocheck.city",
        "photocheck_brand_group_resp_city_rel",
        "responsible_id",
        "city_id",
        string="Allowed Cities",
        help="If empty, this responsible can see all cities."
    )