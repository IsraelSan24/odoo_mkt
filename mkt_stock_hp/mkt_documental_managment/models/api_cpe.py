import json
import requests
import logging

_logger = logging.getLogger(__name__)

url = 'https://apiperu.dev/api/cpe'
token = '4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
}

def apiperu_cpe(emisor_ruc, document_type_code, document_serie,
                document_number, emision_date, total_amount):
    try:
        params = {
            'ruc_emisor': emisor_ruc,
            'codigo_tipo_documento': document_type_code,
            'serie_documento': document_serie,
            'numero_documento': document_number,
            'fecha_de_emision': emision_date,
            'total': total_amount,
        }
        params_json = json.dumps(params)
        response = requests.post(url, data=params_json, headers=headers)
        if response.status_code == 200:
            data = response.json()
            _logger.info('\n\n\n Api response data: %s \n\n\n', data)
            # print('data ', data)
            # access_data = data['data']
            # ruc_emisor = access_data['ruc_emisor']
            # codigo_tipo_documento = access_data['codigo_tipo_documento']
            # serie_documento = access_data['serie_documento']
            # numero_documento = access_data['numero_documento']
            # fecha_de_emision = access_data['fecha_de_emision']
            # total = access_data['total']
            # comprobante_estado_codigo = access_data['comprobante_estado_codigo']
            # comprobante_estado_descripcion = access_data['comprobante_estado_descripcion']
            # empresa_estado_codigo = access_data['empresa_estado_codigo']
            # empresa_estado_descripcion = access_data['empresa_estado_descripcion']
            # empresa_condicion_codigo = access_data['empresa_condicion_codigo']
            # observaciones = access_data['observaciones']
            # return access_data, ruc_emisor, codigo_tipo_documento, serie_documento, numero_documento,\
            #     fecha_de_emision, total, comprobante_estado_codigo, comprobante_estado_descripcion,\
            #     empresa_estado_codigo, empresa_estado_descripcion, empresa_condicion_codigo, observaciones
            # return data['data']
            return data
        else:
            # print(f'Error en la solicitud: {response.status_code}')
            _logger.info('\n\n\n response.status_code: %s \n\n\n', response.status_code)
            # print(response.text)
            _logger.info('\n\n\n response.text: %s \n\n\n', response.text)
            return None
    except requests.RequestException as e:
        _logger.info('\n\n\n Error in request: %s \n\n\n', e)
        return None
    # except requests.RequestException as e:
        # print(f'Error en la solicitud: {e}')
        # _logger.info('\n\n\n eeeeee : %s \n\n\n', e)

# print(apiperu_cpe('20605898506','01','F300','001129','2023-12-01',741.98))
# print(apiperu_cpe('20606174846','01',"E001",'292','2024-06-27',46020))
# print(apiperu_cpe('20609644711','01',"E001",'230','2024-06-27',2006))
# print(apiperu_cpe('20418896915','01','F001','253582','2024-06-05',75.47))
