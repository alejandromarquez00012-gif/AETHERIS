from PIL import Image
import customtkinter as ctk
import tkinter as tk
import json
import threading
import serial
import queue
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

""" DEFINICION DE FUNCIONES """
def frame():
    frame_principal = ctk.CTkFrame(
                                master=app, 
                                fg_color="white")
    frame_principal.place(
                      x=0, 
                      y=0, 
                      relwidth=1, 
                      relheight=1)
    return frame_principal

def subframe(_master,w,h,color_,x,y):
    _subframe = ctk.CTkFrame(
                            master = _master,
                            width = w,
                            height = h,
                            fg_color = "white",
                            corner_radius = 10,
                            border_width = 1,        
                            border_color = color_
                                    )
    _subframe.place(
                    relx=x, 
                    rely=y, 
                    anchor=tk.CENTER)
    return _subframe

def mostrarFrame(frame):
    frame.lift()

def etiqueta(tamano, marco, texto=None, x=0.5, y=0.5, fuente=None,variable=None, fondo=None, color_texto="black",ancho=None, alto=None):
    if fuente is not None:
        configuracion_fuente = ("DejaVu Sans", tamano, fuente)
    else:
        configuracion_fuente = ("DejaVu Sans", tamano)
    argumentos = {
        "master": marco,
        "font": configuracion_fuente,
        "text_color": color_texto,
        "justify": "center"
    }
    if fondo is not None:
        argumentos["fg_color"] = fondo
    if variable is not None:
        argumentos["textvariable"] = variable
    else:
        argumentos["text"] = texto
    if ancho is not None:
        argumentos["width"] = ancho
    if alto is not None:
        argumentos["height"] = alto
    etiqueta_creada = ctk.CTkLabel(**argumentos)
    etiqueta_creada.place(relx=x, rely=y, anchor=tk.CENTER)
    return etiqueta_creada

def cargarImagen(direccion,size_x,size_y,x=None,y=None,frame=None):
    imagen_ = Image.open("./IMGS/"+ direccion)
    imagen_ = ctk.CTkImage(
        light_image=imagen_,
        dark_image=imagen_,
        size=(size_x,size_y))
    if frame is not None:
        logo = ctk.CTkLabel(
                                frame, 
                                image=imagen_, 
                                text="")
        logo.place(
                        relx=x, 
                        rely=y, 
                        anchor="center")
        return None
    else:
        return imagen_

def boton(frame,text_,w,h,x,y,funcion,target=None,img=None,compound=None):
    cmd = funcion if target is None else (lambda: funcion(target))
    if compound is not None:
        boton_ = ctk.CTkButton(
                            master = frame, 
                            text=text_,
                            width=w,      
                            height=h, 
                            font=("DejaVu Sans", 15,"bold"),
                            command=cmd,
                            compound = "bottom",
                            image = img) 
    else:                       
        boton_ = ctk.CTkButton(
                            master = frame, 
                            text=text_,
                            width=w,      
                            height=h, 
                            font=("DejaVu Sans", 15,"bold"),
                            command = cmd,
                            image = img)
    boton_.place(
                 relx = x, 
                 rely = y,
                 anchor = tk.CENTER)
    return boton_

def comboBox(frame,_values,_evento,x,y, variable=None, inicial=None):
    combobox = ctk.CTkComboBox(
        master = frame,
        values = _values,
        command = _evento,
        variable=variable
    )
    if inicial is not None:
        combobox.set(inicial)
        if variable is not None:
            variable.set(inicial)
    elif _values:
        combobox.set(_values[0])
        if variable is not None:
            variable.set(_values[0])
    combobox.place(
        relx=x, rely=y, anchor=tk.CENTER
    )
    return combobox

def onoff():
    global estado_onoff
    estado_onoff = not estado_onoff
    estilo_onOff()

def estilo_onOff():
    for btn_onOff in botones_onoff:
        if estado_onoff:
            btn_onOff.configure(
                text="ON",
                fg_color="green",    
                hover_color="green",
                text_color="white"
            )
        else:
            btn_onOff.configure(
                text="OFF",
                fg_color="red",    
                hover_color="red",
                text_color="white"
            )

