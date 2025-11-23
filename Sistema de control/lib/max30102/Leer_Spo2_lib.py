import math
from machine import Pin, SoftI2C
from max30102._init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM

_sensor = None
_on = False
_lista = []
_ventana = 10
_ventana2 = 100
_ventana_red = []


def config_spo2():

    global _sensor, _on, _lista, _ventana, _ventana2, _ventana_red

    # Inicializa buffers y parámetros
    _lista = []
    _ventana = 10
    _ventana2 = 100
    _ventana_red = []

    # Inicializa I2C y sensor
    i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
    _sensor = MAX30102(i2c=i2c)

    # Verificar sensor
    if (_sensor.i2c_address not in i2c.scan()) or (not _sensor.check_part_id()):
        _on = False
        #return False
    else:
        _sensor.setup_sensor()
        _sensor.set_sample_rate(3200)
        _sensor.set_fifo_average(32)
        _sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
        _on = True
        #return True
    return _on

def leer_spo2():
    
    global _sensor, _on, _lista, _ventana, _ventana2, _ventana_red
    #config = False
    spo2 = None
    if not _on or _sensor is None:
        pass
    else:
        # Lectura
        _sensor.check()
        if _sensor.available():
            red = _sensor.pop_red_from_storage()
            ir = _sensor.pop_ir_from_storage()
            _lista.append(red)
            _ventana_red.append(red)
            if len(_ventana_red) > _ventana2:
                _ventana_red.pop(0)
                #ir.clear()

            if len(_lista) >= _ventana:
                prom = (math.sqrt(sum(x * x for x in _lista))) / len(_lista)
                spo2 = 0.12698 * prom + 79.82
                spo2 = round(spo2,1)
                _lista.clear()
                #return round(spo2, 1)

    return spo2

