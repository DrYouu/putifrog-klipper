# Plan de acción: Habilitar/Configurar UART en Olimex A13

**Fecha**: 2026-01-30  
**Estado**: TODO (investigación completada, pero **SIN EJECUTAR**).

---

## Resumen de hallazgos

| Hallazgo                    | Valor                                                    |
|-----------------------------|----------------------------------------------------------|
| **Tipo de configuración**   | Device Tree (DT) embebido en `/boot/kernel.itb` ✅       |
| **UART habilitados en DT**  | Solo UART1 (serial@1c28400) ✅                           |
| **Estado de UART1**         | Asignado a ttyS0 (consola del kernel) ⚠️                 |
| **Otros UART (0, 2, 3)**    | status = "disabled" en DT ❌                              |
| **Pinmux definiciones**     | Existen para todos, pero solo UART1 activo ℹ️            |
| **Evidencia**               | [evidence/2026-01-30/dt_uart_status.md](../../evidence/2026-01-30/dt_uart_status.md) |

---

## Paso 1: Identificar el UART objetivo

**Antes de cualquier cambio**, necesitas saber:
- ¿En qué **pines físicos** está conectado el cable serie (RX, TX, GND)?
- ¿A qué **UART del chip A13** corresponden esos pines?

**Referencia**: 
- Hoja de datos del A13: tabla de pines (pinout).
- Esquemático de Olimex A13: dónde están los conectores serie.

**Comandos útiles** (si tienes acceso a documentación):
```bash
# Ver qué pines están en qué función en el DTB
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'dtc -I fs -O dts /proc/device-tree 2>/dev/null | grep -E "uart.*pins.*phandle|uart.*pins {" -A 5'
```

---

## Paso 2: Evaluar el escenario

### Escenario A: El cable está en UART1 (pines físicos de serial@1c28400)

**Problema**: UART1 está ocupado por la consola del kernel (ttyS0, 115200 baud).

**Soluciones**:
1. **Opción A1**: Redirigir la consola a UART0 o a USB.
2. **Opción A2**: Usar UART1 de todas formas, pero suprimir mensajes del kernel.

**Riesgo**: Perder acceso a la consola del sistema.

---

### Escenario B: El cable está en UART0, UART2 o UART3

**Problema**: Esos UART están deshabilitados en el DTB (`status = "disabled"`).

**Solución**: Habilitar el UART objetivo en el DTB.

**Pasos**:
1. Descargar/extraer el DTB de `/boot/kernel.itb`.
2. Descompilar a `.dts` (texto).
3. Buscar el nodo `serial@1c28000` (UART0), `serial@1c28800` (UART2), o `serial@1c28c00` (UART3).
4. Cambiar `status = "disabled"` → `status = "okay"`.
5. Asignar pinctrl correcto (referenciando las definiciones ya en el DTB).
6. Recompilar a `.dtb` (binario).
7. Insertar el DTB en `/boot/kernel.itb`.
8. Reboot.
9. Verificar que el puerto aparece en `dmesg` y en `/dev/ttyS*`.

**Riesgo**: Si el pinctrl es incorrecto, podrías deshabilitar otras funciones (ej: SD, Ethernet, etc.).

---

## Paso 3: Antes de habilitar un UART, verificar conflictos de pines

Cada pin del A13 puede asignarse a múltiples funciones. Si UART2 usa el mismo pin que SD, habrá conflicto.

**Verificación**:
1. Ver la hoja de datos del A13: tabla de funciones de pines.
2. En el DTB, encontrar las definiciones `uart*-pins` y verificar qué grupos de pines usan.
3. Comprobar que esos pines no estén ya asignados a otra función crítica (SD, Ethernet, etc.).

**Comando para inspeccionar** (sin ejecutar):
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'dtc -I fs -O dts /proc/device-tree 2>/dev/null | grep -E "uart2-pd-pins|nand-pins|mmc.*-pins" -A 10 | head -100'
```

---

## Paso 4: Herramientas necesarias

Para habilitar un UART, necesitarás:

1. **`dtc`** (Device Tree Compiler)
   - Estado: ✅ Ya presente en Olimex
   - Verificado: `command -v dtc` → OK

2. **Acceso a /boot como root**
   - Modificar `/boot/kernel.itb` requiere permisos de root.
   - Actual: probablemente `olimex` es sudoer (verifica con `sudo -l`).

3. **Editor de texto** (vi, nano, etc.)
   - Para editar el `.dts` después de descompilar.

4. **`mkimage`** (opcional, para repacketizar kernel.itb)
   - Si kernel.itb es un ITB (imagen U-Boot), necesitarás reempacar.

**Comando para verificar herramientas**:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" \
  'for tool in dtc mkimage; do command -v $tool >/dev/null && echo "$tool: OK" || echo "$tool: MISSING"; done'
```

---

## Paso 5: Cambios concretos (abstracto, no ejecutar)

### Si UART0 (serial@1c28000) es el objetivo:

**En el DTB:**
```dts
serial@1c28000 {
    compatible = "snps,dw-apb-uart";
    reg = <0x1c28000 0x400>;
    interrupts = <1>;
    clocks = <&gates 59>;
    status = "disabled";  ← CAMBIAR A "okay"
    pinctrl-names = "default";  ← AGREGAR
    pinctrl-0 = <&uart0_pg_pins>;  ← AGREGAR (referencia a pinctrl existente)
};
```

