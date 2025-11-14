from machine import Pin,ADC
import neopixel


config = {"Btn_arriba":{"pin":4,"modo":Pin.IN,"pull":Pin.PULL_UP},
          "Btn_abajo":{"pin":5,"modo":Pin.IN,"pull":Pin.PULL_UP},
          "Btn_switch":{"pin":6,"modo":Pin.IN,"pull":Pin.PULL_UP},
          "Btn_clk":{"pin":7,"modo":Pin.IN,"pull":Pin.PULL_UP}
          "Btn_D":{"pin":0,"modo":Pin.IN,"pull":Pin.PULL_UP}
          }
configIRQ = {"Btn_arriba":{"trigger":Pin.IRQ_FALLING},
             "Btn_focus_up":{"trigger":Pin.IRQ_FALLING},
             "Btn_switch":{"trigger":Pin.IRQ_FALLING},
             "Btn_D":{"trigger":Pin.IRQ_FALLING}}
pines = {}

np=None

def init_pines():
    for clave, valor in config.items():
        if valor["pull"] is not None:
            pines[clave] = Pin(valor["pin"],valor["modo"],valor["pull"])
        else:
            pines[clave] = Pin(valor["pin"],valor["modo"])

        
def init_irq(clave, _handler):
    valor_trigger = configIRQ[clave]["trigger"]
    pines[clave].irq(handler=_handler,trigger = valor_trigger)
    
def set_color(r, g, b):
    global np
    np[0] = (r, g, b)
    np.write()

def configRGB():
    global np
    NEO_PIN = 8          
    NUM_LEDS = 1
    np = neopixel.NeoPixel(Pin(NEO_PIN), NUM_LEDS)   
