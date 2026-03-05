import base64
from datetime import datetime, timedelta
import math

class AutenticacionTOKEN:
    def respuestasToken():
        
        usuario = "PIAPPLUSER"
        password = "WBS_rfc_2018XXX"
        
        credenciales = f"{usuario}:{password}"
        token = base64.b64encode(credenciales.encode("utf-8")).decode("utf-8")
        return token

if __name__ == "__main__":
    var = AutenticacionTOKEN.respuestasToken()
    time_now = datetime.now()
    anio = time_now.year
    mes = time_now.month
    dia = time_now.day
    consolidado_fecha =  ((anio*100) + mes)*100 + dia
    str_fecha = str(consolidado_fecha)
    var_connection = "D_SERV-DBI01;Database=SIG_COLOMBIA_DW;Integrated Security=true;"
    str_para_tekenizar = str_fecha + '|' + var_connection
    
    token = base64.b64encode(str_para_tekenizar.encode("utf-8")).decode("utf-8")
    print("Encriptacion:", token)

