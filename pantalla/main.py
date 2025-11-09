# main.py
import customtkinter as ctk
import tkinter as tk
import ui_components as ui
import serial_reader as sr 


# ============================================================
# FUNCIONES
# ============================================================

""" def toogleLed():
    global led
    led = not led
    strV_led.set("ledOn" if led else "ledOff")
    sr.enviar_comando({"led":"on"})
 """
def mostrar_pantalla(frame_destino,icono_extra=0):
    global var_etiqueta
    TODOS = [frame_principal, frame_alarmas, frame_auto_manual]
    # Iconos base comunes
    OVERLAYS = [etiqueta_sivora, btn_onOff]
    # Si se pasa un ícono extra, lo agrega
    if frame_destino is frame_auto_manual:
        if icono_extra == 1:
            OVERLAYS.append(imauto)
            var_etiqueta.set("SpO2:")
        else:
            OVERLAYS.append(immanual)
            var_etiqueta.set("flujo:")
        OVERLAYS.append(btn_regresar)
    elif frame_destino is frame_alarmas:
        OVERLAYS.append(btn_regresar)
    ui.mostrar_frame(frame_destino, TODOS, OVERLAYS)
      
def onoff():
    None
def usar_frames(excepto=None):
    todos = [frame_principal, frame_auto_manual, frame_alarmas]
    if excepto is None:
        return todos
    return [f for f in todos if f not in excepto]
def cambio_metrica(value):
    var_metrica.set(value)
    None

# ============================================================
# FUNCIONES
# ============================================================

# ============================================================
# CONFIGURACIÓN DE APP
# ============================================================

"""configuraciones de app  """
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
app.attributes('-fullscreen', True)
app.bind("<Escape>", lambda e: app.destroy())
"""configuraciones de app  """

imlogo = ui.cargar_imagen('IMGS/logo.png',180,40)
imflecha = ui.cargar_imagen('IMGS/flecha2.png',40,20)
imauto = ui.cargar_imagen('IMGS/AUTO.png',40,40)
immanual = ui.cargar_imagen('IMGS/MANUAL.png',40,40)
imgears = ui.cargar_imagen('IMGS/gears.png',40,40)
imhome = ui.cargar_imagen('IMGS/home.png',40,40)

# ============================================================
# CONFIGURACIÓN DE APP
# ============================================================

sr.iniciar_lector_serial(app)

# ============================================================
# CONFIGURACIÓN DE FRAMES/SUBFRAMES
# ============================================================

""" DECLARACION FRAMES """
frame_principal = ui.crear_frame(app,"white")
frame_alarmas = ui.crear_frame(app,"white")
frame_auto_manual = ui.crear_frame(app,"white")

subframe_modos = ui.crear_subframe(frame_principal,400,150,"black",0.33,0.8)
subframe_grafica = ui.crear_subframe(frame_auto_manual,525,300,"black",0.65,0.48)
subframe_variable_numerico = ui.crear_subframe(frame_auto_manual,200,300,"black",0.15,0.48)
""" DECLARACION FRAMES """

var_etiqueta = ui.crear_stringvar(subframe_grafica)
var_variable = ui.crear_stringvar(subframe_grafica,"-.-")
var_metrica = ui.crear_stringvar(subframe_grafica,"sin valor")

""" FRAME PRINCIPAL """
def configFrame_p():
    text_nombre = 'Sistema demostrativo de control\nautomático en oxigenoterapia'
    text_modRangos = "Modificar \nrangos"
    text_controlSpo2 = "Control por\nSpO2"
    text_controlFlujo = "Control por\nflujo"
    text_modos = "Modos de control"
    etiqueta_nombre = ui.crear_etiqueta(frame_principal,tamano = 30,texto=text_nombre,y=0.4)
    etiqueta_modos = ui.crear_etiqueta(subframe_modos,tamano=20,texto=text_modos,x=0.5,y=0.2)
    ui.colocar_imagen(frame_principal,imhome,0.95,0.9)
    ui.colocar_imagen(frame_principal,imlogo,0.14,0.1) 
    ui.crear_boton(frame_principal,text_modRangos,150,60,0.75,0.72,mostrar_pantalla,frame_alarmas)
    ui.crear_boton(subframe_modos,text_controlSpo2,150,60,0.25,0.7,mostrar_pantalla,(frame_auto_manual,1))
    ui.crear_boton(subframe_modos,text_controlFlujo,150,60,0.75,0.7,mostrar_pantalla,(frame_auto_manual,0))
configFrame_p()
""" FRAME PRINCIPAL """

""" FRAME ALARMAS """
ui.colocar_imagen(app,imgears,0.95,0.9)
""" FRAME ALARMAS """

""" FRAME MANUAL/AUTOMATICO """
def configFrame_m_a():
    ui.crear_etiqueta(subframe_variable_numerico,20,
        variable=var_etiqueta,x=0.5, y=0.8)
    ui.crear_etiqueta(subframe_variable_numerico,20,
        variable=var_variable,x=0.5,y=0.9)
    ui.crear_combobox(subframe_grafica,["Flujo","SpO2"],
        cambio_metrica,0.5,0.1,variable=var_metrica)



""" """ """ NOS QUEDAMOS EN VER LOS ARGUMENTOS DE LA 
FUNCION QUE DETONA EL COMBO BOX
 """
 """

 
 """    """ 
    cb_flujo = comboBox(
                        subframe_grafica_manual,
                        ["Flujo", "SpO2"],
                        on_cambio_metrica,
                        0.5, 0.1,
                        variable=metrica_var,
                        inicial="SpO2"
    )
    """
configFrame_m_a()
""" FRAME MANUAL/AUTOMATICO """



""" FRAME GENERAL """
etiqueta_sivora= ui.crear_etiqueta(app,30,"SIVORA",0.9,0.1,"bold",fondo="white")
btn_onOff = ui.crear_boton(app,"OFF",150,60,0.75,0.86,onoff,color="red")
btn_regresar = ui.crear_boton(app,"Regresar",150,60,0.15,0.86,mostrar_pantalla,frame_principal,img=imflecha,compound_bottom=1)
imauto=ui.colocar_imagen(app,imauto,0.95,0.9)
immanual=ui.colocar_imagen(app,immanual,0.95,0.9)
""" FRAME GENERAL """
# ============================================================
# CONFIGURACIÓN DE FRAMES/SUBFRAMES
# ============================================================

mostrar_pantalla(frame_principal)
app.mainloop()