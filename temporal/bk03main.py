import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import pyodbc
import warnings

# Intentamos la importación más compatible para Tableview para evitar que el programa no arranque
try:
    from ttkbootstrap.widgets.tableview import Tableview
except ImportError:
    try:
        from ttkbootstrap.tableview import Tableview
    except ImportError:
        Tableview = None 

# Silenciar avisos
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# CONFIGURACIÓN DE RUTAS Y CONEXIONES
PATH_DB_SQLITE = "Dataset/Credenciales.db"

def ejecutar_sp(fecha_inicio, fecha_fin, sp_name):
    try:
        print('Ingreso a la conexion  a la base de datos')
        print(f"se ejecutara este SP asi EXEC {sp_name} '{fecha_inicio}', '{fecha_fin}'")
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=D_SERV-DBI01;"
            "DATABASE=SIG_COLOMBIA_DW;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                print(sp_name)
                #print(f"EXEC {sp_name} ?, ?")
                #query = f"EXEC {sp_name} ?, ?"
                #print(f' SP encapsulado {query}')
                query = f"EXEC {sp_name} '{fecha_inicio}', '{fecha_fin}'"
                #cursor.execute(query, (fecha_inicio, fecha_fin))
                print(f'el sp esta listo {query}')
                cursor.execute(query)
                print('Finaliza cursor')
                conn.commit()
                print('Finaliza commit')
        return "SP ejecutado correctamente ✅"       
    except Exception as e:
        return f"Error ejecutando SP:\n{str(e)}"

    

# --- VENTANA PARA CONFIGURAR FECHAS ---
class VentanaFechas(tb.Toplevel):
    def __init__(self, parent, titulo_cubo, sp_destino):
        super().__init__(parent)
        self.title(f"Repoblar: {titulo_cubo}")
        self.geometry("450x450")
        self.resizable(False, False)
        self.sp_destino = sp_destino
        self.parent = parent
        self.grab_set() 

        tb.Label(self, text=f"Configuración para:\n{titulo_cubo}", 
                 font=("Segoe UI", 12, "bold"), justify=CENTER).pack(pady=20)

        frame_fechas = tb.Frame(self)
        frame_fechas.pack(pady=10)

        tb.Label(frame_fechas, text="Fecha Inicial:").grid(row=0, column=0, padx=10, pady=5)
        self.fecha_inicio = tb.widgets.DateEntry(frame_fechas, bootstyle="primary", width=15, dateformat="%Y-%m-%d")
        self.fecha_inicio.grid(row=0, column=1, padx=10, pady=5)

        tb.Label(frame_fechas, text="Fecha Final:").grid(row=1, column=0, padx=10, pady=5)
        self.fecha_fin = tb.widgets.DateEntry(frame_fechas, bootstyle="primary", width=15, dateformat="%Y-%m-%d")
        self.fecha_fin.grid(row=1, column=1, padx=10, pady=5)

        self.btn_ejecutar = tb.Button(self, text="🚀 Iniciar Repoblamiento", bootstyle="success", 
                                      command=self.ejecutar, width=25)
        self.btn_ejecutar.pack(pady=30)

        tb.Button(self, text="⬅ Cerrar", bootstyle="danger-outline", 
                  command=self.destroy, width=25).pack()

    def ejecutar(self):
        fi = self.fecha_inicio.entry.get()
        ff = self.fecha_fin.entry.get()
        self.btn_ejecutar.config(state="disabled", text="Procesando...")
        self.update()

        resultado = ejecutar_sp(fi, ff, self.sp_destino)
        self.btn_ejecutar.config(state="normal", text="🚀 Iniciar Repoblamiento")
        Messagebox.show_info(message=resultado, title="Resultado del Proceso")

