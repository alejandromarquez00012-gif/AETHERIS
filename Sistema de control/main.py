from machine import Pin
rangos = {"aceptable":{"min":95,"max":100},
          "regular":{"min":90,"max":95},
          "bajo":{"min":87,"max":90},
          "En riesgo":{"min":15,"max":87}}
#{"rx":"alarmas","aceptable":{"min":95,"max":100},"regular":{"min":90,"max":95},"bajo":{"min":87,"max":90},"En riesgo":{"min":15,"max":87}}
def alarmas_set(cmd):
    global rangos
    for clave, limites in rangos.items():
        rangos[clave] = cmd[clave]
def alarmas_print():
    for clave,limites in rangos.items():
        print(f"la clave es: {clave} y sus limites: {limites}")
def alarmas_on():
    None
def alarmas_off():
    None
def alarmas_config():
    None