def usar_frames(excepto=None):
    todos = [frame_principal, frame_modo_automatico, frame_modo_manual, frame_alarmas]
    if excepto is None:
        return todos
    return [f for f in todos if f not in excepto]

def crear_stringVar(app, valor_inicial="--"):
    return tk.StringVar(master=app, value=valor_inicial)

def lector_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except Exception:
        return 
    while True:
        line = ser.readline()
        if not line:
            continue
        try:
            data = json.loads(line.decode("utf-8").strip())
        except Exception:
            continue 
        spo2  = float(data.get("spo2", 0.0))
        flujo = float(data.get("flujo", 0.0))
        def _upd():
            spo2_var.set(f"{spo2:0.1f} %")
            flujo_var.set(f"{flujo:0.2f} L/min")
            ys_spo2.append(spo2)
            ys_flujo.append(flujo)
        app.after(0, _upd)
        try:
            cantidad_muestra_inicial.put_nowait(spo2)
        except queue.Full:
            pass

def inicializar_grafica(frame_contenedor,
                        relx=0.5, rely=0.5,
                        width=520, height=220,
                        intervalo_ms=150):
    fig = Figure(figsize=(5.4, 2.2), dpi=100)
    ax = fig.add_subplot(111)
    ax.grid(True)
    ax.set_title(" ")
    linea, = ax.plot([], [], linewidth=2)

    canvas = FigureCanvasTkAgg(fig, master=frame_contenedor)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.place(relx=relx, rely=rely, anchor=tk.CENTER, width=width, height=height)

    def actualizar_grafica():
        metrica = metrica_var.get()
        if metrica == "Flujo":
            datos = ys_flujo
            ax.set_ylim(0, 15)
            ax.set_ylabel("L/min")
        else:
            datos = ys_spo2
            ax.set_ylim(0, 100)
            ax.set_ylabel("%")

        ventana = max(int(PUNTOS_GRAFICAR), 1)
        datos_vis = datos[-ventana:] if len(datos) > ventana else datos[:]

        xs = list(range(len(datos_vis)))
        linea.set_data(xs, datos_vis)

        if len(xs) < ventana:
            ax.set_xlim(0, ventana)
        else:
            ax.set_xlim(len(xs) - ventana, len(xs))

        canvas.draw_idle()
        app.after(intervalo_ms, actualizar_grafica)

    actualizar_grafica()
    return {"fig": fig, "ax": ax, "linea": linea, "canvas": canvas, "widget": canvas_widget}

def on_cambio_metrica(value):
    metrica_var.set(value)

def on_cambio_rango(value):
    mins = int(value.split()[0])
    global PUNTOS_GRAFICAR
    PUNTOS_GRAFICAR = PUNTOS_POR_MINUTO * mins

def cuadro_texto(_maestro, x, y, ancho, alto, valor_inicial=""):
    ct = ctk.CTkTextbox(
        master=_maestro,
        width=ancho,
        height=alto,
        border_width=1,
        border_color="black",
        font=("DejaVu Sans", 20)
    )
    ct.place(relx=x, rely=y, anchor=tk.CENTER)
    
    if valor_inicial != "":
        ct.insert("0.0", str(valor_inicial))
    return ct

""" DEFINICION DE FUNCIONES """

""" """ """ """ """ """ """ MAIN """ """ """ """ """ """ """

"""configuraciones de app  """
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
app = ctk.CTk()
"""configuraciones de app  """

""" VARIABLES """ 
botones_onoff = []
estado_onoff = False

cantidad_muestra_inicial = queue.Queue(maxsize=200)

SERIAL_PORT = "/dev/ttyACM0"   
BAUDRATE    = 115200

tiempo_muestra = 0.3                 
PUNTOS_POR_MINUTO  = int(60 / tiempo_muestra)   
PUNTOS_GRAFICAR   = PUNTOS_POR_MINUTO * 1    

