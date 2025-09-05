# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import io
import zipfile
import base64
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

_logger = logging.getLogger(__name__)


class ContractZipWizard(models.TransientModel):
    _name = "contract.zip.wizard"
    _description = "Generate ZIP of contracts split from combined PDF"
    
    zip_file = fields.Binary("ZIP File", readonly=True)
    zip_filename = fields.Char("File Name", readonly=True)
    
    def _render_pdf_batch(self, contract_ids, report):
        """
        Renderiza un batch de contratos y retorna los PDFs individuales
        """
        result = []
        for contract_id in contract_ids:
            try:
                # Renderiza individualmente para mantener footers correctos
                pdf_bytes, _ = report.with_user(self.env.uid)._render_qweb_pdf(
                    res_ids=[contract_id],
                    )
                result.append((contract_id, pdf_bytes))
            except Exception as e:
                _logger.error(f"Error rendering contract {contract_id}: {e}")
                result.append((contract_id, None))
        return result
    
    def _split_into_batches(self, items, num_batches):
        """
        Divide una lista en n batches aproximadamente iguales
        """
        batch_size = len(items) // num_batches
        remainder = len(items) % num_batches
        
        batches = []
        start = 0
        
        for i in range(num_batches):
            # Añadir 1 elemento extra a los primeros batches si hay remainder
            current_batch_size = batch_size + (1 if i < remainder else 0)
            end = start + current_batch_size
            batches.append(items[start:end])
            start = end
            
        return batches
    
    def _parallel_pdf_generation(self, active_ids, report, num_workers=4):
        """
        Genera PDFs en paralelo usando ThreadPoolExecutor
        """
        # Dividir IDs en batches
        batches = self._split_into_batches(active_ids, num_workers)
        
        # Diccionario thread-safe para almacenar resultados
        all_pdfs = {}
        lock = threading.Lock()
        
        def process_batch(batch):
            # Crear nuevo environment para este thread
            with self.env.registry.cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                wizard = new_env[self._name].browse(self.id)
                report_in_thread = new_env.ref('mkt_recruitment.report_contract_action')
                
                batch_results = wizard._render_pdf_batch(batch, report_in_thread)
                
                with lock:
                    for contract_id, pdf_bytes in batch_results:
                        all_pdfs[contract_id] = pdf_bytes
                
                new_cr.commit()
        
        # Ejecutar en paralelo
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(process_batch, batch) for batch in batches if batch]
            
            # Esperar a que todos terminen
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    _logger.error(f"Error in parallel processing: {e}")
        
        # Ordenar PDFs según el orden original (puede que no sea necesario)
        ordered_pdfs = []
        for contract_id in active_ids:
            if contract_id in all_pdfs and all_pdfs[contract_id]:
                ordered_pdfs.append(all_pdfs[contract_id])
        
        return ordered_pdfs
    
    def _create_zip_from_pdfs(self, pdf_list, contracts):
        """
        Crea un ZIP a partir de una lista de PDFs
        """
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for idx, pdf_bytes in enumerate(pdf_list):
                if idx < len(contracts):
                    contract = contracts[idx]
                    safe_name = contract.name or str(contract.id)
                    fname = f"{contract.employee_id.identification_id}_{safe_name}.pdf"
                    zf.writestr(fname, pdf_bytes)
        
        buffer.seek(0)
        return buffer.read()
    
    def action_generate_zip_contracts(self):
        """
        Main entrypoint con paralelización
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
        
        # Determinar número de workers basado en la cantidad de contratos
        num_workers = min(2, max(1, len(active_ids) // 5))  # Max 2 workers, min 1
        _logger.info(f"Processing {len(active_ids)} contracts with {num_workers} workers")
        
        # Generar PDFs en paralelo
        pdf_list = self._parallel_pdf_generation(active_ids, report, num_workers)
        
        if not pdf_list:
            raise UserError(_("No PDFs were generated successfully."))
        
        # Crear ZIP
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
