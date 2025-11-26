import sistema.serial_reader as sr
import time
from machine import Pin
import sistema.IO as io
import micropython
import sistema.sistema as stm
import control.control as cl
import sistema.alarmas as al
from machine import Timer

evento_encoder = False


    
#============== TX ==================
#=== HANDLER ===
def leer_encoder(pin):
    global evento_encoder
    evento_encoder = True
# def btn_enter(io.get_pin("Btn_enter")):
def btn_enter(pin):
    if io.antirrebote("Btn_enter") and not pin.value() and io.get_value("Btn_on_off"):
        sr.send_cmd({"focus":"enter"})

def btn_on_off(pin):
    if io.antirrebote("Btn_on_off") and not pin.value() and io.get_value("Btn_enter"):
        estado1 = io.get_value("Btn_enter")
        estado2 = io.get_value("Btn_on_off")
        estado3 = pin.value()
        print(f"estado on_off {estado2} estado enter {estado1} valor pin {estado3}")
#         None
        sr.send_cmd({"sistema":"toggle"})
#=== FUNC ===
def procesar_encoder():
    if io.antirrebote("up_down"):
        sr.send_cmd(io.encoder_procesar())
#============== TX ==================

#============== RX ==================
t1 = Timer(0)
bool_t1 = False
flag_send = False
def send_control(t1):
    global flag_send
    flag_send = True   
def toogle_t1():
    global bool_t1
    bool_t1 = not bool_t1
    if bool_t1:
        t1.init(period = 50,mode=Timer.PERIODIC,callback=send_control)
    else:
        t1.deinit()
def procesar_cmd(cmd):
    tema = cmd.get("rx")
    if tema is not None:
        handler = handlers.get(tema)
        if handler:
            handler(cmd)
        elif handler is None:
            pass
        
def manejar_sistema(cmd):
    toogle_t1()
    stm.toggle_estado()
def manejar_control(cmd):
    cl.parametros_set(cmd)
def manejar_alarmas(cmd):
    al.alarmas_set(cmd)
#     al.alarmas_print()


handlers = {
    "sistema": manejar_sistema,
    "control": manejar_control,
    "alarmas": manejar_alarmas,
}  
    







flujo = 0

# # # # # # # # CONFIGURACIONES INCIALES
io.init_pines()
io.init_irq("Btn_on_off",btn_on_off)
io.init_irq("Btn_enter", btn_enter)
io.init_irq("Btn_D", leer_encoder)
# io.deinit_pines()
al.pin_set()
cl.init_control()
sistema = False       


# io.set_pwm(30000)



spo2 = 0
flujo = 0
error = 0
pwm = 0
pwm_f = 0
ref = 0
p = 29490
io.set_pwm(65535)
while True:    
    lectura=sr.leer_cmd()
    if lectura is not None:
        procesar_cmd(lectura)
    if evento_encoder:
        evento_encoder = False
        procesar_encoder()
 
    
    if stm.estado:
        if flag_send:
            flag_send = False
#             al.actualizar_alarmas(spo2)
#             print(f"flujo {flujo}, error {error_f} v_prom {pwm_f}, ref {ref}")
            sr.send_cmd({"control":{"flujo":flujo,"spo2":spo2,"error":error}})
#             p = (p+50)%65535
            #pwm.duty_u16(int(p))
#             io.set_pwm(65535)
	
#	Lectura de datos
        flujo = cl.leer_flujo(io.get_adc())
        flujo = round(flujo,2)
        _spo2 = cl.leer_spo2()
        if _spo2 is not None:
            spo2 = _spo2
            spo2 = round(spo2,2)

	#control
        error = cl.control_variable(io.get_pwm(),flujo,spo2)
