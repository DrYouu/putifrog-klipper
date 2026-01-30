# Sesión de Evidencia - 2026-01-30

## Resumen de Recopilación

Se ejecutaron consultas remotas a la A13 Olimex para establecer el baseline de hardware e interconexiones.

Fecha/Hora: 30 de enero de 2026, 17:51 UTC
Objetivo remoto: `olimex@192.168.0.13`
Kernel: Linux 5.10.180-olimex

## Archivos Generados

- `system_baseline.md` - Identificación del sistema y hardware base
- `tty_inventory.md` - Puertos serie disponibles y configuración
- `device_tree_uart.md` - Información de UART del device tree
- `bus_inventory.md` - Buses I2C/SPI, USB y módulos cargados

## Hallazgos Clave

1. **SoC Identificado**: Allwinner A13 (ARMv7)
2. **Puertos Serie Disponibles**: 8 x ttyS (ttyS0-ttyS7) + 1 x ttyGS0 (USB gadget)
3. **Consola Activa**: ttyS0 @ 115200 baud
4. **Buses**: 3 x I2C (i2c-0, i2c-1, i2c-2), sin dispositivos SPI activos
5. **USB**: Múltiples controladores (EHCI, OHCI, MUSB), dispositivos detectados:
   - TP-Link USB 10/100 LAN (idVendor=2357, idProduct=0602)
   - SMSC Hub (idVendor=0424, idProduct=2513)

## Comandos Ejecutados

Todos los comandos se ejecutaron de forma remota vía SSH con contexto de usuario `olimex`.
Ver archivos individuales para detalles de cada comando.

---

Sesión completada. Todos los outputs guardados sin modificación.
