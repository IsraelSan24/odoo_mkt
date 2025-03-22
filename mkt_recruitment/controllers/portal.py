import base64
import binascii
from odoo import _, fields, http, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager

class ApplicantPartner(http.Controller):
    
    @http.route('/applicantpartner', type='http', auth='public', website=True)
    def applicantpartner(self, **kw):
        countries = request.env['res.country'].sudo().search([('code','=','PE')])
        states = request.env['res.country.state'].sudo().search([('country_id.code','=','PE')])
        cities = request.env['res.city'].sudo().search([])
        districts = request.env['l10n_pe.res.city.district'].sudo().search([])
        nationalities = request.env['res.country'].sudo().search([('demonym','!=',False)])
        identifications = request.env['l10n_latam.identification.type'].sudo().search([
            ('name', 'in', ('DNI', 'PTP', 'Pasaporte', 'Cédula Extranjera'))
        ])
        values = {
            'countries': countries,
            'states': states,
            'districts': districts,
            'cities': cities,
            'nationalities': nationalities,
            'identifications': identifications,
        }
        return http.request.render('mkt_recruitment.applicantpartner', values)


    @http.route('/applicantpartner/requested', type='http', auth='public', website=True)
    def applicantpartner_requested(self, **post):
        if  not post['education_start_date']:
            post['education_start_date'] = None
        if  not post['education_end_date']:
            post['education_end_date'] = None

        dni = post.get('dni')
        if dni:
            record = request.env['applicant.partner'].sudo().search([('dni', '=', dni)], limit=1, order='id desc')
            if record:
                record.sudo().unlink()

        new_applicant_partner = request.env['applicant.partner'].sudo().create(post)
        new_applicant_partner.send_email()
        return request.render('mkt_recruitment.applicantpartner_requested', {})


