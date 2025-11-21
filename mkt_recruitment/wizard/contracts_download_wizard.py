# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import io
import zipfile
import base64
import logging
from PyPDF2 import PdfFileReader, PdfFileWriter

_logger = logging.getLogger(__name__)


class ContractZipWizard(models.TransientModel):
    _name = "contract.zip.wizard"
    _description = "Generate ZIP of contracts split from combined PDF"
    
    zip_file = fields.Binary("ZIP File", readonly=True)
    zip_filename = fields.Char("File Name", readonly=True)
    
    def _create_zip_from_pdfs(self, pdf_list, contracts):
        """
        Crea un ZIP a partir de una lista de PDFs
        """
        buffer = io.BytesIO()
        
        # Map contract IDs to contract records for easy access
        contracts_map = {c.id: c for c in contracts}
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for contract_id, pdf_bytes in pdf_list:
                if pdf_bytes:
                    contract = contracts_map.get(contract_id)
                    if contract:
                        safe_name = contract.name or str(contract.id)
                        fname = f"{contract.vat or ''}_{safe_name}.pdf"
                        zf.writestr(fname, pdf_bytes)
        
        buffer.seek(0)
        return buffer.read()
    
    def action_generate_zip_contracts(self):
        """
        Main entrypoint: Bulk Render -> Split
        """
        active_ids = self.env.context.get('active_ids') or []
        if not active_ids:
            raise UserError(_("No contracts selected."))
        
        # Obtener report
        report_xmlid = 'mkt_recruitment.report_contract_action'
        report = self.env.ref(report_xmlid, raise_if_not_found=False)
        if not report:
            raise UserError(_("Report %s not found.") % report_xmlid)
        
        contracts = self.env['hr.contract'].browse(active_ids)
        
        # 1. Render ALL contracts in one go (Bulk Render)
        _logger.info(f"Bulk rendering {len(active_ids)} contracts...")
        try:
            # Ensure we are using the right context/user for rendering
            report = report.with_user(self.env.uid)
            # Pass all IDs at once. This generates ONE large PDF.
            pdf_content, _ = report._render_qweb_pdf(res_ids=active_ids)
        except Exception as e:
            _logger.error(f"Error in bulk rendering: {e}")
            raise UserError(_("Error generating PDF report: %s") % str(e))

        # 2. Split the PDF based on contract_n_pages
        pdf_list = []
        
        try:
            # Read the generated big PDF
            input_pdf = PdfFileReader(io.BytesIO(pdf_content))
            total_pages = input_pdf.getNumPages()
            
            # Calculate expected pages
            expected_pages = sum(c.contract_type_id.contract_n_pages for c in contracts)
            
            _logger.info(f"PDF Generated. Total Pages: {total_pages}. Expected Pages: {expected_pages}")
            
            if total_pages != expected_pages:
                # Fallback or Warning? 
                # If pages don't match, splitting will be wrong. 
                # We should probably abort and suggest serial printing or check configuration.
                _logger.warning("Mismatch in page counts! Fallback to serial generation might be safer, but for now raising error.")
                # For now, let's raise an error so the user knows something is wrong with page configuration
                # Alternatively, we could fallback to serial here automatically.
                # Let's try to be smart: if mismatch, fallback to serial loop immediately.
                _logger.info("Page count mismatch detected. Falling back to serial generation for safety.")
                return self._fallback_serial_generation(active_ids, report, contracts)

            current_page = 0
            for contract in contracts:
                n_pages = contract.contract_type_id.contract_n_pages
                if not n_pages:
                    # If a contract has 0 pages defined, we can't split. Fallback.
                    _logger.warning(f"Contract {contract.id} has 0 pages defined. Fallback to serial.")
                    return self._fallback_serial_generation(active_ids, report, contracts)
                
                output = PdfFileWriter()
                for i in range(n_pages):
                    if current_page < total_pages:
                        output.addPage(input_pdf.getPage(current_page))
                        current_page += 1
                
                output_stream = io.BytesIO()
                output.write(output_stream)
                pdf_list.append((contract.id, output_stream.getvalue()))
                
        except Exception as e:
            _logger.error(f"Error splitting PDF: {e}")
            # Fallback to serial if splitting fails
            return self._fallback_serial_generation(active_ids, report, contracts)
        
        # 3. Create ZIP
        zip_data = self._create_zip_from_pdfs(pdf_list, contracts)
        
        # Guardar y retornar
        self.write({
            'zip_file': base64.b64encode(zip_data),
            'zip_filename': 'contracts.zip',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=zip_file&filename_field=zip_filename&download=true' % (
                self._name, self.id),
            'target': 'self',
        }

    def _fallback_serial_generation(self, active_ids, report, contracts):
        """
        Fallback method: Generate PDFs serially if bulk split fails.
        """
        _logger.info("Executing fallback serial generation...")
        result = []
        report = report.with_user(self.env.uid)
        
        for contract_id in active_ids:
            try:
                pdf_bytes, _ = report._render_qweb_pdf(res_ids=[contract_id])
                result.append((contract_id, pdf_bytes))
            except Exception as e:
                _logger.error(f"Error rendering contract {contract_id}: {e}")
                result.append((contract_id, None))
        
        if not any(p[1] for p in result):
            raise UserError(_("No PDFs were generated successfully (even after fallback)."))
            
        zip_data = self._create_zip_from_pdfs(result, contracts)
        
        self.write({
            'zip_file': base64.b64encode(zip_data),
            'zip_filename': 'contracts_fallback.zip',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=zip_file&filename_field=zip_filename&download=true' % (
                self._name, self.id),
            'target': 'self',
        }
