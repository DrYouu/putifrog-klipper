# Identidad de Hardware - Olimex A13 SOM
## Basado en Evidencia de 2026-01-30

### Hardware Confirmado

**SoC**: Allwinner A13
- Familia: sun4i/sun5i
- Arquitectura: ARMv7 (32-bit)
- Cortex-A8 single-core
- Serial único: 1625420409016318

**Memoria**:
- RAM: 488 MB
- Almacenamiento: microSD/eMMC de 7.2 GB (modelo SA08G, serial 0x1542d98b)

**Kernel**:
- Versión: Linux 5.10.180-olimex
- Build: #145321 SMP Thu Jan 22 14:55:18 UTC 2026
- Distribución: Debian GNU/Linux 11 (bullseye)

### Puertos UART/Serial

**UART Física (Device Tree):**
- UART0 @ 0x1c28000
- UART1 @ 0x1c28400 ← **Puerto de Consola**
- UART2 @ 0x1c28800
- UART3 @ 0x1c28c00

**Todos son drivers dw-apb-uart (Designware APB UART)**

**Puertos Accesibles en Sistema:**
- `/dev/ttyS0`: UART1 @ 115200 baud (consola + getty)
- `/dev/ttyS1-7`: Slots genéricos 8250 (presentes, no en uso)
- `/dev/ttyGS0`: USB Gadget Serial (getty activo) ← **Puerto USB hacia motor**

### Buses de Comunicación

| Bus | Cantidad | Estado | Notas |
|-----|----------|--------|-------|
| I2C | 3 (i2c-0,1,2) | Presente | Sin dispositivos detectados actualmente |
| UART | 4 (hw) + 8 (sw) | Presente | UART1 es consola, otros disponibles |
| USB Host | 3 (EHCI, OHCI, MUSB) | Activo | EHCI tiene TP-Link LAN, MUSB vacío |
| USB Gadget | 1 (g_serial) | Activo | ttyGS0 escuchando |
| SPI | 0 | No activo | No en uso |
| GPIO | Presente | En uso | MMC CD, USB PHY |
| PWM | Presente | No activo | Backlight LCD (sin regulator) |

### Parámetros de Arranque del Kernel

```
root=PARTUUID=023aa8cd-01 rootwait console=ttyS0,115200 panic=10 loglevel=4
```

- Console: ttyS0 @ 115200 baud
- Root filesystem: partición con UUID 023aa8cd-01
- Timeout panic: 10 segundos
- Log level: 4 (warnings and above)

### Confirmación de Estado

✓ = Confirmado en evidencia
? = Presente en device tree pero sin uso actual

| Componente | Confirmado |
|-----------|-----------|
| SoC Allwinner A13 | ✓ |
| UART1 como consola | ✓ |
| USB Gadget Serial | ✓ |
| 3x I2C controllers | ✓ |
| ttyGS0 activo | ✓ |
| TP-Link USB Ethernet | ✓ |
| UART0, UART2, UART3 | ? |
| SPI | X (no) |

### Configuración de Servicios

**Serial Login Activos:**
- `serial-getty@ttyS0.service`: En ejecución
- `serial-getty@ttyGS0.service`: En ejecución

**Módulos USB Cargados:**
- g_serial (USB gadget serial)
- libcomposite (framework gadget)
- cdc_ether (Ethernet sobre USB)
- usbnet (networking USB)

---

## Preguntas Abiertas (Requieren Investigación Posterior)

1. **¿Cómo se conecta la placa de motor a la A13?**
   - Candidatos: USB Gadget (ttyGS0), I2C, UART2/UART3, o combinación

2. **¿Hay periféricos I2C en bus i2c-0, i2c-1, o i2c-2?**
   - Requiere: `i2cdetect` en cada bus

3. **¿UART2 y UART3 están conectados físicamente?**
   - Requiere: Verificar mapeo de pines en módulo A13

4. **¿Qué datos se intercambian vía ttyGS0?**
   - Requiere: Monitoreo de comunicación activa

---

## Referencias de Ubicación

- Baseline del sistema: `evidence/2026-01-30/system_baseline.md`
- Inventario TTY: `evidence/2026-01-30/tty_inventory.md`
- Device Tree: `evidence/2026-01-30/device_tree_uart.md`
- Buses: `evidence/2026-01-30/bus_inventory.md`
