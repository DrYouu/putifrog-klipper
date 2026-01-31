#!/bin/bash

# UART Marlin Scan - Minimal version
# Sin hanging, con timeout agresivo

PORTS=("ttyS1" "ttyS2" "ttyS3")
BAUDRATES=(115200 57600 38400 19200 9600)
TIMEOUT=1

echo "=== UART MARLIN SCAN ==="
echo "Puertos: ${PORTS[@]}"
echo "Baudrates: ${BAUDRATES[@]}"
echo ""

for PORT in "${PORTS[@]}"; do
    for BAUD in "${BAUDRATES[@]}"; do
        TTY="/dev/$PORT"
        
        if [ ! -e "$TTY" ]; then
            continue
        fi
        
        # Enviar M115 + esperar respuesta con timeout
        OUTPUT=$(
            (
                stty -F "$TTY" $BAUD raw -echo 2>/dev/null
                echo -n "M115" > "$TTY" 2>/dev/null
                cat "$TTY" 2>/dev/null &
                PID=$!
                sleep $TIMEOUT
                kill $PID 2>/dev/null || true
            ) 2>/dev/null
        )
        
        # Filtrar ASCII imprimible
        CLEAN=$(echo "$OUTPUT" | tr -d '\0' | LC_ALL=C grep -o '[[:print:]]*' | head -1)
        
        if [ -n "$CLEAN" ]; then
            echo "✓ $PORT @ $BAUD: $CLEAN"
        else
            echo "  $PORT @ $BAUD: (vacío)"
        fi
    done
done
