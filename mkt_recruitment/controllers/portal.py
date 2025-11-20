import base64
import binascii
from odoo import _, fields, http, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from .portal_compliance import require_portal_checks

import logging
_logger = logging.getLogger(__name__)

# class ApplicantPartner(http.Controller):
    
#     @http.route('/applicantpartner', type='http', auth='public', website=True)
#     def applicantpartner(self, **kw):
#         countries = request.env['res.country'].sudo().search([('code','=','PE')])
#         states = request.env['res.country.state'].sudo().search([('country_id.code','=','PE')])
#         cities = request.env['res.city'].sudo().search([])
#         districts = request.env['l10n_pe.res.city.district'].sudo().search([])
#         nationalities = request.env['res.country'].sudo().search([('demonym','!=',False)])
#         identifications = request.env['l10n_latam.identification.type'].sudo().search([
#             ('name', 'in', ('DNI', 'PTP', 'Pasaporte', 'Cédula Extranjera', 'Carnet de Extranjeria'))
#         ])
#         values = {
#             'countries': countries,
#             'states': states,
#             'districts': districts,
#             'cities': cities,
#             'nationalities': nationalities,
#             'identifications': identifications,
#             'action_url': "/applicantpartner/requested"
#         }
#         return http.request.render('mkt_recruitment.applicantpartner', values)


#     @http.route('/applicantpartner/requested', type='http', auth='public', website=True)
#     def applicantpartner_requested(self, **post):
#         # Asegura que los campos opcionales estén definidos o sean None
#         if not post.get('education_start_date'):
#             post['education_start_date'] = None
#         if not post.get('education_end_date'):
#             post['education_end_date'] = None

#         dni = post.get('dni')
#         if dni:
#             record = request.env['applicant.partner'].sudo().search([('dni', '=', dni)], limit=1, order='id desc')
#             if record:
#                 record.sudo().unlink()

#         new_applicant_partner = request.env['applicant.partner'].sudo().create(post)
#         new_applicant_partner.send_email()
#         return request.render('mkt_recruitment.applicantpartner_requested', {})


