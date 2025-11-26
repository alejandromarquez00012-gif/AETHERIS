from machine import Pin

#{"rx":"sistema"}
estado = False

def toggle_estado():
    global estado
    estado = not estado
    

