# Puertos Serie y UART - Resumen de Evidencia
## Basado en Captura del 2026-01-30

## Puertos Serie Disponibles

### Puertos UART Físicos del SoC (Device Tree)

El Allwinner A13 posee **4 UARTs** definidos en el device tree:

| UART | Dirección | Driver | Consola | Pines | CTS/RTS |
|------|-----------|--------|---------|-------|---------|
| UART0 | 0x1c28000 | dw-apb-uart | No | uart0-pins | No |
| UART1 | 0x1c28400 | dw-apb-uart | **Sí** | uart1-pe/pg | No |
| UART2 | 0x1c28800 | dw-apb-uart | No | uart2-pd | **Sí** |
| UART3 | 0x1c28c00 | dw-apb-uart | No | uart3-pg | **Sí** |

### Puertos Accesibles en `/dev/`

| Dispositivo | Origen | Estado | Propósito |
|-----------|--------|--------|-----------|
| `/dev/ttyS0` | UART1 @ 0x1c28400 | **Activo** | Consola del kernel + getty login |
| `/dev/ttyS1-7` | serial8250 (emulado) | Presentes | Slots genéricos (no en uso) |
| `/dev/ttyGS0` | USB Gadget | **Activo** | Puerto USB serie + getty login |

### Configuración de Consola

```
Console: ttyS0, 115200 baud, 8N1
Kernel cmdline: console=ttyS0,115200
Getty activos: ttyS0, ttyGS0
```

---

## Hallazgo Crítico: ttyGS0 (USB Gadget Serial)

El puerto **`/dev/ttyGS0`** es un **puerto USB gadget** que:

1. **Está cargado**: Módulo `g_serial` en kernel
2. **Está activo**: getty@ttyGS0.service corriendo
3. **Apunta a qué**: Probablemente conexión USB hacia la placa de motor
4. **Baud rate**: No especificado (USB no usa baud rate tradicional)

**Evidencia:**
```
g_serial gadget: Gadget Serial v2.4
g_serial gadget: g_serial ready
serial-getty@ttyGS0.service loaded active running
```

---

## Análisis de Disponibilidad para Motor

### ¿Qué puerto(s) puede usar la placa de motor?

**Opción 1: USB Gadget (ttyGS0)** ⭐ Más probable
- ✓ Activo y escuchando
- ✓ getty disponible para conexión
- ✓ Módulo cargado
- Tipo: Comunicación USB (A13 como periférico)

**Opción 2: I2C (i2c-0, i2c-1, i2c-2)**
- ✓ 3 buses disponibles
- ? Sin periféricos detectados
- ? Requiere verificación de direcciones de dispositivos
- Tipo: Bus sincrónico

**Opción 3: UART2 o UART3**
- ✓ Presentes en device tree
- ? No mapeados a `/dev/ttyS*` actualmente
- ? Pines físicos no verificados
- Tipo: Comunicación serie (RX/TX)

**Opción 4: UART1 + Switcher (menos probable)**
- ✗ Ya asignado a consola del sistema
- ✗ Requeriría modificación de kernel

---

## Puertos Accesibles vs Ocupados

| Puerto | Acceso | Ocupación | Disponible |
|--------|--------|-----------|-----------|
| ttyS0 | Lectura | Consola kernel | ⚠️ Solo lectura |
| ttyS1-7 | R/W | Ninguna | ✓ Libre (si hay HW) |
| ttyGS0 | R/W | Getty login | ✓ Libre (con getty) |
| I2C-0 | R/W | Ninguno | ✓ Libre |
| I2C-1 | R/W | Ninguno | ✓ Libre |
| I2C-2 | R/W | Ninguno | ✓ Libre |
| USB Host | - | TP-Link LAN | - |
| USB Gadget | R/W | ttyGS0 | ✓ Libre (con getty) |

---

## Resumen para Pruebas

Para identificar cuál puerto usa el motor:

1. **Verificar ttyGS0**: Ejecutar `cat /dev/ttyGS0` mientras inyectas datos del motor
   - Si ves datos → Motor usa USB Gadget

2. **Verificar I2C**: `i2cdetect -y 0`, `i2cdetect -y 1`, `i2cdetect -y 2`
   - Si ves dispositivos → Motor usa I2C

3. **Verificar UART2/3**: Cargar driver 8250 con parámetros para esas direcciones
   - Requiere kernel modification o parámetro de boot

---

## Documentación Oficial Necesaria

- [x] Device tree UART definido
- [x] Puertos activos confirmados
- [ ] Mapeo físico de pines (requiere datasheet A13)
- [ ] Protocolos de comunicación específicos
- [ ] Velocidades de baudrate para cada puerto

---

## Referencias

- Baseline: `evidence/2026-01-30/system_baseline.md`
- TTY Inventory: `evidence/2026-01-30/tty_inventory.md`
- Device Tree: `evidence/2026-01-30/device_tree_uart.md`
- Buses: `evidence/2026-01-30/bus_inventory.md`
