from machine import Pin,ADC,PWM
import neopixel
import time

config = {"Btn_on_off":{"pin":22,"modo":Pin.IN,"pull":Pin.PULL_UP},
            "Btn_enter":{"pin":23,"modo":Pin.IN,"pull":Pin.PULL_UP},
            "Btn_clk":{"pin":11,"modo":Pin.IN,"pull":Pin.PULL_UP},
            "Btn_D":{"pin":10,"modo":Pin.IN,"pull":Pin.PULL_UP},
            "ADC":{"pin":3,"modo":"ADC","pull":None},
            "PWM":{"pin":1,"modo":"PWM","pull":None,"freq":1000},
            "aceptable":{"pin":21,"modo":Pin.OUT,"pull":None},
            "regular":{"pin":20,"modo":Pin.OUT,"pull":None},
            "malo":{"pin":19,"modo":Pin.OUT,"pull":None},
            "riesgo":{"pin":18,"modo":Pin.OUT,"pull":None},
            "buzzer":{"pin":2,"modo":"PWM","pull":None,"freq":500}
          }
configIRQ = {"Btn_on_off":{"trigger":Pin.IRQ_FALLING},
             "Btn_enter":{"trigger":Pin.IRQ_FALLING},
             "Btn_D":{"trigger":Pin.IRQ_FALLING}
             }
pines = {}



def init_pines():
    for clave, valor in config.items():
        if valor["pull"] is not None:
            pines[clave] = Pin(valor["pin"],valor["modo"],valor["pull"])
        elif valor["modo"] == "ADC":
            pines[clave] = ADC(Pin(valor["pin"]))
            pines[clave].atten(ADC.ATTN_11DB)
        elif valor["modo"] == "PWM":
            pines[clave] = PWM(Pin(valor["pin"]),freq = valor["freq"], duty_u16 = 0)
        else:
            pines[clave] = Pin(valor["pin"],valor["modo"])

        
def init_irq(clave, _handler):
    valor_trigger = configIRQ[clave]["trigger"]
    pines[clave].irq(handler=_handler,trigger = valor_trigger)

def get_value(pin):
    return pines[pin].value()

def get_pin(nombre):
    pin = None
    for clave, valor in pines.items():
        if clave == nombre:
            pin = pines[clave]
    return pin

last_ms = {}
def antirrebote(nombre, intervalo_ms = 100):
    """
    Devuelve True si ya pasó suficiente tiempo desde el último evento 'nombre'.
    Devuelve False si se considera rebote.
    """
    global last_ms
    rebote = False
    now = time.ticks_ms()
    last = last_ms.get(nombre, 0)

    if time.ticks_diff(now, last) < intervalo_ms:
        rebote = False  # rebote
    else:
        #print("entro")
        last_ms[nombre] = now
        rebote = True
    return rebote

def encoder_procesar():
    cmd = None
    valor_clk = get_value("Btn_clk") 
    if valor_clk == 1:
        cmd = {"focus":"arriba"}
    else:
        cmd = {"focus":"abajo"}
    return cmd


def set_pwm(value):
	pines["PWM"].duty_u16(value)


def get_pwm():
    return pines["PWM"]
def get_adc():
    return pines["ADC"]
