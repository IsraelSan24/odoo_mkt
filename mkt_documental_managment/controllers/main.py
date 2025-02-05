import io
from odoo import http
from odoo.http import request, content_disposition

class Affidavit(http.Controller):

    @http.route('/affidavit', method='post', type='http', auth='user', website=True)
    def affidavit(self, **kw):
        user = request.env.user
        countries = request.env['res.country'].sudo().search([('code','=','PE')])
        states = request.env['res.country.state'].sudo().search([('country_id.code','=','PE')])
        districts = request.env['l10n_pe.res.city.district'].sudo().search([])
        cities = request.env['res.city'].sudo().search([])
        values = {
            'user': user,
            'countries': countries,
            'states': states,
            'districts': districts,
            'cities': cities,
            'bootstrap_formatting': True,
            'report_type': 'html',
        }
        return request.render('mkt_documental_managment.portal_affidavit_template', values)

    @http.route('/affidavit/created', method='post', type='http', auth='user', website=True)
    def affidavit_created(self, **post):
        affidavit = request.env['affidavit'].sudo().create(post)
        request.env.cr.commit()
        return request.render('mkt_documental_managment.portal_affidavit_created_template', {
            'affidavit_id': affidavit.id,
        })

    @http.route('/affidavit/download/<int:affidavit_id>', type='http', auth='user', website=True)
    def download_affidavit(self, affidavit_id):
        affidavit_pdf_content = request.env.ref('mkt_documental_managment.action_affidavit_report').sudo()._render_qweb_pdf(affidavit_id)[0]
        pdf_file_name = 'Affidavit_%d.pdf' % affidavit_id
        return request.make_response(affidavit_pdf_content, [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(affidavit_pdf_content)),
            ('Content-Disposition', content_disposition(pdf_file_name))
        ])