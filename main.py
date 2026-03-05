import sqlite3
import pandas as pd
import pyodbc
import warnings
import multiprocessing
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from concurrent.futures import ProcessPoolExecutor
from Conecction.ConnSQL import ConexionSQL
from APIConection.EjecutarAPI import EjecutarAPI
from Conecction import connSQLITE 

warnings.filterwarnings("ignore")

#PATH_DB_SQLITE = "Dataset/Credenciales.db"
PATH_DB_SQLITE = r"\\T_serv-dbi01\t\App_Automatizacion\Repoblmiento_DB\Credenciales.db"
# 🔥 Pool global de procesos
executor = ProcessPoolExecutor(max_workers=1)



class VentanaFechas(tb.Toplevel):

    def __init__(self, parent, titulo_cubo, sp_destino):
        super().__init__(parent)

        self.title(f"Repoblar: {titulo_cubo}")
        self.geometry("500x600")
        #self.wm_state('zoomed')
        self.resizable(False, False)

        self.sp_destino = sp_destino
        self.sevidor = 'D_SERV-DBI01'
        self.base_datos = 'SIG_COLOMBIA_DW'



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
            EjecutarAPI.llamar_servicio,
            self.sevidor,
            self.base_datos,
            self.sp_destino,
            fi,
            ff            
        )
        self.after(400, self.verificar_estado)
        ####self.destroy()

        print("Proceso iniciado en segundo plano...",self.future)



    def verificar_estado(self):
            # Si el proceso ya terminó (status: 200 que ya viste en consola)
            if self.future.done():
                try:
                    resultado = self.future.result()
                    self.progress.stop()
                    
                    Messagebox.show_info(message=f"Respuesta: {resultado}", title="Éxito")
                    
                except Exception as e:
                    Messagebox.show_error(message=f"Error: {e}")
                
                finally:
                    # ESTO ES LO QUE CIERRA LA VENTANA
                    if self.master:
                        self.master.deiconify() # Muestra la ventana principal de nuevo
                    self.destroy() # Cierra la ventana actual de carga
                return

            # Si aún no termina, vuelve a llamar a esta función en 400ms
            self.after(400, self.verificar_estado)


# =====================================
# PANEL PRINCIPAL
# =====================================

class AppPrincipal(tb.Toplevel):

    def __init__(self, parent, rol):
        super().__init__(parent)

        self.title("SISTEMA DE REPOBLAMIENTO BI")
        self.geometry("500x600")

        tb.Label(
            self,
            text=f"PANEL DE CONTROL - {rol}",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=30)

        db = connSQLITE.ConexionSQLite()
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
            
                    # Creamos el botón
                    btn = tb.Button(
                        self,
                        text=texto_btn,
                        bootstyle="primary",
                        width=40
                    )
                    # El comando destruye 'self' (la ventana AppPrincipal) y abre VentanaFechas
                    # Usamos la ventana principal (el root) como padre para que la nueva ventana no muera
                    btn.config(command=lambda t=texto_btn, s=valor_sp: [VentanaFechas(self.master, t, s), self.destroy()])           
                    btn.pack(pady=10)



        # opciones = [
        #     ("📊 ENVIOS MOVILIZADOS",
        #      "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]"),

        #     ("📁 GUIAS ENTREGADAS",
        #      "NA"),

        #     ("⚙ PROCESO LOGISTICO",
        #      "NA")
        # ]


        # for texto, sp in opciones:
        #     # Creamos el botón
        #     btn = tb.Button(
        #         self,
        #         text=texto,
        #         bootstyle="primary",
        #         width=40
        #     )
        #     # El comando destruye 'self' (la ventana AppPrincipal) y abre VentanaFechas
        #     # Usamos la ventana principal (el root) como padre para que la nueva ventana no muera
        #     btn.config(command=lambda t=texto, s=sp: [VentanaFechas(self.master, t, s), self.destroy()])           
        #     btn.pack(pady=10)

        tb.Button(
                    self,
                    text="🛑 FINALIZAR TODO EL PROGRAMA",
                    bootstyle="danger", # Rojo sólido para resaltar
                    width=40,
                    command=self.salir_total
                ).pack(pady=20)
        
    def salir_total(self):
            """Cierra todas las ventanas y finaliza el proceso de Python"""
            self.master.destroy() # Destruye la ventana principal (Root)
            self.quit()           # Sale del mainloop


# =====================================
# LOGIN (VENTANA RAÍZ)
# =====================================

class VentanaLogin(tb.Window):

    def __init__(self):
        super().__init__(themename="darkly")

        self.title("Acceso BI")
        self.geometry("500x600")

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
        self.password.insert(0, "xxxxxxxxxxxxxxx") ##admin123

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