class RecruitmentPortal(portal.CustomerPortal):

    portal.CustomerPortal.MANDATORY_BILLING_FIELDS.remove("city")
    MANDATORY_BILLING_FIELDS = portal.CustomerPortal.MANDATORY_BILLING_FIELDS + [
        "personal_email",
        "emergency_phone",
        "reference_location",
        "emergency_contact",
        "l10n_pe_district",
        "vat",
        "gender",
        "education_level",
        "education_start_date",
        "education_end_date",
        "institution",
        "profession",
        "birthday",
        "marital",
        "children",
        "city_id",
        ]

    OPTIONAL_BILLING_FIELDS = portal.CustomerPortal.OPTIONAL_BILLING_FIELDS + [
        "is_validate",
        "familiar_dni1",
        "familiar_dni2","familiar_dni3","familiar_dni4",
        "familiar_dni5","familiar_dni6","familiar_dni7","familiar_dni8",
        "familiar_full_name1",
        "familiar_full_name2","familiar_full_name3",
        "familiar_full_name4","familiar_full_name5","familiar_full_name6",
        "familiar_full_name7","familiar_full_name8",
        "familiar_birthday1",
        "familiar_birthday2","familiar_birthday3",
        "familiar_birthday4","familiar_birthday5","familiar_birthday6",
        "familiar_birthday7","familiar_birthday8",
        "familiar_relationship1",
        "familiar_relationship2",
        "familiar_relationship3","familiar_relationship4",
        "familiar_relationship5","familiar_relationship6",
        "familiar_relationship7","familiar_relationship8",
        "familiar_gender1",
        "familiar_gender2","familiar_gender3",
        "familiar_gender4","familiar_gender5","familiar_gender6",
        "familiar_gender7","familiar_gender8",
        "familiar_address1",
        "familiar_address2","familiar_address3",
        "familiar_address4","familiar_address5","familiar_address6",
        "familiar_address7","familiar_address8",
        "familiar_dnifile1","familiar_dnifile2","familiar_dnifile3",
        "familiar_dnifile4","familiar_dnifile5","familiar_dnifile6",
        "familiar_dnifile7","familiar_dnifile8",
        "private_pension_system","national_pension_system",
        "afp_first_job","coming_from_onp",
        "current_dni","services_receipt","certijoven",
    ]


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        ContractDocument = request.env['hr.contract'].sudo()
        RecruitmentDocument = request.env['recruitment.document'].sudo()
        if 'contract_count' in counters:
            values['contract_count'] = ContractDocument.search_count(self._prepare_contracts_domain(partner)) \
                if ContractDocument.check_access_rights('read', raise_exception=False) else 0
        if 'document_count' in counters:
            values['document_count'] = RecruitmentDocument.search_count(self._prepare_documents_domain(partner)) \
                if RecruitmentDocument.check_access_rights('read', raise_exception=False) else 0
        return values


    def _prepare_contracts_domain(self, partner):
        employee = request.env.user.employee_id or request.env.user.partner_id.employee_ids
        return [
            ('employee_id','=',employee.id),
            ('employee_id','!=',False),
            ('state','in',('draft','open')),
            ('is_sended','=',True),
        ]


    def _get_contract_searchbar_sortings(self):
        return {
            'date': {'label': _('Contract Date'), 'contract': 'create_date desc'},
            'name': {'label': _('Reference'), 'contract': 'name'},
            'stage': {'label': _('State'), 'contract': 'state'},
        }


    def _prepare_documents_domain(self, partner):
        partner = request.env.user.partner_id
        return [
            ('partner_id','=',partner.id),
            ('state','in',('to_sign','signed'))
        ]


    def _get_document_searchbar_sorting(self):
        return {
            'date': {'label': _('Document date'), 'document': 'create_date desc'},
            'name': {'label': _('Reference'), 'document': 'name'},
            'stage': {'label': _('State'), 'document': 'state'},
        }


    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })
        if post and request.httprequest.method == 'POST':
            post['private_pension_system'] = post.get('private_pension_system', False)
            post['national_pension_system'] = post.get('national_pension_system', False)
            post['coming_from_onp'] = post.get('coming_from_onp', False)
            post['afp_first_job'] = post.get('afp_first_job', False)
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                values['is_validate'] = True
                partner.sudo().write(values)
                partner.sudo()._onchange_age()
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/documents')
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        districts = request.env['l10n_pe.res.city.district'].sudo().search([])
        cities = request.env['res.city'].sudo().search([])
        genders = partner.gender
        education_levels = partner.education_level
        maritals = partner.marital
        familiar_relationship1s = partner.familiar_relationship1
        familiar_relationship2s = partner.familiar_relationship2
        familiar_relationship3s = partner.familiar_relationship3
        familiar_relationship4s = partner.familiar_relationship4
        familiar_relationship5s = partner.familiar_relationship5
        familiar_relationship6s = partner.familiar_relationship6
        familiar_relationship7s = partner.familiar_relationship7
        familiar_relationship8s = partner.familiar_relationship8
        familiar_gender1s = partner.familiar_gender1
        familiar_gender2s = partner.familiar_gender2
        familiar_gender3s = partner.familiar_gender3
        familiar_gender4s = partner.familiar_gender4
        familiar_gender5s = partner.familiar_gender5
        familiar_gender6s = partner.familiar_gender6
        familiar_gender7s = partner.familiar_gender7
        familiar_gender8s = partner.familiar_gender8
        values.update({
            'partner': partner,
            'countries': countries,
            'districts': districts,
            'states': states,
            'cities': cities,
            'genders': genders,
            'education_levels': education_levels,
            'maritals': maritals,
            'familiar_relationship1s': familiar_relationship1s,
            'familiar_relationship2s': familiar_relationship2s,
            'familiar_relationship3s': familiar_relationship3s,
            'familiar_relationship4s': familiar_relationship4s,
            'familiar_relationship5s': familiar_relationship5s,
            'familiar_relationship6s': familiar_relationship6s,
            'familiar_relationship7s': familiar_relationship7s,
            'familiar_relationship8s': familiar_relationship8s,
            'familiar_gender1s': familiar_gender1s,
            'familiar_gender2s': familiar_gender2s,
            'familiar_gender3s': familiar_gender3s,
            'familiar_gender4s': familiar_gender4s,
            'familiar_gender5s': familiar_gender5s,
            'familiar_gender6s': familiar_gender6s,
            'familiar_gender7s': familiar_gender7s,
            'familiar_gender8s': familiar_gender8s,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })
        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    @http.route(['/my/applicant_documents'], type='http', auth='user', website=True)
    def applicant_documents(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        if post and request.httprequest.method == 'POST':
            update_values = {}
            if 'familiar_dnifile1' in post and post['familiar_dnifile1']:
                familiar_dnifile1_content = post['familiar_dnifile1'].read()
                familiar_dnifile1_base64 = base64.b64encode(familiar_dnifile1_content)
                update_values['familiar_dnifile1'] = familiar_dnifile1_base64
            if 'familiar_dnifile2' in post and post['familiar_dnifile2']:
                familiar_dnifile2_content = post['familiar_dnifile2'].read()
                familiar_dnifile2_base64 = base64.b64encode(familiar_dnifile2_content)
                update_values['familiar_dnifile2'] = familiar_dnifile2_base64
            if 'familiar_dnifile3' in post and post['familiar_dnifile3']:
                familiar_dnifile3_content = post['familiar_dnifile3'].read()
                familiar_dnifile3_base64 = base64.b64encode(familiar_dnifile3_content)
                update_values['familiar_dnifile3'] = familiar_dnifile3_base64
            if 'familiar_dnifile4' in post and post['familiar_dnifile4']:
                familiar_dnifile4_content = post['familiar_dnifile4'].read()
                familiar_dnifile4_base64 = base64.b64encode(familiar_dnifile4_content)
                update_values['familiar_dnifile4'] = familiar_dnifile4_base64
            if 'familiar_dnifile1_back' in post and post['familiar_dnifile1_back']:
                familiar_dnifile1_back_content = post['familiar_dnifile1_back'].read()
                familiar_dnifile1_back_base64 = base64.b64encode(familiar_dnifile1_back_content)
                update_values['familiar_dnifile1_back'] = familiar_dnifile1_back_base64
            if 'familiar_dnifile2_back' in post and post['familiar_dnifile2_back']:
                familiar_dnifile2_back_content = post['familiar_dnifile2_back'].read()
                familiar_dnifile2_back_base64 = base64.b64encode(familiar_dnifile2_back_content)
                update_values['familiar_dnifile2_back'] = familiar_dnifile2_back_base64
            if 'familiar_dnifile3_back' in post and post['familiar_dnifile3_back']:
                familiar_dnifile3_back_content = post['familiar_dnifile3_back'].read()
                familiar_dnifile3_back_base64 = base64.b64encode(familiar_dnifile3_back_content)
                update_values['familiar_dnifile3_back'] = familiar_dnifile3_back_base64
            if 'familiar_dnifile4_back' in post and post['familiar_dnifile4_back']:
                familiar_dnifile4_back_content = post['familiar_dnifile4_back'].read()
                familiar_dnifile4_back_base64 = base64.b64encode(familiar_dnifile4_back_content)
                update_values['familiar_dnifile4_back'] = familiar_dnifile4_back_base64
            if 'current_dni' in post and post['current_dni']:
                current_dni_content = post['current_dni'].read()
                current_dni_base64 = base64.b64encode(current_dni_content)
                update_values['current_dni'] = current_dni_base64
            if 'current_dni_back' in post and post['current_dni_back']:
                current_dni_back_content = post['current_dni_back'].read()
                current_dni_back_base64 = base64.b64encode(current_dni_back_content)
                update_values['current_dni_back'] = current_dni_back_base64
            if 'services_receipt' in post and post['services_receipt']:
                services_receipt_content = post['services_receipt'].read()
                services_receipt_base64 = base64.b64encode(services_receipt_content)
                update_values['services_receipt'] = services_receipt_base64
            if 'certijoven' in post and post['certijoven']:
                certijoven_content = post['certijoven'].read()
                certijoven_base64 = base64.b64encode(certijoven_content)
                update_values['certijoven'] = certijoven_base64
            if 'electronic_fine' in post and post['electronic_fine']:
                electronic_fine_content = post['electronic_fine'].read()
                electronic_fine_base64 = base64.b64encode(electronic_fine_content)
                update_values['electronic_fine'] = electronic_fine_base64
            if 'certificate_of_vaccination' in post and post['certificate_of_vaccination']:
                certificate_of_vaccination_content = post['certificate_of_vaccination'].read()
                certificate_of_vaccination_base64 = base64.b64encode(certificate_of_vaccination_content)
                update_values['certificate_of_vaccination'] = certificate_of_vaccination_base64
            if 'health_card' in post and post['health_card']:
                health_card_content = post['health_card'].read()
                health_card_base64 = base64.b64encode(health_card_content)
                update_values['health_card'] = health_card_base64
            if 'contributions_report' in post and post['contributions_report']:
                contributions_report_content = post['contributions_report'].read()
                contributions_report_base64 = base64.b64encode(contributions_report_content)
                update_values['contributions_report'] = contributions_report_base64            
            valid_fields = partner._fields.keys()
            update_values = {key: value for key, value in update_values.items() if key in valid_fields}
            if update_values:
                partner.sudo().write(update_values)
            partner.sudo().onchange_services_receipt()
            partner.sudo().onchange_certijoven()
            partner.sudo().onchange_electronic_fine()
            partner.sudo().onchange_certificate_of_vaccination()
            partner.sudo().onchange_health_card()
            partner.sudo().onchange_contributions_report()
            partner.sudo().compute_document_filename()
            if redirect:
                return request.redirect('/my/home')            
            return request.redirect('/my/home')
        res_partner_values = {
            'familiar_full_name1': partner.familiar_full_name1,
            'familiar_full_name2': partner.familiar_full_name2,
            'familiar_full_name3': partner.familiar_full_name3,
            'familiar_full_name4': partner.familiar_full_name4,
            'familiar_dni1': partner.familiar_dni1,
            'familiar_dni2': partner.familiar_dni2,
            'familiar_dni3': partner.familiar_dni3,
            'familiar_dni4': partner.familiar_dni4,
            'familiar_relationship1': partner.familiar_relationship1,
            'familiar_relationship2': partner.familiar_relationship2,
            'familiar_relationship3': partner.familiar_relationship3,
            'familiar_relationship4': partner.familiar_relationship4,
        }        
        values.update({
            'res_partner': res_partner_values,
            'partner': partner,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_partner_document',
        })
        
        response = request.render("mkt_recruitment.portal_my_partner_document", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    @http.route(['/my/contracts','/my/contracts/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ContractDocument = request.env['hr.contract'].sudo()        
        domain = self._prepare_contracts_domain(partner)
        searchbar_sortings = self._get_contract_searchbar_sortings()
        if not sortby:
            sortby = 'date'
        sort_contract = searchbar_sortings[sortby]['contract']        
        if date_begin and date_end:
            domain += [('create_date','>',date_begin),('create_date','<=',date_end)]
        contract_count = ContractDocument.search_count(domain)
        pager = portal_pager(
            url='/my/contracts',
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=contract_count,
            page=page,
            step=self._items_per_page
        )
        contracts = ContractDocument.search(domain, order=sort_contract, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_contracts_history'] = contracts.ids[:100]
        values.update({
            'date': date_begin,
            'contracts': contracts.sudo(),
            'page_name': 'contract',
            'pager': pager,
            'default_url': '/my/contracts',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("mkt_recruitment.portal_my_contracts", values)


    @http.route('/my/contracts/<int:contract_id>', type='http', auth='public', website=True)
    def portal_contract_page(self, contract_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            contract_sudo = self._document_check_access('hr.contract', contract_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        if report_type in ('html','pdf','text'):
            return self._show_report(model=contract_sudo, report_type=report_type, report_ref="mkt_recruitment.report_contract_action", download=download)
        
        values = {
            'contract_document': contract_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'employee_id': contract_sudo.employee_id.id,
            'report_type': 'html',
            'action': contract_sudo._get_portal_return_action(),
        }
        return request.render('mkt_recruitment.contract_document_portal_template', values)


    @http.route('/my/contracts/<int:contract_id>/sign', type='json', auth='user', website=True)
    def portal_contract_sign(self, contract_id, access_token=None, name=None, signature=None):
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            contract_sudo = self._document_check_access('hr.contract', contract_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid contract.')}

        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            contract_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'contract_signature': signature,
                'signature_state': 'signed',
            })
            contract_sudo.with_context(from_signed_function=True).write({'state': 'open'})
            contract_sudo.send_email_to_employee_signed()
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}
        try:
            applicant = request.env['hr.applicant'].sudo().search([('emp_id','=',contract_sudo.employee_id.id)])
            if applicant:
                applicant.write({
                    'stage_id': request.env['hr.recruitment.stage'].sudo().search([('hired_stage','=',True)]).id,
                })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid data.')}

        pdf = request.env.ref('mkt_recruitment.report_contract_action').with_user(SUPERUSER_ID)._render_qweb_pdf([contract_sudo.id])[0]

        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': '/my/contracts',
        }


    @http.route(['/my/documents','/my/documents/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        RecruitmentDocument = request.env['recruitment.document']
        domain = self._prepare_documents_domain(partner)
        searchbar_sortings = self._get_document_searchbar_sorting()
        if not sortby:
            sortby = 'date'
        sort_document = searchbar_sortings[sortby]['document']
        if date_begin and date_end:
            domain += [('create_date','>',date_begin),('create_date','<=',date_end)]
        document_count = RecruitmentDocument.search_count(domain)
        pager = portal_pager(
            url='/my/documents',
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total = document_count,
            page = page,
            step = self._items_per_page
        )
        documents = RecruitmentDocument.search(domain, order=sort_document, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_documents_history'] = documents.ids[:100]
        values.update({
            'date': date_begin,
            'documents': documents.sudo(),
            'page_name': 'document',
            'pager': pager,
            'default_url': '/my/documents',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("mkt_recruitment.portal_my_documents", values)


    @http.route('/my/documents/<int:document_id>', type='http', auth='user', website=True)
    def portal_document_page(self, document_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            document_sudo = self._document_check_access('recruitment.document', document_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=document_sudo, report_type=report_type, report_ref="mkt_recruitment.report_recruitmentdocument_action", download=download)
        
        values = {
            'recruitment_document': document_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'partner_id': document_sudo.partner_id.id,
            'report_type': 'html',
            'action': document_sudo._get_portal_return_action(),
        }
        return request.render('mkt_recruitment.recruitment_document_portal_template', values)


    @http.route('/my/documents/<int:document_id>/sign', type='json', auth='user', website=True)
    def portal_document_sign(self, document_id, access_token=None, name=None, signature=None):
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            document_sudo = self._document_check_access('recruitment.document', document_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid document.')}
        
        if not document_sudo.has_to_be_signed():
            return {'error': _('The document is not in a state requiring applicant signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}
        
        try:
            document_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'applicant_signature': signature,
                'state': 'signed',
            })
            document_sudo.send_email_to_employee_signed()
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}
        try:
            document_sudo.write_data()
        except:
            pass
        
        pdf = request.env.ref('mkt_recruitment.report_recruitmentdocument_action').with_user(SUPERUSER_ID)._render_qweb_pdf([document_sudo.id])[0]
        
        query_string = '&message=sign_ok'
        return {
            'force_refresh': True,
            'redirect_url': '/my/documents',
        }