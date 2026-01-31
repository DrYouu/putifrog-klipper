# DIAGNÓSTICO UART/MARLIN - 31 de Enero de 2026

## Resultado de Escaneo UART

### Pruebas Realizadas

| Puerto | Baudrates Probados | Respuestas M115 | Estado |
|--------|-------------------|-----------------|--------|
| ttyS1 | 115200, 57600, 38400, 19200, 9600 | Ninguna | ✗ VACÍO |
| ttyS2 | 115200, 57600, 38400, 19200, 9600 | Ninguna | ✗ VACÍO |
| ttyS3 | 115200, 57600, 38400, 19200, 9600 | Ninguna | ✗ VACÍO |

**Conclusión del Escaneo**: No hay respuesta Marlin en los puertos UART serie estándar accesibles.

---

## Análisis del Sistema

### Estado Actual de Klipper

```
Proceso: RUNNING (PID 502)
Configuración: /home/olimex/printer_data/config/printer.cfg
Estado conexión MCU: ✗ FALLO (repeated)
```

### Configuración printer.cfg

```ini
[mcu]
serial: /dev/serial/by-id/<your-mcu-id>
```

**⚠️ PROBLEMA CRÍTICO**: Configuración tiene **placeholder sin resolver**.
- Esperado: `/dev/serial/by-id/usb-EMPRESA_DISPOSITIVO_SERIALNUMBER-if00` (ejemplo)
- Actual: Literal `<your-mcu-id>` (nunca fue configurado)

### Error en Klipper Log

```
mcu 'mcu': Unable to open serial port: [Errno 2] could not open port 
/dev/serial/by-id/<your-mcu-id>: No such file or directory
```

**Causa**: Ruta literal no existe. No es que sea inaccesible, es que **no se ha identificado el puerto del MCU todavía**.

### Estado del Firmware

```
No build file /home/olimex/klipper/klippy/../.config
No build file /home/olimex/klipper/klippy/../out/klipper.elf
```

**⚠️ INFORMACIÓN CRÍTICA**: No hay firmware Klipper compilado para el MCU. El sistema no está completo.

---

## Diagnóstico Técnico

### ¿Por Qué No Hay Respuesta M115 en ttyS1-3?

**Causa identificada**: El puerto Marlin/MCU **no está asignado a ttyS1, ttyS2 o ttyS3**. Posibles ubicaciones:

#### 1. **Puerto USB-Serial (más probable)**
- `/dev/ttyUSB*` o `/dev/ttyACM*` (conversor USB-to-UART)
- Actualmente: **No detectados** (`ls /dev/ttyUSB* → vacío`)
- Implicación: **MCU no está conectado por USB**, O el adaptador no está presente

#### 2. **Puerto I2C (posible si es esclavo I2C)**
- `/dev/i2c-0`, `/dev/i2c-1`, `/dev/i2c-2`
- Herramienta requerida: `i2cdetect` (NO DISPONIBLE en este sistema)
- Implicación: No se puede escanear sin instalar `i2c-tools`

#### 3. **Puerto GPIO/SPI (remoto)**
- Comunicación no es por serie estándar
- Requiere overlays customizados (no configurado)

#### 4. **Socket/Daemon Interno (menos probable)**
- MCU es módulo interno on-board
- Comunicación no es vía UART serial

### Comprobación de Dispositivos Disponibles

```bash
Dispositivos TTY actuales:
  ttyS0    → Consola del kernel (Linux 5.10, Olimex A13)
  ttyS1-7  → 7 puertos adicionales (16550A emulados, sin dispositivo conectado)
  ttyGS0   → USB Gadget Serial (para conectarse A LA PLACA desde USB host)
  ttyUSB*  → No presente
  ttyACM*  → No presente
```

---

## Plan de Identificación del Puerto Correcto

### Opción 1: Conectar MCU por USB (Recomendado)
Si el MCU tiene puerto USB o adaptador USB-to-UART:

```bash
# 1. Conectar adaptador USB al A13
# 2. Ejecutar:
lsusb
ls -la /dev/ttyUSB* /dev/ttyACM*

# 3. Escanear puerto USB detectado
for BAUD in 115200 250000 57600 38400; do
  timeout 1 bash -c "echo -n 'M115' | stty -F /dev/ttyUSB0 $BAUD raw; cat /dev/ttyUSB0" &
  sleep 2
done
```

### Opción 2: Investigar I2C (Si es esclavo I2C)
```bash
# 1. Instalar herramientas:
sudo apt-get install -y i2c-tools

# 2. Escanear buses:
i2cdetect -y 0
i2cdetect -y 1
i2cdetect -y 2

# 3. Identificar dirección del MCU (ej: 0x68)
# 4. Configurar Klipper con serial: /dev/i2c-X (si soporta)
```

### Opción 3: Revisar Device Tree (Overlays UART)
```bash
# Verificar qué UART está realmente habilitada:
cat /proc/device-tree/chosen/stdout-path
dtc -I fs /sys/firmware/devicetree/base | grep -A5 "uart"

# Podría ser que UART3 esté mapeada a pin diferente
```

---

## Recomendaciones Inmediatas

### 1. **Verificar Conexión Física**
   - ¿El MCU (placa de motores) está conectado al A13?
   - ¿Por qué puerto? (USB, UART con cable dupont, I2C, etc.)
   - ¿Hay adaptadores/conversores intermedios?

### 2. **Conseguir Identificador USB/Serial**
   Si está conectado por USB:
   ```bash
   lsusb -v | grep -A5 "iSerial"
   udevadm info /dev/ttyUSB0 | grep "ID_SERIAL"
   ```

### 3. **Completar Configuración Klipper**
   Una vez identificado el puerto:
   ```ini
   [mcu]
   serial: /dev/ttyUSB0        # o el puerto correcto
   baud: 250000               # ajustar según el MCU
   ```

### 4. **Compilar Firmware Klipper para el MCU**
   Actualmente no hay `.config` compilado:
   ```bash
   cd ~/klipper
   make menuconfig            # Seleccionar MCU (STM32, ATmega, etc.)
   make                       # Compilar
   ```

---

## Conclusión Técnica

**La ausencia de respuesta M115 en ttyS1-3 es ESPERADA y NO indica fallo de hardware.**

El sistema está en estado **"pre-configuración"**:
- Klipper está instalado pero **sin firmware MCU**
- Configuración contiene **placeholder sin resolver**
- **Falta especificar físicamente dónde está el MCU**

**Próximo paso**: Determinar de qué puerto FÍSICO (USB, UART GPIO, I2C) está conectada la placa de motores (Marlin) y actualizar `printer.cfg` con la ruta correcta.

---

**Generado**: 31 de enero de 2026
**Sistema**: Olimex A13-SOM (Allwinner A13, Linux 5.10.180)
**Scope**: Diagnóstico no destructivo, solo lectura/I/O temporal
