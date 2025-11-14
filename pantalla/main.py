# main.py
import customtkinter as ctk
import tkinter as tk
import ui_components as ui
import serial_reader as sr 


# ============================================================
# HANDLERS
# ============================================================
y=[]
def agregarValor(payload):
    y.append(payload)
    xvalue=list(range(len(y)))
    grafica["line"].set_data(xvalue,y)
    grafica["canvas"].draw_idle()
indice = 1
btns_focus = {}
def focus(payload):
    global indice
    claves = list(btns_focus.keys()) 
    clave_actual = claves[indice]
    ui.btn_deseleccionar(btns_focus[clave_actual])
    if payload == "enter":
        btns_focus[clave_actual].invoke()
    else:
        if payload == "arriba":
            indice = (indice + 1) % len(claves)  
        elif payload == "abajo":
            indice = (indice - 1) % len(claves)
        
        clave_actual = claves[indice]
        ui.btn_seleccionar(btns_focus[clave_actual])

sistema = False
def handler_on_off(payload):
    onoff()
def onoff():
    global sistema
    sistema = not sistema
    ui.btn_toggle_onoff(btns_grales["btn_onOff"],sistema)
    if sistema: 
        sr.enviar_comando({"sistema":"on"})
    else:
        sr.enviar_comando({"sistema":"off"})

def cambio_variable(value):
    var_metrica.set(value)

def cambio_x(value):
    global grafica
    grafica["ax"].set_xlim(0,int(value))
    grafica["canvas"].draw_idle()
def mandar_limites():
    None
# ============================================================
# HANDLERS
# ============================================================

# ============================================================
# FUNCIONES
# ============================================================
    


def mostrar_pantalla(frame_destino,icono_extra=0):
    global var_etiqueta
    global ventana_actual
    global btns_focus
    global indice 
    indice = 1
    btns_focus.clear()
    
    TODOS = [frame_principal, frame_alarmas, frame_auto_manual]
    OVERLAYS = [etiqueta_sivora, btns_grales["btn_onOff"],imlogo,btns_grales["btn_regresar"]]
    if frame_destino is frame_auto_manual:
        btns_focus.update(btns_manual_automatico)
        btns_focus.update(btns_grales)
        if icono_extra == 1:
            OVERLAYS.append(imauto)
            var_etiqueta.set("SpO2:")
            
        else:
            OVERLAYS.append(immanual)
            var_etiqueta.set("flujo:")
    elif frame_destino is frame_alarmas:
        btns_focus.update(btns_alarmas)
        btns_focus.update(btns_grales)
    else:
        OVERLAYS.remove(btns_grales["btn_regresar"])
        btns_focus.update(btns_principal)
        btns_focus["btn_onOff"]=btns_grales["btn_onOff"]
    ui.mostrar_frame(frame_destino, TODOS, OVERLAYS)

def usar_frames(excepto=None):
    todos = [frame_principal, frame_auto_manual, frame_alarmas]
    if excepto is None:
        return todos
    return [f for f in todos if f not in excepto]
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

grafica=None
sr.iniciar_lector_serial(app,handlers={"focus":focus,"graf":agregarValor,"btn_on_off":handler_on_off})
# ============================================================
# CONFIGURACIÓN DE APP
# ============================================================


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
subframe_limites = ui.crear_subframe(frame_alarmas,650,300,"black",0.5,0.47)
""" DECLARACION FRAMES """

var_etiqueta = ui.crear_stringvar(subframe_grafica)
var_variable = ui.crear_stringvar(subframe_grafica,"-.-")
var_metrica = ui.crear_stringvar(subframe_grafica,"-")
var_rango = ui.crear_stringvar(subframe_grafica,"-")

""" FRAME PRINCIPAL """
btns_principal={}
def configFrame_p():
    text_nombre = 'Sistema demostrativo de control\nautomático en oxigenoterapia'
    text_modRangos = "Modificar \nrangos"
    text_controlSpo2 = "Control por\nSpO2"
    text_controlFlujo = "Control por\nflujo"
    text_modos = "Modos de control"
    etiqueta_nombre = ui.crear_etiqueta(frame_principal,tamano = 30,texto=text_nombre,y=0.4)
    etiqueta_modos = ui.crear_etiqueta(subframe_modos,tamano=20,texto=text_modos,x=0.5,y=0.2)
    ui.colocar_imagen(frame_principal,imhome,0.95,0.9)
    btns_principal["mod_rangos"] = ui.crear_boton(frame_principal,text_modRangos,150,60,0.75,0.72,mostrar_pantalla,frame_alarmas)
    btns_principal["ctrl_spo2"] = ui.crear_boton(subframe_modos,text_controlSpo2,150,60,0.25,0.7,mostrar_pantalla,(frame_auto_manual,1))
    btns_principal["ctrl_flujo"] = ui.crear_boton(subframe_modos,text_controlFlujo,150,60,0.75,0.7,mostrar_pantalla,(frame_auto_manual,0))