class RecruitmentPortal(portal.CustomerPortal):

    portal.CustomerPortal.MANDATORY_BILLING_FIELDS.remove("city")
    MANDATORY_BILLING_FIELDS = portal.CustomerPortal.MANDATORY_BILLING_FIELDS + [
        "personal_email",
        "emergency_phone",
        "reference_location",
        "emergency_contact",
        "emergency_contact_relationship",
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
        "familiar_dni5","familiar_dni6","familiar_dni7","familiar_dni8","familiar_dni9","familiar_dni10",
        "familiar_full_name1",
        "familiar_full_name2","familiar_full_name3",
        "familiar_full_name4","familiar_full_name5","familiar_full_name6",
        "familiar_full_name7","familiar_full_name8","familiar_full_name9","familiar_full_name10",
        "familiar_birthday1",
        "familiar_birthday2","familiar_birthday3",
        "familiar_birthday4","familiar_birthday5","familiar_birthday6",
        "familiar_birthday7","familiar_birthday8","familiar_birthday9","familiar_birthday10",
        "familiar_relationship1",
        "familiar_relationship2",
        "familiar_relationship3","familiar_relationship4",
        "familiar_relationship5","familiar_relationship6",
        "familiar_relationship7","familiar_relationship8","familiar_relationship9","familiar_relationship10",
        "familiar_gender1",
        "familiar_gender2","familiar_gender3",
        "familiar_gender4","familiar_gender5","familiar_gender6",
        "familiar_gender7","familiar_gender8","familiar_gender9","familiar_gender10",
        "familiar_address1",
        "familiar_address2","familiar_address3",
        "familiar_address4","familiar_address5","familiar_address6",
        "familiar_address7","familiar_address8","familiar_address9","familiar_address10",
        "familiar_dnifile1","familiar_dnifile2","familiar_dnifile3",
        "familiar_dnifile4","familiar_dnifile5","familiar_dnifile6",
        "familiar_dnifile7","familiar_dnifile8","familiar_dnifile9","familiar_dnifile10",
        "private_pension_system","national_pension_system",
        "afp_first_job","coming_from_onp","coming_from_afp",
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
        if 'trecord_count' in counters:
            partner = request.env.user.partner_id
            values['trecord_count'] = request.env['t.record'].sudo().search_count([
                ('partner_id', '=', partner.id),
                ('state', '!=', 'draft'),
            ])
        return values


    def _prepare_contracts_domain(self, partner):
        employee = request.env.user.employee_id or request.env.user.partner_id.employee_ids
        return [
            ('employee_id','=',employee.id),
            ('employee_id','!=',False),
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



    @require_portal_checks
    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
            "action_url": "/my/account"
        })

        if post and request.httprequest.method == 'POST':
            # 🟢 Evitar errores con checkboxes (que no se mandan si no están marcados)
            for field in [
                'private_pension_system', 'national_pension_system',
                'coming_from_onp', 'coming_from_afp', 'afp_first_job'
            ]:
                post[field] = post.get(field, False)

            # 🔍 Obtener campos válidos desde el modelo res.partner
            partner_fields = request.env['res.partner'].sudo().fields_get()
            valid_keys = list(partner_fields.keys())

            # 🟡 Filtramos post para evitar errores por campos inexistentes
            safe_post = {k: v for k, v in post.items() if k in valid_keys}

            # 🟢 Convertir a int los IDs si existen
            for field in ['country_id', 'state_id']:
                if field in safe_post:
                    try:
                        safe_post[field] = int(safe_post[field])
                    except Exception:
                        safe_post[field] = False

            # 🟢 Ajuste si usas "zipcode"
            if 'zipcode' in safe_post:
                safe_post['zip'] = safe_post.pop('zipcode')

            # 🟢 Validación opcional solo para campos reales
            error, error_message = {}, []
            for field_name in self.MANDATORY_BILLING_FIELDS:
                if field_name in valid_keys and not post.get(field_name):
                    error[field_name] = 'missing'

            values.update({'error': error, 'error_message': error_message})
            values.update(post)

            if not error:
                safe_post['is_validate'] = True
                partner.sudo().write(safe_post)
                partner.sudo()._onchange_age()

                return request.redirect(redirect or '/my/documents')

        # 🔁 Datos auxiliares para renderizar la página
        values.update({
            'partner': partner,
            'countries': request.env['res.country'].sudo().search([]),
            'districts': request.env['l10n_pe.res.city.district'].sudo().search([]),
            'states': request.env['res.country.state'].sudo().search([]),
            'cities': request.env['res.city'].sudo().search([]),
            'genders': partner.gender,
            'education_levels': partner.education_level,
            'emergency_contact_relationships': partner.emergency_contact_relationship,
            'maritals': partner.marital,
            'child_relationship1s': partner.child_relationship1,
            'child_relationship2s': partner.child_relationship2,
            'child_relationship3s': partner.child_relationship3,
            'child_relationship4s': partner.child_relationship4,
            'child_relationship5s': partner.child_relationship5,
            'child_relationship6s': partner.child_relationship6,
            'child_gender1s': partner.child_gender1,
            'child_gender2s': partner.child_gender2,
            'child_gender3s': partner.child_gender3,
            'child_gender4s': partner.child_gender4,
            'child_gender5s': partner.child_gender5,
            'child_gender6s': partner.child_gender6,
            'familiar_relationship1s': partner.familiar_relationship1,
            'familiar_relationship2s': partner.familiar_relationship2,
            'familiar_relationship3s': partner.familiar_relationship3,
            'familiar_relationship4s': partner.familiar_relationship4,
            'familiar_relationship5s': partner.familiar_relationship5,
            'familiar_relationship6s': partner.familiar_relationship6,
            'familiar_relationship7s': partner.familiar_relationship7,
            'familiar_relationship8s': partner.familiar_relationship8,
            'familiar_relationship9s': partner.familiar_relationship9,
            'familiar_relationship10s': partner.familiar_relationship10,
            'familiar_gender1s': partner.familiar_gender1,
            'familiar_gender2s': partner.familiar_gender2,
            'familiar_gender3s': partner.familiar_gender3,
            'familiar_gender4s': partner.familiar_gender4,
            'familiar_gender5s': partner.familiar_gender5,
            'familiar_gender6s': partner.familiar_gender6,
            'familiar_gender7s': partner.familiar_gender7,
            'familiar_gender8s': partner.familiar_gender8,
            'familiar_gender9s': partner.familiar_gender9,
            'familiar_gender10s': partner.familiar_gender10,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response




    @require_portal_checks
    @http.route(['/my/applicant_documents'], type='http', auth='user', website=True)
    def applicant_documents(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        if post and request.httprequest.method == 'POST':
            update_values = {}
            # Modificado: Reemplazar familiar_dnifile por child_dnifile para los hijos
            if 'child_dnifile1' in post and post['child_dnifile1']:
                child_dnifile1_content = post['child_dnifile1'].read()
                child_dnifile1_base64 = base64.b64encode(child_dnifile1_content)
                update_values['child_dnifile1'] = child_dnifile1_base64
            if 'child_dnifile2' in post and post['child_dnifile2']:
                child_dnifile2_content = post['child_dnifile2'].read()
                child_dnifile2_base64 = base64.b64encode(child_dnifile2_content)
                update_values['child_dnifile2'] = child_dnifile2_base64
            if 'child_dnifile3' in post and post['child_dnifile3']:
                child_dnifile3_content = post['child_dnifile3'].read()
                child_dnifile3_base64 = base64.b64encode(child_dnifile3_content)
                update_values['child_dnifile3'] = child_dnifile3_base64
            if 'child_dnifile4' in post and post['child_dnifile4']:
                child_dnifile4_content = post['child_dnifile4'].read()
                child_dnifile4_base64 = base64.b64encode(child_dnifile4_content)
                update_values['child_dnifile4'] = child_dnifile4_base64
            if 'child_dnifile5' in post and post['child_dnifile5']:
                child_dnifile5_content = post['child_dnifile5'].read()
                child_dnifile5_base64 = base64.b64encode(child_dnifile5_content)
                update_values['child_dnifile5'] = child_dnifile5_base64
            if 'child_dnifile6' in post and post['child_dnifile6']:
                child_dnifile6_content = post['child_dnifile6'].read()
                child_dnifile6_base64 = base64.b64encode(child_dnifile6_content)
                update_values['child_dnifile6'] = child_dnifile6_base64
                
            # Modificado: Reemplazar familiar_dnifile_back por child_dnifile_back para los hijos
            if 'child_dnifile1_back' in post and post['child_dnifile1_back']:
                child_dnifile1_back_content = post['child_dnifile1_back'].read()
                child_dnifile1_back_base64 = base64.b64encode(child_dnifile1_back_content)
                update_values['child_dnifile1_back'] = child_dnifile1_back_base64
            if 'child_dnifile2_back' in post and post['child_dnifile2_back']:
                child_dnifile2_back_content = post['child_dnifile2_back'].read()
                child_dnifile2_back_base64 = base64.b64encode(child_dnifile2_back_content)
                update_values['child_dnifile2_back'] = child_dnifile2_back_base64
            if 'child_dnifile3_back' in post and post['child_dnifile3_back']:
                child_dnifile3_back_content = post['child_dnifile3_back'].read()
                child_dnifile3_back_base64 = base64.b64encode(child_dnifile3_back_content)
                update_values['child_dnifile3_back'] = child_dnifile3_back_base64
            if 'child_dnifile4_back' in post and post['child_dnifile4_back']:
                child_dnifile4_back_content = post['child_dnifile4_back'].read()
                child_dnifile4_back_base64 = base64.b64encode(child_dnifile4_back_content)
                update_values['child_dnifile4_back'] = child_dnifile4_back_base64
            if 'child_dnifile5_back' in post and post['child_dnifile5_back']:
                child_dnifile5_back_content = post['child_dnifile5_back'].read()
                child_dnifile5_back_base64 = base64.b64encode(child_dnifile5_back_content)
                update_values['child_dnifile5_back'] = child_dnifile5_back_base64
            if 'child_dnifile6_back' in post and post['child_dnifile6_back']:
                child_dnifile6_back_content = post['child_dnifile6_back'].read()
                child_dnifile6_back_base64 = base64.b64encode(child_dnifile6_back_content)
                update_values['child_dnifile6_back'] = child_dnifile6_back_base64

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
            'familiar_full_name5': partner.familiar_full_name5,
            'familiar_full_name6': partner.familiar_full_name6,
            'familiar_dni1': partner.familiar_dni1,
            'familiar_dni2': partner.familiar_dni2,
            'familiar_dni3': partner.familiar_dni3,
            'familiar_dni4': partner.familiar_dni4,
            'familiar_dni5': partner.familiar_dni5,
            'familiar_dni6': partner.familiar_dni6,
            'familiar_relationship1': partner.familiar_relationship1,
            'familiar_relationship2': partner.familiar_relationship2,
            'familiar_relationship3': partner.familiar_relationship3,
            'familiar_relationship4': partner.familiar_relationship4,
            'familiar_relationship5': partner.familiar_relationship5,
            'familiar_relationship6': partner.familiar_relationship6,
            # hijos
            'child_full_name1': partner.child_full_name1,
            'child_full_name2': partner.child_full_name2,
            'child_full_name3': partner.child_full_name3,
            'child_full_name4': partner.child_full_name4,
            'child_full_name5': partner.child_full_name5,
            'child_full_name6': partner.child_full_name6,
            'child_dni1': partner.child_dni1,
            'child_dni2': partner.child_dni2,
            'child_dni3': partner.child_dni3,
            'child_dni4': partner.child_dni4,
            'child_dni5': partner.child_dni5,
            'child_dni6': partner.child_dni6,
            'child_relationship1': partner.child_relationship1,
            'child_relationship2': partner.child_relationship2,
            'child_relationship3': partner.child_relationship3,
            'child_relationship4': partner.child_relationship4,
            'child_relationship5': partner.child_relationship5,
            'child_relationship6': partner.child_relationship6,
        }        
        values.update({
            'res_partner': res_partner_values,
            'partner': partner,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_partner_document',
            "action_url": "/my/applicant_documents"
        })
        
        response = request.render("mkt_recruitment.portal_my_partner_document", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


    def _is_first_contract(self, partner):
        """Check if user has only one draft contract without signed documents"""
        contracts_available = request.env['hr.contract'].sudo().search([
            ('employee_id.address_home_id', '=', partner.id),
            ('signature_state', '!=', 'canceled')
        ])
        recruitment_document_signed = request.env['recruitment.document'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'signed')
        ])

        if len(contracts_available) == 1:
            if contracts_available.state != 'draft':
                return False
            else:
                if recruitment_document_signed:
                    return False
                return True
        return False

    @require_portal_checks
    @http.route(['/my/contracts','/my/contracts/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        partner = request.env.user.partner_id

        # Check if this is first contract - redirect to compliance sign all if yes
        if self._is_first_contract(partner):
            return request.redirect('/portal/compliance/signall')

        values = self._prepare_portal_layout_values()
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
        
        partner = request.env.user.partner_id
        signature_short_name = partner._get_signature_name()

        values = {
            'contract_document': contract_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'employee_id': contract_sudo.employee_id.id,
            'report_type': 'html',
            'action': contract_sudo._get_portal_return_action(),
            'signature_short_name': signature_short_name
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
            contract_sudo.with_context(from_signed_function=True).write({'state': 'signed'})
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
        
        return {
            'force_refresh': True,
            'redirect_url': '/my/contracts',
        }


    @require_portal_checks
    @http.route(['/my/documents','/my/documents/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_documents(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        RecruitmentDocument = request.env['recruitment.document'].sudo()
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


    @require_portal_checks
    @http.route('/my/documents/<int:document_id>', type='http', auth='user', website=True)
    def portal_document_page(self, document_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            document_sudo = self._document_check_access('recruitment.document', document_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=document_sudo, report_type=report_type, report_ref="mkt_recruitment.report_recruitmentdocument_action", download=download)
        
        partner = request.env.user.partner_id
        signature_short_name = partner._get_signature_name()
        
        values = {
            'recruitment_document': document_sudo,
            'message': message,
            'token': access_token,
            'bootstrap_formatting': True,
            'partner_id': document_sudo.partner_id.id,
            'report_type': 'html',
            'action': document_sudo._get_portal_return_action(),
            'signature_short_name': signature_short_name
            
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

    @http.route(['/my/trecord', '/my/trecord/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_trecords(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        domain = [('partner_id', '=', partner.id), ('state', '!=', 'draft')]
        TRecord = request.env['t.record'].sudo()
        total = TRecord.search_count(domain)

        pager = portal_pager(
            url="/my/trecord",
            total=total,
            page=page,
            step=20
        )
        trecords = TRecord.search(domain, limit=20, offset=pager['offset'], order='id desc')

        values.update({
            'trecords': trecords,
            'page_name': 'trecord',   # <- Para breadcrumbs del XML
            'pager': pager,
        })
        return request.render('mkt_recruitment.portal_my_trecords', values)

    @http.route(['/my/trecord/<int:record_id>'], type='http', auth='public', website=True)
    def portal_trecord_page(self, record_id=None, access_token=None, report_type=None, download=False, **kw):
        rec = request.env['t.record'].sudo().browse(record_id)
        if not rec.exists():
            return request.not_found()
        if not rec.access_token:
            rec._compute_access_url()

        # Permisos: dueño o con access_token
        allowed = False
        user = request.env.user
        if user and not user._is_public():
            allowed = (rec.partner_id == user.partner_id)
        if access_token and access_token == rec.access_token:
            allowed = True
        if not allowed:
            return request.redirect('/my')

        # Nombre corto para la firma (se usa en el template)
        partner = request.env.user.partner_id
        try:
            sig_name = partner._get_signature_name() if callable(getattr(partner, '_get_signature_name', None)) else partner.name
        except Exception:
            sig_name = partner.name

        # Si piden el PDF directo
        if report_type == 'pdf':
            if not rec.t_record:
                return request.not_found()
            pdf_bytes = base64.b64decode(rec.t_record)
            headers = [('Content-Type', 'application/pdf'), ('Content-Length', str(len(pdf_bytes)))]
            if download:
                filename = (rec.t_record_filename or 'T-record.pdf').replace(' ', '_')
                headers.append(('Content-Disposition', f'attachment; filename="{filename}"'))
            return request.make_response(pdf_bytes, headers)

        # Render de la página (usa el template que hereda portal.portal_sidebar)
        values = {
            'trecord_document': rec,
            'report_type': report_type or 'html',
            'message': kw.get('message'),
            'page_name': 'trecord',            # <- IMPORTANTE: coincide con el XML
            'signature_short_name': sig_name,  # <- lo usa el signature_form por defecto
        }
        return request.render('mkt_recruitment.trecord_document_portal_template', values)

    @http.route('/my/trecord/<int:record_id>/request_code', type='json', auth='user', website=True)
    def trecord_request_code(self, record_id, method='email', **kw):
        rec = request.env['t.record'].sudo().browse(record_id)
        _logger.info("trecord_request_code record_id:%s method:%s user:%s", record_id, method, request.env.user.id)
        if not rec or rec.partner_id != request.env.user.partner_id:
            _logger.warning("request_code denied: rec:%s partner_mismatch", rec and rec.id)
            return {'error': _('Not allowed.')}
        try:
            if method == 'sms':
                res = rec.send_sms_to_validate_trecord()
            else:
                res = rec.send_email_to_validate_trecord()
            request.env.cr.commit()
            _logger.info("request_code result record_id:%s -> %s", record_id, res)
            return res or {'success': True}
        except ValidationError as e:
            _logger.warning("request_code ValidationError record_id:%s -> %s", record_id, e)
            return {'error': e.name or str(e)}
        except Exception as e:
            _logger.exception("request_code Exception record_id:%s", record_id)
            request.env['ir.logging'].sudo().create({
                'name': 'trecord_request_code',
                'type': 'server',
                'level': 'ERROR',
                'dbname': request.db,
                'message': f'Error request_code: {e}',
                'path': 'mkt_recruitment.controllers',
                'line': '0',
                'func': 'trecord_request_code',
            })
            return {'error': _('Error sending code.')}

    @http.route('/my/trecord/<int:record_id>/sign', type='json', auth='user', website=True)
    def trecord_portal_sign(self, record_id, access_token=None, name=None, signature=None, digits=None):
        access_token = access_token or request.httprequest.args.get('access_token')
        rec = request.env['t.record'].sudo().browse(record_id)
        _logger.info("trecord_portal_sign record_id:%s user:%s name:%s sig_len:%s digits:%s",
                     record_id, request.env.user.id, name, len(signature or '') if signature else 0, digits)

        if not rec.exists():
            _logger.warning("trecord_portal_sign invalid document id:%s", record_id)
            return {'error': _('Invalid document.')}

        allowed = (not request.env.user._is_public() and rec.partner_id == request.env.user.partner_id)
        if access_token and access_token == rec.access_token:
            allowed = True
        if not allowed:
            _logger.warning("trecord_portal_sign access denied id:%s", record_id)
            return {'error': _('Access denied.')}

        if not signature or not digits:
            _logger.warning("trecord_portal_sign missing signature/digits id:%s", record_id)
            return {'error': _('Signature and code are required.')}

        # Normaliza firma si viene como dataURL
        try:
            if isinstance(signature, str) and signature.startswith('data:image'):
                header, b64data = signature.split(',', 1)
                _logger.info("trecord_portal_sign signature header:%s ... stripped", header[:32])
                signature = b64data
        except Exception:
            _logger.exception("trecord_portal_sign error stripping signature header")
            return {'error': _('Invalid signature data.')}

        try:
            rec.action_portal_sign_and_stamp(name, signature, ''.join(str(d) for d in str(digits))[:4])
            request.env.cr.commit()
            _logger.info("trecord_portal_sign success id:%s", record_id)
        except ValidationError as e:
            _logger.warning("trecord_portal_sign ValidationError id:%s -> %s", record_id, e)
            return {'error': e.name or str(e)}
        except Exception:
            _logger.exception("trecord_portal_sign Exception id:%s", record_id)
            return {'error': _('Error processing signature.')}

        # return {'force_refresh': True, 'redirect_url': '/my/trecord'}
        return {'force_refresh': True}

    @http.route('/trecord/verify/<string:token>', type='http', auth='public', website=True, sitemap=False)
    def trecord_public_pdf(self, token=None, download=False, **kw):
        """Entrega el PDF de T-Record por access_token, sin login."""
        if not token:
            return request.not_found()

        rec = request.env['t.record'].sudo().search([('access_token', '=', token)], limit=1)
        if not rec or not rec.t_record:
            _logger.warning("trecord_public_pdf token not found or empty pdf: %s", token)
            return request.not_found()

        # Opcional: bloquear si está en draft
        if rec.state == 'draft':
            _logger.warning("trecord_public_pdf draft state blocked: %s", rec.id)
            return request.not_found()

        pdf_bytes = base64.b64decode(rec.t_record)
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', str(len(pdf_bytes))),
        ]
        if download:
            filename = (rec.t_record_filename or 'T-record.pdf').replace(' ', '_')
            headers.append(('Content-Disposition', f'attachment; filename="{filename}"'))

        _logger.info("trecord_public_pdf ok id:%s token:%s", rec.id, token[:8] + '...')
        return request.make_response(pdf_bytes, headers)