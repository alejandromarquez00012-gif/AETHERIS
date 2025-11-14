import serial_reader as sr
import time
from machine import Pin
import IO as io



def focus_up(pin):
    sr.send_cmd({"focus":"arriba"})
def focus_down(pin):
    sr.send_cmd({"focus":"abajo"})
def focus_selec(pin):
    sr.send_cmd({"focus":"selec"})
def change_num(pin):
    valor = io.get_value("Btn_clk")
    print(f"valor:{}",valor)
    
def procesar_cmd(_lectura):
    global sistema
    if "led" in _lectura:
        valor = _lectura["led"]
        if valor is "on":
           # print("prende el led")
            pass
        else:
            #print("apaga el led")
            pass
    if "sistema" in _lectura:
        valor = _lectura["sistema"]
        if valor is "on":
            sistema = True
            #print("sistema prendido")
        else:
            sistema = False
            #print("sistema apagado")
            
sistema = False       
io.init_pines()

io.init_irq("Btn_arriba",focus_up)
io.init_irq("Btn_abajo", focus_down)
io.init_irq("Btn_switch", focus_selec)
io.init_irq("Btn_D", change_num)

while True:
    lectura=sr.leer_cmd()
    if lectura is not None:
        procesar_cmd(lectura)
        
    if sistema:
        sr.send_cmd({"graf":12})
        time.sleep(0.1)
    
    

