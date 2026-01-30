# Análisis Final: Comunicación Marlin ↔ A13
## Fecha: 2026-01-30

## Descubrimientos Clave

### 1. MCU es STM32, No ATmega
- **Kernel Log**: "STM32 USART driver initialized"
- **NO es Arduino Mega** (reporte anterior era incorrecto)
- **Firmware**: Marlin 2.5 en STM32

### 2. Puerto Serie NO Encontrado en /dev/
- **ttyS1-7**: ✗ Sin respuesta a comandos Marlin
- **ttyGS0**: ✓ Existe pero responde a getty, NO a Marlin
- **ttyACM*, ttyUSB***: ✗ No existen
- **STM32 UART**: ✗ Sin exposición en /dev/

### 3. Klipper Está Configurado con Pseudo-TTY
```
/home/olimex/printer_data/comms/klippy.serial → /dev/pts/0
```

**Significado**:
- Klipper NO se conecta a un puerto serie real
- `klippy.serial` es un **pseudo-terminal**
- El MCU debe comunicarse vía otro método

### 4. Posibles Métodos de Comunicación

#### Opción A: Socket Unix Compartido (MÁS PROBABLE)
```
/home/olimex/printer_data/comms/klippy.sock
```
- Klipper escucha en socket
- Algún proceso intermedio se conecta a MCU vía I2C/UART
- Reenvía datos a Klipper

#### Opción B: I2C Directo
- Tres buses I2C disponibles (i2c-0, i2c-1, i2c-2)
- MCU STM32 podría estar en dirección I2C (ej: 0x68)
- Requiere driver específico

#### Opción C: Comunicación Interna del SoC
- MCU STM32 conectado vía bus interno (no estándar)
- Socket integrado con pines dedicados
- Sin exposición a /dev/ estándar

---

## Próximos Pasos Recomendados

### 1️⃣ Verificar Procesos que Usan klippy.sock
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'lsof /home/olimex/printer_data/comms/klippy.sock 2>/dev/null'
```

### 2️⃣ Buscar Procesos que Hablen con MCU
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'ps aux | grep -i "stm32\|mcu\|modbus\|bridge" | grep -v grep'
```

### 3️⃣ Verificar I2C Buses en Detalle
Instalar `i2c-tools` y ejecutar:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'i2cdump -y 0 0x68 2>/dev/null'  # Probar direcciones comunes
```

### 4️⃣ Revisar Logs de Klipper Recientes
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'tail -n 200 /home/olimex/printer_data/logs/klippy.log | grep -A5 -B5 "mcu\|error"'
```

### 5️⃣ Buscar Firmware Bridge o Proxy
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'find /home/olimex -name "*.py" -exec grep -l "klippy.sock\|STM32" {} \;'
```

---

## Resumen Estado Actual

| Aspecto | Resultado |
|---------|-----------|
| **MCU Hardware** | STM32 (confirmado en kernel) |
| **MCU Firmware** | Marlin 2.5 |
| **Conexión Puerto Serie** | NO encontrada en /dev/ |
| **Conexión USB** | NO (ttyGS0 existe pero no responde) |
| **Conexión I2C** | POSIBLE (buses presentes) |
| **Klipper Estado** | Corriendo pero sin MCU conectado |
| **Comunicación Esperada** | ¿Socket? ¿I2C? ¿Interno? |

---

## Conclusión

La placa de motores **STM32/Marlin está presente en el sistema** pero:
- ✗ NO expone puerto série estándar
- ✗ NO responde vía USB/ttyGS0
- ? PROBABLEMENTE comunica vía I2C o socket interno

Necesita:
1. Investigar qué proceso/daemon maneja la comunicación
2. Determinar si usa I2C, socket, o método propietario
3. Una vez identificado, configurar Klipper correctamente
