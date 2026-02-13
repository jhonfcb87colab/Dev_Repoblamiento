from datetime import datetime

# 1. Tu string original (ejemplo)
fecha_str = "2025-01-01" 

# # 2. Convertir string a objeto datetime
# # Ajusta '%d/%m/%Y' según el formato de tu entrada original
# objeto_fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
# # 3. Convertir a string con formato YYYYMMDD
# fecha_final = objeto_fecha.strftime('%Y%m%d')

#print(f"Fecha lista para SQL: {fecha_final}")


print(datetime.strptime(fecha_str, '%Y-%m-%d').strftime('%Y%m%d'))


