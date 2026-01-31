#!/bin/bash
# Minimal UART scan without hanging

PORTS=("ttyS1" "ttyS2" "ttyS3")
BAUDRATES=(115200 57600 38400 19200 9600)

echo "=== UART MARLIN SCAN ==="
echo ""

for PORT in "${PORTS[@]}"; do
    for BAUD in "${BAUDRATES[@]}"; do
        TTY="/dev/$PORT"
        
        if [ ! -e "$TTY" ]; then
            echo "X $PORT @ $BAUD: puerto no existe"
            continue
        fi
        
        # Usar timeout de GNU para evitar cuelgues
        RESULT=$(timeout 1 bash -c "
            stty -F $TTY $BAUD raw -echo 2>/dev/null || true
            echo -n 'M115' > $TTY 2>/dev/null
            timeout 0.8 cat $TTY 2>/dev/null || true
        " 2>/dev/null)
        
        RESULT=$(echo "$RESULT" | tr -cd '[:print:][:space:]' | head -c 100)
        
        if [ -n "$RESULT" ]; then
            echo "✓ $PORT @ $BAUD: $RESULT"
        else
            echo "  $PORT @ $BAUD: (vacío)"
        fi
    done
done

echo ""
echo "=== FIN ==="