metrica_var = tk.StringVar(master=app, value="SpO2")
rango_var = tk.StringVar(master=app, value="1 min")
""" VARIABLES """ 

""" """ """ CREACION DE FRAMES """ """ """
frame_principal = frame()
frame_modo_manual = frame()
frame_modo_automatico = frame()
frame_alarmas = frame()
""" """ """ CREACION DE FRAMES """ """ """

""" """ """ CREACION DE SUBFRAMES """ """ """
subframe_modos = subframe(frame_principal,400,150,"black",0.33,0.8)
subframe_limites = subframe(frame_alarmas,760,300,"black",0.5,0.48)

subframe_grafica_manual = subframe(frame_modo_manual, 525, 300, "black", 0.65, 0.48)
subframe_grafica_auto = subframe(frame_modo_automatico, 525, 300, "black", 0.65, 0.48)

subframe_variable_numerica_flujo = subframe(frame_modo_manual,200,300,"black",0.15,0.48)
subframe_variable_numerica_spo2 = subframe(frame_modo_automatico,200,300,"black",0.15,0.48)
""" """ """ CREACION DE SUBFRAMES """ """ """

""" """ """ CREACION DE STRINVAR """ """ """
spo2_var  = crear_stringVar(app, "--.- %")
etiqueta(20, subframe_variable_numerica_spo2, x=0.5, y=0.9, variable=spo2_var)

flujo_var = crear_stringVar(app, "--.- L/min")
etiqueta(20, subframe_variable_numerica_flujo, x=0.5, y=0.9, variable=flujo_var)
""" """ """ CREACION DE STRINVAR """ """ """

""" """ """ CREACION DE GRAFICA """ """ """
ys_spo2 = []  
ys_flujo = [] 
inicializar_grafica(subframe_grafica_auto)
inicializar_grafica(subframe_grafica_manual)
""" """ """ CREACION DE GRAFICA """ """ """ 

""" """ """ CREACION DE ETIQUETA """ """ """
LF_principal = etiqueta(30,frame_principal,"Sistema demostrativo de control \nautomático en oxigenoterapia",0.5,0.4)
flujo = etiqueta(20,subframe_variable_numerica_flujo,"Flujo:",0.5,0.8)
spo2 = etiqueta(20,subframe_variable_numerica_spo2,"SpO₂:",0.5,0.8)

for f in usar_frames(excepto=None):
 etiqueta(30,f,"SIVORA",0.9,0.1,"bold")

LF_principal = etiqueta(20,subframe_modos,"Modos de control",0.5,0.2)

aceptable = etiqueta(20,subframe_limites, "Aceptable", x=0.2, y=0.26, fondo="blue",color_texto="white", ancho=120, alto=40,fuente="bold")
regular = etiqueta(20,subframe_limites, "Regular", x=0.2, y=0.46, fondo="green",color_texto="white", ancho=120, alto=40,fuente="bold")
bajo = etiqueta(20,subframe_limites, "Bajo", x=0.2, y=0.66, fondo="#DAA520",color_texto="white", ancho=120, alto=40,fuente="bold")
riesgo = etiqueta(20,subframe_limites, "En riesgo", x=0.2, y=0.86, fondo="red",color_texto="white", ancho=120, alto=40,fuente="bold")
limite_sup = etiqueta(20,subframe_limites, "Límite superior (%)", x=0.45, y=0.12)
limite_inf = etiqueta(20,subframe_limites, "Límite inferior (%)", x=0.75, y=0.12)
""" """ """ CREACION DE etiqueta """ """ """

""" """ """ CREACION DE IMAGENES """ """ """
for f in usar_frames(excepto=None):
    cargarImagen("logo.png",180,40,0.14,0.1,f) 

cargarImagen("home.png",40,40,0.95,0.9,frame_principal)
img_flecha = cargarImagen("flecha2.png",40,20)
cargarImagen("AUTO.png",40,40,0.95,0.9,frame_modo_automatico)
cargarImagen("MANUAL.png",40,40,0.95,0.9,frame_modo_manual)
cargarImagen("gears.png",40,40,0.95,0.9,frame_alarmas)
""" """ """ CREACION DE IMAGENES """ """ """

