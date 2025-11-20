import ui_components as ui
import serial_reader as sr
data_imagenes = {
    "logo":   ui.cargar_imagen("IMGS/logo.png",     180, 40),
    "flecha": ui.cargar_imagen("IMGS/flecha2.png",   40, 20),
    "auto":   ui.cargar_imagen("IMGS/AUTO.png",      40, 40),
    "manual": ui.cargar_imagen("IMGS/MANUAL.png",    40, 40),
    "gears":  ui.cargar_imagen("IMGS/gears.png",     40, 40),
    "home":   ui.cargar_imagen("IMGS/home.png",      40, 40)
}

estilos_boton = {
    "on": {
        "text" : "ON",
        "fg_color": "#2ECC71",      # Verde encendido
        "hover_color": "#2ECC71",
        "text_color": "white",
        "border_color": "#1E8449",
        "border_width": 2
    },
    "off": {
        "text" : "OFF",
        "fg_color": "#E74C3C",      # Rojo apagado
        "hover_color": "#E74C3C",
        "text_color": "white",
        "border_color": "#922B21",
        "border_width": 2
    },
    "on_off":{
        "text" : "OFF",
        "fg_color": "#E74C3C",      # Rojo apagado
        "hover_color": "#E74C3C",
        "text_color": "white",
        "border_color": "#922B21",
        "border_width": 2
    },
    "estilo_seleccionado" : {
    "fg_color": "#5DADE2",       # Azul claro profesional
    "hover_color": "#5DADE2",
    "text_color": "white",
    "border_color": "#2E86C1",
    "border_width": 2,
    "corner_radius": 10
    },
    "estilo_default" : {
    "fg_color": "blue",
    "hover_color": "blue",
    "text_color": "white",
    "border_color": "#C8C8C8",
    "border_width": 1,
    "corner_radius": 8
    }
}

bool_on_off = False

botones = {}
etiquetas = {}
imagenes = {}

def init_controles_generales(app,handlers):
    global botones,etiquetas,imagenes
    botones = {
    "btn_onOff": ui.crear_boton(app,"OFF",150,60,0.75,0.86,handlers["h_on_off"],color="red"),
    "btn_regresar" : ui.crear_boton(app,"Regresar",150,60,0.15,0.86,handlers["h_principal"],img=data_imagenes["flecha"],compound_bottom=1)
    }

    etiquetas = {
        "etiqueta_sivora" : ui.crear_etiqueta(app,30,"SIVORA",0.9,0.08,"bold",fondo="white") 
    }

    imagenes = {
        "auto": ui.colocar_imagen(app,data_imagenes["auto"],0.95,0.9),
        "manual" : ui.colocar_imagen(app,data_imagenes["manual"],0.95,0.9),
        "logo" : ui.colocar_imagen(app,data_imagenes["logo"],0.14,0.08),
        "gears" : ui.colocar_imagen(app,data_imagenes["gears"],0.14,0.08)
    }
    for b in botones.values():
        if b is not botones["btn_onOff"]:
            ui.personalizar_widget(b,estilos_boton["estilo_default"])
        else:
            ui.personalizar_widget(b,estilos_boton["off"])
def assets_get_principal():
    return botones["btn_onOff"],*etiquetas.values(),imagenes["logo"]
def assets_get_auto_manual(manual = False):
    if manual:
        imagen = imagenes["manual"]
    else: 
        imagen = imagenes["auto"]
    return *botones.values(),*etiquetas.values(),imagen,imagenes["logo"]
def assets_get_alarmas():
    return *botones.values(),*etiquetas.values(),imagenes["gears"],imagenes["logo"]
def toggle_on_off():
    global bool_on_off
    global estilos_boton
    bool_on_off = not bool_on_off
    if bool_on_off:
        estilos_boton["on_off"] = estilos_boton["on"]
    else:
        estilos_boton["on_off"] = estilos_boton["off"]
    ui.personalizar_widget(botones["btn_onOff"],estilos_boton["on_off"])

    