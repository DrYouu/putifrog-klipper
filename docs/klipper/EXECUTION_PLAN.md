# PLAN EJECUTIVO - Fase 2: Identificar Puerto MCU

## Estado Actual (2026-01-30, 18:35 UTC)

### Evidencia Recopilada
✅ Baseline remoto A13 capturado
✅ TTY devices mapeados (ttyS0-7, ttyGS0)
✅ dmesg analizado → STM32 USART driver confirmado
✅ Klipper status verificado (corriendo, sin config)
✅ No hay firmware Klipper compilado
✅ Escaneo M115 en ttyS1-7 → SIN RESPUESTA
✅ Búsqueda ttyUSB/ttyACM → NO ENCONTRADO

### Hallazgos Clave
1. **MCU es STM32**, no ATmega (confirmsdo por kernel)
2. **No responde en puertos serie estándar**
3. **Comunicación probable**: USB Gadget (ttyGS0), I2C, o socket interno

### Bloqueador Actual
🔒 **Necesita acceso sudo en A13 para**:
- Detener Klipper y liberar puerto
- Ejecutar i2cdetect
- Acceder a ttyGS0 (getty bloqueando)
- Ver permisos exactos de dispositivos

---

## PLAN A: Probar USB Gadget Serial (ttyGS0) - PRIORITARIO

### Comando a ejecutar EN A13 con sudo:
```bash
# 1. Parar getty que bloquea ttyGS0
sudo systemctl stop serial-getty@ttyGS0.service

# 2. Enviar M115 a ttyGS0
echo -e "M115" | timeout 1 cat > /dev/ttyGS0
timeout 0.5 cat /dev/ttyGS0

# 3. Análizar respuesta
# Esperado: "FIRMWARE_NAME:Marlin" o similar

# 4. Si funciona: reconfigurar Klipper
# No funciona: pasar a PLAN B
```

### Resultado Esperado
- **SI funciona**: Puerto = `/dev/ttyGS0`, baud = (USB, no relevante)
- **NO funciona**: Pasar a PLAN B

---

## PLAN B: Escanear I2C - SECUNDARIO

### Comandos a ejecutar EN A13 con sudo:
```bash
# Escanear todos los buses I2C
for i in 0 1 2; do
  echo "=== I2C Bus $i ===" 
  /usr/sbin/i2cdetect -y $i
done
```

### Resultado Esperado
- **Si hay dirección I2C activa** (ej: 0x68, 0x70): 
  - Puerto = `/dev/i2c-X` donde X es el bus
  - Dirección = la que aparece
- **Si está vacío**: Pasar a PLAN C

---

## PLAN C: Investigar Comunicación Interna - TERCIARIO

Si PLAN A y PLAN B fallan:
```bash
# Ver qué procesos/daemons corren en A13
ps aux | grep -E "mcu|motor|serial|bridge|daemon"

# Ver sockets Unix
netstat -an | grep -E "socket|unix"

# Buscar en código Klipper referencias a la conexión
grep -r "klippy.sock\|/dev/pts" ~/klipper ~/moonraker ~/printer_data
```

---

## Pasos DESPUÉS de Identificar Puerto

### 1. Copiar putifrog.cfg a A13 (versión actualizada para STM32)
```bash
scp putifrog_stm32.cfg olimex@192.168.0.13:~/printer_data/config/putifrog.cfg
```

### 2. Actualizar printer.cfg
```ini
[include putifrog_stm32.cfg]
[mcu]
serial: /dev/PUERTO_IDENTIFICADO  # ← Aquí va el resultado de PLAN A/B/C
baud: 250000  # O lo que corresponda
restart_method: command
```

### 3. Compilar firmware Klipper para STM32
```bash
ssh olimex@192.168.0.13
cd ~/klipper
make menuconfig
# Seleccionar: STM32, etc.
make clean && make
```

### 4. Flashear
```bash
cd ~/klipper
make flash FLASH_DEVICE=/dev/PUERTO
```

### 5. Verificar conexión
```bash
sudo systemctl start klipper
tail -f ~/printer_data/logs/klippy.log
# Buscar: "MCU 'mcu' identified"
```

---

## SIGUIENTE ACCIÓN DEL USUARIO

**URGENTE**: Acceder a A13 con permisos sudo y ejecutar PLAN A.

Opciones:
1. **SSH interactivo**:
   ```bash
   ssh olimex@192.168.0.13
   # Ingresar contraseña
   sudo su  # O ejecutar comandos con sudo
   ```

2. **Directamente en A13** (si tienes acceso físico):
   - Conectar monitor/teclado
   - Login como olimex
   - Ejecutar comandos

3. **En este repo local** (Windows):
   ```bash
   ssh -t olimex@192.168.0.13 'sudo /bin/bash'  # TTY interactivo
   # O esperar a tener contraseña
   ```

---

## Archivos Generados Hoy
- `evidence/2026-01-30/system_baseline_new.txt` - Info sistema
- `evidence/2026-01-30/tty_devices.txt` - Puertos serie
- `evidence/2026-01-30/dmesg.txt` - Kernel messages
- `evidence/2026-01-30/klippy_log.txt` - Errores Klipper  
- `evidence/2026-01-30/i2c_scan.txt` - Intento I2C (error permisos)
- `evidence/2026-01-30/CRITICAL_ANALYSIS.md` - Análisis de hallazgos
- `notes/todo/NEXT_STEPS_SUDO_REQUIRED.md` - Pasos siguientes detallados

---

## Siguiente Sesión
Una vez ejecutado PLAN A/B/C y teniendo el puerto identificado:
1. Actualizar putifrog_stm32.cfg
2. Compilar firmware Klipper
3. Flashear
4. Verificar + Calibrar

**Tiempo estimado**: 30-45 minutos (sin incidentes)

