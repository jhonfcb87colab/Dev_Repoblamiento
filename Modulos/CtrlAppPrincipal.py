import ttkbootstrap as tb
from concurrent.futures import ProcessPoolExecutor
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from CtrlVentanaFechas import VentanaFechas



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




