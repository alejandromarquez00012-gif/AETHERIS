Generador de onda senoidal de 8 bits con amplitud adaptable a partir de una lectura ADC tomada exactamente cada 1 s usando la interrupción del Timer1 (sin auto-trigger del ADC).  
La forma de onda se reproduce con el Timer2, mediante interrupciones periódicas, entregando una senoide de ~50 Hz en el puerto de salida.

> Microcontrolador: ATmega328P @ 16 MHz  
> Lenguaje: C (avr-gcc)  
> Periféricos usados: DAC0800

---

## Descripción general

El programa genera una onda senoidal continua cuya amplitud varía en función de la lectura analógica del ADC (canal 0).  
Cada segundo, el Timer1 ejecuta una lectura ADC y recalcula la amplitud de la señal senoidal.  
El Timer2 se encarga de reproducir la tabla seno punto por punto, enviando los valores al puerto PORTD.


## Funcionamiento interno

1. Timer1 (1 Hz):  
   Dispara cada segundo una conversión ADC por software.  
   Calcula la amplitud según:  
   `Amplitud = 0.0293 * ADC + 20`,  
   limitando el resultado entre 20 y 50.

2. Tabla seno:* 
   Contiene 129 valores (8 bits, centrados en 128).  
   Se generan dos tablas (`Senofinal[i][0]` y `[i][1]`) para alternar medio-ciclos.

3. Timer2 (~12.82 kHz):  
   Actualiza el puerto de salida (`PORTD`) recorriendo la tabla seno.  
   Una senoide completa se forma con 254 muestras (≈ 50 Hz de frecuencia de salida).

4. Salida:
   El puerto PORTD entrega los valores de 8 bits.  


## Detalles de temporización

| Elemento | Configuración | Frecuencia resultante |
|-----------|----------------|-----------------------|
| Timer1 | Prescaler 1024, OCR1A = 15624 | 1 Hz (control ADC) |
| Timer2 | Prescaler 32, OCR2A = 38 | 12.82 kHz (muestreo seno) |

## Principales funciones

- CONFIG_ADC()  
  Configura el ADC en modo simple con referencia AVcc, prescaler = 128.

- CONFIG_TIMER1_1Hz() 
  Configura el Timer1 en modo CTC para generar una interrupción cada segundo.

- CONFIG_TIMER2()  
  Configura el Timer2 para generar interrupciones periódicas de muestreo.

- ISR(TIMER1_COMPA_vect)  
  Ejecuta la lectura ADC, calcula la nueva amplitud y actualiza las tablas seno.

- ISR(TIMER2_COMPA_vect) 
  Envía los valores del seno a `PORTD`, alternando entre los dos medio-ciclos.


## Lógica matemática

Senofinal[i][0] = ((Seno[i] - 128) * Amplitud / 50) + 128
Senofinal[i][1] = 128 - ((Seno[i] - 128) * Amplitud / 50)

Esto produce dos ondas simétricas con amplitud dependiente de la señal analógica.


## Conexiones recomendadas

| Pin | Función | Descripción |
|-----|----------|-------------|
| PC0 (ADC0) | Entrada analógica | Lectura de nivel analógico (0–5 V) |
| PORTD[0:7] | Salida digital | Señal de 8 bits senoidal |
| AVcc / ARef | Referencia del ADC | 5 V |
| GND | Tierra común | — |



## Fórmulas útiles

Frecuencia de seno de salida:  
`f_seno = (F_CPU / (prescaler * (OCR2A + 1))) / 254`

Para cambiar la frecuencia, modifica **OCR2A** o el prescaler del Timer2.


## Compilación y carga

Requisitos:
- avr-gcc y avr-libc
- avrdude (para grabar el programa)

Comandos:

```bash
avr-gcc -mmcu=atmega328p -DF_CPU=16000000UL -Os -o main.elf Seno_leds_adc_1s_timer.c
avr-objcopy -O ihex -R .eeprom main.elf main.hex
avrdude -c usbasp -p m328p -U flash:w:main.hex:i

