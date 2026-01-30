# Hipótesis de Interconexión con Placa de Motor
## Basado en Evidencia del 2026-01-30

## Resumen de Buses Detectados

| Bus | Disponible | Activo | Periféricos Detectados |
|-----|-----------|--------|------------------------|
| USB Gadget | ✓ | ✓ | ttyGS0 (getty corriendo) |
| USB Host EHCI | ✓ | ✓ | TP-Link LAN |
| I2C-0 | ✓ | ✓ | NONE detected |
| I2C-1 | ✓ | ✓ | NONE detected |
| I2C-2 | ✓ | ✓ | NONE detected |
| UART0 | ✓ | ? | En device tree, no en `/dev/ttyS*` |
| UART2 | ✓ | ? | En device tree, no en `/dev/ttyS*` |
| UART3 | ✓ | ? | En device tree, no en `/dev/ttyS*` |
| SPI | ✗ | ✗ | No presente |

---

## Escenario Más Probable: USB Gadget Serial (ttyGS0)

### Evidencia Directa
1. Módulo `g_serial` cargado y listo: "g_serial ready"
2. Puerto `/dev/ttyGS0` con getty@ttyGS0.service activo
3. Módulo `libcomposite` (framework USB gadget) presente
4. Módulo `usb_f_acm` disponible

### Mecánica
- A13 actúa como **periférico USB** (Device Mode)
- Placa de motor es el **host USB**
- Se comunican a través de puerto USB físico
- Protocolo: CDC Serial Class (Comunicación Data Class)

### Capacidades
- Bidireccional (RX/TX)
- Control de flujo automático
- Sin limitación de baud rate (USB define velocidad)
- Compatible con sistemas estándar (Linux, Windows, etc.)

### Confirmación Necesaria
```bash
# En A13 (remoto)
stty -F /dev/ttyGS0 -a  # Verificar configuración
cat /dev/ttyGS0         # Monitorear entrada
echo "test" > /dev/ttyGS0  # Enviar dato de prueba
```

---

## Escenario Secundario: I2C (i2c-0, i2c-1, o i2c-2)

### Evidencia Indirecta
1. 3 buses I2C disponibles y driver cargado
2. Sin dispositivos detectados (⚠️ puede significar driver sin cargar)
3. Control pins para GPIO presentes

### Mecánica
- Comunicación sincrónica, diferencial
- Direcciones de 7 u 11 bits
- Requiere power supply compartida
- Topología: Multi-master posible pero típicamente single-master

### Capacidades
- Bajo voltaje (3.3V típico)
- Distancia limitada (~few meters)
- Velocidades: 100 kHz (standard), 400 kHz (fast), 1 MHz (fast+)
- Control de flujo por clock stretching

### Confirmación Necesaria
```bash
# En A13 (remoto)
i2cdetect -y 0  # Escanear bus 0
i2cdetect -y 1  # Escanear bus 1
i2cdetect -y 2  # Escanear bus 2
```

---

## Escenario Terciario: UART2 o UART3 (Conexión Directa)

### Evidencia Indirecta
1. UART2 y UART3 definidos en device tree
2. Pines mapeados en device tree (uart2-pd, uart3-pg)
3. ~~No accesibles vía `/dev/ttyS*` actualmente~~ (necesita activación)

### Mecánica
- Conexión directa RX/TX (solo 2 pines si sin flow control)
- UART2 soporta CTS/RTS si se habilita
- UART3 soporta CTS/RTS si se habilita
- Velocidades: típicamente 9600, 19200, 38400, 115200 baud

### Capacidades
- Simple (solo 2-4 pines)
- Robusto (protocolo maduro)
- Bajo costo de interfaz
- Limitado a corta distancia

### Confirmación Necesaria
```bash
# Primero, verificar pines físicos en módulo A13
# Luego cargar driver:
echo "1c28800 0 115200" > /proc/sys/kernel/unknown_module_parameters
# O recompilar kernel con soporte

# Monitorear:
dmesg | grep uart
cat /dev/ttyS2  # si se carga como ttyS2
```

---

## Matriz de Decisión

Para determinar cuál es el puerto correcto:

| Pregunta | Respuesta | Implica |
|----------|----------|---------|
| ¿Ves datos en `cat /dev/ttyGS0`? | Sí | USB Gadget ✓ |
| ¿Hay dispositivos en `i2cdetect`? | Sí | I2C ✓ |
| ¿Se conectan pines UART? | Sí | UART2/3 ✓ |
| Conexión física ¿es USB? | Sí | USB Gadget ✓ |
| Conexión física ¿es conector especial? | Sí | Verificar pines |
| ¿Cómo arranca la impresora? | Enciende motor | Probable: ttyGS0 |

---

## Hipótesis Final (Más Probable)

**El motor se comunica vía USB Gadget (ttyGS0) porque:**

1. ✓ Está activamente configurado en kernel (`g_serial`)
2. ✓ getty está corriendo esperando conexiones
3. ✓ USB es el método más moderno para interconexión
4. ✓ Reduce complejidad (no requiere múltiples UART físicos)
5. ✓ Compatible con estándares modernos

**Arquitectura esperada:**
```
Placa Motor (Host USB)
        ↓ (USB Cable)
    [USB Type-A]
        ↓
A13 SOM [USB Device Mode]
        ↓ (g_serial gadget)
    /dev/ttyGS0
        ↓
  Klipper / Firmware
```

---

## Próximos Pasos de Verificación

1. **Inmediato**: Monitor `/dev/ttyGS0` durante operación
2. **Backup**: Ejecutar `i2cdetect` en los 3 buses I2C
3. **Confirmación física**: Inspeccionar conector USB/pines en placa
4. **Tracing**: Capturar tráfico USB con `usbmon` si es necesario

---

## Referencias

- Evidencia TTY: `evidence/2026-01-30/tty_inventory.md`
- Evidencia Buses: `evidence/2026-01-30/bus_inventory.md`
- Evidencia Device Tree: `evidence/2026-01-30/device_tree_uart.md`
