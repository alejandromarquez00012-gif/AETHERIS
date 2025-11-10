def leer_spo2():
    # Inicializar
    st = leer_spo2
    if not hasattr(st, "sensor"):
    
        st.lista = []
        st.ventana = 10
        st.ventana2 = 100

        # inicializa I2C y sensor
        i2c = SoftI2C(sda=Pin(6), scl=Pin(7), freq=400000)
        st.sensor = MAX30102(i2c=i2c)

        # verificar
        if (st.sensor.i2c_address not in i2c.scan()) or (not st.sensor.check_part_id()):
            st.on = False
            return "Sensor no funciona"
        else:
            st.on = True
            st.sensor.setup_sensor()
            st.sensor.set_sample_rate(3200)
            st.sensor.set_fifo_average(32)
            st.sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

    # retorna none si el sensor no jala
    if not st.on:
        return "Sensor no funciona"

    # Lee
    st.sensor.check()
    if st.sensor.available():
        red = st.sensor.pop_red_from_storage()

        st.lista.append(red)
        st.ventana_red.append(red)
        if len(st.ventana_red) > st.ventana2:
            st.ventana_red.pop(0)  

        # Norma 2
        if len(st.lista) >= st.ventana:
            prom = (math.sqrt(sum(x*x for x in st.lista))) / len(st.lista)
            spo2 = 0.12698 * prom + 79.82
            st.lista.clear
            return round(spo2, 1)

    return "Datos insuficientes"
