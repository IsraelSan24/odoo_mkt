from odoo import models
from odoo.tools.pdf import merge_pdf
  
class IrActionsReport(models.Model):
    """
    Versión optimizada que mantiene la funcionalidad de footers
    """
    _inherit = 'ir.actions.report'
    
    def _render_qweb_pdf(self, res_ids=None, data=None):
        # Solo aplicar lógica especial para el reporte de contratos
        if self.report_name == 'mkt_recruitment.report_contract':
            # Si es un solo ID, renderizar normalmente
            if res_ids and len(res_ids) == 1:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069') #importante
                return super(IrActionsReport, self)._render_qweb_pdf(res_ids, data={'base_url': base_url + "/"})
            
            # Si son múltiples, renderizar uno por uno y unir al final
            pdfs = []
            for res_id in res_ids or []:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
                pdf_content, _ = super(IrActionsReport, self)._render_qweb_pdf([res_id], data={'base_url': base_url + "/"}) #importante
                pdfs.append(pdf_content)
            return merge_pdf(pdfs), 'pdf'
        
        # Para otros reportes, comportamiento por defecto
        return super(IrActionsReport, self)._render_qweb_pdf(res_ids, data)