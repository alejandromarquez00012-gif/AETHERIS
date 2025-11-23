import serial_reader as sr
import time
from machine import Pin
import IO as io
import micropython
import sistema as sys
import control as cl
import alarmas as al



#============== TX ==================
#=== HANDLER ===
def leer_encoder(pin):
        micropython.schedule(procesar_encoder,0)
def btn_enter(pin):
    if io.antirrebote("Btn_enter"):
        sr.send_cmd({"focus":"enter"})
def btn_on_off(pin):
    if io.antirrebote("Btn_on_off"):
        sr.send_cmd({"sistema":"toggle"})
#=== FUNC ===
def procesar_encoder(_):
    if io.antirrebote("up_down"):
        sr.send_cmd(io.encoder_procesar())
#============== TX ==================

#============== RX ==================   
def procesar_cmd(cmd):
    tema = cmd.get("rx")
    if tema is not None:
        handler = handlers.get(tema)
        if handler:
            handler(cmd)
        elif handler is None:
            sr.send_cmd_not_id()
        
def manejar_sistema(cmd):
    sys.toggle_estado()
def manejar_control(cmd):
    cl.parametros_set(cmd)
def manejar_alarmas(cmd):
    al.alarmas_set(cmd)
    al.alarmas_print()


handlers = {
    "sistema": manejar_sistema,
    "control": manejar_control,
    "alarmas": manejar_alarmas,
}  
    

sistema = False       
io.init_pines()

io.init_irq("Btn_on_off",btn_on_off)
io.init_irq("Btn_enter", btn_enter)
io.init_irq("Btn_D", leer_encoder)


valor = 0
valor2 = 99
while True:
    lectura=sr.leer_cmd()
    if lectura is not None:
        procesar_cmd(lectura)
        
        
    if sys.estado:
        valor = (valor +1 ) % 14
        valor2= (valor2 -1)%100
        sr.send_cmd({"flujo":valor})
        sr.send_cmd({"spo2":valor2})
        time.sleep_ms(10)

    



