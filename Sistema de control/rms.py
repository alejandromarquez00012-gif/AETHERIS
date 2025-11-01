from machine import sleep, SoftI2C, Pin
from utime import ticks_diff, ticks_ms
from _init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import json 
import math
import sys
import time
import uselect

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

        if evento:  # hay algo disponible en stdin
            linea = sys.stdin.readline()
            if not linea:
                # llegó algo raro vacío, ignoramos
                pass
            else:
                linea = linea.strip()  # <- limpiar \n, \r, espacios etc.

                if linea != "":
                    try:
                        comando = json.loads(linea)
                    except Exception:
                        # si mandaron basura que no es JSON, avisamos y seguimos
                        print(json.dumps({"ack": False, "error": "json_invalido"}))
                else:
                    # comando sí se pudo parsear
                    if comando.get("led") == "on":
                        set_color(255, 255, 255)
                        print(json.dumps({"ack": True, "led": "on"}))

                    elif comando.get("led") == "off":
                        set_color(0, 0, 0)
                        print(json.dumps({"ack": True, "led": "off"}))

                    else:
                        print(json.dumps({"ack": False, "error": "comando no identificado"}))

        
        
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
                
if __name__ == "__main__":
    main()
