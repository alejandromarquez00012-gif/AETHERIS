import ui_components as ui
import assets as ast
import focus as fc

btns_alarmas = {}
text_alarmas = {
    "sup":{},
    "inf":{}
}
etiquetas_alarmas = {}
frames = {}
var = {
    "aceptable":98,
    "regular":95,
    "bajo":93,
    "riesgo":88,
    "min":85
}

def config_frame_alarmas(app,_h):
    frames["frame_alarmas"] = ui.crear_frame(app,"white")
    frames["subframe_limites"] = ui.crear_subframe(frames["frame_alarmas"],650,300,"black",0.5,0.47)
    #ui.colocar_imagen(app,imgears,0.95,0.9)
    etiquetas_alarmas["aceptable"] = ui.crear_etiqueta(frames["subframe_limites"],20, "Aceptable", x=0.2, y=0.26, fondo="blue",color_texto="white", ancho=120, alto=40,fuente="bold")
    etiquetas_alarmas["regular"] = ui.crear_etiqueta(frames["subframe_limites"],20, "Regular", x=0.2, y=0.46, fondo="green",color_texto="white", ancho=120, alto=40,fuente="bold")
    etiquetas_alarmas["bajo"] = ui.crear_etiqueta(frames["subframe_limites"],20, "Bajo", x=0.2, y=0.66, fondo="#DAA520",color_texto="white", ancho=120, alto=40,fuente="bold")
    etiquetas_alarmas["riesgo"] = ui.crear_etiqueta(frames["subframe_limites"],20, "En riesgo", x=0.2, y=0.86, fondo="red",color_texto="white", ancho=120, alto=40,fuente="bold")
    etiquetas_alarmas["limite_sup"] = ui.crear_etiqueta(frames["subframe_limites"],20, "Límite superior (%)", x=0.45, y=0.12)
    etiquetas_alarmas["limite_inf"] = ui.crear_etiqueta(frames["subframe_limites"],20, "Límite inferior (%)", x=0.75, y=0.12)

    w = 90
    h = 25

    text_alarmas["sup"]["aceptable"] = ui.crear_cuadro_texto(frames["subframe_limites"], 0.45, 0.26, w, h, valor_inicial="100")
    text_alarmas["sup"]["regular"]   = ui.crear_cuadro_texto(frames["subframe_limites"], 0.45, 0.46, w, h, valor_inicial="94.9")
    text_alarmas["sup"]["bajo"]      = ui.crear_cuadro_texto(frames["subframe_limites"], 0.45, 0.66, w, h, valor_inicial="89.9")
    text_alarmas["sup"]["riesgo"]    = ui.crear_cuadro_texto(frames["subframe_limites"], 0.45, 0.86, w, h, valor_inicial="86.7")

    text_alarmas["inf"]["aceptable"] = ui.crear_cuadro_texto(frames["subframe_limites"], 0.75, 0.26, w, h, valor_inicial="95")
    text_alarmas["inf"]["regular"]   = ui.crear_cuadro_texto(frames["subframe_limites"], 0.75, 0.46, w, h, valor_inicial="90")
    text_alarmas["inf"]["bajo"]      = ui.crear_cuadro_texto(frames["subframe_limites"], 0.75, 0.66, w, h, valor_inicial="87")
    text_alarmas["inf"]["riesgo"]    = ui.crear_cuadro_texto(frames["subframe_limites"], 0.75, 0.86, w, h, valor_inicial="85")

    btns_alarmas["aplicar_cambio"] = ui.crear_boton(frames["frame_alarmas"], "Aplicar cambios", 150, 60, 0.5, 0.86, _h["h_mandar_limites"])
 
def mostrar_alarmas():
    fc.focus_clear()
    actualizar_text()
    #mod_label_ref(manual)
    ui.mostrar_frame(frames["frame_alarmas"])
    fc.focus_set_limites((85,100,85))
    #mostrar_params_gain()
    ui.mostrar_objeto(ast.assets_get_alarmas())
    temp = {}
    
    temp.update(btns_alarmas)
    temp.update(ast.botones)
    #temp.update(combo_alarmas)
    for grupo in ("sup", "inf"):
        for clave, widget in text_alarmas[grupo].items():
            temp[f"{grupo}_{clave}"] = widget
    fc.focus_set(temp)

def mod_text(widget,inc = False):
    texto = widget.get("1.0", "end").strip()  # quita saltos de línea / espacios
    try:
        valor = float(texto)
    except ValueError:
        # Si no hay número válido, iniciar en 85
        valor = 0

    if inc:
        # 3) Incrementar y limitar al máximo
        if valor < 100:
            valor += 0.1
    else:
        if valor > 80:
            valor -= 0.1
    valor = round(valor,1)
    sup,clave = obtener_clave_widget(widget)
    if sup:
        var[clave] = valor
    else:
        claves = list(text_alarmas["sup"].keys())
        i = claves.index(clave)
        clave_sig = claves[i + 1]
        var[clave_sig] = valor
    actualizar_text()
def actualizar_text():
    list_keys = list(var.keys())

    for k in range(len(list_keys)-1):
        clave = list_keys[k]
        clave_sig = list_keys[k+1]
        valor = var[clave]
        valor_sig = var[clave_sig]

        ui.set_text_box(text_alarmas["sup"][clave],valor)
        ui.set_text_box(text_alarmas["inf"][clave],valor_sig)

def obtener_clave_widget(widget):
    _clave = None
    sup = None
    for clave, w in text_alarmas["sup"].items():
        if w is widget:
            _clave = clave
            sup = True
    for clave, w in text_alarmas["inf"].items():
        if w is widget:
            _clave = clave
            sup = False
    return sup,_clave
def verificar_dic(widget):
    salida =False
    for clave, w in text_alarmas["sup"].items():
        if w is widget:
            salida = True
    for clave, w in text_alarmas["inf"].items():
        if w is widget:
            salida = True
    return salida
