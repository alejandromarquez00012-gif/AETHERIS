from machine import sleep, SoftI2C, Pin, PWM, ADC
from utime import ticks_diff, ticks_ms
from _init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import json
import math
import sys
import time
import uselect

# ----------- CONFIGURACIÓN DE LOS ADC / PWM -----------
adc_oxigeno = ADC(Pin(5))
adc_oxigeno.atten(ADC.ATTN_11DB)   # ~0–3.3 V en ESP32
PWM_PIN = 3
pwm = PWM(Pin(PWM_PIN), freq=1000, duty_u16=0)

# ----------- CONSTANTES DE CALIBRACIÓN (V -> LPM) -----------
VMAX_O2 = 1.6     # voltaje = 0 psi
VMIN    = 1.26    # voltaje = 50 psi

K_FLOW = 5.2698
C0     = 103.05
C1     = 73.53

def v_to_lpm(v):
    if v < VMIN:
        v = VMIN
    elif v > VMAX_O2:
        v = VMAX_O2

    inside = C0 - C1 * v
    if inside <= 0:
        return 0.0

    q = K_FLOW * math.sqrt(inside)

    if q < 0.0:
        q = 0.0
    elif q > 15.0:
        q = 15.0

    return q


ALPHA = 0.01       
DEADBAND = 0.1   
_flujo_filtrado = None

def filtrar_flujo(q):

    global _flujo_filtrado
    if _flujo_filtrado is None:
        _flujo_filtrado = q
        return _flujo_filtrado

    if abs(q - _flujo_filtrado) < DEADBAND:
        return _flujo_filtrado

    _flujo_filtrado += ALPHA * (q - _flujo_filtrado)
    return _flujo_filtrado


# ----------- CONTROLADOR
u1 = 0.0; u2 = 0.0
e1 = 0.0; e2 = 0.0; e3 = 0.0
u  = 0.0

r = 2

if r >=12:
    KP = 0.0012166
    KI_TS = 0.000122166
elif r >=6:
    KP = 0.000666
    KI_TS = 0.000052166
else:
    KP = 0.000126
    KI_TS = 0.000032166

def Limite_control(x):
    if x < 0.0:  return 0.0
    if x > 1:  return 1
    return x

def sat01(x):
    return Limite_control(x)

def leer_adc_pwm_control(adc):
    global u1, u2, e1, e2, e3

    v_sum = 0.0
    y_sum = 0.0
    for _ in range(20):
        try:
            raw16 = adc.read_u16()            
        except AttributeError:
            raw16 = adc.read() * 16           

        v = raw16 * 4.1 / 65535.0
        y_i = v_to_lpm(v)                      
        y_if = filtrar_flujo(y_i)

        v_sum += v
        y_sum += y_if

    v_avg = v_sum / 20.0
    y     = y_sum / 20.0

    e0 = r - y
    err=e0/r*100
    
    u0 = u1+ KP*(e0) + KI_TS*e1
    u  = sat01(u0)

    pwm.duty_u16(int(u * 65535))

    u2, u1 = u1, u
    e3, e2, e1 = e2, e1, e0
    print_row(u,y,v,err)
    time.sleep_us(5000)
    
    
    return y   
    
# ----------- UTILIDADES DE IMPRESIÓN / PROMEDIO -----------
_header_done = False
_row_count   = 0

def print_row(u0, y_lpm, v, err):
    global _header_done, _row_count
    if not _header_done or _row_count % 25 == 0:  # reimprime encabezado cada 25 filas
        # print(f"{'Control':>12}  {'Retro[LPM]':>12}  {'V':>8}")
        # print(f"{'-'*12}  {'-'*12}  {'-'*8}")
        _header_done = True
    print(f"{u0:12.4f}  {y_lpm:12.3f}  {v:8.4f}	{err:8.4f}")
    _row_count += 1

def leer_promedio(func, muestras=10):
    """Promedia varias lecturas para mayor estabilidad"""
    return sum(func() for _ in range(muestras)) / muestras

# ----------- HR MONITOR (igual que tu código) -----------
class HeartRateMonitor:
    def __init__(self, ventana=10):
        self.lista = []
        self.ventana = ventana

    def agregarElemento(self, dato):
        self.lista.append(dato)

    def norma2(self):
        if len(self.lista) >= self.ventana:
            prom = (math.sqrt(sum(x**2 for x in self.lista))) / len(self.lista)
            spo2 = 0.12698*prom + 79.82
            self.lista.clear()
            return spo2
        else:
            return None

# ----------- ENTRADA DE COMANDOS POR STDIN (igual) -----------
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
        return None
    linea = sys.stdin.readline()
    if not linea:
        return None
    linea = linea.strip()
    if linea == "":
        return None
    try:
        comando = json.loads(linea)
        return comando
    except Exception:
        return {"_error_parse": "json_invalido", "_raw": linea}

def procesar_comando(cmd):
    """
    Recibe un diccionario (cmd) y decide qué hacer.
    Regresa SIEMPRE un dict de respuesta para imprimir con json.dumps().
    """
    if cmd is None:
        return None
    if "_error_parse" in cmd:
        return {"ack": False, "error": cmd["_error_parse"], "raw": cmd.get("_raw", "")}
    if cmd.get("led") == "on":
        return {"ack": True, "led": "on"}
    elif cmd.get("led") == "off":
        return {"ack": True, "led": "off"}
    return {"ack": False, "error": "comando_no_identificado", "cmd": cmd}

# ----------------- Programa Principal -----------------
def main():
    i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
    sensor = MAX30102(i2c=i2c)
    on = None

    if sensor.i2c_address not in i2c.scan():
        print({"sensor": "no identificado"})
        on = False
    elif not sensor.check_part_id():
        print({"sensor": "I2C device ID not corresponding to MAX30102 or MAX30105."})
        on = False
    else:
        on = True
        print({"sensor": "Sensor connected and recognized."})

    if on:
        sensor.setup_sensor()
        sensor.set_sample_rate(3200)
        sensor.set_fifo_average(32)
        sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    monitor = HeartRateMonitor()
    ventana_red = []
    VENTANA_SIZE = 100

    while True:
        while not on:
            cmd = leer_comando()
            cmd = procesar_comando(cmd)
            if cmd is not None:
                print(cmd)

        sensor.check()
        if sensor.available():
            red = sensor.pop_red_from_storage()
            monitor.agregarElemento(red)
            Spo2 = monitor.norma2()
            ventana_red.append(red)
            if len(ventana_red) > VENTANA_SIZE:
                ventana_red.pop(0)
            if (Spo2 is not None):
                print(json.dumps({"spo2": round(Spo2, 1)}))

        # Lee y promedia el canal de oxígeno (en L/min) mediante el lazo de control
        v_o2_lpm = leer_promedio(lambda: leer_adc_pwm_control(adc_oxigeno))

if __name__ == "__main__":
    main()