# --- GESTIÓN DE USUARIOS (ADMIN) ---
class PanelAdmin(tb.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Usuarios - BI")
        self.geometry("900x600")
        self.grab_set()

        container = tb.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=True)

        tb.Label(container, text="ADMINISTRACIÓN DE ACCESOS", font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.columnas = [
            {"text": "ID", "stretch": False},
            {"text": "Usuario", "stretch": True},
            {"text": "Rol", "stretch": True},
            {"text": "Estado", "stretch": True}
        ]

        if Tableview:
            self.dt = Tableview(master=container, coldata=self.columnas, rowdata=[], bootstyle="info", paginated=True)
            self.dt.pack(fill=BOTH, expand=True, pady=10)
        
        btns = tb.Frame(container)
        btns.pack(fill=X, pady=10)
        tb.Button(btns, text="🔄 Cambiar Estado (ON/OFF)", bootstyle=WARNING, command=self.alternar_estado).pack(side=LEFT, padx=5)
        tb.Button(btns, text="🔄 Refrescar", bootstyle=INFO, command=self.cargar_datos).pack(side=RIGHT, padx=5)
        self.cargar_datos()

    def cargar_datos(self):
        rows = []
        try:
            with sqlite3.connect(PATH_DB_SQLITE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID, USUARIO, TIPO_PERMISO_ACCES, ESTADO FROM CREDENCIALES")
                for f in cursor.fetchall():
                    est = "✅ ACTIVO" if f[3] == 1 else "❌ INACTIVO"
                    rows.append((f[0], f[1], f[2], est))
            self.dt.build_table_data(self.columnas, rows)
        except: pass

    def alternar_estado(self):
        sel = self.dt.view.selection()
        if not sel: return
        vals = self.dt.view.item(sel[0], "values")
        nuevo = 0 if "ACTIVO" in vals[3] else 1
        with sqlite3.connect(PATH_DB_SQLITE) as conn:
            conn.execute("UPDATE CREDENCIALES SET ESTADO = ? WHERE ID = ?", (nuevo, vals[0]))
            conn.commit()
        self.cargar_datos()

# --- PANEL PRINCIPAL DE REPOBLAMIENTO ---
class AppPrincipal(tb.Toplevel):
    def __init__(self, rol):
        super().__init__()
        self.title("SISTEMA DE REPOBLAMIENTO - BI")
        self.geometry("750x650")

        # Header
        tb.Label(self, text=f"PANEL DE CONTROL - {rol}", font=("Segoe UI", 18, "bold"), 
                 bootstyle="inverse-dark").pack(fill=X, pady=20, padx=20)

        # Botón de Admin si aplica
        if rol == "ADMINISTRADOR":
            tb.Button(self, text="🛡️ Gestionar Usuarios", bootstyle="warning-outline", 
                      command=PanelAdmin, width=30).pack(pady=10)

        tb.Label(self, text="Seleccione el cubo que desea procesar:", font=("Segoe UI", 11)).pack(pady=20)

        # Restauración de botones de procesos
        opciones = [
            ("📊 ENVIOS MOVILIZADOS", "primary", "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]"),
            ("📁 GUIAS ENTREGADAS (GETP)", "info", "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]"),
            ("⚙ PROCESO LOGISTICO", "warning", "[TMP].[REPOBLAMIENTO_LLAMAR_ETL_EJECUTAR_SP_ENVIOS_MOVILIZADOS_2]")
        ]

        for texto, estilo, sp in opciones:
            tb.Button(self, text=texto, bootstyle=estilo, width=45,
                      command=lambda t=texto, s=sp: self.abrir_fechas(t, s)).pack(pady=12)

    def abrir_fechas(self, titulo, sp):
        VentanaFechas(self, titulo, sp)

# --- VENTANA DE LOGIN ---
class VentanaLogin(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Acceso BI - Credenciales")
        self.geometry("450x500")

        container = tb.Frame(self, padding=30)
        container.pack(expand=True)

        tb.Label(container, text="LOGIN SISTEMA BI", font=("Segoe UI", 20, "bold")).pack(pady=30)
        
        self.user_ent = tb.Entry(container, width=35); self.user_ent.pack(pady=10)
        self.user_ent.insert(0, "admin")

        self.pass_ent = tb.Entry(container, width=35, show="*"); self.pass_ent.pack(pady=10)
        self.pass_ent.insert(0, "admin123")

        tb.Button(container, text="🚀 Ingresar", bootstyle="primary", width=30, 
                  command=self.login).pack(pady=30)

    def login(self):
        u, p = self.user_ent.get(), self.pass_ent.get()
        try:
            with sqlite3.connect(PATH_DB_SQLITE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT TIPO_PERMISO_ACCES, ESTADO FROM CREDENCIALES WHERE USUARIO=? AND PASSWORD=?", (u, p))
                datos = cursor.fetchone()
            
            if datos:
                rol, estado = datos
                if estado == 1:
                    self.withdraw()
                    AppPrincipal(rol)
                else:
                    Messagebox.show_error("Usuario deshabilitado.", "Acceso Denegado")
            else:
                Messagebox.show_error("Credenciales incorrectas.", "Error")
        except Exception as e:
            Messagebox.show_error(f"Error base de datos: {e}")

if __name__ == "__main__":
    app = VentanaLogin()
    app.mainloop()
