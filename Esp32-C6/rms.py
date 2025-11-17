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
    cmd = None
    evento = recepcion.poll(0)
    if evento:
        # hay algo en stdin
        linea = sys.stdin.readline()
        if  linea:
            linea = linea.strip()
            if linea is not "":
                try:
                    cmd = json.loads(linea)
                except Exception:
                    cmd = {"_error_parse": "json_invalido", "_raw": linea}
    return cmd

def procesar_comando(cmd):
    _cmd = None
    if cmd is not None:
        if "_error_parse" in cmd:
            _cmd = {
                "ack": False,
                "error": cmd["_error_parse"],
                "raw": cmd.get("_raw", "")
            }

        elif cmd.get("led") == "on":
            _cmd = {"ack": True, "led": "on"}
            
        elif cmd.get("led") == "off":
            _cmd = {"ack": True, "led": "off"}
        else:
            _cmd = {"ack": False, "error": "comando_no_identificado", "cmd": cmd}
    return _cmd

# ----------------- Programa Principal -----------------
def main():
    i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
    sensor = MAX30102(i2c=i2c)
    on=None

    if sensor.i2c_address not in i2c.scan():
        print({"sensor":"no identificado"})
        on=False

    elif not sensor.check_part_id():
        print({"sensor":"I2C device ID not corresponding to MAX30102 or MAX30105."})

    else:
        on=True
        print({"sensor":"Sensor connected and recognized."})
        sensor.setup_sensor()
        sensor.set_sample_rate(3200)
        sensor.set_fifo_average(32)
        sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
    

    monitor = HeartRateMonitor()
    SPO2=0
    ventana_red = []
    VENTANA_SIZE =100
    
    
    while True:

        cmd = leer_comando()
        cmd = procesar_comando(cmd)
        if cmd is not None:
            print(json.dumps(cmd))
        if on:
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
                    print(json.dumps({"spo2":  round(Spo2, 1)}))
                
if __name__ == "__main__":
    main()
