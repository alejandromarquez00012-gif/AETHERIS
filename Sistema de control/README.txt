README
main.py

Punto de entrada del firmware.
Inicializa pines, PWM, ADC, alarmas y sensor de SpO₂.
Configura interrupciones para:

  `Btn_on_off`, `Btn_enter`, encoder (`Btn_D` + `Btn_clk`).
Configura un `Timer` periódico (50 ms) para enviar telemetría.
En el bucle principal:

   Lee comandos JSON por serie (`serial_reader.leer_cmd()`).
   Despacha los comandos a:

     `"sistema"` → módulo `sistema`
     `"control"` → módulo `control`
     `"alarmas"` → módulo `alarmas`
   Procesa giros del encoder y envía `{"focus": ...}` a la HMI.
   Si el sistema está encendido:

     Lee flujo (`control.leer_flujo()`) y SpO₂ (`control.leer_spo2()`).
     Ejecuta el control PID (`control.control_variable()`).
     Envía cada 50 ms:
      `{"control":{"flujo":..., "spo2":..., "error":...}}`.

Uso: orquestar todo el sistema de medición, control y comunicación.


control/control.py**

 Administra referencias y ganancias PID para flujo y SpO₂.
 Recibe comandos JSON del tipo:

   `{"rx":"control","flujo":{...}}`
   `{"rx":"control","spo2":{...}}`
 `parametros_set()`:

   Actualiza `kp`, `ki`, `kd` y referencias.
   Escala ganancias según rango (alto/medio/bajo) y nivel de SpO₂.
 `control_variable(pwm, _flujo, _spo2)`:

   Modo flujo: PID con salida normalizada a [0,1] → `duty_u16`.
   Modo SpO₂: PID con integración y derivada, saturación 0–100 %, mapeo a duty.
   Devuelve el error actual.
 `leer_flujo(adc)`:

   Promedia 50 lecturas tipo RMS.
   Convierte ADC → L/min mediante una regresión lineal.
 `leer_spo2()` / `init_control()`:

   Envoltorios hacia `_apoyo_control` para configurar y leer el MAX30102.

Uso: núcleo del control en lazo cerrado para flujo y SpO₂.

control/_apoyo_control.py**

 Manejo de sensor MAX30102 y filtrado de SpO₂.
 `config_spo2()`:

   Inicializa I²C, verifica el sensor, configura tasa de muestreo y promedio.
 `leer_spo2()`:

   Lee muestras RED del MAX30102.
   Calcula un valor tipo RMS en ventana.
   Aplica una regresión lineal → SpO₂.
   Filtra con un filtro exponencial.
   Devuelve SpO₂ filtrada (o `None` si aún no hay datos).

Uso: obtener una medición de SpO₂ estable y utilizable para control.

sistema/IO.py

 Abstracción de todos los pines del microcontrolador.
 `init_pines()`:

   Configura botones, ADC, PWM de válvula, LEDs de alarmas y buzzer.
 `init_irq(nombre, handler)`:

   Asocia interrupciones a botones (`Btn_on_off`, `Btn_enter`, `Btn_D`).
 `antirrebote(nombre, intervalo_ms)`:

   Antirrebote por software usando `ticks_ms`.
 `encoder_procesar()`:

   Lee `Btn_clk` y devuelve:

     `{"focus": "arriba"}` o `{"focus": "abajo"}`.
 Utilidades:

   `get_pwm()`, `set_pwm(value)`, `get_adc()`.
   `get_alarmas()` → devuelve pines de LEDs y buzzer.

Uso: capa de hardware para que el resto del código no dependa de números de pin.

sistema/alarmas.py

 Gestiona LEDs de estado y buzzer según SpO₂.
 `rangos` define umbrales: aceptable, regular, bajo, riesgo, mínimo.
 `alarmas_set(cmd)`:

   Actualiza rangos desde un comando JSON (`"rx":"alarmas"`).
 `clasificar_spo2(spo2)`:

   Devuelve un estado: `"aceptable"`, `"regular"`, `"bajo"`, `"riesgo_buzzer"` o `"apagado"`.
 `actualizar_alarmas(spo2)`:

   Cambia LEDs y buzzer solo cuando el estado de alarma cambia.
 `alarma_on()` / `alarmas_off()`:

   Encienden/apagan LEDs y definen buzzer suave o fuerte.

Uso: indicar visual y acústicamente el estado clínico estimado del paciente/simulación.

sistema/serial_reader.py

 Implementa la comunicación serie basada en JSON entre microcontrolador y Raspberry Pi.
 `capturar_cmd()`:

   Lectura no bloqueante de `stdin` (uso de `uselect.poll`).
   Devuelve `None` si no hay datos o un dict decodificado si el JSON es válido.
 `leer_cmd()`:

   Filtra y solo entrega comandos que contienen `"rx"`.
 `send_cmd(cmd)`:

   Imprime el diccionario como JSON (respuesta o telemetría).

Uso: canal de intercambio de comandos y datos con la HMI.

sistema/sistema.py

 Gestiona el estado global del sistema.
 Variable global `estado` (`True` = encendido, `False` = apagado).
 `toggle_estado()`:

   Cambia el estado; se usa desde `main` cuando se presiona `Btn_on_off`.

Uso: habilitar/deshabilitar el funcionamiento general del lazo de control.

max30102/init.py y **max30102/circular_buffer.py

 Implementan el driver del sensor MAX30102:

  Configuración de registros, FIFO, modos de LED y lectura de muestras.
 `CircularBuffer`:

   Buffer circular simple para almacenar lecturas recientes.

Uso: capa de bajo nivel para acceder al sensor de SpO₂.

Flujo recomendado

1. Configurar hardware y sensor llamando a:

    `io.init_pines()`
    `al.pin_set()`
    `cl.init_control()`
2. Desde la HMI, enviar:

    Comandos `"control"` para fijar referencias y ganancias.
    Comandos `"alarmas"` para ajustar umbrales de SpO₂.
3. Encender el sistema con el botón ON/OFF → `sistema.estado = True`.
4. Monitorear por serie:

    `{"control":{"flujo":..., "spo2":..., "error":...}}`
5. Ajustar ganancias y rangos hasta lograr respuesta estable y alarmas coherentes.
