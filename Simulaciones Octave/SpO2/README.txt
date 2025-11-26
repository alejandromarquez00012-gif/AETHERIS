README — Sistema de modelado y control de SpO₂

Este repositorio incluye dos scripts en Octave/MATLAB para analizar y simular un sistema biomédico basado en la señal de saturación de oxígeno (SpO₂).
Cada archivo cumple un propósito diferente: obtener el modelo discreto a partir de datos reales y simular un controlador PID digital sobre esa planta.

**minimos_cuadrados_spo2.m**

* Lee un archivo de texto con tiempo (ms) y valores de SpO₂ medidos.
* Extrae los valores y calcula el rango observado.
* Ajusta un modelo discreto de primer orden mediante mínimos cuadrados:


y[k] = a1 \cdot y[k-1] + b0 \cdot u[k-1]


* Muestra los valores obtenidos de `a1` y `b0`.
* Grafica:

  * Datos medidos de SpO₂
  * Modelo ajustado (estimación)

**Uso:** obtener el comportamiento dinámico aproximado del sistema SpO₂ medido.


 **Simulacion_PID_SpO2.m**

* Simula el sistema SpO₂ usando un controlador PID digital en forma incremental.
* Implementa el PID:

u[k] = u[k-1] + r0,e[k] + r1,e[k-1] + r2,e[k-2]

* Calcula:

  * error entre referencia y salida,
  * señal de control,
  * evolución de la planta.

* Grafica:

  * Respuesta del sistema vs referencia,
  * Señal de control generada por el PID.

**Uso:** evaluar el desempeño del controlador antes de aplicarlo a hardware real.

 **Flujo recomendado**

1. Ejecutar **minimos_cuadrados_spo2.m** → obtener los parámetros `a1` y `b0`.
2. Insertar esos valores en **Simulacion_PID_SpO2.m**.
3. Ajustar las ganancias PID hasta lograr estabilidad y error aceptable.
