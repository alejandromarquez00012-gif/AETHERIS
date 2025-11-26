from machine import Pin, ADC, PWM
import time

config = {
    "Btn_on_off": {"pin": 22, "modo": Pin.IN,  "pull": Pin.PULL_UP},
    "Btn_enter":  {"pin": 18, "modo": Pin.IN,  "pull": Pin.PULL_UP},
    "Btn_clk":    {"pin": 4,  "modo": Pin.IN,  "pull": Pin.PULL_UP},
    "Btn_D":      {"pin": 3,  "modo": Pin.IN,  "pull": Pin.PULL_UP},
    "ADC":        {"pin": 5,  "modo": "ADC",   "pull": None},
    "PWM":        {"pin": 23, "modo": "PWM",   "pull": None, "freq": 1000},
    "aceptable":  {"pin": 11, "modo": Pin.OUT, "pull": None},
    "regular":    {"pin": 10, "modo": Pin.OUT, "pull": None},
    "bajo":       {"pin": 2,  "modo": Pin.OUT, "pull": None},
    "riesgo":     {"pin": 1,  "modo": Pin.OUT, "pull": None},
    "buzzer":     {"pin": 0,  "modo": "PWM",   "pull": None, "freq": 2},
}

# Solo por si quieres limpiar por número de pin
num_pin = [22, 18, 4, 3, 5, 23, 11, 10, 2, 1, 0, 19]

configIRQ = {
    "Btn_on_off": {"trigger": Pin.IRQ_FALLING},
    "Btn_enter":  {"trigger": Pin.IRQ_FALLING},
    "Btn_D":      {"trigger": Pin.IRQ_FALLING},
}

pines = {}
last_ms = {}
def deinit_pin(nombre):
    """Apaga correctamente el periférico asociado a 'nombre' y deja el GPIO como entrada."""
    global pines
    obj = pines.get(nombre, None)
    if obj is None:
        print(f"no se encontro {nombre}")
        return

    pin_num = config[nombre]["pin"]

    # Apagar periféricos si aplica
    try:
        if isinstance(obj, PWM):
            obj.deinit()
        # ADC no tiene deinit; basta con perder la referencia
    except Exception:
        pass

    # Dejar el pin como entrada "neutra"
    try:
        Pin(pin_num, Pin.IN)
    except Exception:
        pass

    # Borrar del diccionario
    try:
        del pines[nombre]
    except KeyError:
        pass
def deinit_pines():
    for nombre in list(pines.keys()):
        deinit_pin(nombre)
        
        
def init_pines():
    # Si quieres que siempre arranque limpio, descomenta:
    deinit_pines()

    for clave, valor in config.items():
        pin_num = valor["pin"]
        modo    = valor["modo"]
        pull    = valor["pull"]

        # Limpiar ese pin específicamente antes de reconfigurar
#         deinit_pin(clave)

        if modo == "ADC":
            adc = ADC(Pin(pin_num))
            adc.atten(ADC.ATTN_11DB)
            pines[clave] = adc

        elif modo == "PWM":
            freq = valor.get("freq", 1000)
            pwm = PWM(Pin(pin_num), freq=freq, duty_u16=0)
            pines[clave] = pwm

        else:
            # GPIO normal
            if pull is not None:
                pines[clave] = Pin(pin_num, modo, pull)
            else:
                pines[clave] = Pin(pin_num, modo)
def init_irq(clave, _handler):
    valor_trigger = configIRQ[clave]["trigger"]
    pines[clave].irq(handler=_handler, trigger=valor_trigger)

def get_value(nombre):
    return pines[nombre].value()

def get_pin(nombre):
    return pines[nombre]

def antirrebote(nombre, intervalo_ms=300):
    global last_ms
    now  = time.ticks_ms()
    last = last_ms.get(nombre, 0)
    if time.ticks_diff(now, last) < intervalo_ms:
        return False
    last_ms[nombre] = now
    return True

def encoder_procesar():
    valor_clk = get_value("Btn_clk")
    if valor_clk == 1:
        return {"focus": "arriba"}
    else:
        return {"focus": "abajo"}

def set_pwm(value):
    pines["PWM"].duty_u16(value)

def get_pwm():
    return pines["PWM"]

def get_adc():
    return pines["ADC"]

def get_alarmas():
    deseados = ["aceptable", "regular", "bajo", "riesgo", "buzzer"]
    return {k: pines[k] for k in deseados if k in pines}


