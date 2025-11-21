import ui_components as ui
import assets as ast
import focus as fc

imagenes = ast.data_imagenes

btns_principal={}
frames = {}
asset = {}
def configFrame_p(app,handlers):
    global frames
    frames["frame_principal"] = ui.crear_frame(app,"white")
    frames["subframe_modos"] = ui.crear_subframe(frames["frame_principal"],400,150,"black",0.33,0.8)
    text_nombre = 'Sistema demostrativo de control\nautomático en oxigenoterapia'
    text_modRangos = "Modificar \nrangos"
    text_controlSpo2 = "Control por\nSpO2"
    text_controlFlujo = "Control por\nflujo"
    text_modos = "Modos de control"
    etiqueta_nombre = ui.crear_etiqueta(frames["frame_principal"],tamano = 30,texto=text_nombre,y=0.4)
    etiqueta_modos = ui.crear_etiqueta(frames["subframe_modos"],tamano=20,texto=text_modos,x=0.5,y=0.2)
    ui.colocar_imagen(frames["frame_principal"],imagenes["home"],0.95,0.9)
    btns_principal["mod_rangos"] = ui.crear_boton(frames["frame_principal"],text_modRangos,150,60,0.75,0.72,handlers["h_mod_rangos"])
    btns_principal["ctrl_spo2"] = ui.crear_boton(frames["subframe_modos"],text_controlSpo2,150,60,0.25,0.7,handlers["h_spo2"])
    btns_principal["ctrl_flujo"] = ui.crear_boton(frames["subframe_modos"],text_controlFlujo,150,60,0.75,0.7,handlers["h_flujo"])
    for b in btns_principal.values():
        ui.personalizar_widget(b,ast.estilos_boton["estilo_default"]) 

def mostrar_principal():
    fc.focus_clear()
    ui.mostrar_frame(frames["frame_principal"])
    ui.mostrar_objeto(ast.assets_get_principal())
    temp = {}
    temp.update(btns_principal)
    temp["btn_onOff"] = ast.botones["btn_onOff"]
    fc.focus_set(temp)
def enfocar(btn):
    ui.enfocar(btns_principal[btn])