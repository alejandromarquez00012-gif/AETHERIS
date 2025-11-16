import tkinter as tk
import customtkinter as ctk
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

formato_estandar = {}
# ============================================================
# GRAFICA
# ============================================================


def crear_grafica_linea(
    parent,
    relx=0.5, rely=0.5,
    width=520, height=210,
    titulo="",
    xlabel="",
    ylabel="",
    x_lim=None,
    y_lim=None,
    grid=True,
    linewidth=2
):
    """
    Crea una gráfica de línea de Matplotlib embebida en Tk/CTk.
    Coloca el canvas con place() y devuelve un dict con referencias útiles.

    return:
      {
        "fig": Figure,
        "ax": Axes,
        "line": Line2D,
        "canvas": FigureCanvasTkAgg,
        "widget": canvas_widget (para .place/.lift),
      }
    """
    fig = Figure(figsize=(width/100.0, height/100.0), dpi=100)
    ax = fig.add_subplot(111)
    ax.grid(grid)
    ax.set_title(titulo)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if y_lim is not None:
        ax.set_ylim(*y_lim)
    if x_lim is not None:
        ax.set_xlim(*x_lim)

    # Línea vacía inicial
    line, = ax.plot([], [], linewidth=linewidth)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    widget = canvas.get_tk_widget()
    widget.place(relx=relx, rely=rely, anchor=tk.CENTER, width=width, height=height)

    canvas.draw_idle()

    return {"fig": fig, "ax": ax, "line": line, "canvas": canvas, "widget": widget}


def actualizar_grafica_linea(refs, x_data, y_data, autoscale_x=True, autoscale_y=False, y_lim=None):
    """
    Actualiza los datos de la línea y redibuja.
    - refs: dict devuelto por crear_grafica_linea
    - x_data, y_data: listas/arrays con datos
    - autoscale_x/autoscale_y: si True, recalcula límites del eje
    - y_lim: si se indica, fija límites de Y (anula autoscale_y)
    """
    line = refs["line"]
    ax   = refs["ax"]
    cvs  = refs["canvas"]

    line.set_data(x_data, y_data)

    # Ajustes de límites
    if autoscale_x:
        if len(x_data) >= 1:
            ax.set_xlim(min(x_data), max(x_data))
        else:
            ax.set_xlim(0, 1)

    if y_lim is not None:
        ax.set_ylim(*y_lim)
    elif autoscale_y:
        ax.relim()
        ax.autoscale(axis='y')

    cvs.draw_idle()


def limpiar_grafica_linea(refs):
    """ Limpia la línea (deja sin datos) y refresca. """
    actualizar_grafica_linea(refs, [], [], autoscale_x=True, autoscale_y=True)

# ============================================================
# GRAFICA
# ============================================================

# ============================================================
# FRAMES / CONTENEDORES
# ============================================================
def crear_frame(root, fg=None):
    """
    Crea un frame de pantalla completa (usa place con relwidth/relheight = 1).
    root: CTk() o cualquier frame padre.
    fg: color de fondo.
    return: frame creado (CTkFrame)
    """
    frame_principal = ctk.CTkFrame(
        master=root,
        fg_color=fg
    )
    frame_principal.place(
        x=0,
        y=0,
        relwidth=1,
        relheight=1
    )
    return frame_principal

def crear_subframe(parent, w, h, border_color="black", relx=0.5, rely=0.5,
                   fg="white", corner_radius=10, border_width=1):
    """
    Crea un subframe tipo tarjeta con borde.
    parent: frame padre.
    w, h: ancho/alto en px.
    border_color: color del borde.
    relx, rely: posición relativa (0-1) dentro del parent.
    return: subframe creado (CTkFrame)
    """
    _subframe = ctk.CTkFrame(
        master=parent,
        width=w,
        height=h,
        fg_color=fg,
        corner_radius=corner_radius,
        border_width=border_width,
        border_color=border_color
    )
    _subframe.place(
        relx=relx,
        rely=rely,
        anchor=tk.CENTER
    )
    return _subframe

def mostrar_objeto(objeto):
    """
    Trae al frente uno o varios objetos (frames, labels, botones, etc.)
    usando lift().
    """
    if not isinstance(objeto, (list, tuple)):
        objeto = [objeto]

    for o in objeto:
        try:
            o.lift()
        except Exception:
            print(f"No se pudo hacer lift() de {o}")


