from odoo import _, api, fields, models, Command
from datetime import timedelta
from odoo.exceptions import UserError, AccessError
from odoo.addons.mkt_recruitment.models.apiperu import apiperu_dni
import logging
_logger = logging.getLogger(__name__)


class Applicant(models.Model):
    _inherit = 'hr.applicant'

    vat = fields.Char(string='Vat')
    photo = fields.Image(string='Photo')
    is_autoemployee = fields.Boolean(default=False, compute='_compute_auto_employee_and_documents', string='Employee created from stage', store=True)
    has_documents = fields.Boolean(default=False, compute='_compute_auto_employee_and_documents', string='Document created from stage', store=True)
    hr_responsible_contract_id = fields.Many2one(comodel_name='res.users', string='Approved by')
    applicant_partner_id = fields.Many2one(comodel_name='applicant.partner', string='Applicant partner')
    is_reinstatement = fields.Boolean(default=False, string='Is reinstatement', store=True)

    first_contract_id = fields.Many2one('hr.contract', string=_("First Contract"), ondelete='set null', tracking=True)
    _sql_constraints = [
        ('unique_first_contract_id', 'UNIQUE(first_contract_id)', 'Este contrato ya está asignado a otro postulante.')
    ]

    first_contract_type_id = fields.Many2one('hr.contract.type', string=_("First Contract Type"))
    first_contract_signed = fields.Boolean(
        string=_("Is First Contract Signed?"),
        compute="_compute_first_contract_signed",
        store=True
    )
    first_contract_start = fields.Date(string=_("First Contract Start Date"), tracking=True) 
    first_contract_end = fields.Date(string=_("First Contract End Date"), tracking=True)
    send_first_contract = fields.Boolean(string=_("Send Contract"))

    cost_center_id = fields.Many2one('cost.center', string="Cost Center", tracking=True)
    selected_applicant_approved = fields.Boolean(string=_("Is selected applicant approved?"), tracking=True)
    supervision_data_approved = fields.Selection([
                                    ('pending', 'Pending'),
                                    ('approved', 'Approved'),
                                    ('rejected', 'Rejected'),
                                ], string='Supervision Status', tracking=True)
    supervision_data_sent = fields.Boolean(_("Is supervision data sent?"), tracking=True, default=False) 

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    work_type = fields.Selection([
        ('week_end', 'Fin de Semana'),
        ('fix_without_mobility', 'Fijo sin Movilidad'),
        ('fix_with_mobility', 'Fijo con Movilidad'),
        ],
        string=_('Condición'))

    parent_id = fields.Many2one('hr.employee', 'Jefe Directo', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.model
    def _init_data(self):
        ICP = self.env['ir.config_parameter'].sudo()
        
        # Verificar si ya se ejecutó
        if ICP.get_param('mkt_recruitment.init_data_executed'):
            return
        
        for rec in self.search([]):
            if rec.selected_applicant_approved and rec.supervision_data_approved == 'approved':
                employee_first_contract = rec.env['hr.contract'].search([('employee_id', '=', rec.emp_id.id)], order='create_date asc', limit=1)
                _logger.info(f"\n\n\nINITDATA: {employee_first_contract}\n\n")

                if employee_first_contract and not rec.first_contract_id and (rec.salary_proposed == employee_first_contract.wage) and (rec.first_contract_start == employee_first_contract.date_start) and (rec.first_contract_end == employee_first_contract.date_end):
                    _logger.info(f"\n\n\nINITDATA: {employee_first_contract.is_sended}-{employee_first_contract.id}-{employee_first_contract.contract_type_id.id}\n\n")
                    rec.with_context(skip_contract_sync=True).write({
                        "send_first_contract": employee_first_contract.is_sended or False,
                        "first_contract_id": employee_first_contract.id or False,
                        "first_contract_type_id": employee_first_contract.contract_type_id.id or False,
                    })

        ICP.set_param('mkt_recruitment.init_data_executed', 'True')



    def write(self, vals):
        if 'stage_id' in vals:
            new_stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            if not new_stage.exists():
                raise UserError(_("El nuevo estado no es válido."))
            
            # restrict if not in group
            if new_stage.id == 4 and not self.env.user.has_group('mkt_supervision.group_supervision_hiring_approver'):
                _logger.info(f"\n\n\nHRAPPLICANT RESTRICT GROUP\n\n\n")
                raise AccessError(_("You don't have permissions to move candidates to this stage."))


            _logger.info(f"\n\n\nHR APPLICANT PASSED\n\n\n")
            for rec in self:
                if not rec.stage_id:
                    raise UserError(_("El registro no tiene un estado actual asignado."))
                if abs(new_stage.sequence - rec.stage_id.sequence) > 1:
                    raise UserError(_("Solo puedes cambiar el estado al siguiente o anterior en la vista Kanban."))
        
        res = super(Applicant, self).write(vals)
        
        for rec in self:
            if rec.partner_id:
                for partner in rec.partner_id:
                    partner.write({
                        'belong_applicant_id': rec.id
                    })
        
        return res


    def _message_post_after_hook(self, message, msg_vals):
        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                if new_partner.create_date.date() == fields.Date.today():
                    new_partner.write({
                        'name': self.partner_name,
                        'type': 'private',
                        'phone': self.partner_phone,
                        'mobile': self.partner_mobile,
                        'l10n_latam_identification_type_id': self.env['l10n_latam.identification.type'].search([('name','=','DNI')]).id,
                        'vat': self.vat,
                        'image_1920': self.photo,
                        'personal_email': self.email_from,
                    })
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(Applicant, self)._message_post_after_hook(message, msg_vals)


    @api.depends('stage_id')
    def _compute_auto_employee_and_documents(self):
        for rec in self:
            # Si el stage es el inicial (id = 1), omitir la validación
            if rec.stage_id.id == 1:
                continue

            # Solo aplicar la validación en los stages 2, 3 o 4
            if rec.stage_id.id in (2, 3, 4):
                look_for_employee = rec.env['hr.employee'].search([
                    ('address_home_id.vat', '=', rec.vat)
                ], limit=1)

                if look_for_employee and not rec.is_autoemployee:
                    raise UserError(_("An active employee exists with this DNI %s (%s). It is necesary to terminate the employee before trying to continue with a new recruitment process.") % (rec.vat, look_for_employee.name))
            rec.contact_merge_stage()
            rec.update_data_partner()
            rec.create_employee_by_stage()
            rec.access_portal_partner()

    @api.depends("first_contract_id.signed_by")
    def _compute_first_contract_signed(self):
        for rec in self:
            if rec.first_contract_id:
                contract = rec.first_contract_id
                rec.first_contract_signed = bool(contract.signed_by) if contract else False

    def update_data_partner(self):
        if self.stage_id.update_data:
            applicant_partner = self.env['applicant.partner'].search([('dni','=',self.vat)], order='create_date desc')
            if applicant_partner and applicant_partner.state != 'uploaded':
                applicant_partner.update_partner()


    def contact_merge_stage(self):
        if self.stage_id.contact_merge:
            contact = self.env['res.partner'].search([('vat', '=', self.vat)], order='create_date asc')
            if contact and len(contact) == 2:
                # Asignar como destino el más reciente
                partner_ids_sorted = [contact[0].id, contact[1].id]
                dst_partner = contact[1]  # Más reciente

                context = dict(self.env.context)
                context.update({
                    'active_model': 'res.partner',
                    'active_ids': partner_ids_sorted,
                })

                contact_merge = self.env['base.partner.merge.automatic.wizard'].with_context(context).create({
                    'partner_ids': [Command.set(partner_ids_sorted)],
                    'dst_partner_id': dst_partner.id,
                    'state': 'selection',
                })
                contact_merge.action_merge()


    def access_portal_partner(self):
        if self.stage_id.access_portal:
            contact = self.env['res.partner'].search([('vat','=',self.vat)], order='create_date desc')

            if not contact:
                raise UserError(_('No contacts were found with the same DNI, please solve the problem to continue with the process.'))
            
            if len(contact) > 1:
                raise UserError(_('More than one contact has been found with the same DNI, please solve the problem to continue with the process.'))

            self.hr_responsible_contract_id = self.env.user.id

            # Verify if user associated to that contact exist
            user = self.env['res.users'].sudo().with_context(active_test=False).search([('partner_id', '=', contact.id)], limit=1)
            employee = self.env['hr.employee'].sudo().search([('address_home_id', '=', contact.id)], limit=1)

            password = str(contact.vat)
            if not user:
                user = self.env['res.users'].with_context(no_reset_password=True).sudo().create({
                    'name': contact.name,
                    'login': contact.email,
                    'partner_id': contact.id,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                })

                user.password = password

                if employee:
                    employee.write({
                        'user_id': user.id
                    })
                self._send_email_with_credentials(user, contact)
            else:
                if user.active:
                    user.sudo().write({
                        'password': password,
                        'login': self.email_from,
                    })
                    self._send_email_with_credentials(user, contact)
                    _logger.info(f"User {user.login} already exists and is active.")

                else:
                    user.sudo().write({
                        'password': password,
                        'login': self.email_from,
                    })
                    
                    user.sudo().toggle_active()
                    if employee:
                        employee.write({
                            'user_id': user.id
                        })
                    self._send_email_with_credentials(user, contact)


    def _send_email_with_credentials(self, user, contact):

        # Send email with credentials
        template = self.env.ref('mkt_recruitment.mail_new_user_credentials')

        mail = False

        if template:
            mail_id = template.sudo().send_mail(self.id, force_send=True)
            mail = self.env['mail.mail'].browse(mail_id)

        else:
            mail_obj = self.env['mail.mail'].sudo()
            subject = 'Marketing Alterno - Acceso al Portal ODOO'
            body_html = f"""
                    Hola {user.name},<br/><br/>
                    Tu cuenta del portal ODOO ha sido creada.<br/>
                    <b>Usuario:</b> {user.login}<br/>
                    <b>Tu contraseña es tu número de identificación.<br/><br/>
                    Puedes ingresar aquí: <a href="{self.env['ir.config_parameter'].sudo().get_param('web.base.url.home')}">Portal</a><br/><br/>
                """
            mail = mail_obj.create({
                'subject': subject,
                'body_html': body_html,
                'email_to': contact.personal_email or contact.email,
            })
            mail.send()

        if mail.state in ['outgoing', 'sent', 'received']:
            return {'success': True, 'message': _('Email sent successfully.')}
        elif mail.state == 'exception':
            return {'success': False, 'message': _('Error sending email: %s' % mail.failure_reason)}



    def create_employee_by_stage(self):
        employee = False
        if not self.is_autoemployee and self.stage_id.employee_stage:
            look_for_employee = self.env['hr.employee'].search([('address_home_id.vat', '=', self.vat)], limit=1)
            if look_for_employee:
                raise UserError(_("An active employee exists with this DNI %s (%s). It is necesary to terminate the employee before trying to continue with a new recruitment process.") % (self.vat, look_for_employee.name))

            contact_name = False
            if self.partner_id:
                address_id = self.partner_id.address_get(['contact'])['contact']
                contact_name = self.partner_id.display_name
            else:
                # Creates a partner if applicant is not associated to a partner
                if not self.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': self.partner_name,
                    'email': self.email_from,
                    'phone': self.partner_phone,
                    'mobile': self.partner_mobile,
                    'vat': self.vat or False
                })
                self.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            if self.partner_name or contact_name:
                values = {
                    'name': self.partner_name or contact_name,
                    'job_id': self.job_id.id,
                    'job_title': self.job_id.name,
                    'address_home_id': address_id,
                    'department_id': self.department_id.id or False,
                    'address_id': self.company_id and self.company_id.partner_id
                            and self.company_id.partner_id.id or False,
                    'work_phone': self.department_id.company_id.phone,
                    'applicant_id': self.ids,
                    'image_1920': self.photo,
                    'identification_id': self.partner_id.vat or False,
                    # 'cost_center_id': self.cost_center_id.id or False
                }
                self.env['hr.employee'].create(values)
                self.partner_id.write({
                    'requires_compliance_process': True,
                    't_and_c_login': True
                })

                if self.partner_id.is_validate:
                    self.partner_id.write({'is_validate': False})
                
                if self.partner_id.document_okay:
                    self.partner_id.write({'document_okay': False})
                
                if self.partner_id.children_okay:
                    self.partner_id.write({'children_okay': False})


                self.is_autoemployee = True


    def create_first_contract(self):
        employee_contract_history = self.env['hr.contract.history'].search([('employee_id', '=', self.emp_id.id)])
        
        if (not employee_contract_history or len(employee_contract_history) == 1):
            if not employee_contract_history.contract_id:
                values = {
                'employee_id': self.emp_id.id,
                'date_start': self.first_contract_start,
                'date_end': self.first_contract_end,
                'wage': self.salary_proposed,
                'structure_type_id': 1,
                'is_renovation': False,
                'department_id': self.emp_id.department_id.id,
                'job_id': self.emp_id.job_id.id,
                'contract_type_id': self.first_contract_type_id.id or False,
                }
                first_contract = self.env['hr.contract'].sudo().create(values)
                first_contract._compute_contract_duration()

    @api.model
    def create(self, vals):
        vat = vals.get('vat')
        if vat and len(vat) == 8:
            try:
                # Solo sustituye si la API devuelve algo válido
                name_from_api = apiperu_dni(vat)
                if name_from_api:
                    vals['partner_name'] = name_from_api
                else:
                    # Si la API no responde, mantiene lo que el usuario puso
                    vals['partner_name'] = vals.get('partner_name').upper().strip()
            except Exception as e:
                # Si hay error, mantén el valor del usuario
                # vals['partner_name'] = vals.get('partner_name').upper().strip()
                _logger.warning("No se pudo obtener el nombre desde API PERU para %s: %s", vat, e)
        else:
            # Si no hay DNI válido, mantiene lo que ingresó el usuario
            vals['partner_name'] = vals.get('partner_name').upper().strip()
            
        if vals.get('email_from'):
            vals['email_from'] = vals['email_from'].lower()
        if vals.get('vat'):
            vals['vat'] = vals['vat'].strip()
            reinstatement = self.env['hr.applicant'].with_context(active_test=False).search([('vat', '=', vals['vat']),('stage_id.sequence', 'in', [2,3])], limit=1)
            if reinstatement:
                vals['is_reinstatement'] = True
        return super(Applicant, self).create(vals)
    
    def action_approve_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(_("You can approve only applicants in Contract Proposal."))
            
            if record.supervision_data_approved != 'pending':
                raise UserError(_("You can approve only when the request is pending."))
            
            if not record.first_contract_type_id:
                raise UserError("Debes asignar un tipo de contrato para poder aprobar la solicitud de contrato.") 

            record.supervision_data_approved = 'approved'

            current_employee = self.env['hr.employee'].search([('address_home_id.id', '=', record.partner_id.id)], order='create_date desc', limit=1)
            
            if current_employee:
                current_employee.sudo().write({'cost_center_id': record.cost_center_id.id,
                                                'parent_id': record.parent_id.id})
                if not record.partner_id.requires_compliance_process:
                    record.create_first_contract()
            else:
                _logger.info(f"\n\n\nNO EMPLOYEE WAS FOUND\n\n\n")

    def action_correct_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(_("You can correct data only for applicants in Contract Proposal."))

            if record.supervision_data_approved != 'rejected':
                    raise UserError(_("You can correct only when the request is rejected."))

            self.supervision_data_approved = 'pending'

    def action_reject_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(_("You can reject only applicants in Contract Proposal."))

            if record.supervision_data_approved != 'pending':
                raise UserError(_("You can reject only when the request is pending."))

            self.supervision_data_approved = 'rejected'
    
    def action_restore_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(_("You can restore only applicants in Contract Proposal."))
            
            if record.supervision_data_approved != 'approved':
                raise UserError(_("You can restore only when the request is approved."))

            current_employee = self.env['hr.employee'].search([('address_home_id.id', '=', record.partner_id.id)], order='create_date desc', limit=1)
            
            if current_employee:
                current_employee.sudo().write({'cost_center_id': False,
                                               'parent_id': False})

                employee_contract_history = self.env['hr.contract.history'].search([('employee_id', '=', record.emp_id.id)])

                if employee_contract_history and len(employee_contract_history) == 1:
                    if employee_contract_history.contract_id:
                        first_contract = employee_contract_history.contract_id.sudo()
                        if first_contract.state in ['cancel', 'draft']:
                            first_contract.toggle_active()
                        else:
                            raise UserError(_("It is not possible to restore the request because the first contract has been signed."))
            else:
                _logger.info(f"\n\n\nNO EMPLOYEE WAS FOUND\n\n\n")

            # Reset first contract data
            record.with_context(skip_contract_sync=True).write({
                "send_first_contract": False,
                "first_contract_id": False,
                # "first_contract_type_id": False,
                "supervision_data_approved": 'pending'
            })

    def action_applicant_data_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Datos del Postulante',
            'res_model': 'applicant.data.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids}
        }
    
    def action_open_first_contract(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrato',
            'res_model': 'hr.contract',
            'res_id': self.first_contract_id.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
    
    def action_send_unsend_first_contract(self):
        for rec in self:
            if rec.first_contract_id and rec.supervision_data_approved == 'approved':
                rec.send_first_contract = not rec.send_first_contract
            else:
                raise UserError(_("You can only send/unsend the contract when the supervision data is approved and the first contract is created."))
            
    def unlink(self):
        for rec in self:
            if rec.stage_id.sequence > 1:
                raise UserError(_("You can only delete applicants in the initial stage. Try archive them instead."))

        return super().unlink()
    
    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('skip_contract_sync'):
            self._sync_to_contracts()
        return res

    def _sync_to_contracts(self):
        for rec in self:
            contract = rec.first_contract_id
            if contract:
                contract.with_context(skip_applicant_sync=True).write({
                    "contract_type_id": rec.first_contract_type_id.id or False,
                    "is_sended": rec.send_first_contract or False,
                })
            else:
                rec.with_context(skip_contract_sync=True).write({
                    'send_first_contract': False
                })