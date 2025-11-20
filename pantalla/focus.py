import ui_components as ui
import assets as ast
import tkinter as tk
import customtkinter as ctk
import alarmas as al

estilo_default        = ast.estilos_boton["estilo_default"]
estilo_seleccionado   = ast.estilos_boton["estilo_seleccionado"]
estilo_onoff     = ast.estilos_boton["on_off"]       

btns_focus = {}
indice = 0
BTN_ONOFF = None
is_text = False
widget = None
claves = None
bloqueo = False
limites = None


def focus_init():
    global BTN_ONOFF
    BTN_ONOFF = ast.botones["btn_onOff"]

def focus_set(btns):
    #btns_focus.clear()
    btns_focus.update(btns)
    for b in btns_focus.values():
        habilitar_focus(b)
    
def focus_remove(btns):
    for k in btns:
        btns_focus.pop(k, None)
def focus_set_limites(lim = (0,1,1)):
    global limites
    limites = lim
def focus_clear():
    global indice
    indice = 0
    btns_focus.clear()
def aplicar_focus_visual(event):
    w = _get_ctkbutton_from_widget(event.widget)        
    #print("FOCUS EN:", w, type(w))
    ui.personalizar_widget(w, estilo_seleccionado)
def quitar_focus_visual(event):
    w = _get_ctkbutton_from_widget(event.widget)
    #print("FOCUS EN:", w, type(w))
    if w is BTN_ONOFF:
        ui.personalizar_widget(w, ast.estilos_boton["on_off"])
        
    else:
        ui.personalizar_widget(w, estilo_default)

def habilitar_focus(widget):
    widget.bind("<FocusIn>", aplicar_focus_visual)
    widget.bind("<FocusOut>", quitar_focus_visual)

def _get_ctkbutton_from_widget(widget):
    w = widget
    while w is not None:
        if isinstance(w, ctk.CTkButton):
            return w
        w = getattr(w, "master", None)  # subir un nivel
    return widget

def navegar_focus(cmd):

    focus_actualizar()

    focus_desplazamiento(cmd)

    if isinstance(widget, ctk.CTkButton):
        focus_btn(cmd)
    elif isinstance(widget, ctk.CTkComboBox):
        focus_combo(cmd)
    elif isinstance(widget, ctk.CTkTextbox):
        focus_text(cmd)


def focus_btn(cmd):
    if cmd == "enter":
        widget.invoke()
def focus_combo(cmd):
    global bloqueo
    if cmd == "enter":
        bloqueo = not bloqueo
        #print("se bloqueo")
    if bloqueo:
        if cmd == "arriba":
            ui.combo_box_navegar(widget,"arriba")
        elif cmd == "abajo":
            ui.combo_box_navegar(widget,"abajo")
def focus_text(cmd):
    global bloqueo
    if cmd == "enter":
        bloqueo = not bloqueo
    if bloqueo:
        if cmd == "arriba":
            if al.verificar_dic(widget):
                al.mod_text(widget,True)
            else:
                ui.modificar_text_box(widget,limites,True)
        elif cmd == "abajo":
            if al.verificar_dic(widget):
                al.mod_text(widget,False)
            else:
                ui.modificar_text_box(widget,limites,False)

def focus_actualizar():
    global indice
    global widget
    global claves
    claves = list(btns_focus.keys()) 
    clave_actual = claves[indice]
    widget = btns_focus[clave_actual]

def focus_desplazamiento(cmd):
    global indice
    if not bloqueo:
        if cmd == "arriba":
            indice = (indice + 1) % len(claves)
            focus_actualizar() 
        elif cmd == "abajo":
            indice = (indice - 1) % len(claves)
            focus_actualizar() 
        ui.enfocar(widget)
