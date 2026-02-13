import sqlite3
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from CtrlAppPrincipal import AppPrincipal

#PATH_DB_SQLITE = "Dataset/Credenciales.db"
PATH_DB_SQLITE = r"\\T_serv-dbi01\t\App_Automatizacion\Repoblmiento_DB\Credenciales.db"


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

