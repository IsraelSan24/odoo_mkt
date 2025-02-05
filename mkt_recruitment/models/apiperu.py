
import json
import requests


url = 'https://apiperu.dev/api/dni'
token= '4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
}

def apiperu_dni(dni):
    try:
        params = {'dni': str(dni)}
        params_json = json.dumps(params)
        response = requests.post(url, data=params_json, headers=headers, verify=True)
        if response.status_code == 200:
            data = response.json()
            print('data:', data)
            access_data = data['data']
            print('data[data]: ', access_data)
            print("Sucess!")
            return access_data['nombre_completo']
        else:
            print(f"Fac {response.status_code}")
            print(response.text)
    except requests.RequestException as e:
        print(f'Error {e}')
