import base64
import binascii
from odoo import _, fields, http, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager

class PayrollPortal(portal.CustomerPortal):


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        Paycheck = request.env['paycheck'].sudo()
        if 'paycheck_count' in counters:
            values['paycheck_count'] = Paycheck.search_count(self._prepare_paychecks_domain(partner)) \
                if Paycheck.check_access_rights('read', raise_exception=False) else 0
        return values


    def _prepare_paychecks_domain(self, partner):
        employee = request.env.user.employee_id or request.env.user.partner_id.employee_ids
        return [
            ('employee_id','=',employee.id),
            ('employee_id','!=',False),
        ]


    def _get_paycheck_sortings(self):
        return {
            'date': {'label': _('Paycheck date'), 'paycheck': 'create_date desc'},
            'name': {'label': _('Reference'), 'paycheck': 'name'},
        }


    @http.route(['/my/paychecks','/my/paychecks/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_paychecks(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Paycheck = request.env['paycheck'].sudo()
        domain = self._prepare_paychecks_domain(partner)
        searchbar_sortings = self._get_paycheck_sortings()
        if not sortby:
            sortby = 'date'
        sort_paycheck = searchbar_sortings[sortby]['paycheck']
        if date_begin and date_end:
            domain += [('create_date','>',date_begin),('create_date','<=',date_end)]
        paycheck_count = Paycheck.search_count(domain)
        pager = portal_pager(
            url='/my/paychecks',
            total=paycheck_count,
            page=page,
            step=self._items_per_page
        )
        paychecks = Paycheck.search(domain, order=sort_paycheck, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_paycheck_history'] = paychecks.ids[:100]
        values.update({
            'date': date_begin,
            'paychecks': paychecks.sudo(),
            'page_name': 'paycheck',
            'pager': pager,
            'default_url': '/my/paychecks',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render('mkt_payroll.portal_my_paychecks', values)


    @http.route(['/my/paychecks/download/<int:paycheck_id>'], type='http', auth='user', website=True)
    def download_paycheck(self, paycheck_id):
        Paycheck = request.env['paycheck'].sudo().browse(paycheck_id)
        if not Paycheck.exists() or not Paycheck.paycheck:
            return request.not_found()
        
        filecontent = base64.b64decode(Paycheck.paycheck)
        filename = Paycheck.paycheck_filename or 'paycheck.pdf'
        
        return request.make_response(filecontent, [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', f'attachment; filename="{filename}"'),
        ])
