# controllers/dni_api_controller.py
# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)


class DNIAPIController(http.Controller):
    
    @http.route('/api/dni/validate', type='json', auth='user', methods=['POST'], csrf=False)
    def validate_dni(self, dni):
        """
        Endpoint para validar DNI a través de API externa
        """
        try:
            # Token de la API
            token = "alterno_3or6s9qzf6cv"
            
            # Headers
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }
            
            # URL de la API
            url = f"http://go.net.pe:3000/api/v2/dni/{str(dni)}"
            
            _logger.info(f"Requesting DNI data for: {dni}")
            
            # Hacer petición GET
            response = requests.get(url, headers=headers, timeout=30)
            
            # Verificar respuesta
            if response.status_code == 200:
                data = response.json()
                access_data = data.get('data', {})
                
                _logger.info(f"DNI data retrieved successfully for: {dni}")
                
                return {
                    'success': True,
                    'data': access_data
                }
            else:
                _logger.error(f"API Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'API returned status {response.status_code}',
                    'message': 'No se pudo obtener los datos del DNI'
                }
                
        except requests.exceptions.Timeout:
            _logger.error(f"Timeout error for DNI: {dni}")
            return {
                'success': False,
                'error': 'timeout',
                'message': 'La consulta tardó demasiado tiempo'
            }
        except requests.exceptions.RequestException as e:
            _logger.error(f"Request error for DNI {dni}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error al conectar con el servicio de validación'
            }
        except Exception as e:
            _logger.error(f"Unexpected error for DNI {dni}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error inesperado al validar el DNI'
            }