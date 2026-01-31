# Intento 1: Habilitar todos los UART en DTB - Resultado

**Fecha**: 2026-01-30  
**Objetivo**: Habilitar UART0, UART2, UART3 en Device Tree para mapearlos a ttyS y probar cuál responde.

---

## Resumen

| Paso | Acción | Resultado |
|------|--------|-----------|
| 1 | Descargar kernel.itb desde Olimex | ✅ Éxito (21 MB) |
| 2 | Script de sed para habilitar UART | ⚠️ No funcionó (sed con regex complejo) |
| 3 | Reboot de Olimex | ✅ Éxito (arrancó correctamente) |
| 4 | Verificar puertos después de reboot | ❌ Aún solo ttyS0 activo |
| 5 | Editar DTB con Python regex | ⏳ Parcial (shell inestable) |
| 6 | Estado actual | ⏳ Indeterminado |

---

## Hallazgos técnicos

###  Después del primer reboot (intentó cambios de sed)

**dmesg**:
```
Serial: 8250/16550 driver, 8 ports, IRQ sharing disabled
1c28400.serial: ttyS0 at MMIO 0x1c28400 (irq = 34, base_baud = 1500000) is a 16550A
```

✅ Solo ttyS0 registrado (aún deshabilitados UART0/2/3).

**Puertos en /dev**:
```
ttyS0 - crw--w---- (consola)
ttyS1-S7 - crw-rw---- (existen, pero...)
```

❌ Todos devuelven "Input/output error" excepto ttyS0.

---

##  Problemas encontrados

1. **Edición de DTS es frágil**:
   - `sed` con rangos multilinea es complicado en bash.
   - Los heredocs en SSH tienen limitaciones con escapes.
   - Python regex también requiere escapado cuidadoso.

2. **Shell SSH inestable con heredocs**:
   - Comandos largos tipo heredoc colapsan frecuentemente.
   - La conexión se queda "colgada" en prompts de `sudo -S`.

3. **Método alternativo necesario**:
   - Lugar de heredocs, crear archivos locales.
   - O usar SCP para enviar scripts.
   - O simplificar los cambios (ej: solo cambiar un UART a la vez).

---

## Recomendación: Próximo intento

**Enfoque simplificado**:

1. **Restablecer DTB original** (si existe backup).
2. **Crear script en archivo local** (no heredoc).
3. **Enviarlo a Olimex con SCP**.
4. **Ejecutarlo remoto sin heredoc**.

O:

**Enfoque minimalista**:
1. Editar solo **UART0** (no los 3).
2. Hacer cambio manual simple (`sed` line-by-line, no regex).
3. Reboot y verificar.
4. Si funciona, repetir para UART2 y UART3.

---

## Archivos generados

- Backup en Olimex: `/boot/kernel.itb.backup-2026-01-30` (del primer script que SÍ funcionó)
- DTB actual: `/boot/kernel.itb` (sin cambios efectivos de sed/Python)

---

## Estado final

✅ **Olimex está operativa** (2 min de uptime)  
❓ **UART0/2/3 aún deshabilitados en DTB**  
⏳ **Necesita reintentar con método más robusto**

---

## Siguientes pasos

Opción A (revert y simplificar):
```bash
# Restaurar original
ssh olimex@192.168.0.13 'echo olimex | sudo -S cp /boot/kernel.itb.backup-2026-01-30 /boot/kernel.itb'
ssh olimex@192.168.0.13 'sudo reboot'

# Entonces: intentar edición más simple
```

Opción B (continuar desde DTB actual):
```bash
# Intentar editar UART0 solamente
# Si funciona, repetir para los demás
```

Se recomienda **Opción B** (continuar): el DTB actual está funcional, incluso si los cambios no se aplicaron.
