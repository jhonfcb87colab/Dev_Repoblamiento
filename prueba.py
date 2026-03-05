from Conecction import connSQLITE 
import pandas as pd
db = connSQLITE.ConexionSQLite()


insert_sql = "INSERT INTO CONFIG_CUBOS " \
"(NOMBRE_MOSTRAR, SP_ASOCIADO) " \
"VALUES ('MODELO EFICIENCIA RECOLECCION','[TMP].[REPOBLAR_EFICIENCIA_RECOLECCION]')"
print(db.ejecutar_dml(insert_sql))


if db.conn:
    opciones = pd.DataFrame()
    if db.conn:
        query = "SELECT * FROM CONFIG_CUBOS"
        opciones = db.ejecutar_dql(query)  
        # Iteramos usando itertuples por eficiencia y claridad
        for fila in opciones.itertuples(index=False):
            texto_btn = fila.NOMBRE_MOSTRAR
            valor_sp = fila.SP_ASOCIADO
            print(texto_btn,' - ',valor_sp)
