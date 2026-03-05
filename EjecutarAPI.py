import http.client
import json
import base64
from datetime import datetime

# --- VOLVEMOS A HTTP (Sin la S) ---
# El error WRONG_VERSION_NUMBER confirma que el puerto 5555 es HTTP
conn = http.client.HTTPConnection("t_serv-dbi01", 5555)

# Limpieza de variables (quitando posibles espacios invisibles)
SERVIDOR = 'D_SERV-DBI01'
BASE_DE_DATOS = 'SIG_COLOMBIA_DW'
SP_EJECUTAR = '[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]'
FECH_INI = '2026-01-01'
FECH_FIN = '2026-02-01'

# # Agregamos el User-Agent que usa Thunder Client por si el servidor lo requiere
# headersList = {
#     "Accept": "*/*",
#     "User-Agent": "Thunder Client (https://www.thunderclient.com)",
#     "Content-Type": "application/json"
# }

# Generación dinámica del Token
time_now = datetime.now()
str_fecha = time_now.strftime("%Y%m%d") 
var_connection = f"{SERVIDOR};Database={BASE_DE_DATOS};Integrated Security=true;"
str_para_tekenizar = f"{str_fecha}|{var_connection}"

token_dinamico = base64.b64encode(str_para_tekenizar.encode("utf-8")).decode("utf-8")

payload = json.dumps({
    "Param1": FECH_INI,
    "Param2": FECH_FIN,
    "Param3": SP_EJECUTAR,
    "Param4": token_dinamico
})

try:
    # Realizar la petición
    conn.request("POST", "/api/datos", payload)#, headersList
    response = conn.getresponse()
    
    print(f"Status: {response.status}")
    print(f"Reason: {response.reason}")
    
    result = response.read()
    print("\nRespuesta del servidor:")
    print(result.decode("utf-8"))



except Exception as e:
    print(f"Error al conectar: {e}")

finally:
    conn.close()






























# import http.client
# import json
# import base64
# from datetime import datetime, timedelta

# conn = http.client.HTTPConnection("t_serv-dbi01", 5555)

# SERVIDOR = 'D_SERV-DBI01'
# BASE_DE_DATOS =  'SIG_COLOMBIA_DW'
# SP_EJECUTAR = '[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]'
# FECH_INI = '2026-01-01'
# FECH_FIN = '2026-02-01'


# headersList = {
#     "Accept": "*/*",
#     "Content-Type": "application/json"
# }

# time_now = datetime.now()
# anio = time_now.year
# mes = time_now.month
# dia = time_now.day
# consolidado_fecha =  ((anio*100) + mes)*100 + dia
# str_fecha = str(consolidado_fecha)
# var_connection = f"{SERVIDOR};Database={BASE_DE_DATOS};Integrated Security=true;"
# str_para_tekenizar = str_fecha + '|' + var_connection

# token = base64.b64encode(str_para_tekenizar.encode("utf-8")).decode("utf-8")

# print(token)



# payload = json.dumps({
#     "Param1": FECH_INI,
#     "Param2": FECH_FIN,
#     "Param3": SP_EJECUTAR,
#     "Param4": "MjAyNjAzMDN8RF9TRVJWLURCSTAxO0RhdGFiYXNlPVNJR19DT0xPTUJJQV9EVztJbnRlZ3JhdGVkIFNlY3VyaXR5PXRydWU7"
# })

# conn.request("POST", "/api/datos", payload, headersList)

# response = conn.getresponse()

# print("Status:", response.status)
# print("Reason:", response.reason)

# result = response.read()
# print(result.decode("utf-8"))

# conn.close()
