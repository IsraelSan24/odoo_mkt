from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class Migrator(models.Model):
    _name = 'migrator'
    _description = 'Migrator'

    name = fields.Char(string='Name of migration')

    def migrator(self):
        self.migrate_province()
        self.migrate_brand()
        self.migrate_budget_campaign()
        self.migrate_d_budget_class()
        self.migrate_document_type()
        self.migrate_month_year()
        self.migrate_payroll_payment()
        self.migrate_service_type()

        self.migrate_d_cost_center()
        self.migrate_d_bugdet()

        self.migrate_documentary()
        self.migrate_requirement()
        self.migrate_requirement_line()
        self.migrate_settlement_detail()
        self.migrate_settlement_detail_line()
        self.migrate_requirement_justification()
        self.migrate_d_budget_line()

        self.delete_mail_message_d_budget()
        self.replace_mail_message_budget()
        self.delete_mail_message_d_cost_center()
        self.replace_mail_message_cost_center()
        self.delete_mail_message_documentary()
        self.replace_mail_message_settlement_documentary()
        self.replace_mail_message_requirement_documentary()

        self.compute_all()
        


# ? MODELS
#* ############################
    def migrate_province(self):
        new_provinces = self.env['province'].search([])
        for province in new_provinces:
            province.sudo().unlink()
        provinces = self.env['res.province'].search([])
        for province in provinces:
            self.env['province'].with_user(province.create_uid).create({
                'name': province.name,
                'user_id': province.user_id.id,
            })._write({
                'id': province.id,
                'create_date': province.create_date,
                'write_uid': province.write_uid.id,
                'write_date': province.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_province(self):
    #     provinces = self.env['province'].search([])
    #     for province in provinces:
    #         province.sudo().unlink()

    def migrate_brand(self):
        new_brands = self.env['brand'].search([])
        for brand in new_brands:
            brand.sudo().unlink()
        brands = self.env['res.partner.brand'].search([])
        for brand in brands:
            self.env['brand'].with_user(brand.create_uid).create({
                'name': brand.name,
                'user_id': brand.user_id.id,
            })._write({
                'id': brand.id,
                'create_date': brand.create_date,
                'write_uid': brand.write_uid.id,
                'write_date': brand.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_brand(self):
    #     brands = self.env['brand'].search([])
    #     for brand in brands:
    #         brand.sudo().unlink()

    def migrate_budget_campaign(self):
        new_campaigns = self.env['d.campaign'].search([])
        for campaign in new_campaigns:
            campaign.sudo().unlink()
        campaigns = self.env['budget.campaign'].search([])
        for campaign in campaigns:
            self.env['d.campaign'].with_user(campaign.create_uid).create({
                'name': campaign.name,
                'user_id': campaign.user_id.id,
            })._write({
                'id': campaign.id,
                'create_date': campaign.create_date,
                'write_uid': campaign.write_uid.id,
                'write_date': campaign.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_d_campaign(self):
    #     campaigns = self.env['d.campaign'].search([])
    #     for campaign in campaigns:
    #         campaign.sudo().unlink()

    def migrate_d_budget_class(self):
        new_budget_classes = self.env['d.budget.class'].search([])
        for classes in new_budget_classes:
            classes.sudo().unlink()
        budget_classes = self.env['budget.class'].search([])
        for classes in budget_classes:
            self.env['d.budget.class'].with_user(classes.create_uid).create({
                'name': classes.name,
                'user_id': classes.create_uid.id,
            })._write({
                'id': classes.id,
                'create_date': classes.create_date,
                'write_uid': classes.write_uid.id,
                'write_date': classes.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_budget_class(self):
    #     budget_classes = self.env['d.budget.class'].search([])
    #     for classes in budget_classes:
    #         classes.sudo().unlink()

    def migrate_document_type(self):
        new_documents = self.env['document.type'].search([])
        for document in new_documents:
            document.sudo().unlink()
        documents = self.env['settlement.line.type'].search([])
        for document in documents:
            self.env['document.type'].with_user(document.create_uid).create({
                'name': document.name,
                'budgetable': document.budgetable,
                'national_format': document.national_format,
                'short_name': document.short_name or 'DEFAULT',
                'need_ruc': document.is_ruc,
                'accountable': document.accountable,
                'external_return': document.is_return,
            })._write({
                'id': document.id,
                'create_date': document.create_date,
                'write_uid': document.write_uid.id,
                'write_date': document.write_date,
            })
        self.env['document.type'].sudo().create({
            'name': 'JUSTIFICATION',
            'short_name': 'JF',
        })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_document_type(self):
    #     documents = self.env['document.type'].search([])
    #     for document in documents:
    #         document.sudo().unlink()

    def migrate_d_cost_center(self):
        new_cost_centers = self.env['d.cost.center'].search([])
        for cost_center in new_cost_centers:
            cost_center.sudo().unlink()
        cost_centers = self.env['cost.center'].search([])
        for cost_center in cost_centers:
            self.env['d.cost.center'].with_user(cost_center.create_uid).create({
                'name': cost_center.name,
                'code': cost_center.code,
                'partner_id': cost_center.partner_id.id,
                'province_id': cost_center.province_id.id,
                'brand_id': cost_center.partner_brand_id.id,
                'executive_id': cost_center.executive_id.id,
                'responsible_id': cost_center.responsible_id.id,
            })._write({
                'id': cost_center.id,
                'create_date': cost_center.create_date,
                'write_uid': cost_center.write_uid.id,
                'write_date': cost_center.write_date,
                'message_main_attachment_id': cost_center.message_main_attachment_id.id or None,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_d_cost_center(self):
    #     cost_centers = self.env['d.cost.center'].search([])
    #     for cost_center in cost_centers:
    #         cost_center.sudo().unlink()

    def migrate_month_year(self):
        new_year_months = self.env['month.year'].search([])
        for monthyear in new_year_months:
            monthyear.sudo().unlink()
        month_years = self.env['year.month'].search([])
        for monthyear in month_years:
            self.env['month.year'].with_user(monthyear.create_uid).create({
                'name': monthyear.name,
                'month': monthyear.month,
                'year': monthyear.year,
                'sequence_id': monthyear.sequence_id.id,
            })._write({
                'id': monthyear.id,
                'create_date': monthyear.create_date,
                'write_uid': monthyear.write_uid.id,
                'write_date': monthyear.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_month_year(self):
    #     year_months = self.env['month.year'].search([])
    #     for monthyear in year_months:
    #         monthyear.sudo().unlink()

    def migrate_d_bugdet(self):
        new_budgets = self.env['d.budget'].search([])
        for budget in new_budgets:
            budget.sudo().unlink()
        budgets = self.env['budget'].search([])
        for budget in budgets:
            self.env['d.budget'].with_user(budget.create_uid).create({
                'name': budget.name,
                'month': budget.month,
                'year': budget.year,
                'my_month_year': budget.my_month_year,
                'month_year_id': budget.year_month_id.id,
                'cost_center_id': budget.cost_center_id.id,
                'partner_id': budget.partner_id.id,
                'brand_id': budget.partner_brand_id.id,
                'responsible_revision': budget.responsible_revision,
                'campaign_id': budget.campaign_id.id,
                'budget_class_id': budget.class_id.id,
                'executive_id': budget.executive_id.id,
                'responsible_id': budget.responsible_id.id,
                'max_amount': budget.max_amount,
                'state': budget.state,
                'sequence_id': budget.sequence_id.id,
                'user_id': budget.user_id.id,
                'message_main_attachment_id': budget.message_main_attachment_id.id or None,
            })._write({
                'id': budget.id,
                'create_date': budget.create_date,
                'write_uid': budget.write_uid.id,
                'write_date': budget.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_budget(self):
    #     budgets = self.env['d.budget'].search([])
    #     for budget in budgets:
    #         budget.sudo().unlink()


    def migrate_payroll_payment(self):
        new_payrolls = self.env['payroll.payment'].search([])
        for payroll in new_payrolls:
            payroll.sudo().unlink()
        payrolls = self.env['requirement.payroll'].search([])
        for payroll in payrolls:
            self.env['payroll.payment'].with_user(payroll.create_uid).create({
                'name': payroll.name,
                'code': payroll.code,
            })._write({
                'id': payroll.id,
                'create_date': payroll.create_date,
                'write_uid': payroll.write_uid.id,
                'write_date': payroll.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_payroll(self):
    #     payrolls = self.env['payroll.payment'].search([])
    #     for payroll in payrolls:
    #         payroll.sudo().unlink()

    def migrate_d_budget_line(self):
        budget_lines = self.env['budget.line'].search([])
        for line in budget_lines:
            _logger.info('\n\n\n line.document_type: %s \n\n\n', line.document_type)
            self.env['d.budget.line'].with_user(line.create_uid).create({
                'budget_id': line.budget_id.id,
                'documentary_id': line.requirement_id.id,
                'settlement_id': line.settlement_detail_id.id,
                'date': line.date,
                'document_filename': line.document_filename,
                'document_file': line.document_file,
                'document_type_id': self.env['document.type'].search([('name','=',line.document_type)]).id,
                'document': line.document,
                'reason': line.reason,
                'amount': line.amount,
                'remove': line.remove,
                'state': line.state,
            })._write({
                'id': line.id,
                'create_date': line.create_date,
                'write_uid': line.write_uid.id,
                'write_date': line.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def change_state_name(self, state):
        final_state = ''
        if state == 'draft':
            final_state ='draft'
        if state == 'waiting_boss_validation':
            final_state = 'executive'
        if state == 'waiting_budget_executive_validation':
            final_state = 'responsible'
        if state == 'waiting_intern_control_validation':
            final_state = 'intern_control'
        if state == 'waiting_administration_validation':
            final_state = 'administration'
        if state == 'to_settle':
            final_state = 'to_settle'
        if state == 'settled':
            final_state = 'settled'
        if state == 'refused':
            final_state = 'refused'
        return final_state

    def migrate_documentary(self):
        new_documentaries = self.env['documentary'].search([])
        for documentary in new_documentaries:
            documentary.sudo().unlink()
        requirements = self.env['documental.requirements'].search([])
        for requirement in requirements:
            self.env['documentary'].with_user(requirement.create_uid).sudo().create({
                'name': requirement.name,
                'active': requirement.active,
                'urgency': requirement.urgency,
                'unify': False,
                'paid_partner_id': requirement.paid_to.id or 1,
                'vat_partner': requirement.dni_or_ruc,
                'card_payment': requirement.card_payment,
                'bank_id': requirement.bank.id,
                'partner_bank_ids': [(6,0,requirement.current_partner_bank_ids.ids)],
                'bank_account_number': requirement.customer_account_number,
                'currency': requirement.amount_currency_type,
                'budget_id': requirement.budget_id.id,
                'cost_center_id': requirement.cost_center_id.id,
                'partner_id': requirement.partner_id.id,
                'month_year_id': requirement.year_month_id.id,
                'campaign_id': requirement.campaign_id.id,
                'show_budget_detail': True,
                'detraction_bank': requirement.deduction_bank.id,
                'detraction_acc_number': requirement.deduction_acc_number,
                'timer_state': requirement.timer_state,
                'concept': requirement.concept,
                'detail': requirement.detail,
                'amount': requirement.amount_soles if requirement.amount_soles != 0 else requirement.amount_uss,
                'amount_text': requirement.amount_char,
                'payment_date': requirement.payment_date,
                'check_operation': requirement.check_or_operation,
                'operation_number': requirement.operation_number,
                'payroll_payment_id': requirement.requirement_payroll_id.id,
                'in_bank': requirement.in_bank,
                'balance': requirement.settlement_id.balance,
                'user_id': requirement.full_name.id,
                'vat_user_id': requirement.dni,
                'employee_id': requirement.employee_id.id,
                'refund_user_id': requirement.refund_user_id.id,
                # 'refund_documentary_id': requirement.refund_requirement_id.id,
                'refund_created': requirement.settlement_id.refund_created,
                'requirement_has_det_ret': True if requirement.detraction_amount > 0 else False,
                'settlement_has_det_ret': True if requirement.settlement_id.total_detraction > 0 else False,
                'requirement_service_reviewed': True if requirement.account_check else False,
                'settlement_service_reviewed': True if requirement.account_check else False,
                'service_reviewed': True if requirement.account_check else False,
                'requirement_amount': requirement.amount_soles if requirement.amount_soles != 0 else requirement.amount_uss,
                'requirement_detraction': requirement.detraction_amount,
                'requirement_retention': requirement.retention_amount,
                'requirement_vendor': requirement.to_pay_supplier,
                # 'requirement_amount_text': '',
                # 'requirement_detraction_text': '',
                # 'requirement_retention_text': '',
                # 'requirement_vendor_text': '',
                # 'requirement_ids': '',
                # 'lock_requirement_ids': '',
                'requirement_state': self.change_state_name(requirement.state),
                'settlement_amount': requirement.settlement_id.total_amount_sum,
                'settlement_detraction': requirement.settlement_id.total_detraction,
                'settlement_retention': requirement.settlement_id.total_retention,
                'settlement_vendor': requirement.settlement_id.total_to_pay_supplier,
                # 'settlement_amount_text': ,
                # 'settlement_detraction_text': '',
                # 'settlement_retention_text': '',
                # 'settlement_vendor_text': '',
                # 'settlement_ids': '',
                # 'lock_settlement_ids': '',
                'settlement_state': self.change_state_name(requirement.settlement_id.state),
                'setttlement_lines': requirement.settlement_id.total_lines,
                'requirement_petitioner_user_id': requirement.full_name.id,
                'requirement_petitioner_signature': requirement.petitioner_signature,
                'requirement_petitioner_signed_on': requirement.petitioner_signed_on,
                'requirement_executive_user_id': requirement.user_boss_signed_id.id,
                'requirement_executive_signature': requirement.boss_signature,
                'requirement_executive_signed_on': requirement.boss_signed_on,
                'requirement_responsible_user_id': requirement.user_budget_executive_signed_id.id,
                'requirement_responsible_signature': requirement.budget_executive_signature,
                'requirement_responsible_signed_on': requirement.budget_executive_signed_on,
                'requirement_intern_control_received_on': requirement.intern_control_received,
                'requirement_intern_control_user_id': requirement.user_intern_control_signed_id.id,
                'requirement_intern_control_signature': requirement.intern_control_signature,
                'requirement_intern_control_signed_on': requirement.intern_control_signed_on,
                'requirement_administration_user_id': requirement.user_administration_signed_id.id,
                'requirement_administration_signature': requirement.administration_signature,
                'requirement_administration_signed_on': requirement.administration_signed_on,
                'settlement_petitioner_user_id': requirement.settlement_id.responsible_id.id,
                'settlement_petitioner_signature': requirement.settlement_id.petitioner_signature,
                'settlement_petitioner_signed_on': requirement.settlement_id.petitioner_signed_on,
                'settlement_executive_user_id': requirement.settlement_id.user_boss_signed_id.id,
                'settlement_executive_signature': requirement.settlement_id.boss_signature,
                'settlement_executive_signed_on': requirement.settlement_id.boss_signed_on,
                'settlement_responsible_user_id': requirement.settlement_id.user_budget_executive_signed_id.id,
                'settlement_responsible_signature': requirement.settlement_id.budget_executive_signature,
                'settlement_responsible_signed_on': requirement.settlement_id.budget_executive_signed_on,
                'settlement_intern_control_received_on': requirement.settlement_id.intern_control_received,
                'settlement_intern_control_user_id': requirement.settlement_id.user_intern_control_signed_id.id,
                'settlement_intern_control_signature': requirement.settlement_id.intern_control_signature,
                'settlement_intern_control_signed_on': requirement.settlement_id.intern_control_signed_on,
                'settlement_administration_user_id': requirement.settlement_id.user_administration_signed_id.id,
                'settlement_administration_signature': requirement.settlement_id.administration_signature,
                'settlement_administration_signed_on': requirement.settlement_id.administration_signed_on,
                'message_main_attachment_id': requirement.message_main_attachment_id.id or None,
            })._write({
                'id': requirement.id,
                'create_date': requirement.create_date,
                'write_uid': requirement.write_uid.id,
                'write_date': requirement.write_date,
            })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_documentary(self):
    #     documentaries = self.env['documentary'].search([])
    #     for documentary in documentaries:
    #         documentary.sudo().unlink()

    def migrate_requirement(self):
        new_requirements = self.env['requirement'].search([])
        for requirement in new_requirements:
            requirement.sudo().unlink()
        details = self.env['requirement.detail'].search([])
        for detail in details:
            if detail.requirement_id:
                if self.env['documentary'].browse(detail.requirement_id.id).exists():
                    self.env['requirement'].with_user(detail.create_uid).sudo().create({
                        'documentary_id': detail.requirement_id.id or None,
                        'handler': detail.sequence_handle,
                        'date': detail.date,
                        'dni_ruc': detail.ruc,
                        'partner': detail.partner,
                        'document_type_id': detail.document_type.id,
                        'document': detail.document,
                        'document_file': detail.document_file,
                        'document_filename': detail.document_filename,
                        'reason': detail.reason,
                        'required_amount': detail.amount,
                        'required_igv': sum( detail.requirement_detail_line_ids.mapped('igv') ),
                        'amount': detail.amount,
                        'vendor': detail.to_pay,
                        'detraction': detail.detraction,
                        'retention': detail.retention,
                        'tax_id': detail.tax_igv_id.id,
                        'igv_included': detail.igv_included,
                        'state': detail.state,
                    })._write({
                        'id': detail.id,
                        'create_date': detail.create_date,
                        'write_uid': detail.write_uid.id,
                        'write_date': detail.write_date,
                    })
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_requirement(self):
    #     requirements = self.env['requirement'].search([])
    #     for requirement in requirements:
    #         requirement.sudo().unlink()
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Deletetion completed',
    #             'type': 'rainbow_man',
    #         }
    #     }

    def migrate_service_type(self):
        new_services = self.env['service.type'].search([])
        for service in new_services:
            service.sudo().unlink()
        services = self.env['requirement.service.type'].search([])
        for service in services:
            self.env['service.type'].with_user(service.create_uid).sudo().create({
                'name': service.name,
                'percentage': service.percentage,
                'amount_from': service.amount_from,
                'detraction': service.detraction,
                'retention': service.retention,
                'code': service.code,
            })._write({
                'id': service.id,
                'create_date': service.create_date,
                'write_uid': service.write_uid.id,
                'write_date': service.write_date,
            })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    # def delete_service(self):
    #     services = self.env['service.type'].search([])
    #     for service in services:
    #         service.sudo().unlink()
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Deletetion completed',
    #             'type': 'rainbow_man',
    #         }
    #     }

    def change_tax_name(self, state):
        final_state = ''
        if state == 'levied':
            final_state ='levied'
        if state == 'exonerated':
            final_state = 'exonerated'
        if state == 'consumption_surcharge':
            final_state = 'surcharge'
        return final_state


    def migrate_requirement_line(self):
        requirement_lines = self.env['requirement.detail.line'].search([])
        for line in requirement_lines:
            if self.env['requirement'].browse(line.requirement_detail_id.id).exists():
                self.env['requirement.line'].with_user(line.create_uid).sudo().create({
                    'name': line.name,
                    'requirement_id': line.requirement_detail_id.id,
                    'service_type_id': line.service_type_id.id,
                    'tax': self.change_tax_name(line.igv_tax),
                    'tax_id': line.tax_igv_id.id,
                    'igv_included': line.igv_included,
                    'quantity': line.quantity,
                    'unit_price': line.unit_price,
                    'base_amount': line.base_amount,
                    'igv': line.igv,
                    'amount': line.amount,
                })._write({
                    'id': line.id,
                    'create_date': line.create_date,
                    'write_uid': line.write_uid.id,
                    'write_date': line.write_date,
                })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    def migrate_requirement_justification(self):
        justifications = self.env['requirement.detail.justification'].search([])
        for justification in justifications:
            if self.env['documentary'].browse(justification.requirement_id.id).exists():
                self.env['requirement'].with_user(justification.create_uid).sudo().create({
                    'documentary_id': justification.requirement_id.id,
                    # 'handler': justification.sequence_handle,
                    'date': justification.create_date,
                    # 'dni_ruc': justification.ruc,
                    'partner':self.env['res.partner'].search([('name','=',justification.partner.name)]).name or None,
                    'document_type_id': self.env['document.type'].search([('short_name','=','JF')]).id,
                    # 'document': justification.document,
                    'document_file': justification.document_file,
                    'document_filename': justification.document_filename,
                    'reason': justification.reason,
                    'required_amount': justification.amount,
                    # 'required_igv': False,
                    # 'amount': justification.amount,
                    # 'vendor': justification.to_pay,
                    # 'detraction': justification.detraction,
                    # 'retention': justification.retention,
                    # 'tax_id': justification.tax_igv_id.id,
                    # 'igv_included': justification.igv_included,
                    'state': justification.requirement_id.state,
                })._write({
                    # 'id': justification.id,
                    'create_date': justification.create_date,
                    'write_uid': justification.write_uid.id,
                    'write_date': justification.write_date,
                })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    def migrate_requirement_line_from_just(self):
        requirements = self.env['requirement'].search([])
        for requirement in requirements:
            if requirement.document_type_id.short_name == 'JF':
                self.env['requirement.line'].sudo().create({
                    'name': requirement.reason,
                    'requirement_id': requirement.id,
                    'tax': 'exonerated',
                    'quantity': 1,
                    'unit_price': requirement.required_amount,
                })._write({
                    'create_date': requirement.create_date,
                    'write_uid': requirement.write_uid.id,
                    'write_date': requirement.write_date,
                })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    def compute_base_amount_requirement_line(self):
        requirements = self.env['requirement.line'].search([])
        for requirement in requirements:
            requirement._compute_base_amount()
            requirement._compute_igv()
            requirement._compute_amount()
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Migration completed',
        #         'type': 'rainbow_man',
        #     }
        # }

    def compute_amount_requirement(self):
        requirements = self.env['requirement'].search([])
        for requirement in requirements:
            requirement._compute_filename()
            requirement._compute_amount()
            requirement._compute_detraction_retention()
            requirement._compute_vendor()
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Migration completed',
        #         'type': 'rainbow_man',
        #     }
        # }

    def compute_documentary(self):
        documentaries = self.env['documentary'].search([])
        for documentary in documentaries:
            documentary._compute_settlement_lines()
            documentary._compute_service_reviewed()
            documentary._compute_balance()
            documentary._compute_settlement_amount_text()
            documentary._compute_settlement_detraction_text()
            documentary._compute_settlement_retention_text()
            documentary._compute_settlement_vendor_text()
            documentary._compute_requirement_amount_text()
            documentary._compute_requirement_detraction_text()
            documentary._compute_requirement_retention_text()
            documentary._compute_requirement_vendor_text()
            documentary._compute_requirement_amount()
            documentary._compute_requirement_detraction()
            documentary._compute_requirement_retention()
            documentary._compute_requirement_vendor()
            documentary._compute_settlement_amount()
            documentary._compute_settlement_detraction()
            documentary._compute_settlement_retention()
            documentary._compute_settlement_vendor()
            documentary._compute_amount_text()
            documentary._compute_amount()
            documentary._compute_bank()
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Migration completed',
        #         'type': 'rainbow_man',
        #     }
        # }

    def migrate_settlement_detail(self):
        settlement_details = self.env['documental.settlements.detail'].search([])
        for detail in settlement_details:
            self.env['settlement'].with_user(detail.create_uid).sudo().create({
                'documentary_id': self.env['documental.requirements'].sudo().search([('settlement_id','=',detail.documental_settlement_id.id)]).id,
                'repeated': detail.repeated,
                'handler': detail.sequence_handle,
                'date': detail.date,
                'dni_ruc': detail.ruc,
                'partner': detail.partner,
                'document_type_id': detail.document_type.id,
                'document': detail.document,
                'movement_number': detail.movement_number,
                'document_file': detail.document_file,
                'document_filename': detail.document_filename,
                'reason': detail.reason,
                'settle_amount': detail.amount,
                'amount': detail.amount,
                'vendor': detail.to_pay,
                'detraction': detail.detraction_amount,
                'retention': detail.retention_amount,
                'tax_id': detail.tax_igv_id.id,
                'igv_included': detail.igv_included,
                'state': detail.state,
            })._write({
                    'id': detail.id,
                    'create_date': detail.create_date,
                    'write_uid': detail.write_uid.id,
                    'write_date': detail.write_date,
                })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }


    def migrate_settlement_detail_line(self):
        settlement_lines = self.env['settlement.detail.line'].search([])
        for line in settlement_lines:
            self.env['settlement.line'].with_user(line.create_uid).sudo().create({
                'name': line.name,
                'settlement_id': line.settlement_detail.id,
                'service_type_id': line.service_type_id.id,
                'tax': self.change_tax_name(line.igv_tax),
                'tax_id': line.tax_igv_id.id,
                'igv_included': line.igv_included,
                'quantity': line.quantity,
                'unit_price': line.unit_price,
                'base_amount': line.base_amount,
                'igv': line.igv,
                'amount': line.amount,
            })._write({
                    'id': line.id,
                    'create_date': line.create_date,
                    'write_uid': line.write_uid.id,
                    'write_date': line.write_date,
                })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    def compute_settlement_line(self):
        settlement_lines = self.env['settlement.line'].search([])
        for line in settlement_lines:
            line._compute_base_amount()
            line._compute_igv()
            line._compute_amount()
        # return {
        #     'effect': {
        #         'fadeout': 'slow',
        #         'message': 'Migration completed',
        #         'type': 'rainbow_man',
        #     }
        # }

    def compute_settlement(self):
        settlements = self.env['settlement'].search([])
        for settlement in settlements:
            settlement._compute_filename()
            settlement._compute_amount()
            settlement._compute_detraction_retention()
            settlement._compute_vendor()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    def compute_all(self):
        self.compute_settlement_line()
        self.compute_settlement()
        self.compute_base_amount_requirement_line()
        self.compute_amount_requirement()
        self.compute_documentary()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Compute completed',
                'type': 'rainbow_man',
            }
        }


    def change_month(self, state):
        final_state = ''
        if state == 'enero':
            final_state ='Enero'
        if state == 'febrero':
            final_state = 'Febrero'
        if state == 'marzo':
            final_state = 'Marzo'
        if state == 'abril':
            final_state ='Abril'
        if state == 'mayo':
            final_state = 'Mayo'
        if state == 'junio':
            final_state = 'Junio'
        if state == 'julio':
            final_state = 'Julio'
        if state == 'agosto':
            final_state = 'Agosto'
        if state == 'septiembre':
            final_state = 'Septiembre'
        if state == 'octubre':
            final_state = 'Octubre'
        if state == 'noviembre':
            final_state = 'Noviembre'
        if state == 'diciembre':
            final_state = 'Diciembre'
        return final_state


    def migrate_mobility(self):
        new_services = self.env['mobility'].search([])
        for service in new_services:
            service.sudo().unlink()
        mobilities = self.env['documental.mobility.expediture'].search([])
        for mobility in mobilities:
            self.env['mobility'].with_user(mobility.create_uid).sudo().create({
                'name': mobility.name,
                'state': mobility.state,
                'budget_id': mobility.budget_id.id,
                'cost_center_id': mobility.cost_center_id.id,
                'month': self.change_month(mobility.period),
                'employee_id': mobility.employee_id.id,
                'user_id': mobility.full_name.id,
                'amount': mobility.amount_total,
                # 'petitioner_user_id': ,
                'petitioner_signature': mobility.petitioner_signature,
                'petitioner_signed_on': mobility.petitioner_signed_on,
                # 'executive_user_id': mobility.,
                'executive_signature': mobility.executive_signature,
                'executive_signed_on': mobility.executive_signed_on,
            })._write({
                'id': mobility.id,
                'create_date': mobility.create_date,
                'write_uid': mobility.write_uid.id,
                'write_date': mobility.write_date,
            })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }

    def migrate_mobility_line(self):
        new_services = self.env['mobility.line'].search([])
        for service in new_services:
            service.sudo().unlink()
        mobility_lines = self.env['documental.mobility.expediture.detail'].search([])
        for line in mobility_lines:
            self.env['mobility.line'].sudo().with_user(line.create_uid).create({
                'mobility_id': line.documental_mobility_id.id,
                'handler': line.sequence_handle,
                'date': line.date,
                'reason': line.reason,
                'origin': line.origin_place,
                'destiny': line.destiny,
                'document_file': line.document_file,
                'document_filename': line.document_filename,
                'partial_amount': line.amount,
                'amount': line.partial_amount,
                'rowspan_quant': line.rowspan_quant,
                'user_id': line.user_id,
            })._write({
                'id': line.id,
                'create_date': line.create_date,
                'write_uid': line.write_uid.id,
                'write_date': line.write_date,
            })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed',
                'type': 'rainbow_man',
            }
        }


# ? MAIL MESSAGE
#* ############################
    #* Mail message delete d_budget autogenerated
    def delete_mail_message_d_budget(self):
        self.env.cr.execute("DELETE FROM mail_message WHERE model = 'd.budget'")
        # mail_messages = self.env['mail.message'].search([])
        # _logger.info('\n\n\n mail_messages: %s \n\n\n', mail_messages)
        # for messages in mail_messages:
            # if messages.model == 'd.budget':
                # _logger.info('\n\n\n messages: %s \n\n\n', messages)
                # messages.sudo().unlink()
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Deletetion completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message replace budget by d_budget
    def replace_mail_message_budget(self):
        self.env.cr.execute("""
            UPDATE mail_message
            SET model = 'd.budget'
            WHERE model = 'budget'
        """)
        # mail_messages = self.env['mail.message'].search([('model','=','budget')])
        # for messages in mail_messages:
        #     _logger.info('\n\n\n messages: %s \n\n\n', messages)
        #     messages.write({
        #         'model': 'd.budget',
        #     })
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message delete d_cost_center autogenerated
    def delete_mail_message_d_cost_center(self):
        self.env.cr.execute("DELETE FROM mail_message WHERE model = 'd.cost.center'")
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Deletetion completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message replace cost_center by d_cost_center
    def replace_mail_message_cost_center(self):
        self.env.cr.execute("""
            UPDATE mail_message
            SET model = 'd.cost.center'
            WHERE model = 'cost.center'
        """)
        # mail_messages = self.env['mail.message'].search([('model','=','cost.center')])
        # for messages in mail_messages:
        #     _logger.info('\n\n\n messages: %s \n\n\n', messages)
        #     messages.write({
        #         'model': 'd.cost.center',
        #     })
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message delete documentary autogenerated
    def delete_mail_message_documentary(self):
        self.env.cr.execute("DELETE FROM mail_message WHERE model = 'documentary'")
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Deletetion completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message replace documental.settlements by documentary
    def replace_mail_message_settlement_documentary(self):
        mail_message = self.env['mail.message'].search([('model','=','documental.settlements')])
        _logger.info('\n\n\n mail_message: %s \n\n\n', mail_message)
        for message in mail_message:
            _logger.info('\n\n\n messages: %s \n\n\n', message)
            message.write({
                'model': 'documentary',
                'res_id': self.env['documental.requirements'].search([('settlement_id','=',message.res_id)]).id,
            })
        # self.env.cr.close()
        # self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message replace documental.requirements by documentary
    def replace_mail_message_requirement_documentary(self):
        self.env.cr.execute("""
            UPDATE mail_message
            SET model = 'documentary'
            WHERE model = 'documental.requirements'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message delete mobility
    def delete_message_mobility(self):
        self.env.cr.execute("DELETE FROM mail_message WHERE model = 'mobility'")
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    #* Mail message replace mobility
    def replace_mail_message_mobility(self):
        self.env.cr.execute("""
            UPDATE mail_message
            SET model = 'mobility'
            WHERE model = 'documental.mobility.expediture'
        """)
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }


# ? ATTACHMENT
#* ############################
    def delete_attachment_documentary(self):
        self.env.cr.execute("""
            DELETE FROM ir_attachment WHERE res_model = 'documentary' AND res_field IS NOT NULL
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def replace_attachment_requirements(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'documentary',
                res_field = 
                    CASE
                        WHEN res_field = 'petitioner_signature' THEN 'requirement_petitioner_signature'
                        WHEN res_field = 'boss_signature' THEN 'requirement_executive_signature'
                        WHEN res_field = 'budget_executive_signature' THEN 'requirement_responsible_signature'
                        WHEN res_field = 'intern_control_signature' THEN 'requirement_intern_control_signature'
                        WHEN res_field = 'administration_signature' THEN 'requirement_administration_signature'
                        ELSE res_field
                    END
            WHERE
                res_model = 'documental.requirements' AND res_field IS NOT NULL;
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def replace_attachment_settlements(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'documentary',
                res_field = 
                    CASE
                        WHEN res_field = 'petitioner_signature' THEN 'settlement_petitioner_signature'
                        WHEN res_field = 'boss_signature' THEN 'settlement_executive_signature'
                        WHEN res_field = 'budget_executive_signature' THEN 'settlement_responsible_signature'
                        WHEN res_field = 'intern_control_signature' THEN 'settlement_intern_control_signature'
                        WHEN res_field = 'administration_signature' THEN 'settlement_administration_signature'
                        ELSE res_field
                    END
            WHERE
                res_model = 'documental.settlements' AND res_field IS NOT NULL
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def delete_attachment_requirement(self):
        self.env.cr.execute("""
            DELETE FROM ir_attachment WHERE res_model = 'requirement' 
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }
    
    def replace_attachment_requirement_detail(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'requirement'
            WHERE res_model = 'requirement.detail'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def delete_attachment_settlement(self):
        self.env.cr.execute("""
            DELETE FROM ir_attachment WHERE res_model = 'settlement'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def replace_attachment_settlement_detail(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'settlement'
            WHERE res_model = 'documental.settlements.detail'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def replace_attachment_settlement_null(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET 
                res_model = 'documentary',
                res_id = (
                    SELECT ds.requirement_id
                    FROM documental_settlements AS ds
                    WHERE ds.id = ir_attachment.res_id
                )
            WHERE res_model = 'documental.settlements'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def delete_attachment_d_budget_line(self):
        self.env.cr.execute("""
            DELETE FROM ir_attachment WHERE res_model = 'd.budget.line'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def replace_attachment_budget_line(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'd.budget.line'
            WHERE res_model = 'budget.line'
        """)
        # self.env.cr.close()
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }


    def delete_attachment_mobility(self):
        self.env.cr.execute("DELETE FROM ir_attachment WHERE res_model = 'mobility'")
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }

    def replace_attachment_mobility(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'mobility'
            WHERE res_model = 'documental.mobility.expediture'
        """)
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migrate completed',
                'type': 'rainbow_man',
            }
        }