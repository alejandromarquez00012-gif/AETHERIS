from machine import sleep, SoftI2C, Pin
from utime import ticks_diff, ticks_ms
from _init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import json 
import math

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


# ----------------- Programa Principal -----------------
def main():
    i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
    sensor = MAX30102(i2c=i2c)

    if sensor.i2c_address not in i2c.scan():
        print("Sensor not found.")
        return
    elif not sensor.check_part_id():
        print("I2C device ID not corresponding to MAX30102 or MAX30105.")
        return
    else:
        print("Sensor connected and recognized.")

    sensor.setup_sensor()
    sensor.set_sample_rate(3200)
    sensor.set_fifo_average(32)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
    
    #actual_acquisition_rate = int(3200 /4)
    monitor = HeartRateMonitor()
    SPO2=0
    ventana_red = []
    VENTANA_SIZE =100
    while True:
        sensor.check()
        if sensor.available():
            red = sensor.pop_red_from_storage()
            #ir = sensor.pop_ir_from_storage()
            
            monitor.agregarElemento(red)
            Spo2=monitor.norma2()
            ventana_red.append(red)
            
            if len(ventana_red) > VENTANA_SIZE:
                ventana_red.pop(0)
                #ventana_ir.pop(0)
            
#             
#                 print("RED: {:04d}, Promedio: {:0.2f}".format(red,Spo2))
#             else:
#                 None
#                 print("RED: {:04d}, Promedio: ------".format(red))
#
            if(Spo2 is not None):
                print(json.dumps(
                {
                "spo2":  round(Spo2, 1)
            #La función round() sirve para redondear números en Python.
            #"flujo": round(flujo_lm, 2)
                }
        ))
                
if __name__ == "__main__":
    main()