**Después de recompiler y reboot**, debería aparecer en dmesg:
```
[...] 1c28000.serial: ttyS0 at MMIO 0x1c28000 (irq = 33, base_baud = 1500000) is a 16550A
```

### Si UART2 (serial@1c28800) es el objetivo:

Similar, pero con:
```dts
status = "okay";
pinctrl-names = "default";
pinctrl-0 = <&uart2_pd_pins>;  ← O uart2-cts-rts-pd-pins si necesita RTS/CTS
```

---

## Paso 6: Procedimiento de habilitar (pseudocódigo, NO EJECUTAR)

```bash
# 1. Backup
sudo cp /boot/kernel.itb /boot/kernel.itb.backup

# 2. Extraer DTB de kernel.itb (depende del formato de ITB)
cd /tmp
sudo dumpimage -T flat_dt -i /boot/kernel.itb -p <numero> kernel.dtb
# o
sudo dd if=/boot/kernel.itb of=kernel.itb.raw bs=1 skip=<offset>
file kernel.itb.raw  # Identificar offset de DTB

# 3. Descompilar
dtc -I dtb -O dts kernel.dtb -o kernel.dts

# 4. Editar (buscar serial@1c28000 o serial@1c28800, cambiar status)
vi kernel.dts
# Cambiar: status = "disabled" → status = "okay"
# Agregar: pinctrl-names = "default"; pinctrl-0 = <&uart0_pg_pins>;

# 5. Recompilar
dtc -I dts -O dtb kernel.dts -o kernel.dtb.new

# 6. Reempacar en kernel.itb
mkimage -D '-I dts -O dtb' -T flat_dt -i kernel.dtb.new -o kernel.itb.new
sudo cp kernel.itb.new /boot/kernel.itb

# 7. Reboot
sudo reboot

# 8. Verificar
dmesg | grep ttyS0
ls -l /dev/ttyS*
```

**⚠️ NOTA**: Los pasos exactos dependen del formato de `/boot/kernel.itb` en esta Olimex.
Podrían variar (ITB, FIT, raw binary, etc.).

---

## Paso 7: Verificación posterior

Después de cambios y reboot, ejecuta:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'dmesg -T | grep -i "ttyS\|uart"'
```

Debería mostrar los nuevos puertos activos.

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'ls -l /dev/ttyS*'
```

Verifica que el archivo exista.

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 "olimex@192.168.0.13" 'cat /proc/device-tree/serial@1c28800/status 2>/dev/null && echo OK || echo DISABLED'
```

(Reemplaza `1c28800` por el puerto que habilitaste.)

---

## Riesgos potenciales

| Riesgo                                 | Mitigación                                                     |
|----------------------------------------|----------------------------------------------------------------|
| Deshabilitar SD, Ethernet, etc.        | Verificar pinctrl conflicts antes. Backup de kernel.itb.       |
| Perder acceso SSH durante cambios      | Hacer cambios en sesión local si es posible. Tener respaldo. |
| Kernel no arranca                      | DTB corrupto o inválido. Usar `/boot/kernel.itb.backup`.      |
| Consola no funciona                    | Si cambias console=, podrías no ver errores de boot.          |
| El UART no aparece en dmesg            | DTB no aplicado correctamente, o pinctrl mal referenciado.    |

---

## Decisión: ¿Habilitar UART0, UART2 o UART3?

**Depende de**:
1. Dónde está físicamente conectado el cable (qué pines RX/TX).
2. Qué otros dispositivos usan en esos pines.
3. Si hay documentación de Olimex sobre pinout.

**Recomendación**:
- Consulta el esquemático de la Olimex A13.
- Identifica el conector serie en la placa.
- Lee a qué pines corresponds (ej: "UART2 on pins PD2/PD3").
- Entonces habilita ese UART en el DTB.

---

## Plan ejecutable (cuando se apruebe)

1. ✅ Diagnóstico completado (este documento).
2. ⏭️ **DECISION**: ¿Qué UART habilitar? (necesita confirmación del usuario).
3. ⏭️ Backup y extracción del DTB.
4. ⏭️ Edición del DTB (cambiar `status`, asignar `pinctrl`).
5. ⏭️ Recompilación y inserción en kernel.itb.
6. ⏭️ Reboot.
7. ⏭️ Verificación de que el puerto está activo.
8. ⏭️ Test de comunicación con Klipper.

---

## Próximo paso

📖 **Lee primero**:
- [docs/hardware/uart_pinmux_explicado_para_lego.md](../../docs/hardware/uart_pinmux_explicado_para_lego.md)
- [evidence/2026-01-30/dt_uart_status.md](../../evidence/2026-01-30/dt_uart_status.md)

🔍 **Entonces decide**: ¿Cuál UART necesita estar habilitado?

⚠️ **Una vez decidido**: puedes ordenar que se ejecute este plan (paso 1 a 8).

---

**Creado**: 2026-01-30  
**Estado**: TODO, esperando feedback del usuario.
