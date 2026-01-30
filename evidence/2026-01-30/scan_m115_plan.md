# Plan de Escaneo M115 - 2026-01-30

## Situación Actual
- Klipper está corriendo (PID 527)
- pyserial NO está instalado en A13
- Herramientas disponibles: stty, timeout, cat
- **Bloqueador**: `sudo systemctl stop klipper` requiere contraseña interactiva

## Estrategia de Escaneo

Como no tenemos pyserial, vamos a usar:
1. Detener Klipper (requiere contraseña interactiva en A13)
2. Usar `stty` + `cat` + `timeout` para leer datos de puerto

### Script de Escaneo (a ejecutar en A13 con permisos)

```bash
#!/bin/bash
# scan_m115.sh - Escaneo M115 en puertos serie

PORTS=(/dev/ttyS1 /dev/ttyS2 /dev/ttyS3 /dev/ttyS4 /dev/ttyS5 /dev/ttyS6 /dev/ttyS7)
BAUDS=(250000 115200 57600 19200)

echo "=== ESCANEO M115 ==="
for PORT in "${PORTS[@]}"; do
  [ ! -e "$PORT" ] && continue
  for BAUD in "${BAUDS[@]}"; do
    echo -n "Testing $PORT @ $BAUD baud... "
    stty -F "$PORT" "$BAUD" 2>/dev/null || continue
    {
      echo -e "M115" | timeout 1 cat > "$PORT" 2>/dev/null
      timeout 0.5 cat "$PORT" 2>/dev/null
    } > /tmp/response_${PORT##*/}_${BAUD}.txt 2>&1
    RESP=$(cat /tmp/response_${PORT##*/}_${BAUD}.txt 2>/dev/null | tr -cd '\00-\177')
    if echo "$RESP" | grep -q "FIRMWARE\|Marlin\|ok"; then
      echo "HIT! Response: $(echo "$RESP" | head -c 100)"
    else
      echo "No response"
    fi
  done
done
echo "=== FIN ESCANEO ==="
```

## Próximos Pasos

1. **Usuario debe ejecutar en A13**:
   ```
   sudo su -
   cd /tmp && vi scan_m115.sh  # Copiar script anterior
   chmod +x scan_m115.sh
   systemctl stop klipper
   ./scan_m115.sh
   systemctl start klipper
   ```

2. **O (alternativa sin permisos)**:
   - Identificar puerto por contexto: config anterior menciona ATmega2560
   - ATmega típicamente @ 250000 o 115200 baud
   - Asumir puerto por orden de instalación (likely ttyS1 o ttyS2)

## Dependencias/Bloqueadores

- [x] Verificar stty disponible
- [x] Verificar timeout disponible
- [ ] **Obtener contraseña de olimex para sudo** O permitir scan sin pausar Klipper
- [ ] Ejecutar script en A13
- [ ] Identificar puerto responde M115
