from machine import Pin
import sistema.IO as io
# rangos = {"aceptable":{"rango":98,"estado":False},
#           "regular":{"rango":95,"estado":False},
#           "bajo":{"rango":93,"estado":False},
#           "riesgo":{"rango":88,"estado":False},
#           "minimo":{"rango":85,"estado":False}
#           }
rangos = {"aceptable":98,
          "regular":95,
          "bajo":93,
          "riesgo":92,
          "minimo":80
          }
alarmas = {}
#{"rx":"alarmas","aceptable":0,"regular":0,"bajo":0,"riesgo":0,"minimo":0}
valor = 0
def alarmas_set(cmd):
    global rangos
    for clave in rangos.keys():
        rangos[clave] = cmd[clave]
#     alarmas_print()
        
def pin_set():
    global alarmas
    alarmas = io.get_alarmas()
    #print(alarmas)
    
def alarmas_print():
    for clave,limites in rangos.items():
        print(f"la clave es: {clave} y sus limites: {limites}")
estado_alarma = None  # global
def clasificar_spo2(spo2):
    if spo2 > rangos["regular"]:
        return "aceptable"
    elif spo2 > rangos["bajo"]:
        return "regular"
    elif spo2 > rangos["riesgo"]:
        return "bajo"
    elif spo2 > rangos["minimo"]:
        return "riesgo_buzzer"
    else:
        return "apagado"
def actualizar_alarmas(spo2):
    global estado_alarma

    nuevo_estado = clasificar_spo2(spo2)

    # Si no cambió el estado, no toques el hardware
    if nuevo_estado == estado_alarma:
        return

    estado_alarma = nuevo_estado

    # Apaga todo primero
    alarmas_off()

    # Enciende según el estado
    if nuevo_estado == "aceptable":
        alarma_on("aceptable")

    elif nuevo_estado == "regular":
        alarma_on("regular")

    elif nuevo_estado == "bajo":
        alarma_on("bajo")
        alarma_on("buzzer", False)   # buzzer suave

    elif nuevo_estado == "riesgo_buzzer":
        alarma_on("buzzer", True)    # buzzer fuerte
        alarma_on("riesgo")


def alarma_on(alarma,b = False):
    if alarma == "buzzer" and b:
        #alarmas[alarma].freq(60)
        alarmas[alarma].duty_u16(65534)
    elif alarma == "buzzer" and not b:
        alarmas[alarma].duty_u16(30000)
    else:
        alarmas[alarma].value(1)
    #print(f"se activo {alarma}")


def alarmas_off():
    for nombre, dev in alarmas.items():
        if nombre == "buzzer":
            dev.duty_u16(0)      # apagar buzzer
        else:
            dev.value(0)         # apagar LEDs / demás salidas
