def control_flujo(adc, pwm, r, cmd):
    VMAX_o2 = 1.56   # 0 L/min
    VMIN    = 1.4   # 15 L/min
    
    #PI
    KP_f    = 3.894026662
    KI_TS_f = 0.1678643955
    # PID
    KP_spo2    = 3.894026662
    KI_TS_spo2 = 0.1678643955
    KD_div_TS_spo2 = 0.0
    
    st = control_flujo
    if not hasattr(st, "u1"):
        st.u1 = 0.0
    if not hasattr(st, "e1"):
        st.e1 = 0.0
    if not hasattr(st, "e2"):
        st.e2 = 0.0
    if not hasattr(st, "e3"):
        st.e3 = 0.0
        
    # Promedio
    v_sum = 0.0
    y_sum = 0.0
    for _ in range(20):
        raw16 = adc.read() * 16
        v = raw16 * 4.1 / 65535.0

        if v < VMIN:       v_med = VMIN
        elif v > VMAX_o2:  v_med = VMAX_o2
        else:              v_med = v

        t = (v_med - VMIN) / (VMAX_o2 - VMIN)
        y_i = 15.8 + t * (0.0 - 15.8)

        if y_i < 0.0:   y_i = 0.0
        if y_i > 15.0:  y_i = 15.0

        v_sum += v
        y_sum += y_i
        
    y_prom = y_sum / 20.0

    # --------- Control ----------
    e0 = r - y_prom

    if cmd == 'f': #Flujo
        u0 = st.u1 + KP*(e0 - st.e1) + KI_TS*e0
    elif cmd == 's' #SpO2
        u0 = st.u1 + KP*(e0 - st.e1) + KI_TS*e0 + KD_div_TS*(e0 - 2*st.e1 + st.e2)

    if u0 < 0.0:
        u = 0.0
    elif u0 > 1.0:
        u = 1.0
    else:
        u = u0

    pwm.duty_u16(int(u * 65535))

    # Actualiza estados anteriores
    st.u1 = u
    st.e3, st.e2, st.e1 = st.e2, st.e1, e0
    
    return y_prom