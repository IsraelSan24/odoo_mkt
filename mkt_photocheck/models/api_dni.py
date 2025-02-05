import json
import requests

url = 'https://apiperu.dev/api/dni'
token= '61d0d69022c6913d6b35cf682ab78ea14a19b251cebe0efbd433600e6236abe4'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
}

def apiperu_dni(dni):
    try:
        params = {'dni': str(dni)}
        params_json = json.dumps(params)
        response = requests.post(url, data=params_json, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            access_data = data['data']
            return access_data['nombre_completo'],access_data['nombres'],access_data['apellido_paterno'],access_data['apellido_materno']
        else:
            print(f"Fac {response.status_code}")
            print(response.text)
    except requests.RequestException as e:
        print(f'Error {e}')