from machine import Pin, PWM
import time

pines = {
    "1":Pin(2,Pin.OUT),
    "2":Pin(11,Pin.OUT),
    "3":Pin(10,Pin.OUT),
    "4":Pin(1,Pin.OUT),
#     "5":PWM(Pin(0))
    "5":Pin(0,Pin.OUT)
    }

#11
#10
#1

# pines["5"].duty_u16(30000)
# pines["5"].freq(2)
for pin in pines.values():
    pin.value(1)
    time.sleep(1)
    pin.value(0)
    time.sleep(1)