""" """ """ CREACION DE BOTONES """ """ """
boton(subframe_modos,"Control por\nSpO2",150,60,0.25,0.7,mostrarFrame,frame_modo_automatico)
boton(subframe_modos,"Control por\nflujo",150,60,0.75,0.7,mostrarFrame,frame_modo_manual)
boton(frame_principal,"Modificar \nrangos",150,60,0.75,0.72,mostrarFrame,frame_alarmas)

for f in usar_frames(excepto=[frame_alarmas]):
    btn_onOff = boton(f,"OFF",150,60,0.75,0.86,onoff)
    botones_onoff.append(btn_onOff) 
estilo_onOff()

for f in usar_frames(excepto=[frame_principal]):
    boton(f, "Regresar", 150, 60, 0.15, 0.86, mostrarFrame, frame_principal, img_flecha, 1)

for f in usar_frames(excepto=[frame_principal,frame_alarmas]):
    boton(f, "Modificar ganancias", 150, 60, 0.5, 0.86, mostrarFrame, None)

boton(frame_alarmas,"Aplicar cambios",150,60,0.6,0.86,mostrarFrame,frame_alarmas)
""" """ """ CREACION DE BOTONES """ """ """

""" """ """ CREACION DE COMBO BOX """ """ """
cb_spo2 = comboBox(
                    subframe_grafica_auto,
                    ["SpO2", "Flujo"],
                    on_cambio_metrica,
                    0.5, 0.1,
                    variable=metrica_var,inicial="SpO2"
)
cb_flujo = comboBox(
                    subframe_grafica_manual,
                    ["Flujo", "SpO2"],
                    on_cambio_metrica,
                    0.5, 0.1,
                    variable=metrica_var,
                    inicial="SpO2"
)
cb_rango_auto = comboBox(
    subframe_grafica_auto,
    ["1 min", "2 min", "3 min", "4 min", "5 min"],
    on_cambio_rango,
    0.5, 0.93,
    variable=rango_var,
    inicial="1 min"
)
cb_rango_manual = comboBox(
    subframe_grafica_manual,
    ["1 min", "2 min", "3 min", "4 min", "5 min"],
    on_cambio_rango,
    0.5, 0.93,
    variable=rango_var,       # comparte la misma selección
    inicial=rango_var.get()
)
""" """ """ CREACION DE COMBO BOX """ """ """

""" """ """ CREACION DE CUADRO DE TEXTO """ """ """
ct_aceptable_limsup = cuadro_texto(subframe_limites,0.45,0.26,75,25,valor_inicial="100")
ct_regular_limsup = cuadro_texto(subframe_limites,0.45,0.46,75,25,valor_inicial="94.9")
ct_bajo_limsup = cuadro_texto(subframe_limites,0.45,0.66,75,25,valor_inicial="89.9")
ct_riesgo_limsup = cuadro_texto(subframe_limites,0.45,0.86,75,25,valor_inicial="86.7")

ct_aceptable_liminf = cuadro_texto(subframe_limites,0.75,0.26,75,25,valor_inicial="95")
ct_regular_liminf = cuadro_texto(subframe_limites,0.75,0.46,75,25,valor_inicial="90")
ct_bajo_liminf = cuadro_texto(subframe_limites,0.75,0.66,75,25,valor_inicial="87")
ct_riesgo_liminf = cuadro_texto(subframe_limites,0.75,0.86,75,25,valor_inicial="15")
""" """ """ CREACION DE CUADRO DE TEXTO """ """ """

app.attributes('-fullscreen', True)
app.bind("<Escape>", lambda e: app.destroy())

""" """ """ SELECCION DE FRAMES """ """ """
mostrarFrame(frame_principal)
""" """ """ SELECCION DE FRAMES """ """ """


threading.Thread(target=lector_serial, daemon=True).start()

app.mainloop()
""" """ """ """ """ """ """ MAIN """ """ """ """ """ """ """