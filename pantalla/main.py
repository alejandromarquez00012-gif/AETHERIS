import principal as pp
import ui_components as ui
import customtkinter as ctk
import tkinter as tk
import assets as ast
import focus as fc
import serial_reader as sr
import auto_manual as am
import alarmas as al
import queue

#====== HANDLERS ====== 
def mostrar_ctrl_spo2():
    am.mostrar_auto_manual(False)
def mostrar_ctrl_flujo():
    am.mostrar_auto_manual(True)
def mostrar_mod_rangos():
    al.mostrar_alarmas()
def mostrar_principal():
    pp.mostrar_principal()
def cambio_variable(value):
    am.cambio_variable(value)
    #print(value)
def set_x(value):
    am.set_x(value)
    #print(value)
def mostrar_params_gain():
    am.mostrar_params_gain()
#====== HANDLERS ======

#====== HANDLERS TX ======
def send_on_off():
    ast.toggle_on_off()
    sr.enviar_comando("sistema")
def send_control():
    am.send_control()
def send_limites():
    None
#====== HANDLERS TX ======

#====== HANDLERS RX ======
def navegar_focus(payload):
    fc.navegar_focus(payload)
def toggle_sistema(payload):
    send_on_off()
#====== HANDLERS RX ======


handlers ={
            "h_spo2":mostrar_ctrl_spo2,
            "h_flujo":mostrar_ctrl_flujo,
            "h_mod_rangos":mostrar_mod_rangos,
            "h_principal":mostrar_principal,
            "h_on_off":send_on_off,
            "h_cambio_variable":cambio_variable,
            "h_set_x":set_x,
            "h_mostrar_params_gain":mostrar_params_gain,
            "h_send_control":send_control,
            "h_mandar_limites":send_limites
}
handlers_rx = {
            "focus":navegar_focus,
            "sistema":toggle_sistema
}
"""configuraciones de app  """
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.attributes('-fullscreen', True)
app.bind("<Escape>", lambda e: app.destroy())
"""configuraciones de app  """

"""configuraciones de SR  """
colas = sr.iniciar_lector_serial(app,handlers = handlers_rx)
"""configuraciones de SR  """

cola_flujo = colas["flujo"]
cola_spo2 = colas["spo2"]

def procesar_cola_flujo():
    try:
        while True:
            payload = cola_flujo.get_nowait()
            if payload is not None:
                am.data_flujo(payload)
    except queue.Empty:
        pass

    # Volver a llamar esta función en 30 ms
    app.after(10, procesar_cola_flujo)
def procesar_cola_spo2():
    try:
        while True:
            payload = cola_spo2.get_nowait()
            if payload is not None:
                am.data_spo2(payload)
    except queue.Empty:
        pass

    # Volver a llamar esta función en 30 ms
    app.after(10, procesar_cola_spo2)

pp.configFrame_p(app,handlers)
ast.init_controles_generales(app,handlers)
am.configFrame_m_a(app,handlers)
al.config_frame_alarmas(app,handlers)
fc.focus_init()

procesar_cola_flujo()
procesar_cola_spo2()
pp.mostrar_principal()
app.mainloop()


