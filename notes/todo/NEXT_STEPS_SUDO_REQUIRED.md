# PROCEDIMIENTO VERIFICACIÓN MCU - Requiere Acceso Sudo

## Objetivo
Identificar puerto y protocolo real entre A13 ↔ Placa Motores (STM32)

## Bloqueador Actual
El usuario `olimex` no tiene acceso sudo sin contraseña para:
- Detener Klipper (`systemctl stop klipper`)
- Ejecutar i2cdetect (requiere permisos root)
- Ver lsof de procesos
- Acceder a puertos serie ocupados

## Solución: Dos Opciones

### OPCIÓN A: Acceso SSH Interactivo con Contraseña
```bash
ssh olimex@192.168.0.13
# Ingresa contraseña cuando se pida
```

Luego ejecuta (dentro de la sesión SSH):
```bash
# 1. Verifica acceso sudo
sudo -l

# 2. Busca port serie placa motores
sudo lsof +D /dev 2>/dev/null | grep -E 'ttyS|ttyUSB|ttyACM'

# 3. Escanea buses I2C
sudo /usr/sbin/i2cdetect -y 0
sudo /usr/sbin/i2cdetect -y 1
sudo /usr/sbin/i2cdetect -y 2

# 4. Verifica en dmesg si hay info de motor/STM32
sudo dmesg | grep -i "motor\|stm32\|atmega"

# 5. Lista procesos que usan puertos
sudo lsof -i :250000 -i :115200
```

### OPCIÓN B: Script Bash Remoto (no requiere TTY interactivo)
Si tienes sudoers configurado sin contraseña, ejecuta:
```bash
ssh olimex@192.168.0.13 'sudo bash' << 'EOF'
echo "=== Información de Dispositivos ===" 
lsof +D /dev 2>/dev/null | grep -E 'ttyS|ttyUSB'
echo "=== I2C Bus 0 ===" 
/usr/sbin/i2cdetect -y 0
echo "=== I2C Bus 1 ===" 
/usr/sbin/i2cdetect -y 1
echo "=== I2C Bus 2 ===" 
/usr/sbin/i2cdetect -y 2
echo "=== Kernel Messages STM32 ===" 
dmesg | grep -i stm32
EOF
```

## Pasos Posteriores (Una Vez Identificado Puerto)

### Si el resultado es `HIT` en I2C (ej: dirección 0x68)
1. Configurar Klipper:
   ```ini
   [mcu]
   serial: /dev/i2c-0
   # O los que correspondan
   ```
2. Compilar firmware Klipper para STM32 (no ATmega)

### Si el resultado es `HIT` en ttyUSB/ttyACM
1. Nota el puerto exacto
2. Configurar Klipper:
   ```ini
   [mcu]
   serial: /dev/ttyUSB0
   baud: 250000
   ```

### Si NO hay respuesta en ningún método
- Podría ser comunicación por socket/daemon interno
- Requiere análisis más profundo del hardware de la impresora

## Archivos de Evidencia Generados
- `system_baseline_new.txt` - info sistema
- `tty_devices.txt` - puertos serie disponibles
- `dmesg.txt` - kernel messages (incluye STM32 USART driver)
- `klippy_log.txt` - error Klipper (placeholder config)
- `CRITICAL_ANALYSIS.md` - análisis de hallazgos