def mostrar_frame(frame, todos, overlays=None):
    """
    Baja todos los frames en 'todos', levanta el frame indicado,
    y opcionalmente levanta los overlays.
    """
    for f in todos:
        f.lower()

    frame.lift()

    if overlays:
        mostrar_objeto(overlays)

# ============================================================
# ETIQUETAS / TEXTO
# ============================================================

def crear_etiqueta(
    parent,
    tamano=30,
    texto=None,
    x=0.5,
    y=0.5,
    fuente=None,
    variable=None,
    fondo=None,
    color_texto="black",
    ancho=None,
    alto=None,
    font_family="DejaVu Sans"
):
    """
    Crea y coloca una etiqueta (CTkLabel) en 'parent', en (relx=x, rely=y).
    Puede mostrar texto fijo ('texto') o una StringVar ('variable').

    return: label creado (CTkLabel)
    """
    if fuente is not None:
        configuracion_fuente = (font_family, tamano, fuente)
    else:
        configuracion_fuente = (font_family, tamano)

    args = {
        "master": parent,
        "font": configuracion_fuente,
        "text_color": color_texto,
        "justify": "center"
    }
    if fondo is not None:
        args["fg_color"] = fondo

    if variable is not None:
        args["textvariable"] = variable
    else:
        args["text"] = texto if texto is not None else ""

    if ancho is not None:
        args["width"] = ancho
    if alto is not None:
        args["height"] = alto

    etiqueta_creada = ctk.CTkLabel(**args)
    etiqueta_creada.place(relx=x, rely=y, anchor=tk.CENTER)
    return etiqueta_creada
# ============================================================
# IMÁGENES
# ============================================================
def cargar_imagen(ruta_local, size_x, size_y):
    """
    Carga una imagen desde ./IMGS/<ruta_local> y la devuelve
    envuelta en CTkImage (listo para usar en Label o Button).
    NO la coloca en pantalla todavía.
    """
    img_pil = Image.open( ruta_local)
    img_ctk = ctk.CTkImage(
        light_image=img_pil,
        dark_image=img_pil,
        size=(size_x, size_y)
    )
    return img_ctk
def colocar_imagen(parent, img_ctk, relx, rely):
    """
    Coloca una imagen (CTkImage ya creada) dentro de un frame usando un CTkLabel.
    return: label_imagen (por si quieres guardarlo)
    """
    lbl = ctk.CTkLabel(
        master=parent,
        image=img_ctk,
        text=""
    )
    lbl.place(relx=relx, rely=rely, anchor="center")
    return lbl

# ============================================================
# BOTONES
# ============================================================
def crear_boton(
    parent,
    texto,
    w,
    h,
    relx,
    rely,
    callback,
    callback_arg=None,     # <── acepta 0, 1 o muchos argumentos
    img=None,
    compound_bottom=False,
    font=("DejaVu Sans", 15, "bold"),
    color="blue"
):
    """
    Crea un botón CTkButton y lo ubica vía place().
    - callback: función a ejecutar al presionar el botón.
    - *callback_args: todos los argumentos que el callback necesite.
    """

     # Comando según el tipo del argumento
    if callback_arg is None:
        cmd = callback
    elif isinstance(callback_arg, (list, tuple)):
        cmd = lambda: callback(*callback_arg)  # desempaqueta varios args
    else:
        cmd = lambda: callback(callback_arg)   # un solo argumento

    kwargs = {
        "master": parent,
        "text": texto,
        "width": w,
        "height": h,
        "font": font,
        "fg_color":color,
        "command": cmd,
        "image": img
    }

    if compound_bottom:
        kwargs["compound"] = "bottom"

    boton_ = ctk.CTkButton(**kwargs)
    boton_.place(relx=relx, rely=rely, anchor=tk.CENTER)
    return boton_
def btn_toggle_onoff(btn,on):
    if on:
        texto = "ON"
        color = "green"
        hover = "green"
        tcolor = "white"
    else:
        texto = "OFF"
        color = "red"
        hover = "red"
        tcolor = "white"
       
    btn.configure(
                text=texto,
                fg_color=color,    
                hover_color=hover,
                text_color=tcolor
                )
def btn_actualizar_texto(btn,txt):
    btn.configure(text=txt)

# ============================================================
# COMBOBOX
# ============================================================