configFrame_p()
""" FRAME PRINCIPAL """

""" FRAME ALARMAS """
btns_alarmas = {}
etiquetas_alarmas = {}
text_alarmas = {}
def config_Frame_alarmas():
    ui.colocar_imagen(app,imgears,0.95,0.9)
    aceptable = ui.crear_etiqueta(subframe_limites,20, "Aceptable", x=0.2, y=0.26, fondo="blue",color_texto="white", ancho=120, alto=40,fuente="bold")
    regular = ui.crear_etiqueta(subframe_limites,20, "Regular", x=0.2, y=0.46, fondo="green",color_texto="white", ancho=120, alto=40,fuente="bold")
    bajo = ui.crear_etiqueta(subframe_limites,20, "Bajo", x=0.2, y=0.66, fondo="#DAA520",color_texto="white", ancho=120, alto=40,fuente="bold")
    riesgo = ui.crear_etiqueta(subframe_limites,20, "En riesgo", x=0.2, y=0.86, fondo="red",color_texto="white", ancho=120, alto=40,fuente="bold")
    limite_sup = ui.crear_etiqueta(subframe_limites,20, "Límite superior (%)", x=0.45, y=0.12)
    limite_inf = ui.crear_etiqueta(subframe_limites,20, "Límite inferior (%)", x=0.75, y=0.12)

    text_alarmas["aceptable_ls"] = ui.crear_cuadro_texto(subframe_limites,0.45,0.26,75,25,valor_inicial="100")
    text_alarmas["regular_ls"] = ui.crear_cuadro_texto(subframe_limites,0.45,0.46,75,25,valor_inicial="94.9")
    text_alarmas["bajo_ls"] = ui.crear_cuadro_texto(subframe_limites,0.45,0.66,75,25,valor_inicial="89.9")
    text_alarmas["riesgo_ls"] = ui.crear_cuadro_texto(subframe_limites,0.45,0.86,75,25,valor_inicial="86.7")

    text_alarmas["aceptable_li"] = ui.crear_cuadro_texto(subframe_limites,0.75,0.26,75,25,valor_inicial="95")
    text_alarmas["regular_li"] = ui.crear_cuadro_texto(subframe_limites,0.75,0.46,75,25,valor_inicial="90")
    text_alarmas["bajo_li"] = ui.crear_cuadro_texto(subframe_limites,0.75,0.66,75,25,valor_inicial="87")
    text_alarmas["riesgo_li"] = ui.crear_cuadro_texto(subframe_limites,0.75,0.86,75,25,valor_inicial="15")
    btns_alarmas["aplicar_cambio"] = ui.crear_boton(frame_alarmas,"Aplicar cambios",150,60,0.5,0.86,mandar_limites)
config_Frame_alarmas()
""" FRAME ALARMAS """

""" FRAME MANUAL/AUTOMATICO """
btns_manual_automatico = {}
def configFrame_m_a():
    global grafica
    ui.crear_etiqueta(subframe_variable_numerico,20,
        variable=var_etiqueta,x=0.5, y=0.8)
    ui.crear_etiqueta(subframe_variable_numerico,20,
        variable=var_variable,x=0.5,y=0.9)
    ui.crear_combobox(subframe_grafica,["Flujo","SpO2"],
        cambio_variable,0.5,0.1,variable=var_metrica)
    grafica=ui.crear_grafica_linea(subframe_grafica,
        xlabel="s",ylabel="%",x_lim=(0,20),y_lim=(0,15))
    ui.crear_combobox(subframe_grafica,["10","20","30","40","50"],
        cambio_x,0.5,0.9,variable=var_rango)
configFrame_m_a()
""" FRAME MANUAL/AUTOMATICO """



""" FRAME GENERAL """
btns_grales = {}
etiqueta_sivora= ui.crear_etiqueta(app,30,"SIVORA",0.9,0.1,"bold",fondo="white")
btns_grales["btn_onOff"] = ui.crear_boton(app,"OFF",150,60,0.75,0.86,onoff,color="red")
btns_grales["btn_regresar"] = ui.crear_boton(app,"Regresar",150,60,0.15,0.86,mostrar_pantalla,frame_principal,img=imflecha,compound_bottom=1)
imauto=ui.colocar_imagen(app,imauto,0.95,0.9)
immanual=ui.colocar_imagen(app,immanual,0.95,0.9)
imlogo=ui.colocar_imagen(app,imlogo,0.14,0.1) 
""" FRAME GENERAL """
# ============================================================
# CONFIGURACIÓN DE FRAMES/SUBFRAMES
# ============================================================

mostrar_pantalla(frame_principal)
app.mainloop()