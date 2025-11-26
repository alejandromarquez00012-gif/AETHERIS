clear all
file_path = "C:\\Users\\aleja\\OneDrive\\Desktop\\Integrador\\Adquisición de datos\\datos_flujo.txt";

fid = fopen(file_path, "r");
if fid < 0
    error("No pude abrir el archivo");
end


t_ms = [];
v_volt = [];

while true
    ln = fgetl(fid);
    if ~ischar(ln)
        break;
    end


    ln_clean = strrep(ln, "ms", "");
    ln_clean = strrep(ln_clean, "V", "");

    partes = strsplit(ln_clean, ",");

    if numel(partes) >= 3

        t_val = str2double(strtrim(partes{1}));
        v_val = str2double(strtrim(partes{3}));

        if !isnan(t_val) && !isnan(v_val)
            t_ms(end+1) = t_val;
            v_volt(end+1) = v_val;
        end
    end
end

fclose(fid);

v_min = min(v_volt);
v_max = max(v_volt);

flujo_lpm = 15 * (v_volt - v_min) / (v_max - v_min);

fprintf("Voltaje mínimo: %.3f V\n", v_min);
fprintf("Voltaje máximo: %.3f V\n", v_max);
fprintf("Rango escalado a 0–15 L/min\n");

figure;
plot(t_ms, flujo_lpm, 'b', 'LineWidth', 1.2);
xlabel('Tiempo [ms]');
ylabel('Flujo [L/min]');
title('Flujo en función del tiempo');
grid on;

y = v_volt(:);
u = ones(size(y));

N = length(y);
Phi = [y(1:N-1), u(1:N-1)];
Yv = y(2:N);

theta = (Phi' * Phi) \ (Phi' * Yv);
a1 = theta(1);
b0 = theta(2);

fprintf('Modelo discreto (un polo, sin ceros):\n');
fprintf('G(z) = %.6f / (1 - %.6f z^-1)\n', b0, a1);
fprintf('Ecuación de diferencia: y[k] = %.6f*y[k-1] + %.6f*u[k-1]\n', a1, b0);

y_est = filter(b0, [1, -a1], u);

figure;
plot(y, 'b'); hold on;
plot(y_est, 'r--', 'LineWidth', 1.5);
grid on;
xlabel('Muestras');
ylabel('Voltaje (V)');
title('Ajuste discreto por mínimos cuadrados (G(z))');
legend('Datos medidos','Modelo estimado');


