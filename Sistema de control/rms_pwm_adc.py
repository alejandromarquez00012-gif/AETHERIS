from machine import sleep, SoftI2C, Pin, PWM, ADC
from utime import ticks_diff, ticks_ms
from _init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import json 
import math
import sys
import time
import uselect

# ----------- CONFIGURACIÓN DE LOS ADC -----------
adc_oxigeno = ADC(Pin(5)) 
adc_oxigeno.atten(ADC.ATTN_11DB)   # rango 0–1.1 V (en ESP32)
PWM_PIN=4
pwm = PWM(Pin(PWM_PIN), freq=1000, duty_u16=0)

# ----------- CONSTANTES DE CALIBRACIÓN -----------
VMAX_o2  =  2.198 
VMIN       = 1.957 

# controlador
A1 = 1.984321652
A2 = 0.9843139066
B1 = 0.9257012353
B2 = 1.825199557
B3 = 0.8996790191
Ts=.005

u1 = 0.0; u2 = 0.0          # u(k-1), u(k-2)
e1 = 0.0; e2 = 0.0; e3 = 0.0  # e(k-1), e(k-2), e(k-3)
u=0

r = 5

def Limite_control(x):
    """Saturación a [0,1]."""
    if x < 0.0:  return 0.0
    if x > .7:  return .7
    return x

# Alias para mantener el nombre usado en el control (no cambia la lógica)
def sat01(x):
    return Limite_control(x)


# ----------- FUNCIONES AUXILIARES -----------
def leer_adc_pwm_control(adc):
    """Lee el ADC en voltios (0–1.1 V nominal)"""
    global u1, u2, e1, e2, e3  # estados del controlador

    # --- 10 mediciones y promedio ---
    v_sum = 0.0
    y_sum = 0.0
    for _ in range(20):
        raw = adc.read() * 16                 # 0..65535 aprox
        v    = raw * 3.3 / 65535.0            # voltaje del sensor

        # clip al rango [VMIN, VMAX_o2]
        if v < VMIN:      v_clip = VMIN
        elif v > VMAX_o2: v_clip = VMAX_o2
        else:             v_clip = v

        # L/min: 1.957V -> 15 L/min ; 2.198V -> 0 L/min
        y_i = (VMAX_o2 - v_clip) * (15.0 / (VMAX_o2 - VMIN))

        v_sum += v
        y_sum += y_i

    v = v_sum / 20.0   # voltaje promedio (solo para imprimir/debug)
    y = y_sum / 20.0   # retroalimentación en L/min (promedio)

    # --- Control (misma lógica) ---
    e0 = r - y
    u0 = (A1*u1) - (A2*u2) + (B1*e1) - (B2*e2) + (B3*e3)
    u  = sat01(u0)
    pwm.duty_u16(int(u * 65535))

    # Actualiza estados
    u2, u1 = u1, u
    e3, e2, e1 = e2, e1, e0
    
    print_row(u0, y, v)
    
    return adc.read() * 3.3*16 / 65535

_header_done = False
_row_count   = 0

def print_row(u0, y_lpm, v):
    global _header_done, _row_count
    if not _header_done or _row_count % 25 == 0:  # reimprime encabezado cada 25 filas
        #print(f"{'Control':>12}  {'Retro[LPM]':>12}  {'V':>8}")
        #print(f"{'-'*12}  {'-'*12}  {'-'*8}")
        _header_done = True
    print(f"{u0:12.4f}  {y_lpm:12.3f}  {v:8.4f}")
    _row_count += 1
    
    
def leer_promedio(func, muestras=10):
    """Promedia varias lecturas para mayor estabilidad"""
    return sum(func() for _ in range(muestras)) / muestras


class HeartRateMonitor:
    def __init__(self, ventana=10):
        self.lista = []
        self.ventana = ventana

    def agregarElemento(self, dato):
        self.lista.append(dato)

    def norma2(self):
        if len(self.lista) >= self.ventana:
            prom = (math.sqrt(sum(x**2 for x in self.lista))) / len(self.lista)
            spo2 = 0.12698*prom +79.82  
            self.lista.clear()
            return spo2
        else:
            return None

recepcion = uselect.poll()
recepcion.register(sys.stdin, uselect.POLLIN)


def leer_comando():
    """
    No bloquea.
    - Si NO hay datos -> regresa None
    - Si hay datos pero no es JSON válido -> regresa {"_error_parse": "..."}
    - Si hay datos válidos -> regresa el dict decodificado
    """
    evento = recepcion.poll(0)
    if not evento:
        return None  # nada nuevo

    # hay algo en stdin
    linea = sys.stdin.readline()
    if not linea:
        return None  # línea vacía/rara, ignoramos

    linea = linea.strip()
    if linea == "":
        return None  # pura cadena vacía, ignoramos

    try:
        comando = json.loads(linea)
        return comando
    except Exception:
        # devolvemos un dict especial que indica error de parseo
        return {"_error_parse": "json_invalido", "_raw": linea}

def procesar_comando(cmd):
    """
    Recibe un diccionario (cmd) y decide qué hacer.
    Regresa SIEMPRE un diccionario de respuesta para imprimir con json.dumps().
    """
    if cmd is None:
        return None
    # 1. primero checamos si venía roto
    if "_error_parse" in cmd:
        return {
            "ack": False,
            "error": cmd["_error_parse"],
            "raw": cmd.get("_raw", "")
        }

    # 2. ejemplo simple: control de LED

    if cmd.get("led") == "on":
#         set_color(255, 255, 255)
        return {"ack": True, "led": "on"}

    elif cmd.get("led") == "off":
#         set_color(0, 0, 0)
        return {"ack": True, "led": "off"}
    return {"ack": False, "error": "comando_no_identificado", "cmd": cmd}

# ----------------- Programa Principal -----------------
def main():
    i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
    sensor = MAX30102(i2c=i2c)
    on=None
#     while not on:
    if sensor.i2c_address not in i2c.scan():
        print({"sensor":"no identificado"})
        on=False
#         return
    elif not sensor.check_part_id():
        print({"sensor":"I2C device ID not corresponding to MAX30102 or MAX30105."})
#         return
    else:
        on=True
        print({"sensor":"Sensor connected and recognized."})
# # # # # # # # # # #     BORRAR CONDICIONAL    
    if on:		
        sensor.setup_sensor()
        sensor.set_sample_rate(3200)
        sensor.set_fifo_average(32)
        sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
    

    monitor = HeartRateMonitor()
    SPO2=0
    ventana_red = []
    VENTANA_SIZE =100
    
    
    while True:
# # # # # # # # #         BORRAR CONDICIONAL
        while not on:
            cmd = leer_comando()
            cmd = procesar_comando(cmd)
            if cmd is not None:
                print(cmd)
        
        sensor.check()
        if sensor.available():
            red = sensor.pop_red_from_storage()
            #ir = sensor.pop_ir_from_storage()
            
            monitor.agregarElemento(red)
            Spo2=monitor.norma2()
            ventana_red.append(red)
            
            if len(ventana_red) > VENTANA_SIZE:
                ventana_red.pop(0)

            if(Spo2 is not None):
                print(json.dumps(
                {
                "spo2":  round(Spo2, 1)

                }
        ))
        # Lee y promedia los dos canales
        v_o2  = leer_promedio(lambda: leer_adc_pwm_control(adc_oxigeno))

       
                
    
if __name__ == "__main__":
    main()
    
