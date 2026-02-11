import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import pyodbc
import warnings
from concurrent.futures import ProcessPoolExecutor

warnings.filterwarnings("ignore")

PATH_DB_SQLITE = "Dataset/Credenciales.db"

# Pool global (MUY IMPORTANTE)
executor = ProcessPoolExecutor(max_workers=1)


# =====================================
# EJECUTAR SP (CORRE EN OTRO PROCESO)
# =====================================

def ejecutar_sp(fecha_inicio, fecha_fin, sp_name):

    try:

        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=D_SERV-DBI01;"
            "DATABASE=SIG_COLOMBIA_DW;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=300;"
        )

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            query = f"EXEC {sp_name} ?, ?"

            cursor.execute(query, fecha_inicio, fecha_fin)
            conn.commit()

        return "✅ Stored Procedure ejecutado correctamente."

    except Exception as e:
        return f"❌ Error:\n{str(e)}"


# =====================================
# VENTANA FECHAS
# =====================================

class VentanaFechas(tb.Toplevel):

    def __init__(self, parent, titulo_cubo, sp_destino):
        super().__init__(parent)

        self.title(f"Repoblar: {titulo_cubo}")
        self.geometry("450x420")
        self.resizable(False, False)

        self.sp_destino = sp_destino
        self.grab_set()

        tb.Label(
            self,
            text=f"Configuración para:\n{titulo_cubo}",
            font=("Segoe UI", 12, "bold"),
            justify=CENTER
        ).pack(pady=20)

        frame = tb.Frame(self)
        frame.pack(pady=10)

        tb.Label(frame, text="Fecha Inicial:").grid(row=0, column=0, padx=10, pady=5)
        self.fi = tb.widgets.DateEntry(frame, width=15, dateformat="%Y-%m-%d")
        self.fi.grid(row=0, column=1)

        tb.Label(frame, text="Fecha Final:").grid(row=1, column=0, padx=10, pady=5)
        self.ff = tb.widgets.DateEntry(frame, width=15, dateformat="%Y-%m-%d")
        self.ff.grid(row=1, column=1)

        self.btn = tb.Button(
            self,
            text="🚀 Iniciar Repoblamiento",
            bootstyle="success",
            command=self.ejecutar
        )
        self.btn.pack(pady=20)

        self.progress = tb.Progressbar(
            self,
            mode="indeterminate",
            bootstyle="info-striped",
            length=250
        )

    # =====================================

    def ejecutar(self):

        fi = self.fi.entry.get()
        ff = self.ff.entry.get()

        self.btn.config(state="disabled", text="Procesando...")

        self.progress.pack(pady=15)
        self.progress.start(10)

        self.config(cursor="watch")

        # 🔥 EJECUTA EN OTRO PROCESO
        self.future = executor.submit(
            ejecutar_sp,
            fi,
            ff,
            self.sp_destino
        )

        # monitorear sin congelar UI
        self.after(400, self.verificar_estado)

    # =====================================

    def verificar_estado(self):

        if self.future.done():

            resultado = self.future.result()

            self.progress.stop()

            Messagebox.show_info(
                message=resultado,
                title="Resultado del Proceso"
            )

            # 🔥 cerrar ventana automáticamente
            self.destroy()

            return

        self.after(400, self.verificar_estado)


# =====================================
# APP PRINCIPAL
# =====================================

class AppPrincipal(tb.Window):

    def __init__(self):
        super().__init__(themename="darkly")

        self.title("SISTEMA DE REPOBLAMIENTO BI")
        self.geometry("650x500")

        tb.Label(
            self,
            text="PANEL DE REPOBLAMIENTO",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=30)

        opciones = [
            ("📊 ENVIOS MOVILIZADOS",
             "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]"),

            ("📁 GUIAS ENTREGADAS",
             "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]"),

            ("⚙ PROCESO LOGISTICO",
             "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]")
        ]

        for texto, sp in opciones:

            tb.Button(
                self,
                text=texto,
                bootstyle="primary",
                width=40,
                command=lambda t=texto, s=sp: VentanaFechas(self, t, s)
            ).pack(pady=10)


# =====================================

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()
