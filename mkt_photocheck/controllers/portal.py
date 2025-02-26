from odoo import _, http
from odoo.http import request
import base64
import json

class Photocheck(http.Controller):

    @http.route('/photocheck', type='http', auth='public', website=True)
    def photocheck(self, **kw):
        jobs = request.env['photocheck.job'].sudo().search([])
        citys = request.env['photocheck.city'].sudo().search([])
        brands = request.env['photocheck.brand.group'].sudo().search([])
        supervisors = request.env['photocheck.supervisor'].sudo().search([])
        values = {
            'jobs': jobs,
            'citys': citys,
            'brands': brands,
            'supervisors': supervisors
        }
        return http.request.render('mkt_photocheck.request_photocheck', values)


    @http.route('/photocheck/requested', type='http', auth='public', website=True)
    def photocheck_requested(self, **post):
        if 'photo' in post:
            photo_content = post['photo'].read()
            photo_data64 = base64.b64encode(photo_content)
            post['photo'] = photo_data64
        new_photo = request.env['photocheck'].sudo().create(post)
        new_photo.sudo().modify_image()
        return request.render('mkt_photocheck.photocheck_requested', {})