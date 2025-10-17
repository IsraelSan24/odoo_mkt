from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo.exceptions import UserError, ValidationError, AccessDenied, AccessError, MissingError
from odoo import _, SUPERUSER_ID
import binascii
import base64
import json

import logging

_logger = logging.getLogger(__name__)

class PortalCompliance(portal.CustomerPortal):
    # portal.CustomerPortal.MANDATORY_BILLING_FIELDS.remove("city")
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

    def _is_first_contract(self, partner):
        contracts_available = request.env['hr.contract'].sudo().search([('employee_id.address_home_id', '=', partner.id), ('signature_state', '!=', 'canceled')])
        recruitment_document_signed = request.env['recruitment.document'].sudo().search([('partner_id', '=', partner.id), ('state', '=', 'signed')])

        if len(contracts_available) == 1:
            if contracts_available.state != 'draft':
                return False
            
            else:
                if recruitment_document_signed:
                    return False

                return True
        return False
        

    @http.route(['/my/home', '/my'], type='http', auth='user', website=True, inherit=True)
    def home(self, **kw):
        partner = request.env.user.partner_id

        # if self._needs_compliance(partner) and not request.httprequest.path.startswith('/portal/compliance/'):
        if partner.requires_compliance_process and not request.httprequest.path.startswith('/portal/compliance/'):
            return request.redirect('/portal/compliance/step/1')
        
        return super().home(**kw)
    
    @http.route(['/portal/compliance/step/<int:step>'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def compliance_step(self, step=1, **post):
        partner = request.env.user.partner_id

        if partner.requires_compliance_process and not request.httprequest.path.startswith('/portal/compliance/'):
            return request.redirect('/my/home')

        
        if request.httprequest.method == 'POST':
            if step == 1:

                applicant_partner = request.env['applicant.partner'].sudo().search([('dni', '=', partner.vat)], limit=1, order='create_date desc')

                partner_fields = [
                        'name',
                        'dni',
                        'email',
                        'gender',
                        'phone',
                        'birthday',
                        'marital',
                        'nationality_id',
                        'identification_type_id',
                        'children',
                        'emergency_contact',
                        'emergency_phone',
                        'emergency_contact_relationship',
                        'age',
                        'country_id',
                        'state_id',
                        'city_id',
                        'district_id',
                        'zip',
                        'street',
                        'reference_location',
                        'child_dni1',
                        'child_dni2',
                        'child_dni3',
                        'child_dni4',
                        'child_dni5',
                        'child_dni6',
                        'child_full_name1',
                        'child_full_name2',
                        'child_full_name3',
                        'child_full_name4',
                        'child_full_name5',
                        'child_full_name6',
                        'child_birthday1',
                        'child_birthday2',
                        'child_birthday3',
                        'child_birthday4',
                        'child_birthday5',
                        'child_birthday6',
                        'child_gender1',
                        'child_gender2',
                        'child_gender3',
                        'child_gender4',
                        'child_gender5',
                        'child_gender6',
                        'child_relationship1',
                        'child_relationship2',
                        'child_relationship3',
                        'child_relationship4',
                        'child_relationship5',
                        'child_relationship6',
                        'child_address1',
                        'child_address2',
                        'child_address3',
                        'child_address4',
                        'child_address5',
                        'child_address6',
                        'familiar_dni1',
                        'familiar_dni2',
                        'familiar_dni3',
                        'familiar_dni4',
                        'familiar_dni5',
                        'familiar_dni6',
                        'familiar_dni7',
                        'familiar_dni8',
                        'familiar_dni9',
                        'familiar_dni10',
                        'familiar_address1',
                        'familiar_address2',
                        'familiar_address3',
                        'familiar_address4',
                        'familiar_address5',
                        'familiar_address6',
                        'familiar_address7',
                        'familiar_address8',
                        'familiar_address9',
                        'familiar_address10',
                        'familiar_birthday1',
                        'familiar_birthday2',
                        'familiar_birthday3',
                        'familiar_birthday4',
                        'familiar_birthday5',
                        'familiar_birthday6',
                        'familiar_birthday7',
                        'familiar_birthday8',
                        'familiar_birthday9',
                        'familiar_birthday10',
                        'familiar_full_name1',
                        'familiar_full_name2',
                        'familiar_full_name3',
                        'familiar_full_name4',
                        'familiar_full_name5',
                        'familiar_full_name6',
                        'familiar_full_name7',
                        'familiar_full_name8',
                        'familiar_full_name9',
                        'familiar_full_name10',
                        'familiar_gender1',
                        'familiar_gender2',
                        'familiar_gender3',
                        'familiar_gender4',
                        'familiar_gender5',
                        'familiar_gender6',
                        'familiar_gender7',
                        'familiar_gender8',
                        'familiar_gender9',
                        'familiar_gender10',
                        'familiar_relationship1',
                        'familiar_relationship2',
                        'familiar_relationship3',
                        'familiar_relationship4',
                        'familiar_relationship5',
                        'familiar_relationship6',
                        'familiar_relationship7',
                        'familiar_relationship8',
                        'familiar_relationship9',
                        'familiar_relationship10',
                        'is_beneficiary1',
                        'is_beneficiary2',
                        'is_beneficiary3',
                        'is_beneficiary4',
                        'is_beneficiary5',
                        'is_beneficiary6',
                        'is_beneficiary7',
                        'is_beneficiary8',
                        'is_beneficiary9',
                        'is_beneficiary10',
                        'private_pension_system',
                        'afp_first_job',
                        'coming_from_onp',
                        'coming_from_afp',
                        'national_pension_system',
                        'education_level',
                        'education_start_date',
                        'education_end_date',
                        'institution',
                        'profession',
                ]

                ## Optional Fields
                optional_fields = [
                    'emergency_contact',
                    'emergency_phone',
                    'emergency_contact_relationship',
                    'reference_location',
                    'education_end_date',
                ]

                # for optional_field in optional_fields:
                #     if not post.get(optional_field):
                #         post[optional_field] = False

                ## ID fields str -> int
                id_fields = [
                    'identification_type_id',
                    'nationality_id',
                    'country_id',
                    'state_id',
                    'city_id',
                    'district_id',
                ]

                for field in id_fields:
                    if field:
                        post[field] = int(post[field])

                ## All fileds if they are not filled
                for field in partner_fields:
                    if field not in list(post.keys()):
                        post[field] = False


                _logger.info(f"\n\n-{post}-\n\n")


                applicant_partner.sudo().write(post)
                applicant_partner.sudo().update_partner()

                existing_document_ddjj = request.env['recruitment.document'].sudo().with_context().search([('partner_id', '=', partner.id)], limit=1)
                if not existing_document_ddjj:
                    partner.sudo().button_send_documents()

                else:
                    existing_document_ddjj.sudo().write_data()


                partner = request.env['res.partner'].sudo().browse(partner.id)
                return request.redirect('/portal/compliance/step/2')
                  
            if step == 2:
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
          
                    return request.redirect('/portal/compliance/step/3')
            
            if step == 3:
                partner.sudo().write({'requires_compliance_process': False})
                # partner.sudo().write({'is_validate': True})
                return request.redirect('/my/home')
            
        values = {'step': step, 'error': {}, 'error_message': [], 'compliance_process': partner.requires_compliance_process, "action_url": f"/portal/compliance/step/{step}"}

        if step == 1:
            applicant_partner = request.env['applicant.partner'].sudo().search([('dni', '=', partner.vat)], limit=1, order='create_date desc')
        
            if not applicant_partner:
                request.env['applicant.partner'].sudo().create({
                    'dni': partner.vat,
                    'name': partner.name,
                    'email': partner.personal_email,
                    'phone': partner.phone,
                })


            countries = request.env['res.country'].sudo().search([('code','=','PE')])
            states = request.env['res.country.state'].sudo().search([('country_id.code','=','PE')])
            cities = request.env['res.city'].sudo().search([])
            districts = request.env['l10n_pe.res.city.district'].sudo().search([])
            nationalities = request.env['res.country'].sudo().search([('demonym','!=',False)])
            identifications = request.env['l10n_latam.identification.type'].sudo().search([
                ('name', 'in', ('DNI', 'PTP', 'Pasaporte', 'Cédula Extranjera', 'Carnet de Extranjeria'))
            ])

            values.update({
                # 'partner': partner,
                'countries': countries,
                'states': states,
                'districts': districts,
                'cities': cities,
                'nationalities': nationalities,
                'identifications': identifications,
            })

            ## Chidren data to load if needed 
            children_data = []
            for i in range(6):
                dni = getattr(partner, f'child_dni{i+1}', '') or ''
                full_name = getattr(partner, f'child_full_name{i+1}', '') or ''
                birthday = getattr(partner, f'child_birthday{i+1}', None)
                relationship = getattr(partner, f'child_relationship{i+1}', '') or ''
                gender = getattr(partner, f'child_gender{i+1}', '') or ''
                address = getattr(partner, f'child_address{i+1}', '') or ''

                # Solo agregar si hay datos reales
                if any([dni, full_name, birthday, relationship, gender, address]):
                    children_data.append({
                        'dni': dni,
                        'full_name': full_name,
                        'birthday': birthday.isoformat() if birthday else '',
                        'relationship': relationship,
                        'gender': gender,
                        'address': address,
                    })

            values.update({
                'partner': partner,
                'children_data_json': json.dumps(children_data),
            })

            ## First beneficiaries data to load if needed
            first_beneficiaries = []
            n_first_beneficiaries = 0
            for i in range(6):
                dni = getattr(partner, f'familiar_dni{i+1}', '') or ''
                full_name = getattr(partner, f'familiar_full_name{i+1}', '') or ''
                birthday = getattr(partner, f'familiar_birthday{i+1}', None)
                relationship = getattr(partner, f'familiar_relationship{i+1}', '') or ''
                gender = getattr(partner, f'familiar_gender{i+1}', '') or ''
                address = getattr(partner, f'familiar_address{i+1}', '') or ''
                is_beneficiary = getattr(partner, f'is_beneficiary{i+1}', '') or ''
                

                _logger.info(f"\n\n-{dni}-{full_name}-{birthday}-{relationship}-{gender}-{address}-\n\n")

                # Solo agregar si hay datos reales
                if any([dni, full_name, birthday, relationship, gender, address]):
                    first_beneficiaries.append({
                        'dni': dni,
                        'full_name': full_name,
                        'birthday': birthday.isoformat() if birthday else '',
                        'relationship': relationship,
                        'gender': gender,
                        'address': address,
                        'is_beneficiary': is_beneficiary,
                    })
                    n_first_beneficiaries += 1
                
            values.update({
                'n_first_beneficiaries': n_first_beneficiaries,
                'first_beneficiaries_data_json': json.dumps(first_beneficiaries),
            })


            ## Other beneficiary data to load if needed
            other_beneficiary = []
            n_other_beneficiary = 0
            for i in range(3):
                dni = getattr(partner, f'familiar_dni{i+7}', '') or ''
                full_name = getattr(partner, f'familiar_full_name{i+7}', '') or ''
                birthday = getattr(partner, f'familiar_birthday{i+7}', None)
                relationship = getattr(partner, f'familiar_relationship{i+7}', '') or ''
                gender = getattr(partner, f'familiar_gender{i+7}', '') or ''
                address = getattr(partner, f'familiar_address{i+7}', '') or ''
                is_beneficiary = getattr(partner, f'is_beneficiary{i+7}', '') or ''
                

                _logger.info(f"\n\n-{dni}-{full_name}-{birthday}-{relationship}-{gender}-{address}-\n\n")

                # Solo agregar si hay datos reales
                if any([dni, full_name, birthday, relationship, gender, address]):
                    other_beneficiary.append({
                        'dni': dni,
                        'full_name': full_name,
                        'birthday': birthday.isoformat() if birthday else '',
                        'relationship': relationship,
                        'gender': gender,
                        'address': address,
                        'is_beneficiary': is_beneficiary,
                    })
                    n_other_beneficiary += 1
                
            values.update({
                'n_other_beneficiary': n_other_beneficiary,
                'other_beneficiary_data_json': json.dumps(other_beneficiary),
            })


            return http.request.render('mkt_recruitment.applicantpartner', values)
                  
        elif step == 2:
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
                'page_name': 'my_partner_document',
            })
            
            response = request.render("mkt_recruitment.portal_my_partner_document", values)
            response.headers['X-Frame-Options'] = 'DENY'
            return response

        elif step == 3:
            first_recruitment_document = request.env['recruitment.document'].sudo().search([('partner_id', '=', partner.id)], limit=1, order='create_date desc')

            values.update({
                'recruitment_document': first_recruitment_document,
                'message': False,
                'token': first_recruitment_document.access_token,
                'bootstrap_formatting': True,
                'partner_id': first_recruitment_document.partner_id.id,
                'report_type': 'html',
                'action': first_recruitment_document._get_portal_return_action(),
            })
            html = request.env['ir.ui.view']._render_template(
                'mkt_recruitment.recruitment_document_portal_template',
                values
            )
                
            return html
         

    @http.route('/portal/compliance/signall/sign', type='json', auth='user', website=True)
    def portal_contract_and_recruitment_document_sign(self, access_token=None, name=None, signature=None):
        employee = request.env.user.employee_id or request.env.user.partner_id.employee_ids
        partner = request.env.user.partner_id

        first_contract = request.env['hr.contract'].sudo().search([('employee_id', '=', employee.id)], limit=1, order='create_date desc')
        first_recruitment_document = request.env['recruitment.document'].sudo().search([('partner_id', '=', partner.id)], limit=1, order='create_date desc')

        access_token = access_token or request.httprequest.args.get('access_token')

        ## SIGN RECRUITMENT DOCUMENTS
        if not first_recruitment_document.has_to_be_signed():
            return {'error': _('The document is not in a state requiring applicant signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}
        
        try:
            first_recruitment_document.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'applicant_signature': signature,
                'state': 'signed',
            })
            first_recruitment_document.send_email_to_employee_signed()
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}
        try:
            first_recruitment_document.write_data()
        except:
            pass
        
        # pdf_recruitment_document = request.env.ref('mkt_recruitment.report_recruitmentdocument_action').with_user(SUPERUSER_ID)._render_qweb_pdf([first_recruitment_document.id])[0]

        ## SIGN CONTRACT
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            first_contract.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'contract_signature': signature,
                'signature_state': 'signed',
            })
            first_contract.with_context(from_signed_function=True).write({'state': 'signed'})
            first_contract.send_email_to_employee_signed()
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}
        try:
            applicant = request.env['hr.applicant'].sudo().search([('emp_id','=',first_contract.employee_id.id)])
            if applicant:
                applicant.write({
                    'stage_id': request.env['hr.recruitment.stage'].sudo().search([('hired_stage','=',True)]).id,
                })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid data.')}

        # pdf_contract = request.env.ref('mkt_recruitment.report_contract_action').with_user(SUPERUSER_ID)._render_qweb_pdf([first_contract.id])[0]

        query_string = '&message=sign_ok'

        return {
            'force_refresh': True,
            'redirect_url': '/my/home',
        }

    @http.route('/portal/compliance/signall', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_sign_all(self, **post):
        partner = request.env.user.partner_id
        is_first_contract = self._is_first_contract(partner)

        if not is_first_contract:
            return request.redirect('/my/contracts')

        if request.httprequest.method == 'POST':
            return request.redirect('/my/contracts')

        values = {'error': {}, 'error_message': [], "action_url": f"portal/compliance/signall"}

        employee = request.env.user.employee_id or request.env.user.partner_id.employee_ids
        if len(employee) != 1 or not employee :
            raise ValidationError("Más de 1 empleado, o ninguno asociado a este usuario.")
        
        first_contract = request.env['hr.contract'].sudo().search([('employee_id', '=', employee.id)], limit=1, order='create_date desc')
        first_recruitment_document = request.env['recruitment.document'].sudo().search([('partner_id', '=', partner.id)], limit=1, order='create_date desc')

        if first_contract.is_sended:
            values = {
                'is_first_contract': is_first_contract,
                'contract_document': first_contract,
                'message': False,
                'token': first_contract.access_token,
                'bootstrap_formatting': True,
                'employee_id': first_contract.employee_id.id,
                'report_type': 'html',
                'action': first_contract._get_portal_return_action(),
                'recruitment_document': first_recruitment_document
            }
            html = request.env['ir.ui.view']._render_template(
                'mkt_recruitment.contract_document_portal_template',
                values
            )
            return html
    
        else:
            raise MissingError("Your first contract hasn't been generated yet, please wait to your recruiter's indication.")


    @http.route(['/my/contracts','/my/contracts/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        partner = request.env.user.partner_id
        
        if self._is_first_contract(partner):
            _logger.info(f"\n\nEs primer contrato\n\n")
            return request.redirect('/portal/compliance/signall')

        # 🔁 Si no, seguimos con la lógica normal del portal
        return super().portal_my_contracts(page=page, date_begin=date_begin, date_end=date_end, sortby=sortby, **kw)

