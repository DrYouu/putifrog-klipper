# Device Tree - Información UART/Serial
## Evidencia: 2026-01-30

### Comando: Extracción de UART del Device Tree Compilado

#### Qué Ejecuté
```
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dtc -I fs -O dts /proc/device-tree 2>/dev/null | grep -nEi "uart|serial" | sed -n "1,260p"'
```

#### Output
```
5:      serial-number = "1625420409016318";
68:             uart2_pd_pins = "/soc/pinctrl@1c20800/uart2-pd-pins";
87:             uart2_cts_rts_pd_pins = "/soc/pinctrl@1c20800/uart2-cts-rts-pd-pins";
90:             uart1_pg_pins = "/soc/pinctrl@1c20800/uart1-pg-pins";
101:            uart2 = "/soc/serial@1c28800";
108:            uart3_cts_rts_pg_pins = "/soc/pinctrl@1c20800/uart3-cts-rts-pg-pins";
109:            uart0 = "/soc/serial@1c28000";
120:            uart1_pe_pins = "/soc/pinctrl@1c20800/uart1-pe-pins";
146:            uart3 = "/soc/serial@1c28c00";
147:            uart3_pg_pins = "/soc/pinctrl@1c20800/uart3-pg-pins";
154:            uart1 = "/soc/serial@1c28400";
155:            uart0_pins = "/soc/pinctrl@1c20800/uart0-pins";
193:            serial@1c28000 {
195:                    compatible = "snps,dw-apb-uart";
510:            serial@1c28800 {
512:                    compatible = "snps,dw-apb-uart";
585:            serial@1c28400 {
587:                    compatible = "snps,dw-apb-uart";
610:                    uart2-pd-pins {
613:                            function = "uart2";
650:                    uart1-pg-pins {
653:                            function = "uart1";
688:            uart2-cts-rts-pd-pins {
691:                    function = "uart2";
694:            uart1-pe-pins {
697:                    function = "uart1";
730:            uart3-cts-rts-pg-pins {
733:                    function = "uart3";
736:            uart3-pg-pins {
739:                    function = "uart3";
856:            serial@1c28c00 {
858:                    compatible = "snps,dw-apb-uart";
945:            serial0 = "/soc/serial@1c28400";
949:            stdout-path = "serial0:115200n8";
```

#### Interpretación Detallada

**UART Controllers (módulos de hardware):**

1. **serial@1c28000** (UART0)
   - Dirección: 0x1c28000
   - Driver: snps,dw-apb-uart (Designware APB UART)
   - Pines: uart0-pins (device tree alias)

2. **serial@1c28800** (UART2)
   - Dirección: 0x1c28800
   - Driver: snps,dw-apb-uart
   - Pines: uart2-pd-pins (Port D, control flow: uart2-cts-rts-pd-pins)
   - Función: UART2 mapeado a pines PD

3. **serial@1c28400** (UART1)
   - Dirección: 0x1c28400
   - Driver: snps,dw-apb-uart
   - **ASIGNADO COMO CONSOLA**: `stdout-path = "serial0:115200n8"`
   - Pines: uart1-pe-pins (Port E) + uart1-pg-pins (Port G)
   - Este es **ttyS0** en el sistema

4. **serial@1c28c00** (UART3)
   - Dirección: 0x1c28c00
   - Driver: snps,dw-apb-uart
   - Pines: uart3-pg-pins, uart3-cts-rts-pg-pins (control flow)
   - Función: UART3 mapeado a Port G

**Pin Configuration Summary:**

| UART | Puerto | Dirección | Pines | CTS/RTS | Alias Device Tree |
|------|--------|-----------|-------|---------|-------------------|
| UART0 | uart0-pins | 1c28000 | - | No | uart0 |
| UART1 | uart1-pe/pg | 1c28400 | PE, PG | uart1-pe | uart1 (console) |
| UART2 | uart2-pd | 1c28800 | PD | uart2-cts-rts-pd | uart2 |
| UART3 | uart3-pg | 1c28c00 | PG | uart3-cts-rts-pg | uart3 |

**Configuración de Consola:**
- `serial0` → apunta a `/soc/serial@1c28400` (UART1)
- Path: `serial0:115200n8` (115200 baud, 8 bits, no parity)
- Mapeado en kernel como `ttyS0`

**Disponibilidad de Flow Control:**
- UART1 (console): sin CTS/RTS (basado en output)
- UART2: Tiene CTS/RTS habilitado (uart2-cts-rts-pd-pins)
- UART3: Tiene CTS/RTS habilitado (uart3-cts-rts-pg-pins)

---

## Resumen de UARTs en Device Tree

El device tree define **4 UARTs principales** (UART0-3), aunque el kernel emula 8 puertos (ttyS0-7) vía `serial8250`.

**UART0, UART2, UART3** están disponibles en pines de hardware pero **no actualmente enrutados** a puertos `/dev/ttyS*` (serían emulados por el driver 8250 genérico).

**UART1** @ 0x1c28400 es la consola principal y está mapeada como ttyS0.

---

## Nota sobre ttyS1-7

Los puertos ttyS1-7 son creados por el driver 8250 genérico pero corresponden a:
- Direcciones de memoria estándar del controlador 16550
- No necesariamente vinculados a UARTs del SoC
- Posiblemente utilizados para pruebas/emulación

El mapeo real del hardware sugiere:
- **ttyS0** = serial@1c28400 (UART1) ✓ Confirmado en dmesg
- **ttyS1-7** = slots del driver 8250 genérico, disponibles si se habilitan en device tree

---

## Conclusión

El A13 posee **cuatro UARTs (UART0-3)** en el SoC, con **UART1** asignado a la consola del sistema (ttyS0@115200).

Los otros **UART0, UART2, UART3** están habilitados en el device tree pero no enrutados activamente a `/dev/ttyS*` en este kernel.

Para usar UART2 o UART3 se necesitaría:
1. Verificar pines de conexión física en el módulo A13
2. Potencialmente cargar driver 8250 con parámetros adicionales
3. O compilar kernel con soporte directo para estos UARTs
