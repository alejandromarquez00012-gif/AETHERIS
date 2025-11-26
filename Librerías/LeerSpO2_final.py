import math
from machine import SoftI2C, Pin
from max30102._init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM

class HeartRateMonitor:
    def __init__(self, ventana=10):
        self.lista = []
        self.ventana = ventana

    def agregar(self, dato):
        self.lista.append(dato)

    def calcular_spo2(self):
        if len(self.lista) >= self.ventana:
            prom = math.sqrt(sum(x * x for x in self.lista)) / len(self.lista)
            spo2 = 0.0448 * prom + 80.99
            self.lista.clear()
            return spo2
        return None

class FiltroExpSpo2:
    def __init__(self, alpha=0.25):
        self.alpha = alpha
        self.y = None

    def filtrar(self, x):

        if x is None:
            return self.y

        if self.y is None:
            self.y = x
        else:
            self.y = self.y + self.alpha * (x - self.y)
        return self.y


_sensor = None
_on = False
_monitor = None
_filtro = None


def config_spo2(ventana=10, alpha=.02):
    global _sensor, _on, _monitor, _filtro

    i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
    sensor = MAX30102(i2c=i2c)

    if (sensor.i2c_address not in i2c.scan()) or (not sensor.check_part_id()):
        _on = False
        return False

    sensor.setup_sensor()
    sensor.set_sample_rate(3200)
    sensor.set_fifo_average(32)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    _sensor = sensor
    _monitor = HeartRateMonitor(ventana=ventana)
    _filtro = FiltroExpSpo2(alpha=alpha)
    _on = True
    return True


def leer_spo2():
    
    global _sensor, _on, _monitor, _filtro

    if not _on or _sensor is None or _monitor is None or _filtro is None:
        return False

    _sensor.check()
    if _sensor.available():
        red = _sensor.pop_red_from_storage()

        _monitor.agregar(red)

        spo2_inst = _monitor.calcular_spo2()

        if spo2_inst is not None:
            spo2_filtrada = _filtro.filtrar(spo2_inst)
            if spo2_filtrada is not None:
                return round(spo2_filtrada, 1)

    return None
