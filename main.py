import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import pyodbc
import warnings
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

warnings.filterwarnings("ignore")

#PATH_DB_SQLITE = "Dataset/Credenciales.db"
PATH_DB_SQLITE = r"\\T_serv-dbi01\t\App_Automatizacion\Repoblmiento_DB\Credenciales.db"
# 🔥 Pool global de procesos
executor = ProcessPoolExecutor(max_workers=1)


# =====================================
# STORED PROCEDURE (PROCESO SEPARADO)
# =====================================

def ejecutar_sp(fecha_inicio, fecha_fin, sp_name):

    try:

        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=D_SERV-DBI01;"
            "DATABASE=SIG_COLOMBIA_DW;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            query = f"EXEC {sp_name} ?, ?"
            cursor.execute(query, fecha_inicio, fecha_fin)

            conn.commit()
        Messagebox.show_info(
            message="✅ El Stored Procedure finalizó correctamente.",
            title="Proceso Finalizado"
        )

        return "✅ Stored Procedure ejecutado correctamente."

    except Exception as e:
        return f"❌ Error ejecutando SP:\n{str(e)}"


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

    # ===============================

    def ejecutar(self):

        fi = self.fi.entry.get()
        ff = self.ff.entry.get()

        self.btn.config(state="disabled", text="Procesando...")
        self.progress.pack(pady=15)
        self.progress.start(10)

        self.config(cursor="watch")

        self.future = executor.submit(
            ejecutar_sp,
            fi,
            ff,
            self.sp_destino
        )

        self.after(400, self.verificar_estado)

    # ===============================

    def verificar_estado(self):

        if self.future.done():

            resultado = self.future.result()

            self.progress.stop()

            Messagebox.show_info(
                message=resultado,
                title="Resultado del Proceso"
            )

            self.destroy()
            return

        self.after(400, self.verificar_estado)


# =====================================
# PANEL PRINCIPAL
# =====================================

class AppPrincipal(tb.Toplevel):

    def __init__(self, parent, rol):
        super().__init__(parent)

        self.title("SISTEMA DE REPOBLAMIENTO BI")
        self.geometry("650x500")

        tb.Label(
            self,
            text=f"PANEL DE CONTROL - {rol}",
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
# LOGIN (VENTANA RAÍZ)
# =====================================

class VentanaLogin(tb.Window):

    def __init__(self):
        super().__init__(themename="darkly")

        self.title("Acceso BI")
        self.geometry("420x420")

        container = tb.Frame(self, padding=40)
        container.pack(expand=True)

        tb.Label(
            container,
            text="LOGIN SISTEMA BI",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        self.user = tb.Entry(container, width=30)
        self.user.pack(pady=10)
        self.user.insert(0, "admin")

        self.password = tb.Entry(container, width=30, show="*")
        self.password.pack(pady=10)
        self.password.insert(0, "admin123")

        tb.Button(
            container,
            text="Ingresar",
            bootstyle="success",
            width=25,
            command=self.login
        ).pack(pady=20)

    # ===============================

    def login(self):

        u = self.user.get()
        p = self.password.get()

        try:
            with sqlite3.connect(PATH_DB_SQLITE) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT TIPO_PERMISO_ACCES, ESTADO FROM CREDENCIALES WHERE USUARIO=? AND PASSWORD=?",
                    (u, p)
                )

                datos = cursor.fetchone()

            if datos:

                rol, estado = datos

                if estado == 1:

                    # ocultamos login
                    self.withdraw()

                    AppPrincipal(self, rol)

                else:
                    Messagebox.show_error("Usuario deshabilitado.")

            else:
                Messagebox.show_error("Credenciales incorrectas.")

        except Exception as e:
            Messagebox.show_error(f"Error DB:\n{e}")


# =====================================

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)

    app = VentanaLogin()
    app.mainloop()
