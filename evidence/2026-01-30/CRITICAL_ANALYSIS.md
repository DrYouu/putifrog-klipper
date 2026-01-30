# ANÁLISIS CRÍTICO: Puerto MCU - 2026-01-30

## Evidencia Recopilada

### 1. **Escaneo M115 - Resultado: SIN RESPUESTA en ttyS1-7**
- Archivo: `serial_scan_result.txt`
- Todos los puertos ttyS1-7 retornaron `ERR_OPEN` (28 intentos combinados)
- Conclusión: MCU NO está en puertos ttyS estándar, O los permisos son insuficientes

### 2. **Búsqueda de dispositivos USB - Resultado: VACÍO**
```bash
$ ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
→ NO_USB_DEVICES
```
- Conclusión: No hay adaptador USB-Serial activo

### 3. **dmesg - Hallazgo CRÍTICO**
```
[    1.368133] STM32 USART driver initialized
```
- **Evidencia**: Kernel carga driver STM32, no ATmega
- Archivo: `dmesg.txt`
- Conclusión: **MCU real es STM32**, no ATmega1280/2560 (putifrog.cfg es INCORRECTO)

### 4. **Klipper Log - Configuración Placeholder**
```
mcu 'mcu': Unable to open serial port: [Errno 2] ... '/dev/serial/by-id/<your-mcu-id>'
No build file /home/olimex/klipper/klippy/../.config
No build file /home/olimex/klipper/klippy/../out/klipper.elf
```
- Archivo: `klippy_log.txt`
- Conclusiones:
  1. Configuración tiene placeholder (no ha sido configurada)
  2. NO HAY firmware Klipper compilado para ningún MCU

### 5. **Hardware Confirmado**
- **Placa Host**: Olimex A13-SOM-512 (Allwinner A13, ARMv7, Debian 11)
- **MCU**: STM32 (confirmado por kernel STM32 USART driver)
- **Puertos disponibles**: ttyS0-7 (8 UARTs @ 16550A driver), NO_USB

---

## PROBLEMA IDENTIFICADO

**Discrepancia Critical**:
- `putifrog.cfg` asume ATmega1280/2560 @ 250000 baud 
- Kernel STM32 driver sugiere MCU es STM32
- **Hipótesis**: Archivo putifrog.cfg es de configuración anterior (Leapfrog Creatr HS original), pero esta impresora tiene hardware diferente (STM32 en lugar de ATmega)

**Segunda Discrepancia**:
- No hay respuesta M115 en puertos serie estándar
- Podría ser:
  1. Puerto es I2C, no UART (STM32 puede ser esclavo I2C)
  2. Comunicación es socket/interna (gestor daemon)
  3. Puerto es GPIO/SPI (no UART)
  4. Permisos/grupo incorrecto para acceder al puerto

---

## ESTRATEGIA DE CONTINUACIÓN

### Fase A: Investigar I2C (PROBABLE)
STM32 es compatible con I2C. La placa de motores podría estar en bus I2C.

**Comandos**:
```bash
# En A13:
i2cdetect -y 0  # Detectar dispositivos en bus I2C-0
i2cdetect -y 1  # Detectar dispositivos en bus I2C-1
i2cdetect -y 2  # Detectar dispositivos en bus I2C-2
```

**Esperado**: Dirección I2C (ej: 0x68, 0x70, etc.)
**Acción siguiente**: Configurar Klipper con `serial: /dev/i2c-X` y dirección

### Fase B: Investigar socket/daemon internal
De sesión anterior se vio que klippy.serial apunta a /dev/pts/0 (pseudo-TTY), no a UART real.

**Comandos**:
```bash
netstat -an | grep -i socket  # Ver sockets Unix
lsof /home/olimex/printer_data/comms/klippy.sock  # ¿Quién conecta?
ps aux | grep -E "mcu|serial|bridge|motor"  # Buscar daemon gestor
```

### Fase C: Recompilação de putifrog.cfg
Actualizar asunciones de ATmega a STM32.

---

## PRÓXIMA ACCIÓN INMEDIATA

**Usuario/Operador debe ejecutar en A13**:

1. **Instalar herramienta I2C** (si no existe):
   ```bash
   sudo apt-get install i2c-tools
   ```

2. **Detectar dispositivos I2C**:
   ```bash
   for i in 0 1 2; do echo "=== I2C Bus $i ==="; i2cdetect -y $i; done
   ```

3. **Verificar permisos de puertos**:
   ```bash
   stat /dev/ttyS[1-3]  # Ver propietario/grupo
   id  # Ver grupos de usuario olimex
   ```

4. **Copiar outputs** a `evidence/2026-01-30/` para análisis

---

## Bloqueadores Actuales

- ❌ Contraseña de `olimex` no disponible (necesaria para `sudo systemctl stop klipper`)
- ❌ Permisos del usuario `olimex` en puertos ttyS* (¿en grupo dialout correctamente?)
- ❌ Tipo de conexión MCU desconocido (UART/I2C/Socket/GPIO)
- ❌ MCU tipo desconocido (ATmega vs STM32 actual)

