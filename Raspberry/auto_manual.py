import ui_components as ui
import assets as ast
import focus as fc
import serial_reader as sr
btns_manual_automatico = {}
combo_manual_automatico = {}
etiquetas_manual_automatico = {}
text_manual_automatico = {}
text_manual_automatico_ganancias = {}
frames = {}
var = {}
val_param = {
    "var_error" : 0,
    "var_flujo" : 0,
    "var_spo2" : 0
}
bool_params_gain = True
lim = None

bool_modo_manual = False
bool_visual_manual = True
graf_spo2 = False

def configFrame_m_a(app,_h):
    global grafica
    
    frames["frame_auto_manual"] = ui.crear_frame(app,"white")
    frames["subframe_grafica"] = ui.crear_subframe(frames["frame_auto_manual"],525,300,"black",0.65,0.45)
    grafica=ui.crear_grafica_linea(frames["subframe_grafica"],relx=0.5, rely=0.45,xlabel="s",ylabel="lpm",x_lim=(0,1000),y_lim=(0,15))
    w = 200
    h = 300
    frames["subframe_parametros"] = ui.crear_subframe(frames["frame_auto_manual"],w,h,"black",0.15,0.45)
    frames["subframe_ganancias"] = ui.crear_subframe(frames["frame_auto_manual"],w,h,"black",0.15,0.45)

    y_init = 0.08
    y_separacion = 0.14
    delta_y = 0.11
    tamano = 20
    w = 70
    h = 8
    var["var_error"] = ui.crear_stringvar(frames["subframe_grafica"])
    var["var_flujo"] = ui.crear_stringvar(frames["subframe_grafica"])
    var["var_spo2"] = ui.crear_stringvar(frames["subframe_grafica"])
    
    var["var_kp"] = ui.crear_stringvar(frames["subframe_grafica"])
    var["var_kd"] = ui.crear_stringvar(frames["subframe_grafica"])
    var["var_ki"] = ui.crear_stringvar(frames["subframe_grafica"])

    var["var_metrica"] = ui.crear_stringvar(frames["subframe_grafica"])
    var["var_rango"] = ui.crear_stringvar(frames["subframe_grafica"])
    var["var_toogle"] = ui.crear_stringvar(valor_inicial="Ganancias")

    etiquetas_manual_automatico["etiqueta_referencia"] = ui.crear_etiqueta(frames["subframe_parametros"],tamano,"Referencia (%)",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico["referencia"] = ui.crear_cuadro_texto(frames["subframe_parametros"],0.5,y_init,w,h,"85.0")
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_flujo"] = ui.crear_etiqueta(frames["subframe_parametros"],tamano,"Flujo (lpm)",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    etiquetas_manual_automatico["etiqueta_valor_flujo"] = ui.crear_etiqueta(frames["subframe_parametros"],20,variable=var["var_flujo"],x=0.5,y=y_init)
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_spo2"] = ui.crear_etiqueta(frames["subframe_parametros"],tamano,"SpO2 (%)",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    etiquetas_manual_automatico["etiqueta_valor_spo2"] = ui.crear_etiqueta(frames["subframe_parametros"],20,variable=var["var_spo2"],x=0.5,y=y_init)
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_error"] = ui.crear_etiqueta(frames["subframe_parametros"],tamano,"Error (%)",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    etiquetas_manual_automatico["etiqueta_valor_error"] = ui.crear_etiqueta(frames["subframe_parametros"],20,variable=var["var_error"],x=0.5,y=y_init)
    y_init = 0.08
    y_separacion = 0.2
    delta_y = 0.11
    etiquetas_manual_automatico["etiqueta_kp"] = ui.crear_etiqueta(frames["subframe_ganancias"],tamano,"Ganancia Kp",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico_ganancias["kp"] = ui.crear_cuadro_texto(frames["subframe_ganancias"],0.5,y_init,w,h,"0")
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_ki"] = ui.crear_etiqueta(frames["subframe_ganancias"],tamano,"Ganancia Ki",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico_ganancias["ki"] = ui.crear_cuadro_texto(frames["subframe_ganancias"],0.5,y_init,w,h,"0")
    y_init = y_init + y_separacion
    etiquetas_manual_automatico["etiqueta_kd"] = ui.crear_etiqueta(frames["subframe_ganancias"],tamano,"Ganancia Kd",x=0.5, y=y_init,fuente = "bold")
    y_init = y_init + delta_y
    text_manual_automatico_ganancias["kd"] = ui.crear_cuadro_texto(frames["subframe_ganancias"],0.5,y_init,w,h,"0")

    combo_manual_automatico["combo_variable"] = ui.crear_combobox(frames["subframe_grafica"],["Flujo","SpO2"],_h["h_cambio_variable"],0.2,0.92,variable=var["var_metrica"])
    combo_manual_automatico["combo_rango"] = ui.crear_combobox(frames["subframe_grafica"],["1 min","2 min","5 min","8 min","15 min"],_h["h_set_x"],0.8,0.92,variable=var["var_rango"])
    btns_manual_automatico["btn_toggle"] = ui.crear_boton(frames["frame_auto_manual"],"Ganancias",150,60,0.555,0.86,_h["h_mostrar_params_gain"])
    btns_manual_automatico["btn_envio"] = ui.crear_boton(frames["frame_auto_manual"],"Actualizar control",150,60,0.353,0.86,_h["h_send_control"])
    
    for b in btns_manual_automatico.values():
        ui.personalizar_widget(b,ast.estilos_boton["estilo_default"]) 


#====== APOYO ======
def send_control():
    dic = {
        "ganancias":{
            "kp": text_manual_automatico_ganancias["kp"].get("1.0", "end").strip(),
            "ki": text_manual_automatico_ganancias["ki"].get("1.0", "end").strip(),
            "kd": text_manual_automatico_ganancias["kd"].get("1.0", "end").strip(),
        }
    }
    if bool_modo_manual:
        referencias = {"referencias":{
            "Flujo":text_manual_automatico["referencia"].get("1.0", "end").strip(),
            "spo2":None
        }}
    else:
        referencias = {"referencias":{
            "spo2":text_manual_automatico["referencia"].get("1.0", "end").strip(),
            "Flujo":None
        }}
    dic["referencias"] = referencias["referencias"]

    sr.enviar_comando("control", dic)
    #print(dic)
def mod_label_ref():
    if bool_modo_manual:
        etiquetas_manual_automatico["etiqueta_referencia"].configure(text="Referencia (lpm)")
        lim = (0,15,0)
    else:
        etiquetas_manual_automatico["etiqueta_referencia"].configure(text="Referencia (%)")
        lim = (85,100,85)
#====== APOYO ======

#====== HANDLERS ======
def mostrar_auto_manual(manual = False):
    global bool_modo_manual
    global lim
    lim = (0,0,0)
    bool_modo_manual = manual
    fc.focus_clear()
    mod_label_ref()
    ui.mostrar_frame(frames["frame_auto_manual"])

    mostrar_params_gain(False)
    ui.mostrar_objeto(ast.assets_get_auto_manual(manual))
    temp = {}
    
    temp.update(btns_manual_automatico)
    temp.update(ast.botones)
    temp.update(combo_manual_automatico)
    fc.focus_set(temp)

def mostrar_params_gain(toggle = True):
    global bool_params_gain
    if toggle:
        bool_params_gain = not bool_params_gain
    if bool_params_gain:
        ui.btn_actualizar_texto(btns_manual_automatico["btn_toggle"],"Ganancias")
        ui.mostrar_frame(frames["subframe_ganancias"])
        fc.focus_remove(text_manual_automatico)
        fc.focus_set(text_manual_automatico_ganancias)
        fc.focus_set_limites((0,1,0))
    else:
        ui.btn_actualizar_texto(btns_manual_automatico["btn_toggle"],"Parametros")
        ui.mostrar_frame(frames["subframe_parametros"])
        fc.focus_remove(text_manual_automatico_ganancias)
        fc.focus_set(text_manual_automatico)
        fc.focus_set_limites(lim)

def cambio_variable(value):
    global graf_spo2
    global spo2
    global flujo
    global y
    y.clear()
    if value == "SpO2":
        flujo.clear()
        graf_spo2 = True
        ui.mod_grafica(grafica, ylim = (0,100),legend = "%")
    else:
        spo2.clear()
        ui.mod_grafica(grafica,ylim = (0,15),legend = "lpm")
        graf_spo2 = False
def set_x(value):
    data = value.strip()
    data = data.split()
    data = float(data[0]) * 1000
    ui.mod_grafica(grafica,xlim = (0,data))
    
y = []
spo2 = []
flujo = []
def data_flujo(payload):
    flujo.append(payload)
    add_punto()
def data_spo2(payload):
    spo2.append(payload)
    add_punto()
def add_punto():
    global y
    if graf_spo2:
        y = spo2
    else:
        y  = flujo
    limx_min, limx_max = grafica["ax"].get_xlim()
    if len(y) > limx_max:
        y.pop(0)
   # y.append(payload)
    xvalue=list(range(len(y)))
    grafica["line"].set_data(xvalue,y)
    grafica["canvas"].draw_idle()
    
#====== HANDLERS ======
