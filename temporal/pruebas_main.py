import ttkbootstrap as tb
import warnings
import sqlite3
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from Conecction.ConnSQL import Conxion
from Modulos.CtrlLogin import VentanaLogin  
from Modulos.CtrlAppPrincipal import AppPrincipal

warnings.filterwarnings("ignore")
# Pool global de procesos
executor = ProcessPoolExecutor(max_workers=1)




if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)

    app = VentanaLogin.VentanaLogin()
    app.mainloop()
