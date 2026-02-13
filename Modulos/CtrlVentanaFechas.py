import ttkbootstrap as tb
from concurrent.futures import ProcessPoolExecutor
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from concurrent.futures import ProcessPoolExecutor
# from Conecction.SQL import ConexionSQL


# =====================================
# VENTANA FECHAS
# =====================================
executor = ProcessPoolExecutor(max_workers=1)

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

        # self.future = executor.submit(
        #     ConexionSQL.Conxion.ejecutar_sp,
        #     fi,
        #     ff,
        #     self.sp_destino
        # )

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




