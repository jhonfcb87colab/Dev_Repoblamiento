import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.dialogs import Messagebox
import pyodbc
from datetime import datetime
import warnings

# Silenciamos el aviso de formato de fecha al iniciar el widget
warnings.filterwarnings("ignore", category=UserWarning, module="ttkbootstrap")

###############################
# CONEXION SQL SERVER
###############################

def ejecutar_sp(fecha_inicio, fecha_fin, sp_name):
    try:
        # Configuración de conexión
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=D_SERV-DBI01;"
            "DATABASE=SIG_COLOMBIA_DW;"
            "UID=SERVIENT\\inteligencianegocios;"
            "PWD=N3g0c10S3rv13ntr3g4TGB.159yhn753.*-;"
            "TrustServerCertificate=yes;"
        )
        
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                # Usamos parámetros (?) para evitar inyección SQL y errores de formato
                query = f"EXEC {sp_name} ?, ?"
                cursor.execute(query, (fecha_inicio, fecha_fin))
                conn.commit()
                
        return "SP ejecutado correctamente ✅"

    except Exception as e:
        return f"Error ejecutando SP:\n{str(e)}"


##################################
# VENTANA SECUNDARIA
##################################

class VentanaFechas(tb.Toplevel):
    def __init__(self, parent, titulo_cubo, sp_destino):
        super().__init__(parent)

        self.title(f"Repoblar: {titulo_cubo}")
        self.geometry("450x400")
        self.resizable(False, False)
        self.sp_destino = sp_destino # Guardamos el SP que corresponde al botón presionado
        self.parent = parent

        # Centrar ventana respecto a la principal
        self.grab_set() 

        tb.Label(self, text=f"Configuración para:\n{titulo_cubo}", 
                 font=("Segoe UI", 12, "bold"), justify=CENTER).pack(pady=20)

        # Contenedor de fechas
        frame_fechas = tb.Frame(self)
        frame_fechas.pack(pady=10)

        tb.Label(frame_fechas, text="Fecha Inicial:").grid(row=0, column=0, padx=10, pady=5)
        self.fecha_inicio = DateEntry(frame_fechas, bootstyle="primary", width=15, dateformat="%Y-%m-%d")
        self.fecha_inicio.grid(row=0, column=1, padx=10, pady=5)

        tb.Label(frame_fechas, text="Fecha Final:").grid(row=1, column=0, padx=10, pady=5)
        self.fecha_fin = DateEntry(frame_fechas, bootstyle="primary", width=15, dateformat="%Y-%m-%d")
        self.fecha_fin.grid(row=1, column=1, padx=10, pady=5)

        # Botones de acción
        self.btn_ejecutar = tb.Button(
            self, text="🚀 Iniciar Repoblamiento", 
            bootstyle="success", command=self.ejecutar, width=25
        )
        self.btn_ejecutar.pack(pady=30)

        tb.Button(
            self, text="⬅ Volver al Menú", 
            bootstyle="danger-outline", command=self.volver, width=25
        ).pack()

    def ejecutar(self):
        # Capturamos el texto directamente del entry del widget
        fi = self.fecha_inicio.entry.get()
        ff = self.fecha_fin.entry.get()

        # Feedback visual
        self.btn_ejecutar.config(state="disabled", text="Procesando...")
        self.update()

        resultado = ejecutar_sp(fi, ff, self.sp_destino)

        self.btn_ejecutar.config(state="normal", text="🚀 Iniciar Repoblamiento")
        
        Messagebox.show_info(message=resultado, title="Resultado del Proceso")

    def volver(self):
        self.destroy()
        self.parent.deiconify()


##################################
# VENTANA PRINCIPAL
##################################

class App(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")

        self.title("SISTEMA DE REPOBLAMIENTO DE CUBOS - BI")
        self.geometry("700x550")

        tb.Label(
            self, text="PANEL DE CONTROL REPOBLAMIENTOS",
            font=("Segoe UI", 18, "bold"), bootstyle="inverse-dark"
        ).pack(fill=X, pady=20, padx=20)

        tb.Label(
            self, text="Seleccione el cubo que desea procesar:",
            font=("Segoe UI", 11)
        ).pack(pady=10)

        # Definición de botones con sus respectivos SPs
        opciones = [
            ("📊 ENVIOS MOVILIZADOS", "primary", "SP_REPOBLAR_ENVIOS"),
            ("📁 GUIAS ENTREGADAS (GETP)", "info", "SP_REPOBLAR_GETP"),
            ("⚙ PROCESO LOGISTICO", "warning", "SP_REPOBLAR_LOGISTICA")
        ]

        for texto, estilo, sp in opciones:
            tb.Button(
                self, text=texto, bootstyle=estilo, width=40,
                command=lambda t=texto, s=sp: self.abrir_fechas(t, s)
            ).pack(pady=12)

    def abrir_fechas(self, titulo, sp):
        self.withdraw()
        VentanaFechas(self, titulo, sp)


if __name__ == "__main__":
    app = App()
    app.mainloop()