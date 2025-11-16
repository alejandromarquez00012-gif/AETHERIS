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
    limx_min, limx_max = grafica["ax"].get_xlim()
    if len(y) > limx_max:
        y.pop(0)
    y.append(payload)
    xvalue=list(range(len(y)))
    grafica["line"].set_data(xvalue,y)
    grafica["canvas"].draw_idle()
indice = 1
btns_focus = {}
bool_mod_text = False
bool_combo = False

def focus(payload):
    global indice
    global bool_mod_text
    global bool_combo
    claves = list(btns_focus.keys()) 
    clave_actual = claves[indice]
    ui.aplicar_estilo_default(btns_focus[clave_actual],True)
    if payload == "enter":
        if clave_actual in text_alarmas or clave_actual in text_manual_automatico or clave_actual in text_manual_automatico_ganancias :
            bool_mod_text = not bool_mod_text
        elif clave_actual in combo_manual_automatico:
            bool_combo = not bool_combo
        else:
            btns_focus[clave_actual].invoke()
    else:
        limites = obtener_limites(clave_actual)
        if payload == "arriba":
            if bool_mod_text:
                ui.modificar_text_box(btns_focus[clave_actual],limites)
            elif bool_combo:
                ui.combo_box_navegar(btns_focus[clave_actual],"arriba")
            else:
                indice = (indice + 1) % len(claves)  
        elif payload == "abajo":
            if bool_mod_text:
                ui.modificar_text_box(btns_focus[clave_actual],limites,False)
            elif bool_combo:
                ui.combo_box_navegar(btns_focus[clave_actual],"abajo")
            else:
                indice = (indice - 1) % len(claves)
        
    clave_actual = claves[indice]
    ui.guardar_estilo(btns_focus[clave_actual])
    ui.aplicar_estilo_default(btns_focus[clave_actual],False)
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
    global y 
    y.clear()
    grafica["ax"].set_xlim(0,int(value))
    grafica["canvas"].draw_idle()
def mandar_limites():
    sr.enviar_comando({"gain":{"kp":1,"ki":1,"kd":1}})
    None
bool_toggle_param = True
# ============================================================
# HANDLERS
# ============================================================

# ============================================================
# FUNCIONES
# ============================================================
def toggle():
    global btns_manual_automatico
    global bool_toggle_param
    bool_toggle_param = not bool_toggle_param
    if bool_toggle_param:
        ui.mostrar_objeto(subframe_parametros)
        ui.btn_actualizar_texto(btns_manual_automatico["btn_toggle"],"Ganancias") 
        btns_focus.update(text_manual_automatico) 
        borrar_dic(btns_focus,text_manual_automatico_ganancias)
    else:
        ui.mostrar_objeto(subframe_ganancias)
        ui.btn_actualizar_texto(btns_manual_automatico["btn_toggle"],"Parametros")
        borrar_dic(btns_focus,text_manual_automatico)
        btns_focus.update(text_manual_automatico_ganancias)

def enviar_control():
    None

def obtener_limites(widget):
    # en base al control definir limites del text box
    limites = (0,0)
    if widget in text_manual_automatico_ganancias:
        limites = (0,1)
    else:
        limites = (85,95)
    return limites

def borrar_dic(dic,remove):
    for r in remove:
        dic.pop(r) 


def mostrar_pantalla(frame_destino, icono_extra=0):
    global ventana_actual
    global btns_focus
    global indice 
    global bool_toggle_param
    try:
        claves = list(btns_focus.keys()) 
        clave_actual = claves[indice]
        ui.aplicar_estilo_default(btns_focus[clave_actual],True)
    except:
        pass
    # Reiniciar foco
    indice = 0
    btns_focus.clear()

    TODOS = [frame_principal, frame_alarmas, frame_auto_manual]

    # OVERLAYS base (copia)
    overlays = [
        etiqueta_sivora,
        btns_grales["btn_onOff"],
        imlogo
    ]
    ui.reiniciar_estilo()

    # -----------------------------------
    #  PANTALLA AUTO / MANUAL
    # -----------------------------------
    if frame_destino is frame_auto_manual:

        # botones navegables
        btns_focus.update(btns_manual_automatico)
        btns_focus.update(btns_grales)
        btns_focus.update(combo_manual_automatico)
        btns_focus.update(text_manual_automatico)
        #btns_focus.update(text_manual_automatico_ganancias)
        # agregar botón regresar
        overlays.append(btns_grales["btn_regresar"])
        overlays.append(subframe_parametros)

        if icono_extra == 1:
            overlays.append(imauto)
        else:
            overlays.append(immanual)

    # -----------------------------------
    #  PANTALLA ALARMAS
    # -----------------------------------
    elif frame_destino is frame_alarmas:

        btns_focus.update(btns_alarmas)
        btns_focus.update(btns_grales)
        btns_focus.update(text_alarmas)
        overlays.append(btns_grales["btn_regresar"])

    # -----------------------------------
    #  PANTALLA PRINCIPAL u otras
    # -----------------------------------
    else:
        btns_focus.update(btns_principal)
        # agregar solo on/off a foco
        btns_focus["btn_onOff"] = btns_grales["btn_onOff"]

    # Mostrar frame
    ui.mostrar_frame(frame_destino, TODOS, overlays)

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
subframe_limites = ui.crear_subframe(frame_alarmas,650,300,"black",0.5,0.47)
w = 200
h = 300
subframe_parametros = ui.crear_subframe(frame_auto_manual,w,h,"black",0.15,0.48)
subframe_ganancias = ui.crear_subframe(frame_auto_manual,w,h,"black",0.15,0.48)
""" DECLARACION FRAMES """