def crear_combobox(
    parent,
    values,
    evento_on_change,
    relx,
    rely,
    variable=None,
    valor_inicial=None
):
    """
    Crea un CTkComboBox con opciones 'values'.
    - evento_on_change(value) se dispara cada vez que cambia.
    - variable: StringVar externa (para que otras partes lean el valor)
    - valor_inicial: si se da, se usa como valor inicial del combo.
                     si no, usamos el primer 'values[0]' si existe.

    return: combobox creado (CTkComboBox)
    """
    combobox = ctk.CTkComboBox(
        master=parent,
        values=values,
        command=evento_on_change,
        variable=variable
    )
    if valor_inicial is not None:
        combobox.set(valor_inicial)
        if variable is not None:
            variable.set(valor_inicial)
    elif values:
        combobox.set(values[0])
        if variable is not None:
            variable.set(values[0])

    combobox.place(relx=relx, rely=rely, anchor=tk.CENTER)
    return combobox
def combo_box_navegar(combo, direccion):
    opciones = combo._values
    actual = combo.get()

    try:
        idx = opciones.index(actual)
    except ValueError:
        idx = 0

    if direccion == "arriba":
        idx = (idx - 1) % len(opciones)
    else:  # "abajo"
        idx = (idx + 1) % len(opciones)

    nuevo_valor = opciones[idx]
    combo.set(nuevo_valor)

    # Actualizar variable asociada, si existe
    if combo._variable is not None:
        combo._variable.set(nuevo_valor)

    if combo._command is not None:
        combo._command(nuevo_valor)
# ============================================================
# TEXTBOX
# ============================================================

def crear_cuadro_texto(
    parent,
    relx,
    rely,
    ancho_px,
    alto_px,
    valor_inicial="",
    font=("DejaVu Sans", 20),
    border_width=1,
    border_color="black"
):
    """
    Crea un CTkTextbox para límites / valores.
    return: textbox creado (CTkTextbox)
    """
    ct = ctk.CTkTextbox(
        master=parent,
        width=ancho_px,
        height=alto_px,
        border_width=border_width,
        border_color=border_color,
        font=font
    )
    ct.place(relx=relx, rely=rely, anchor=tk.CENTER)

    if valor_inicial != "":
        ct.insert("0.0", str(valor_inicial))

    return ct
def modificar_text_box(widget,limites,inc=True):
    # 1) Leer el contenido actual
    texto = widget.get("1.0", "end").strip()  # quita saltos de línea / espacios
    _min,_max = limites
    # 2) Convertir a entero, con manejo de errores
    try:
        valor = float(texto)
    except ValueError:
        # Si no hay número válido, iniciar en 85
        valor = 0.0

    if inc:
        # 3) Incrementar y limitar al máximo
        if valor < _max:
            valor += 0.1
    else:
        if valor > _min:
            valor -= 0.1

    valor = round(valor,1)
    # 4) Reemplazar el contenido del TextBox
    widget.delete("1.0", "end")
    widget.insert("1.0", str(valor))
def resaltar_text_box(widget,resaltar=False):
    None
# ============================================================
# STRINGVAR HELPERS
# ============================================================

def crear_stringvar(app=None, valor_inicial="--"):
    """
    Crea un tk.StringVar con valor inicial.
    Devuelve ese StringVar.
    """
    return tk.StringVar(master=app, value=valor_inicial)
def var_mod_texto(var,text):
    var.set(text)
# ============================================================
# BOTÓN ON/OFF (ESTADO VISUAL)
# ============================================================
estilo = {}
PROPIEDADES_SEGURO = [
    "fg_color",
    "border_color",
    "border_width",
    "text_color",
]
def aplicar_estilo_default(widget,aplicar = True):
    if aplicar and estilo:
        widget.configure(
            border_color = estilo["border_color"],   # azul cyan brillante
            border_width = estilo["border_width"],           # borde grueso
            fg_color     = estilo["fg_color"],   # fondo ligeramente más claro
            text_color   = estilo["text_color"]      # texto visible
        )
    elif not aplicar:
        widget.configure(
            border_color = "black",   # azul cyan brillante
            border_width = 3,           # borde grueso
            fg_color     = "#3A3A3A",   # fondo ligeramente más claro
            text_color   = "white"      # texto visible
        )
    #si aplicar es falso se captura el estilo en estilo = {}
    
    #si es verdadero, aplicamos el estilo preciamente guardado
def guardar_estilo(widget):
    for prop in PROPIEDADES_SEGURO:
        estilo[prop] = widget.cget(prop)

def aplicar_estilo_onoff_a_lista(lista_botones, encendido):
    """
    Igual que aplicar_estilo_onoff() pero para varios botones en paralelo.
    """
    for b in lista_botones:
        aplicar_estilo_onoff(b, encendido)
def reiniciar_estilo():
    estilo.clear()


