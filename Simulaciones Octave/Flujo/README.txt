README — Sistema de modelado y control de flujo

Este repositorio incluye tres scripts en Octave/MATLAB para analizar y simular un sistema de flujo neumático. Cada archivo cumple un propósito diferente: obtener el modelo discreto a partir de datos reales, validar su función de transferencia y simular un controlador PID digital.

minimos_cuadrados_flujo.m

Lee un archivo de texto con tiempo y voltaje registrados del sensor.
Escala el voltaje al rango físico de flujo (0–15 L/min).
Calcula un modelo discreto de primer orden mediante mínimos cuadrados:

y[k] = a1 * y[k-1] + b0 * u[k-1]

Muestra los valores de a1 y b0.
Grafica: datos medidos vs. modelo estimado.
Uso: obtener el comportamiento dinámico real del sensor.

FT_flujo_LA.m

Usa a1 y b0 para definir la función de transferencia discreta:
G(z) = b0 / (1 - a1*z^-1)
Simula una respuesta al escalón.
Grafica la salida en función del tiempo (muestras).
Uso: verificar la dinámica del sistema y su estabilidad.

Simulacion_control_flujo.m

Simula el sistema con un controlador PID discreto.
Implementa el PID en forma incremental:
u[k] = u[k-1] + r0e[k] + r1e[k-1] + r2*e[k-2]
Calcula el error, la señal de control y la salida de la planta.
Grafica la respuesta a una referencia y la acción de control.
Uso: evaluar el desempeño del PID antes de implementarlo en hardware real.
Flujo recomendado:
Ejecutar minimos_cuadrados_flujo.m → obtener modelo.
Ejecutar FT_flujo_LA.m → validar comportamiento.
Ejecutar Simulacion_control_flujo.m → probar controlador.