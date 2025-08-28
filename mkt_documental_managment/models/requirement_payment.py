import base64
import io
import os
import tempfile
import mimetypes
import subprocess
import shutil  

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

try:
    from PIL import Image
except Exception:
    Image = None

class RequirementPayment(models.Model):
    _name = 'requirement.payment'
    _description = 'Requirement payment'

    requirement_id = fields.Many2one(comodel_name='documental.requirements', string='Requirement')
    requirement_state = fields.Selection(related='requirement_id.requirement_state', string='Requirement state')
    date_requested = fields.Date(string='Date requested', tracking=True)
    check_or_operation = fields.Selection(selection=[('check','Check'),('operation','Operation')], default='operation', string='Check/Operation', tracking=True)
    payment_bank_id = fields.Many2one(comodel_name="res.bank", string="Bank", domain="[('id','in',current_partner_bank_ids)]", default=lambda self: self._default_payment_bank_id(), tracking=True)
    bank_accounting_account = fields.Char(string='Bank accounting account')
    operation_number = fields.Char(string='Operation number', tracking=True)
    check_number = fields.Char(string='Check number', tracking=True)
    payment_date = fields.Date(string='Payment date', tracking=True)
    requirement_payroll_id = fields.Many2one(comodel_name='requirement.payroll', string='Payroll', tracking=True)
    amount = fields.Float(string='Amount', tracking=True)
    in_bank = fields.Boolean(default=False, copy=False, tracking=True)
    wrong_payment = fields.Boolean(default=False, copy=False, tracking=True)
    document_file = fields.Binary(string="Document File", attachment=True)
    document_filename = fields.Char(string="Filename")
    is_amount_editable = fields.Boolean(compute="_compute_is_amount_editable")
    is_administration_editable = fields.Boolean(compute="_compute_is_administration_editable")
    current_partner_bank_ids = fields.Many2many(
        comodel_name='res.bank', 
        compute='_compute_bank'
    )


    @api.constrains('in_bank')
    def _update_documental_requirement_in_bank(self):
        """Si cualquier RP tiene in_bank=True, marcar DR como True.
           Si todos los RP son False, marcar DR como False."""
        for record in self:
            if record.requirement_id:
                new_value = any(record.requirement_id.requirement_payment_ids.mapped('in_bank'))
                if record.requirement_id.in_bank != new_value:  # Solo escribir si es necesario
                    record.requirement_id.sudo().write({'in_bank': new_value})
                

    @api.depends('check_or_operation')
    def _compute_bank(self):
        bank_ids = self.env['res.partner'].browse(1).bank_ids.mapped('bank_id').ids
        self.current_partner_bank_ids = bank_ids


    def _default_payment_bank_id(self):
        bank = self.env['res.bank'].browse(4)
        if bank.exists():
            if self.requirement_id.amount_currency_type:
                currency = self.requirement_id.amount_currency_type.lower()
                if  currency == 'soles':
                    self.bank_accounting_account = '104103'
                elif currency == 'dolares':
                    self.bank_accounting_account = '104102'
            return bank.id
        return False


    @api.onchange('payment_bank_id')
    def onchange_payment_bank(self):
        for rec in self:
            if rec.payment_bank_id and rec.requirement_id.amount_currency_type:
                bank_name = (rec.payment_bank_id.name or '').lower()
                currency = (rec.requirement_id.amount_currency_type or '').lower()
                if "bcp" in bank_name and currency == 'soles':
                    rec.bank_accounting_account = '104101'
                elif "bcp" in bank_name and currency == 'dolares':
                    rec.bank_accounting_account = '104105'
                elif "bbva" in bank_name and currency == 'soles':
                    rec.bank_accounting_account = '104103'
                elif "bbva" in bank_name and currency == 'dolares':
                    rec.bank_accounting_account = '104102'
                else:
                    rec.bank_accounting_account = ''
            else:
                rec.bank_accounting_account = ''


    @api.depends("requirement_id.requirement_state")
    def _compute_is_amount_editable(self):
        for record in self:
            requirement = record.requirement_id  # Accede al modelo relacionado
            record.is_amount_editable = (
                requirement.requirement_state in ("draft", "refused") or
                (requirement.requirement_state == "administration" and 
                 self.env.user.has_group("mkt_documental_managment.documental_requirement_administration"))
            )


    @api.depends("requirement_id.requirement_state")
    def _compute_is_administration_editable(self):
        for record in self:
            requirement = record.requirement_id  # Accede al modelo relacionado
            record.is_administration_editable = (
                self.env.user.has_group("mkt_documental_managment.documental_requirement_administration") or
                requirement.requirement_state in ("draft", "refused")
            )


    @api.depends('document_file')
    def _compute_filename(self):
        for rec in self:
            if rec.document_file and (not rec.document_filename or not rec.document_filename.endswith('.pdf')):
                rec.document_filename = f"payment_{rec.id}.pdf"

    @staticmethod
    def _final_fname(rec):
        # Cambia si prefieres "Voucher - {rec.requirement_id.display_name}.pdf"
        return f"payment_{rec.id}.pdf"

    @staticmethod
    def _looks_like_text(raw_bytes, sample=4096):
        try:
            raw_bytes[:sample].decode('utf-8')
            return True
        except Exception:
            return False

    @staticmethod
    def _is_image_bytes(raw_bytes):
        if raw_bytes.startswith(b'\xFF\xD8'):  # JPEG
            return True
        if raw_bytes.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
            return True
        if raw_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return True
        return False

    @staticmethod
    def _default_ext_for_mime(mime):
        mapping = {
            'text/plain': '.txt', 'text/csv': '.csv', 'text/html': '.html',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/vnd.oasis.opendocument.text': '.odt',
            'application/vnd.oasis.opendocument.spreadsheet': '.ods',
            'application/vnd.oasis.opendocument.presentation': '.odp',
        }
        return mapping.get(mime)

    @staticmethod
    def _get_soffice_bin():
        return shutil.which('soffice') or shutil.which('libreoffice')

    # -------- Conversión a PDF robusta (imágenes -> Pillow | img2pdf | soffice) --------
    def _convert_to_pdf(self, b64_data, filename=None):
        if not b64_data:
            return b64_data

        raw = base64.b64decode(b64_data)
        in_name = filename or 'document'
        guess_type, enc = mimetypes.guess_type(in_name)
        guess_type = guess_type or ''

        # 1) Si ya es PDF, devuélvelo tal cual
        if guess_type == 'application/pdf' or raw[:4] == b'%PDF':
            return b64_data

        # 2) Imágenes
        if guess_type.startswith('image/') or (Image and self._is_image_bytes(raw)):
            # a) Intento con Pillow
            if Image:
                try:
                    img = Image.open(io.BytesIO(raw))
                    if img.mode in ('RGBA', 'P', 'LA'):
                        img = img.convert('RGB')
                    out = io.BytesIO()
                    try:
                        # Algunos builds no tienen plugin PDF -> KeyError('PDF')
                        img.save(out, format='PDF')
                        return base64.b64encode(out.getvalue())
                    except KeyError:
                        pass  # probamos fallback
                except Exception as e:
                    # seguimos a fallback de img2pdf/soffice
                    pass

            # b) Fallback con img2pdf (ligero y sin plugins)
            try:
                import img2pdf
                pdf_bytes = img2pdf.convert(raw)
                return base64.b64encode(pdf_bytes)
            except Exception:
                pass

            # c) Fallback con LibreOffice
            soffice_bin = self._get_soffice_bin()
            if soffice_bin:
                with tempfile.TemporaryDirectory() as tmp:
                    ext = os.path.splitext(in_name)[1].lower() or '.png'
                    in_path = os.path.join(tmp, f"input{ext}")
                    out_dir = tmp
                    with open(in_path, 'wb') as f:
                        f.write(raw)
                    cmd = [soffice_bin, '--headless', '--convert-to', 'pdf', '--outdir', out_dir, in_path]
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    pdf_path = os.path.splitext(in_path)[0] + '.pdf'
                    if not os.path.exists(pdf_path):
                        # buscar cualquier PDF generado
                        cands = [p for p in os.listdir(out_dir) if p.lower().endswith('.pdf')]
                        if cands:
                            pdf_path = os.path.join(out_dir, cands[0])
                    if not os.path.exists(pdf_path):
                        raise ValidationError(_("LibreOffice no generó el PDF a partir de la imagen."))
                    with open(pdf_path, 'rb') as f:
                        return base64.b64encode(f.read())

            # d) Sin fallbacks disponibles
            raise ValidationError(_(
                "No se pudo convertir la imagen a PDF. Instala Pillow con soporte PDF, o el paquete python 'img2pdf', "
                "o LibreOffice ('soffice').")
            )

        # 3) Office / texto -> LibreOffice
        office_exts = ('.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods', '.odp', '.rtf', '.txt', '.csv', '.html', '.htm')
        ext = os.path.splitext(in_name)[1].lower()
        soffice_bin = self._get_soffice_bin()
        if not soffice_bin:
            raise ValidationError(_("No se encontró 'soffice' (LibreOffice) para convertir %s a PDF.") % (ext or guess_type or 'el archivo'))

        with tempfile.TemporaryDirectory() as tmp:
            in_ext = ext if ext else self._default_ext_for_mime(guess_type) or ('.txt' if self._looks_like_text(raw) else '.bin')
            in_path = os.path.join(tmp, f"input{in_ext}")
            out_dir = tmp
            with open(in_path, 'wb') as f:
                f.write(raw)
            cmd = [soffice_bin, '--headless', '--convert-to', 'pdf', '--outdir', out_dir, in_path]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                raise ValidationError(_("Error de LibreOffice al convertir a PDF: %s")
                                      % (e.stderr.decode('utf-8', errors='ignore') or str(e)))
            pdf_path = os.path.splitext(in_path)[0] + '.pdf'
            if not os.path.exists(pdf_path):
                cands = [p for p in os.listdir(out_dir) if p.lower().endswith('.pdf')]
                if cands:
                    pdf_path = os.path.join(out_dir, cands[0])
            if not os.path.exists(pdf_path):
                raise ValidationError(_("LibreOffice no generó el PDF."))
            with open(pdf_path, 'rb') as f:
                return base64.b64encode(f.read())


    def _final_fname(self):
        # Cambia si quieres "Voucher - {self.requirement_id.display_name}.pdf"
        return f"payment_{self.id}.pdf"

    @staticmethod
    def _is_pdf_b64(b64_data):
        try:
            return base64.b64decode(b64_data, validate=False)[:4] == b'%PDF'
        except Exception:
            return False

    def _post_to_parent(self, created=False, override_b64=None):
        """Upsert del adjunto en el chatter del padre, con conversión a PDF si hace falta."""
        self.ensure_one()
        if not self.requirement_id:
            return

        data_b64 = override_b64 or self.document_file
        if not data_b64:
            return

        fname = self._final_fname()

        # Asegurar PDF
        if not self._is_pdf_b64(data_b64):
            if hasattr(self, '_convert_to_pdf'):
                data_b64 = self._convert_to_pdf(data_b64, self.document_filename or fname)
            else:
                raise ValidationError(_("The file is not a PDF and no converter is available."))

        Attachment = self.env['ir.attachment']
        existing = Attachment.search([
            ('res_model', '=', 'documental.requirements'),
            ('res_id', '=', self.requirement_id.id),
            ('name', '=', fname),
        ], limit=1)

        vals_att = {
            'name': fname,
            'datas': data_b64,
            'mimetype': 'application/pdf',
            'type': 'binary',
            'res_model': 'documental.requirements',
            'res_id': self.requirement_id.id,
        }

        if existing:
            existing.write({'datas': data_b64, 'mimetype': 'application/pdf'})
            attachment = existing
        else:
            attachment = Attachment.create(vals_att)

        msg = _("Uploaded the document from %s (%s).") if created else _("Updated the document from %s (%s).")
        self.requirement_id.message_post(
            body=msg % (self._name, self.display_name),
            attachment_ids=[attachment.id]
        )

        # Renombrar el filename del registro SIN recursión
        desired = fname
        if self.document_filename != desired:
            self.with_context(skip_postproc=True).write({'document_filename': desired})

    @api.model
    def create(self, vals):
        vals = dict(vals)

        # 1) Convertir a PDF si viene archivo
        b64 = vals.get('document_file')
        if b64:
            in_name = vals.get('document_filename') or 'document'
            pdf_b64 = self._convert_to_pdf(b64, in_name)
            vals['document_file'] = pdf_b64
            base, ext = os.path.splitext(in_name)
            vals['document_filename'] = f"{base}.pdf"

        # 2) Crear registro
        rec = super().create(vals)

        # 3) Si YA hay padre en create, adjuntar de inmediato usando el binario de vals
        if rec.requirement_id and vals.get('document_file'):
            rec._post_to_parent(created=True, override_b64=vals['document_file'])

        return rec


    def write(self, vals):
        # Evitar post-proceso interno
        if self.env.context.get('skip_postproc'):
            return super().write(vals)

        vals = dict(vals)
        incoming_b64 = vals.get('document_file')
        parent_changed = 'requirement_id' in vals  # puede venir int o False

        # 1) Convertir a PDF si viene archivo nuevo
        if incoming_b64:
            in_name = vals.get('document_filename') or (self.document_filename if len(self) == 1 else 'document')
            pdf_b64 = self._convert_to_pdf(incoming_b64, in_name)
            vals['document_file'] = pdf_b64
            base, ext = os.path.splitext(in_name)
            vals['document_filename'] = f"{base}.pdf"

        # 2) Escribir cambios
        res = super().write(vals)

        # 3) Post-procesos:
        for rec in self:
            # a) Si hubo archivo -> adjuntar/actualizar en el padre actual
            if incoming_b64 and rec.requirement_id:
                rec._post_to_parent(created=False)
            # b) Si cambió/recibió requirement_id y YA existe archivo, adjuntar aunque no haya archivo nuevo
            elif parent_changed and rec.requirement_id and rec.document_file:
                rec._post_to_parent(created=False)

        return res

    # ---------- Tu método de adjuntar (ya que ahora siempre es PDF) ----------
    def attach_files(self):
        for rec in self:
            if rec.document_file:
                attachment = self.env['ir.attachment'].create({
                    'name': rec.document_filename or f"payment_{rec.id}.pdf",
                    'datas': rec.document_file,
                    'res_model': rec._name,
                    'res_id': rec.id,
                    'type': 'binary',
                    'mimetype': 'application/pdf',
                })
                rec.message_post(body=_("File uploaded successfully"), attachment_ids=[attachment.id])


    @api.model
    def default_get(self, fields_list):
        """ Calcula el valor por defecto de 'amount' basado en el total pendiente a pagar """
        defaults = super().default_get(fields_list)
        requirement_id = self._context.get('default_requirement_id')

        if requirement_id:
            requirement = self.env['documental.requirements'].browse(requirement_id)
            total_paid = sum(requirement.requirement_payment_ids.mapped('amount') or [0])
            remaining_amount = requirement.total_vendor - total_paid
            defaults['amount'] = max(0, remaining_amount)  # Si es negativo, asigna 0

        return defaults