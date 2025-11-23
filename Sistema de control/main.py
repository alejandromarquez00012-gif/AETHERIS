import sistema.serial_reader as sr
import time
from machine import Pin
import sistema.IO as io
import micropython
import sistema.sistema as stm
import control.control as cl
import sistema.alarmas as al


evento_encoder = False


    
#============== TX ==================
#=== HANDLER ===
def leer_encoder(pin):
    global evento_encoder
    evento_encoder = True
def btn_enter(pin):
    if io.antirrebote("Btn_enter"):
        sr.send_cmd({"focus":"enter"})
def btn_on_off(pin):
    if io.antirrebote("Btn_on_off"):
        sr.send_cmd({"sistema":"toggle"})
#=== FUNC ===
def procesar_encoder():
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
    stm.toggle_estado()
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

if cl.init_control():
    sr.send_cmd({"sensor":"ok"})
else:
    sr.send_cmd({"sensor":"not ok"})
flujo = 0



io.set_pwm(30000)



while True:    
    lectura=sr.leer_cmd()
    if lectura is not None:
        procesar_cmd(lectura)
    if evento_encoder:

        evento_encoder = False
        procesar_encoder()
 
    if stm.estado:
        spo2 = cl.leer_spo2()
        if spo2 is not None:
            sr.send_cmd({"spo2":spo2})
        cl.control_flujo(io.get_adc(),io.get_pwm(),2,"f")
#         flujo = mx.leer_flujo()
#         if flujo is not None:
#             sr.send_cmd({"flujo":flujo})
 




