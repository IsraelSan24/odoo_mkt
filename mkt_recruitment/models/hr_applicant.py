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

    first_contract_start = fields.Date(string="First Contract Start Date", tracking=True) 
    first_contract_end = fields.Date(string="First Contract End Date", tracking=True)

    cost_center_id = fields.Many2one('cost.center', string="Cost Center", tracking=True)
    selected_applicant_approved = fields.Boolean(string="Is selected applicant approved?", tracking=True)
    supervision_data_approved = fields.Selection([
                                    ('pending', 'Pending'),
                                    ('approved', 'Approved'),
                                    ('rejected', 'Rejected'),
                                ], string='Supervision Status', tracking=True)
    supervision_data_sent = fields.Boolean("Is supervision data sent?", tracking=True, default=False) 

    def write(self, vals):
        if 'stage_id' in vals:
            new_stage = self.env['hr.recruitment.stage'].browse(vals['stage_id'])
            if not new_stage.exists():
                raise UserError("El nuevo estado no es válido.")
            
            # restrict if not in group
            if new_stage.id == 4 and not self.env.user.has_group('mkt_supervision.group_supervision_hiring_approver'):
                _logger.info(f"\n\n\nHRAPPLICANT RESTRICT GROUP\n\n\n")
                raise AccessError("You don't have permissions to move candidates to this stage.")


            _logger.info(f"\n\n\nHR APPLICANT PASSED\n\n\n")
            for rec in self:
                if not rec.stage_id:
                    raise UserError("El registro no tiene un estado actual asignado.")
                if abs(new_stage.sequence - rec.stage_id.sequence) > 1:
                    raise UserError("Solo puedes cambiar el estado al siguiente o anterior en la vista Kanban.")
        
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
            look_for_employee = rec.env['hr.employee'].search([('address_home_id.vat', '=', rec.vat)], limit=1)
            if look_for_employee:
                raise UserError(f"An active employee exists with this DNI {rec.vat} ({look_for_employee.name}). It is necesary to terminate the employee before trying to continue with a new recruitment process.")

            rec.contact_merge_stage()
            rec.update_data_partner()
            rec.create_employee_by_stage()
            rec.access_portal_partner()


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
            portal_wizar_vals = {}
            if contact and len(contact) == 1:
                self.hr_responsible_contract_id = self.env.user.id
                # try:
                #     portal_wizard_user_vals = {
                #         'wizard_id': self.env['portal.wizard'].create(portal_wizar_vals).id,
                #         'partner_id': contact.id,
                #         'email': contact.email,
                #         'user_id': contact.user_id,
                #     }
                #     portal_wizard_user = self.env['portal.wizard.user'].create(portal_wizard_user_vals)
                #     portal_wizard_user.action_grant_access()
                # except:
                #     pass
                portal_wizard_user_vals = {
                    'wizard_id': self.env['portal.wizard'].create(portal_wizar_vals).id,
                    'partner_id': contact.id,
                    'email': contact.email,
                    'user_id': contact.user_id,
                }
                portal_wizard_user = self.env['portal.wizard.user'].create(portal_wizard_user_vals)
                user = self.env['res.users'].with_context(active_test=False).search([('partner_id', '=', self.partner_id.id)], limit=1)
                if self.is_reinstatement == False:
                    if not user:
                        portal_wizard_user.action_grant_access()
                    else:
                        portal_wizard_user.action_invite_again()
                else:
                    if user.active == False:
                        user.toggle_active()
                    if user:
                        user.login = self.email_from
            elif len(contact) > 1:
                raise UserError(_('More than one contact has been found with the same DNI, please solve the problem to continue with the process.'))
            elif len(contact) < 1:
                raise UserError(_('No contacts were found with the same DNI, please solve the problem to continue with the process.'))
            else:
                raise UserError(_('The contact for this application is not found.'))


    def create_employee_by_stage(self):
        employee = False
        if not self.is_autoemployee and self.stage_id.employee_stage:
            look_for_employee = self.env['hr.employee'].search([('address_home_id.vat', '=', self.vat)], limit=1)
            if look_for_employee:
                raise UserError(f"An active employee exists with this DNI {self.vat} ({look_for_employee.name}). It is necesary to terminate the employee before trying to continue with a new recruitment process.")

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
                self.partner_id.write({'requires_compliance_process': True})

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
                }
                first_contract = self.env['hr.contract'].sudo().create(values)
                first_contract.write_data() 
                first_contract._compute_contract_duration()


    @api.model
    def create(self, vals):
        if vals.get('partner_name'):
            try:
                vals['partner_name'] = apiperu_dni(vals.get('vat'))
            except:
                pass
        if vals.get('email_from'):
            vals['email_from'] = vals['email_from'].lower()
        if vals.get('vat'):
            vals['vat'] = vals['vat'].strip()
            time_range = fields.Datetime.today() - timedelta(days=10)
            reinstatement = self.env['hr.applicant'].search([('vat', '=', vals['vat']),('stage_id.sequence', 'in', [4,5]),('create_date', '<', time_range)], limit=1)
            if reinstatement:
                vals['is_reinstatement'] = True
        return super(Applicant, self).create(vals)
    
    def action_approve_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(f"You can approve only applicants in Contract Proposal.")
            
            if record.supervision_data_approved != 'pending':
                raise UserError(f"You can approve only when the request is pending.")

            record.supervision_data_approved = 'approved'

            if not record.partner_id.requires_compliance_process:
                current_employee = self.env['hr.employee'].search([('address_home_id.id', '=', record.partner_id.id)], order='create_date desc', limit=1)
                
                if current_employee:
                    current_employee.sudo().write({'cost_center_id': record.cost_center_id.id})
                    record.create_first_contract()
                else:
                    _logger.info(f"\n\n\nNO EMPLOYEE WAS FOUND\n\n\n")

    def action_correct_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(f"You can correct data only for applicants in Contract Proposal.")

            if record.supervision_data_approved != 'rejected':
                    raise UserError(f"You can correct only when the request is rejected.")

            self.supervision_data_approved = 'pending'

    def action_reject_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(f"You can approve only applicants in Contract Proposal.")

            if record.supervision_data_approved != 'pending':
                raise UserError(f"You can reject only when the request is pending.")

            self.supervision_data_approved = 'rejected'
    
    def action_restore_supervision_data(self):
        for record in self:
            
            if int(record.stage_id) != 4:
                raise UserError(f"You can restore only applicants in Contract Proposal.")
            
            if record.supervision_data_approved != 'approved':
                raise UserError(f"You can restore only when the request is approved.")

            record.supervision_data_approved = 'pending'

            current_employee = self.env['hr.employee'].search([('address_home_id.id', '=', record.partner_id.id)], order='create_date desc', limit=1)
            
            if current_employee:
                current_employee.sudo().write({'cost_center_id': False})

                employee_contract_history = self.env['hr.contract.history'].search([('employee_id', '=', record.emp_id.id)])

                if employee_contract_history and len(employee_contract_history) == 1:
                    if employee_contract_history.contract_id:
                        first_contract = employee_contract_history.contract_id.sudo()
                        if first_contract.state in ['cancel', 'draft']:
                            first_contract.toggle_active()
                        else:
                            raise UserError("It is not possible to restore the request because the first contract has been signed.")
            else:
                _logger.info(f"\n\n\nNO EMPLOYEE WAS FOUND\n\n\n")
