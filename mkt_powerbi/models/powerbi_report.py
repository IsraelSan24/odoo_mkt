from odoo import fields, models, api

class PowerBIReport(models.Model):
    _name = 'powerbi.report'
    _description = "Power BI Report Model"

    active = fields.Boolean(default=True) # reserved field: indicates record is tagged as not visible in the UI

    author_id = fields.Many2one(comodel_name='res.users', string='Analyst', tracking=True, default=lambda self: self.env.user)
    customer_ids = fields.One2many(comodel_name='powerbi.report.customer', inverse_name='powerbi_report_id', string="Customers")
    description = fields.Text()
    name = fields.Char(string="Title", required=True)
    powerbi_embed = fields.Html(string="Power BI Embed", compute="_generate_embed_url", store=True, sanitize=False, readonly=True)
    url = fields.Char(string='PowerBI Report URL', required=True)

    @api.depends("url")
    def _generate_embed_url(self):
        """
        Generates a valid iframe html using the powerBI URL provided.
        """
        for record in self:
            if record.url:
                record.powerbi_embed = f"""
                <iframe src="{record.url}"
                        width="80%"
                        height="700"
                        frameborder="1"
                        style="border:1px solid #000000;"
                        allowfullscreen="False">
                </iframe>"""
            else:
                record.powerbi_embed = ""