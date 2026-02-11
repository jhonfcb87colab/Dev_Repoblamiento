import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import sqlite3
import warnings

# Intentamos la importación más compatible para Tableview
try:
    from ttkbootstrap.tableview import Tableview
except ImportError:
    try:
        from ttkbootstrap.widgets.tableview import Tableview
    except ImportError:
        # Si falla todo, usamos el Treeview estándar de bootstrap
        Tableview = None 

# Silenciar avisos innecesarios
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# CONFIGURACIÓN DE RUTA
PATH_DB = "C:/ARCHIVOS_DEV/Archivos_Py/PROY_INTERFACES_PY/Dev_Repoblamiento/Dataset/Credenciales.db"

# --- FUNCIONES DE BASE DE DATOS ---
def validar_usuario(user, password):
    try:
        with sqlite3.connect(PATH_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TIPO_PERMISO_ACCES, ESTADO 
                FROM CREDENCIALES 
                WHERE USUARIO = ? AND PASSWORD = ?
            """, (user, password))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# --- VISTA: GESTIÓN DE USUARIOS (ADMIN) ---
class PanelAdmin(tb.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Usuarios - BI")
        self.geometry("900x550")
        self.grab_set()

        container = tb.Frame(self, padding=20)
        container.pack(fill=BOTH, expand=True)

        tb.Label(container, text="ADMINISTRACIÓN DE ACCESOS", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Configuración de columnas
        self.columnas = [
            {"text": "ID", "stretch": False},
            {"text": "Usuario", "stretch": True},
            {"text": "Rol", "stretch": True},
            {"text": "Estado", "stretch": True},
            {"text": "Tipo", "stretch": True}
        ]

        # Crear tabla si la librería cargó correctamente
        if Tableview:
            self.dt = Tableview(master=container, coldata=self.columnas, rowdata=[], bootstyle="info", paginated=True)
            self.dt.pack(fill=BOTH, expand=True, pady=10)
        else:
            tb.Label(container, text="Error: No se pudo cargar el widget de tabla.", bootstyle="danger").pack()

        btns = tb.Frame(container)
        btns.pack(fill=X, pady=10)
        tb.Button(btns, text="🔄 Cambiar Estado (ON/OFF)", bootstyle=WARNING, command=self.alternar_estado).pack(side=LEFT, padx=5)
        tb.Button(btns, text="🔄 Refrescar", bootstyle=INFO, command=self.cargar_datos).pack(side=RIGHT, padx=5)

        self.cargar_datos()

    def cargar_datos(self):
        rows = []
        try:
            with sqlite3.connect(PATH_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ID, USUARIO, TIPO_PERMISO_ACCES, ESTADO, TIPO FROM CREDENCIALES")
                for f in cursor.fetchall():
                    est = "✅ ACTIVO" if f[3] == 1 else "❌ INACTIVO"
                    rows.append((f[0], f[1], f[2], est, f[4]))
            self.dt.build_table_data(self.columnas, rows)
        except: pass

    def alternar_estado(self):
        sel = self.dt.view.selection()
        if not sel: return
        vals = self.dt.view.item(sel[0], "values")
        nuevo = 0 if "ACTIVO" in vals[3] else 1
        with sqlite3.connect(PATH_DB) as conn:
            conn.execute("UPDATE CREDENCIALES SET ESTADO = ? WHERE ID = ?", (nuevo, vals[0]))
        self.cargar_datos()

# --- VISTA: APP PRINCIPAL ---
class AppPrincipal(tb.Toplevel):
    def __init__(self, rol):
        super().__init__()
        self.title("SISTEMA DE REPOBLAMIENTO - BI")
        self.geometry("700x500")
        
        tb.Label(self, text=f"PANEL DE CONTROL - {rol}", font=("Segoe UI", 18, "bold"), 
                 bootstyle="inverse-dark").pack(fill=X, pady=20, padx=20)

        if rol == "ADMINISTRADOR":
            tb.Button(self, text="🛡️ Gestionar Usuarios", bootstyle="warning-outline", 
                      command=PanelAdmin).pack(pady=10)

        tb.Label(self, text="Seleccione un proceso para iniciar:").pack(pady=20)
        # Aquí irían tus botones de SP_REPOBLAR...

# --- VISTA: LOGIN ---
class VentanaLogin(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Acceso BI")
        self.geometry("400x450")

        container = tb.Frame(self, padding=30)
        container.pack(expand=True)

        tb.Label(container, text="LOGIN BI", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        self.user_ent = tb.Entry(container, width=30)
        self.user_ent.pack(pady=10)
        self.user_ent.insert(0, "admin")

        self.pass_ent = tb.Entry(container, width=30, show="*")
        self.pass_ent.pack(pady=10)
        self.pass_ent.insert(0, "admin123")

        tb.Button(container, text="Entrar", bootstyle="primary", width=25, 
                  command=self.login).pack(pady=20)

    def login(self):
        u, p = self.user_ent.get(), self.pass_ent.get()
        datos = validar_usuario(u, p)
        
        if datos:
            rol, estado = datos
            if estado == 1:
                self.withdraw()
                AppPrincipal(rol)
            else:
                Messagebox.show_error("Usuario deshabilitado.", "Error")
        else:
            Messagebox.show_error("Credenciales incorrectas", "Error")

if __name__ == "__main__":
    app = VentanaLogin()
    app.mainloop()