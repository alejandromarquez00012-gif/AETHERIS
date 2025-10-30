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
            spo2 = 0.12698*prom + 79.82
            self.lista.clear()
            return spo2
        else:
            return None


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

    # === NUEVO: poner en alto GPIO 0, 1, 10, 11 y 2 ===
    pines_alto = [0, 1, 10, 11, 2]
    salidas = [Pin(p, Pin.OUT) for p in pines_alto]
    for s in salidas:
        s.value(1)
    print("GPIO 0, 1, 10, 11 y 2 configurados como salida y en HIGH")

    monitor = HeartRateMonitor()
    ventana_red = []
    VENTANA_SIZE = 100
    ultimo_spo2 = None  # para evitar errores cuando norma2() aún regresa None

    while True:
        sensor.check()
        if sensor.available():
            red = sensor.pop_red_from_storage()
            monitor.agregarElemento(red)
            Spo2 = monitor.norma2()  # puede ser None al inicio
            ventana_red.append(red)

            if len(ventana_red) > VENTANA_SIZE:
                ventana_red.pop(0)

            # Evita fallo si Spo2 es None (redondear None lanza error)
            if Spo2 is not None:
                ultimo_spo2 = round(Spo2, 1)

            print(json.dumps({
                "spo2": ultimo_spo2  # imprime el último válido o None al inicio
            }))

if __name__ == "__main__":
    main()
