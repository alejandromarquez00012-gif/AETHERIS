from machine import Pin, ADC
import time
import json #JavaScript Object Notation
#import json se usa para convertir un diccionario (o listas, números, etc) de Python en una cadena de texto con formato JSON, que después se envía por el puerto serie (UART)
#Qué es un diccionario? es un tipo de dato que guarda información en pares clave–valor, parecido a un “diccionario real” por ejemplo 'spo2': 95.4, 'flujo': 7.25

# ----------- CONFIGURACIÓN DE LOS ADC -----------
adc_spo2 = ADC(Pin(0))   # Potenciómetro 1 -> SpO2
adc_flujo = ADC(Pin(1))  # Potenciómetro 2 -> Flujo

adc_spo2.atten(ADC.ATTN_11DB)   # rango 0–3.3 V (en ESP32)
adc_flujo.atten(ADC.ATTN_11DB)

# ----------- CONSTANTES DE CALIBRACIÓN -----------
VMAX_SPO2  = 2.66   # voltaje máximo real para el pot de SpO2
VMAX_FLUJO = 2.66   # voltaje máximo real para el pot de Flujo
VMIN       = 0.00   # offset en caso de que el cero no sea 0 V

# ----------- FUNCIONES AUXILIARES -----------
def leer_adc_volts(adc):
    """Lee el ADC en voltios (0–3.3 V nominal)"""
    return adc.read() * 3.3 / 4095   # 12 bits en MicroPython/ESP32

def mapear(x, in_min, in_max, out_min, out_max):
    """Mapea el valor x de un rango de entrada a uno de salida"""
    if x < in_min:
        x = in_min
    if x > in_max:
        x = in_max
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def leer_promedio(func, muestras=10):
    """Promedia varias lecturas para mayor estabilidad"""
    return sum(func() for _ in range(muestras)) / muestras

# ----------- BUCLE PRINCIPAL -----------
while True:
    # Lee y promedia los dos canales
    v_spo2  = leer_promedio(lambda: leer_adc_volts(adc_spo2))
    v_flujo = leer_promedio(lambda: leer_adc_volts(adc_flujo))

    # Mapea a % y L/min usando los máximos medidos
    spo2_pct  = mapear(v_spo2, VMIN, VMAX_SPO2, 0.0, 100.0)
    flujo_lm  = mapear(v_flujo, VMIN, VMAX_FLUJO, 0.0, 15.0)

    #json.dumps(obj): convierte un objeto de Python (diccionario, lista, números, etc.) en una cadena de texto JSON. en este caso nuestro diccionario se spo2 y flujo se vuelve una cadena por json
    #Las claves ("spo2" y "flujo") son cadenas.
    #qué es una clave? la clave es el nombre o identificador único que sirve para acceder a su valor correspondiente. en este caso "spo2" y "flujo" son las claves
    #el valor es lo que viene después de ":" 
    
    #Los valores son números ya redondeados:
        #round(spo2_pct, 1) → un decimal, por ejemplo 95.4
        #round(flujo_lm, 2) → dos decimales, por ejemplo 7.25
    
    print(json.dumps(
        {
        "spo2":  round(spo2_pct, 1),
        #La función round() sirve para redondear números en Python.
        "flujo": round(flujo_lm, 2)
        }
        ))
    #El print(...) manda esa cadena JSON por el puerto serie (la salida estándar de MicroPython).
    #La Raspberry Pi, ejecutando tu código en VS Code, lee la línea completa, por ejemplo: {"spo2": 95.4, "flujo": 7.25}


    time.sleep(0.3)   # refresco cada 0.3 s}hh
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    