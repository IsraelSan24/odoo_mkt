import json
import requests

url = "https://apiperu.dev/api/ruc"
token = '4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479'

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
}

def apiperu_ruc(ruc):
    try:
        params = {'ruc': str(ruc)}
        params_json = json.dumps(params)
        response = requests.post(url, data=params_json, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            access_data = data['data']
            address = access_data['direccion']
            complete_address = access_data['direccion_completa']
            ruc = access_data['ruc']
            name = access_data['nombre_o_razon_social']
            state = access_data['estado']
            condition = access_data['condicion']
            department = access_data['departamento']
            province = access_data['provincia']
            district = access_data['distrito']
            ubigeo_sunat = access_data['ubigeo_sunat']
            ubigeo = access_data['ubigeo']
            is_retention = access_data['es_agente_de_retencion']
            return address, complete_address, ruc, name, state, condition,\
                department, province, district, ubigeo_sunat, ubigeo, is_retention
        else:
            print(f"Error en la solicitud: {response.status_code}")
            print(response.text)
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")

# print(apiperu_ruc(20512433821))
