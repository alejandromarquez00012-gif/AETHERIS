# MAX30102 SpO₂ Reader – MicroPython Implementation

Este proyecto implementa la lectura y procesamiento de datos del sensor MAX30102 utilizando MicroPython, permitiendo estimar el nivel de saturación de oxígeno en sangre (SpO₂) a partir de la señal de luz roja.  
El código está basado en la librería pública MAX30102-MicroPython-driver desarrollada por n-elia, la cual proporciona la interfaz para comunicación I²C con el sensor.

## Aviso importante:
Este código está diseñado exclusivamente para fines demostrativos y de laboratorio dentro del proyecto Sistema demostrativo de control automático en oxigenoterapia.
No debe usarse para el monitoreo o diagnóstico real de pacientes.

Lenguaje: MicroPython  
Hardware: ESP32-C3 / ESP32-C6 / Raspberry Pi Pico  
Sensor: MAX30102 (pulso-oxímetro óptico)  
Licencia base: MIT  

## Descripción general

El programa establece comunicación I²C con el sensor MAX30102, configura sus parámetros de adquisición y procesa las muestras del canal Red (RED LED) para calcular una estimación del SpO₂ mediante una ventana deslizante de tamaño configurable.

El cálculo de SpO₂ se realiza a partir de la norma cuadrática promedio de la señal, usando la siguiente relación empírica:

SpO₂ = 0.12698 × norma2 + 79.82

donde norma2 es la raíz cuadrada de la suma de cuadrados de los valores de la ventana de muestras, dividida entre el tamaño de la ventana, lo cual representa la cantidad de energía promedio de la señal.

## Créditos y referencias

Este código utiliza la librería desarrollada por n-elia (2021) disponible públicamente en GitHub:

Repositorio original:  
[https://github.com/n-elia/MAX30102-MicroPython-driver](https://github.com/n-elia/MAX30102-MicroPython-driver)

Archivos utilizados del repositorio original:
- `__init__.py` → contiene la clase `MAX30102` para manejo del sensor.
- `circular_buffer.py` → implementa almacenamiento circular de muestras.

Licencia: MIT  
Autor original: n-elia  
Año: 2021  

La presente adaptación fue realizada por el equipo de ingeniería del proyecto Sistema demostrativo de control automático en oxigenoterapia, para integrar el sensor MAX30102 dentro del subsistema de adquisición de señales fisiológicas.



### Librerías importadas

python
from machine import sleep, SoftI2C, Pin
from utime import ticks_diff, ticks_ms
from _init_ import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import math


### Clase `HeartRateMonitor`

Implementa una ventana deslizante para almacenar muestras del canal RED y calcular la norma cuadrática promedio cada cierto número de datos.

python
class HeartRateMonitor:
    def __init__(self, ventana=10):
        self.lista = []
        self.ventana = ventana

    def agregarElemento(self, dato):
        self.lista.append(dato)

    def norma2(self):
        if len(self.lista) >= self.ventana:
            prom = (math.sqrt(sum(x**2 for x in self.lista))) / len(self.lista)
            spo2 = 0.12698 * prom + 79.82
            self.lista.clear()
            return spo2
        else:
            return None

### Programa principal

- Configura el bus I²C en los pines SDA=6 y SCL=7.  
- Inicializa el sensor y verifica su conexión.  
- Configura parámetros de muestreo (set_sample_rate(3200), set_fifo_average(32)).  
- Calcula el valor de SpO₂ en tiempo real e imprime los resultados en consola.

python
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
    
    monitor = HeartRateMonitor()
    ventana_red = []
    VENTANA_SIZE = 100
    
    while True:
        sensor.check()
        if sensor.available():
            red = sensor.pop_red_from_storage()
            monitor.agregarElemento(red)
            Spo2 = monitor.norma2()
            ventana_red.append(red)

            if len(ventana_red) > VENTANA_SIZE:
                ventana_red.pop(0)
            
            if Spo2 is not None:
                print("RED: {:04d}, Promedio: {:0.2f}".format(red, Spo2))
            else:
                print("RED: {:04d}, Promedio: ------".format(red))

## Fórmulas y procesamiento de señal

1. Ventana de cálculo: 10 muestras.  
2. Operación matemática:  
   - Cálculo de la norma 2: `√(Σ x²)`  
   - Normalización por número de elementos.  
3. Conversión empírica a SpO₂:  
   SpO₂ = 0.12698 × norma2 + 79.82

## Ejemplo de salida

Sensor connected and recognized.
RED: 0123, Promedio: ------
RED: 0087, Promedio: ------
RED: 0132, Promedio: 96.42

## Parámetros de configuración

| Parámetro | Valor | Descripción |
|------------|--------|-------------|
| Frecuencia I²C | 400 kHz | Comunicación rápida con el sensor |
| Tasa de muestreo | 3200 Hz | Lectura de muestras ópticas |
| Promedio FIFO | 32 | Suavizado interno |
| Ventana SpO₂ | 10 muestras | Cálculo cada 10 muestras |
| Relación empírica | `0.12698 * norma2 + 79.82` | Ajuste obtenido experimentalmente |

## Conexión del sensor MAX30102

| Sensor MAX30102 | Microcontrolador (ESP32-C3/C6) |
|-----------------|-------------------------------|
| VIN             | 3.3 V                         |
| GND             | GND                           |
| SDA             | GPIO 6                        |
| SCL             | GPIO 7                        |

Asegúrese de usar resistencias pull-up de 4.7 kΩ en las líneas SDA y SCL.

## Licencia

Este proyecto se distribuye bajo la licencia MIT, respetando la licencia original del repositorio de n-elia.  



## Autoría y contribución

Adaptación y uso en contexto biomédico realizada por el equipo de ingeniería del Sistema demostrativo de control automático en oxigenoterapia, como parte del módulo de adquisición de señales fisiológicas.  

Créditos adicionales:**  
- n-elia – Autor original del driver MAX30102 para MicroPython (2021).  
- Maxim Integrated – Fabricante del sensor MAX30102/MAX30105.  