""" DECLARACION VAR """
var = {}
def init_var():
    var["var_error"] = ui.crear_stringvar(subframe_grafica,"100")
    var["var_flujo"] = ui.crear_stringvar(subframe_grafica,"100")
    var["var_spo2"] = ui.crear_stringvar(subframe_grafica,"90")

    var["var_metrica"] = ui.crear_stringvar(subframe_grafica,"-")
    var["var_rango"] = ui.crear_stringvar(subframe_grafica,"-")
    var["var_toogle"] = ui.crear_stringvar(valor_inicial="Ganancias")
init_var()

""" DECLARACION VAR """


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

    w = 90
    h = 25

    text_alarmas["aceptable_ls"] = ui.crear_cuadro_texto(subframe_limites, 0.45, 0.26, w, h, valor_inicial="100")
    text_alarmas["regular_ls"]   = ui.crear_cuadro_texto(subframe_limites, 0.45, 0.46, w, h, valor_inicial="94.9")
    text_alarmas["bajo_ls"]      = ui.crear_cuadro_texto(subframe_limites, 0.45, 0.66, w, h, valor_inicial="89.9")
    text_alarmas["riesgo_ls"]    = ui.crear_cuadro_texto(subframe_limites, 0.45, 0.86, w, h, valor_inicial="86.7")

    text_alarmas["aceptable_li"] = ui.crear_cuadro_texto(subframe_limites, 0.75, 0.26, w, h, valor_inicial="95")
    text_alarmas["regular_li"]   = ui.crear_cuadro_texto(subframe_limites, 0.75, 0.46, w, h, valor_inicial="90")
    text_alarmas["bajo_li"]      = ui.crear_cuadro_texto(subframe_limites, 0.75, 0.66, w, h, valor_inicial="87")
    text_alarmas["riesgo_li"]    = ui.crear_cuadro_texto(subframe_limites, 0.75, 0.86, w, h, valor_inicial="15")

    btns_alarmas["aplicar_cambio"] = ui.crear_boton(frame_alarmas, "Aplicar cambios", 150, 60, 0.5, 0.86, mandar_limites)
    
config_Frame_alarmas()
""" FRAME ALARMAS """

""" FRAME MANUAL/AUTOMATICO """
btns_manual_automatico = {}
combo_manual_automatico = {}
etiquetas_manual_automatico = {}
text_manual_automatico = {}
text_manual_automatico_ganancias = {}
def configFrame_m_a():
    global grafica
    grafica=ui.crear_grafica_linea(subframe_grafica,xlabel="s",ylabel="%",x_lim=(0,20),y_lim=(0,15))

    y_init = 0.08
    y_separacion = 0.14
    delta_y = 0.11
    tamano = 20
    w = 70
    h = 8
    etiquetas_manual_automatico["etiqueta_referencia"] = ui.crear_etiqueta(subframe_parametros,tamano,"Referencia",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico["referencia"] = ui.crear_cuadro_texto(subframe_parametros,0.5,y_init,w,h,"85.0")
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_flujo"] = ui.crear_etiqueta(subframe_parametros,tamano,"Flujo",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    etiquetas_manual_automatico["etiqueta_valor_flujo"] = ui.crear_etiqueta(subframe_parametros,20,variable=var["var_flujo"],x=0.5,y=y_init)
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_spo2"] = ui.crear_etiqueta(subframe_parametros,tamano,"SpO2",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    etiquetas_manual_automatico["etiqueta_valor_spo2"] = ui.crear_etiqueta(subframe_parametros,20,variable=var["var_spo2"],x=0.5,y=y_init)
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_error"] = ui.crear_etiqueta(subframe_parametros,tamano,"Error",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    etiquetas_manual_automatico["etiqueta_valor_error"] = ui.crear_etiqueta(subframe_parametros,20,variable=var["var_error"],x=0.5,y=y_init)
    y_init = 0.08
    y_separacion = 0.2
    delta_y = 0.11
    etiquetas_manual_automatico["etiqueta_kp"] = ui.crear_etiqueta(subframe_ganancias,tamano,"Ganancia Kp",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico_ganancias["kp"] = ui.crear_cuadro_texto(subframe_ganancias,0.5,y_init,w,h,"0.0")
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_ki"] = ui.crear_etiqueta(subframe_ganancias,tamano,"Ganancia Ki",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico_ganancias["ki"] = ui.crear_cuadro_texto(subframe_ganancias,0.5,y_init,w,h,"0.0")
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_kd"] = ui.crear_etiqueta(subframe_ganancias,tamano,"Ganancia Kd",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico_ganancias["kd"] = ui.crear_cuadro_texto(subframe_ganancias,0.5,y_init,w,h,"0.0")

    combo_manual_automatico["combo_variable"] = ui.crear_combobox(subframe_grafica,["Flujo","SpO2"],cambio_variable,0.5,0.1,variable=var["var_metrica"])
    combo_manual_automatico["combo_rango"] = ui.crear_combobox(subframe_grafica,["10","20","30","40","50"],cambio_x,0.5,0.9,variable=var["var_rango"])
    btns_manual_automatico["btn_toggle"] = ui.crear_boton(frame_auto_manual,"Ganancias",150,60,0.555,0.86,toggle)
    btns_manual_automatico["btn_envio"] = ui.crear_boton(frame_auto_manual,"Actualizar control",150,60,0.353,0.86,enviar_control)
    
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
