# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import io
import zipfile
import base64
import logging
_logger = logging.getLogger(__name__)

# from PyPDF2 import PdfFileReader, PdfFileWriter
try:
    # from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2 import PdfFileReader, PdfFileWriter
    PYPDF2_AVAILABLE = True
except Exception:
    PYPDF2_AVAILABLE = False


class ContractZipWizard(models.TransientModel):
    _name = "contract.zip.wizard"
    _description = "Generate ZIP of contracts split from combined PDF"

    zip_file = fields.Binary("ZIP File", readonly=True)
    zip_filename = fields.Char("File Name", readonly=True)

    def action_generate_zip_from_combined(self):
        """
        Main entrypoint:
         - render combined PDF once
         - split according to mode
         - create zip and populate zip_file, zip_filename
         - return act_url to download
        """
        active_ids = self.env.context.get('active_ids') or []
        if not active_ids:
            raise UserError(_("No contracts selected."))

        # Replace with your report xml id
        report_xmlid = 'mkt_recruitment.report_contract_action'  # <- ajustar
        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            raise UserError(_("Report %s not found. Adjust report_xmlid in the wizard.") % report_xmlid)

        # 1) render combined PDF (single call) as bytes
        pdf_all_bytes, _ = report.with_user(self.env.uid)._render_qweb_pdf(active_ids)

        # if PyPDF2 not available, return the combined PDF inside the ZIP as a single file
        if not PYPDF2_AVAILABLE:
            _logger.info("\n\n\n-----------------PYPDF2 NOT AVAILABLE---------------\n\n\n")
            # put combined PDF as a single file in zip
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("combined_contracts.pdf", pdf_all_bytes)
            buffer.seek(0)
            data = buffer.read()
            self.write({
                'zip_file': base64.b64encode(data),
                'zip_filename': 'contracts.zip',
            })
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/?model=%s&id=%s&field=zip_file&filename_field=zip_filename&download=true' % (self._name, self.id),
                'target': 'self',
            }

        # 2) split the big PDF using PyPDF2
        reader = PdfFileReader(io.BytesIO(pdf_all_bytes))

        contracts = self.env['hr.contract'].browse(active_ids)
        pages_per_contract = [contract.contract_type_id.contract_n_pages for contract in contracts]
        total_pages = len(reader.pages)

        # _logger.info(f"\n\n\n{active_ids}\n\n\n")
        # _logger.info(f"\n\n\n{contracts.ids}\n\n\n")
        # _logger.info(f"\n\n\n{type(pages_per_contract)} -- {type(pages_per_contract[0])} -- {pages_per_contract} -- {sum(pages_per_contract)} -- {total_pages}  \n\n\n")
        
        if sum(pages_per_contract) != total_pages:
            _logger.info("\n\n\nNÚMERO DE PÁGINAS NO ES IGUAL A PÁGINA POR CONTRATO\n\n\n")

            # If mismatch, prefer a graceful fallback: try to distribute evenly
            # but warn the user
            raise UserError(_("Sum of pages_per_contract (%s) does not equal total pages in PDF (%s). Please check.") % (sum(pages_per_contract), total_pages))

        # split according to page counts
        files = []
        offset = 0
        for idx, pages_count in enumerate(pages_per_contract):
            writer = PdfFileWriter()
            for p in range(offset, offset + pages_count):
                writer.addPage(reader.pages[p])
            offset += pages_count
            buf = io.BytesIO()
            writer.write(buf)
            buf.seek(0)
            contract = contracts[idx]
            safe_name = contract.name or str(contract.id)
            fname = f"{contract.employee_id.identification_id}_{safe_name}.pdf"
            files.append((fname, buf.read()))

        # 3) create zip in memory (streaming)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for fname, content in files:
                zf.writestr(fname, content)
        buffer.seek(0)
        data = buffer.read()

        # 4) write to transient (so web/content can serve it)
        self.write({
            'zip_file': base64.b64encode(data),
            'zip_filename': 'contracts_split.zip',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=zip_file&filename_field=zip_filename&download=true' % (self._name, self.id),
            'target': 'self',
        }
