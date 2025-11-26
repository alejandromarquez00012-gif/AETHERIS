clear all
close all
file_path = "C:\\Users\\aleja\\OneDrive\\Desktop\\Integrador\\Adquisición de datos\\datos_spo2.txt";

fid = fopen(file_path, "r");
if fid < 0
    error("No pude abrir el archivo");
end

t_ms  = [];
spo2v = [];

while true
    ln = fgetl(fid);
    if ~ischar(ln)
        break;
    end

    ln_clean = strrep(ln, "ms", "");

    partes = strsplit(ln_clean, ",");

    if numel(partes) >= 2

        t_val    = str2double(strtrim(partes{1}));
        spo2_val = str2double(strtrim(partes{2}));

        if !isnan(t_val) && !isnan(spo2_val)
            t_ms(end+1)  = t_val;
            spo2v(end+1) = spo2_val;
        end
    end
end

fclose(fid);

spo2_min = min(spo2v);
spo2_max = max(spo2v);

fprintf("SpO2 mínima: %.1f %%\n", spo2_min);
fprintf("SpO2 máxima: %.1f %%\n", spo2_max);

figure;
plot(t_ms, spo2v, 'b', 'LineWidth', 1.2);
xlabel('Tiempo [ms]');
ylabel('SpO2 [%]');
title('SpO2 en función del tiempo');
grid on;


y = spo2v(:);
u = ones(size(y));

N = length(y);
Phi = [y(1:N-1), u(1:N-1)];
Yv  = y(2:N);

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
ylabel('SpO2 [%]');
title('Ajuste discreto por mínimos cuadrados (G(z))');
legend('Datos medidos','Modelo estimado');
