# import requests
# from datetime import datetime

# def api_change_type():
#     url = f"https://www.sunat.gob.pe/a/txt/tipoCambio.txt"
#     response_change_type = requests.get(url)
#     if response_change_type.status_code == 200:
#         data_response = response_change_type.text
#         separate_data = data_response.split('|')
#         date_str = separate_data[0]
#         buy_change_type = float(separate_data[1])
#         sell_change_type = float(separate_data[2])
#         exchange_type_date = datetime.strptime(date_str,"%d/%m/%Y").date()
#         print(buy_change_type)
#         print(sell_change_type)
#         print(exchange_type_date)
#         return exchange_type_date,buy_change_type, sell_change_type
#     else:
#         data_response = None

# # print(api_change_type())

import requests
from datetime import date

url = "https://apiperu.dev/api/tipo_de_cambio"
token = "61d0d69022c6913d6b35cf682ab78ea14a19b251cebe0efbd433600e6236abe4"
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

def api_change_type():
    fecha_actual = date.today().strftime("%Y-%m-%d")
    params = {'fecha': fecha_actual}
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        try:
            data = response.json()
            data = data['data']
            sunat_date = data['fecha_sunat']
            sell = data['venta']
            buy = data['compra']
            return sunat_date, buy, sell
        except ValueError as e:
            print(response.text)
    else:
        print(response.text)
